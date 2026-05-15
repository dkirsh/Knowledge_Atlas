import json
from pathlib import Path

from scripts.build_topic_center_periphery import build_payload


REPO_ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = REPO_ROOT / "data" / "ka_payloads" / "topic_center_periphery.json"


def test_center_periphery_payload_has_reviewable_layers():
    payload = json.loads(PAYLOAD.read_text())

    assert payload["schema_version"] == "ka_topic_center_periphery_v1"
    assert payload["summary"]["topics_with_papers"] >= 5

    acoustic = next(topic for topic in payload["topics"] if topic["topic"] == "Acoustic Environment")
    assert acoustic["paper_count"] >= 10
    assert acoustic["center"]
    assert acoustic["inner_ring"]
    assert acoustic["periphery"]
    assert acoustic["method"]["status"] == "heuristic_needs_expert_review"

    center = acoustic["center"][0]
    assert center["layer"] == "center"
    assert center["role"] == "core"
    assert center["centrality_score"] >= 0
    assert center["interpretation_note"]


def test_center_periphery_can_build_for_single_given_topic():
    payload = build_payload(["Luminous Environment"])

    assert payload["summary"]["topic_count"] == 1
    topic = payload["topics"][0]
    assert topic["topic"] == "Luminous Environment"
    assert topic["paper_count"] >= 10
    roles = {paper["role"] for layer in ("center", "inner_ring", "periphery") for paper in topic[layer]}
    assert "core" in roles
    assert roles <= {
        "core",
        "confirmatory",
        "complementary",
        "modifying_or_extending",
        "redundant",
        "contested_or_boundary_condition",
    }


def test_adapter_rebuild_writes_center_periphery_payload():
    adapter = (REPO_ROOT / "scripts" / "build_ka_adapter_payloads.py").read_text()

    assert "build_topic_center_periphery_payload" in adapter
    assert "topic_center_periphery.json" in adapter
