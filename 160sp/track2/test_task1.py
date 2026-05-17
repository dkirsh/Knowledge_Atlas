# -*- coding: utf-8 -*-
from __future__ import annotations
import sqlite3
from pathlib import Path
from types import SimpleNamespace
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

def _pdf_with_doi(doi="10.1234/test.001"):
    payload = ("DOI: " + doi + "\n").encode("ascii")
    return b"%PDF-1.4\n" + payload + b"%body\n%%EOF\n"

def _make_result(verdict, confidence, next_action="ready_for_intake_decision", shared_label="empirical_research", primary_topic="daylight_and_cognition"):
    cand = [SimpleNamespace(topic=primary_topic, best_confidence=confidence)]
    routing = SimpleNamespace(primary_topic=primary_topic, candidates=cand, emergent_candidates=())
    summary = SimpleNamespace(best_verdict=verdict, best_confidence=confidence, reasons=("ok",), needs_manual_review=False)
    snapshot = SimpleNamespace(first_page_excerpt="A randomized trial of classroom lighting on attention.", abstract_excerpt="We tested whether classroom lighting affects attention.")
    return SimpleNamespace(next_action=next_action, question_summary=summary, overall_confidence=confidence, article_type=SimpleNamespace(value=shared_label, confidence=confidence), stable_topic_routing=routing, active_topic_matches=(), surface_snapshot=snapshot, evidence_stage="pdf_surface_light", available_evidence_types=("title", "first_page_text", "pdf_path"), analysis_steps_run=("surface_extraction",))

class FakeClassifier:
    def __init__(self): self._next = _make_result("accept", 0.9)
    def queue(self, r): self._next = r
    def classify(self, evidence, **kwargs): return self._next

@pytest.fixture
def env(tmp_path, monkeypatch):
    storage = tmp_path / "storage"
    db_path = tmp_path / "ka_auth.db"
    monkeypatch.setenv("KA_STORAGE_ROOT", str(storage))
    monkeypatch.setenv("KA_QUARANTINE_DIR", str(storage / "quarantine"))
    monkeypatch.setenv("KA_PDF_COLLECTION_DIR", str(storage / "pdf_collection"))
    monkeypatch.setenv("KA_REJECTED_DIR", str(storage / "rejected"))
    import importlib
    import ka_article_endpoints as kae
    importlib.reload(kae)
    def get_db():
        c = sqlite3.connect(str(db_path))
        c.row_factory = sqlite3.Row
        return c
    kae.configure(get_db, lambda: None, lambda: None, lambda: None)
    kae._init_article_tables()
    fake = FakeClassifier()
    monkeypatch.setattr(kae, "_get_shared_article_classifier", lambda: fake)
    app = FastAPI()
    app.include_router(kae.router)
    return SimpleNamespace(client=TestClient(app), fake=fake, kae=kae, db_path=db_path, quarantine=storage / "quarantine")

def _rows(db_path, sql):
    c = sqlite3.connect(str(db_path)); c.row_factory = sqlite3.Row
    try: return [dict(r) for r in c.execute(sql).fetchall()]
    finally: c.close()

def _post(env, filename, doi):
    return env.client.post("/api/articles/submit", files={"files": (filename, _pdf_with_doi(doi), "application/pdf")}, data={"source_surface": "ka_contribute_public"})

def test_accept(env):
    env.fake.queue(_make_result("accept", 0.85))
    item = _post(env, "a.pdf", "10.1/accept").json()["items"][0]
    assert item["status"] == env.kae.STATUS_STAGED
    assert item["decision"] == env.kae.DECISION_ACCEPT
    assert item["primary_topic"] == "daylight_and_cognition"
    assert item["classifier_confidence"] == 0.85
    row = _rows(env.db_path, "SELECT * FROM articles WHERE article_id='" + item["article_id"] + "'")[0]
    assert row["quarantine_path"] and Path(row["quarantine_path"]).exists()
    assert row["staged_at"] and row["rejected_at"] is None
    assert row["relevance_score"] == 0.85

def test_edge_case(env):
    env.fake.queue(_make_result("edge_case", 0.55))
    item = _post(env, "b.pdf", "10.1/edge").json()["items"][0]
    assert item["status"] == env.kae.STATUS_STAGED_EDGE_CASE
    assert item["decision"] == env.kae.DECISION_EDGE_CASE
    row = _rows(env.db_path, "SELECT * FROM articles WHERE article_id='" + item["article_id"] + "'")[0]
    assert row["quarantine_path"] and Path(row["quarantine_path"]).exists()
    assert row["staged_at"] and row["rejected_at"] is None

def test_reject(env):
    env.fake.queue(_make_result("reject", 0.10))
    item = _post(env, "c.pdf", "10.1/reject").json()["items"][0]
    assert item["status"] == env.kae.STATUS_REJECTED_OFF_TOPIC
    assert item["decision"] == env.kae.DECISION_REJECT
    row = _rows(env.db_path, "SELECT * FROM articles WHERE article_id='" + item["article_id"] + "'")[0]
    assert row["quarantine_path"] is None
    assert row["rejected_at"] and row["staged_at"] is None
    assert not any(p.name == item["article_id"] + ".pdf" for p in env.quarantine.rglob("*.pdf"))

def test_duplicate(env):
    env.fake.queue(_make_result("accept", 0.8))
    pdf = _pdf_with_doi("10.1/dup")
    r1 = env.client.post("/api/articles/submit", files={"files": ("first.pdf", pdf, "application/pdf")}, data={"source_surface": "ka_contribute_public"})
    first_id = r1.json()["items"][0]["article_id"]
    r2 = env.client.post("/api/articles/submit", files={"files": ("second.pdf", pdf, "application/pdf")}, data={"source_surface": "ka_contribute_public"})
    item = r2.json()["items"][0]
    assert item["status"] == env.kae.STATUS_REJECTED_DUPLICATE
    assert item["duplicate_of"] == first_id
    row = _rows(env.db_path, "SELECT * FROM articles WHERE article_id='" + item["article_id"] + "'")[0]
    assert row["quarantine_path"] is None
    assert row["rejected_at"] and row["duplicate_of"] == first_id

def test_grader_invariants(env):
    env.fake.queue(_make_result("accept", 0.85)); _post(env, "a.pdf", "10.1/a")
    env.fake.queue(_make_result("edge_case", 0.55)); _post(env, "b.pdf", "10.1/b")
    env.fake.queue(_make_result("reject", 0.10)); _post(env, "c.pdf", "10.1/c")
    env.fake.queue(_make_result("accept", 0.85)); _post(env, "a.pdf", "10.1/a")
    assert _rows(env.db_path, "SELECT 1 FROM articles WHERE status LIKE 'reject%' AND quarantine_path IS NOT NULL") == []
    assert _rows(env.db_path, "SELECT 1 FROM articles WHERE status IN ('staged_pending_review','staged_edge_case') AND quarantine_path IS NULL") == []
    assert _rows(env.db_path, "SELECT a.article_id FROM articles a LEFT JOIN audit_log al ON a.article_id=al.article_id WHERE al.log_id IS NULL") == []
    assert _rows(env.db_path, "SELECT 1 FROM articles WHERE status IS NULL OR created_at IS NULL") == []
    stat = {r["status"] for r in _rows(env.db_path, "SELECT DISTINCT status FROM articles WHERE status IN ('staged_pending_review','staged_edge_case')")}
    assert stat == {"staged_pending_review", "staged_edge_case"}