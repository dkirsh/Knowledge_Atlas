#!/usr/bin/env python3
"""Build a static search index for the Knowledge Atlas site.

Walks every .html file under the repo root (skipping the frozen
ka_live_snapshot/ mirror, build/dist/node_modules, and a few other
known-noisy directories), extracts:

  - <title>
  - h1..h3 headings
  - a plain-text excerpt of the body (first ~1500 chars after stripping
    script/style/svg blocks and HTML tags)
  - an "area" classifier (e.g. 160sp, track-overview, track-task,
    track-submission, evidence, contribute, global, admin)
  - a "track" classifier (track1, track2, track3, track4, none) for
    160sp track pages

…and writes search_index.json at the repo root for the client-side
search page (ka_search.html) to consume.

Stdlib only. Run:
    python3 scripts/build_search_index.py
"""
from __future__ import annotations

import html as html_mod
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

# Directories we never want to index.
EXCLUDE_DIRS = {
    "ka_live_snapshot",       # frozen historical mirror
    "node_modules",
    ".git",
    "build", "dist",
    "__pycache__",
    "venv", ".venv",
    "Patches_etc",            # operator scratch
    "Older Repos etc",
}

# Filename prefixes/patterns we never want to index.
EXCLUDE_FILES = {
    "ka_canonical_navbar.js",
    "ka_user_type.js",
}

OUTPUT_PATH = REPO_ROOT / "search_index.json"

# ---------------------------------------------------------------------------
# Regex extractors. We deliberately keep these simple and stdlib-only.
# ---------------------------------------------------------------------------
_TITLE_RE       = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_HEADING_RE     = re.compile(r"<h([1-3])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
_DROP_BLOCK_RE  = re.compile(r"<(script|style|svg|noscript)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_TAG_RE         = re.compile(r"<[^>]+>")
_WHITESPACE_RE  = re.compile(r"\s+")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _clean_text(s: str) -> str:
    """Decode HTML entities and collapse whitespace."""
    if not s:
        return ""
    s = html_mod.unescape(s)
    s = _WHITESPACE_RE.sub(" ", s)
    return s.strip()


def extract_page(html_text: str) -> dict:
    """Extract title, headings, excerpt from raw HTML."""
    # Strip comments, then script/style/svg blocks
    cleaned = _HTML_COMMENT_RE.sub(" ", html_text)
    cleaned = _DROP_BLOCK_RE.sub(" ", cleaned)

    # Title
    m = _TITLE_RE.search(cleaned)
    title = _clean_text(m.group(1)) if m else ""

    # Headings (h1..h3) in order
    headings: list[str] = []
    for hm in _HEADING_RE.finditer(cleaned):
        h = _clean_text(_TAG_RE.sub(" ", hm.group(2)))
        if h and h not in headings:
            headings.append(h)
        if len(headings) >= 30:
            break

    # Body excerpt
    body = _TAG_RE.sub(" ", cleaned)
    body = _clean_text(body)

    return {
        "title": title,
        "headings": headings,
        "excerpt": body[:1500],
        "full_len": len(body),
    }


# ---------------------------------------------------------------------------
# Area classifier — what bucket does this page belong in?
# ---------------------------------------------------------------------------
def classify(rel_path: Path) -> tuple[str, str]:
    """Return (area, track) for a page."""
    parts = rel_path.parts
    name  = rel_path.name

    # COGS 160 pages
    if parts and parts[0] == "160sp":
        # Track pages: t1_intro, t1_task1, t1_submissions, etc.
        m = re.match(r"t([1-4])_(intro|task[1-3]|submissions)\.html$", name)
        if m:
            track_num, kind = m.group(1), m.group(2)
            track = f"track{track_num}"
            if kind == "intro":           area = "track-overview"
            elif kind == "submissions":   area = "track-submission"
            else:                          area = "track-task"
            return area, track

        # Other 160sp pages (legacy assignment, hub pages, weeks, etc.)
        if "track1" in name or name.startswith("t1_"):
            return "160sp-other", "track1"
        if "track2" in name or name.startswith("t2_"):
            return "160sp-other", "track2"
        if "track3" in name or name.startswith("t3_"):
            return "160sp-other", "track3"
        if "track4" in name or name.startswith("t4_") or "gui" in name:
            return "160sp-other", "track4"
        if "schedule" in name or "syllabus" in name:
            return "160sp-syllabus", "none"
        return "160sp-other", "none"

    # Root-level Atlas pages
    if name.startswith("ka_"):
        if "evidence" in name or "claim" in name:
            return "evidence", "none"
        if "gap" in name:
            return "gaps", "none"
        if "topic" in name:
            return "topics", "none"
        if "article" in name:
            return "articles", "none"
        if "contribute" in name:
            return "contribute", "none"
        if "admin" in name or "approve" in name:
            return "admin", "none"
        if "sitemap" in name or "search" in name:
            return "site-utility", "none"
        if name == "ka_home.html":
            return "home", "none"
    return "other", "none"


# ---------------------------------------------------------------------------
# Crawler
# ---------------------------------------------------------------------------
def should_skip(p: Path) -> bool:
    if p.name in EXCLUDE_FILES:
        return True
    for part in p.parts:
        if part in EXCLUDE_DIRS:
            return True
    return False


def main() -> int:
    t0 = time.time()
    pages: list[dict] = []
    skipped = 0
    failed = 0

    for html_path in REPO_ROOT.rglob("*.html"):
        rel = html_path.relative_to(REPO_ROOT)
        if should_skip(rel):
            skipped += 1
            continue
        try:
            text = html_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            failed += 1
            continue
        info = extract_page(text)
        if not info["title"] and not info["headings"] and info["full_len"] < 50:
            # Skip empty/redirect pages with nothing to index
            skipped += 1
            continue
        area, track = classify(rel)
        rel_url = str(rel).replace("\\", "/")
        pages.append({
            "path": rel_url,
            "url":  rel_url,
            "title": info["title"] or rel.stem.replace("_", " ").replace("-", " "),
            "area":  area,
            "track": track,
            "headings": info["headings"],
            "excerpt":  info["excerpt"],
            "full_len": info["full_len"],
            "size_kb":  html_path.stat().st_size // 1024,
        })

    # Stable order: by area, then path
    pages.sort(key=lambda p: (p["area"], p["path"]))

    out = {
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "page_count": len(pages),
        "pages": pages,
    }
    OUTPUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"Indexed {len(pages)} pages")
    print(f"  skipped: {skipped}")
    print(f"  failed:  {failed}")
    print(f"  → {OUTPUT_PATH.relative_to(REPO_ROOT)}  "
          f"({OUTPUT_PATH.stat().st_size // 1024} KB)")
    print(f"  elapsed: {time.time() - t0:.2f}s")

    # Summary by area
    by_area: dict[str, int] = {}
    for p in pages:
        by_area[p["area"]] = by_area.get(p["area"], 0) + 1
    print("\nBy area:")
    for a, n in sorted(by_area.items(), key=lambda x: -x[1]):
        print(f"  {a:25s} {n:4d}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
