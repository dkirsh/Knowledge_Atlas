#!/usr/bin/env python3
"""Build topic-level center/periphery paper analyses.

The analysis is intentionally heuristic. It ranks papers by how close they are
to a topic's claim centroid, how much source-backed evidence they carry, and
how much new signal they add relative to already-central papers. It does not
pretend to know the "best" paper without expert review.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_DIR = REPO_ROOT / "data" / "ka_payloads"
DEFAULT_OUTPUT = PAYLOAD_DIR / "topic_center_periphery.json"

TOKEN_RE = re.compile(r"[a-z][a-z0-9_/-]{2,}")
STOPWORDS = {
    "about",
    "after",
    "also",
    "among",
    "and",
    "are",
    "because",
    "between",
    "can",
    "from",
    "has",
    "have",
    "into",
    "not",
    "paper",
    "show",
    "shows",
    "study",
    "that",
    "the",
    "their",
    "this",
    "through",
    "using",
    "with",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def high_topic(label: str) -> str:
    text = str(label or "").strip()
    for sep in ("→", "->"):
        if sep in text:
            return text.split(sep, 1)[0].strip()
    return text or "Unspecified"


def tokens(*parts: Any) -> Counter[str]:
    text = " ".join(str(part or "") for part in parts).lower()
    out: Counter[str] = Counter()
    for token in TOKEN_RE.findall(text):
        token = token.strip("-_/")
        if token and token not in STOPWORDS:
            out[token] += 1
    return out


def cosine(a: Counter[str], b: Counter[str]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(value * b.get(term, 0) for term, value in a.items())
    norm_a = math.sqrt(sum(value * value for value in a.values()))
    norm_b = math.sqrt(sum(value * value for value in b.values()))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def norm(value: float, cap: float) -> float:
    if cap <= 0:
        return 0.0
    return max(0.0, min(1.0, value / cap))


def article_topic_labels(article: dict[str, Any]) -> list[str]:
    labels = []
    if article.get("primary_topic"):
        labels.append(str(article["primary_topic"]))
    for key in ("topic_labels", "fronts"):
        for item in article.get(key) or []:
            if isinstance(item, str) and item not in labels:
                labels.append(item)
    return labels


def matches_topic(article: dict[str, Any], evidence_rows: list[dict[str, Any]], topic: str) -> bool:
    topic_lower = topic.lower()
    labels = article_topic_labels(article)
    if any(topic_lower == label.lower() or topic_lower == high_topic(label).lower() for label in labels):
        return True
    for row in evidence_rows:
        label = str(row.get("primary_topic") or "")
        if topic_lower == label.lower() or topic_lower == high_topic(label).lower():
            return True
    return False


def build_analysis(topic: str, articles_payload: dict[str, Any], evidence_payload: dict[str, Any]) -> dict[str, Any]:
    articles = articles_payload.get("articles") or []
    evidence = evidence_payload.get("evidence") or []
    evidence_by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in evidence:
        paper_id = str(row.get("paper_id") or "").strip()
        if paper_id:
            evidence_by_paper[paper_id].append(row)

    paper_rows: list[dict[str, Any]] = []
    paper_tokens: dict[str, Counter[str]] = {}
    for article in articles:
        paper_id = str(article.get("paper_id") or "").strip()
        if not paper_id:
            continue
        rows = evidence_by_paper.get(paper_id, [])
        if not matches_topic(article, rows, topic):
            continue
        claim_text = " ".join(str(row.get("claim") or row.get("finding") or "") for row in rows)
        vec = tokens(
            article.get("title"),
            article.get("abstract"),
            article.get("main_conclusion"),
            article.get("primary_topic"),
            claim_text,
        )
        if not vec:
            continue
        paper_tokens[paper_id] = vec
        paper_rows.append({"article": article, "evidence": rows})

    centroid: Counter[str] = Counter()
    for vec in paper_tokens.values():
        centroid.update(vec)

    if not paper_rows:
        return {
            "topic": topic,
            "paper_count": 0,
            "center": [],
            "inner_ring": [],
            "periphery": [],
            "notes": ["No papers matched this topic label in the current KA payload."],
        }

    max_claims = max(len(row["evidence"]) for row in paper_rows) or 1
    max_support = max(
        sum(int(ev.get("support_count") or 0) for ev in row["evidence"]) for row in paper_rows
    ) or 1

    scored = []
    for row in paper_rows:
        article = row["article"]
        ev_rows = row["evidence"]
        paper_id = article["paper_id"]
        avg_credence = (
            sum(float(ev.get("credence") or 0.0) for ev in ev_rows) / len(ev_rows)
            if ev_rows
            else 0.0
        )
        support = sum(int(ev.get("support_count") or 0) for ev in ev_rows)
        attacks = sum(int(ev.get("attack_count") or 0) for ev in ev_rows)
        claim_count = len(ev_rows) or int(article.get("claim_count") or 0)
        centrality = cosine(paper_tokens[paper_id], centroid)
        primary_bonus = 1.0 if high_topic(article.get("primary_topic")) == topic or article.get("primary_topic") == topic else 0.0
        warrant_score = max(0.0, avg_credence - attacks * 0.05)
        score = (
            centrality * 0.34
            + norm(claim_count, max_claims) * 0.22
            + norm(support, max_support) * 0.16
            + warrant_score * 0.20
            + primary_bonus * 0.08
        )
        scored.append(
            {
                "paper_id": paper_id,
                "title": article.get("title") or article.get("apa_citation") or paper_id,
                "year": article.get("year") or "",
                "article_type": article.get("article_type") or "",
                "primary_topic": article.get("primary_topic") or "",
                "centrality_score": round(score, 4),
                "topic_centroid_similarity": round(centrality, 4),
                "claim_count": claim_count,
                "support_count": support,
                "attack_count": attacks,
                "average_credence": round(avg_credence, 3),
                "constructs": article.get("constructs") or [],
                "theories": article.get("theories") or [],
                "sample_n": article.get("sample_n") or article.get("subject_count_total") or "",
                "main_conclusion": article.get("main_conclusion") or "",
                "_tokens": paper_tokens[paper_id],
            }
        )

    scored.sort(key=lambda item: item["centrality_score"], reverse=True)
    center_cut = max(1, min(5, math.ceil(len(scored) * 0.12)))
    inner_cut = max(center_cut + 1, min(len(scored), math.ceil(len(scored) * 0.40)))
    center_vectors = [item["_tokens"] for item in scored[:center_cut]]

    for index, item in enumerate(scored):
        similarity_to_center = max((cosine(item["_tokens"], vec) for vec in center_vectors), default=0.0)
        item["similarity_to_center"] = round(similarity_to_center, 4)
        item["layer"] = "center" if index < center_cut else "inner_ring" if index < inner_cut else "periphery"
        item["role"] = role_for(item, similarity_to_center)
        item["interpretation_note"] = note_for(item)
        del item["_tokens"]

    return {
        "topic": topic,
        "paper_count": len(scored),
        "method": {
            "status": "heuristic_needs_expert_review",
            "score_inputs": [
                "topic-centroid text similarity",
                "claim count",
                "support count",
                "average credence",
                "primary-topic match",
                "redundancy relative to center papers",
            ],
            "non_promises": [
                "does not assert definitive historical importance",
                "does not replace expert review of insightfulness",
            ],
        },
        "center": scored[:center_cut],
        "inner_ring": scored[center_cut:inner_cut],
        "periphery": scored[inner_cut:],
    }


def role_for(item: dict[str, Any], similarity_to_center: float) -> str:
    if item["attack_count"] > 0:
        return "contested_or_boundary_condition"
    if item["layer"] == "center":
        return "core"
    if similarity_to_center >= 0.86 and item["claim_count"] <= 2:
        return "redundant"
    if similarity_to_center >= 0.72:
        return "confirmatory"
    if 0.45 <= similarity_to_center < 0.72 and item["claim_count"] >= 2:
        return "modifying_or_extending"
    return "complementary"


def note_for(item: dict[str, Any]) -> str:
    if item["role"] == "core":
        return "Candidate center paper: close to the topic centroid and carries a relatively large share of topic evidence."
    if item["role"] == "confirmatory":
        return "Supports the center pattern without obviously changing the topic frame."
    if item["role"] == "redundant":
        return "Very close to center papers and currently adds little unique signal in the payload."
    if item["role"] == "modifying_or_extending":
        return "Close enough to the center to matter, but appears to add a qualification, adjacent construct, or extension."
    if item["role"] == "contested_or_boundary_condition":
        return "Carries attacks or dispute markers; useful for limits and counter-arguments."
    return "Peripheral but useful as a neighboring case, design variation, or less-central evidence path."


def available_topics(articles_payload: dict[str, Any], evidence_payload: dict[str, Any]) -> list[str]:
    topics = set()
    for article in articles_payload.get("articles") or []:
        for label in article_topic_labels(article):
            topics.add(high_topic(label))
            topics.add(label)
    for row in evidence_payload.get("evidence") or []:
        label = str(row.get("primary_topic") or "")
        if label:
            topics.add(high_topic(label))
            topics.add(label)
    return sorted(topic for topic in topics if topic and topic != "Unknown")


def build_payload_from_payloads(
    articles_payload: dict[str, Any],
    evidence_payload: dict[str, Any],
    topics: list[str] | None = None,
) -> dict[str, Any]:
    selected = topics or available_topics(articles_payload, evidence_payload)
    analyses = [build_analysis(topic, articles_payload, evidence_payload) for topic in selected]
    return {
        "schema_version": "ka_topic_center_periphery_v1",
        "generated_at": utc_now(),
        "source_files": {
            "articles": "data/ka_payloads/articles.json",
            "evidence": "data/ka_payloads/evidence.json",
        },
        "summary": {
            "topic_count": len(analyses),
            "topics_with_papers": sum(1 for item in analyses if item["paper_count"] > 0),
        },
        "topics": analyses,
    }


def build_payload(topics: list[str] | None = None) -> dict[str, Any]:
    articles_payload = load_json(PAYLOAD_DIR / "articles.json")
    evidence_payload = load_json(PAYLOAD_DIR / "evidence.json")
    return build_payload_from_payloads(articles_payload, evidence_payload, topics)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", action="append", help="Topic label or high-level topic to analyze. Repeatable.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    payload = build_payload(args.topic)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(payload['topics'])} topic center/periphery analyses to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
