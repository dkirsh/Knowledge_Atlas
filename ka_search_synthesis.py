#!/usr/bin/env python3
"""Server-side search synthesis through subscription CLIs only.

The browser must not hold AI API keys. This endpoint accepts source context from
`ka_search.html` and asks a local subscription CLI to write the answer.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ka_subscription_llm import SUBSCRIPTION_CLI_ONLY_CONTRACT, call_subscription_llm


router = APIRouter(prefix="/api/search", tags=["search_synthesis"])
SUBSCRIPTION_SYNTHESIS_CONTRACT = SUBSCRIPTION_CLI_ONLY_CONTRACT


class SearchSynthesisRequest(BaseModel):
    question: str = Field(..., min_length=1)
    context: str = ""
    system_prompt: str = ""
    mode: str = "concise"
    contract: str = SUBSCRIPTION_SYNTHESIS_CONTRACT


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
    result = call_subscription_llm(prompt, env_var="KA_SEARCH_SYNTH_LLM_COMMAND")
    if not result.ok:
        raise HTTPException(503, result.error)
    return {
        "answer": result.text,
        "source": "subscription_cli",
        "contract": SUBSCRIPTION_SYNTHESIS_CONTRACT,
    }
