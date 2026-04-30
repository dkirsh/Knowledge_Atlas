#!/usr/bin/env python3
"""Build a static search index for the Article Eater research corpus.

Reads every PDF-*.md science-writer summary from the AE data directory,
extracts YAML frontmatter (title, authors, year, article_type) and the
body text, then writes research_index.json for the Knowledge Atlas
search page to consume alongside search_index.json.

This script can be:
  1. Run standalone:     python3 scripts/build_research_index.py
  2. Called by AE pipeline as a terminal post-hook after SC regeneration.

The --source flag specifies where the science_writer_articles directory is.
Default: looks for the AE recovery repo, then the active AE workspace.

Stdlib only.
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "research_index.json"

# Search order for default source directories
_CANDIDATE_SOURCES = [
    Path.home() / "REPOS" / "Article_Eater_PostQuinean_v1_recovery" / "data" / "science_writer_articles",
    Path.home() / "REPOS" / "Article_Eater_PostQuinean_v1" / "data" / "science_writer_articles",
]

MIN_WORDS = 80

# ---------------------------------------------------------------------------
# YAML frontmatter parser (stdlib only — no pyyaml dependency)
# ---------------------------------------------------------------------------
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (metadata_dict, body_text) from a markdown file with YAML frontmatter."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    raw = m.group(1)
    body = text[m.end():]
    meta = {}
    for line in raw.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        colon = line.find(":")
        if colon == -1:
            continue
        key = line[:colon].strip()
        val = line[colon + 1:].strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
            val = val[1:-1]
        meta[key] = val
    return meta, body


ARTICLE_TYPE_LABEL = {
    "empirical_research": "Empirical",
    "review": "Review",
    "meta_analysis": "Meta-analysis",
    "meta-analysis": "Meta-analysis",
    "theoretical": "Theoretical",
    "book_chapter": "Book chapter",
    "case_study": "Case study",
    "narrative_review": "Narrative review",
    "systematic_review": "Systematic review",
    "design_guideline": "Design guideline",
    "methodology": "Methodology",
}


def build_entry(md_path: Path) -> dict | None:
    """Parse a single PDF-XXXX.md and return a search index entry, or None."""
    try:
        text = md_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    meta, body = parse_frontmatter(text)
    body = body.strip()
    word_count = len(body.split())
    if word_count < MIN_WORDS:
        return None

    pdf_id = meta.get("pdf_id", md_path.stem)
    title = meta.get("title", "")
    if not title:
        hm = re.search(r"^#+\s+(.+)$", body, re.MULTILINE)
        if hm:
            title = hm.group(1).strip()
        else:
            title = pdf_id

    authors = meta.get("authors", "")
    year = meta.get("year", "")
    article_type = meta.get("article_type", "")
    type_label = ARTICLE_TYPE_LABEL.get(article_type,
        article_type.replace("_", " ").title() if article_type else "")

    excerpt = re.sub(r"\s+", " ", body)[:1200]

    headings = []
    for hm in re.finditer(r"^#{1,3}\s+(.+)$", body, re.MULTILINE):
        h = hm.group(1).strip()
        if h and h not in headings:
            headings.append(h)
        if len(headings) >= 15:
            break

    return {
        "path": f"research/{pdf_id}",
        "url": f"/ka/research/{pdf_id}",
        "title": title,
        "area": "research",
        "track": "none",
        "headings": headings,
        "excerpt": excerpt,
        "full_len": len(body),
        "size_kb": md_path.stat().st_size // 1024,
        "pdf_id": pdf_id,
        "authors": authors,
        "year": year,
        "article_type": type_label,
        "word_count": word_count,
        "_full_body": body,  # stripped before writing search index
    }


def main() -> int:
    t0 = time.time()

    source = None
    output = OUTPUT_PATH

    if "--source" in sys.argv:
        idx = sys.argv.index("--source")
        if idx + 1 < len(sys.argv):
            source = Path(sys.argv[idx + 1])
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output = Path(sys.argv[idx + 1])

    # Auto-detect source if not specified
    if source is None:
        for candidate in _CANDIDATE_SOURCES:
            if candidate.is_dir():
                source = candidate
                break

    if source is None or not source.is_dir():
        print(f"ERROR: Source directory not found.", file=sys.stderr)
        print(f"  Tried: {[str(c) for c in _CANDIDATE_SOURCES]}", file=sys.stderr)
        print(f"  Pass --source /path/to/science_writer_articles", file=sys.stderr)
        return 1

    md_files = sorted(source.glob("PDF-*.md"))
    if not md_files:
        print(f"ERROR: No PDF-*.md files found in {source}", file=sys.stderr)
        return 1

    entries = []
    skipped = 0
    for md in md_files:
        entry = build_entry(md)
        if entry:
            entries.append(entry)
        else:
            skipped += 1

    entries.sort(key=lambda e: e.get("pdf_id", ""))

    # --- Build the full-text companion file ---
    full_map = {}
    for e in entries:
        full_map[e["pdf_id"]] = {
            "title": e["title"],
            "authors": e.get("authors", ""),
            "year": e.get("year", ""),
            "article_type": e.get("article_type", ""),
            "text": e.pop("_full_body", ""),
        }

    full_output = output.parent / "research_full.json"
    full_out = {
        "version": "1.0",
        "schema": "ka.research_full.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "paper_count": len(full_map),
        "papers": full_map,
    }
    full_output.write_text(json.dumps(full_out, ensure_ascii=False, indent=1), encoding="utf-8")
    full_kb = full_output.stat().st_size // 1024

    # --- Build the search index (excerpts only) ---
    # Strip any remaining _full_body keys
    for e in entries:
        e.pop("_full_body", None)

    out = {
        "version": "1.0",
        "schema": "ka.research_index.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_dir": str(source),
        "paper_count": len(entries),
        "papers": entries,
    }

    output.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    elapsed = time.time() - t0
    total_kb = output.stat().st_size // 1024
    print(f"Built research index: {len(entries)} papers")
    print(f"  source:  {source}")
    print(f"  skipped: {skipped} (stubs < {MIN_WORDS} words)")
    print(f"  index:   {output}  ({total_kb} KB)")
    print(f"  full:    {full_output}  ({full_kb} KB)")
    print(f"  elapsed: {elapsed:.2f}s")

    by_type: dict[str, int] = {}
    for e in entries:
        t = e.get("article_type") or "unknown"
        by_type[t] = by_type.get(t, 0) + 1
    print("\nBy article type:")
    for t, n in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {t:25s} {n:4d}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
