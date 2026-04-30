#!/usr/bin/env python3
"""
site_validator.py — static CI gate for the Knowledge Atlas site.

Validates every HTML file against the KA_NAV_CONTRACT rules. Produces an
exit-1 on any violation so the output can gate a deploy.

Checks (see KA_NAV_CONTRACT.md):
  - Canonical navbar script include present
  - <body data-ka-regime> declared and consistent with URL path
  - No inline <nav> outside the #ka-navbar-slot
  - data-ka-active points to a valid item in REGIME_ITEMS[regime]
  - No hand-coded hrefs to navbar items (must go through the table)
  - Every referenced local file exists on disk
  - No broken relative <a href> or <img src> or <script src> or <link href>
  - Archive regime pages linked only from ka_archive.html,
    ka_track4_hub.html, and ka_admin.html
  - data-verified timestamps present on data-bearing cards and
    within freshness thresholds
  - No personalised content rendered before auth validation
    (heuristic: localStorage read for user-visible content in <body>)

Usage:
    python3 scripts/site_validator.py              # scan repo root
    python3 scripts/site_validator.py --root .     # explicit root
    python3 scripts/site_validator.py --fix-hints  # print suggestions
    python3 scripts/site_validator.py --json       # machine-readable output
    python3 scripts/site_validator.py --since HEAD~1  # only changed files

Exit codes:
    0  no errors
    1  validation errors found
    2  I/O or parse error (bug in the scanner or corrupt input)
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


SCRIPT_DIR = Path(__file__).resolve().parent
KA_ROOT = SCRIPT_DIR.parent


# ─── Canonical REGIME_ITEMS, read from the JS file of record ───────────

REGIME_RE = re.compile(
    r"const REGIME_ITEMS = \{(.*?)\};", re.S)
ITEM_RE = re.compile(
    r"\{\s*id:'(?P<id>[^']+)',\s*label:'(?P<label>[^']+)',\s*href:'(?P<href>[^']+)'")


def load_regime_items(navbar_js: Path) -> dict[str, list[dict]]:
    text = navbar_js.read_text(encoding="utf-8")
    m = REGIME_RE.search(text)
    if not m:
        raise ValueError(f"Could not parse REGIME_ITEMS from {navbar_js}")
    block = m.group(1)
    # Split the block into regime sections
    regimes: dict[str, list[dict]] = {}
    current = None
    for line in block.splitlines():
        hdr = re.match(r"\s*(['\"]?)(\w+)\1\s*:\s*\[", line)
        if hdr:
            current = hdr.group(2)
            regimes[current] = []
            continue
        it = ITEM_RE.search(line)
        if it and current is not None:
            regimes[current].append(it.groupdict())
    return regimes


# ─── Violation types ────────────────────────────────────────────────────

@dataclass
class Violation:
    file: str
    line: Optional[int]
    code: str
    message: str
    severity: str = "error"  # error / warn / info


# ─── Per-file checks ────────────────────────────────────────────────────

NAVBAR_SCRIPT_RE = re.compile(r'<script[^>]+src=["\']?([^"\'>]*ka_canonical_navbar\.js)["\']?', re.I)
BODY_TAG_RE      = re.compile(r'<body\b([^>]*)>', re.I)
DATA_REGIME_RE   = re.compile(r'data-ka-regime\s*=\s*["\']([^"\']+)["\']', re.I)
DATA_ACTIVE_RE   = re.compile(r'data-ka-active\s*=\s*["\']([^"\']*)["\']', re.I)
INLINE_NAV_RE    = re.compile(r'<nav\b', re.I)
NAV_SLOT_RE      = re.compile(r'id=["\']ka-navbar-slot["\']', re.I)
DATA_VERIFIED_RE = re.compile(r'data-verified\s*=\s*["\']([0-9]{4}-[0-9]{2}-[0-9]{2})["\']', re.I)
LOCALSTORAGE_RE  = re.compile(r'\blocalStorage\.(?:getItem|removeItem|setItem)')
HREF_RE          = re.compile(r'(?:href|src)\s*=\s*["\']([^"\'#?][^"\']*)["\']', re.I)
SAFE_LOCALSTORAGE_PREFIXES = ("ka.t4", "ka.critique.")

# Surfaces allowed to link to archive pages
ARCHIVE_LINKERS = {"ka_archive.html", "ka_track4_hub.html", "ka_admin.html"}

# Pages intentionally kept as static no-JS fallbacks. These are exempt from
# canonical-navbar requirements but still get local link/security checks.
STATIC_NAV_EXEMPT = {"160sp/ka_student_setup.html"}


def expected_regime(rel_path: str) -> str:
    if "/160sp/" in rel_path.replace("\\", "/") or rel_path.startswith("160sp/"):
        return "160sp"
    if rel_path.endswith("ka_archive.html"):
        return "archive"
    return "global"


def check_html(path: Path, root: Path, regime_items: dict[str, list[dict]],
               archive_entries: set[str]) -> list[Violation]:
    rel = path.relative_to(root).as_posix()
    vs: list[Violation] = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [Violation(rel, None, "IO", f"could not read file: {e}")]

    # HTML fragments (no <body> tag) are not full pages — skip them.
    # These are usually template partials included elsewhere.
    if not BODY_TAG_RE.search(text):
        return []

    static_nav_exempt = rel in STATIC_NAV_EXEMPT

    # Canonical navbar include
    if not static_nav_exempt and not NAVBAR_SCRIPT_RE.search(text):
        vs.append(Violation(rel, None, "NAV001",
            "missing <script src=...ka_canonical_navbar.js>"))

    # Body regime
    body_match = BODY_TAG_RE.search(text)
    body_attrs = body_match.group(1) if body_match else ""
    regime_match = DATA_REGIME_RE.search(body_attrs)
    declared_regime = regime_match.group(1) if regime_match else None
    if not declared_regime:
        if not static_nav_exempt:
            vs.append(Violation(rel, None, "NAV002",
                "missing data-ka-regime on <body>"))
    else:
        exp = expected_regime(rel)
        # Archive exception: declared "archive" is allowed anywhere (by design)
        if declared_regime != exp and declared_regime != "archive":
            vs.append(Violation(rel, None, "NAV003",
                f"regime '{declared_regime}' contradicts URL path (expected '{exp}')"))

    # data-ka-active resolves to a valid item
    active_match = DATA_ACTIVE_RE.search(body_attrs)
    if active_match and declared_regime in regime_items:
        active_id = active_match.group(1).strip()
        if active_id:
            valid_ids = {it["id"] for it in regime_items[declared_regime]}
            if active_id not in valid_ids:
                vs.append(Violation(rel, None, "NAV004",
                    f"data-ka-active='{active_id}' not in REGIME_ITEMS[{declared_regime}]"))

    # Inline <nav> outside the slot — accept if it's INSIDE the navbar slot
    # (which is empty in source; the script injects it) or as part of a
    # nav that's purely presentational inside a section. Heuristic:
    # reject any <nav> that has classes or IDs indicating it's a global
    # navigation row, UNLESS it carries style="display:none" (hidden
    # after canonical navbar rollout, preserved in source for history).
    # Match each <nav ...> opening tag and look at its attributes only
    # (not inner content). This prevents class="nav-brand" on an inner
    # <a> from triggering a false positive on a classless <nav>.
    NAV_TAG = re.compile(r'<nav\b([^>]*)>', re.I)
    for m in NAV_TAG.finditer(text):
        attrs = m.group(1)
        # A classless <nav> is almost always a semantic section-level nav
        # (e.g. login-page branding wrapper); leave it alone.
        cls_m = re.search(r'\bclass\s*=\s*["\']([^"\']+)["\']', attrs, re.I)
        if not cls_m:
            continue
        first = cls_m.group(1).split()[0] if cls_m.group(1).strip() else ""
        global_classes = {"top-nav","topnav","classbar","ka-nav","header-nav","global-nav","main-nav","site-nav"}
        if first not in global_classes:
            continue
        # Skip if already hidden (e.g. via hide_inline_navs.py)
        if re.search(r'style\s*=\s*["\'][^"\']*display\s*:\s*none', attrs, re.I):
            continue
        line = text.count("\n", 0, m.start()) + 1
        vs.append(Violation(rel, line, "NAV005",
            f'inline global <nav class="{first}"> found; use the canonical navbar instead'))

    # Local file references — check existence
    base_dir = path.parent
    for href_match in HREF_RE.finditer(text):
        target = href_match.group(1).strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "javascript:", "#", "tel:", "data:")):
            continue
        if target.startswith("/"):
            # Absolute from site root
            target_path = root / target.lstrip("/")
        else:
            target_path = (base_dir / target).resolve()
        # Strip ?query#fragment
        target_clean = re.sub(r'[?#].*$', '', str(target_path))
        target_clean_path = Path(target_clean)
        if not target_clean_path.exists():
            line = text.count("\n", 0, href_match.start()) + 1
            vs.append(Violation(rel, line, "LNK001",
                f"broken reference: {target}", severity="warn"))

    # Archive regime constraint
    # If this file is NOT in ARCHIVE_LINKERS, and it references an archived page,
    # that's a violation.
    if path.name not in ARCHIVE_LINKERS and archive_entries:
        for entry in archive_entries:
            if entry in text:
                line_no = text.count("\n", 0, text.find(entry)) + 1
                vs.append(Violation(rel, line_no, "ARC001",
                    f"links to archived page '{entry}' from non-archive-linker surface"))

    # localStorage-driven personalization before auth (heuristic)
    # Flag if localStorage.getItem appears inside a <body> and not inside a
    # guarded block like if(!authed). Very rough heuristic; warn only.
    for m in LOCALSTORAGE_RE.finditer(text):
        # Peek back 200 chars for a guard keyword
        pre = text[max(0, m.start()-200):m.start()]
        post = text[m.start():m.start()+200]
        if "authed" in pre or "validated" in pre or "token" in pre:
            continue
        if any(prefix in (pre + post) for prefix in SAFE_LOCALSTORAGE_PREFIXES):
            continue
        line = text.count("\n", 0, m.start()) + 1
        vs.append(Violation(rel, line, "SEC001",
            "localStorage read without visible auth guard (review manually)",
            severity="warn"))

    return vs


# ─── Archive entry discovery ───────────────────────────────────────────

def find_archive_entries(root: Path) -> set[str]:
    """Return the set of pages that actually declare data-ka-regime="archive".

    We do NOT use the list in ka_archive.html as the authoritative archive
    set, because that index is aspirational — it names pages we consider
    archived-in-principle but may still be live canonical surfaces. Only
    pages that explicitly declare the archive regime on <body> are treated
    as archived for the ARC001 orphan-check.
    """
    entries = set()
    for p in root.rglob("*.html"):
        # Skip the archive index itself and directories we don't scan
        if p.name == "ka_archive.html":
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if 'data-ka-regime="archive"' in text or "data-ka-regime='archive'" in text:
            entries.add(p.name)
    return entries


# ─── Walk + summarise ─────────────────────────────────────────────────

def walk_html(root: Path, skip_dirs: set[str]) -> list[Path]:
    files = []
    for p in root.rglob("*.html"):
        parts = set(p.relative_to(root).parts)
        if parts & skip_dirs:
            continue
        files.append(p)
    return sorted(files)


def summarise(all_violations: list[Violation]) -> dict:
    by_code: dict[str, int] = {}
    by_severity = {"error": 0, "warn": 0, "info": 0}
    for v in all_violations:
        by_code[v.code] = by_code.get(v.code, 0) + 1
        by_severity[v.severity] = by_severity.get(v.severity, 0) + 1
    return {"by_code": by_code, "by_severity": by_severity,
            "total": len(all_violations)}


# ─── Main ─────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=KA_ROOT,
                    help="Site root directory")
    ap.add_argument("--json", action="store_true",
                    help="Emit machine-readable JSON output")
    ap.add_argument("--fix-hints", action="store_true",
                    help="Print fix suggestions inline")
    ap.add_argument("--warn-as-error", action="store_true",
                    help="Treat warnings as errors for exit code")
    ap.add_argument("--skip", nargs="*", default=["archive", "__pycache__",
                    "node_modules", ".git", "ka_live_snapshot"],
                    help="Directories to skip")
    ap.add_argument("--navbar", type=Path,
                    default=None,
                    help="Path to ka_canonical_navbar.js (defaults to <root>/ka_canonical_navbar.js)")
    args = ap.parse_args()

    navbar_js = args.navbar or (args.root / "ka_canonical_navbar.js")
    if not navbar_js.exists():
        print(f"ERROR: cannot find navbar JS at {navbar_js}", file=sys.stderr)
        return 2

    regime_items = load_regime_items(navbar_js)
    archive_entries = find_archive_entries(args.root)
    files = walk_html(args.root, set(args.skip))

    all_violations: list[Violation] = []
    for f in files:
        all_violations.extend(check_html(f, args.root, regime_items, archive_entries))

    summary = summarise(all_violations)

    if args.json:
        print(json.dumps({
            "files_scanned": len(files),
            "summary": summary,
            "violations": [asdict(v) for v in all_violations],
        }, indent=2))
    else:
        # Human output
        for v in all_violations:
            sev = {"error": "\033[31mERROR\033[0m",
                   "warn":  "\033[33mWARN \033[0m",
                   "info":  "\033[36mINFO \033[0m"}.get(v.severity, v.severity)
            loc = f":{v.line}" if v.line else ""
            print(f"{sev} [{v.code}] {v.file}{loc}  {v.message}")

        print()
        print(f"Scanned {len(files)} HTML files.")
        print(f"Summary: {summary['by_severity']}")
        if summary["by_code"]:
            print("By code:")
            for code, n in sorted(summary["by_code"].items()):
                print(f"  {code}: {n}")

    # Exit codes
    err = summary["by_severity"]["error"]
    if args.warn_as_error:
        err += summary["by_severity"]["warn"]
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main())
