#!/usr/bin/env python3
"""Initialize the paper-quality blackboard manifest.

The script is deliberately small and deterministic. It reads a corpus JSON,
creates one job per (paper_id, pass_type), groups each pass into batches, and
writes a cross-sandbox JSON mirror. Re-running it is safe: database writes use
INSERT OR IGNORE and the mirror is regenerated from current database state.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = REPO_ROOT / "contracts" / "schemas" / "paper_quality.sql"
DEFAULT_MIRROR = REPO_ROOT / "data" / "paper_quality_progress.json"
DEFAULT_DB_CANDIDATES = (
    REPO_ROOT / "data" / "pipeline_lifecycle_full.db",
    REPO_ROOT / "data" / "ka_payloads" / "pipeline_lifecycle_full.db",
    REPO_ROOT / "160sp" / "pipeline_lifecycle_full.db",
)
PASS_TYPES = ("extract_claude", "extract_codex", "verify_gemini")
PASS_LABELS = {
    "extract_claude": "CLAUDE",
    "extract_codex": "CODEX",
    "verify_gemini": "GEMINI",
}


@dataclass(frozen=True)
class Pool:
    name: str
    slots: int


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def resolve_repo_path(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    return candidate


def default_db_path() -> Path:
    for candidate in DEFAULT_DB_CANDIDATES:
        if candidate.exists():
            return candidate
    return DEFAULT_DB_CANDIDATES[1]


def load_paper_ids(corpus_path: Path) -> list[str]:
    raw = json.loads(corpus_path.read_text())
    if isinstance(raw, list):
        records = raw
    elif isinstance(raw, dict):
        for key in ("paper_ids", "papers", "articles", "corpus", "items"):
            value = raw.get(key)
            if isinstance(value, list):
                records = value
                break
        else:
            raise ValueError(
                f"{corpus_path} must contain a list, or one of: paper_ids, papers, articles, corpus, items"
            )
    else:
        raise ValueError(f"{corpus_path} must be a JSON list or object")

    paper_ids: list[str] = []
    for item in records:
        if isinstance(item, str):
            paper_id = item
        elif isinstance(item, dict):
            paper_id = (
                item.get("paper_id")
                or item.get("id")
                or item.get("pdf_id")
                or item.get("slug")
            )
        else:
            paper_id = None
        if not paper_id:
            raise ValueError(f"Could not extract paper_id from corpus item: {item!r}")
        paper_ids.append(str(paper_id))

    deduped = sorted(dict.fromkeys(paper_ids))
    if not deduped:
        raise ValueError(f"{corpus_path} did not contain any paper IDs")
    return deduped


def parse_pools(value: str) -> list[Pool]:
    pools: list[Pool] = []
    for chunk in value.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ":" not in chunk:
            raise ValueError(f"Pool entry must be name:slots, got {chunk!r}")
        name, slots_raw = chunk.split(":", 1)
        slots = int(slots_raw)
        if slots < 1:
            raise ValueError(f"Pool slots must be positive, got {chunk!r}")
        pools.append(Pool(name=name.strip(), slots=slots))
    if not pools:
        raise ValueError("At least one pool is required")
    return pools


def pools_for_pass(pools: Sequence[Pool], pass_type: str) -> list[str]:
    needle = {
        "extract_claude": "claude",
        "extract_codex": "codex",
        "verify_gemini": "gemini",
    }[pass_type]
    expanded = [
        f"{pool.name}-{slot + 1}"
        for pool in pools
        if needle in pool.name.lower()
        for slot in range(pool.slots)
    ]
    if expanded:
        return expanded
    return [f"{pool.name}-{slot + 1}" for pool in pools for slot in range(pool.slots)]


def chunks(items: Sequence[str], size: int) -> Iterable[list[str]]:
    for start in range(0, len(items), size):
        yield list(items[start : start + size])


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").upper()


def ensure_schema(conn: sqlite3.Connection, schema_path: Path) -> None:
    conn.executescript(schema_path.read_text())


def initialize_blackboard(
    conn: sqlite3.Connection,
    paper_ids: Sequence[str],
    batch_size: int,
    pools: Sequence[Pool],
) -> dict[str, int]:
    inserted_jobs = 0
    inserted_batches = 0
    now = utc_now()
    for pass_type in PASS_TYPES:
        assignees = pools_for_pass(pools, pass_type)
        label = PASS_LABELS[pass_type]
        for batch_index, paper_chunk in enumerate(chunks(paper_ids, batch_size), start=1):
            batch_id = f"PQ-BATCH-{label}-{batch_index:03d}"
            assignee = f"pre-allocated:{assignees[(batch_index - 1) % len(assignees)]}"
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO paper_quality_batches (
                  batch_id, pass_type, paper_ids, batch_size, status,
                  current_assignee, notification_events
                )
                VALUES (?, ?, ?, ?, 'pending', ?, ?)
                """,
                (
                    batch_id,
                    pass_type,
                    json.dumps(paper_chunk, sort_keys=True),
                    len(paper_chunk),
                    assignee,
                    json.dumps(
                        [
                            {
                                "event": "pre_allocated",
                                "at": now,
                                "assignee": assignee,
                            }
                        ],
                        sort_keys=True,
                    ),
                ),
            )
            inserted_batches += cur.rowcount
            for paper_id in paper_chunk:
                job_id = f"PQ-{safe_id(paper_id)}-{label}"
                cur = conn.execute(
                    """
                    INSERT OR IGNORE INTO paper_quality_jobs (
                      job_id, paper_id, pass_type, batch_id, status
                    )
                    VALUES (?, ?, ?, ?, 'pending')
                    """,
                    (job_id, paper_id, pass_type, batch_id),
                )
                inserted_jobs += cur.rowcount
    conn.commit()
    return {
        "inserted_jobs": inserted_jobs,
        "inserted_batches": inserted_batches,
        "total_papers": len(paper_ids),
    }


def mirror_payload(conn: sqlite3.Connection, stats: dict[str, int]) -> dict[str, object]:
    pass_counts = {
        row["pass_type"]: {
            "jobs": row["jobs"],
            "done": row["done"],
            "failed": row["failed"],
        }
        for row in conn.execute(
            """
            SELECT
              pass_type,
              COUNT(*) AS jobs,
              SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) AS done,
              SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed
            FROM paper_quality_jobs
            GROUP BY pass_type
            ORDER BY pass_type
            """
        )
    }
    batch_counts = {
        row["status"]: row["count"]
        for row in conn.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM paper_quality_batches
            GROUP BY status
            ORDER BY status
            """
        )
    }
    return {
        "generated_at": utc_now(),
        "source": "scripts/paper_quality_blackboard_init.py",
        "total_papers": stats["total_papers"],
        "inserted_jobs": stats["inserted_jobs"],
        "inserted_batches": stats["inserted_batches"],
        "pass_counts": pass_counts,
        "batch_counts": batch_counts,
    }


def write_mirror(conn: sqlite3.Connection, mirror_path: Path, stats: dict[str, int]) -> None:
    mirror_path.parent.mkdir(parents=True, exist_ok=True)
    payload = mirror_payload(conn, stats)
    mirror_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize paper-quality blackboard batches and jobs.")
    parser.add_argument("--corpus", required=True, help="JSON corpus list or object containing paper IDs.")
    parser.add_argument("--db", default=str(default_db_path()), help="Lifecycle SQLite DB to update.")
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA), help="Schema SQL to apply before initialization.")
    parser.add_argument("--no-ensure-schema", action="store_true", help="Do not apply the schema before inserting rows.")
    parser.add_argument("--batch-size", type=int, default=28, help="Papers per batch; must be 1..30.")
    parser.add_argument("--pools", default="claude-max:4,codex-pro:4,gemini:1", help="Worker pools as name:slots CSV.")
    parser.add_argument("--out-mirror", default=str(DEFAULT_MIRROR), help="JSON mirror output path.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not 1 <= args.batch_size <= 30:
        raise SystemExit("--batch-size must be between 1 and 30")
    corpus_path = resolve_repo_path(args.corpus)
    db_path = resolve_repo_path(args.db)
    schema_path = resolve_repo_path(args.schema)
    mirror_path = resolve_repo_path(args.out_mirror)

    paper_ids = load_paper_ids(corpus_path)
    pools = parse_pools(args.pools)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        if not args.no_ensure_schema:
            ensure_schema(conn, schema_path)
        stats = initialize_blackboard(conn, paper_ids, args.batch_size, pools)
        write_mirror(conn, mirror_path, stats)
    finally:
        conn.close()

    print(
        "paper-quality blackboard initialized: "
        f"{stats['total_papers']} papers, "
        f"{stats['inserted_jobs']} new jobs, "
        f"{stats['inserted_batches']} new batches, "
        f"mirror={mirror_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
