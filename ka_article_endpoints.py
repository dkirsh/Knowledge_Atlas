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

        article_type        TEXT,          -- experimental | review | theory | mechanism | meta_analysis | other | unknown
        a0_task             TEXT,          -- task1 (experimental-only) | task2 (any-type) | NULL (non-A0)
        article_type_valid  INTEGER DEFAULT 0,  -- 1 if type confirmed appropriate for the task

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

    -- Question claiming: each question can be held by one student per round.
    -- Once all 8 questions are claimed in a round, a new round opens.
    CREATE TABLE IF NOT EXISTS question_claims (
        claim_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id     TEXT NOT NULL,          -- FK → research_questions.question_id
        user_id         TEXT NOT NULL,           -- FK → users.user_id
        round           INTEGER NOT NULL DEFAULT 1,  -- round 1, 2, 3, ...
        claimed_at      TEXT NOT NULL,
        released_at     TEXT,                    -- NULL if still held
        task1_count     INTEGER NOT NULL DEFAULT 0,  -- experimental articles submitted for this claim
        task2_count     INTEGER NOT NULL DEFAULT 0,  -- any-type articles submitted for this claim
        UNIQUE(question_id, round)               -- one claim per question per round
    );
    CREATE INDEX IF NOT EXISTS idx_claims_user ON question_claims(user_id);
    CREATE INDEX IF NOT EXISTS idx_claims_question ON question_claims(question_id, round);
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
    a0_task: str = Form(default=""),          # task1 (experimental-only) | task2 (any-type)
    article_type: str = Form(default=""),     # experimental | review | theory | mechanism | meta_analysis | other
):
    """
    Submit one or more articles (PDFs and/or citation text).
    Auth is optional — anonymous submissions are allowed.

    A0 submissions should include:
      - a0_task: 'task1' (10 experimental articles) or 'task2' (10 any-type articles)
      - article_type: classification of the article
    For task1, only 'experimental' articles count toward the requirement.
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

        # Determine article type validity for A0 task
        art_type = article_type if article_type in VALID_ARTICLE_TYPES else None
        art_type_valid = 1 if (not a0_task or a0_task != "task1" or art_type == "experimental") else 0

        # Insert article record
        db = _get_db()
        db.execute("""INSERT INTO articles
            (article_id, submission_id, submitter_id, submitter_type, track, input_mode,
             doi, pdf_filename, pdf_hash_sha256, pdf_size_bytes, quarantine_path,
             article_type, a0_task, article_type_valid,
             status, validation_notes,
             assigned_question_id, topic_tags,
             source_surface, course_context, submitter_notes,
             created_at, validated_at, staged_at, metadata_confidence)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (article_id, submission_id, submitter_id, submitter_type, track, "pdf_single",
             extracted_doi, filename, pdf_hash, len(content), str(quarantine_path),
             art_type, a0_task or None, art_type_valid,
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
            "status": "staged_pending_review",
            "a0_task": a0_task or None,
            "article_type": art_type,
            "counts_toward_requirement": bool(art_type_valid)
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


# ════════════════════════════════════════════════
# QUESTION CLAIMING (A0 Assignment)
# ════════════════════════════════════════════════

TOTAL_QUESTIONS = 30  # Q01–Q30 (covers all 9 IV domains across the topic ontology)


def _current_round(db) -> int:
    """
    Determine the current round. A round is complete when all 8 questions
    have been claimed in that round. When round N is full, round N+1 opens.
    """
    for r in range(1, 100):  # Practical upper bound
        claimed_count = db.execute(
            "SELECT COUNT(DISTINCT question_id) FROM question_claims WHERE round=? AND released_at IS NULL",
            (r,)).fetchone()[0]
        if claimed_count < TOTAL_QUESTIONS:
            return r
    return 1  # Fallback


def _available_questions(db, round_num: int) -> list:
    """Return question_ids not yet claimed in the given round."""
    claimed = db.execute(
        "SELECT question_id FROM question_claims WHERE round=? AND released_at IS NULL",
        (round_num,)).fetchall()
    claimed_ids = {r["question_id"] for r in claimed}
    all_qs = db.execute("SELECT question_id FROM research_questions ORDER BY question_id").fetchall()
    return [r["question_id"] for r in all_qs if r["question_id"] not in claimed_ids]


@router.get("/questions/available")
async def available_questions(request: Request):
    """
    Return the list of questions still available for claiming.
    Students see only unclaimed questions in the current round.
    Once all 8 are claimed, a new round opens and all questions
    become available again (we want more experimental articles per question).
    """
    db = _get_db()
    current_round = _current_round(db)
    available_ids = _available_questions(db, current_round)

    # Fetch full question details for available ones
    if not available_ids:
        db.close()
        return {"round": current_round, "available": [], "message": "All questions claimed this round"}

    placeholders = ",".join("?" * len(available_ids))
    questions = db.execute(
        f"SELECT * FROM research_questions WHERE question_id IN ({placeholders}) ORDER BY question_id",
        available_ids).fetchall()

    # Also return claim counts per question across all rounds (so students see coverage)
    coverage = db.execute("""
        SELECT question_id, COUNT(*) as times_claimed,
               SUM(task1_count) as total_experimental,
               SUM(task2_count) as total_any_type
        FROM question_claims WHERE released_at IS NULL
        GROUP BY question_id
    """).fetchall()
    coverage_map = {r["question_id"]: dict(r) for r in coverage}

    db.close()
    return {
        "round": current_round,
        "total_questions": TOTAL_QUESTIONS,
        "available_count": len(available_ids),
        "available": [
            {**dict(q), "coverage": coverage_map.get(q["question_id"], {
                "times_claimed": 0, "total_experimental": 0, "total_any_type": 0
            })}
            for q in questions
        ]
    }


class ClaimQuestionRequest(BaseModel):
    question_id: str


@router.post("/questions/claim")
async def claim_question(req: ClaimQuestionRequest, request: Request):
    """
    Claim a question for A0. Each question can only be held by one student
    per round. When all 8 are claimed, a new round opens.
    Requires authentication.
    """
    user = _get_optional_user(request)
    if not user:
        raise HTTPException(401, "You must be logged in to claim a question")

    db = _get_db()

    # Check the question exists
    q = db.execute("SELECT * FROM research_questions WHERE question_id=?",
                   (req.question_id,)).fetchone()
    if not q:
        db.close()
        raise HTTPException(404, f"Question {req.question_id} not found")

    current_round = _current_round(db)

    # Check if this question is already claimed in the current round
    existing = db.execute(
        "SELECT * FROM question_claims WHERE question_id=? AND round=? AND released_at IS NULL",
        (req.question_id, current_round)).fetchone()
    if existing:
        db.close()
        raise HTTPException(409, f"Question {req.question_id} is already claimed in round {current_round}. "
                                 f"Choose a different question.")

    # Check if this student already has a claim in the current round
    student_claim = db.execute(
        "SELECT * FROM question_claims WHERE user_id=? AND round=? AND released_at IS NULL",
        (user["user_id"], current_round)).fetchone()
    if student_claim:
        db.close()
        raise HTTPException(409, f"You already claimed question {student_claim['question_id']} in round {current_round}. "
                                 f"Release it first if you want to switch.")

    # Claim it
    now = _now()
    db.execute(
        "INSERT INTO question_claims (question_id, user_id, round, claimed_at) VALUES (?,?,?,?)",
        (req.question_id, user["user_id"], current_round, now))

    # Also update the user's question_id in the users table for backward compatibility
    db.execute("UPDATE users SET question_id=? WHERE user_id=?",
               (req.question_id, user["user_id"]))
    db.commit()

    # Check if this claim completed the round
    remaining = _available_questions(db, current_round)
    db.close()

    return {
        "claimed": True,
        "question_id": req.question_id,
        "round": current_round,
        "remaining_in_round": len(remaining),
        "message": f"You claimed {q['label']} (round {current_round}). "
                   f"{len(remaining)} question(s) still available this round."
                   + (" All questions claimed — next round now open!" if len(remaining) == 0 else "")
    }


@router.post("/questions/release")
async def release_question(req: ClaimQuestionRequest, request: Request):
    """Release a claimed question (e.g., student wants to switch)."""
    user = _get_optional_user(request)
    if not user:
        raise HTTPException(401, "You must be logged in")

    db = _get_db()
    claim = db.execute(
        "SELECT * FROM question_claims WHERE question_id=? AND user_id=? AND released_at IS NULL",
        (req.question_id, user["user_id"])).fetchone()
    if not claim:
        db.close()
        raise HTTPException(404, "You don't have an active claim on this question")

    db.execute("UPDATE question_claims SET released_at=? WHERE claim_id=?",
               (_now(), claim["claim_id"]))
    db.execute("UPDATE users SET question_id=NULL WHERE user_id=?", (user["user_id"],))
    db.commit()
    db.close()
    return {"released": True, "question_id": req.question_id}


@router.get("/questions/my-claim")
async def my_claim(request: Request):
    """
    Return ALL of the current student's active question claims and A0 progress.
    A student may have claims across multiple rounds (e.g., Q01 in round 1, Q03 in round 2).
    Each claim tracks task1 (experimental) and task2 (any-type) progress independently.
    """
    user = _get_optional_user(request)
    if not user:
        raise HTTPException(401, "You must be logged in")

    db = _get_db()
    claims = db.execute("""
        SELECT qc.*, rq.label, rq.domain, rq.text, rq.atlas_topic, rq.notes
        FROM question_claims qc
        JOIN research_questions rq ON qc.question_id = rq.question_id
        WHERE qc.user_id=? AND qc.released_at IS NULL
        ORDER BY qc.round ASC, qc.claimed_at ASC
    """, (user["user_id"],)).fetchall()

    if not claims:
        db.close()
        return {"has_claim": False, "claims": [], "message": "You haven't claimed a question yet"}

    claim_list = []
    total_task1_exp = 0
    total_task2 = 0

    for claim in claims:
        qid = claim["question_id"]

        task1_articles = db.execute("""
            SELECT COUNT(*) FROM articles
            WHERE submitter_id=? AND assigned_question_id=? AND a0_task='task1'
            AND status NOT LIKE 'rejected%%' AND status != 'duplicate_existing'
        """, (user["user_id"], qid)).fetchone()[0]

        task2_articles = db.execute("""
            SELECT COUNT(*) FROM articles
            WHERE submitter_id=? AND assigned_question_id=? AND a0_task='task2'
            AND status NOT LIKE 'rejected%%' AND status != 'duplicate_existing'
        """, (user["user_id"], qid)).fetchone()[0]

        task1_experimental = db.execute("""
            SELECT COUNT(*) FROM articles
            WHERE submitter_id=? AND assigned_question_id=? AND a0_task='task1'
            AND article_type='experimental' AND article_type_valid=1
            AND status NOT LIKE 'rejected%%' AND status != 'duplicate_existing'
        """, (user["user_id"], qid)).fetchone()[0]

        total_task1_exp += task1_experimental
        total_task2 += task2_articles

        claim_list.append({
            "question_id": qid,
            "label": claim["label"],
            "domain": claim["domain"],
            "text": claim["text"],
            "round": claim["round"],
            "progress": {
                "task1": {
                    "submitted": task1_articles,
                    "confirmed_experimental": task1_experimental,
                    "required": 10,
                    "requirement": "All 10 must be experimental articles",
                    "complete": task1_experimental >= 10
                },
                "task2": {
                    "submitted": task2_articles,
                    "required": 10,
                    "requirement": "Any article type accepted",
                    "complete": task2_articles >= 10
                },
                "a0_complete": task1_experimental >= 10 and task2_articles >= 10
            }
        })

    db.close()

    return {
        "has_claim": True,
        "claims": claim_list,
        "total_progress": {
            "total_experimental": total_task1_exp,
            "total_any_type": total_task2,
            "total_articles": total_task1_exp + total_task2,
            "target": 20
        }
    }


# ════════════════════════════════════════════════
# A0 ARTICLE TYPE VALIDATION
# ════════════════════════════════════════════════

VALID_ARTICLE_TYPES = {"experimental", "review", "theory", "mechanism", "meta_analysis", "other", "unknown"}


class SetArticleTypeRequest(BaseModel):
    article_type: str  # experimental | review | theory | mechanism | meta_analysis | other
    a0_task: str = ""  # task1 | task2 (optional, set at submission time)


@router.post("/{article_id}/set-type")
async def set_article_type(article_id: str, req: SetArticleTypeRequest, request: Request):
    """
    Set or update the article type classification. Used by:
    - Students self-classifying during upload
    - Instructors correcting classifications during review

    For Task 1 submissions, article_type MUST be 'experimental' to count toward
    the 10-article requirement. Non-experimental articles submitted to Task 1 are
    stored but flagged as not counting.
    """
    user = _get_optional_user(request)
    if not user:
        raise HTTPException(401, "Authentication required")

    if req.article_type not in VALID_ARTICLE_TYPES:
        raise HTTPException(400, f"Invalid article_type. Must be one of: {', '.join(sorted(VALID_ARTICLE_TYPES))}")

    db = _get_db()
    row = db.execute("SELECT * FROM articles WHERE article_id=?", (article_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, "Article not found")

    a0_task = req.a0_task or row["a0_task"]
    # For task1: only 'experimental' is valid (counts toward requirement)
    type_valid = 1
    message = f"Article classified as {req.article_type}"
    if a0_task == "task1" and req.article_type != "experimental":
        type_valid = 0
        message = (f"Article classified as {req.article_type}. Note: Task 1 requires experimental "
                   f"articles — this paper is stored but does not count toward your 10-article requirement.")

    db.execute("""UPDATE articles SET article_type=?, a0_task=?, article_type_valid=?
                  WHERE article_id=?""",
               (req.article_type, a0_task, type_valid, article_id))
    db.commit()

    # Update the claim's task counts
    if a0_task and row["submitter_id"] and row["assigned_question_id"]:
        _update_claim_counts(db, row["submitter_id"], row["assigned_question_id"])

    db.close()

    return {"article_id": article_id, "article_type": req.article_type,
            "a0_task": a0_task, "counts_toward_requirement": bool(type_valid),
            "message": message}


def _update_claim_counts(db, user_id: str, question_id: str):
    """Recalculate task1/task2 counts on the user's active claim."""
    task1 = db.execute("""
        SELECT COUNT(*) FROM articles
        WHERE submitter_id=? AND assigned_question_id=? AND a0_task='task1'
        AND article_type='experimental' AND article_type_valid=1
        AND status NOT LIKE 'rejected%%' AND status != 'duplicate_existing'
    """, (user_id, question_id)).fetchone()[0]

    task2 = db.execute("""
        SELECT COUNT(*) FROM articles
        WHERE submitter_id=? AND assigned_question_id=? AND a0_task='task2'
        AND status NOT LIKE 'rejected%%' AND status != 'duplicate_existing'
    """, (user_id, question_id)).fetchone()[0]

    db.execute("""UPDATE question_claims SET task1_count=?, task2_count=?
                  WHERE user_id=? AND question_id=? AND released_at IS NULL""",
               (task1, task2, user_id, question_id))
    db.commit()


# ════════════════════════════════════════════════
# AUTOMATIC ARTICLE TYPE CLASSIFICATION
# ════════════════════════════════════════════════

# Keywords strongly associated with experimental papers
_EXP_KEYWORDS = {
    "participants", "experiment", "experiments", "experimental", "randomized",
    "randomised", "randomly assigned", "controlled trial", "rct", "anova",
    "t-test", "t test", "chi-square", "regression analysis", "sample size",
    "n =", "n=", "between-subjects", "within-subjects", "repeated measures",
    "condition", "conditions", "manipulation", "manipulated", "stimulus",
    "stimuli", "pre-test", "post-test", "pretest", "posttest", "baseline",
    "intervention", "dependent variable", "independent variable", "effect size",
    "cohen's d", "eta squared", "significant difference", "p <", "p<", "p =",
    "findings suggest", "results showed", "results indicated", "was measured",
    "were measured", "performance was", "reaction time", "accuracy was",
    "eye tracking", "eye-tracking", "fmri", "eeg", "galvanic skin",
    "physiological", "behavioral measure", "self-report", "likert",
    "questionnaire", "survey instrument", "recruited", "enrolled",
    "informed consent", "irb", "ethics committee", "exclusion criteria",
    "inclusion criteria", "control group", "experimental group",
    "treatment group", "placebo", "double-blind", "single-blind",
    "counterbalanced", "latin square", "factorial design", "mixed design",
    "between-group", "within-group", "lab study", "laboratory study",
    "field experiment", "quasi-experiment", "longitudinal study",
    "cross-sectional study", "cohort study", "observational study"
}

# Keywords associated with reviews and meta-analyses
_REVIEW_KEYWORDS = {
    "systematic review", "meta-analysis", "meta analysis", "literature review",
    "scoping review", "narrative review", "reviewed the literature",
    "databases were searched", "prisma", "search strategy", "inclusion criteria",
    "exclusion criteria for studies", "studies were identified", "studies met",
    "effect sizes were", "pooled effect", "heterogeneity", "funnel plot",
    "publication bias", "forest plot", "quality assessment", "risk of bias",
    "we reviewed", "this review", "review of the literature"
}

# Keywords associated with theoretical papers
_THEORY_KEYWORDS = {
    "theoretical framework", "we propose", "we argue", "conceptual model",
    "conceptual framework", "theoretical model", "theory of", "we theorize",
    "philosophical", "epistemological", "ontological", "we contend",
    "thought experiment", "framework for understanding", "taxonomy of",
    "typology of", "we develop a", "integrative model", "computational model"
}


def _classify_article_type(text: str) -> dict:
    """
    Classify article type from abstract or full text using keyword heuristics.
    Returns {"article_type": str, "confidence": float, "signals": list}.
    """
    if not text or len(text.strip()) < 20:
        return {"article_type": "unknown", "confidence": 0.0, "signals": ["insufficient_text"]}

    text_lower = text.lower()
    signals = []

    # Count keyword matches for each type
    exp_hits = sum(1 for kw in _EXP_KEYWORDS if kw in text_lower)
    rev_hits = sum(1 for kw in _REVIEW_KEYWORDS if kw in text_lower)
    theory_hits = sum(1 for kw in _THEORY_KEYWORDS if kw in text_lower)

    # Strong signals: methods section indicators
    has_methods = bool(re.search(r'\b(method|methods|procedure|materials|design)\b', text_lower))
    has_results = bool(re.search(r'\b(results|findings)\b', text_lower))
    has_n_equals = bool(re.search(r'\bn\s*=\s*\d+', text_lower))
    has_p_value = bool(re.search(r'p\s*[<>=]\s*[0-9.]', text_lower))

    if has_methods:
        signals.append("has_methods_section")
    if has_results:
        signals.append("has_results_section")
    if has_n_equals:
        signals.append("has_sample_size")
        exp_hits += 3  # strong signal
    if has_p_value:
        signals.append("has_p_values")
        exp_hits += 3  # strong signal

    # Weighted scoring
    exp_score = exp_hits
    rev_score = rev_hits * 2  # review keywords are more specific
    theory_score = theory_hits * 2

    # Determine classification
    if rev_score >= 4 and rev_score > exp_score:
        article_type = "review" if "meta-analysis" not in text_lower and "meta analysis" not in text_lower else "meta_analysis"
        confidence = min(0.95, 0.5 + rev_score * 0.05)
        signals.append(f"review_keywords={rev_hits}")
    elif exp_score >= 3:
        article_type = "experimental"
        confidence = min(0.95, 0.4 + exp_score * 0.03)
        signals.append(f"exp_keywords={exp_hits}")
    elif theory_score >= 4 and theory_score > exp_score:
        article_type = "theory"
        confidence = min(0.90, 0.4 + theory_score * 0.05)
        signals.append(f"theory_keywords={theory_hits}")
    elif exp_score >= 1 and has_methods and has_results:
        article_type = "experimental"
        confidence = 0.55
        signals.append("weak_exp_with_methods_results")
    else:
        article_type = "unknown"
        confidence = 0.2
        signals.append("no_strong_signal")

    return {"article_type": article_type, "confidence": round(confidence, 2), "signals": signals}


def _extract_text_from_pdf_bytes(data: bytes, max_chars: int = 5000) -> str:
    """Extract text from PDF bytes for classification. Best-effort."""
    try:
        import io
        # Try pdfplumber first (better extraction)
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                text = ""
                for page in pdf.pages[:5]:  # first 5 pages max
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
                    if len(text) > max_chars:
                        break
                return text[:max_chars]
        except ImportError:
            pass

        # Fallback: PyPDF2
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(data))
            text = ""
            for page in reader.pages[:5]:
                text += (page.extract_text() or "") + "\n"
                if len(text) > max_chars:
                    break
            return text[:max_chars]
        except ImportError:
            pass

        # Last resort: raw byte search for text
        text_bytes = data[:50000]
        # Extract ASCII text fragments
        fragments = re.findall(rb'[A-Za-z][A-Za-z0-9\s.,;:!?\-()]{10,}', text_bytes)
        return " ".join(f.decode('ascii', errors='ignore') for f in fragments)[:max_chars]
    except Exception:
        return ""


# ════════════════════════════════════════════════
# STUDENT-FACING BRIDGE ENDPOINTS
# ════════════════════════════════════════════════
# These wrap the core submit infrastructure and add automatic classification.
# The frontend (collect-articles-upload.html) calls these endpoints.

student_router = APIRouter(prefix="/api/student", tags=["student"])


@student_router.post("/fetch-abstracts")
async def fetch_abstracts_and_classify(request: Request):
    """
    A0 upload endpoint: receive PDFs + citation metadata, automatically classify
    each article's type, store everything, and return per-paper feedback.

    Expects multipart form data with:
    - question_id: str
    - question_type: '10-exp' | 'mixed'
    - papers_json: JSON array of {doi, apa_citation, filename}
    - pdfs: uploaded PDF files
    """
    user = _get_optional_user(request)
    if not user:
        raise HTTPException(401, "You must be signed in to submit articles")

    form = await request.form()
    question_id = form.get("question_id", "")
    question_type = form.get("question_type", "10-exp")
    papers_json_str = form.get("papers_json", "[]")

    try:
        papers_meta = json.loads(papers_json_str)
    except json.JSONDecodeError:
        papers_meta = []

    # Determine A0 task from question_type
    a0_task = "task1" if question_type == "10-exp" else "task2"

    # Get uploaded files
    pdf_files = form.getlist("pdfs") if hasattr(form, "getlist") else []
    # Also check for UploadFile objects
    if not pdf_files:
        for key in form:
            val = form.getlist(key)
            for v in val:
                if hasattr(v, 'read') and hasattr(v, 'filename'):
                    pdf_files.append(v)

    # Create batch
    submission_id = _next_id("KA-IN-", "submission_batches", "submission_id")
    now = _now()
    db = _get_db()
    db.execute(
        "INSERT INTO submission_batches VALUES (?,?,?,?,?,?,?,?)",
        (submission_id, user["user_id"], user["role"], "a0_upload", 0,
         "collect_articles_upload", now, None))
    db.commit()
    db.close()

    result_papers = []
    qualifying_count = 0

    # Process each PDF
    for i, pdf_file in enumerate(pdf_files):
        if not hasattr(pdf_file, 'read'):
            continue
        content = await pdf_file.read()
        filename = getattr(pdf_file, 'filename', f'paper_{i}.pdf')

        article_id = _next_id("KA-ART-", "articles", "article_id")
        pdf_hash = _compute_sha256(content)

        # Validate PDF
        validation = _validate_pdf_bytes(content, filename)
        if not validation.get("valid"):
            result_papers.append({
                "title": filename,
                "filename": filename,
                "article_type": "unknown",
                "abstract": f"Invalid PDF: {validation.get('rejection_reason', 'validation failed')}",
                "pdf_present": True,
                "in_corpus": False,
                "classification_confidence": 0.0,
                "qualifies": False,
                "feedback": f"Rejected: {validation.get('rejection_reason', 'invalid file')}"
            })
            continue

        # Extract text for classification
        extracted_text = _extract_text_from_pdf_bytes(content)
        classification = _classify_article_type(extracted_text)
        art_type = classification["article_type"]
        art_confidence = classification["confidence"]

        # Extract abstract (first ~500 chars after "abstract" keyword, or first paragraph)
        abstract = ""
        if extracted_text:
            abs_match = re.search(r'(?i)\babstract\b[:\s]*(.{50,800}?)(?:\n\n|\bintroduction\b|\bkeywords\b)', extracted_text)
            if abs_match:
                abstract = abs_match.group(1).strip()
            else:
                abstract = extracted_text[:300].strip()

        # Get citation metadata if available
        meta = papers_meta[i] if i < len(papers_meta) else {}
        apa_citation = meta.get("apa_citation", "")
        doi = meta.get("doi", "")
        extracted_doi = _extract_doi_from_pdf(content) or doi

        # Duplicate check
        dup_result = _check_duplicate(pdf_hash=pdf_hash, doi=extracted_doi)

        # Determine if it qualifies
        type_valid = 1 if (a0_task != "task1" or art_type == "experimental") else 0
        if art_type == "experimental" and a0_task == "task1":
            qualifying_count += 1

        # Determine status
        if not validation.get("valid"):
            status = "rejected_bad_file"
        elif dup_result["is_duplicate"]:
            status = "duplicate_existing"
        else:
            status = "staged_pending_review"

        # Extract title from text
        title = filename
        if extracted_text:
            # First substantial line is often the title
            lines = [l.strip() for l in extracted_text.split('\n') if len(l.strip()) > 10]
            if lines:
                candidate = lines[0][:200]
                if len(candidate) > 15 and not candidate.lower().startswith(('http', 'doi', 'volume', 'journal')):
                    title = candidate

        # Store in database
        db = _get_db()
        try:
            db.execute("""INSERT INTO articles
                (article_id, submission_id, submitter_id, submitter_type, track, input_mode,
                 doi, pdf_filename, pdf_hash_sha256, pdf_size_bytes, quarantine_path,
                 article_type, a0_task, article_type_valid,
                 status, validation_notes, citation_raw,
                 assigned_question_id,
                 source_surface, course_context,
                 created_at, validated_at, staged_at, metadata_confidence)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (article_id, submission_id, user["user_id"], user["role"],
                 user.get("track"), "pdf_single",
                 extracted_doi, filename, pdf_hash, len(content), "",
                 art_type, a0_task, type_valid,
                 status, json.dumps(validation), apa_citation,
                 question_id or None,
                 "collect_articles_upload", "COGS160-SP26",
                 now, now, now if status == "staged_pending_review" else None,
                 "high" if extracted_doi else "medium"))
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"[KA-ARTICLES] DB error storing {article_id}: {e}")
        finally:
            db.close()

        # Save PDF to quarantine
        try:
            month_dir = QUARANTINE_DIR / datetime.now().strftime("%Y-%m")
            month_dir.mkdir(parents=True, exist_ok=True)
            (month_dir / f"{article_id}.pdf").write_bytes(content)
        except Exception as e:
            print(f"[KA-ARTICLES] File storage error for {article_id}: {e}")

        # Build feedback message
        if art_type == "experimental":
            feedback = f"✓ Accepted — experimental article (confidence: {art_confidence:.0%})"
        elif art_type == "unknown":
            feedback = "⚠ Could not determine article type — will be reviewed manually"
        else:
            feedback = f"✗ Classified as {art_type} (confidence: {art_confidence:.0%}) — not an experiment"

        if dup_result["is_duplicate"]:
            feedback = "⚠ Duplicate — this article is already in the system"

        result_papers.append({
            "title": title,
            "filename": filename,
            "article_type": art_type if art_type != "unknown" else "Other",
            "abstract": abstract[:300] if abstract else "Abstract not extracted",
            "pdf_present": True,
            "in_corpus": dup_result["is_duplicate"],
            "classification_confidence": art_confidence,
            "qualifies": bool(type_valid) and art_type == "experimental",
            "feedback": feedback,
            "article_id": article_id
        })

    # Update batch count
    db = _get_db()
    db.execute("UPDATE submission_batches SET item_count=?, completed_at=? WHERE submission_id=?",
               (len(result_papers), _now(), submission_id))
    db.commit()
    db.close()

    return {
        "papers": result_papers,
        "qualifying_count": qualifying_count,
        "submission_id": submission_id,
        "task": a0_task,
        "total_submitted": len(result_papers)
    }


@student_router.post("/title-only")
async def submit_title_only_papers(request: Request):
    """
    Submit citation-only papers (no PDF) for classification.
    Used by the quick-add citation feature and bulk .txt upload.
    """
    user = _get_optional_user(request)
    if not user:
        raise HTTPException(401, "You must be signed in to submit articles")

    body = await request.json()
    question_id = body.get("question_id", "")
    question_type = body.get("question_type", "10-exp")
    papers = body.get("papers", [])
    a0_task = "task1" if question_type == "10-exp" else "task2"

    if not papers:
        raise HTTPException(400, "No papers provided")

    submission_id = _next_id("KA-IN-", "submission_batches", "submission_id")
    now = _now()

    db = _get_db()
    db.execute(
        "INSERT INTO submission_batches VALUES (?,?,?,?,?,?,?,?)",
        (submission_id, user["user_id"], user["role"], "a0_title_only", 0,
         "collect_articles_upload", now, None))
    db.commit()
    db.close()

    result_papers = []
    qualifying_count = 0

    for paper in papers:
        article_id = _next_id("KA-ART-", "articles", "article_id")
        title = paper.get("article_title", "")
        doi = paper.get("doi", "")
        apa = paper.get("apa_citation", "")

        # Classify from citation text (limited, but catches reviews/meta-analyses)
        classify_text = f"{title} {apa}"
        classification = _classify_article_type(classify_text)
        art_type = classification["article_type"]
        art_confidence = classification["confidence"]

        # For citation-only, if we can't tell, default to "unknown" (needs manual review)
        if art_type == "unknown" and art_confidence < 0.3:
            # Citation-only papers are harder to classify; mark for review
            art_type = "unknown"

        type_valid = 1 if (a0_task != "task1" or art_type == "experimental") else 0
        if art_type == "experimental" and a0_task == "task1":
            qualifying_count += 1

        # Duplicate check by DOI
        dup_result = _check_duplicate(doi=doi if doi else None,
                                       title=title if title else None)

        status = "duplicate_existing" if dup_result["is_duplicate"] else "staged_pending_review"

        # Parse citation for structured fields
        parsed = _parse_citation_line(apa) if apa else {"title": title, "authors": "", "year": ""}

        db = _get_db()
        try:
            db.execute("""INSERT INTO articles
                (article_id, submission_id, submitter_id, submitter_type, track, input_mode,
                 doi, title, authors, year, citation_raw,
                 article_type, a0_task, article_type_valid,
                 status, duplicate_of,
                 assigned_question_id,
                 source_surface, course_context,
                 created_at, staged_at, metadata_confidence)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (article_id, submission_id, user["user_id"], user["role"],
                 user.get("track"), "citation_text",
                 doi or None,
                 parsed["title"] or title or None,
                 parsed["authors"] or None,
                 int(parsed["year"]) if parsed.get("year") else None,
                 apa,
                 art_type, a0_task, type_valid,
                 status,
                 dup_result["matches"][0]["article_id"] if dup_result["is_duplicate"] and dup_result["matches"] else None,
                 question_id or None,
                 "collect_articles_upload", "COGS160-SP26",
                 now, now if status == "staged_pending_review" else None,
                 "medium" if doi else "low"))
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"[KA-ARTICLES] DB error storing title-only {article_id}: {e}")
        finally:
            db.close()

        # Build display title
        display_title = parsed["title"] or title or apa[:80]

        # Feedback
        if art_type == "experimental":
            feedback = f"✓ Accepted — likely experimental (confidence: {art_confidence:.0%})"
        elif art_type == "unknown":
            feedback = "⚠ Cannot determine type from citation alone — upload PDF for classification"
        else:
            feedback = f"✗ Classified as {art_type} (confidence: {art_confidence:.0%})"

        result_papers.append({
            "title": display_title,
            "article_type": art_type.capitalize() if art_type != "unknown" else "Unknown",
            "abstract": "Citation only — upload PDF for full abstract",
            "pdf_present": False,
            "in_corpus": dup_result["is_duplicate"],
            "title_only": True,
            "classification_confidence": art_confidence,
            "qualifies": bool(type_valid) and art_type == "experimental",
            "feedback": feedback,
            "article_id": article_id
        })

    # Update batch
    db = _get_db()
    db.execute("UPDATE submission_batches SET item_count=?, completed_at=? WHERE submission_id=?",
               (len(result_papers), _now(), submission_id))
    db.commit()
    db.close()

    return {
        "papers": result_papers,
        "qualifying_count": qualifying_count,
        "submission_id": submission_id,
        "task": a0_task,
        "total_submitted": len(result_papers)
    }


@student_router.post("/classify-one")
async def classify_single_paper(request: Request):
    """
    Real-time single-paper classification. Called when a PDF is dropped
    into the upload zone — gives immediate feedback without batch submission.
    Does NOT store the article; that happens on the full submit.
    """
    form = await request.form()
    pdf_file = form.get("pdf")

    if not pdf_file or not hasattr(pdf_file, 'read'):
        raise HTTPException(400, "No PDF file provided")

    content = await pdf_file.read()
    filename = getattr(pdf_file, 'filename', 'paper.pdf')

    # Quick validation
    validation = _validate_pdf_bytes(content, filename)
    if not validation.get("valid"):
        return {
            "filename": filename,
            "valid": False,
            "article_type": "unknown",
            "confidence": 0.0,
            "feedback": f"Invalid PDF: {validation.get('rejection_reason', 'validation failed')}",
            "is_experimental": False
        }

    # Extract text and classify
    extracted_text = _extract_text_from_pdf_bytes(content)
    classification = _classify_article_type(extracted_text)

    art_type = classification["article_type"]
    confidence = classification["confidence"]

    if art_type == "experimental":
        feedback = f"✓ Experimental article (confidence: {confidence:.0%})"
    elif art_type == "unknown":
        feedback = "⚠ Could not determine type — will be classified on submission"
    else:
        feedback = f"✗ Appears to be {art_type} (confidence: {confidence:.0%}) — not experimental"

    return {
        "filename": filename,
        "valid": True,
        "article_type": art_type,
        "confidence": confidence,
        "feedback": feedback,
        "is_experimental": art_type == "experimental",
        "signals": classification["signals"]
    }


@student_router.get("/progress/{student_id}")
async def get_student_progress(student_id: str):
    """
    Returns the student's A0 completion status.
    A0 is complete when task1_count >= 10 (10 experimental articles for Q1).
    Used for client-side redirect logic after login.
    """
    db = _get_db()

    # Get all claims for this student
    rows = db.execute("""
        SELECT question_id, task1_count, task2_count, round
        FROM question_claims
        WHERE user_id = ? AND released_at IS NULL
        ORDER BY round, question_id
    """, (student_id,)).fetchall()

    q1_experimental = 0
    q2_any_type = 0
    brownie_count = 0

    for row in rows:
        qid = row["question_id"]
        t1 = row["task1_count"] or 0
        t2 = row["task2_count"] or 0
        rnd = row["round"] or 1

        if rnd == 1:
            # Round 1: Q1 = experimental, Q2 = mixed
            if "q1" in qid.lower() or qid.endswith("-1"):
                q1_experimental = t1
            else:
                q2_any_type = t2
        else:
            # Round 2+: brownie questions
            brownie_count += 1 if t2 >= 10 else 0

    a0_complete = q1_experimental >= 10

    return {
        "student_id": student_id,
        "a0_complete": a0_complete,
        "q1_experimental_count": q1_experimental,
        "q2_any_type_count": q2_any_type,
        "brownie_questions_complete": brownie_count,
        "redirect_to": "ka_schedule.html" if a0_complete else "ka_student_setup.html"
    }
