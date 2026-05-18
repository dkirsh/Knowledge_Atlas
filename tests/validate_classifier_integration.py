#!/usr/bin/env python3
"""
Validation harness for the Classifier Integration Contract.

Spec source of truth:
  Track 2/Phase 1 & 2/contracts/CLASSIFIER_INTEGRATION_CONTRACT_2026-05-09.md
  Track 2/Phase 1 & 2/contracts/schemas/classifier_response.json

What this script does:
  1. Spins up a fresh empty `articles` DB at $KA_STORAGE_ROOT/tmp_test/.
  2. Runs TC-1 .. TC-8 against POST /api/articles/submit on --base-url.
  3. Validates every response body against the post-merge JSON Schema.
  4. Checks invariants I-1, I-2a, I-2b, I-3 .. I-13 against the responses
     and on-disk state.
  5. Computes thresholds T-1 .. T-13.
  6. Writes a machine-readable report; exits 0 iff every record is pass.

This file is a SKELETON. Each `_todo_*` function raises NotImplementedError
and must be filled in alongside the implementation PR. The structure of the
report and the skeleton's CLI / argument handling are the binding part.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Callable

try:
    import jsonschema
except ImportError:
    sys.stderr.write("Missing dependency: pip install jsonschema scipy requests\n")
    raise


# ──────────────────────────────────────────────────────────────────────
# Result types
# ──────────────────────────────────────────────────────────────────────

@dataclass
class CheckResult:
    id: str
    kind: str        # "invariant" | "threshold" | "test_case" | "structural"
    passed: bool
    detail: str = ""
    measured: Any = None
    bound: Any = None


@dataclass
class Report:
    started_at: str
    finished_at: str = ""
    base_url: str = ""
    fixtures_dir: str = ""
    results: list[CheckResult] = field(default_factory=list)
    overall_pass: bool = False

    def add(self, r: CheckResult) -> None:
        self.results.append(r)

    def to_json(self) -> dict:
        return {
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "base_url": self.base_url,
            "fixtures_dir": self.fixtures_dir,
            "overall_pass": self.overall_pass,
            "results": [asdict(r) for r in self.results],
        }


# ──────────────────────────────────────────────────────────────────────
# Test-case runners (skeleton)
# ──────────────────────────────────────────────────────────────────────

def _todo_run_tc_1(env: "Env") -> CheckResult:
    """TC-1: clean accept of an on-topic PDF."""
    raise NotImplementedError("TC-1 runner not yet wired to live endpoint")


def _todo_run_tc_2(env: "Env") -> CheckResult:
    """TC-2: edge-case majority match against reviewer-labeled pool."""
    raise NotImplementedError("TC-2 runner pending reviewer labels in fixtures/edge_cases/")


def _todo_run_tc_3(env: "Env") -> CheckResult:
    """TC-3: bad-magic-bytes file rejected without quarantine write."""
    raise NotImplementedError("TC-3 runner")


def _todo_run_tc_4(env: "Env") -> CheckResult:
    """TC-4: SHA-256 duplicate of TC-1's bytes, no new row."""
    raise NotImplementedError("TC-4 runner")


def _todo_run_tc_5(env: "Env") -> CheckResult:
    """TC-5: DOI duplicate (different bytes), no new row."""
    raise NotImplementedError("TC-5 runner")


def _todo_run_tc_7(env: "Env") -> CheckResult:
    """TC-7: clean PDF, off-topic — verdict=reject, no quarantine write."""
    raise NotImplementedError("TC-7 runner")


def _todo_run_tc_8(env: "Env") -> CheckResult:
    """TC-8: mixed batch (accept + bad-magic + dup) — accept item still staged."""
    raise NotImplementedError("TC-8 runner")


# Note: TC-6 (frontend network failure) is verified separately via vitest.
# This script does not run it.


# ──────────────────────────────────────────────────────────────────────
# Invariant checkers (skeleton)
# ──────────────────────────────────────────────────────────────────────

def _todo_check_i1(env: "Env") -> CheckResult:
    """I-1: every classifier.verdict in {accept, edge_case, reject}."""
    raise NotImplementedError


def _todo_check_i2a_determinism(env: "Env") -> CheckResult:
    """I-2a: |conf₁ − conf₂| < 0.001 on duplicate submission of TC-1."""
    raise NotImplementedError


def _todo_check_i2b_monotonicity(env: "Env") -> CheckResult:
    """I-2b: Spearman ρ(human_rank, primary_topic_confidence) >= 0.5."""
    raise NotImplementedError("Requires labeled_20.json with human ranks")


def _todo_check_i3(env: "Env") -> CheckResult:
    """I-3: file at quarantine/<YYYY-MM>/<article_id>.pdf with matching SHA."""
    raise NotImplementedError


def _todo_check_i4(env: "Env") -> CheckResult:
    """I-4: duplicate items don't write to quarantine."""
    raise NotImplementedError


def _todo_check_i5(env: "Env") -> CheckResult:
    """I-5: article_type_confidence >= 0.50 ⇒ primary_topic non-null."""
    raise NotImplementedError


def _todo_check_i6(env: "Env") -> CheckResult:
    """I-6: audit_log row exists for every article_id with matching action."""
    raise NotImplementedError


def _todo_check_i7(env: "Env") -> CheckResult:
    """I-7: no non-PDF file present anywhere under quarantine/."""
    raise NotImplementedError


def _todo_check_i8(env: "Env") -> CheckResult:
    """I-8: every response body validates against the post-merge schema.

    Fails if zero responses were captured (vacuous truth would mask missing TCs)."""
    schema_path = env.contract_dir / "schemas" / "classifier_response.json"
    schema = json.loads(schema_path.read_text())
    if not env.captured_responses:
        return CheckResult(
            id="I-8", kind="invariant", passed=False,
            detail="No responses captured — TC runners must populate env.captured_responses before I-8 runs.",
            measured=0, bound=">= 1 response captured per TC that completes",
        )
    failures: list[str] = []
    for tc_id, response in env.captured_responses.items():
        try:
            jsonschema.validate(response, schema)
        except jsonschema.ValidationError as e:
            failures.append(f"{tc_id}: {e.message}")
    return CheckResult(
        id="I-8", kind="invariant",
        passed=not failures,
        detail="; ".join(failures) or f"all {len(env.captured_responses)} responses valid",
        measured=len(env.captured_responses),
        bound="0 schema errors",
    )


def _todo_check_i9(env: "Env") -> CheckResult:
    """I-9: ka.public_suggestions never written to localStorage.

    Verified statically by grep over the rendered HTML; no runtime check needed."""
    target = env.repo_root / "Knowledge_Atlas" / "ka_contribute_public.html"
    text = target.read_text()
    bad = (
        'localStorage.setItem("ka.public_suggestions"' in text
        or "localStorage.setItem('ka.public_suggestions'" in text
    )
    return CheckResult(
        id="I-9", kind="invariant",
        passed=not bad,
        detail="ka.public_suggestions write removed" if not bad else "FOUND in ka_contribute_public.html",
        bound="0 occurrences",
    )


def _todo_check_i10_i11(env: "Env") -> list[CheckResult]:
    """I-10 (submit re-enabled) and I-11 (no card on network failure).

    Verified by vitest, not this script. Reported here as 'deferred'."""
    return [
        CheckResult(id="I-10", kind="invariant", passed=False,
                    detail="DEFERRED — verified by vitest run, see test_contribute_public.spec.js"),
        CheckResult(id="I-11", kind="invariant", passed=False,
                    detail="DEFERRED — verified by vitest run, see test_contribute_public.spec.js"),
    ]


def _todo_check_i12(env: "Env") -> CheckResult:
    """I-12: dedup probe runs before any INSERT INTO articles.

    Verified end-to-end via TC-4/TC-5 row-count delta, not by mocking."""
    raise NotImplementedError


def _todo_check_i13(env: "Env") -> CheckResult:
    """I-13: classifier block present on non-rejected items.

    Plus structural check: grep for AdaptiveClassifierSubsystem in endpoints."""
    raise NotImplementedError


# ──────────────────────────────────────────────────────────────────────
# Threshold checkers (skeleton)
# ──────────────────────────────────────────────────────────────────────

def _todo_check_thresholds(env: "Env") -> list[CheckResult]:
    """T-1 .. T-13. Several depend on baseline.json (T-1, T-2, T-8)."""
    raise NotImplementedError


# Structural check supporting I-13.
#
# The classifier symbol appears 7× in ka_article_endpoints.py today (import +
# fallback + a separate `_classify_article_payload` helper called from other
# endpoints), but NOT inside the `submit_articles` handler at line 648-919.
# This PR adds the call there. We verify by extracting the body of
# `async def submit_articles(...)` and counting classifier calls inside it.
def check_structural_classifier_call_site(env: "Env") -> CheckResult:
    target = env.repo_root / "Knowledge_Atlas" / "ka_article_endpoints.py"
    text = target.read_text()
    import ast
    tree = ast.parse(text)
    submit_body_src = ""
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "submit_articles":
            submit_body_src = ast.get_source_segment(text, node) or ""
            break
    if not submit_body_src:
        return CheckResult(
            id="STRUCT-classifier-call-site", kind="structural",
            passed=False,
            detail="Could not locate async def submit_articles in ka_article_endpoints.py",
            bound="function present",
        )
    # Count both the canonical-helper call and direct classifier calls.
    helper_calls   = submit_body_src.count("_classify_article_payload(")
    direct_calls   = submit_body_src.count(".classify(")
    total_calls    = helper_calls + direct_calls
    return CheckResult(
        id="STRUCT-classifier-call-site",
        kind="structural",
        passed=total_calls >= 1,
        measured=total_calls,
        bound=">= 1 classifier call inside submit_articles()",
        detail=(f"submit_articles contains {helper_calls}× _classify_article_payload "
                f"and {direct_calls}× .classify() calls"),
    )


# ──────────────────────────────────────────────────────────────────────
# Environment & runner glue
# ──────────────────────────────────────────────────────────────────────

@dataclass
class Env:
    base_url: str
    fixtures_dir: Path
    repo_root: Path
    contract_dir: Path
    schema_path: Path
    legacy_schema_path: Path
    captured_responses: dict[str, dict] = field(default_factory=dict)


def run_all(env: Env, report: Report) -> Report:
    runners: list[Callable[[Env], CheckResult]] = [
        _todo_run_tc_1, _todo_run_tc_2, _todo_run_tc_3,
        _todo_run_tc_4, _todo_run_tc_5,
        _todo_run_tc_7, _todo_run_tc_8,
    ]
    for fn in runners:
        try:
            report.add(fn(env))
        except NotImplementedError as e:
            report.add(CheckResult(
                id=fn.__name__.removeprefix("_todo_run_").upper(),
                kind="test_case", passed=False,
                detail=f"SKELETON: {e}",
            ))

    invariant_runners: list[Callable[[Env], Any]] = [
        _todo_check_i1, _todo_check_i2a_determinism, _todo_check_i2b_monotonicity,
        _todo_check_i3, _todo_check_i4, _todo_check_i5, _todo_check_i6,
        _todo_check_i7, _todo_check_i8, _todo_check_i9,
        _todo_check_i10_i11,
        _todo_check_i12, _todo_check_i13,
    ]
    for fn in invariant_runners:
        try:
            res = fn(env)
            if isinstance(res, list):
                for r in res:
                    report.add(r)
            else:
                report.add(res)
        except NotImplementedError as e:
            report.add(CheckResult(
                id=fn.__name__.removeprefix("_todo_check_").upper(),
                kind="invariant", passed=False,
                detail=f"SKELETON: {e}",
            ))

    report.add(check_structural_classifier_call_site(env))

    try:
        for r in _todo_check_thresholds(env):
            report.add(r)
    except NotImplementedError as e:
        report.add(CheckResult(
            id="THRESHOLDS", kind="threshold", passed=False,
            detail=f"SKELETON: {e}",
        ))

    report.overall_pass = all(r.passed for r in report.results)
    report.finished_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return report


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://127.0.0.1:8765")
    p.add_argument("--fixtures", required=True, type=Path)
    p.add_argument("--report", required=True, type=Path)
    p.add_argument("--repo-root", type=Path,
                   default=Path(__file__).resolve().parents[2])
    args = p.parse_args(argv)

    repo_root: Path = args.repo_root
    contract_dir = repo_root / "Track 2" / "Phase 1 & 2" / "contracts"
    env = Env(
        base_url=args.base_url,
        fixtures_dir=args.fixtures,
        repo_root=repo_root,
        contract_dir=contract_dir,
        schema_path=contract_dir / "schemas" / "classifier_response.json",
        legacy_schema_path=contract_dir / "schemas" / "classifier_response.legacy.json",
    )

    report = Report(
        started_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        base_url=env.base_url,
        fixtures_dir=str(env.fixtures_dir),
    )
    run_all(env, report)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report.to_json(), indent=2))
    print(f"Report written: {args.report}")
    print(f"Overall pass: {report.overall_pass}")
    print(f"Records: {len(report.results)}; failed: {sum(1 for r in report.results if not r.passed)}")

    return 0 if report.overall_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
