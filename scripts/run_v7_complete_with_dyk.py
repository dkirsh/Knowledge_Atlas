#!/usr/bin/env python3
"""Run the offline V7-complete Did You Know generation stage.

This script is intentionally outside the KA browser runtime. It can use
subscription CLI by default or API mode when DK explicitly authorizes an offline
batch run. Public card prose is always authored by an LLM and then validated.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ka_dyk_writer import DYKSourcePacket, DYKWriterError, generate_dyk_card
from ka_llm_dispatch import LLMDispatchResult, call_llm
from scripts.verify_dyk_llm_authoring_contract import REQUIRED_CONTRACT, validate_card, validate_payload


DEFAULT_PAYLOAD_DIR = REPO_ROOT / "data" / "ka_payloads"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "v7_complete_dyk_cards"
DEFAULT_CONSOLIDATED = DEFAULT_PAYLOAD_DIR / "did_you_know_llm_overrides.json"
DEFAULT_INDEX = DEFAULT_PAYLOAD_DIR / "did_you_know_index.json"


class CostCeilingExceeded(RuntimeError):
    pass


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def _words(text: str) -> int:
    return len(str(text or "").split())


def load_payload_context(payload_dir: Path = DEFAULT_PAYLOAD_DIR) -> dict[str, Any]:
    articles = (_load_json(payload_dir / "articles.json", {"articles": []}).get("articles") or [])
    details = (_load_json(payload_dir / "article_details.json", {"details": {}}).get("details") or {})
    evidence = (_load_json(payload_dir / "evidence.json", {"evidence": []}).get("evidence") or [])
    by_paper: dict[str, list[dict[str, Any]]] = {}
    for claim in evidence:
        paper_id = str(claim.get("paper_id") or "")
        if paper_id:
            by_paper.setdefault(paper_id, []).append(claim)
    return {
        "articles_by_id": {str(row.get("paper_id")): row for row in articles if row.get("paper_id")},
        "details_by_id": details,
        "evidence_by_paper": by_paper,
    }


def _science_summary_text(detail: dict[str, Any], article: dict[str, Any]) -> str:
    summary = detail.get("science_summary") or {}
    pieces = [
        summary.get("core_finding") or "",
        summary.get("methods_and_design") or "",
        summary.get("key_statistics") or "",
        summary.get("design_implications") or "",
        summary.get("limitations") or "",
        article.get("main_conclusion") or "",
        article.get("abstract") or "",
    ]
    text = "\n\n".join(str(piece).strip() for piece in pieces if str(piece or "").strip())
    return text if _words(text) >= 60 else ""


def select_claims_for_paper(article: dict[str, Any], claims: list[dict[str, Any]], *, max_cards: int = 3) -> list[dict[str, Any]]:
    if not claims:
        return []
    article_type = str(article.get("article_type") or "").lower()
    threshold = 0.65 if "review" in article_type else 0.70
    eligible = [
        claim for claim in claims
        if float(claim.get("credence") or 0) >= threshold
        and str(claim.get("claim") or claim.get("finding") or "").strip()
    ]
    if not eligible:
        eligible = sorted(claims, key=lambda c: float(c.get("credence") or 0), reverse=True)[:1]
    selected: list[dict[str, Any]] = []
    seen_pairs: set[tuple[str, str]] = set()
    for claim in sorted(eligible, key=lambda c: (float(c.get("credence") or 0), int(c.get("support_count") or 0)), reverse=True):
        pair = (str(claim.get("primary_topic_id") or claim.get("primary_topic") or ""), str(claim.get("construct") or claim.get("warrant_class") or ""))
        if pair in seen_pairs and len(selected) >= 1:
            continue
        seen_pairs.add(pair)
        selected.append(claim)
        if len(selected) >= max_cards:
            break
    return selected


def selection_reason_for(article: dict[str, Any], selected: list[dict[str, Any]]) -> str:
    if len(selected) <= 1:
        return "default_one_card"
    article_type = str(article.get("article_type") or "").lower()
    if "review" in article_type:
        return "review_multi_claim"
    if article.get("landmark") or article.get("methodological_landmark"):
        return "methodological_landmark"
    return "multi_finding_high_credence"


def _metadata_for(article: dict[str, Any], detail: dict[str, Any]) -> dict[str, Any]:
    meta = dict(article)
    meta.update((detail.get("article_meta") or {}))
    meta["title"] = meta.get("title") or article.get("title") or ""
    meta["authors"] = meta.get("authors") or article.get("authors") or []
    meta["apa_citation"] = meta.get("apa_citation") or article.get("apa_citation") or ""
    return meta


def build_source_packet(article: dict[str, Any], detail: dict[str, Any], claim: dict[str, Any]) -> DYKSourcePacket | None:
    paper_id = str(article.get("paper_id") or claim.get("paper_id") or "")
    science_summary = _science_summary_text(detail, article)
    if not paper_id or not science_summary:
        return None
    meta = _metadata_for(article, detail)
    summary = detail.get("science_summary") or {}
    operational = detail.get("operationalization") or {}
    instruments = article.get("instruments") or detail.get("instruments") or []
    source_brief = "\n".join(
        str(item or "").strip()
        for item in (
            f"Claim: {claim.get('claim') or claim.get('finding') or ''}",
            f"Credence: {claim.get('credence')}; warrant: {claim.get('warrant_class') or claim.get('warrant') or ''}",
            f"Paper abstract: {article.get('abstract') or claim.get('abstract') or ''}",
            f"Core finding: {summary.get('core_finding') or ''}",
            f"Key statistics: {summary.get('key_statistics') or article.get('p_value') or ''}",
            f"Limitations: {summary.get('limitations') or ''}",
        )
        if str(item or "").strip()
    )
    methods = "\n".join(
        str(item or "").strip()
        for item in (
            summary.get("methods_and_design") or "",
            f"Instruments: {', '.join(str(x) for x in instruments)}" if instruments else "",
            f"Measures: {json.dumps(operational.get('measurement_inventory') or [])[:1200]}",
        )
        if str(item or "").strip()
    )
    sample = f"sample_n: {article.get('sample_n') or meta.get('sample_n') or ''}; setting/topic: {article.get('primary_topic') or ''}"
    claim_id = str(claim.get("id") or claim.get("claim_id") or f"{paper_id}_claim")
    return DYKSourcePacket(
        paper_id=paper_id,
        source_claim_ids=[claim_id],
        paper_metadata=meta,
        source_claim=claim,
        science_summary=science_summary,
        source_brief=source_brief[:4000],
        methods_and_measures=methods[:3000],
        sample=sample,
        topic_tags=[str(x) for x in (article.get("topic_labels") or claim.get("topic_labels") or [])],
        science_summary_dependency={"status": "available", "paper_id": paper_id, "source": "article_details.json"},
    )


def _per_paper_path(output_dir: Path, paper_id: str) -> Path:
    return output_dir / f"{paper_id}.json"


def _valid_cards(cards: list[dict[str, Any]]) -> bool:
    return bool(cards) and all(validate_card(card, i) == [] for i, card in enumerate(cards))


def load_existing_per_paper(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    payload = _load_json(path, {})
    cards = payload.get("cards")
    if isinstance(cards, list) and _valid_cards(cards):
        return payload
    return None


def generate_cards_for_paper(
    paper_id: str,
    context: dict[str, Any],
    *,
    output_dir: Path,
    max_cards_per_paper: int = 3,
    mode: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    llm_call: Callable[..., LLMDispatchResult] = call_llm,
    regenerate: str = "skip",
) -> dict[str, Any]:
    out_path = _per_paper_path(output_dir, paper_id)
    if regenerate == "skip":
        existing = load_existing_per_paper(out_path)
        if existing is not None:
            return {**existing, "status": "skipped_existing_valid", "path": str(out_path)}
    article = context["articles_by_id"].get(paper_id)
    if not article:
        return {"paper_id": paper_id, "status": "dyk_skipped_missing_article", "cards": [], "path": str(out_path)}
    detail = context["details_by_id"].get(paper_id) or {}
    claims = select_claims_for_paper(article, context["evidence_by_paper"].get(paper_id, []), max_cards=max_cards_per_paper)
    selection_reason = selection_reason_for(article, claims)
    if not claims:
        return {"paper_id": paper_id, "status": "dyk_skipped_no_source_claims", "cards": [], "path": str(out_path)}
    cards: list[dict[str, Any]] = []
    failures: list[str] = []
    for claim in claims:
        packet = build_source_packet(article, detail, claim)
        if packet is None:
            failures.append(f"{paper_id}: dyk_skipped_no_science_summary")
            continue
        try:
            cards.append(generate_dyk_card(packet, llm_call=llm_call, mode=mode, provider=provider, model=model))
        except DYKWriterError as exc:
            failures.append(f"{paper_id}:{claim.get('id')}: {exc}")
    status = "dyk_complete" if cards else ("dyk_generation_failed" if failures else "dyk_skipped")
    payload = {
        "schema_version": "ka_v7_complete_dyk_cards_per_paper_v1",
        "paper_id": paper_id,
        "status": status,
        "selection_reason": selection_reason,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cards": cards,
        "failures": failures,
    }
    _write_json(out_path, payload)
    return {**payload, "path": str(out_path)}


def _total_cost(cards: list[dict[str, Any]]) -> float:
    return round(sum(float((card.get("llm_authoring") or {}).get("cost_estimate_usd") or 0.0) for card in cards), 6)


def _card_count_distribution(results: list[dict[str, Any]]) -> dict[str, int]:
    distribution = {"0": 0, "1": 0, "2": 0, "3_plus": 0}
    for result in results:
        count = len(result.get("cards") or [])
        if count <= 0:
            distribution["0"] += 1
        elif count == 1:
            distribution["1"] += 1
        elif count == 2:
            distribution["2"] += 1
        else:
            distribution["3_plus"] += 1
    return distribution


def run_v7_complete_dyk_batch(
    paper_ids: list[str],
    *,
    payload_dir: Path = DEFAULT_PAYLOAD_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    batch_size: int = 50,
    concurrency: int = 1,
    cost_ceiling_usd: float = 250.0,
    consolidate_into: Path | None = None,
    mode: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    max_cards_per_paper: int = 3,
    llm_call: Callable[..., LLMDispatchResult] = call_llm,
    regenerate: str = "skip",
) -> dict[str, Any]:
    context = load_payload_context(payload_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    total_cost = 0.0
    for start in range(0, len(paper_ids), batch_size):
        batch = paper_ids[start:start + batch_size]
        if concurrency > 1:
            with ThreadPoolExecutor(max_workers=concurrency) as pool:
                futures = [
                    pool.submit(
                        generate_cards_for_paper,
                        paper_id,
                        context,
                        output_dir=output_dir,
                        max_cards_per_paper=max_cards_per_paper,
                        mode=mode,
                        provider=provider,
                        model=model,
                        llm_call=llm_call,
                        regenerate=regenerate,
                    )
                    for paper_id in batch
                ]
                batch_results = [future.result() for future in as_completed(futures)]
        else:
            batch_results = [
                generate_cards_for_paper(
                    paper_id,
                    context,
                    output_dir=output_dir,
                    max_cards_per_paper=max_cards_per_paper,
                    mode=mode,
                    provider=provider,
                    model=model,
                    llm_call=llm_call,
                    regenerate=regenerate,
                )
                for paper_id in batch
            ]
        results.extend(batch_results)
        batch_cards = [card for result in batch_results for card in (result.get("cards") or [])]
        total_cost += _total_cost(batch_cards)
        if total_cost > cost_ceiling_usd:
            raise CostCeilingExceeded(f"DYK run exceeded cost ceiling: ${total_cost:.4f} > ${cost_ceiling_usd:.4f}")
    consolidated_path = ""
    if consolidate_into is not None:
        consolidated_path = str(consolidate_dyk_payload(output_dir, consolidate_into=consolidate_into))
    return {
        "status": "complete",
        "paper_count": len(paper_ids),
        "cards_written": sum(len(result.get("cards") or []) for result in results),
        "card_count_distribution": _card_count_distribution(results),
        "estimated_cost_usd": round(total_cost, 6),
        "results": results,
        "consolidated_path": consolidated_path,
    }


def consolidate_dyk_payload(
    output_dir: Path,
    *,
    consolidate_into: Path = DEFAULT_CONSOLIDATED,
    index_path: Path | None = None,
    preserve_existing: bool = True,
) -> Path:
    index_path = index_path or (consolidate_into.parent / DEFAULT_INDEX.name)
    existing_cards = []
    if preserve_existing and consolidate_into.exists():
        existing_cards = (_load_json(consolidate_into, {"cards": []}).get("cards") or [])
    generated_cards = []
    for path in sorted(output_dir.glob("PDF-*.json")):
        payload = _load_json(path, {})
        cards = payload.get("cards") or []
        for index, card in enumerate(cards):
            errors = validate_card(card, index)
            if errors:
                raise RuntimeError(f"{path}: invalid DYK card: {'; '.join(errors[:4])}")
            generated_cards.append(card)
    by_id: dict[str, dict[str, Any]] = {}
    for card in existing_cards + generated_cards:
        by_id[str(card.get("id"))] = card
    cards = sorted(by_id.values(), key=lambda c: (str(c.get("paper_id") or ""), str(c.get("id") or "")))
    payload = {
        "schema_version": "ka_did_you_know_llm_overrides_v1",
        "writing_contract": REQUIRED_CONTRACT,
        "generation_note": {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "source": "v7_complete_dyk_batch",
            "existing_cards_preserved": len(existing_cards),
            "generated_cards_loaded": len(generated_cards),
            "total_cards": len(cards),
        },
        "cards": cards,
    }
    tmp_path = consolidate_into.with_suffix(consolidate_into.suffix + ".tmp")
    _write_json(tmp_path, payload)
    errors = validate_payload(tmp_path)
    if errors:
        tmp_path.unlink(missing_ok=True)
        raise RuntimeError("Consolidated DYK payload failed validation: " + "; ".join(errors[:8]))
    tmp_path.replace(consolidate_into)
    index = {
        "schema_version": "ka_did_you_know_index_v1",
        "generated_at": payload["generation_note"]["generated_at"],
        "card_count": len(cards),
        "by_paper": {},
    }
    for card in cards:
        index["by_paper"].setdefault(card.get("paper_id"), []).append(card.get("id"))
    _write_json(index_path, index)
    return consolidate_into


def main() -> int:
    parser = argparse.ArgumentParser(description="Run offline V7-complete DYK generation.")
    parser.add_argument("--corpus-list", required=True)
    parser.add_argument("--payload-dir", default=str(DEFAULT_PAYLOAD_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--consolidate-into", default="")
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--cost-ceiling-usd", type=float, default=250.0)
    parser.add_argument("--mode", choices=["subscription_cli", "api"], default=None)
    parser.add_argument("--provider", choices=["subscription", "anthropic", "openai", "google"], default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-cards-per-paper", type=int, default=3)
    parser.add_argument("--regenerate", choices=["skip", "all"], default="skip")
    args = parser.parse_args()

    paper_ids = [line.strip() for line in Path(args.corpus_list).read_text().splitlines() if line.strip() and not line.startswith("#")]
    result = run_v7_complete_dyk_batch(
        paper_ids,
        payload_dir=Path(args.payload_dir),
        output_dir=Path(args.output_dir),
        batch_size=args.batch_size,
        concurrency=max(1, args.concurrency),
        cost_ceiling_usd=args.cost_ceiling_usd,
        consolidate_into=Path(args.consolidate_into) if args.consolidate_into else None,
        mode=args.mode,
        provider=args.provider,
        model=args.model,
        max_cards_per_paper=args.max_cards_per_paper,
        regenerate=args.regenerate,
    )
    print(json.dumps({k: v for k, v in result.items() if k != "results"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
