import json
import re
from pathlib import Path

import pytest

from ka_llm_dispatch import LLMDispatchResult
from scripts import run_v7_complete_with_dyk as runner
from scripts.verify_dyk_llm_authoring_contract import validate_payload


def _summary_text():
    return (
        "The science summary reports a controlled built-environment study in which a measurable room condition was compared with an alternative condition. "
        "The paper describes the environmental manipulation, the participant task, the dependent variables, and the uncertainty around interpretation. "
        "It is long enough to serve as the upstream science-writer dependency for a Did You Know card. "
        "The summary emphasizes that the claim is useful because it connects a design feature to cognitive, physiological, or affective outcomes without pretending that one study settles the whole field. "
        "It also records the methods, instruments, sample, and limitations so the card writer can explain what changed, how it was measured, and why the result matters."
    )


def _write_payloads(root: Path, paper_ids=("PDF-0001", "PDF-0002", "PDF-0003")):
    payload_dir = root / "payloads"
    payload_dir.mkdir()
    articles = []
    details = {}
    evidence = []
    for index, paper_id in enumerate(paper_ids, start=1):
        articles.append(
            {
                "paper_id": paper_id,
                "title": f"Built environment test paper {index}",
                "year": 2026,
                "doi": f"10.0000/example.{index}",
                "authors": [f"Author {index}"],
                "apa_citation": f"Author {index}. (2026). Built environment test paper {index}.",
                "abstract": "A controlled study tested how an environmental condition changed attention and physiology.",
                "article_type": "empirical_research",
                "primary_topic": "Acoustic Environment → Cognitive Performance",
                "topic_labels": ["Acoustic Environment → Cognitive Performance"],
                "sample_n": 40 + index,
                "instruments": ["PVT", "heart rate"],
            }
        )
        details[paper_id] = {
            "science_summary": {
                "core_finding": _summary_text(),
                "methods_and_design": "Participants completed attention tasks while physiological measures were recorded.",
                "key_statistics": "Reported tests were available in the source packet.",
                "limitations": "The sample and setting limit generalization.",
            }
        }
        evidence.append(
            {
                "id": index,
                "paper_id": paper_id,
                "claim": "The environmental condition changed response speed and physiological arousal during the task.",
                "finding": "The environmental condition changed response speed and physiological arousal during the task.",
                "credence": 0.82,
                "warrant_class": "empirical_association",
                "primary_topic": "Acoustic Environment → Cognitive Performance",
                "topic_labels": ["Acoustic Environment → Cognitive Performance"],
            }
        )
    (payload_dir / "articles.json").write_text(json.dumps({"articles": articles}))
    (payload_dir / "article_details.json").write_text(json.dumps({"details": details}))
    (payload_dir / "evidence.json").write_text(json.dumps({"evidence": evidence}))
    return payload_dir


def _valid_llm_json(prompt: str, *, short_body: bool = False):
    claim_match = re.search(r"claim_id:\s*(\S+)", prompt)
    claim_id = claim_match.group(1) if claim_match else "1"
    body = (
        "Too short."
        if short_body
        else "A room condition can change how quickly people respond during a demanding task. In this study, the environmental contrast was not merely background decoration; it became part of the cognitive load. The result matters because a measurable feature of the setting was linked to attention, performance, or bodily regulation in the same experimental frame."
    )
    expanded = (
        "The fuller point is practical and cautious. The paper gives designers a way to think about an environmental variable as an experimental input rather than a vague atmosphere. It also shows why a result should be tied to the task, exposure, participant group, and measurement window. A classroom, office, or laboratory may produce different outcomes if those conditions change. The value of the card is that it makes the causal question concrete without pretending that the present evidence has already solved every boundary condition."
    )
    measurables = (
        "Measured with task performance, response timing, physiological recording, participant ratings, sample description, exposure details, and the controlled comparison between environmental conditions."
    )
    summary = " ".join(
        [
            "This paper tested a built-environment condition as a measurable input to human performance and bodily state.",
            "The useful feature of the study is that it does not treat the room as a neutral container.",
            "Instead, the source packet connects an environmental contrast with task outcomes, physiological recording, and participant context.",
            "That gives the card writer enough evidence to explain the finding without turning it into a universal design rule.",
            "The claim is strongest as a prompt for better experiments: define the stimulus, specify the exposure, record the task, and measure more than one response channel.",
            "The uncertainty is also part of the story because the paper is one study in a broader evidence base.",
            "Sample size, task difficulty, setting, participant expectations, and measurement timing can all alter the observed result.",
            "A production Atlas card should therefore make the phenomenon clear while keeping the warrant modest.",
            "The finding is useful when it helps a reader ask what changed, who was measured, how the outcome was recorded, and what would count as a stronger replication.",
            "It belongs in a topic browser because it gives beginners a concrete doorway into the relation between environmental form and cognitive or physiological response.",
            "It also supports later navigation to the article page, where the longer science summary, measures, and limitations can be reviewed.",
            "The most careful interpretation is not that one design feature always causes one outcome.",
            "It is that built conditions can be treated as testable variables when the measurement strategy is explicit and the uncertainty is visible.",
        ]
    )
    return json.dumps(
        {
            "title": "Room Conditions Can Change Task Performance",
            "body": body,
            "expanded_summary": expanded,
            "measurables": measurables,
            "short_science_summary": summary,
            "source_claim_ids": [claim_id],
        }
    )


def _fake_result(text: str, *, cost=0.0):
    return LLMDispatchResult(
        ok=True,
        text=text,
        mode="api",
        provider="anthropic",
        model="claude-test",
        invocation={
            "invocation_mode": "api",
            "invocation_provider": "anthropic",
            "model": "claude-test",
            "invocation_timestamp": "2026-05-19T00:00:00Z",
            "tokens_in": 100,
            "tokens_out": 100,
            "cost_estimate_usd": cost,
        },
    )


def test_v7_complete_dyk_batch_generates_and_consolidates(tmp_path):
    payload_dir = _write_payloads(tmp_path)
    output_dir = tmp_path / "dyk"
    consolidated = tmp_path / "did_you_know_llm_overrides.json"

    def fake_call(prompt, **kwargs):
        return _fake_result(_valid_llm_json(prompt), cost=0.01)

    result = runner.run_v7_complete_dyk_batch(
        ["PDF-0001", "PDF-0002", "PDF-0003"],
        payload_dir=payload_dir,
        output_dir=output_dir,
        consolidate_into=consolidated,
        batch_size=2,
        cost_ceiling_usd=1.0,
        max_cards_per_paper=1,
        llm_call=fake_call,
        mode="api",
    )

    assert result["cards_written"] == 3
    assert result["card_count_distribution"]["1"] == 3
    assert (output_dir / "PDF-0001.json").exists()
    per_paper = json.loads((output_dir / "PDF-0001.json").read_text())
    assert per_paper["selection_reason"] == "default_one_card"
    assert validate_payload(consolidated) == []
    index = json.loads((tmp_path / "did_you_know_index.json").read_text())
    assert index["card_count"] == 3


def test_v7_complete_dyk_batch_retries_malformed_json_and_word_count(tmp_path):
    payload_dir = _write_payloads(tmp_path, paper_ids=("PDF-0001", "PDF-0002"))
    calls = {"PDF-0001": 0, "PDF-0002": 0}

    def fake_call(prompt, **kwargs):
        paper_match = re.search(r"paper_id:\s*(PDF-\d+)", prompt)
        paper_id = paper_match.group(1)
        calls[paper_id] += 1
        if paper_id == "PDF-0001" and calls[paper_id] == 1:
            return _fake_result("not json")
        if paper_id == "PDF-0002" and calls[paper_id] == 1:
            return _fake_result(_valid_llm_json(prompt, short_body=True))
        return _fake_result(_valid_llm_json(prompt))

    result = runner.run_v7_complete_dyk_batch(
        ["PDF-0001", "PDF-0002"],
        payload_dir=payload_dir,
        output_dir=tmp_path / "dyk",
        batch_size=2,
        max_cards_per_paper=1,
        llm_call=fake_call,
        mode="api",
    )

    assert result["cards_written"] == 2
    assert calls == {"PDF-0001": 2, "PDF-0002": 2}


def test_v7_complete_dyk_batch_enforces_cost_ceiling(tmp_path):
    payload_dir = _write_payloads(tmp_path, paper_ids=("PDF-0001",))

    def fake_call(prompt, **kwargs):
        return _fake_result(_valid_llm_json(prompt), cost=2.0)

    with pytest.raises(runner.CostCeilingExceeded):
        runner.run_v7_complete_dyk_batch(
            ["PDF-0001"],
            payload_dir=payload_dir,
            output_dir=tmp_path / "dyk",
            cost_ceiling_usd=0.25,
            max_cards_per_paper=1,
            llm_call=fake_call,
            mode="api",
        )
