#!/usr/bin/env python3
"""Calibrate V7-Lite topic thresholds from the current KA payload.

This is a deterministic local approximation of the spec's centroid holdout
protocol. It uses the same lexical centroid machinery as `ka_v7_lite.py`,
computes each member paper's similarity to its topic centroid, and stores the
5th percentile as that topic's threshold.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import ka_v7_lite

DEFAULT_OUTPUT = REPO_ROOT / "data" / "v7_lite_topic_thresholds.json"


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.12
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * p
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - rank) + ordered[upper] * (rank - lower)


def calibrate() -> dict:
    centroids = ka_v7_lite._topic_centroids()
    topic_thresholds: dict[str, float] = {}
    diagnostics: dict[str, dict] = {}
    for topic_id, info in centroids.items():
        values = [
            ka_v7_lite._cosine(
                ka_v7_lite._token_counts(ka_v7_lite._article_text(row)),
                info["vector"],
            )
            for row in info["rows"]
        ]
        values = [value for value in values if value > 0]
        if not values:
            continue
        # The V7-Lite query is often only a title plus a short abstract, whereas
        # member-paper centroid scores are computed from richer payload records.
        # Cap the local lexical threshold so calibration does not over-reject
        # plausible student uploads before the full embedding store is wired in.
        threshold = max(0.05, min(0.20, percentile(values, 0.05)))
        topic_thresholds[topic_id] = round(threshold, 3)
        diagnostics[topic_id] = {
            "label": info["label"],
            "n": len(values),
            "min": round(min(values), 3),
            "median": round(statistics.median(values), 3),
            "p05": round(percentile(values, 0.05), 3),
        }
    return {
        "schema_version": "ka_v7_lite_topic_thresholds_v1",
        "method": "lexical_centroid_member_5th_percentile",
        "default_threshold": 0.12,
        "topics": topic_thresholds,
        "diagnostics": diagnostics,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(calibrate(), indent=2, sort_keys=True) + "\n")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
