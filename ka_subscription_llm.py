#!/usr/bin/env python3
"""Subscription-CLI LLM helper for Knowledge Atlas.

This module is the only supported runtime path for LLM prose generation in KA.
It calls local subscription CLIs such as `claude -p` or `codex exec`; it does
not use AI API SDKs or browser-held API keys.
"""

from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass


SUBSCRIPTION_CLI_ONLY_CONTRACT = "SUBSCRIPTION_CLI_ONLY_NO_AI_API_KEYS"


@dataclass(frozen=True)
class SubscriptionLLMResult:
    ok: bool
    text: str
    command: tuple[str, ...]
    error: str = ""


def call_subscription_llm(
    prompt: str,
    *,
    env_var: str,
    default_command: str = "claude -p",
    timeout: int = 120,
) -> SubscriptionLLMResult:
    """Call a local subscription CLI and return a structured result.

    Failure is non-exceptional at this boundary because public endpoints must be
    able to return structured facts even if the prose writer is unavailable.
    """
    command = shlex.split(os.environ.get(env_var, default_command))
    if not command:
        return SubscriptionLLMResult(False, "", tuple(), f"{env_var} is empty")
    try:
        completed = subprocess.run(
            command,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except Exception as exc:
        return SubscriptionLLMResult(False, "", tuple(command), str(exc))
    if completed.returncode != 0:
        return SubscriptionLLMResult(
            False,
            "",
            tuple(command),
            (completed.stderr or "").strip()[:500],
        )
    return SubscriptionLLMResult(True, (completed.stdout or "").strip(), tuple(command), "")
