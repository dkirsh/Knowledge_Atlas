import copy
import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "verify_dyk_llm_authoring_contract.py"

spec = importlib.util.spec_from_file_location("verify_dyk_llm_authoring_contract", SCRIPT_PATH)
verify = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(verify)


def _valid_card():
    return {
        "id": "dyk_test",
        "paper_id": "PDF-0001",
        "source_claim_ids": ["1"],
        "title": "Window Views Can Change Stress Physiology",
        "body": "A brief view through a real window can coincide with lower heart rate and skin conductance. The point is not that every window is therapeutic, but that visual access can become a measurable input to short-term stress.",
        "expanded_summary": "The fuller evidence is more modest and more useful. Participants in a controlled room showed physiological differences when blinds were open rather than closed, while cognitive effects were narrower. This makes the finding suitable for design hypotheses, not for universal promises.",
        "measurables": "Measured through skin conductance, heart rate, skin temperature, visual comfort ratings, and working-memory tasks.",
        "short_science_summary": "This study tested whether a window view changed short-term physiological and cognitive outcomes. The important feature is that the room condition was measured alongside bodily response and task performance. The result supports treating a view as an environmental input whose effects depend on task, duration, and setting.",
        "writing_agent": "llm_science_writer",
        "authoring_mode": "llm_authored",
        "writing_contract": verify.REQUIRED_CONTRACT,
        "llm_authoring": {
            "model": "gpt-5.5",
            "prompt_contract": verify.REQUIRED_CONTRACT,
            "source_claim_ids": ["1"],
            "quality_gate": "passed",
        },
        "longer_summary_link": "ka_article_view.html?id=PDF-0001",
        "source_link": "ka_article_view.html?id=PDF-0001",
        "apa_citation": "Example, A. (2026). Example title.",
    }


def test_current_dyk_payload_satisfies_llm_authoring_contract():
    assert verify.validate_payload(REPO_ROOT / "data" / "ka_payloads" / "did_you_know_llm_overrides.json") == []


def test_contract_rejects_python_authored_production_prose():
    card = _valid_card()
    card["authoring_mode"] = "python_generated"

    errors = verify.validate_card(card, 0)

    assert any("authoring_mode must be LLM or human" in error for error in errors)
    assert any("forbidden authoring mode" in error for error in errors)


def test_contract_rejects_llm_card_without_authoring_provenance():
    card = _valid_card()
    del card["llm_authoring"]

    errors = verify.validate_card(card, 0)

    assert any("lacks llm_authoring object" in error for error in errors)


def test_contract_rejects_internal_authorial_directions_in_public_text():
    card = _valid_card()
    card["expanded_summary"] = "The DYK should lead users toward the difference between dose and experience."

    errors = verify.validate_card(card, 0)

    assert any("authorial/template instruction" in error for error in errors)


def test_contract_accepts_human_edited_cards_without_llm_object():
    card = copy.deepcopy(_valid_card())
    card["authoring_mode"] = "human_authored"
    card["writing_agent"] = "human_editor"
    del card["llm_authoring"]

    assert verify.validate_card(card, 0) == []
