"""
ka_critique_endpoints.py
========================

KA-T22: subscription-CLI-backed "Get AI Suggestions" endpoint for the usability
critic panel.

Accepts the structured ratings from `ka_usability_critic.js`, filters to the items
the student flagged as minor/major, and asks the local Claude subscription CLI
to produce a concrete suggestion + priority + estimated effort for each one.
Returns a JSON list the front-end renders inline below the summary.

Graceful degradation:
- If the subscription CLI is unavailable, the endpoint returns a rule-based
  canned response so the UI still works in local dev. The response body's
  `source` field is set to `"fallback"` in that case and `"llm"` when the
  subscription-CLI call succeeds.
- If the subscription-CLI call fails for any reason (timeout, malformed JSON,
  malformed JSON from the model), the endpoint does NOT return 502; it catches
  the exception, logs it, and silently falls back to the rule-based path so the
  panel remains usable. Callers should treat `source == "fallback"` as the
  signal that the LLM path did not complete.

The router is registered by `ka_auth_server.py`.  The endpoint is public — the
critic panel can be used without login — and does NOT currently attach a
`student_id` to the response. JWT-derived student tagging is a follow-up
(KA-T23/T24); until that ships, responses are anonymous.
"""
from __future__ import annotations

import os
import json
import logging
import shlex
import subprocess
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

log = logging.getLogger("ka.critique")

router = APIRouter(prefix="/api/critique", tags=["critique"])


# ── Request / response schemas ─────────────────────────────────────────────

class CritiqueItem(BaseModel):
    heuristicId: str = Field(..., description="Stable id like 'n3' or 'v8'")
    heuristicCode: Optional[str] = Field(None, description="Display code like 'H3' or 'V8'")
    heuristicLabel: str
    framework: Optional[str] = Field(
        None, description="'Nielsen' | 'Shneiderman' | 'Viz' or free text"
    )
    rating: str = Field(..., description="'pass' | 'minor' | 'major' | 'unrated'")
    note: Optional[str] = ""


class CritiqueContext(BaseModel):
    h1: Optional[str] = None
    title: Optional[str] = None
    vizElements: Optional[List[str]] = None


class CritiqueSuggestRequest(BaseModel):
    pageUrl: str
    pageTitle: str
    ratings: List[CritiqueItem]
    context: Optional[CritiqueContext] = None


class Suggestion(BaseModel):
    heuristicId: str
    heuristicLabel: str
    rating: str
    suggestion: str
    priority: str  # 'High' | 'Medium' | 'Low'
    estimatedEffort: str  # '15 min' | '1 hr' | 'Half day' etc.


class CritiqueSuggestResponse(BaseModel):
    suggestions: List[Suggestion]
    source: str  # 'llm' | 'fallback'
    note: Optional[str] = None


# ── Canned fallback (used when subscription CLI is unavailable) ────────────

_PRIORITY_BY_RATING = {"major": "High", "minor": "Medium", "pass": "Low"}


def _rule_based_suggestion(item: CritiqueItem) -> Suggestion:
    """A modest heuristic-based response when the LLM is unavailable.
    Not intended to replace the LLM — just to keep the UI functional offline."""
    rating = item.rating
    label = item.heuristicLabel
    note = (item.note or "").strip()
    priority = _PRIORITY_BY_RATING.get(rating, "Low")
    if rating == "major":
        effort = "Half day"
        prefix = f"Address the '{label}' violation"
    elif rating == "minor":
        effort = "30–60 min"
        prefix = f"Tighten the '{label}' dimension"
    else:
        effort = "15 min"
        prefix = f"Review '{label}'"
    suffix = f" Student observed: \"{note}\"" if note else ""
    suggestion = (
        f"{prefix} on this page.{suffix} "
        f"Review the heuristic's standard remedies (see Nielsen/Shneiderman/"
        f"Tufte source) and apply the smallest change that resolves the issue."
    )
    return Suggestion(
        heuristicId=item.heuristicId,
        heuristicLabel=label,
        rating=rating,
        suggestion=suggestion,
        priority=priority,
        estimatedEffort=effort,
    )


# ── LLM path ───────────────────────────────────────────────────────────────

_SYS_PROMPT = (
    "You are a concise usability reviewer. For each flagged heuristic violation "
    "on a Knowledge Atlas web page, produce ONE concrete, actionable suggestion. "
    "Be specific about what to change in the HTML/CSS/copy — no vague advice. "
    "Return strict JSON with an array 'suggestions'. Each item: "
    "{heuristicId, suggestion (<= 280 chars), priority ('High'|'Medium'|'Low'), "
    "estimatedEffort ('15 min'|'30-60 min'|'1 hr'|'Half day'|'Full day')}. "
    "Priority: major violations = High, minor = Medium, pass = Low. "
    "Output only JSON, no prose."
)


def _build_user_prompt(req: CritiqueSuggestRequest, flagged: List[CritiqueItem]) -> str:
    ctx = req.context or CritiqueContext()
    lines = [
        f"Page URL: {req.pageUrl}",
        f"Page title: {req.pageTitle}",
    ]
    if ctx.h1:
        lines.append(f"Main H1: {ctx.h1}")
    if ctx.vizElements:
        lines.append(f"Visualization elements detected: {', '.join(ctx.vizElements)}")
    lines.append("")
    lines.append("Flagged heuristics (fix each):")
    for item in flagged:
        note_part = f' — note: "{item.note.strip()}"' if item.note and item.note.strip() else ""
        lines.append(
            f"- heuristicId={item.heuristicId} | {item.framework or ''} {item.heuristicCode or ''} "
            f"{item.heuristicLabel} | rating={item.rating}{note_part}"
        )
    lines.append("")
    lines.append("Return JSON only.")
    return "\n".join(lines)


def _call_subscription_llm(system: str, user: str) -> str:
    """Call a local subscription CLI. API SDKs and API keys are forbidden."""
    command = shlex.split(os.environ.get("KA_CRITIQUE_LLM_COMMAND", "claude -p"))
    if not command:
        raise RuntimeError("KA_CRITIQUE_LLM_COMMAND is empty")
    prompt = system + "\n\n" + user
    completed = subprocess.run(
        command,
        input=prompt,
        text=True,
        capture_output=True,
        timeout=90,
        check=False,
    )
    if completed.returncode != 0:
        stderr = (completed.stderr or "").strip()
        raise RuntimeError(f"subscription CLI failed with code {completed.returncode}: {stderr[:300]}")
    return (completed.stdout or "").strip()


def _parse_llm_json(raw: str) -> List[Dict[str, Any]]:
    """Parse the LLM's JSON response.  Tolerant of ```json fences."""
    text = raw.strip()
    if text.startswith("```"):
        # Strip ``` and optional language tag
        text = text.lstrip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip("`\n ")
    # Find the first { or [
    start = min([i for i in (text.find("{"), text.find("[")) if i >= 0], default=-1)
    if start > 0:
        text = text[start:]
    data = json.loads(text)
    if isinstance(data, dict) and "suggestions" in data:
        return data["suggestions"]
    if isinstance(data, list):
        return data
    raise ValueError("Unexpected JSON shape from LLM")


# ── Endpoint ───────────────────────────────────────────────────────────────


@router.post("/suggest", response_model=CritiqueSuggestResponse)
def suggest_fixes(req: CritiqueSuggestRequest, request: Request):
    # Filter to items worth a suggestion
    flagged = [r for r in req.ratings if r.rating in ("minor", "major")]
    if not flagged:
        return CritiqueSuggestResponse(
            suggestions=[],
            source="fallback",
            note="No minor or major issues flagged; nothing to suggest.",
        )

    use_llm = os.environ.get("KA_CRITIQUE_DISABLE_LLM", "").lower() not in {"1", "true", "yes"}
    if not use_llm:
        log.info("Critique suggest: subscription LLM disabled, returning rule-based fallback")
        return CritiqueSuggestResponse(
            suggestions=[_rule_based_suggestion(i) for i in flagged],
            source="fallback",
            note="Subscription LLM disabled; showing rule-based suggestions.",
        )

    system = _SYS_PROMPT
    user = _build_user_prompt(req, flagged)
    try:
        raw = _call_subscription_llm(system, user)
        items = _parse_llm_json(raw)
    except Exception as e:
        log.exception("Critique suggest: LLM call failed: %s", e)
        # Fall back so the UI still gets useful output
        return CritiqueSuggestResponse(
            suggestions=[_rule_based_suggestion(i) for i in flagged],
            source="fallback",
            note=f"LLM call failed ({type(e).__name__}); showing rule-based suggestions.",
        )

    # Normalize — align returned items with the flagged heuristics
    flagged_by_id = {i.heuristicId: i for i in flagged}
    out: List[Suggestion] = []
    for it in items:
        hid = it.get("heuristicId")
        src = flagged_by_id.get(hid)
        if src is None:
            continue
        out.append(Suggestion(
            heuristicId=hid,
            heuristicLabel=src.heuristicLabel,
            rating=src.rating,
            suggestion=str(it.get("suggestion", "")).strip()[:600],
            priority=str(it.get("priority", _PRIORITY_BY_RATING.get(src.rating, "Low"))),
            estimatedEffort=str(it.get("estimatedEffort", "30–60 min")),
        ))
    # Backfill any missed items with rule-based suggestions
    covered = {s.heuristicId for s in out}
    for item in flagged:
        if item.heuristicId not in covered:
            out.append(_rule_based_suggestion(item))

    return CritiqueSuggestResponse(suggestions=out, source="llm")
