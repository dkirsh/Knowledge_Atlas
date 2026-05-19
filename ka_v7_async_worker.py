#!/usr/bin/env python3
"""Async full-V7 worker for V7-Lite queue rows.

The worker consumes V7-Lite jobs from Article Eater's `processing_queue`,
updates the same partial belief row, and enforces the subscription-CLI-only
rule for public science prose. Deterministic Python code may compute structured
fields; it must not author science-summary or PNU prose.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ka_subscription_llm import call_subscription_llm
from ka_v7_lite import DEFAULT_AE_DB_PATH, V7_LITE_FULL_WORKER_CONTRACT


FULL_V7_ASYNC_WORKER_VERSION = "2026-05-19.v1"
FULL_V7_PROSE_CONTRACT = "FULL_V7_ASYNC_SUBSCRIPTION_CLI_PUBLIC_PROSE_CONTRACT_2026-05-19"
SUBSCRIPTION_LLM_COMMANDS = ["claude -p", "codex exec"]

VOI_TARGETS = {
    "target_1_better_stimuli": "Does the paper improve stimulus ecological validity?",
    "target_2_better_measures": "Does the paper improve the measurement strategy?",
    "target_3_better_design": "Does the paper improve causal or comparative design?",
    "target_4_deconfounding": "Does the paper reduce a known confound?",
    "target_5_mechanism_weak_links": "Does the paper test a weak mechanism link?",
    "target_6_boundary_conditions": "Does the paper clarify scope or boundary conditions?",
    "target_7_theory_discrimination": "Does the paper discriminate between theories?",
    "target_8_replication_priority": "Does the paper provide or motivate replication?",
    "target_9_design_translation": "Does the paper translate into design practice?",
    "target_10_weird_extension": "Does the paper extend beyond WEIRD samples?",
}


@dataclass(frozen=True)
class QueueJob:
    job_id: str
    job_type: str
    params: dict[str, Any]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_loads(value: Any, default: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if not value:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def _connect(db_path: Path) -> sqlite3.Connection:
    db = sqlite3.connect(str(db_path))
    db.row_factory = sqlite3.Row
    return db


def _is_v7_lite_job(row: sqlite3.Row, params: dict[str, Any]) -> bool:
    return (
        str(row["job_id"]).startswith("full_v7_")
        or params.get("source") == "v7_lite"
        or params.get("worker_contract") == V7_LITE_FULL_WORKER_CONTRACT
    )


def claim_next_job(db: sqlite3.Connection, *, job_id: str = "", dry_run: bool = False) -> QueueJob | None:
    """Claim one pending V7-Lite full-worker job."""
    db.execute("BEGIN IMMEDIATE")
    try:
        if job_id:
            rows = db.execute(
                """
                SELECT job_id, job_type, params
                FROM processing_queue
                WHERE job_id = ? AND status = 'pending'
                """,
                (job_id,),
            ).fetchall()
        else:
            rows = db.execute(
                """
                SELECT job_id, job_type, params
                FROM processing_queue
                WHERE status = 'pending' AND job_type = 'L2_extract'
                ORDER BY priority ASC, created_at ASC, job_id ASC
                LIMIT 50
                """
            ).fetchall()
        for row in rows:
            params = _json_loads(row["params"], {})
            if row["job_type"] != "L2_extract" or not _is_v7_lite_job(row, params):
                continue
            if not dry_run:
                now = _now()
                db.execute(
                    """
                    UPDATE processing_queue
                    SET status = 'running', started_at = COALESCE(started_at, ?), updated_at = ?
                    WHERE job_id = ? AND status = 'pending'
                    """,
                    (now, now, row["job_id"]),
                )
            db.commit()
            return QueueJob(job_id=row["job_id"], job_type=row["job_type"], params=params)
        db.commit()
        return None
    except Exception:
        db.rollback()
        raise


def _belief_for_job(db: sqlite3.Connection, belief_id: str) -> sqlite3.Row:
    row = db.execute(
        "SELECT belief_id, content, status, paper_ids, epistemic_v2 FROM beliefs WHERE belief_id = ?",
        (belief_id,),
    ).fetchone()
    if row is None:
        raise ValueError(f"belief row not found for {belief_id}")
    return row


def _evaluation_from(epistemic_v2: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    evaluation = _json_loads(params.get("evaluation"), {})
    if evaluation:
        return evaluation
    return {
        "paper_id": params.get("paper_id") or "PDF-LITE-PENDING",
        "paper_type": epistemic_v2.get("paper_type"),
        "topic_fit": epistemic_v2.get("topic_fit"),
        "iv": epistemic_v2.get("iv"),
        "dv": epistemic_v2.get("dv"),
        "methods": epistemic_v2.get("methods"),
        "vr_suitability_mapping": epistemic_v2.get("vr_suitability_mapping"),
        "conditional_voi": epistemic_v2.get("conditional_voi"),
        "recommendation": {"summary": "", "rationale": ""},
    }


def _rating(value: Any) -> str:
    if isinstance(value, str) and value in {"high", "medium", "low", "na"}:
        return value
    return "na"


def compute_full_conditional_voi(evaluation: dict[str, Any]) -> dict[str, dict[str, str]]:
    lite = _json_loads(evaluation.get("conditional_voi"), {})
    methods = _json_loads(evaluation.get("methods"), {})
    dv = evaluation.get("dv") or []
    substitution = evaluation.get("vr_suitability_mapping") or []
    paper_type = str(evaluation.get("paper_type") or "")
    topic_fit = _json_loads(evaluation.get("topic_fit"), {})
    design = str(methods.get("design") or "").lower()
    sample = _json_loads(methods.get("sample_composition"), {})

    design_rating = "medium" if design and "unclassified" not in design else "low"
    mechanism_rating = "medium" if any(row.get("type") in {"biomarker", "task_embedded_performance"} for row in dv) else "low"
    boundary_rating = "medium" if sample else "low"
    theory_rating = "low"
    replication_rating = "high" if paper_type == "replication" else "low"
    translation_rating = "medium" if substitution or topic_fit.get("admitted_to") else "low"

    computed = {
        "target_1_better_stimuli": (_rating(lite.get("target_1_better_stimuli")), "copied from V7-Lite synchronous pass"),
        "target_2_better_measures": (_rating(lite.get("target_2_better_measures")), "copied from V7-Lite synchronous pass"),
        "target_3_better_design": (design_rating, "estimated from extracted design subtype; full methods review may revise"),
        "target_4_deconfounding": (_rating(lite.get("target_4_deconfounding")), "copied from V7-Lite synchronous pass"),
        "target_5_mechanism_weak_links": (mechanism_rating, "estimated from measurement class; mechanism-chain review remains provisional"),
        "target_6_boundary_conditions": (boundary_rating, "estimated from extracted sample-composition fields"),
        "target_7_theory_discrimination": (theory_rating, "not enough synchronous evidence for theory-discrimination credit"),
        "target_8_replication_priority": (replication_rating, "high only when the classifier identifies a replication paper"),
        "target_9_design_translation": (translation_rating, "estimated from admitted topic and substitution mapping"),
        "target_10_weird_extension": (_rating(lite.get("target_10_weird_extension")), "copied from V7-Lite synchronous pass"),
    }
    return {
        target: {
            "rating": rating,
            "question": VOI_TARGETS[target],
            "basis": basis,
            "status": "provisional_full_v7_async",
        }
        for target, (rating, basis) in computed.items()
    }


def build_argumentation_scaffold(evaluation: dict[str, Any], full_voi: dict[str, Any]) -> dict[str, Any]:
    topic_fit = _json_loads(evaluation.get("topic_fit"), {})
    dv = evaluation.get("dv") or []
    methods = _json_loads(evaluation.get("methods"), {})
    admitted_topic = topic_fit.get("admitted_to") or ""
    grounds = []
    if admitted_topic:
        grounds.append({"type": "topic_fit", "value": admitted_topic, "cosine": topic_fit.get("max_cosine")})
    for row in dv:
        grounds.append({"type": "measure", "name": row.get("name"), "measure_type": row.get("type")})
    if methods.get("design"):
        grounds.append({"type": "design", "value": methods.get("design")})
    challenges = [
        {
            "challenge": "V7-Lite fields are sufficient for triage, not final warrant grading.",
            "basis": "science summary, PNU, and full literature challenge review require subscription-LLM or human authoring.",
        }
    ]
    if full_voi.get("target_7_theory_discrimination", {}).get("rating") == "low":
        challenges.append({
            "challenge": "Theory discrimination is not yet established.",
            "basis": "No high-threshold theory-matching lane has been run for this upload.",
        })
    return {
        "status": "structured_scaffold_pending_review",
        "claims": [
            {
                "claim": "This paper is provisionally admissible to the Knowledge Atlas topic if the topic-fit and extracted methods survive full review.",
                "type": "admission_claim",
            }
        ],
        "grounds": grounds,
        "warrants": [
            {
                "warrant": "A paper can enter the Atlas when topic fit, measurement tractability, and conditional VOI are sufficient for a student or researcher to act on.",
                "source": "V7-Lite build spec and VOI panel synthesis",
            }
        ],
        "challenges": challenges,
        "python_public_prose_allowed": False,
    }


def _llm_required(stage: str, result: Any = None) -> dict[str, Any]:
    error = getattr(result, "error", "") if result is not None else ""
    command = " ".join(getattr(result, "command", ()) or ()) if result is not None else ""
    return {
        "status": "requires_subscription_cli_llm",
        "stage": stage,
        "contract": FULL_V7_PROSE_CONTRACT,
        "allowed_commands": SUBSCRIPTION_LLM_COMMANDS,
        "attempted_command": command,
        "error": error,
        "api_access_allowed": False,
        "python_public_prose_allowed": False,
    }


def _clean_llm_text(value: str, max_words: int) -> str:
    text = " ".join(str(value or "").split())
    forbidden = ["this prompt", "template fallback", "python", "as an ai language model"]
    if not text or any(marker in text.lower() for marker in forbidden):
        return ""
    words = text.split()
    if len(words) > max_words:
        text = " ".join(words[:max_words]).rstrip(" ,;:") + "."
    return text


def _parse_llm_json(text: str) -> dict[str, Any]:
    stripped = str(text or "").strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, flags=re.DOTALL)
    if fenced:
        stripped = fenced.group(1)
        return json.loads(stripped)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass
    starts = [match.start() for match in re.finditer(r"\{", stripped)]
    for start in reversed(starts):
        depth = 0
        in_string = False
        escape = False
        for index in range(start, len(stripped)):
            char = stripped[index]
            if escape:
                escape = False
                continue
            if char == "\\" and in_string:
                escape = True
                continue
            if char == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    candidate = stripped[start:index + 1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        break
    raise json.JSONDecodeError("No JSON object found in subscription CLI output", stripped, 0)


def write_subscription_public_prose(evaluation: dict[str, Any], full_voi: dict[str, Any]) -> dict[str, Any]:
    prompt = f"""You are the Knowledge Atlas full-V7 science writer.
Use only the structured packet below. Do not invent papers, results, figures, theory names, or measurements.
Return strict JSON with:
- science_summary: 250-400 words, public-facing.
- plausible_neural_explanation: 120-220 words, explicitly provisional.
- argument_importance: 60-120 words.
- limitations: 60-120 words.

Python is not allowed to author these public prose fields. If the packet is insufficient, say so inside the relevant field.

Structured packet:
{json.dumps({"evaluation": evaluation, "full_conditional_voi": full_voi}, indent=2)}
"""
    result = call_subscription_llm(prompt, env_var="KA_FULL_V7_WORKER_LLM_COMMAND", timeout=180)
    if not result.ok:
        required = _llm_required("full_v7_public_prose", result)
        return {
            "science_summary": {"text": "", "generation": required},
            "plausible_neural_explanation": {"text": "", "generation": required},
            "argument_importance": {"text": "", "generation": required},
            "limitations": {"text": "", "generation": required},
        }
    try:
        parsed = _parse_llm_json(result.text)
    except Exception:
        required = _llm_required("full_v7_public_prose_json_parse", result)
        return {
            "science_summary": {"text": "", "generation": required},
            "plausible_neural_explanation": {"text": "", "generation": required},
            "argument_importance": {"text": "", "generation": required},
            "limitations": {"text": "", "generation": required},
        }
    generation = {
        "status": "subscription_cli_llm_authored",
        "contract": FULL_V7_PROSE_CONTRACT,
        "command": " ".join(result.command),
        "api_access_allowed": False,
        "python_public_prose_allowed": False,
    }
    return {
        "science_summary": {"text": _clean_llm_text(parsed.get("science_summary") or "", 450), "generation": generation},
        "plausible_neural_explanation": {"text": _clean_llm_text(parsed.get("plausible_neural_explanation") or "", 240), "generation": generation},
        "argument_importance": {"text": _clean_llm_text(parsed.get("argument_importance") or "", 140), "generation": generation},
        "limitations": {"text": _clean_llm_text(parsed.get("limitations") or "", 140), "generation": generation},
    }


def build_full_v7_result(evaluation: dict[str, Any], *, generate_prose: bool = True) -> dict[str, Any]:
    full_voi = compute_full_conditional_voi(evaluation)
    result = {
        "worker_contract": V7_LITE_FULL_WORKER_CONTRACT,
        "worker_version": FULL_V7_ASYNC_WORKER_VERSION,
        "completed_at": _now(),
        "paper_id": evaluation.get("paper_id") or "PDF-LITE-PENDING",
        "paper_type": evaluation.get("paper_type"),
        "source_metadata": evaluation.get("source_metadata") or {},
        "topic_fit": evaluation.get("topic_fit"),
        "iv": evaluation.get("iv"),
        "dv": evaluation.get("dv"),
        "methods": evaluation.get("methods"),
        "vr_suitability_mapping": evaluation.get("vr_suitability_mapping"),
        "full_conditional_voi": full_voi,
        "argumentation": build_argumentation_scaffold(evaluation, full_voi),
    }
    if generate_prose:
        result.update(write_subscription_public_prose(evaluation, full_voi))
    else:
        required = _llm_required("full_v7_public_prose")
        result.update({
            "science_summary": {"text": "", "generation": required},
            "plausible_neural_explanation": {"text": "", "generation": required},
            "argument_importance": {"text": "", "generation": required},
            "limitations": {"text": "", "generation": required},
        })
    prose_statuses = {
        result.get("science_summary", {}).get("generation", {}).get("status"),
        result.get("plausible_neural_explanation", {}).get("generation", {}).get("status"),
    }
    result["completion_status"] = (
        "full_v7_async_complete"
        if prose_statuses == {"subscription_cli_llm_authored"}
        else "full_v7_structured_complete_public_prose_pending"
    )
    return result


def complete_job(db: sqlite3.Connection, job: QueueJob, *, generate_prose: bool = True, dry_run: bool = False) -> dict[str, Any]:
    belief_id = str(job.params.get("belief_id") or "")
    if not belief_id:
        raise ValueError(f"job {job.job_id} is missing params.belief_id")
    belief = _belief_for_job(db, belief_id)
    epistemic_v2 = _json_loads(belief["epistemic_v2"], {})
    evaluation = _evaluation_from(epistemic_v2, job.params)
    result = build_full_v7_result(evaluation, generate_prose=generate_prose)

    updated_epistemic = dict(epistemic_v2)
    updated_epistemic.update({
        "v7_lite_partial": False,
        "v7_lite_partial_superseded": True,
        "full_v7_async_completed": True,
        "full_v7_async_completed_at": result["completed_at"],
        "full_v7_async_worker_version": FULL_V7_ASYNC_WORKER_VERSION,
        "full_v7_result": result,
        "full_conditional_voi": result["full_conditional_voi"],
        "science_summary": result["science_summary"],
        "plausible_neural_explanation": result["plausible_neural_explanation"],
        "argumentation": result["argumentation"],
    })
    if not dry_run:
        now = _now()
        content = f"Full V7 async ingest completed for {result['paper_id']}; prose status: {result['completion_status']}"
        db.execute(
            """
            UPDATE beliefs
            SET epistemic_v2 = ?, content = ?, status = ?, updated_at = ?
            WHERE belief_id = ?
            """,
            (json.dumps(updated_epistemic, sort_keys=True), content, "TENTATIVE", now, belief_id),
        )
        db.execute(
            """
            UPDATE processing_queue
            SET status = 'complete', completed_at = ?, updated_at = ?, result = ?, error = NULL
            WHERE job_id = ?
            """,
            (now, now, json.dumps({"belief_id": belief_id, "completion_status": result["completion_status"]}, sort_keys=True), job.job_id),
        )
        db.commit()
    return {"job_id": job.job_id, "belief_id": belief_id, "result": result}


def fail_job(db: sqlite3.Connection, job_id: str, error: str) -> None:
    now = _now()
    db.execute(
        """
        UPDATE processing_queue
        SET status = 'failed', completed_at = ?, updated_at = ?, error = ?
        WHERE job_id = ?
        """,
        (now, now, error[:1000], job_id),
    )
    db.commit()


def run_once(db_path: Path, *, job_id: str = "", generate_prose: bool = True, dry_run: bool = False) -> dict[str, Any]:
    if not db_path.exists():
        return {"status": "skipped", "reason": "ae_db_missing", "path": str(db_path)}
    db = _connect(db_path)
    try:
        job = claim_next_job(db, job_id=job_id, dry_run=dry_run)
        if job is None:
            return {"status": "idle", "path": str(db_path)}
        try:
            completed = complete_job(db, job, generate_prose=generate_prose, dry_run=dry_run)
        except Exception as exc:
            if not dry_run:
                fail_job(db, job.job_id, str(exc))
            return {"status": "failed", "job_id": job.job_id, "error": str(exc)}
        return {"status": "complete", **completed}
    finally:
        db.close()


def run_loop(
    db_path: Path,
    *,
    limit: int = 1,
    poll_seconds: float = 5.0,
    generate_prose: bool = True,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    completed = 0
    while limit <= 0 or completed < limit:
        result = run_once(db_path, generate_prose=generate_prose, dry_run=dry_run)
        results.append(result)
        if result["status"] in {"complete", "failed"}:
            completed += 1
            continue
        if limit > 0:
            break
        time.sleep(poll_seconds)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the KA V7-Lite full async worker.")
    parser.add_argument("--db", default=os.environ.get("KA_AE_DB_PATH", str(DEFAULT_AE_DB_PATH)))
    parser.add_argument("--job-id", default="")
    parser.add_argument("--limit", type=int, default=1, help="Number of jobs to process; 0 means watch indefinitely.")
    parser.add_argument("--poll-seconds", type=float, default=5.0)
    parser.add_argument("--no-prose", action="store_true", help="Complete structured fields and leave public prose pending subscription LLM.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.job_id:
        results = [run_once(Path(args.db), job_id=args.job_id, generate_prose=not args.no_prose, dry_run=args.dry_run)]
    else:
        results = run_loop(
            Path(args.db),
            limit=args.limit,
            poll_seconds=args.poll_seconds,
            generate_prose=not args.no_prose,
            dry_run=args.dry_run,
        )
    for result in results:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if any(result["status"] == "failed" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
