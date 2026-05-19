from types import SimpleNamespace
from pathlib import Path

import ka_critique_endpoints as critique
import ka_search_synthesis as search_synth
from scripts.verify_subscription_ai_only_contract import DEFAULT_RUNTIME_PATHS, REPO_ROOT, verify


def test_search_synthesis_uses_subscription_cli_not_api(monkeypatch):
    calls = []

    def fake_run(command, input, text, capture_output, timeout, check):
        calls.append(
            {
                "command": command,
                "input": input,
                "text": text,
                "capture_output": capture_output,
                "timeout": timeout,
                "check": check,
            }
        )
        return SimpleNamespace(returncode=0, stdout="Answer\nRELEVANCE_ORDER: 1", stderr="")

    monkeypatch.setattr(search_synth.subprocess, "run", fake_run)

    result = search_synth.synthesize(
        search_synth.SearchSynthesisRequest(
            question="What does the corpus say about classroom acoustics?",
            context="SOURCE 1: classroom sound and stress",
            system_prompt="Use only sources.",
            contract=search_synth.SUBSCRIPTION_SYNTHESIS_CONTRACT,
        )
    )

    assert result["source"] == "subscription_cli"
    assert calls[0]["command"] == ["claude", "-p"]
    assert "Use only sources." in calls[0]["input"]


def test_critique_endpoint_uses_subscription_cli_not_api(monkeypatch):
    calls = []

    def fake_run(command, input, text, capture_output, timeout, check):
        calls.append({"command": command, "input": input})
        return SimpleNamespace(
            returncode=0,
            stdout='{"suggestions":[{"heuristicId":"n1","suggestion":"Clarify the first control label.","priority":"High","estimatedEffort":"15 min"}]}',
            stderr="",
        )

    monkeypatch.setattr(critique.subprocess, "run", fake_run)
    req = critique.CritiqueSuggestRequest(
        pageUrl="http://127.0.0.1/test",
        pageTitle="Test",
        ratings=[
            critique.CritiqueItem(
                heuristicId="n1",
                heuristicLabel="Visibility of system status",
                rating="major",
                note="The user cannot tell what changed.",
            )
        ],
    )

    result = critique.suggest_fixes(req, request=None)

    assert result.source == "llm"
    assert calls[0]["command"] == ["claude", "-p"]
    assert "Visibility of system status" in calls[0]["input"]


def test_runtime_ai_paths_do_not_import_api_sdks():
    assert Path(search_synth.__file__).exists()
    assert verify([REPO_ROOT / path for path in DEFAULT_RUNTIME_PATHS]) == []
