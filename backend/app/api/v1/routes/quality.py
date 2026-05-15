from __future__ import annotations

import os
import json
import sqlite3
import sys
from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict


REPO_ROOT = Path(__file__).resolve().parents[5]
ATLAS_SHARED_SRC = REPO_ROOT.parent / "atlas_shared" / "src"
if ATLAS_SHARED_SRC.exists() and str(ATLAS_SHARED_SRC) not in sys.path:
    sys.path.insert(0, str(ATLAS_SHARED_SRC))

from atlas_shared.claim_strengths import (  # noqa: E402
    ClaimStrengthsWeaknesses,
    Warrant,
    aggregate_claim_strengths,
)
from atlas_shared.literature_body import (  # noqa: E402
    LiteratureBodyQuality,
    aggregate_literature_body_quality,
)
from atlas_shared.paper_quality import (  # noqa: E402
    PaperQualityFingerprint,
    QualityFingerprintEnvelope,
    SampleOverlapEdge,
    WEIGHTING_FUNCTION_VERSION,
    normalize_paper_id,
)


DEFAULT_DB_PATH = REPO_ROOT / "data" / "paper_quality_blackboard.db"


class AdjudicationDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    queue_id: int
    adjudicated_value: Any
    adjudicator_id: str
    adjudicator_notes: str = ""
    status: str = "resolved"


class AdjudicationDecisionResponse(BaseModel):
    ok: bool
    queue_id: int
    weighting_function_version: str


router = APIRouter(prefix="/api/v1/quality", tags=["quality"])
admin_router = APIRouter(prefix="/api/v1/admin/paper_quality", tags=["paper-quality-admin"])


def db_path() -> Path:
    return Path(os.environ.get("KA_PAPER_QUALITY_DB", DEFAULT_DB_PATH))


@contextmanager
def connect() -> Iterable[sqlite3.Connection]:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def require_admin(x_admin_token: str = Header(default="")) -> None:
    expected = os.environ.get("KA_ADMIN_TOKEN")
    if not expected:
        if os.environ.get("KA_ADMIN_ALLOW_OPEN") == "1":
            return
        raise HTTPException(503, "Admin token is not configured")
    if x_admin_token != expected:
        raise HTTPException(401, "Invalid X-Admin-Token")


def _maybe_refreshing(response: Response) -> None:
    if os.environ.get("KA_PAPER_QUALITY_REFRESHING") == "1":
        retry_after = os.environ.get("KA_PAPER_QUALITY_RETRY_AFTER", "300")
        response.headers["Retry-After"] = retry_after
        raise HTTPException(
            503,
            "Paper-quality materialized view is refreshing",
            headers={"Retry-After": retry_after},
        )
    with connect() as conn:
        if not _table_exists(conn, "paper_quality_refresh_state"):
            return
        row = conn.execute(
            "SELECT status, retry_after_seconds FROM paper_quality_refresh_state "
            "ORDER BY updated_at DESC LIMIT 1"
        ).fetchone()
    if row and row["status"] == "refreshing":
        retry_after = str(row["retry_after_seconds"] or 300)
        response.headers["Retry-After"] = retry_after
        raise HTTPException(
            503,
            "Paper-quality materialized view is refreshing",
            headers={"Retry-After": retry_after},
        )


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('table', 'view') AND name = ?",
        (name,),
    ).fetchone()
    return row is not None


def _fingerprints(conn: sqlite3.Connection, *, topic: str | None = None, design_type: str | None = None) -> list[PaperQualityFingerprint]:
    sql = "SELECT * FROM paper_quality_fingerprints"
    clauses: list[str] = []
    params: list[Any] = []
    if design_type:
        clauses.append("design_type = ?")
        params.append(design_type)
    if topic and _table_exists(conn, "paper_quality_topic_memberships"):
        sql = (
            "SELECT pq.* FROM paper_quality_fingerprints pq "
            "JOIN paper_quality_topic_memberships tm ON tm.paper_id = pq.paper_id"
        )
        clauses.append("tm.topic_id = ?")
        params.append(topic)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    rows = conn.execute(sql, params).fetchall()
    return [PaperQualityFingerprint.from_sql_row(dict(row)) for row in rows]


def _claim_warrants(conn: sqlite3.Connection, claim_id: str) -> list[Warrant]:
    if _table_exists(conn, "claim_paper_warrants"):
        rows = conn.execute(
            "SELECT paper_id, direction, warrant_weight FROM claim_paper_warrants WHERE claim_id = ?",
            (claim_id,),
        ).fetchall()
        return [
            Warrant(
                paper_id=normalize_paper_id(row["paper_id"]),
                direction=row["direction"] or "supporting",
                warrant_weight=float(row["warrant_weight"] or 1.0),
            )
            for row in rows
        ]
    paper_id = normalize_paper_id(claim_id)
    row = conn.execute(
        "SELECT 1 FROM paper_quality_fingerprints WHERE paper_id = ?",
        (paper_id,),
    ).fetchone()
    return [Warrant(paper_id=paper_id)] if row else []


def _overlap_edges(conn: sqlite3.Connection) -> list[SampleOverlapEdge]:
    if not _table_exists(conn, "sample_overlap_edges"):
        return []
    rows = conn.execute(
        "SELECT paper_id_a, paper_id_b, overlap_kind, confidence, detected_by FROM sample_overlap_edges"
    ).fetchall()
    return [
        SampleOverlapEdge(
            paper_id_a=row["paper_id_a"],
            paper_id_b=row["paper_id_b"],
            overlap_kind=row["overlap_kind"],
            confidence=float(row["confidence"]),
            detected_by=row["detected_by"],
        )
        for row in rows
    ]


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


@router.get(
    "/claim/{claim_id}/strengths",
    response_model=ClaimStrengthsWeaknesses,
)
def claim_strengths(claim_id: str, response: Response) -> ClaimStrengthsWeaknesses:
    _maybe_refreshing(response)
    with connect() as conn:
        warrants = _claim_warrants(conn, claim_id)
        if not warrants:
            raise HTTPException(404, f"No paper-quality warrants found for {claim_id}")
        paper_ids = [w.paper_id for w in warrants]
        placeholders = ",".join("?" for _ in paper_ids)
        rows = conn.execute(
            f"SELECT * FROM paper_quality_fingerprints WHERE paper_id IN ({placeholders})",
            paper_ids,
        ).fetchall()
        fingerprints = [PaperQualityFingerprint.from_sql_row(dict(row)) for row in rows]
        return aggregate_claim_strengths(claim_id, warrants, fingerprints, _overlap_edges(conn))


@router.get(
    "/literature-body",
    response_model=LiteratureBodyQuality,
)
def literature_body(
    response: Response,
    topic: str = Query(default="all_papers"),
    era: str | None = Query(default=None),
    design_type: str | None = Query(default=None),
) -> LiteratureBodyQuality:
    _ = era
    _maybe_refreshing(response)
    with connect() as conn:
        fingerprints = _fingerprints(
            conn,
            topic=None if topic == "all_papers" else topic,
            design_type=design_type,
        )
    return aggregate_literature_body_quality(topic, fingerprints)


@router.get(
    "/paper/{paper_id}/fingerprint",
    response_model=QualityFingerprintEnvelope,
)
def paper_fingerprint(paper_id: str, response: Response) -> QualityFingerprintEnvelope:
    _maybe_refreshing(response)
    raw_paper_id = normalize_paper_id(paper_id)
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM paper_quality_fingerprints WHERE paper_id = ?",
            (raw_paper_id,),
        ).fetchone()
    if not row:
        raise HTTPException(404, f"No paper-quality fingerprint found for {raw_paper_id}")
    return QualityFingerprintEnvelope.from_fingerprint(PaperQualityFingerprint.from_sql_row(dict(row)))


@admin_router.post(
    "/adjudicate",
    response_model=AdjudicationDecisionResponse,
    dependencies=[Depends(require_admin)],
)
def adjudicate(decision: AdjudicationDecision) -> AdjudicationDecisionResponse:
    with connect() as conn:
        row = conn.execute(
            "SELECT queue_id FROM quality_adjudication_queue WHERE queue_id = ?",
            (decision.queue_id,),
        ).fetchone()
        if not row:
            raise HTTPException(404, f"No adjudication queue row {decision.queue_id}")
        conn.execute(
            """
            UPDATE quality_adjudication_queue
               SET adjudicated_value_json = ?,
                   adjudicator_id = ?,
                   adjudicator_notes = ?,
                   status = ?,
                   resolved_at = CURRENT_TIMESTAMP
             WHERE queue_id = ?
            """,
            (
                json.dumps(_jsonable(decision.adjudicated_value), sort_keys=True),
                decision.adjudicator_id,
                decision.adjudicator_notes,
                decision.status,
                decision.queue_id,
            ),
        )
        conn.commit()
    return AdjudicationDecisionResponse(
        ok=True,
        queue_id=decision.queue_id,
        weighting_function_version=WEIGHTING_FUNCTION_VERSION,
    )
