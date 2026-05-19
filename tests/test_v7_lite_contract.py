import ka_v7_lite as v7


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
    assert evaluation["topic_fit"]["admitted_to"] == "nature_views_cognitive_recovery"
    assert evaluation["queued_for_full_v7"] if "queued_for_full_v7" in evaluation else result["queued_for_full_v7"]
    cortisol = next(row for row in evaluation["vr_suitability_mapping"] if row["measure_short_code"] == "x5.biomarker")
    assert cortisol["admit_verdict"] == "admit_with_substitution"
    assert cortisol["substitution_candidates"][0]["measure_short_code"] == "f4.eda"
    assert evaluation["recommendation"]["rationale"] == ""
    assert evaluation["recommendation"]["rationale_generation"]["python_public_prose_allowed"] is False


def test_v7_lite_does_not_import_api_llm_clients():
    source = v7.Path(v7.__file__).read_text()

    assert "import openai" not in source
    assert "import anthropic" not in source
    assert "OpenAI(" not in source
    assert "Anthropic(" not in source
