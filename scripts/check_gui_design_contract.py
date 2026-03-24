#!/usr/bin/env python3
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "gui_design_success_conditions.json"
DEFAULT_SCAN_DIRS = [ROOT, ROOT / "Designing_Experiments"]
DEFAULT_EXCLUDES = {".git", "__pycache__"}


@dataclass
class CheckResult:
    check_id: str
    description: str
    severity: str
    passed: bool


def load_config(path: Path) -> dict:
    return json.loads(path.read_text())


def iter_html_files(paths: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for base in paths:
        if base.is_file() and base.suffix.lower() == ".html":
            files.append(base)
            continue
        if not base.exists():
            continue
        for candidate in base.rglob("*.html"):
            if any(part in DEFAULT_EXCLUDES for part in candidate.parts):
                continue
            files.append(candidate)
    return sorted(set(files))


def run_regex_check(text: str, check: dict) -> bool:
    return re.search(check["pattern"], text, re.IGNORECASE | re.MULTILINE) is not None


def evaluate_file(path: Path, config: dict) -> list[CheckResult]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    results: list[CheckResult] = []
    for severity_key, severity in (("required_checks", "required"), ("warning_checks", "warning")):
        for check in config.get(severity_key, []):
            passed = run_regex_check(text, check)
            results.append(
                CheckResult(
                    check_id=check["id"],
                    description=check["description"],
                    severity=severity,
                    passed=passed,
                )
            )
    return results


def summarize(paths: Iterable[Path]) -> int:
    config = load_config(CONFIG_PATH)
    html_files = iter_html_files(paths)
    if not html_files:
        print("No HTML files found.")
        return 1

    required_failures = 0
    warning_failures = 0

    for path in html_files:
        results = evaluate_file(path, config)
        req = [r for r in results if r.severity == "required" and not r.passed]
        warn = [r for r in results if r.severity == "warning" and not r.passed]
        status = "PASS"
        if req:
            status = "FAIL"
            required_failures += len(req)
        elif warn:
            status = "WARN"
            warning_failures += len(warn)

        print(f"[{status}] {path}")
        for item in req + warn:
            print(f"  - {item.severity}: {item.check_id} :: {item.description}")

    print("---")
    print(f"Files scanned: {len(html_files)}")
    print(f"Required failures: {required_failures}")
    print(f"Warning failures: {warning_failures}")
    return 1 if required_failures else 0


if __name__ == "__main__":
    targets = [Path(arg).resolve() for arg in sys.argv[1:]] if len(sys.argv) > 1 else DEFAULT_SCAN_DIRS
    raise SystemExit(summarize(targets))
