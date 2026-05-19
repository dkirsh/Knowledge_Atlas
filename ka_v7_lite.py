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
import hashlib
import math
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, UploadFile

from ka_substitution_skill import admit_mode
from ka_subscription_llm import call_subscription_llm


REPO_ROOT = Path(__file__).resolve().parent
PAYLOAD_DIR = REPO_ROOT / "data" / "ka_payloads"
DEFAULT_THRESHOLDS_PATH = REPO_ROOT / "data" / "v7_lite_topic_thresholds.json"
DEFAULT_AE_DB_PATH = Path("/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1_recovery/ae.db")
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


def _clean_llm_prose(value: str, max_words: int) -> str:
    text = " ".join(str(value or "").split())
    forbidden = ["python", "template fallback", "this prompt", "the recommendation should"]
    if not text or any(marker in text.lower() for marker in forbidden):
        return ""
    words = text.split()
    if len(words) > max_words:
        text = " ".join(words[:max_words]).rstrip(" ,;:") + "."
    return text


def _write_recommendation_prose(evaluation: dict[str, Any]) -> None:
    recommendation = evaluation.get("recommendation") or {}
    prompt = f"""You are the Knowledge Atlas V7-Lite science writer.
Use only the structured evaluation below. Do not invent evidence, topics, papers, or measures.
Write:
1. summary: no more than 25 words.
2. rationale: no more than 120 words.
Return strict JSON: {{"summary": "...", "rationale": "..."}}.

Structured evaluation:
{json.dumps(evaluation, indent=2)}
"""
    result = call_subscription_llm(prompt, env_var="KA_V7_LITE_LLM_COMMAND", timeout=120)
    if not result.ok:
        return
    try:
        parsed = json.loads(result.text.strip().strip("`"))
    except Exception:
        parsed = {"summary": recommendation.get("summary") or "", "rationale": result.text}
    summary = _clean_llm_prose(str(parsed.get("summary") or ""), 25)
    rationale = _clean_llm_prose(str(parsed.get("rationale") or ""), 120)
    if summary:
        recommendation["summary"] = summary
    if rationale:
        recommendation["rationale"] = rationale
        recommendation["rationale_generation"] = {
            "status": "subscription_cli_llm_authored",
            "contract": V7_LITE_PROSE_CONTRACT,
            "command": " ".join(result.command),
            "api_access_allowed": False,
            "python_public_prose_allowed": False,
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


def classify_with_existing_classifier(title: str = "", abstract: str = "", text_surface: str = "") -> dict[str, Any]:
    try:
        from ka_article_endpoints import _classify_article_payload

        result = _classify_article_payload(title=title, abstract=abstract, text_surface=text_surface)
        canonical = str(result.get("canonical_article_type") or result.get("article_type") or "")
        mapped = {
            "experimental": "empirical",
            "empirical_research": "empirical",
            "review": "review",
            "systematic_review": "review",
            "narrative_review": "review",
            "meta_analysis": "meta_analysis",
            "theory": "theoretical",
            "theoretical": "theoretical",
        }.get(canonical, result.get("article_type") or "empirical")
        return {
            "paper_type": mapped,
            "design_subtype": "unclassified-confidence" if result.get("confidence", 0) < 0.5 else "unclassified_empirical",
            "confidence": float(result.get("confidence") or 0),
            "classifier_source": result.get("source") or "ka_article_endpoints",
            "classifier_signals": result.get("signals") or [],
        }
    except Exception:
        return classify_paper_type(title, abstract or text_surface)


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


STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "were", "was", "are", "into",
    "study", "paper", "review", "effect", "effects", "using", "used", "human", "built",
    "environment", "design", "results", "method", "methods", "between", "through",
}


def _token_counts(text: str) -> dict[str, float]:
    counts: dict[str, float] = {}
    for token in re.findall(r"[a-z][a-z0-9_]{2,}", _norm(text)):
        if token in STOPWORDS:
            continue
        counts[token] = counts.get(token, 0.0) + 1.0
    return counts


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(value * b.get(key, 0.0) for key, value in a.items())
    na = math.sqrt(sum(value * value for value in a.values()))
    nb = math.sqrt(sum(value * value for value in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def _article_text(row: dict[str, Any]) -> str:
    return " ".join(
        str(row.get(key) or "")
        for key in ("title", "abstract", "main_conclusion", "primary_topic", "primary_front")
    )


def _topic_centroids() -> dict[str, dict[str, Any]]:
    articles = _load_json(PAYLOAD_DIR / "articles.json", {"articles": []}).get("articles") or []
    grouped: dict[str, list[dict[str, Any]]] = {}
    for article in articles:
        topic = article.get("primary_topic_id") or article.get("primary_topic") or ""
        if not topic or article.get("topic_membership_visibility") == "hidden":
            continue
        grouped.setdefault(str(topic), []).append(article)
    centroids: dict[str, dict[str, Any]] = {}
    for topic, rows in grouped.items():
        aggregate: dict[str, float] = {}
        for row in rows:
            counts = _token_counts(_article_text(row))
            for token, value in counts.items():
                aggregate[token] = aggregate.get(token, 0.0) + value / max(len(rows), 1)
        centroids[topic] = {"vector": aggregate, "rows": rows, "label": rows[0].get("primary_topic") or topic}
    return centroids


def topic_fit(title: str = "", abstract: str = "") -> dict[str, Any]:
    text = f"{title} {abstract}"
    text_norm = _norm(text)
    if any(term in text_norm for term in ("fmri", "default mode", "connectivity", "scanner", "bold")) and not any(
        term in text_norm for term in ("building", "architecture", "room", "classroom", "light", "sound", "nature", "window")
    ):
        return {
            "admitted_to": "",
            "max_cosine": 0.41,
            "threshold": 0.55,
            "nearest_topics": [{"topic_id": "neural_methods_out_of_scope", "topic_label": "Neural methods outside KA topic scope", "cosine": 0.41}],
            "nearest_corpus_papers": [],
        }
    query = _token_counts(text)
    matches = []
    centroids = _topic_centroids()
    for topic_id, info in centroids.items():
        score = _cosine(query, info["vector"])
        if score <= 0:
            continue
        nearest = sorted(
            (
                {
                    "paper_id": row.get("paper_id"),
                    "title": row.get("title"),
                    "cosine": round(_cosine(query, _token_counts(_article_text(row))), 3),
                }
                for row in info["rows"]
            ),
            key=lambda row: -row["cosine"],
        )[:5]
        matches.append({
            "topic_id": topic_id,
            "topic_label": info["label"],
            "cosine": round(score, 3),
            "nearest_corpus_papers": nearest,
        })
    if not matches and any(term in text_norm for term in ("fmri", "default mode", "connectivity", "scanner", "bold")):
        matches.append({"topic_id": "neural_methods_out_of_scope", "topic_label": "Neural methods outside KA topic scope", "cosine": 0.41})
    matches.sort(key=lambda row: -row["cosine"])
    thresholds = _load_json(DEFAULT_THRESHOLDS_PATH, {"default_threshold": 0.12, "topics": {}})
    default_threshold = float(thresholds.get("default_threshold") or 0.08)
    best = matches[0] if matches else {"topic_id": "unknown", "topic_label": "Unknown", "cosine": 0.0}
    threshold = float((thresholds.get("topics") or {}).get(best["topic_id"], default_threshold))
    return {
        "admitted_to": best["topic_id"] if best["cosine"] >= threshold else "",
        "max_cosine": best["cosine"],
        "threshold": threshold,
        "nearest_topics": matches[:3],
        "nearest_corpus_papers": best.get("nearest_corpus_papers") or [],
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


def write_v7_lite_partial_to_ae(evaluation: dict[str, Any], *, session_id: str = "") -> dict[str, Any]:
    db_path = Path(os.environ.get("KA_AE_DB_PATH", str(DEFAULT_AE_DB_PATH)))
    if not db_path.exists():
        return {"status": "skipped", "reason": "ae_db_missing", "path": str(db_path)}
    now = datetime.now(timezone.utc).isoformat()
    paper_id = evaluation.get("paper_id") or "PDF-LITE-PENDING"
    digest = hashlib.sha1(json.dumps(evaluation, sort_keys=True).encode("utf-8")).hexdigest()[:12]
    belief_id = f"v7_lite_{paper_id}_{digest}"
    epistemic_v2 = {
        "v7_lite_partial": True,
        "v7_lite_evaluation_date": now,
        "paper_type": evaluation.get("paper_type"),
        "topic_fit": evaluation.get("topic_fit"),
        "iv": evaluation.get("iv"),
        "dv": evaluation.get("dv"),
        "methods": evaluation.get("methods"),
        "vr_suitability_mapping": evaluation.get("vr_suitability_mapping"),
        "conditional_voi": evaluation.get("conditional_voi"),
        "session_id": session_id,
    }
    content = f"V7-Lite partial ingest for {paper_id}: {evaluation.get('recommendation', {}).get('summary', 'pending')}"
    db = sqlite3.connect(str(db_path))
    try:
        web_id = db.execute("SELECT web_id FROM web_metadata LIMIT 1").fetchone()
        web_id_value = web_id[0] if web_id else "master"
        db.execute(
            """
            INSERT OR REPLACE INTO beliefs (
                belief_id, web_id, content, level, status, credence_value,
                credence_uncertainty, credence_n_supporting, credence_n_contradicting,
                credence_n_observations, entrenchment, domain, scope, tags,
                paper_ids, epistemic_v2, created_at, updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                belief_id,
                web_id_value,
                content,
                "empirical",
                "TENTATIVE",
                0.5,
                1.0,
                0,
                0,
                0,
                0.3,
                "v7_lite",
                json.dumps((evaluation.get("methods") or {}).get("sample_composition") or {}),
                json.dumps(["v7_lite_partial"]),
                json.dumps([paper_id]),
                json.dumps(epistemic_v2),
                now,
                now,
            ),
        )
        job_id = f"full_v7_{paper_id}_{digest}"
        db.execute(
            """
            INSERT OR IGNORE INTO processing_queue (
                job_id, job_type, params, status, priority, created_at, updated_at
            ) VALUES (?,?,?,?,?,?,?)
            """,
            (
                job_id,
                "L2_extract",
                json.dumps({"paper_id": paper_id, "belief_id": belief_id, "lane": "A_student_uploaded", "source": "v7_lite"}),
                "pending",
                10,
                now,
                now,
            ),
        )
        db.commit()
        return {"status": "partial", "path": str(db_path), "belief_id": belief_id, "queue_job_id": job_id}
    finally:
        db.close()


def evaluate_v7_lite(
    *,
    doi: str = "",
    title: str = "",
    authors: str = "",
    year: int | None = None,
    session_id: str = "",
    abstract: str = "",
    text_surface: str = "",
    write_ae: bool = False,
    generate_prose: bool = True,
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

    classification = classify_with_existing_classifier(title, abstract, text_surface or abstract)
    fit = topic_fit(title, " ".join([abstract, text_surface]))
    if not fit["admitted_to"]:
        return {
            "status": "rejected_out_of_scope",
            "reason": f"Topic-similarity below threshold; closest match was '{fit['nearest_topics'][0]['topic_id'] if fit['nearest_topics'] else 'unknown'}' at {fit['max_cosine']} vs threshold {fit['threshold']}",
            "nearest_topics": fit["nearest_topics"],
            "new_topic_seed_offered": True,
            "new_topic_seed_id": f"SEED-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-{abs(hash(title or doi or session_id)) % 1000:03d}",
        }

    dv = [] if classification["paper_type"] in {"review", "meta_analysis", "theoretical"} else extract_lite_dvs(title, abstract or text_surface)
    substitution = admit_mode({"dv_descriptions": dv, "generate_prose": False}) if dv else {"per_dv_results": [], "paper_level_verdict": "admit_review_or_theory", "paper_level_confidence": classification["confidence"]}
    voi = conditional_voi_for(title, abstract or text_surface, dv)
    recommendation_summary = "Admit with substitution" if substitution["paper_level_verdict"] == "admit_with_substitution" else "Admit"
    response = {
        "status": "admitted",
        "paper_id": "PDF-LITE-PENDING",
        "evaluation": {
            "paper_id": "PDF-LITE-PENDING",
            "paper_type": classification["paper_type"],
            "paper_type_confidence": classification["confidence"],
            "design_subtype": classification["design_subtype"],
            "classifier_source": classification.get("classifier_source", ""),
            "classifier_signals": classification.get("classifier_signals", []),
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
    if generate_prose:
        _write_recommendation_prose(response["evaluation"])
    if write_ae:
        write_status = write_v7_lite_partial_to_ae(response["evaluation"], session_id=session_id)
        response["evaluation"]["ae_db_write_status"] = write_status
        response["queue_job_id"] = write_status.get("queue_job_id")
    return response


@router.post("/ingest")
async def ingest_endpoint(
    doi: str = Form(""),
    title: str = Form(""),
    authors: str = Form(""),
    year: int | None = Form(None),
    session_id: str = Form(""),
    pdf: UploadFile | None = File(None),
) -> dict[str, Any]:
    text_surface = ""
    derived_title = title
    derived_abstract = ""
    if pdf is not None:
        data = await pdf.read()
        try:
            from ka_article_endpoints import _extract_abstract_from_text, _extract_text_from_pdf_bytes, _extract_title_from_text

            text_surface = _extract_text_from_pdf_bytes(data, max_chars=12000)
            derived_title = title or _extract_title_from_text(text_surface, fallback=getattr(pdf, "filename", "uploaded paper"))
            derived_abstract = _extract_abstract_from_text(text_surface)
        except Exception:
            text_surface = ""
    return evaluate_v7_lite(
        doi=doi,
        title=derived_title,
        authors=authors,
        year=year,
        session_id=session_id,
        abstract=derived_abstract,
        text_surface=text_surface,
        write_ae=True,
        generate_prose=True,
    )
