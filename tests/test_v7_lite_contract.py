import ka_v7_lite as v7
import ka_subscription_llm
import sqlite3
from types import SimpleNamespace
from scripts.calibrate_v7_lite_topic_thresholds import calibrate


def test_v7_lite_in_corpus_short_circuit_uses_cached_article():
    result = v7.evaluate_v7_lite(doi="10.1016/j.physbeh.2020.112999")

    assert result["status"] == "admitted"
    assert result["paper_id"] == "PDF-0007"
    assert result["queued_for_full_v7"] is False
    recommendation = result["evaluation"]["recommendation"]
    assert recommendation["summary"] == "Admit"
    assert recommendation["rationale"] == ""
    assert recommendation["rationale_generation"]["status"] == "requires_subscription_cli_llm"
    assert recommendation["rationale_generation"]["api_access_allowed"] is False


def test_v7_lite_rejects_out_of_scope_neural_methods():
    result = v7.evaluate_v7_lite(
        title="Default mode connectivity during resting-state fMRI",
        abstract="This scanner study measures BOLD connectivity in the default mode network.",
    )

    assert result["status"] == "rejected_out_of_scope"
    assert result["new_topic_seed_offered"] is True
    assert result["nearest_topics"][0]["topic_id"] == "neural_methods_out_of_scope"


def test_v7_lite_admits_on_topic_paper_and_maps_substitution():
    result = v7.evaluate_v7_lite(
        title="Biophilic virtual nature exposure and salivary cortisol",
        abstract="Participants viewed immersive nature and urban VR scenes in a controlled experiment. Salivary cortisol and working memory were measured before and after exposure.",
    )

    assert result["status"] == "admitted"
    evaluation = result["evaluation"]
    assert evaluation["topic_fit"]["admitted_to"] == "natural__cog_attention"
    assert evaluation["queued_for_full_v7"] if "queued_for_full_v7" in evaluation else result["queued_for_full_v7"]
    cortisol = next(row for row in evaluation["vr_suitability_mapping"] if row["measure_short_code"] == "x5.biomarker")
    assert cortisol["admit_verdict"] == "admit_with_substitution"
    assert cortisol["substitution_candidates"][0]["measure_short_code"] == "f4.eda"
    assert evaluation["recommendation"]["rationale"] == ""
    assert evaluation["recommendation"]["rationale_generation"]["python_public_prose_allowed"] is False


def test_v7_lite_extracts_dynamic_lighting_iv_dvs_and_methods():
    abstract = (
        "This study investigated non-image forming effects of dynamic light on alertness, "
        "cognitive performance and mood. Sixteen participants completed a psychomotor "
        "vigilance test, MATB-II and n-back under dynamic 4000 to 12000 K and static "
        "4000 K lighting. Psychological, behavioural, biochemical and electrophysiological "
        "responses were assessed. The results showed benefits on subjective sleepiness, "
        "positive mood and task performance."
    )

    result = v7.evaluate_v7_lite(
        title="Diurnal effects of dynamic lighting on alertness, cognition, and mood of mentally fatigued individuals",
        abstract=abstract,
        generate_prose=False,
    )

    evaluation = result["evaluation"]
    assert evaluation["paper_type"] == "empirical"
    assert evaluation["paper_type_confidence"] >= 0.7
    assert evaluation["iv"]["levels"] == ["dynamic lighting", "static lighting"]
    assert evaluation["methods"]["sample_n"] == 16
    names = {row["name"] for row in evaluation["dv"]}
    assert "Psychomotor Vigilance Test" in names
    assert "n-back task" in names
    assert "mood rating" in names


def test_v7_lite_does_not_import_api_llm_clients():
    source = v7.Path(v7.__file__).read_text()

    assert "import openai" not in source
    assert "import anthropic" not in source
    assert "OpenAI(" not in source
    assert "Anthropic(" not in source


def test_v7_lite_can_fill_recommendation_with_subscription_cli(monkeypatch):
    def fake_run(command, input, text, capture_output, timeout, check):
        return SimpleNamespace(
            returncode=0,
            stdout='{"summary":"Admit with substitution","rationale":"The paper is on topic and useful because it tests nature exposure while using cortisol. The synchronous map flags EDA as a practical substitute and leaves full V7 for deeper warrant review."}',
            stderr="",
        )

    monkeypatch.setattr(ka_subscription_llm.subprocess, "run", fake_run)
    result = v7.evaluate_v7_lite(
        title="Biophilic virtual nature exposure and salivary cortisol",
        abstract="Participants viewed immersive nature and urban VR scenes in a controlled experiment. Salivary cortisol was measured before and after exposure.",
        generate_prose=True,
    )

    recommendation = result["evaluation"]["recommendation"]
    assert recommendation["rationale"]
    assert recommendation["rationale_generation"]["status"] == "subscription_cli_llm_authored"
    assert recommendation["rationale_generation"]["api_access_allowed"] is False


def test_v7_lite_writes_partial_belief_and_full_v7_queue(tmp_path, monkeypatch):
    db_path = tmp_path / "ae.db"
    db = sqlite3.connect(str(db_path))
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
    monkeypatch.setenv("KA_AE_DB_PATH", str(db_path))

    result = v7.evaluate_v7_lite(
        title="Biophilic virtual nature exposure and salivary cortisol",
        abstract="Participants viewed immersive nature and urban VR scenes in a controlled experiment. Salivary cortisol was measured before and after exposure.",
        write_ae=True,
        generate_prose=False,
    )

    assert result["evaluation"]["ae_db_write_status"]["status"] == "partial"
    assert result["paper_id"].startswith("PDF-")
    assert result["paper_id"] != "PDF-LITE-PENDING"
    db = sqlite3.connect(str(db_path))
    try:
        assert db.execute("SELECT COUNT(*) FROM beliefs").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM processing_queue").fetchone()[0] == 1
        params = db.execute("SELECT params FROM processing_queue").fetchone()[0]
        queue_params = v7.json.loads(params)
        assert queue_params["worker_contract"] == v7.V7_LITE_FULL_WORKER_CONTRACT
        assert queue_params["evaluation"]["paper_type"] == "empirical"
        assert queue_params["evaluation"]["source_metadata"]["text_surface_chars"] >= 0
    finally:
        db.close()


def test_v7_lite_persists_uploaded_pdf_for_async_full_worker(tmp_path, monkeypatch):
    monkeypatch.setattr(v7, "DEFAULT_UPLOAD_DIR", tmp_path / "uploads")

    saved = v7.persist_v7_lite_upload(b"%PDF-1.4 test", "A Paper: Draft.pdf")

    assert saved.endswith(".pdf")
    assert "A_Paper_Draft" in saved
    assert v7.Path(saved).read_bytes() == b"%PDF-1.4 test"


def test_v7_lite_threshold_calibration_produces_topic_thresholds():
    payload = calibrate()

    assert payload["schema_version"] == "ka_v7_lite_topic_thresholds_v1"
    assert payload["default_threshold"] == 0.12
    assert payload["topics"]
    assert all(0.05 <= value <= 0.55 for value in payload["topics"].values())
