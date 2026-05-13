import json
import sqlite3
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "contracts" / "schemas" / "paper_quality.sql"
INIT = ROOT / "scripts" / "paper_quality_blackboard_init.py"


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def test_paper_quality_schema_applies_to_empty_sqlite_db(tmp_path):
    db = tmp_path / "pq.db"
    conn = _connect(db)
    conn.executescript(SCHEMA.read_text())
    names = {
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
        )
    }
    expected = {
        "paper_quality_fingerprints",
        "fingerprint_staging",
        "sample_overlap_edges",
        "fingerprint_extraction_events",
        "quality_adjudication_queue",
        "quality_calibration_history",
        "hard_rule_violations",
        "paper_interpretation",
        "paper_quality_batches",
        "paper_quality_jobs",
        "holding_pen",
        "paper_quality_progress",
        "claim_strengths_weaknesses",
        "literature_body_quality",
    }
    assert expected <= names
    conn.executescript(SCHEMA.read_text())
    conn.close()


def test_blackboard_init_creates_idempotent_batches_jobs_and_mirror(tmp_path):
    db = tmp_path / "pq.db"
    corpus = tmp_path / "corpus.json"
    mirror = tmp_path / "progress.json"
    paper_ids = [f"PDF-{i:04d}" for i in range(1, 57)]
    corpus.write_text(json.dumps({"papers": [{"paper_id": paper_id} for paper_id in paper_ids]}))

    cmd = [
        sys.executable,
        str(INIT),
        "--corpus",
        str(corpus),
        "--db",
        str(db),
        "--batch-size",
        "28",
        "--pools",
        "claude-max:2,codex-pro:2,gemini:1",
        "--out-mirror",
        str(mirror),
    ]
    subprocess.run(cmd, cwd=ROOT, check=True, text=True, capture_output=True)
    subprocess.run(cmd, cwd=ROOT, check=True, text=True, capture_output=True)

    conn = _connect(db)
    assert conn.execute("SELECT COUNT(*) FROM paper_quality_jobs").fetchone()[0] == 56 * 3
    assert conn.execute("SELECT COUNT(*) FROM paper_quality_batches").fetchone()[0] == 6
    assert conn.execute("SELECT COUNT(*) FROM paper_quality_progress").fetchone()[0] == 56
    assignees = [
        row[0]
        for row in conn.execute(
            "SELECT DISTINCT current_assignee FROM paper_quality_batches ORDER BY current_assignee"
        )
    ]
    assert all(assignee.startswith("pre-allocated:") for assignee in assignees)
    conn.close()

    payload = json.loads(mirror.read_text())
    assert payload["total_papers"] == 56
    assert payload["inserted_jobs"] == 0
    assert payload["inserted_batches"] == 0
    assert payload["pass_counts"]["extract_claude"]["jobs"] == 56
    assert payload["batch_counts"]["pending"] == 6
