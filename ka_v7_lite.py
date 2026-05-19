#!/usr/bin/env python3
"""V7-Lite contract implementation for Knowledge Atlas.

This module implements the synchronous API shape from
`docs/V7_LITE_SPEC_2026-05-18.md`. It is intentionally conservative: in-corpus
papers short-circuit to the current KA payloads, while out-of-corpus papers use
deterministic topic-fit heuristics until the recovery repo's full V7 stages and
embedding store are wired in.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, UploadFile

from ka_substitution_skill import admit_mode


REPO_ROOT = Path(__file__).resolve().parent
PAYLOAD_DIR = REPO_ROOT / "data" / "ka_payloads"
DEFAULT_THRESHOLDS_PATH = REPO_ROOT / "data" / "v7_lite_topic_thresholds.json"
V7_LITE_PROSE_CONTRACT = "V7_LITE_SUBSCRIPTION_CLI_RECOMMENDATION_CONTRACT_2026-05-18"
SUBSCRIPTION_LLM_COMMANDS = ["claude -p", "codex exec"]

router = APIRouter(prefix="/api/v7_lite", tags=["v7_lite"])


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def _norm(value: str) -> str:
    return " ".join(str(value or "").lower().replace("-", " ").replace("_", " ").split())


def _llm_recommendation_required(stage: str) -> dict[str, Any]:
    return {
        "status": "requires_subscription_cli_llm",
        "stage": stage,
        "contract": V7_LITE_PROSE_CONTRACT,
        "allowed_commands": SUBSCRIPTION_LLM_COMMANDS,
        "api_access_allowed": False,
        "python_public_prose_allowed": False,
        "python_role": "classify, compute topic fit, map measures, compute VOI, and assemble writer packet only",
    }


def find_in_corpus(doi: str = "", title: str = "") -> dict[str, Any] | None:
    payload = _load_json(PAYLOAD_DIR / "articles.json", {"articles": []})
    doi_norm = _norm(doi)
    title_norm = _norm(title)
    for row in payload.get("articles") or []:
        if doi_norm and _norm(row.get("doi") or "") == doi_norm:
            return row
        if title_norm and _norm(row.get("title") or "") == title_norm:
            return row
    return None


def classify_paper_type(title: str = "", abstract: str = "") -> dict[str, Any]:
    text = _norm(f"{title} {abstract}")
    if "meta analysis" in text:
        return {"paper_type": "meta_analysis", "design_subtype": "review_synthesis", "confidence": 0.9}
    if "systematic review" in text or "review" in text:
        return {"paper_type": "review", "design_subtype": "literature_review", "confidence": 0.84}
    if "replication" in text:
        return {"paper_type": "replication", "design_subtype": "replication", "confidence": 0.78}
    if any(term in text for term in ("participants", "experiment", "randomized", "anova", "survey", "trial")):
        return {"paper_type": "empirical", "design_subtype": "unclassified_empirical", "confidence": 0.72}
    return {"paper_type": "empirical", "design_subtype": "unclassified-confidence", "confidence": 0.35}


def topic_fit(title: str = "", abstract: str = "") -> dict[str, Any]:
    text = _norm(f"{title} {abstract}")
    topic_rules = [
        ("acoustic_environment", "Acoustic Environment", ["sound", "noise", "acoustic", "reverberation"], 0.78),
        ("lighting_circadian", "Luminous Environment", ["light", "daylight", "illuminance", "circadian"], 0.76),
        ("nature_views_cognitive_recovery", "Nature & Biophilia", ["nature", "green", "biophilic", "restorative", "vegetation"], 0.82),
        ("spatial_form_navigation", "Spatial Form", ["wayfinding", "layout", "corridor", "spatial"], 0.72),
    ]
    matches = []
    for topic_id, label, terms, base in topic_rules:
        hits = sum(1 for term in terms if term in text)
        cosine = round(min(base + hits * 0.025, 0.92), 3) if hits else 0.0
        if hits:
            matches.append({"topic_id": topic_id, "topic_label": label, "cosine": cosine})
    if not matches and any(term in text for term in ("fmri", "default mode", "connectivity", "scanner")):
        matches.append({"topic_id": "neural_methods_out_of_scope", "topic_label": "Neural methods outside KA topic scope", "cosine": 0.41})
    matches.sort(key=lambda row: -row["cosine"])
    thresholds = _load_json(DEFAULT_THRESHOLDS_PATH, {"default_threshold": 0.55, "topics": {}})
    default_threshold = float(thresholds.get("default_threshold") or 0.55)
    best = matches[0] if matches else {"topic_id": "unknown", "topic_label": "Unknown", "cosine": 0.0}
    threshold = float((thresholds.get("topics") or {}).get(best["topic_id"], default_threshold))
    return {
        "admitted_to": best["topic_id"] if best["cosine"] >= threshold else "",
        "max_cosine": best["cosine"],
        "threshold": threshold,
        "nearest_topics": matches[:3],
        "nearest_corpus_papers": [],
    }


def extract_lite_dvs(title: str = "", abstract: str = "") -> list[dict[str, Any]]:
    text = _norm(f"{title} {abstract}")
    dvs: list[dict[str, Any]] = []
    if "cortisol" in text:
        dvs.append({"name": "salivary cortisol", "type": "biomarker", "claimed_construct": "stress_response", "measurement_window": "pre vs post"})
    if "digit span" in text or "working memory" in text:
        dvs.append({"name": "backward digit span", "type": "task_embedded_performance", "claimed_construct": "attention_restoration", "measurement_window": "pre vs post"})
    if "iat" in text or "implicit association" in text:
        dvs.append({"name": "IAT", "type": "task_embedded_performance", "claimed_construct": "implicit_attitude", "measurement_window": "task"})
    if not dvs:
        dvs.append({"name": "self-report rating", "type": "self_report_questionnaire", "claimed_construct": "configurational_preference", "measurement_window": "post"})
    return dvs


def conditional_voi_for(title: str = "", abstract: str = "", dv: list[dict[str, Any]] | None = None) -> dict[str, str]:
    text = _norm(f"{title} {abstract}")
    dv = dv or []
    return {
        "target_1_better_stimuli": "medium" if any(term in text for term in ("vr", "immersive", "photogrammetry", "ecological")) else "low",
        "target_2_better_measures": "medium" if any(item.get("type") == "task_embedded_performance" for item in dv) else "na",
        "target_4_deconfounding": "medium" if any(term in text for term in ("control", "controlled", "confound")) else "low",
        "target_10_weird_extension": "high" if any(term in text for term in ("non-oecd", "community sample", "older adults")) else "na",
    }


def evaluate_v7_lite(
    *,
    doi: str = "",
    title: str = "",
    authors: str = "",
    year: int | None = None,
    session_id: str = "",
    abstract: str = "",
) -> dict[str, Any]:
    corpus_hit = find_in_corpus(doi=doi, title=title)
    if corpus_hit:
        return {
            "status": "admitted",
            "paper_id": corpus_hit.get("paper_id"),
            "evaluation": {
                "paper_id": corpus_hit.get("paper_id"),
                "source": "corpus_cache",
                "paper_type": corpus_hit.get("article_type") or "unknown",
                "paper_type_confidence": 1.0,
                "topic_fit": {
                    "admitted_to": corpus_hit.get("primary_topic") or "",
                    "max_cosine": 1.0,
                    "threshold": 0.0,
                    "nearest_corpus_papers": [{"paper_id": corpus_hit.get("paper_id"), "cosine": 1.0}],
                },
                "recommendation": {
                    "summary": "Admit",
                    "rationale": "",
                    "rationale_generation": _llm_recommendation_required("s7_recommendation_rationale"),
                    "next_step_url": f"/ka_article_view.html?id={corpus_hit.get('paper_id')}",
                },
                "ae_db_write_status": "not_needed_corpus_cache",
                "computation_date": datetime.now(timezone.utc).isoformat(),
                "corpus_size_at_computation": len((_load_json(PAYLOAD_DIR / "articles.json", {"articles": []}).get("articles") or [])),
            },
            "queued_for_full_v7": False,
            "queue_eta_minutes": 0,
        }

    classification = classify_paper_type(title, abstract)
    fit = topic_fit(title, abstract)
    if not fit["admitted_to"]:
        return {
            "status": "rejected_out_of_scope",
            "reason": f"Topic-similarity below threshold; closest match was '{fit['nearest_topics'][0]['topic_id'] if fit['nearest_topics'] else 'unknown'}' at {fit['max_cosine']} vs threshold {fit['threshold']}",
            "nearest_topics": fit["nearest_topics"],
            "new_topic_seed_offered": True,
            "new_topic_seed_id": f"SEED-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-{abs(hash(title or doi or session_id)) % 1000:03d}",
        }

    dv = [] if classification["paper_type"] in {"review", "meta_analysis"} else extract_lite_dvs(title, abstract)
    substitution = admit_mode({"dv_descriptions": dv}) if dv else {"per_dv_results": [], "paper_level_verdict": "admit_review_or_theory", "paper_level_confidence": classification["confidence"]}
    voi = conditional_voi_for(title, abstract, dv)
    recommendation_summary = "Admit with substitution" if substitution["paper_level_verdict"] == "admit_with_substitution" else "Admit"
    return {
        "status": "admitted",
        "paper_id": "PDF-LITE-PENDING",
        "evaluation": {
            "paper_id": "PDF-LITE-PENDING",
            "paper_type": classification["paper_type"],
            "paper_type_confidence": classification["confidence"],
            "design_subtype": classification["design_subtype"],
            "topic_fit": {
                "admitted_to": fit["admitted_to"],
                "max_cosine": fit["max_cosine"],
                "threshold": fit["threshold"],
                "nearest_corpus_papers": fit["nearest_corpus_papers"],
            },
            "iv": None,
            "dv": dv,
            "methods": {"design": classification["design_subtype"], "sample_n": None, "sample_composition": {}, "statistical_test": "", "preregistered": None, "open_data": None},
            "vr_suitability_mapping": substitution["per_dv_results"],
            "conditional_voi": voi,
            "recommendation": {
                "summary": recommendation_summary,
                "rationale": "",
                "rationale_generation": _llm_recommendation_required("s7_recommendation_rationale"),
                "next_step_url": "/ka_choose_measure_for_vr.html?paper_id=PDF-LITE-PENDING" if recommendation_summary.endswith("substitution") else f"/ka_topic_facet_view.html?topic={fit['admitted_to']}",
            },
            "ae_db_write_status": "partial_pending_recovery_repo",
            "computation_date": datetime.now(timezone.utc).isoformat(),
            "corpus_size_at_computation": len((_load_json(PAYLOAD_DIR / "articles.json", {"articles": []}).get("articles") or [])),
        },
        "queued_for_full_v7": True,
        "queue_eta_minutes": 120,
    }


@router.post("/ingest")
async def ingest_endpoint(
    doi: str = Form(""),
    title: str = Form(""),
    authors: str = Form(""),
    year: int | None = Form(None),
    session_id: str = Form(""),
    pdf: UploadFile | None = File(None),
) -> dict[str, Any]:
    return evaluate_v7_lite(doi=doi, title=title, authors=authors, year=year, session_id=session_id)
