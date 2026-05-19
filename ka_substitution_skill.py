#!/usr/bin/env python3
"""Knowledge Atlas substitution-skill v1.

This is the deterministic substrate for the Week-1 Surface 4 / 4b skill. The
LLM may explain results later, but this module owns the graph lookup, ranking,
and refusal logic so substitutions cannot be invented in prose.
"""

from __future__ import annotations

import json
import math
import sqlite3
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ka_subscription_llm import call_subscription_llm


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_GRAPH_PATH = REPO_ROOT / "data" / "substitution_seed_graph.json"
DEFAULT_DB_PATH = REPO_ROOT / "data" / "substitution_graph.db"
AE_SUBSTITUTION_DB_PATH = Path("/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1_recovery/substitution_graph.db")
SUBSCRIPTION_LLM_PROSE_CONTRACT = "SUBSTITUTION_SKILL_SUBSCRIPTION_CLI_PROSE_CONTRACT_2026-05-18"
SUBSCRIPTION_LLM_COMMANDS = ["claude -p", "codex exec"]

router = APIRouter(prefix="/api/substitution_skill", tags=["substitution_skill"])


class DVDescription(BaseModel):
    name: str
    type: str = ""
    claimed_construct: str = ""


class AdmitModeRequest(BaseModel):
    paper_id: str | None = None
    dv_descriptions: list[DVDescription] = Field(default_factory=list)
    generate_prose: bool = True


class ChoiceModeRequest(BaseModel):
    topic_id: str
    project_constraints: dict[str, Any] = Field(default_factory=dict)
    generate_prose: bool = True


def load_graph(path: Path = DEFAULT_GRAPH_PATH) -> dict[str, Any]:
    db_override = os.environ.get("KA_SUBSTITUTION_GRAPH_DB", "").strip()
    if path == DEFAULT_GRAPH_PATH and db_override:
        return load_graph_from_db(Path(db_override))
    return json.loads(path.read_text())


def load_graph_from_db(db_path: Path) -> dict[str, Any]:
    db = sqlite3.connect(str(db_path))
    db.row_factory = sqlite3.Row
    try:
        constructs = []
        measures = []
        links = []
        for row in db.execute("SELECT * FROM constructs ORDER BY construct_id"):
            item = dict(row)
            item["aliases"] = json.loads(item.get("aliases") or "[]")
            item["proliferation_warning"] = json.loads(item.get("proliferation_warning") or "{}")
            constructs.append(item)
        for row in db.execute("SELECT * FROM measures ORDER BY measure_id"):
            item = dict(row)
            item["vr_tractable"] = bool(item.get("vr_tractable"))
            for key, default in [
                ("vr_tractability_conditions", {}),
                ("psychometric_profile", {}),
                ("construct_validity_per_paper", {}),
                ("hardware_required", []),
                ("canonical_references", []),
            ]:
                item[key] = json.loads(item.get(key) or json.dumps(default))
            measures.append(item)
        for row in db.execute("SELECT * FROM construct_measure_links ORDER BY link_id"):
            links.append(dict(row))
        return {
            "schema_version": "ka_substitution_graph_sqlite_v1",
            "constructs": constructs,
            "measures": measures,
            "construct_measure_links": links,
        }
    finally:
        db.close()


def init_substitution_graph_db(db_path: Path = DEFAULT_DB_PATH, graph_path: Path = DEFAULT_GRAPH_PATH) -> None:
    """Create and seed the SQLite substitution graph.

    The tables match `docs/SUBSTITUTION_SKILL_SPEC_2026-05-18.md`. Existing rows
    are replaced from the seed graph so local development remains reproducible.
    """
    graph = load_graph(graph_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(db_path))
    try:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS constructs (
                construct_id TEXT PRIMARY KEY,
                canonical_name TEXT NOT NULL,
                aliases JSON,
                family_theory_id TEXT,
                proliferation_warning JSON
            );
            CREATE TABLE IF NOT EXISTS measures (
                measure_id TEXT PRIMARY KEY,
                short_code TEXT NOT NULL,
                canonical_name TEXT NOT NULL,
                measurement_family TEXT NOT NULL,
                vr_tractable BOOLEAN NOT NULL,
                vr_tractability_conditions JSON,
                psychometric_profile JSON,
                construct_validity_per_paper JSON,
                administration_time_min INTEGER,
                hardware_required JSON,
                principal_pitfall TEXT,
                canonical_references JSON
            );
            CREATE TABLE IF NOT EXISTS construct_measure_links (
                link_id INTEGER PRIMARY KEY AUTOINCREMENT,
                construct_id TEXT NOT NULL REFERENCES constructs(construct_id),
                measure_id TEXT NOT NULL REFERENCES measures(measure_id),
                construct_validity FLOAT NOT NULL,
                field_acceptance INTEGER NOT NULL,
                canonical_paper_id TEXT,
                citation_count INTEGER,
                severity_average FLOAT,
                notes TEXT
            );
            DELETE FROM construct_measure_links;
            DELETE FROM measures;
            DELETE FROM constructs;
            """
        )
        for row in graph["constructs"]:
            db.execute(
                "INSERT INTO constructs VALUES (?,?,?,?,?)",
                (
                    row["construct_id"],
                    row["canonical_name"],
                    json.dumps(row.get("aliases") or []),
                    row.get("family_theory_id") or "",
                    json.dumps(row.get("proliferation_warning") or {}),
                ),
            )
        for row in graph["measures"]:
            db.execute(
                "INSERT INTO measures VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    row["measure_id"],
                    row["short_code"],
                    row["canonical_name"],
                    row["measurement_family"],
                    int(bool(row["vr_tractable"])),
                    json.dumps(row.get("vr_tractability_conditions") or {}),
                    json.dumps(row.get("psychometric_profile") or {}),
                    json.dumps(row.get("construct_validity_per_paper") or {}),
                    row.get("administration_time_min"),
                    json.dumps(row.get("hardware_required") or []),
                    row.get("principal_pitfall") or "",
                    json.dumps(row.get("canonical_references") or []),
                ),
            )
        for row in graph["construct_measure_links"]:
            db.execute(
                """
                INSERT INTO construct_measure_links (
                    construct_id, measure_id, construct_validity, field_acceptance,
                    canonical_paper_id, citation_count, severity_average, notes
                ) VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    row["construct_id"],
                    row["measure_id"],
                    float(row["construct_validity"]),
                    int(row["field_acceptance"]),
                    row.get("canonical_paper_id") or "",
                    int(row.get("citation_count") or 0),
                    float(row.get("severity_average") or 0),
                    row.get("notes") or "",
                ),
            )
        db.commit()
    finally:
        db.close()


def _norm(value: str) -> str:
    return " ".join(str(value or "").lower().replace("-", " ").replace("_", " ").split())


def _index_graph(graph: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], list[dict[str, Any]]]:
    constructs = {row["construct_id"]: row for row in graph.get("constructs", [])}
    measures = {row["measure_id"]: row for row in graph.get("measures", [])}
    return constructs, measures, list(graph.get("construct_measure_links", []))


def resolve_construct(text: str, graph: dict[str, Any]) -> tuple[str | None, float, dict[str, Any] | None]:
    needle = _norm(text)
    if not needle:
        return None, 0.0, None
    best: tuple[str | None, float, dict[str, Any] | None] = (None, 0.0, None)
    for row in graph.get("constructs", []):
        names = [row.get("construct_id", ""), row.get("canonical_name", ""), *(row.get("aliases") or [])]
        for name in names:
            n = _norm(name)
            if not n:
                continue
            if needle == n:
                score = 1.0
            elif needle in n or n in needle:
                score = min(len(needle), len(n)) / max(len(needle), len(n))
            else:
                score = 0.0
            if score > best[1]:
                best = (row["construct_id"], score, row)
    return best


def resolve_measure(text: str, graph: dict[str, Any]) -> dict[str, Any] | None:
    needle = _norm(text)
    if not needle:
        return None
    for row in graph.get("measures", []):
        names = [row.get("short_code", ""), row.get("canonical_name", "")]
        if any(_norm(name) == needle or needle in _norm(name) for name in names):
            return row
    if "cortisol" in needle or "biomarker" in needle or "salivary" in needle or "biochemical" in needle:
        return next((row for row in graph.get("measures", []) if row["short_code"] == "x5.biomarker"), None)
    if "fmri" in needle or "bold" in needle:
        return next((row for row in graph.get("measures", []) if row["short_code"] == "x1.fmri"), None)
    if "iat" in needle or "implicit association" in needle:
        return next((row for row in graph.get("measures", []) if row["short_code"] == "f2.iat"), None)
    if "psychomotor vigilance" in needle or needle == "pvt":
        return next((row for row in graph.get("measures", []) if row["short_code"] == "f2.pvt"), None)
    if "n back" in needle or "nback" in needle:
        return next((row for row in graph.get("measures", []) if row["short_code"] == "f2.nback"), None)
    if "matb" in needle or "multi attribute task battery" in needle:
        return next((row for row in graph.get("measures", []) if row["short_code"] == "f2.matb"), None)
    if "sleepiness" in needle or "mood rating" in needle or "state rating" in needle:
        return next((row for row in graph.get("measures", []) if row["short_code"] == "f3.state_rating"), None)
    if "electrophysiological" in needle or "mobile eeg" in needle or needle == "eeg":
        return next((row for row in graph.get("measures", []) if row["short_code"] == "f4.mobile_eeg"), None)
    if "q sort" in needle or "q-sort" in needle or "card sort" in needle:
        return next((row for row in graph.get("measures", []) if row["short_code"] == "f2.qsort"), None)
    return None


def _links_for_construct(graph: dict[str, Any], construct_id: str) -> list[dict[str, Any]]:
    return [row for row in graph.get("construct_measure_links", []) if row["construct_id"] == construct_id]


def _candidate_payload(link: dict[str, Any], measure: dict[str, Any], project_constraints: dict[str, Any] | None = None) -> dict[str, Any]:
    hardware = set((project_constraints or {}).get("lab_hardware") or [])
    required = set(measure.get("hardware_required") or [])
    hardware_satisfied = not required or bool(hardware.intersection(required)) or "headset" in required
    validity = float(link.get("construct_validity") or 0)
    field_acceptance = int(link.get("field_acceptance") or 0)
    severity = float(link.get("severity_average") or 0)
    time_within_budget = int(measure.get("administration_time_min") or 0) <= 25
    feasibility = (
        validity * 0.42
        + min(math.log1p(field_acceptance) / math.log(51), 1.0) * 0.2
        + severity * 0.2
        + (0.1 if hardware_satisfied else 0)
        + (0.08 if time_within_budget else 0)
    )
    return {
        "measure_short_code": measure["short_code"],
        "measure_id": measure["measure_id"],
        "canonical_name": measure["canonical_name"],
        "construct_validity": round(validity, 3),
        "field_acceptance": field_acceptance,
        "severity_average": round(severity, 3),
        "psychometric_summary": (measure.get("psychometric_profile") or {}).get("validity_note", ""),
        "principal_pitfall": measure.get("principal_pitfall") or "",
        "hardware_satisfied": hardware_satisfied,
        "time_within_budget": time_within_budget,
        "estimated_administration_min": measure.get("administration_time_min"),
        "feasibility_score": round(feasibility, 3),
        "trade_offs": link.get("notes") or "",
    }


def _llm_prose_required(stage: str) -> dict[str, Any]:
    return {
        "status": "requires_subscription_cli_llm",
        "stage": stage,
        "contract": SUBSCRIPTION_LLM_PROSE_CONTRACT,
        "allowed_commands": SUBSCRIPTION_LLM_COMMANDS,
        "api_access_allowed": False,
        "python_public_prose_allowed": False,
        "python_role": "assemble structured evidence, validate graph, rank candidates, and reject unsafe outputs only",
    }


def _clean_llm_prose(value: str, max_words: int) -> str:
    text = " ".join(str(value or "").split())
    forbidden = ["the dyk should", "this card should", "the card should", "python", "template fallback"]
    if not text or any(marker in text.lower() for marker in forbidden):
        return ""
    words = text.split()
    if len(words) > max_words:
        text = " ".join(words[:max_words]).rstrip(" ,;:") + "."
    return text


def _write_admit_explanation(row: dict[str, Any]) -> None:
    prompt = f"""You are the Knowledge Atlas substitution-skill science writer.
Use only the structured facts below. Do not invent substitutes. Do not mention this prompt.
Write one public-facing explanation in 80 words or fewer.

Facts:
{json.dumps(row, indent=2)}
"""
    result = call_subscription_llm(prompt, env_var="KA_SUBSTITUTION_LLM_COMMAND", timeout=90)
    text = _clean_llm_prose(result.text, 80) if result.ok else ""
    if text:
        row["explanation"] = text
        row["explanation_generation"] = {
            "status": "subscription_cli_llm_authored",
            "contract": SUBSCRIPTION_LLM_PROSE_CONTRACT,
            "command": " ".join(result.command),
            "api_access_allowed": False,
            "python_public_prose_allowed": False,
        }


def _write_choice_recommendation(result_payload: dict[str, Any]) -> None:
    prompt = f"""You are the Knowledge Atlas substitution-skill science writer.
Use only the structured ranking below. Do not invent measures. Do not hide uncertainty.
Write one public-facing recommendation in 200 words or fewer.

Facts:
{json.dumps(result_payload, indent=2)}
"""
    result = call_subscription_llm(prompt, env_var="KA_SUBSTITUTION_LLM_COMMAND", timeout=90)
    text = _clean_llm_prose(result.text, 200) if result.ok else ""
    if text:
        result_payload["recommendation_prose"] = text
        result_payload["recommendation_generation"] = {
            "status": "subscription_cli_llm_authored",
            "contract": SUBSCRIPTION_LLM_PROSE_CONTRACT,
            "command": " ".join(result.command),
            "api_access_allowed": False,
            "python_public_prose_allowed": False,
        }


def admit_mode(payload: dict[str, Any], graph: dict[str, Any] | None = None) -> dict[str, Any]:
    graph = graph or load_graph()
    _, measures, _ = _index_graph(graph)
    results = []
    for dv in payload.get("dv_descriptions") or []:
        dv_name = str(dv.get("name") or "")
        claimed = str(dv.get("claimed_construct") or dv_name)
        construct_id, confidence, construct = resolve_construct(claimed, graph)
        measure = resolve_measure(dv_name, graph)
        if not construct_id or confidence < 0.4:
            row = {
                    "dv_input": dv_name,
                    "claimed_construct": claimed,
                    "resolved_construct_id": None,
                    "measure_short_code": measure.get("short_code") if measure else "",
                    "vr_tractable_as_is": bool(measure and measure.get("vr_tractable")),
                    "substitution_candidates": [],
                    "admit_verdict": "reject",
                    "confidence": round(confidence, 3),
                    "refusal_reason": "no_construct_match",
                    "explanation": "",
                    "explanation_generation": _llm_prose_required("admit_mode_per_dv_explanation"),
                }
            if payload.get("generate_prose", True):
                _write_admit_explanation(row)
            results.append(row)
            continue
        candidates = []
        for link in _links_for_construct(graph, construct_id):
            linked_measure = measures[link["measure_id"]]
            if linked_measure.get("vr_tractable") and linked_measure.get("measure_id") != (measure or {}).get("measure_id"):
                candidates.append(_candidate_payload(link, linked_measure))
        candidates.sort(key=lambda item: (-item["construct_validity"], -item["field_acceptance"], -item["severity_average"]))
        as_is = bool(measure and measure.get("vr_tractable"))
        verdict = "admit_as_is" if as_is else ("admit_with_substitution" if candidates else "reject")
        warning = construct.get("proliferation_warning") if construct else {}
        row = {
                "dv_input": dv_name,
                "claimed_construct": claimed,
                "resolved_construct_id": construct_id,
                "measure_short_code": measure.get("short_code") if measure else "",
                "vr_tractable_as_is": as_is,
                "substitution_candidates": candidates,
                "admit_verdict": verdict,
                "confidence": round(max(confidence, candidates[0]["construct_validity"] if candidates else 0), 3),
                "proliferation_warning": warning if warning and (warning.get("jangle_with") or warning.get("jingle_with")) else {},
                "explanation": "",
                "explanation_generation": _llm_prose_required("admit_mode_per_dv_explanation"),
            }
        if payload.get("generate_prose", True):
            _write_admit_explanation(row)
        results.append(row)
    verdicts = [row["admit_verdict"] for row in results]
    if not verdicts:
        paper_verdict = "reject_dv_missing"
    elif any(value == "reject" for value in verdicts):
        paper_verdict = "reject_dv_unmeasurable"
    elif all(value == "admit_as_is" for value in verdicts):
        paper_verdict = "admit"
    else:
        paper_verdict = "admit_with_substitution"
    confidence_values = [float(row.get("confidence") or 0) for row in results]
    return {
        "per_dv_results": results,
        "paper_level_verdict": paper_verdict,
        "paper_level_confidence": round(sum(confidence_values) / len(confidence_values), 3) if confidence_values else 0.0,
        "prose_contract": _llm_prose_required("admit_mode_explanations"),
    }


def choice_mode(payload: dict[str, Any], graph: dict[str, Any] | None = None) -> dict[str, Any]:
    graph = graph or load_graph()
    topic_id = str(payload.get("topic_id") or "").strip()
    construct_id, confidence, _ = resolve_construct(topic_id, graph)
    if not construct_id:
        construct_id = topic_id
    _, measures, _ = _index_graph(graph)
    candidates = []
    for link in _links_for_construct(graph, construct_id):
        measure = measures[link["measure_id"]]
        if measure.get("vr_tractable"):
            candidates.append(_candidate_payload(link, measure, payload.get("project_constraints") or {}))
    candidates.sort(key=lambda item: (-item["feasibility_score"], -item["construct_validity"], -item["field_acceptance"]))
    for index, item in enumerate(candidates, start=1):
        item["rank"] = index
        item["construct_indexed"] = construct_id
    result_payload = {
        "resolved_construct_id": construct_id,
        "construct_resolution_confidence": round(confidence, 3),
        "candidate_measures": candidates,
        "recommendation_prose": "",
        "recommendation_generation": _llm_prose_required("choice_mode_recommendation_prose"),
    }
    if payload.get("generate_prose", True):
        _write_choice_recommendation(result_payload)
    return result_payload


@router.post("/admit_mode")
def admit_mode_endpoint(payload: AdmitModeRequest) -> dict[str, Any]:
    return admit_mode(payload.model_dump())


@router.post("/choice_mode")
def choice_mode_endpoint(payload: ChoiceModeRequest) -> dict[str, Any]:
    return choice_mode(payload.model_dump())
