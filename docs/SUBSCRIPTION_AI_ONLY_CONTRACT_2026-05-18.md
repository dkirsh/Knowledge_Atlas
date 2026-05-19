# Subscription AI Only Contract

Date: 2026-05-18

AI calls in Knowledge Atlas production paths must use local subscription CLIs.
Direct AI API calls are forbidden.

## Rule

Use `claude -p`, `codex exec`, or another approved local subscription CLI for
LLM work. Do not use OpenAI, Anthropic, Gemini, or other AI API SDKs from KA
runtime code. Do not ask users to paste browser-held AI API keys.

## Why

Two failures must be impossible:

- a repetitive production task silently switches to Python prose or a template
  instead of an LLM science-writer pass;
- an implementation bypasses the subscription tools and starts using API keys.

## Allowed

- Python may assemble source packets, validate fields, run deterministic
  ranking, and call local subscription CLI commands.
- UI code may call KA server endpoints that themselves use subscription CLIs.
- Deterministic fallback text may keep a non-production tool usable when a
  subscription CLI is unavailable, but fallback text must be marked as fallback
  and must not be represented as LLM-authored science prose.

## Forbidden

- `import anthropic`, `import openai`, or direct AI SDK client construction in KA
  runtime modules.
- Browser calls to AI model APIs.
- Browser storage of AI API keys.
- Production DYK prose authored by Python templates or deterministic fallback
  rules.

## Mechanical Gates

- `tests/test_subscription_ai_contract.py` verifies runtime AI paths use
  subscription CLI commands and not API SDKs.
- `scripts/verify_subscription_ai_only_contract.py --strict` provides a
  standalone runtime-path scan for direct AI API patterns.
- `scripts/verify_dyk_llm_authoring_contract.py --strict` verifies production
  Did You Know prose is LLM- or human-authored, never Python-authored.
