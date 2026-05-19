#!/usr/bin/env python3
"""Verify KA runtime code does not use direct AI API calls.

Subscription CLIs are allowed. AI SDK imports, browser model API calls, and
browser-held AI API keys are not allowed in runtime paths.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_RUNTIME_PATHS = [
    "ka_auth_server.py",
    "ka_critique_endpoints.py",
    "ka_search_synthesis.py",
    "ka_search.html",
    "ka_substitution_skill.py",
    "ka_v7_lite.py",
    "ka_usability_critic.js",
    "scripts/track3/llm_wrapper_starter.py",
]

FORBIDDEN_PATTERNS = [
    "import anthropic",
    "import openai",
    "Anthropic(",
    "OpenAI(",
    "messages.create(",
    "responses.create(",
    "chat.completions",
    "generativelanguage.googleapis.com",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "ka_gemini_api_key",
]


def verify(paths: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        if not path.exists():
            errors.append(f"{path.relative_to(REPO_ROOT)}: missing runtime path")
            continue
        text = path.read_text(errors="replace")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in text:
                errors.append(f"{path.relative_to(REPO_ROOT)}: forbidden AI API pattern {pattern!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", help="Optional runtime paths to check.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero on violations.")
    args = parser.parse_args()

    paths = [REPO_ROOT / p for p in (args.paths or DEFAULT_RUNTIME_PATHS)]
    errors = verify(paths)
    if errors:
        print(f"FAIL subscription-AI-only contract: {len(errors)} violation(s)")
        for error in errors:
            print(f"- {error}")
        return 1 if args.strict else 0
    print("PASS subscription-AI-only contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
