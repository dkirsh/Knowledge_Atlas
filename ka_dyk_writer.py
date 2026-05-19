#!/usr/bin/env python3
"""DYK science-writer stage for offline V7-complete runs.

Python assembles source packets, calls an LLM writer, merges metadata, and
validates the result. Python must not author the public DYK prose fields.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Callable

from ka_llm_dispatch import LLMDispatchResult, call_llm
from scripts.verify_dyk_llm_authoring_contract import REQUIRED_CONTRACT, validate_card


DYK_CARD_SCHEMA_VERSION = "ka_v7_complete_dyk_card_v1"
DYK_PROMPT_CONTRACT = REQUIRED_CONTRACT
PROSE_FIELDS = ("title", "body", "expanded_summary", "measurables", "short_science_summary")
WORD_BANDS = {
    "body": (50, 110),
    "expanded_summary": (75, 170),
    "measurables": (20, 90),
    "short_science_summary": (250, 450),
}


class DYKWriterError(RuntimeError):
    pass


@dataclass(frozen=True)
class DYKSourcePacket:
    paper_id: str
    source_claim_ids: list[str]
    paper_metadata: dict[str, Any]
    source_claim: dict[str, Any]
    science_summary: str
    source_brief: str
    methods_and_measures: str
    sample: str
    topic_tags: list[str]
    science_summary_dependency: dict[str, Any]


def _words(value: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", str(value or ""))


def _parse_json_object(text: str) -> dict[str, Any]:
    stripped = str(text or "").strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, flags=re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass
    starts = [match.start() for match in re.finditer(r"\{", stripped)]
    for start in reversed(starts):
        depth = 0
        in_string = False
        escape = False
        for index in range(start, len(stripped)):
            char = stripped[index]
            if escape:
                escape = False
                continue
            if char == "\\" and in_string:
                escape = True
                continue
            if char == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(stripped[start:index + 1])
    raise DYKWriterError("LLM did not return a JSON object")


def dyk_id_for(paper_id: str, source_claim_id: str) -> str:
    digest = hashlib.sha1(f"{paper_id}:{source_claim_id}".encode("utf-8")).hexdigest()[:10]
    return f"dyk_{digest}"


def build_prompt(packet: DYKSourcePacket, *, retry_feedback: str = "") -> str:
    metadata = packet.paper_metadata
    claim = packet.source_claim
    feedback = f"\n=== Previous validation failure ===\n{retry_feedback}\n" if retry_feedback else ""
    return f"""SYSTEM:
You are a science writer for the Knowledge Atlas, writing public-facing
"Did You Know" cards about peer-reviewed research on the built environment and
human experience. Your audience is undergraduate Cognitive Science students and
curious practitioners: informed, but not specialised.

Use only the source material below. Do not invent papers, results, measures,
statistics, figures, theory names, or citations. Return only JSON.

USER:
=== Paper metadata ===
paper_id: {packet.paper_id}
title: {metadata.get('title') or ''}
authors: {metadata.get('authors') or ''}
year: {metadata.get('year') or ''}
doi: {metadata.get('doi') or ''}
venue: {metadata.get('venue') or ''}
apa_citation: {metadata.get('apa_citation') or ''}

=== Source claim ===
claim_id: {packet.source_claim_ids[0]}
claim_text: {claim.get('claim') or claim.get('finding') or ''}
warrant_class: {claim.get('warrant_class') or claim.get('warrant') or ''}
credence: {claim.get('credence') if claim.get('credence') is not None else ''}

=== Existing science summary ===
{packet.science_summary}

=== Source-backed brief ===
{packet.source_brief}

=== Methods and measures ===
{packet.methods_and_measures}

=== Sample ===
{packet.sample}

=== Topic tags ===
{', '.join(packet.topic_tags)}
{feedback}
=== Quality rules ===
1. title states an intelligible claim, not a label. Max 100 characters.
2. body's first sentence identifies the phenomenon in ordinary language.
3. body explains what changes, under what condition, and why it matters. 50-110 words.
4. expanded_summary continues the explanation; it must not repeat the body. 75-170 words.
5. measurables describes how the phenomenon is measured. 20-90 words.
6. short_science_summary is a longer source-grounded summary. 250-450 words.
7. No authorial instructions in public text: never write "this card should",
   "the DYK should", "users should", or similar.
8. No Python-template phrasing, fallback markers, or private process notes.

Return ONLY a JSON object with exactly these fields:
{{
  "title": "...",
  "body": "...",
  "expanded_summary": "...",
  "measurables": "...",
  "short_science_summary": "...",
  "source_claim_ids": ["{packet.source_claim_ids[0]}"]
}}
"""


def _normalize_prose(value: Any) -> str:
    return " ".join(str(value or "").split())


def merge_card_metadata(packet: DYKSourcePacket, prose: dict[str, Any], dispatch: LLMDispatchResult) -> dict[str, Any]:
    claim_id = str((prose.get("source_claim_ids") or packet.source_claim_ids)[0])
    metadata = packet.paper_metadata
    invocation = dict(dispatch.invocation or {})
    invocation.setdefault("model", dispatch.model)
    invocation.setdefault("invocation_mode", dispatch.mode)
    invocation.setdefault("invocation_provider", dispatch.provider)
    return {
        "id": dyk_id_for(packet.paper_id, claim_id),
        "paper_id": packet.paper_id,
        "source_claim_ids": [str(value) for value in (prose.get("source_claim_ids") or packet.source_claim_ids)],
        "title": _normalize_prose(prose.get("title")),
        "body": _normalize_prose(prose.get("body")),
        "expanded_summary": _normalize_prose(prose.get("expanded_summary")),
        "measurables": _normalize_prose(prose.get("measurables")),
        "short_science_summary": _normalize_prose(prose.get("short_science_summary")),
        "writing_agent": "llm_science_writer",
        "authoring_mode": "llm_authored",
        "writing_contract": DYK_PROMPT_CONTRACT,
        "llm_authoring": {
            "model": invocation.get("model") or dispatch.model,
            "prompt_contract": DYK_PROMPT_CONTRACT,
            "source_claim_ids": [str(value) for value in (prose.get("source_claim_ids") or packet.source_claim_ids)],
            "quality_gate": "passed",
            "invocation_mode": invocation.get("invocation_mode") or dispatch.mode,
            "invocation_provider": invocation.get("invocation_provider") or dispatch.provider,
            "invocation_timestamp": invocation.get("invocation_timestamp") or "",
            "tokens_in": invocation.get("tokens_in"),
            "tokens_out": invocation.get("tokens_out"),
            "cost_estimate_usd": invocation.get("cost_estimate_usd"),
        },
        "science_summary_dependency": packet.science_summary_dependency,
        "longer_summary_link": f"ka_article_view.html?id={packet.paper_id}",
        "source_link": f"ka_article_view.html?id={packet.paper_id}",
        "apa_citation": metadata.get("apa_citation") or _fallback_apa(metadata),
    }


def _fallback_apa(metadata: dict[str, Any]) -> str:
    authors = metadata.get("authors") or "Unknown author"
    if isinstance(authors, list):
        authors = ", ".join(str(a) for a in authors if a)
    year = metadata.get("year") or "n.d."
    title = metadata.get("title") or "Untitled paper"
    doi = metadata.get("doi") or ""
    return f"{authors} ({year}). {title}.{(' https://doi.org/' + doi) if doi and not str(doi).startswith('http') else (' ' + doi if doi else '')}".strip()


def validate_generated_card(card: dict[str, Any]) -> list[str]:
    errors = validate_card(card, 0)
    if len(str(card.get("title") or "")) > 100:
        errors.append(f"{card.get('id', 'card')}: title exceeds 100 characters")
    for field, (lo, hi) in WORD_BANDS.items():
        count = len(_words(str(card.get(field) or "")))
        if count < lo or count > hi:
            errors.append(f"{card.get('id', 'card')}: {field} word count {count} outside {lo}-{hi}")
    return errors


def generate_dyk_card(
    packet: DYKSourcePacket,
    *,
    llm_call: Callable[..., LLMDispatchResult] = call_llm,
    mode: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    max_attempts: int = 2,
) -> dict[str, Any]:
    feedback = ""
    last_error = ""
    for _attempt in range(1, max_attempts + 1):
        prompt = build_prompt(packet, retry_feedback=feedback)
        dispatch = llm_call(prompt, mode=mode, provider=provider, model=model)
        if not dispatch.ok:
            last_error = dispatch.error or "LLM call failed"
            feedback = last_error
            continue
        try:
            prose = _parse_json_object(dispatch.text)
        except Exception as exc:
            last_error = f"malformed JSON: {exc}"
            feedback = last_error
            continue
        card = merge_card_metadata(packet, prose, dispatch)
        errors = validate_generated_card(card)
        if not errors:
            return card
        last_error = "; ".join(errors[:8])
        feedback = last_error
    raise DYKWriterError(last_error or "DYK generation failed")
