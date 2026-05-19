#!/usr/bin/env python3
"""Offline LLM dispatch for V7-complete batch jobs.

Knowledge Atlas browser/runtime paths remain subscription-CLI-only. This module
is for offline batch jobs, including the AG V7-complete DYK run where DK may
explicitly authorize API credits for throughput.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from ka_subscription_llm import call_subscription_llm


DEFAULT_SUBSCRIPTION_COMMAND = "claude -p"
DEFAULT_CONTRACT = "OFFLINE_V7_COMPLETE_LLM_DISPATCH_2026-05-19"

MODEL_COSTS_PER_MILLION = {
    "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
    "claude-3-7-sonnet-20250219": {"input": 3.0, "output": 15.0},
    "gpt-4.1": {"input": 2.0, "output": 8.0},
    "gpt-4.1-mini": {"input": 0.4, "output": 1.6},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.0},
}


@dataclass(frozen=True)
class LLMDispatchResult:
    ok: bool
    text: str
    mode: str
    provider: str
    model: str
    invocation: dict[str, Any]
    error: str = ""


class LLMDispatchError(RuntimeError):
    pass


def _rough_tokens(text: str) -> int:
    return max(1, int(len(str(text or "").split()) * 1.33))


def estimate_cost_usd(model: str, tokens_in: int, tokens_out: int) -> float:
    rates = MODEL_COSTS_PER_MILLION.get(model, {"input": 3.0, "output": 15.0})
    return round(tokens_in / 1_000_000 * rates["input"] + tokens_out / 1_000_000 * rates["output"], 6)


def _api_key_env(provider: str) -> str:
    return {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "google": "GOOGLE_API_KEY",
    }.get(provider, "")


def _post_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _call_anthropic(prompt: str, *, model: str, timeout: int) -> str:
    api_key = os.environ.get(_api_key_env("anthropic"), "")
    if not api_key:
        raise LLMDispatchError("ANTHROPIC_API_KEY is required for provider=anthropic")
    payload = {
        "model": model,
        "max_tokens": 1800,
        "messages": [{"role": "user", "content": prompt}],
    }
    data = _post_json(
        "https://api.anthropic.com/v1/messages",
        {"x-api-key": api_key, "anthropic-version": "2023-06-01"},
        payload,
        timeout,
    )
    parts = data.get("content") or []
    return "\n".join(str(part.get("text") or "") for part in parts if isinstance(part, dict)).strip()


def _call_openai(prompt: str, *, model: str, timeout: int) -> str:
    api_key = os.environ.get(_api_key_env("openai"), "")
    if not api_key:
        raise LLMDispatchError("OPENAI_API_KEY is required for provider=openai")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
    }
    data = _post_json(
        "https://api.openai.com/v1/chat/completions",
        {"Authorization": f"Bearer {api_key}"},
        payload,
        timeout,
    )
    return str((((data.get("choices") or [{}])[0].get("message") or {}).get("content")) or "").strip()


def _call_google(prompt: str, *, model: str, timeout: int) -> str:
    api_key = os.environ.get(_api_key_env("google"), "")
    if not api_key:
        raise LLMDispatchError("GOOGLE_API_KEY is required for provider=google")
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    data = _post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
        {},
        payload,
        timeout,
    )
    candidates = data.get("candidates") or []
    parts = (((candidates[0] if candidates else {}).get("content") or {}).get("parts") or [])
    return "\n".join(str(part.get("text") or "") for part in parts if isinstance(part, dict)).strip()


def call_llm(
    prompt: str,
    *,
    mode: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    timeout: int = 180,
    subscription_env_var: str = "KA_DYK_LLM_COMMAND",
    default_subscription_command: str = DEFAULT_SUBSCRIPTION_COMMAND,
) -> LLMDispatchResult:
    mode = (mode or os.environ.get("LLM_INVOCATION_MODE") or "subscription_cli").strip()
    provider = (provider or os.environ.get("LLM_PROVIDER") or ("subscription" if mode == "subscription_cli" else "anthropic")).strip()
    model = (model or os.environ.get("LLM_MODEL") or ("subscription_cli" if mode == "subscription_cli" else "claude-3-5-sonnet-20241022")).strip()
    started = time.time()
    tokens_in = _rough_tokens(prompt)
    try:
        if mode == "subscription_cli":
            result = call_subscription_llm(
                prompt,
                env_var=subscription_env_var,
                default_command=default_subscription_command,
                timeout=timeout,
            )
            text = result.text
            if not result.ok:
                return LLMDispatchResult(
                    False,
                    "",
                    mode,
                    provider,
                    model,
                    {
                        "invocation_mode": mode,
                        "invocation_provider": provider,
                        "model": model,
                        "command": " ".join(result.command),
                        "tokens_in": tokens_in,
                        "tokens_out": 0,
                        "cost_estimate_usd": 0.0,
                    },
                    result.error,
                )
        elif mode == "api":
            if provider == "anthropic":
                text = _call_anthropic(prompt, model=model, timeout=timeout)
            elif provider == "openai":
                text = _call_openai(prompt, model=model, timeout=timeout)
            elif provider == "google":
                text = _call_google(prompt, model=model, timeout=timeout)
            else:
                raise LLMDispatchError(f"Unsupported API provider: {provider}")
        else:
            raise LLMDispatchError(f"Unsupported LLM invocation mode: {mode}")
    except urllib.error.HTTPError as exc:
        return LLMDispatchResult(False, "", mode, provider, model, {"invocation_mode": mode, "invocation_provider": provider, "model": model}, f"HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')[:500]}")
    except Exception as exc:
        return LLMDispatchResult(False, "", mode, provider, model, {"invocation_mode": mode, "invocation_provider": provider, "model": model}, str(exc))
    tokens_out = _rough_tokens(text)
    invocation = {
        "invocation_mode": mode,
        "invocation_provider": provider,
        "model": model,
        "invocation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost_estimate_usd": 0.0 if mode == "subscription_cli" else estimate_cost_usd(model, tokens_in, tokens_out),
    }
    return LLMDispatchResult(True, text, mode, provider, model, invocation, "")
