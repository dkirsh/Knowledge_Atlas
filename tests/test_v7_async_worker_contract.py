import json
import sqlite3
from types import SimpleNamespace

import ka_subscription_llm
import ka_v7_async_worker as worker
import ka_v7_lite as v7


def _make_db(path):
    db = sqlite3.connect(str(path))
    db.executescript(
        """
        CREATE TABLE web_metadata (web_id TEXT PRIMARY KEY);
        INSERT INTO web_metadata VALUES ('master');
        CREATE TABLE beliefs (
            belief_id TEXT PRIMARY KEY,
            web_id TEXT NOT NULL,
            content TEXT NOT NULL,
            level TEXT NOT NULL,
            status TEXT NOT NULL,
            credence_value REAL NOT NULL,
            credence_uncertainty REAL,
            credence_n_supporting INTEGER DEFAULT 0,
            credence_n_contradicting INTEGER DEFAULT 0,
            credence_n_observations INTEGER DEFAULT 0,
            theory_id TEXT,
            entrenchment REAL DEFAULT 0.3,
            domain TEXT,
            attribute_id TEXT,
            outcome_type TEXT,
            scope TEXT,
            environment_id TEXT,
            outcome_id TEXT,
            evidence_cluster_id TEXT,
            tags TEXT,
            paper_ids TEXT,
            epistemic_v2 TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            rebuild_id TEXT
        );
        CREATE TABLE processing_queue (
            job_id TEXT PRIMARY KEY,
            job_type TEXT CHECK(job_type IN ('L0_harvest', 'L1_cluster', 'L2_extract', 'L3_synthesize', 'L4_expand')),
            params TEXT,
            status TEXT CHECK(status IN ('pending', 'running', 'complete', 'failed')),
            priority INTEGER DEFAULT 100,
            created_at TEXT,
            started_at TEXT,
            completed_at TEXT,
            error TEXT,
            result TEXT,
            updated_at TEXT
        );
        """
    )
    db.close()


def _seed_partial(db_path, monkeypatch):
    monkeypatch.setenv("KA_AE_DB_PATH", str(db_path))
    result = v7.evaluate_v7_lite(
        title="Biophilic virtual nature exposure and salivary cortisol",
        abstract="Participants viewed immersive nature and urban VR scenes in a controlled experiment. Salivary cortisol was measured before and after exposure.",
        write_ae=True,
        generate_prose=False,
    )
    return result["queue_job_id"], result["evaluation"]["ae_db_write_status"]["belief_id"]


def test_v7_lite_queue_payload_carries_worker_contract_and_evaluation(tmp_path, monkeypatch):
    db_path = tmp_path / "ae.db"
    _make_db(db_path)
    job_id, belief_id = _seed_partial(db_path, monkeypatch)

    db = sqlite3.connect(str(db_path))
    try:
        params = json.loads(db.execute("SELECT params FROM processing_queue WHERE job_id = ?", (job_id,)).fetchone()[0])
    finally:
        db.close()

    assert params["source"] == "v7_lite"
    assert params["worker_contract"] == v7.V7_LITE_FULL_WORKER_CONTRACT
    assert params["belief_id"] == belief_id
    assert params["evaluation"]["paper_type"] == "empirical"
    assert params["evaluation"]["conditional_voi"]["target_1_better_stimuli"] == "medium"
    assert "source_metadata" in params["evaluation"]


def test_async_worker_upgrades_partial_belief_without_python_public_prose(tmp_path, monkeypatch):
    db_path = tmp_path / "ae.db"
    _make_db(db_path)
    job_id, belief_id = _seed_partial(db_path, monkeypatch)

    result = worker.run_once(db_path, job_id=job_id, generate_prose=False)

    assert result["status"] == "complete"
    db = sqlite3.connect(str(db_path))
    try:
        status, queue_result = db.execute("SELECT status, result FROM processing_queue WHERE job_id = ?", (job_id,)).fetchone()
        epistemic = json.loads(db.execute("SELECT epistemic_v2 FROM beliefs WHERE belief_id = ?", (belief_id,)).fetchone()[0])
    finally:
        db.close()

    assert status == "complete"
    assert json.loads(queue_result)["completion_status"] == "full_v7_structured_complete_public_prose_pending"
    assert epistemic["v7_lite_partial"] is False
    assert epistemic["full_v7_async_completed"] is True
    assert "source_metadata" in epistemic["full_v7_result"]
    assert len(epistemic["full_conditional_voi"]) == 10
    assert epistemic["science_summary"]["text"] == ""
    assert epistemic["science_summary"]["generation"]["python_public_prose_allowed"] is False
    assert epistemic["argumentation"]["python_public_prose_allowed"] is False


def test_v7_lite_async_article_endpoint_shape_uses_upgraded_belief(tmp_path, monkeypatch):
    db_path = tmp_path / "ae.db"
    _make_db(db_path)
    job_id, belief_id = _seed_partial(db_path, monkeypatch)
    worker.run_once(db_path, job_id=job_id, generate_prose=False)

    payload = v7.load_v7_lite_async_article("PDF-LITE-PENDING", belief_id=belief_id)

    assert payload["status"] == "found"
    assert payload["source"] == "ae_db_v7_lite_async"
    assert payload["article"]["paper_id"].startswith("PDF-")
    assert payload["detail"]["article_meta"]["belief_id"] == belief_id
    assert payload["detail"]["science_summary"]["core_finding"] == ""
    assert payload["full_v7_result"]["completion_status"] == "full_v7_structured_complete_public_prose_pending"


def test_async_worker_can_fill_public_prose_with_subscription_cli(tmp_path, monkeypatch):
    db_path = tmp_path / "ae.db"
    _make_db(db_path)
    job_id, belief_id = _seed_partial(db_path, monkeypatch)

    def fake_run(command, input, text, capture_output, timeout, check):
        return SimpleNamespace(
            returncode=0,
            stdout="```json\n" + json.dumps(
                {
                    "science_summary": "This paper tests whether immersive nature exposure changes a measurable stress marker after a controlled viewing session. It is provisionally useful because the dependent variable is explicit and the stimulus can be remade in VR.",
                    "plausible_neural_explanation": "A plausible explanation is that immersive nature reduces threat monitoring and autonomic arousal, which would be consistent with a lower stress response.",
                    "argument_importance": "The paper matters if it connects an architectural stimulus to a tractable physiological outcome.",
                    "limitations": "The claim remains limited until the full review checks the stimulus contrast, sample, and measurement timing.",
                }
            ) + "\n```",
            stderr="",
        )

    monkeypatch.setattr(ka_subscription_llm.subprocess, "run", fake_run)
    result = worker.run_once(db_path, job_id=job_id, generate_prose=True)

    assert result["status"] == "complete"
    db = sqlite3.connect(str(db_path))
    try:
        epistemic = json.loads(db.execute("SELECT epistemic_v2 FROM beliefs WHERE belief_id = ?", (belief_id,)).fetchone()[0])
    finally:
        db.close()

    generation = epistemic["science_summary"]["generation"]
    assert generation["status"] == "subscription_cli_llm_authored"
    assert generation["api_access_allowed"] is False
    assert generation["python_public_prose_allowed"] is False
    assert "immersive nature exposure" in epistemic["science_summary"]["text"]


def test_async_worker_parses_json_from_subscription_cli_transcript():
    transcript = """
OpenAI Codex v0.129.0
--------
user
Return strict JSON.

codex
{"science_summary":"A clear summary.","plausible_neural_explanation":"A provisional PNU.","argument_importance":"Important.","limitations":"Limited."}
tokens used
123
"""

    parsed = worker._parse_llm_json(transcript)

    assert parsed["science_summary"] == "A clear summary."
    assert parsed["plausible_neural_explanation"] == "A provisional PNU."


def test_async_worker_marks_missing_belief_job_failed(tmp_path):
    db_path = tmp_path / "ae.db"
    _make_db(db_path)
    db = sqlite3.connect(str(db_path))
    db.execute(
        """
        INSERT INTO processing_queue (job_id, job_type, params, status, priority, created_at, updated_at)
        VALUES (?, 'L2_extract', ?, 'pending', 10, 'now', 'now')
        """,
        ("full_v7_missing", json.dumps({"source": "v7_lite", "belief_id": "missing", "paper_id": "PDF-X"})),
    )
    db.commit()
    db.close()

    result = worker.run_once(db_path, job_id="full_v7_missing", generate_prose=False)

    assert result["status"] == "failed"
    db = sqlite3.connect(str(db_path))
    try:
        status, error = db.execute("SELECT status, error FROM processing_queue WHERE job_id = 'full_v7_missing'").fetchone()
    finally:
        db.close()
    assert status == "failed"
    assert "belief row not found" in error


def test_async_worker_does_not_import_api_llm_clients():
    source = worker.Path(worker.__file__).read_text()

    assert "import openai" not in source
    assert "import anthropic" not in source
    assert "OpenAI(" not in source
    assert "Anthropic(" not in source
