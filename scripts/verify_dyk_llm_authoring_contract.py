#!/usr/bin/env python3
"""Verify production Did You Know cards are not Python-authored prose.

Python is allowed to validate cards. It is not allowed to author production card
prose. This verifier makes that distinction executable.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAYLOAD = REPO_ROOT / "data" / "ka_payloads" / "did_you_know_llm_overrides.json"
REQUIRED_CONTRACT = "DID_YOU_KNOW_SCIENCE_WRITING_CONTRACT_2026-05-16"

ALLOWED_AUTHORING_MODES = {"llm_authored", "human_authored"}
ALLOWED_WRITING_AGENTS = {"llm_science_writer", "human_editor"}
FORBIDDEN_AUTHORING_MODES = {
    "python_generated",
    "python_authored",
    "template_generated",
    "heuristic_draft",
    "fallback",
    "scaffold",
    "scaffolded",
    "draft",
}
FORBIDDEN_PUBLIC_PROSE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bthe dyk should\b",
        r"\bthis dyk should\b",
        r"\bthis card should\b",
        r"\bthe card belongs\b",
        r"\bthe card should\b",
        r"\ba good dyk should\b",
        r"\busers should\b",
        r"\bpython generated\b",
        r"\btemplate generated\b",
        r"\bfallback prose\b",
    )
]
PROSE_FIELDS = ("title", "body", "expanded_summary", "measurables", "short_science_summary")


def _words(value: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", value or "")


def _card_label(card: dict[str, Any], index: int) -> str:
    return str(card.get("id") or card.get("paper_id") or f"card[{index}]")


def validate_card(card: dict[str, Any], index: int) -> list[str]:
    label = _card_label(card, index)
    errors: list[str] = []

    authoring_mode = str(card.get("authoring_mode") or "").strip()
    writing_agent = str(card.get("writing_agent") or "").strip()
    writing_contract = str(card.get("writing_contract") or "").strip()

    if authoring_mode not in ALLOWED_AUTHORING_MODES:
        errors.append(f"{label}: authoring_mode must be LLM or human, got {authoring_mode!r}")
    if authoring_mode in FORBIDDEN_AUTHORING_MODES:
        errors.append(f"{label}: forbidden authoring mode {authoring_mode!r}")
    if writing_agent not in ALLOWED_WRITING_AGENTS:
        errors.append(f"{label}: writing_agent must be science-writer/human editor, got {writing_agent!r}")
    if writing_contract != REQUIRED_CONTRACT:
        errors.append(f"{label}: writing_contract must be {REQUIRED_CONTRACT}")

    if authoring_mode == "llm_authored":
        llm = card.get("llm_authoring")
        if not isinstance(llm, dict):
            errors.append(f"{label}: llm_authored card lacks llm_authoring object")
        else:
            if not str(llm.get("model") or "").strip():
                errors.append(f"{label}: llm_authoring.model is required")
            if llm.get("prompt_contract") != REQUIRED_CONTRACT:
                errors.append(f"{label}: llm_authoring.prompt_contract must match writing contract")
            if llm.get("quality_gate") != "passed":
                errors.append(f"{label}: llm_authoring.quality_gate must be passed")
            source_claim_ids = llm.get("source_claim_ids")
            if not isinstance(source_claim_ids, list) or not source_claim_ids:
                errors.append(f"{label}: llm_authoring.source_claim_ids must be non-empty")
            elif card.get("source_claim_ids") and source_claim_ids != card.get("source_claim_ids"):
                errors.append(f"{label}: llm_authoring.source_claim_ids must match top-level source_claim_ids")
            invocation_mode = llm.get("invocation_mode")
            if invocation_mode is not None and invocation_mode not in {"api", "subscription_cli"}:
                errors.append(f"{label}: llm_authoring.invocation_mode must be api or subscription_cli")
            invocation_provider = llm.get("invocation_provider")
            if invocation_provider is not None and not str(invocation_provider).strip():
                errors.append(f"{label}: llm_authoring.invocation_provider must be non-empty when present")
            for numeric_field in ("tokens_in", "tokens_out", "cost_estimate_usd"):
                if numeric_field in llm and llm.get(numeric_field) is not None:
                    try:
                        if float(llm.get(numeric_field)) < 0:
                            errors.append(f"{label}: llm_authoring.{numeric_field} must be non-negative")
                    except Exception:
                        errors.append(f"{label}: llm_authoring.{numeric_field} must be numeric when present")

    for field in PROSE_FIELDS:
        value = card.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label}: missing public prose field {field}")
            continue
        for pattern in FORBIDDEN_PUBLIC_PROSE_PATTERNS:
            if pattern.search(value):
                errors.append(f"{label}: {field} contains authorial/template instruction: {pattern.pattern}")

    body = str(card.get("body") or "")
    expanded = str(card.get("expanded_summary") or "")
    if body and expanded:
        body_words = set(word.lower() for word in _words(body) if len(word) > 4)
        expanded_words = set(word.lower() for word in _words(expanded) if len(word) > 4)
        if body_words and len(body_words & expanded_words) / len(body_words) > 0.82:
            errors.append(f"{label}: expanded_summary appears to repeat the body")

    source_link = str(card.get("source_link") or "")
    longer_summary_link = str(card.get("longer_summary_link") or "")
    if not source_link.startswith("ka_article_view.html?id=PDF-"):
        errors.append(f"{label}: source_link must point to KA article page")
    if not longer_summary_link.startswith("ka_article_view.html?id=PDF-"):
        errors.append(f"{label}: longer_summary_link must point to KA article page")
    if not str(card.get("apa_citation") or "").strip():
        errors.append(f"{label}: apa_citation is required")

    return errors


def validate_payload(path: Path) -> list[str]:
    payload = json.loads(path.read_text())
    errors: list[str] = []
    if payload.get("writing_contract") != REQUIRED_CONTRACT:
        errors.append(f"payload: writing_contract must be {REQUIRED_CONTRACT}")
    cards = payload.get("cards")
    if not isinstance(cards, list) or not cards:
        return errors + ["payload: cards must be a non-empty list"]
    for index, card in enumerate(cards):
        if not isinstance(card, dict):
            errors.append(f"card[{index}]: must be an object")
            continue
        errors.extend(validate_card(card, index))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", nargs="?", default=str(DEFAULT_PAYLOAD))
    parser.add_argument("--strict", action="store_true", help="Return non-zero on any contract violation.")
    args = parser.parse_args()

    path = Path(args.payload)
    errors = validate_payload(path)
    if errors:
        print(f"FAIL did-you-know LLM authoring contract: {len(errors)} violation(s)")
        for error in errors:
            print(f"- {error}")
        return 1 if args.strict else 0
    print("PASS did-you-know LLM authoring contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
