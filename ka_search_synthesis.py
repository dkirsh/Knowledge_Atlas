#!/usr/bin/env python3
"""Server-side search synthesis through subscription CLIs only.

The browser must not hold AI API keys. This endpoint accepts source context from
`ka_search.html` and asks a local subscription CLI to write the answer.
"""

from __future__ import annotations

import os
import shlex
import subprocess

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/search", tags=["search_synthesis"])
SUBSCRIPTION_SYNTHESIS_CONTRACT = "SUBSCRIPTION_CLI_ONLY_NO_AI_API_KEYS"


class SearchSynthesisRequest(BaseModel):
    question: str = Field(..., min_length=1)
    context: str = ""
    system_prompt: str = ""
    mode: str = "concise"
    contract: str = SUBSCRIPTION_SYNTHESIS_CONTRACT


def call_subscription_cli(prompt: str) -> str:
    command = shlex.split(os.environ.get("KA_SEARCH_SYNTH_LLM_COMMAND", "claude -p"))
    if not command:
        raise RuntimeError("KA_SEARCH_SYNTH_LLM_COMMAND is empty")
    completed = subprocess.run(
        command,
        input=prompt,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )
    if completed.returncode != 0:
        stderr = (completed.stderr or "").strip()
        raise RuntimeError(f"subscription CLI failed with code {completed.returncode}: {stderr[:300]}")
    return (completed.stdout or "").strip()


@router.post("/synthesize")
def synthesize(req: SearchSynthesisRequest) -> dict[str, str]:
    if req.contract != SUBSCRIPTION_SYNTHESIS_CONTRACT:
        raise HTTPException(400, "Search synthesis requires subscription-CLI-only contract.")
    if len(req.context) > 120_000:
        raise HTTPException(413, "Context too large for synchronous synthesis.")
    prompt = "\n\n".join(
        part
        for part in (
            req.system_prompt.strip(),
            f"QUESTION: {req.question.strip()}",
            req.context.strip(),
        )
        if part
    )
    try:
        answer = call_subscription_cli(prompt)
    except Exception as exc:
        raise HTTPException(503, str(exc)) from exc
    return {
        "answer": answer,
        "source": "subscription_cli",
        "contract": SUBSCRIPTION_SYNTHESIS_CONTRACT,
    }
