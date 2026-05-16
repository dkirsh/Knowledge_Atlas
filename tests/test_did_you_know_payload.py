import json
from pathlib import Path

from scripts.build_did_you_know_payload import build_payload


REPO_ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_DIR = REPO_ROOT / "data" / "ka_payloads"


def test_did_you_know_payload_exists_and_is_source_backed():
    payload = json.loads((PAYLOAD_DIR / "did_you_know.json").read_text())

    assert payload["schema_version"] == "ka_did_you_know_v1"
    assert payload["source_kind"] == "ka_evidence_did_you_know_generator"
    assert payload["science_writer"]["agent"] == "science_writer"
    assert payload["summary"]["card_count"] >= 25

    sample = next(card for card in payload["cards"] if card["verification_status"] == "source_backed")
    assert sample["id"].startswith("dyk_")
    assert sample["title"]
    assert sample["body"]
    assert sample["source_claim_ids"]
    assert sample["source_paper_ids"]
    assert sample["topic_labels"]
    assert sample["writing_agent"] == "science_writer"
    assert sample["verification_status"] == "source_backed"
    assert sample["evidence_strength"] in {"strong", "moderate", "emerging", "contested"}
    assert 0 <= sample["confidence"] <= 1


def test_generator_refuses_to_create_cards_without_source_claim_or_paper():
    payload = build_payload(
        {
            "evidence": [
                {
                    "id": 1,
                    "paper_id": "",
                    "claim": "A long enough claim that would otherwise be eligible if it had a source paper.",
                    "primary_topic": "Lighting -> Sleep",
                    "credence": 0.9,
                },
                {
                    "id": 2,
                    "paper_id": "PDF-TEST",
                    "claim": "",
                    "primary_topic": "Lighting -> Sleep",
                    "credence": 0.9,
                },
            ]
        },
        limit=10,
        include_hand_authored=False,
    )

    assert payload["summary"]["card_count"] == 0
    assert payload["cards"] == []


def test_generator_preserves_claim_source_and_marks_science_writer_version():
    payload = build_payload(
        {
            "evidence": [
                {
                    "id": 42,
                    "paper_id": "PDF-0042",
                    "claim": "Morning daylight exposure improved alertness and sleep outcomes in office workers.",
                    "finding": "Morning daylight exposure improved alertness and sleep outcomes in office workers.",
                    "primary_topic": "Luminous Environment -> Sleep Quality",
                    "primary_topic_id": "luminous__sleep",
                    "topic_ids": ["luminous__sleep"],
                    "credence": 0.92,
                    "support_count": 6,
                    "attack_count": 0,
                    "paper_title": "Daylight and sleep in office workers",
                    "citation": "Author (2024). Daylight and sleep in office workers.",
                }
            ]
        },
        limit=10,
        include_hand_authored=False,
    )

    card = payload["cards"][0]
    assert card["source_claim_ids"] == ["42"]
    assert card["source_paper_ids"] == ["PDF-0042"]
    assert card["topic_ids"] == ["luminous__sleep"]
    assert card["evidence_strength"] == "strong"
    assert card["writing_agent_version"].startswith("science_writer_dyk_v1")
    assert "Morning daylight exposure" in card["body"]


def test_hand_authored_dyk_cards_are_included_and_marked_curated():
    payload = build_payload({"evidence": []}, limit=10)
    cards = {card["id"]: card for card in payload["cards"]}

    assert payload["summary"]["hand_authored_card_count"] == 8
    assert payload["summary"]["generated_card_count"] == 0
    assert payload["summary"]["card_count"] == 8
    assert "dyk_hand_predictive_processing" in cards
    assert "dyk_hand_material_textures" in cards

    card = cards["dyk_hand_predictive_processing"]
    assert "unresolved prediction error" in card["body"]
    assert card["writing_agent"] == "human_curated"
    assert card["verification_status"] == "hand_authored_curated"
    assert card["source_claim_ids"] == []
    assert card["source_paper_ids"] == []
    assert "topic_browser" in card["journey_tags"]


def test_acoustic_physiology_card_explains_stimulus_and_response():
    payload = build_payload(
        {
            "evidence": [
                {
                    "id": 252,
                    "paper_id": "PDF-0181",
                    "claim": (
                        "Prodi and Visentin examined conditions in two classrooms with different RT, "
                        "one quiet and one noisy, on school children."
                    ),
                    "primary_topic": "Acoustic Environment -> Physiological Response",
                    "primary_topic_id": "acoustic__physio",
                    "topic_ids": ["acoustic__physio"],
                    "credence": 0.87,
                    "support_count": 5,
                    "attack_count": 0,
                    "paper_title": "Indicators and methods for assessing acoustical preferences in schools",
                    "sensor_summary": "EEG, electrodermal, heart rate, pupil",
                }
            ]
        },
        limit=10,
        include_hand_authored=False,
    )

    card = payload["cards"][0]
    assert card["title"] == "Classroom sound can change children's bodies, not just their attention."
    assert card["body"].startswith("The acoustic stimulus is a classroom soundscape")
    assert "EEG, electrodermal activity, heart rate, and pupil response" in card["body"]


def test_home_pages_load_generated_dyk_runtime():
    for filename in ("ka_home.html", "ka_home_student.html", "ka_home_student_new.html", "ka_did_you_know.html"):
        text = (REPO_ROOT / filename).read_text()
        assert "ka_did_you_know.js" in text

    home = (REPO_ROOT / "ka_home.html").read_text()
    assert "hydrateHomeGrid('#dykGrid', 3)" in home
    assert 'id="dykGrid"' in home

    dyk_page = (REPO_ROOT / "ka_did_you_know.html").read_text()
    assert "loadDidYouKnowCards" in dyk_page
    assert "journeyFilter" in dyk_page


def test_topic_dyk_page_filters_high_level_topics():
    text = (REPO_ROOT / "ka_topics_dyk.html").read_text()

    assert "High-level topics" in text
    assert "MAX_VISIBLE = 40" in text
    assert "highTopic(card)" in text
    assert "sourceText(card)" in text
    assert "More" in text
    assert "writing_agent || 'science_writer'" not in text
    assert "loadDidYouKnowCards" in text


def test_adapter_rebuild_writes_generated_dyk_payload():
    adapter = (REPO_ROOT / "scripts" / "build_ka_adapter_payloads.py").read_text()

    assert "build_did_you_know_payload" in adapter
    assert "did_you_know.json" in adapter
