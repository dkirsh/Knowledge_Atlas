import json
import sqlite3
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
ATLAS_SHARED_SRC = ROOT.parent / "atlas_shared" / "src"
if str(ATLAS_SHARED_SRC) not in sys.path:
    sys.path.insert(0, str(ATLAS_SHARED_SRC))

from atlas_shared.paper_quality import (  # noqa: E402
    EffectSize,
    FingerprintField,
    PaperQualityFingerprint,
    PreregRecord,
)

from backend.app.api.v1.routes.quality import admin_router, router  # noqa: E402


SCHEMA = ROOT / "contracts" / "schemas" / "paper_quality.sql"


def _client(db_path: Path, monkeypatch) -> TestClient:
    monkeypatch.setenv("KA_PAPER_QUALITY_DB", str(db_path))
    monkeypatch.setenv("KA_ADMIN_ALLOW_OPEN", "1")
    app = FastAPI()
    app.include_router(router)
    app.include_router(admin_router)
    return TestClient(app)


def _insert_fingerprint(conn: sqlite3.Connection, fingerprint: PaperQualityFingerprint) -> None:
    row = fingerprint.to_sql_row()
    cols = ", ".join(row)
    placeholders = ", ".join("?" for _ in row)
    conn.execute(
        f"INSERT INTO paper_quality_fingerprints ({cols}) VALUES ({placeholders})",
        tuple(row.values()),
    )


def _seed(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA.read_text())
    for idx in range(1, 6):
        _insert_fingerprint(
            conn,
            PaperQualityFingerprint(
                paper_id=f"PDF-{idx:04d}",
                extractor_version="test-v1",
                n_total=FingerprintField(value=80 + idx * 10, confidence=0.9),
                sample_country=FingerprintField(value=("US",)),
                design_type=FingerprintField(value="lab_experiment" if idx < 5 else "field_experiment"),
                preregistration=FingerprintField(
                    value=PreregRecord(url=f"https://osf.io/test{idx}", verified=idx % 2 == 0)
                ),
                replication_count=FingerprintField(value=idx % 2),
                primary_effect_size=FingerprintField(
                    value=EffectSize(value=0.2 + idx / 10, metric="d", ci_lower=0.05, ci_upper=0.65)
                ),
                open_data_url=FingerprintField(value=f"https://data.example/{idx}"),
                open_data_verified=FingerprintField(value=idx % 2 == 0),
                construct_validity_flag="good",
                overall_confidence=0.75,
                notes_markdown="Fixture paper-quality row.",
            ),
        )
    conn.execute(
        """
        CREATE TABLE claim_paper_warrants (
          claim_id TEXT NOT NULL,
          paper_id TEXT NOT NULL,
          direction TEXT NOT NULL DEFAULT 'supporting',
          warrant_weight REAL NOT NULL DEFAULT 1.0
        )
        """
    )
    conn.executemany(
        "INSERT INTO claim_paper_warrants (claim_id, paper_id, direction, warrant_weight) VALUES (?, ?, ?, ?)",
        [
            ("claim-fixture", "PDF-0001", "supporting", 1.0),
            ("claim-fixture", "PDF-0002", "supporting", 1.0),
            ("claim-fixture", "PDF-0003", "defeating", 0.7),
        ],
    )
    conn.execute(
        "INSERT INTO sample_overlap_edges (paper_id_a, paper_id_b, overlap_kind, confidence, detected_by) "
        "VALUES ('PDF-0001', 'PDF-0002', 'shared_dataset', 0.80, 'manual')"
    )
    conn.execute(
        """
        INSERT INTO quality_adjudication_queue (
          paper_id, field_name, suggested_value_json, source_excerpt, confidence_score, queue_reason
        ) VALUES (
          'PDF-0001', 'construct_validity_flag', '{"value":"mixed"}',
          'Methods paragraph 3', 0.42, 'low confidence'
        )
        """
    )
    conn.commit()
    conn.close()


def test_quality_claim_strengths_endpoint_uses_imported_aggregator_shape(tmp_path, monkeypatch):
    db = tmp_path / "pq.db"
    _seed(db)
    client = _client(db, monkeypatch)

    response = client.get("/api/v1/quality/claim/claim-fixture/strengths")

    assert response.status_code == 200
    payload = response.json()
    assert payload["claim_id"] == "claim-fixture"
    assert payload["n_supporting"] == 2
    assert payload["n_defeating"] == 1
    assert payload["cumulative_n_overlap_flagged"] == 1
    assert payload["weighting_function_version"] == "v1.0-2026-05-13"


def test_quality_literature_body_endpoint_supports_design_filter(tmp_path, monkeypatch):
    db = tmp_path / "pq.db"
    _seed(db)
    client = _client(db, monkeypatch)

    response = client.get("/api/v1/quality/literature-body?design_type=field_experiment")

    assert response.status_code == 200
    payload = response.json()
    assert payload["topic_id"] == "all_papers"
    assert payload["total_primary_paper_count"] == 1
    assert payload["weighted_median_sample_size"] == 130.0


def test_quality_paper_fingerprint_endpoint_normalizes_bel_prefix(tmp_path, monkeypatch):
    db = tmp_path / "pq.db"
    _seed(db)
    client = _client(db, monkeypatch)

    response = client.get("/api/v1/quality/paper/bel_PDF-0001/fingerprint")

    assert response.status_code == 200
    payload = response.json()
    assert payload["paper_id"] == "PDF-0001"
    assert payload["extractor_version"] == "test-v1"
    assert payload["fingerprint"]["paper_id"] == "PDF-0001"


def test_quality_endpoint_returns_retry_after_when_refreshing(tmp_path, monkeypatch):
    db = tmp_path / "pq.db"
    _seed(db)
    monkeypatch.setenv("KA_PAPER_QUALITY_REFRESHING", "1")
    monkeypatch.setenv("KA_PAPER_QUALITY_RETRY_AFTER", "120")
    client = _client(db, monkeypatch)

    response = client.get("/api/v1/quality/literature-body")

    assert response.status_code == 503
    assert response.headers["retry-after"] == "120"


def test_admin_adjudication_endpoint_records_decision_with_version(tmp_path, monkeypatch):
    db = tmp_path / "pq.db"
    _seed(db)
    client = _client(db, monkeypatch)

    response = client.post(
        "/api/v1/admin/paper_quality/adjudicate",
        json={
            "queue_id": 1,
            "adjudicated_value": {"value": "good"},
            "adjudicator_id": "dk",
            "adjudicator_notes": "Fixture review.",
        },
    )

    assert response.status_code == 200
    assert response.json()["weighting_function_version"] == "v1.0-2026-05-13"
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, adjudicated_value_json, adjudicator_id FROM quality_adjudication_queue WHERE queue_id = 1"
    ).fetchone()
    assert row == ("resolved", json.dumps({"value": "good"}, sort_keys=True), "dk")
    conn.close()
