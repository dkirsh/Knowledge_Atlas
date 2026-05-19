from pathlib import Path
from types import SimpleNamespace

import ka_substitution_skill as skill
import ka_subscription_llm


def test_substitution_graph_schema_can_seed_sqlite(tmp_path):
    db_path = tmp_path / "substitution_graph.db"
    skill.init_substitution_graph_db(db_path=db_path)

    import sqlite3

    db = sqlite3.connect(str(db_path))
    try:
        assert db.execute("SELECT COUNT(*) FROM constructs").fetchone()[0] >= 4
        assert db.execute("SELECT COUNT(*) FROM measures").fetchone()[0] >= 10
        assert db.execute("SELECT COUNT(*) FROM construct_measure_links").fetchone()[0] >= 10
    finally:
        db.close()


def test_admit_mode_accepts_iat_as_vr_tractable():
    result = skill.admit_mode(
        {
            "generate_prose": False,
            "dv_descriptions": [
                {"name": "IAT", "type": "task_embedded_performance", "claimed_construct": "implicit attitude"}
            ]
        }
    )

    row = result["per_dv_results"][0]
    assert row["admit_verdict"] == "admit_as_is"
    assert row["measure_short_code"] == "f2.iat"
    assert result["paper_level_verdict"] == "admit"


def test_admit_mode_substitutes_cortisol_with_eda():
    result = skill.admit_mode(
        {
            "generate_prose": False,
            "dv_descriptions": [
                {"name": "salivary cortisol", "type": "biomarker", "claimed_construct": "stress response"}
            ]
        }
    )

    row = result["per_dv_results"][0]
    assert row["admit_verdict"] == "admit_with_substitution"
    assert row["measure_short_code"] == "x5.biomarker"
    assert row["substitution_candidates"][0]["measure_short_code"] == "f4.eda"
    assert result["paper_level_verdict"] == "admit_with_substitution"
    assert row["explanation"] == ""
    assert row["explanation_generation"]["status"] == "requires_subscription_cli_llm"
    assert row["explanation_generation"]["python_public_prose_allowed"] is False


def test_admit_mode_accepts_core_task_measures_as_vr_tractable():
    result = skill.admit_mode(
        {
            "generate_prose": False,
            "dv_descriptions": [
                {"name": "Psychomotor Vigilance Test", "type": "task_embedded_performance", "claimed_construct": "attention_restoration"},
                {"name": "n-back task", "type": "task_embedded_performance", "claimed_construct": "attention_restoration"},
                {"name": "MATB-II task performance", "type": "task_embedded_performance", "claimed_construct": "attention_restoration"},
            ],
        }
    )

    rows = result["per_dv_results"]
    assert [row["measure_short_code"] for row in rows] == ["f2.pvt", "f2.nback", "f2.matb"]
    assert all(row["admit_verdict"] == "admit_as_is" for row in rows)
    assert result["paper_level_verdict"] == "admit"


def test_admit_mode_accepts_state_ratings_but_substitutes_biomarkers():
    result = skill.admit_mode(
        {
            "generate_prose": False,
            "dv_descriptions": [
                {"name": "subjective sleepiness rating", "type": "self_report_questionnaire", "claimed_construct": "physiological_stress_response"},
                {"name": "biochemical response measure", "type": "biomarker", "claimed_construct": "physiological_stress_response"},
            ],
        }
    )

    state, biomarker = result["per_dv_results"]
    assert state["measure_short_code"] == "f3.state_rating"
    assert state["admit_verdict"] == "admit_as_is"
    assert biomarker["measure_short_code"] == "x5.biomarker"
    assert biomarker["admit_verdict"] == "admit_with_substitution"


def test_admit_mode_refuses_unknown_construct():
    result = skill.admit_mode(
        {
            "generate_prose": False,
            "dv_descriptions": [
                {"name": "frontier aura score", "type": "unknown", "claimed_construct": "newly named frontier aura"}
            ]
        }
    )

    row = result["per_dv_results"][0]
    assert row["admit_verdict"] == "reject"
    assert row["refusal_reason"] == "no_construct_match"


def test_choice_mode_attention_restoration_ranks_sart_prs_first():
    result = skill.choice_mode(
        {
            "generate_prose": False,
            "topic_id": "attention_restoration",
            "project_constraints": {
                "weeks_available": 8,
                "lab_hardware": ["quest2", "eda", "hrv", "respiration", "wrist_accel"],
                "n_participants_max": 60,
            },
        }
    )

    assert result["candidate_measures"][0]["measure_short_code"] == "f2.sart_plus_f3.prs"
    assert result["candidate_measures"][0]["rank"] == 1
    assert "feasibility_score" in result["candidate_measures"][0]
    assert result["recommendation_prose"] == ""
    assert result["recommendation_generation"]["status"] == "requires_subscription_cli_llm"
    assert result["recommendation_generation"]["api_access_allowed"] is False


def test_jangle_warning_surfaces_for_cognitive_restoration():
    result = skill.admit_mode(
        {
            "generate_prose": False,
            "dv_descriptions": [
                {"name": "Perceived Restorativeness Scale", "type": "self_report", "claimed_construct": "cognitive restoration"}
            ]
        }
    )

    warning = result["per_dv_results"][0]["proliferation_warning"]
    assert "mental_recovery" in warning["jangle_with"]


def test_admit_mode_can_fill_explanation_with_subscription_cli(monkeypatch):
    def fake_run(command, input, text, capture_output, timeout, check):
        return SimpleNamespace(
            returncode=0,
            stdout="Cortisol is not practical for short class VR work, but EDA can index stress-related arousal with clear trade-offs.",
            stderr="",
        )

    monkeypatch.setattr(ka_subscription_llm.subprocess, "run", fake_run)
    result = skill.admit_mode(
        {
            "generate_prose": True,
            "dv_descriptions": [
                {"name": "salivary cortisol", "type": "biomarker", "claimed_construct": "stress response"}
            ],
        }
    )

    row = result["per_dv_results"][0]
    assert row["explanation"]
    assert row["explanation_generation"]["status"] == "subscription_cli_llm_authored"
    assert row["explanation_generation"]["api_access_allowed"] is False
