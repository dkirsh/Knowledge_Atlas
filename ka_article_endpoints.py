#!/usr/bin/env python3
"""
Knowledge Atlas — Article Submission Endpoints
===============================================
Extends the KA auth server with article intake, validation, duplicate
detection, staging, and instructor review.

This module is imported by ka_auth_server.py and registered as a FastAPI
APIRouter.  It adds:

    POST /api/articles/submit          – upload PDFs and/or citations
    GET  /api/articles/status/{id}     – check article status
    GET  /api/articles/my-submissions  – student's own submissions
    GET  /api/articles/pending-review  – instructor: articles awaiting review
    POST /api/articles/{id}/review     – instructor: accept or reject
    POST /api/articles/check-duplicate – real-time duplicate probe
    GET  /api/articles/stats           – corpus + personal statistics

See docs/ARTICLE_SUBMISSION_MODULE_SPEC_2026-03-30.md for the full contract.
"""

import hashlib, json, os, re, secrets, shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# ════════════════════════════════════════════════
# CONFIG — overridable via environment variables
# ════════════════════════════════════════════════
STORAGE_ROOT       = Path(os.environ.get("KA_STORAGE_ROOT", Path(__file__).parent / "data" / "storage"))
QUARANTINE_DIR     = Path(os.environ.get("KA_QUARANTINE_DIR", STORAGE_ROOT / "quarantine"))
PDF_COLLECTION_DIR = Path(os.environ.get("KA_PDF_COLLECTION_DIR", STORAGE_ROOT / "pdf_collection"))
REJECTED_DIR       = Path(os.environ.get("KA_REJECTED_DIR", STORAGE_ROOT / "rejected"))

MAX_FILE_SIZE_BYTES   = int(os.environ.get("KA_MAX_FILE_SIZE_MB", 100)) * 1024 * 1024
MAX_BATCH_SIZE_BYTES  = int(os.environ.get("KA_MAX_BATCH_SIZE_MB", 500)) * 1024 * 1024
MAX_ANON_PER_HOUR     = int(os.environ.get("KA_MAX_ANON_SUBMISSIONS_PER_HOUR", 10))
MAX_AUTH_PER_HOUR     = int(os.environ.get("KA_MAX_AUTH_SUBMISSIONS_PER_HOUR", 50))

# Ensure storage directories exist
for d in (QUARANTINE_DIR, PDF_COLLECTION_DIR, REJECTED_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ════════════════════════════════════════════════
# ROUTER
# ════════════════════════════════════════════════
router = APIRouter(prefix="/api/articles", tags=["articles"])

# We need access to the auth server's DB and user helpers.
# These are injected by the main server when it includes this router.
_get_db = None
_get_current_user_optional = None
_get_current_user = None
_require_instructor = None


def configure(get_db, get_current_user, get_current_user_optional, require_instructor):
    """Called by ka_auth_server.py to inject shared dependencies."""
    global _get_db, _get_current_user, _get_current_user_optional, _require_instructor
    _get_db = get_db
    _get_current_user = get_current_user
    _get_current_user_optional = get_current_user_optional
    _require_instructor = require_instructor


def _init_article_tables():
    """Create article-related tables if they don't exist."""
    db = _get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS articles (
        article_id          TEXT PRIMARY KEY,
        submission_id       TEXT NOT NULL,
        submitter_id        TEXT,
        submitter_type      TEXT NOT NULL DEFAULT 'anonymous',
        track               TEXT,
        input_mode          TEXT NOT NULL,

        doi                 TEXT,
        title               TEXT,
        authors             TEXT,
        year                INTEGER,
        journal             TEXT,
        abstract            TEXT,
        citation_raw        TEXT,

        pdf_filename        TEXT,
        pdf_hash_sha256     TEXT,
        pdf_size_bytes      INTEGER,
        quarantine_path     TEXT,
        promoted_path       TEXT,

        status              TEXT NOT NULL DEFAULT 'received',
        duplicate_of        TEXT,
        validation_notes    TEXT,
        relevance_score     REAL,
        review_notes        TEXT,

        assigned_question_id TEXT,
        topic_tags          TEXT,

        source_surface      TEXT DEFAULT 'ka_contribute',
        course_context      TEXT,
        submitter_notes     TEXT,

        created_at          TEXT NOT NULL,
        validated_at        TEXT,
        staged_at           TEXT,
        reviewed_at         TEXT,
        promoted_at         TEXT,
        rejected_at         TEXT,

        metadata_confidence TEXT DEFAULT 'low'
    );

    CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
    CREATE INDEX IF NOT EXISTS idx_articles_submitter ON articles(submitter_id);
    CREATE INDEX IF NOT EXISTS idx_articles_doi ON articles(doi);
    CREATE INDEX IF NOT EXISTS idx_articles_hash ON articles(pdf_hash_sha256);
    CREATE INDEX IF NOT EXISTS idx_articles_submission ON articles(submission_id);

    CREATE TABLE IF NOT EXISTS submission_batches (
        submission_id   TEXT PRIMARY KEY,
        submitter_id    TEXT,
        submitter_type  TEXT NOT NULL DEFAULT 'anonymous',
        input_mode      TEXT NOT NULL,
        item_count      INTEGER NOT NULL DEFAULT 0,
        source_surface  TEXT,
        created_at      TEXT NOT NULL,
        completed_at    TEXT
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        log_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        article_id  TEXT NOT NULL,
        action      TEXT NOT NULL,
        old_status  TEXT,
        new_status  TEXT,
        actor_id    TEXT,
        actor_type  TEXT DEFAULT 'system',
        details     TEXT,
        created_at  TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_audit_article ON audit_log(article_id);
    CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action);
    """)
    db.commit()
    db.close()


# ════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════

def _next_id(prefix: str, table: str, id_col: str) -> str:
    """Generate the next sequential ID like KA-ART-000001."""
    db = _get_db()
    row = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    db.close()
    seq = (row[0] or 0) + 1
    return f"{prefix}{seq:06d}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _validate_pdf_bytes(data: bytes, filename: str) -> dict:
    """Check that the file is a valid PDF. Returns validation dict."""
    notes = {"filename": filename, "size": len(data)}

    # Magic bytes check
    if not data[:5] == b"%PDF-":
        notes["magic_bytes"] = "FAIL"
        notes["rejection_reason"] = "Not a PDF file (invalid magic bytes)"
        return notes
    notes["magic_bytes"] = "PASS"

    # Size check
    if len(data) > MAX_FILE_SIZE_BYTES:
        notes["size_check"] = "FAIL"
        notes["rejection_reason"] = f"File too large ({len(data)} bytes > {MAX_FILE_SIZE_BYTES} limit)"
        return notes
    notes["size_check"] = "PASS"

    # Basic structure check (PDF should end with %%EOF somewhere near the end)
    tail = data[-1024:]
    if b"%%EOF" not in tail:
        notes["structure_check"] = "WARN"
        notes["structure_note"] = "No %%EOF marker in last 1024 bytes (possibly truncated)"
    else:
        notes["structure_check"] = "PASS"

    notes["valid"] = True
    return notes


def _extract_doi_from_pdf(data: bytes) -> Optional[str]:
    """Try to extract a DOI from the first ~5000 bytes of a PDF."""
    try:
        text = data[:5000].decode("latin-1", errors="ignore")
        doi_pattern = r'10\.\d{4,9}/[^\s]+'
        match = re.search(doi_pattern, text)
        if match:
            return match.group(0).rstrip(".")
    except Exception:
        pass
    return None


def _parse_citation_line(line: str) -> dict:
    """
    Best-effort extraction of authors, year, and title from a citation string.
    Handles common APA-ish formats:
      - 'Boubekri, M., Cheung, I. N., & Reid, K. J. (2014). Impact of windows...'
      - 'Boubekri et al. (2014). Impact of windows and daylight exposure...'
      - 'Impact of windows and daylight exposure on sleep. Boubekri 2014'
      - Just a title with no structured author/year

    Returns dict with keys: authors, year, title (any may be empty string).
    """
    result = {"authors": "", "year": "", "title": ""}

    # Extract year (4-digit number in parens or standalone)
    year_match = re.search(r'\((\d{4})\)', line) or re.search(r'\b(19|20)\d{2}\b', line)
    if year_match:
        result["year"] = year_match.group(1) if '(' in year_match.group(0) else year_match.group(0)

    # Try APA pattern: Authors (Year). Title. Journal...
    # Pattern: everything before (YYYY) is authors, everything after is title+journal
    apa_match = re.match(r'^(.+?)\s*\(\d{4}\)\.\s*(.+)', line)
    if apa_match:
        result["authors"] = apa_match.group(1).strip().rstrip(',').rstrip('.')
        remainder = apa_match.group(2)
        # Title is typically the first sentence (ends at period followed by space+capital or italic marker)
        title_match = re.match(r'^(.+?)\.\s+[A-Z]', remainder)
        if title_match:
            result["title"] = title_match.group(1).strip()
        else:
            # Take everything up to the first period as title
            result["title"] = remainder.split('.')[0].strip()
        return result

    # Try: Authors. (Year). Title. ...
    apa_match2 = re.match(r'^(.+?)\.\s*\(\d{4}\)\.\s*(.+)', line)
    if apa_match2:
        result["authors"] = apa_match2.group(1).strip()
        remainder = apa_match2.group(2)
        title_match = re.match(r'^(.+?)\.\s+[A-Z]', remainder)
        result["title"] = title_match.group(1).strip() if title_match else remainder.split('.')[0].strip()
        return result

    # No structured format detected — treat the whole line as a title
    # Strip any DOI from the end
    cleaned = re.sub(r'\s*https?://doi\.org/\S+', '', line)
    cleaned = re.sub(r'\s*10\.\d{4,9}/\S+', '', cleaned)
    result["title"] = cleaned.strip().rstrip('.')
    return result


def _normalize_text(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    t = re.sub(r'[^\w\s]', ' ', (text or '').lower())
    return re.sub(r'\s+', ' ', t).strip()


def _tokenize(text: str) -> list:
    """Split normalized text into word tokens."""
    return _normalize_text(text).split()


def _word_edit_distance(a_tokens: list, b_tokens: list) -> int:
    """
    Compute word-level Levenshtein distance between two token lists.
    Each operation (insert, delete, substitute) costs 1 word.
    """
    m, n = len(a_tokens), len(b_tokens)
    # Optimisation: if lengths differ by more than allowed threshold, skip
    if abs(m - n) > max(2, min(m, n) // 3):
        return max(m, n)
    # Standard DP
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        curr = [i] + [0] * n
        for j in range(1, n + 1):
            cost = 0 if a_tokens[i - 1] == b_tokens[j - 1] else 1
            curr[j] = min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost)
        prev = curr
    return prev[n]


def _titles_match(title_a: str, title_b: str, max_word_distance: int = 1) -> bool:
    """
    True if two titles are within max_word_distance words of each other.
    Also returns True for exact containment (one is a substring of the other
    after normalization), which catches truncation cases.
    """
    norm_a = _normalize_text(title_a)
    norm_b = _normalize_text(title_b)
    if not norm_a or not norm_b:
        return False
    # Exact match after normalization
    if norm_a == norm_b:
        return True
    # Containment (handles truncated titles)
    if norm_a in norm_b or norm_b in norm_a:
        return True
    # Word-level edit distance
    toks_a = norm_a.split()
    toks_b = norm_b.split()
    # Both must have at least 3 words to be meaningful for fuzzy matching
    if len(toks_a) < 3 or len(toks_b) < 3:
        return False
    dist = _word_edit_distance(toks_a, toks_b)
    return dist <= max_word_distance


def _authors_match(authors_a: str, authors_b: str, max_word_distance: int = 1) -> bool:
    """
    True if two author strings are within max_word_distance words of each other.
    Handles common APA variations:
      - 'Boubekri, M., Cheung, I. N.' vs 'Boubekri, M., Cheung, I.N.'
      - 'Boubekri et al.' vs 'Boubekri, M., Cheung, I. N., Reid, K. J.'
    Also matches if the first author's last name is identical (covers
    'Boubekri et al.' matching 'Boubekri, Cheung, & Reid').
    """
    norm_a = _normalize_text(authors_a)
    norm_b = _normalize_text(authors_b)
    if not norm_a or not norm_b:
        return False
    if norm_a == norm_b:
        return True
    # First-author last name check: extract the first word (last name in APA)
    first_a = norm_a.split()[0] if norm_a else ''
    first_b = norm_b.split()[0] if norm_b else ''
    # If both have 'et al' and share first author, that's a match
    if first_a == first_b and ('et al' in norm_a or 'et al' in norm_b):
        return True
    # Full word-level edit distance
    toks_a = norm_a.split()
    toks_b = norm_b.split()
    dist = _word_edit_distance(toks_a, toks_b)
    return dist <= max_word_distance


def _check_duplicate(pdf_hash: Optional[str] = None, doi: Optional[str] = None,
                     title: Optional[str] = None, authors: Optional[str] = None) -> dict:
    """
    Check for duplicates using a cascade of increasingly fuzzy methods:
      1. Exact PDF hash match (definitive)
      2. Exact DOI match (definitive)
      3. Fuzzy title match (≤1 word edit distance) — flags as duplicate
      4. Fuzzy title+authors match — if title alone is ambiguous, author
         agreement strengthens the match

    Many APA citations lack DOIs, so title+author fuzzy matching is essential.
    The word-level edit distance tolerates one word difference (e.g., a subtitle
    variation, a dropped article, or a minor wording change between preprint
    and published version).
    """
    db = _get_db()
    result = {"is_duplicate": False, "matches": [], "check_type": []}

    # ── 1. Hash check (exact, definitive)
    if pdf_hash:
        result["check_type"].append("hash")
        row = db.execute(
            "SELECT article_id, title, authors, doi, status FROM articles WHERE pdf_hash_sha256=? LIMIT 1",
            (pdf_hash,)).fetchone()
        if row:
            result["is_duplicate"] = True
            result["matches"].append({
                "article_id": row["article_id"],
                "title": row["title"],
                "authors": row["authors"],
                "doi": row["doi"],
                "match_type": "exact_hash",
                "confidence": "definitive"
            })
            db.close()
            return result

    # ── 2. DOI check (exact, definitive)
    if doi:
        result["check_type"].append("doi")
        clean_doi = doi.strip().lower()
        row = db.execute(
            "SELECT article_id, title, authors, doi, status FROM articles WHERE LOWER(doi)=? LIMIT 1",
            (clean_doi,)).fetchone()
        if row:
            result["is_duplicate"] = True
            result["matches"].append({
                "article_id": row["article_id"],
                "title": row["title"],
                "authors": row["authors"],
                "doi": row["doi"],
                "match_type": "exact_doi",
                "confidence": "definitive"
            })
            db.close()
            return result

    # ── 3. Fuzzy title (+ optional author) matching
    if title and len(title.strip()) > 10:
        result["check_type"].append("title_fuzzy")
        rows = db.execute(
            "SELECT article_id, title, authors, doi, status FROM articles WHERE title IS NOT NULL"
        ).fetchall()

        for row in rows:
            existing_title = row["title"] or ""
            if not existing_title:
                continue

            if _titles_match(title, existing_title, max_word_distance=1):
                # Title matches within 1 word — check if authors also match
                match_type = "title_fuzzy_1word"
                confidence = "high"

                existing_authors = row["authors"] or ""
                # If we have authors for both, author agreement raises confidence
                if authors and existing_authors:
                    if _authors_match(authors, existing_authors, max_word_distance=1):
                        match_type = "title_and_authors_fuzzy"
                        confidence = "very_high"
                    else:
                        # Title matches but authors don't — possible different paper
                        # with a similar title. Still flag but lower confidence.
                        match_type = "title_fuzzy_authors_differ"
                        confidence = "medium"

                result["is_duplicate"] = True
                result["matches"].append({
                    "article_id": row["article_id"],
                    "title": row["title"],
                    "authors": row["authors"],
                    "doi": row["doi"],
                    "match_type": match_type,
                    "confidence": confidence
                })
                break  # One match is enough

    # ── 4. Author-only check: if title is very short or missing but authors are provided,
    #    we don't flag as duplicate (too many false positives). Author matching is only
    #    a strengthener for title matches, not standalone.

    db.close()
    return result


def _sanitize_filename(name: str) -> str:
    """Strip to alphanumeric + hyphens."""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', Path(name).stem)[:80]


def _write_audit(article_id: str, action: str, old_status: str = None,
                 new_status: str = None, actor_id: str = None,
                 actor_type: str = "system", details: dict = None):
    db = _get_db()
    db.execute(
        "INSERT INTO audit_log (article_id, action, old_status, new_status, actor_id, actor_type, details, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (article_id, action, old_status, new_status, actor_id, actor_type,
         json.dumps(details) if details else None, _now()))
    db.commit()
    db.close()


def _get_optional_user(request: Request) -> Optional[dict]:
    """Extract user from Bearer token if present, otherwise return None."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        from jose import jwt, JWTError
        # Import secret from main module
        import ka_auth_server as main
        payload = jwt.decode(auth[7:], main.SECRET_KEY, algorithms=[main.ALGORITHM])
        if payload.get("type") != "access":
            return None
        db = _get_db()
        row = db.execute("SELECT * FROM users WHERE user_id=?", (payload["sub"],)).fetchone()
        db.close()
        if row and row["status"] == "approved":
            return dict(row)
    except Exception:
        pass
    return None


# ════════════════════════════════════════════════
# ENDPOINTS
# ════════════════════════════════════════════════

@router.post("/submit")
async def submit_articles(
    request: Request,
    files: List[UploadFile] = File(default=[]),
    citations: str = Form(default=""),
    question_id: str = Form(default=""),
    topic_tags: str = Form(default=""),
    notes: str = Form(default=""),
    source_surface: str = Form(default="ka_contribute"),
):
    """
    Submit one or more articles (PDFs and/or citation text).
    Auth is optional — anonymous submissions are allowed.
    """
    user = _get_optional_user(request)

    # Must provide at least something
    if not files and not citations.strip():
        raise HTTPException(400, "Provide at least one PDF file or citation text")

    # Check batch size
    total_size = 0
    for f in files:
        content = await f.read()
        total_size += len(content)
        await f.seek(0)  # reset for later read
    if total_size > MAX_BATCH_SIZE_BYTES:
        raise HTTPException(
            413, f"Total batch size ({total_size} bytes) exceeds limit ({MAX_BATCH_SIZE_BYTES} bytes)")

    # Create submission batch
    submission_id = _next_id("KA-IN-", "submission_batches", "submission_id")
    now = _now()
    submitter_id = user["user_id"] if user else None
    submitter_type = user["role"] if user else "anonymous"
    track = user.get("track") if user else None

    db = _get_db()
    db.execute(
        "INSERT INTO submission_batches VALUES (?,?,?,?,?,?,?,?)",
        (submission_id, submitter_id, submitter_type, "mixed", 0, source_surface, now, None))
    db.commit()
    db.close()

    items = []

    # ── Process PDF files
    for f in files:
        content = await f.read()
        article_id = _next_id("KA-ART-", "articles", "article_id")
        pdf_hash = _compute_sha256(content)
        filename = f.filename or "unknown.pdf"

        # Validate
        validation = _validate_pdf_bytes(content, filename)

        if not validation.get("valid"):
            # Rejected at validation
            db = _get_db()
            db.execute("""INSERT INTO articles
                (article_id, submission_id, submitter_id, submitter_type, track, input_mode,
                 pdf_filename, pdf_hash_sha256, pdf_size_bytes,
                 status, validation_notes,
                 assigned_question_id, topic_tags,
                 source_surface, course_context, submitter_notes,
                 created_at, validated_at, rejected_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (article_id, submission_id, submitter_id, submitter_type, track, "pdf_single",
                 filename, pdf_hash, len(content),
                 "rejected_bad_file", json.dumps(validation),
                 question_id or None, topic_tags or None,
                 source_surface, "COGS160-SP26", notes or None,
                 now, now, now))
            db.commit()
            db.close()
            _write_audit(article_id, "rejected_bad_file", "received", "rejected_bad_file",
                         actor_type="system", details=validation)
            items.append({
                "article_id": article_id,
                "input_mode": "pdf_single",
                "filename": filename,
                "validation_status": "invalid",
                "duplicate_status": "not_checked",
                "metadata": {},
                "status": "rejected_bad_file",
                "reason": validation.get("rejection_reason", "Validation failed")
            })
            continue

        # Duplicate check
        extracted_doi = _extract_doi_from_pdf(content)
        dup_result = _check_duplicate(pdf_hash=pdf_hash, doi=extracted_doi)

        if dup_result["is_duplicate"]:
            dup_match = dup_result["matches"][0] if dup_result["matches"] else {}
            db = _get_db()
            db.execute("""INSERT INTO articles
                (article_id, submission_id, submitter_id, submitter_type, track, input_mode,
                 doi, pdf_filename, pdf_hash_sha256, pdf_size_bytes,
                 status, duplicate_of, validation_notes,
                 assigned_question_id, topic_tags,
                 source_surface, course_context, submitter_notes,
                 created_at, validated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (article_id, submission_id, submitter_id, submitter_type, track, "pdf_single",
                 extracted_doi, filename, pdf_hash, len(content),
                 "duplicate_existing", dup_match.get("article_id"),
                 json.dumps(validation),
                 question_id or None, topic_tags or None,
                 source_surface, "COGS160-SP26", notes or None,
                 now, now))
            db.commit()
            db.close()
            _write_audit(article_id, "duplicate_detected", "received", "duplicate_existing",
                         details=dup_result)
            items.append({
                "article_id": article_id,
                "input_mode": "pdf_single",
                "filename": filename,
                "validation_status": "valid",
                "duplicate_status": "duplicate",
                "duplicate_of": dup_match.get("article_id"),
                "metadata": {"doi": extracted_doi},
                "status": "duplicate_existing"
            })
            continue

        # Save to quarantine
        month_dir = QUARANTINE_DIR / datetime.now().strftime("%Y-%m")
        month_dir.mkdir(parents=True, exist_ok=True)
        quarantine_path = month_dir / f"{article_id}.pdf"
        quarantine_path.write_bytes(content)

        # Determine metadata confidence
        confidence = "low"
        if extracted_doi:
            confidence = "medium"

        # Insert article record
        db = _get_db()
        db.execute("""INSERT INTO articles
            (article_id, submission_id, submitter_id, submitter_type, track, input_mode,
             doi, pdf_filename, pdf_hash_sha256, pdf_size_bytes, quarantine_path,
             status, validation_notes,
             assigned_question_id, topic_tags,
             source_surface, course_context, submitter_notes,
             created_at, validated_at, staged_at, metadata_confidence)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (article_id, submission_id, submitter_id, submitter_type, track, "pdf_single",
             extracted_doi, filename, pdf_hash, len(content), str(quarantine_path),
             "staged_pending_review", json.dumps(validation),
             question_id or None, topic_tags or None,
             source_surface, "COGS160-SP26", notes or None,
             now, now, now, confidence))
        db.commit()
        db.close()

        _write_audit(article_id, "staged", "received", "staged_pending_review",
                     actor_id=submitter_id, actor_type=submitter_type)

        items.append({
            "article_id": article_id,
            "input_mode": "pdf_single",
            "filename": filename,
            "validation_status": "valid",
            "duplicate_status": "not_duplicate",
            "metadata": {"doi": extracted_doi, "confidence": confidence},
            "status": "staged_pending_review"
        })

    # ── Process citation text
    if citations.strip():
        for line in citations.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            article_id = _next_id("KA-ART-", "articles", "article_id")

            # Parse citation to extract structured fields
            parsed = _parse_citation_line(line)

            # Try to extract DOI from citation
            doi_match = re.search(r'10\.\d{4,9}/[^\s]+', line)
            extracted_doi = doi_match.group(0).rstrip(".") if doi_match else None

            # Use parsed title for dedup (falls back to raw line if parsing fails)
            dedup_title = parsed["title"] if parsed["title"] else line[:200]
            dedup_authors = parsed["authors"]

            # Duplicate check — fuzzy on title and authors (≤1 word edit distance)
            dup_result = _check_duplicate(doi=extracted_doi, title=dedup_title, authors=dedup_authors)

            status = "duplicate_existing" if dup_result["is_duplicate"] else "staged_pending_review"
            dup_of = dup_result["matches"][0]["article_id"] if dup_result["is_duplicate"] and dup_result["matches"] else None

            db = _get_db()
            db.execute("""INSERT INTO articles
                (article_id, submission_id, submitter_id, submitter_type, track, input_mode,
                 doi, title, authors, year, citation_raw,
                 status, duplicate_of,
                 assigned_question_id, topic_tags,
                 source_surface, course_context, submitter_notes,
                 created_at, staged_at, metadata_confidence)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (article_id, submission_id, submitter_id, submitter_type, track, "citation_text",
                 extracted_doi,
                 parsed["title"] or None,
                 parsed["authors"] or None,
                 int(parsed["year"]) if parsed["year"] else None,
                 line,
                 status, dup_of,
                 question_id or None, topic_tags or None,
                 source_surface, "COGS160-SP26", notes or None,
                 now, now if status == "staged_pending_review" else None,
                 "high" if extracted_doi and parsed["title"] and parsed["authors"]
                 else "medium" if extracted_doi or (parsed["title"] and parsed["authors"])
                 else "low"))
            db.commit()
            db.close()

            _write_audit(article_id,
                         "duplicate_detected" if dup_result["is_duplicate"] else "staged",
                         "received", status,
                         actor_id=submitter_id, actor_type=submitter_type)

            items.append({
                "article_id": article_id,
                "input_mode": "citation_text",
                "citation": line[:200],
                "validation_status": "accepted",
                "duplicate_status": "duplicate" if dup_result["is_duplicate"] else "not_duplicate",
                "metadata": {"doi": extracted_doi},
                "status": status
            })

    # Update batch count
    db = _get_db()
    db.execute("UPDATE submission_batches SET item_count=?, completed_at=? WHERE submission_id=?",
               (len(items), _now(), submission_id))
    db.commit()
    db.close()

    staged = sum(1 for i in items if i["status"] == "staged_pending_review")
    dups = sum(1 for i in items if i["status"] == "duplicate_existing")
    rejected = sum(1 for i in items if "rejected" in i["status"])

    return {
        "submission_id": submission_id,
        "items": items,
        "summary": {
            "total": len(items),
            "staged": staged,
            "duplicates": dups,
            "rejected": rejected
        }
    }


@router.get("/status/{article_id}")
async def article_status(article_id: str):
    """Check the current status of a submitted article."""
    db = _get_db()
    row = db.execute(
        "SELECT article_id, status, title, doi, created_at, duplicate_of, metadata_confidence FROM articles WHERE article_id=?",
        (article_id,)).fetchone()
    db.close()
    if not row:
        raise HTTPException(404, "Article not found")
    return dict(row)


@router.get("/my-submissions")
async def my_submissions(
    request: Request,
    status_filter: str = "",
    limit: int = 50,
    offset: int = 0,
):
    """List all articles submitted by the authenticated user."""
    user = _get_optional_user(request)
    if not user:
        raise HTTPException(401, "Authentication required to view submissions")

    db = _get_db()
    base_query = "FROM articles WHERE submitter_id=?"
    params = [user["user_id"]]

    if status_filter:
        base_query += " AND status=?"
        params.append(status_filter)

    total = db.execute(f"SELECT COUNT(*) {base_query}", params).fetchone()[0]
    rows = db.execute(
        f"SELECT article_id, submission_id, input_mode, doi, title, pdf_filename, status, created_at, metadata_confidence {base_query} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [limit, offset]).fetchall()

    # Counts by status
    counts_rows = db.execute(
        "SELECT status, COUNT(*) as cnt FROM articles WHERE submitter_id=? GROUP BY status",
        (user["user_id"],)).fetchall()
    db.close()

    counts = {r["status"]: r["cnt"] for r in counts_rows}

    return {
        "submissions": [dict(r) for r in rows],
        "counts": {
            "total": total,
            "staged": counts.get("staged_pending_review", 0),
            "accepted": counts.get("accepted_for_extraction", 0),
            "rejected": counts.get("rejected_irrelevant", 0) + counts.get("rejected_bad_file", 0),
            "duplicate": counts.get("duplicate_existing", 0)
        }
    }


@router.get("/pending-review")
async def pending_review(
    request: Request,
    limit: int = 50,
    offset: int = 0,
):
    """List articles awaiting instructor review."""
    user = _get_optional_user(request)
    if not user or user["role"] not in ("instructor", "admin"):
        raise HTTPException(403, "Instructor access required")

    db = _get_db()
    rows = db.execute(
        """SELECT a.*, u.email as submitter_email, u.first_name, u.last_name
           FROM articles a
           LEFT JOIN users u ON a.submitter_id = u.user_id
           WHERE a.status = 'staged_pending_review'
           ORDER BY a.created_at DESC LIMIT ? OFFSET ?""",
        (limit, offset)).fetchall()
    total = db.execute(
        "SELECT COUNT(*) FROM articles WHERE status='staged_pending_review'").fetchone()[0]
    db.close()
    return {"items": [dict(r) for r in rows], "total": total}


class ReviewRequest(BaseModel):
    decision: str  # "accept" or "reject"
    reason: str = ""
    topic_override: str = ""
    notes: str = ""


@router.post("/{article_id}/review")
async def review_article(article_id: str, req: ReviewRequest, request: Request):
    """Accept or reject a staged article (instructor only)."""
    user = _get_optional_user(request)
    if not user or user["role"] not in ("instructor", "admin"):
        raise HTTPException(403, "Instructor access required")

    if req.decision not in ("accept", "reject"):
        raise HTTPException(400, "Decision must be 'accept' or 'reject'")

    db = _get_db()
    row = db.execute("SELECT * FROM articles WHERE article_id=?", (article_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, "Article not found")

    if row["status"] != "staged_pending_review":
        db.close()
        raise HTTPException(400, f"Article is not pending review (current status: {row['status']})")

    now = _now()

    if req.decision == "accept":
        # Determine topic folder
        topic_slug = "general"
        if req.topic_override:
            topic_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', req.topic_override.lower())
        elif row["topic_tags"]:
            try:
                tags = json.loads(row["topic_tags"])
                if tags:
                    topic_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', tags[0].lower())
            except (json.JSONDecodeError, IndexError):
                pass

        # Move PDF from quarantine to collection
        promoted_path = None
        if row["quarantine_path"] and Path(row["quarantine_path"]).exists():
            dest_dir = PDF_COLLECTION_DIR / topic_slug
            dest_dir.mkdir(parents=True, exist_ok=True)
            safe_title = _sanitize_filename(row["title"] or row["pdf_filename"] or "untitled")
            dest_name = f"{article_id}_{safe_title}.pdf"
            promoted_path = dest_dir / dest_name
            shutil.move(row["quarantine_path"], str(promoted_path))

            # Write sidecar JSON for extraction pipeline
            sidecar = {
                "article_id": article_id,
                "doi": row["doi"],
                "title": row["title"],
                "authors": json.loads(row["authors"]) if row["authors"] else [],
                "year": row["year"],
                "journal": row["journal"],
                "abstract": row["abstract"],
                "promoted_at": now,
                "source": "ka_article_submission",
                "submitter_id": row["submitter_id"],
                "pdf_hash_sha256": row["pdf_hash_sha256"]
            }
            sidecar_path = promoted_path.with_suffix(".json")
            sidecar_path.write_text(json.dumps(sidecar, indent=2))

        db.execute("""UPDATE articles SET
            status='accepted_for_extraction', promoted_path=?,
            reviewed_at=?, promoted_at=?, review_notes=?
            WHERE article_id=?""",
            (str(promoted_path) if promoted_path else None, now, now, req.notes, article_id))
        db.commit()
        db.close()

        _write_audit(article_id, "accepted", "staged_pending_review", "accepted_for_extraction",
                     actor_id=user["user_id"], actor_type="instructor",
                     details={"topic": topic_slug, "promoted_path": str(promoted_path) if promoted_path else None})

        return {"article_id": article_id, "status": "accepted_for_extraction",
                "promoted_path": str(promoted_path) if promoted_path else None}

    else:  # reject
        # Delete PDF from quarantine
        if row["quarantine_path"] and Path(row["quarantine_path"]).exists():
            Path(row["quarantine_path"]).unlink()

        # Write rejection stub
        reject_dir = REJECTED_DIR / datetime.now().strftime("%Y-%m")
        reject_dir.mkdir(parents=True, exist_ok=True)
        stub = {
            "article_id": article_id,
            "title": row["title"],
            "doi": row["doi"],
            "submitter_id": row["submitter_id"],
            "rejection_reason": req.reason,
            "rejected_at": now,
            "reviewer": user["user_id"]
        }
        (reject_dir / f"{article_id}.json").write_text(json.dumps(stub, indent=2))

        new_status = "rejected_irrelevant" if req.reason else "rejected_irrelevant"
        db.execute("""UPDATE articles SET
            status=?, rejected_at=?, review_notes=?, quarantine_path=NULL
            WHERE article_id=?""",
            (new_status, now, req.notes or req.reason, article_id))
        db.commit()
        db.close()

        _write_audit(article_id, "rejected", "staged_pending_review", new_status,
                     actor_id=user["user_id"], actor_type="instructor",
                     details={"reason": req.reason})

        return {"article_id": article_id, "status": new_status}


class DuplicateCheckRequest(BaseModel):
    doi: str = ""
    title: str = ""
    authors: str = ""
    pdf_hash: str = ""


@router.post("/check-duplicate")
async def check_duplicate(req: DuplicateCheckRequest):
    """Quick duplicate check without full submission. Fuzzy-matches title
    and authors within 1 word edit distance to catch APA citations without DOIs."""
    if not req.doi and not req.title and not req.pdf_hash:
        raise HTTPException(400, "Provide at least one of: doi, title, pdf_hash")
    result = _check_duplicate(
        pdf_hash=req.pdf_hash or None, doi=req.doi or None,
        title=req.title or None, authors=req.authors or None)
    return result


@router.get("/stats")
async def article_stats(request: Request):
    """Corpus and personal statistics."""
    user = _get_optional_user(request)
    db = _get_db()

    # Corpus stats
    corpus_total = db.execute(
        "SELECT COUNT(*) FROM articles WHERE status='accepted_for_extraction'").fetchone()[0]
    corpus_staged = db.execute(
        "SELECT COUNT(*) FROM articles WHERE status='staged_pending_review'").fetchone()[0]
    corpus_rejected = db.execute(
        "SELECT COUNT(*) FROM articles WHERE status LIKE 'rejected%'").fetchone()[0]

    # By topic (from topic_tags JSON)
    by_topic = {}
    accepted = db.execute(
        "SELECT topic_tags FROM articles WHERE status='accepted_for_extraction' AND topic_tags IS NOT NULL"
    ).fetchall()
    for row in accepted:
        try:
            tags = json.loads(row["topic_tags"])
            for t in tags:
                by_topic[t] = by_topic.get(t, 0) + 1
        except (json.JSONDecodeError, TypeError):
            pass

    result = {
        "corpus": {
            "total_accepted": corpus_total,
            "total_staged": corpus_staged,
            "total_rejected": corpus_rejected,
            "by_topic": by_topic
        }
    }

    # Personal stats (if authenticated)
    if user:
        personal_rows = db.execute(
            "SELECT status, COUNT(*) as cnt FROM articles WHERE submitter_id=? GROUP BY status",
            (user["user_id"],)).fetchall()
        personal = {r["status"]: r["cnt"] for r in personal_rows}
        result["personal"] = {
            "submitted": sum(personal.values()),
            "accepted": personal.get("accepted_for_extraction", 0),
            "staged": personal.get("staged_pending_review", 0),
            "rejected": personal.get("rejected_irrelevant", 0) + personal.get("rejected_bad_file", 0),
            "duplicate": personal.get("duplicate_existing", 0)
        }

    db.close()
    return result
