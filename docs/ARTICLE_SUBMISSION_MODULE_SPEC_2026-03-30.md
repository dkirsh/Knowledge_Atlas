# Article Submission Module — Specification & Contract

**Date**: 2026-03-30
**Author**: CW (Claude Code) for Prof. David Kirsh
**Status**: Draft for review
**Scope**: Backend endpoints, database schema, storage layout, and integration points for article intake in the Knowledge Atlas platform

---

## 1. Purpose

The Knowledge Atlas frontend already provides two intake surfaces — `ka_contribute.html` (simple single-article) and `ka_article_propose.html` (batch-capable, multi-mode) — but neither connects to a backend. All collected articles currently live in `localStorage` via `ka_article_collector.js` and vanish when the browser clears storage.

This module closes that gap. It extends `ka_auth_server.py` with endpoints for receiving article submissions, performing immediate validation and duplicate detection, staging PDFs in quarantine, and promoting accepted files into the extraction pipeline's PDF collection.

The design honours three existing policy documents:

- `ARTICLE_INTAKE_POLICY_2026-03-24.md` (intake states, security gates, audit rules)
- `ARTICLE_INTAKE_AF_INTEGRATION_CONTRACT_2026-03-24.md` (adapter request/response objects, AF capabilities)
- `GUI_DATA_CONTRACTS_2026-03-24.md` (frontend data shapes)

---

## 2. Architecture Overview

```
┌─────────────────────────────┐
│  ka_contribute.html         │
│  ka_article_propose.html    │──── POST /api/articles/submit ────┐
│  ka_article_collector.js    │                                    │
└─────────────────────────────┘                                    ▼
                                                        ┌──────────────────┐
                                                        │  ka_auth_server   │
                                                        │  (FastAPI)        │
                                                        │                  │
                                                        │  /api/articles/* │
                                                        └───────┬──────────┘
                                                                │
                                        ┌───────────────────────┼────────────────────┐
                                        ▼                       ▼                    ▼
                                ┌──────────────┐    ┌───────────────┐    ┌──────────────────┐
                                │  SQLite DB   │    │  Quarantine   │    │  Promoted PDFs   │
                                │  articles    │    │  /quarantine/ │    │  /pdf_collection/│
                                │  table       │    │  (temp hold)  │    │  (pipeline-ready)│
                                └──────────────┘    └───────────────┘    └──────────────────┘
```

**Single server, single database.** We extend `ka_auth_server.py` rather than creating a separate service. The auth database (`data/ka_auth.db`) gains new tables. PDFs land on the 5TB mount in a directory structure the extraction pipeline already expects.

---

## 3. Database Schema Extensions

### 3.1 `articles` table

Stores metadata for every submission, regardless of outcome.

```sql
CREATE TABLE IF NOT EXISTS articles (
    article_id       TEXT PRIMARY KEY,          -- 'KA-ART-' + 6-digit zero-padded sequence
    submission_id    TEXT NOT NULL,             -- 'KA-IN-' + 6-digit sequence (groups batch items)
    submitter_id     TEXT,                      -- FK → users.user_id (NULL for anonymous)
    submitter_type   TEXT NOT NULL DEFAULT 'anonymous',  -- anonymous | student | contributor | maintainer
    track            TEXT,                      -- Track ID if student submitter
    input_mode       TEXT NOT NULL,             -- pdf_single | pdf_batch | citation_text | citation_file | doi_only | title_only

    -- Metadata (extracted or user-provided)
    doi              TEXT,
    title            TEXT,
    authors          TEXT,                      -- JSON array of author strings
    year             INTEGER,
    journal          TEXT,
    abstract         TEXT,
    citation_raw     TEXT,                      -- Original citation text as submitted

    -- File information
    pdf_filename     TEXT,                      -- Original upload filename
    pdf_hash_sha256  TEXT,                      -- SHA-256 of PDF bytes (computed on receipt)
    pdf_size_bytes   INTEGER,
    quarantine_path  TEXT,                      -- Path in quarantine area
    promoted_path    TEXT,                      -- Path in extraction pipeline collection (NULL until promoted)

    -- Status tracking
    status           TEXT NOT NULL DEFAULT 'received',
        -- received → validated → staged_pending_review → accepted_for_extraction | rejected_irrelevant | rejected_bad_file | duplicate_existing
    duplicate_of     TEXT,                      -- article_id of the existing duplicate, if any
    validation_notes TEXT,                      -- JSON: magic byte check, parser check, size check results
    relevance_score  REAL,                      -- 0.0–1.0 from nightly relevance triage (NULL until scored)
    review_notes     TEXT,                      -- Instructor/reviewer notes on acceptance/rejection

    -- Topic linkage
    assigned_question_id TEXT,                  -- FK → research_questions.question_id (which question this article addresses)
    topic_tags       TEXT,                      -- JSON array of topic labels

    -- Source context
    source_surface   TEXT DEFAULT 'ka_contribute', -- ka_contribute | ka_article_propose | api_direct
    course_context   TEXT,                      -- e.g., 'COGS160-SP26'
    submitter_notes  TEXT,                      -- "Why this paper matters" free text

    -- Timestamps
    created_at       TEXT NOT NULL,             -- ISO 8601
    validated_at     TEXT,
    staged_at        TEXT,
    reviewed_at      TEXT,
    promoted_at      TEXT,
    rejected_at      TEXT,

    -- Audit
    metadata_confidence TEXT DEFAULT 'low',     -- high | medium | low (how much metadata was extractable)

    FOREIGN KEY (submitter_id) REFERENCES users(user_id),
    FOREIGN KEY (assigned_question_id) REFERENCES research_questions(question_id)
);

CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_submitter ON articles(submitter_id);
CREATE INDEX idx_articles_doi ON articles(doi);
CREATE INDEX idx_articles_hash ON articles(pdf_hash_sha256);
CREATE INDEX idx_articles_submission ON articles(submission_id);
```

### 3.2 `submission_batches` table

Groups items submitted together.

```sql
CREATE TABLE IF NOT EXISTS submission_batches (
    submission_id    TEXT PRIMARY KEY,          -- 'KA-IN-' + 6-digit sequence
    submitter_id     TEXT,                      -- FK → users.user_id (NULL for anonymous)
    submitter_type   TEXT NOT NULL DEFAULT 'anonymous',
    input_mode       TEXT NOT NULL,             -- pdf_batch | citation_list | citation_file | mixed
    item_count       INTEGER NOT NULL DEFAULT 0,
    source_surface   TEXT,
    created_at       TEXT NOT NULL,
    completed_at     TEXT,                      -- When all items have been processed

    FOREIGN KEY (submitter_id) REFERENCES users(user_id)
);
```

### 3.3 `audit_log` table

Immutable record of every state transition, kept even after file deletion.

```sql
CREATE TABLE IF NOT EXISTS audit_log (
    log_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id       TEXT NOT NULL,
    action           TEXT NOT NULL,             -- received | validated | staged | accepted | rejected | promoted | deleted_file
    old_status       TEXT,
    new_status       TEXT,
    actor_id         TEXT,                      -- user_id of whoever triggered the action (NULL for system)
    actor_type       TEXT DEFAULT 'system',     -- system | student | instructor | maintainer
    details          TEXT,                      -- JSON with action-specific detail
    created_at       TEXT NOT NULL,

    FOREIGN KEY (article_id) REFERENCES articles(article_id)
);

CREATE INDEX idx_audit_article ON audit_log(article_id);
CREATE INDEX idx_audit_action ON audit_log(action);
```

---

## 4. PDF Storage Layout

All paths are relative to a configurable `STORAGE_ROOT` (default: `/mnt/ka_storage` on the university VM).

```
$STORAGE_ROOT/
├── quarantine/                        # Uploaded PDFs awaiting validation/review
│   └── {YYYY-MM}/                     # Monthly partitions
│       └── {article_id}.pdf           # Renamed to article_id on receipt
│
├── pdf_collection/                    # Promoted PDFs ready for extraction pipeline
│   └── {topic_slug}/                  # Grouped by primary topic
│       └── {article_id}_{sanitized_title}.pdf
│
├── rejected/                          # Audit stubs (no PDF retained, just metadata)
│   └── {YYYY-MM}/
│       └── {article_id}.json          # Metadata + rejection reason
│
└── backups/                           # Nightly SQLite backup
    └── ka_auth_{YYYY-MM-DD}.db
```

**Extraction pipeline compatibility**: The `pdf_collection/` directory mirrors the structure expected by Article_Eater's `cmd_import_pdfs` command. Each PDF is accompanied by a sidecar `.json` file containing extracted metadata, so the pipeline can ingest without re-extracting basic bibliographic data.

---

## 5. API Endpoints

All new endpoints live under `/api/articles/`. Authentication is optional for submission (anonymous allowed) but required for review actions.

### 5.1 `POST /api/articles/submit`

**Purpose**: Receive one or more articles (PDF files and/or citation text).

**Auth**: Optional. If Bearer token provided, submission is attributed to user. Otherwise marked anonymous.

**Content-Type**: `multipart/form-data`

**Form fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `files` | File[] | No | One or more PDF files |
| `citations` | string | No | Newline-separated citation text (APA, DOI, or title) |
| `citation_file` | File | No | `.bib`, `.ris`, `.csv`, or `.txt` citation file |
| `question_id` | string | No | Research question this addresses (e.g., `Q01`) |
| `topic_tags` | string | No | JSON array of topic labels |
| `notes` | string | No | "Why this paper matters" free text |
| `source_surface` | string | No | Which page submitted from (default: `ka_contribute`) |

**At least one of** `files`, `citations`, or `citation_file` must be provided.

**Response** (JSON):

```json
{
  "submission_id": "KA-IN-000042",
  "items": [
    {
      "article_id": "KA-ART-000197",
      "input_mode": "pdf_single",
      "filename": "boubekri_2014_daylighting.pdf",
      "validation_status": "valid",
      "duplicate_status": "not_duplicate",
      "metadata": {
        "doi": "10.1016/j.jenvp.2014.02.003",
        "title": "Impact of Windows and Daylight Exposure...",
        "authors": ["Boubekri, M.", "Cheung, I. N.", "Reid, K. J."],
        "year": 2014,
        "confidence": "high"
      },
      "status": "staged_pending_review"
    }
  ],
  "summary": {
    "total": 1,
    "staged": 1,
    "duplicates": 0,
    "rejected": 0
  }
}
```

**Processing sequence** (per item):

1. **Receive** — Assign `article_id`, compute SHA-256 hash, save to quarantine
2. **Validate** — Check magic bytes (must be `%PDF`), reject encrypted/malformed, reject if >100 MB
3. **Deduplicate** — Check `pdf_hash_sha256` against existing articles; check DOI if extractable; check title similarity (Levenshtein ≥ 0.85) as fallback
4. **Extract metadata** — Parse first page for DOI, title, authors, year; use DOI resolution if DOI found
5. **Stage** — Set status to `staged_pending_review`; write audit log entry

### 5.2 `GET /api/articles/status/{article_id}`

**Purpose**: Check the current status of a submitted article.

**Auth**: Optional. Anonymous users can check by `article_id` (which serves as a receipt token). Authenticated users see richer detail.

**Response**:

```json
{
  "article_id": "KA-ART-000197",
  "status": "staged_pending_review",
  "title": "Impact of Windows and Daylight Exposure...",
  "submitted_at": "2026-03-30T14:22:00Z",
  "duplicate_status": "not_duplicate",
  "metadata_confidence": "high"
}
```

### 5.3 `GET /api/articles/my-submissions`

**Purpose**: List all articles submitted by the authenticated user.

**Auth**: Required (Bearer token).

**Query params**: `?status=staged_pending_review&limit=50&offset=0`

**Response**: Array of article summary objects with counts:

```json
{
  "submissions": [...],
  "counts": {
    "total": 12,
    "staged": 5,
    "accepted": 4,
    "rejected": 2,
    "duplicate": 1
  }
}
```

### 5.4 `GET /api/articles/pending-review`

**Purpose**: List articles awaiting instructor review.

**Auth**: Required (instructor or maintainer role).

**Query params**: `?limit=50&offset=0&sort=created_at`

**Response**: Array of article objects with full metadata and validation details.

### 5.5 `POST /api/articles/{article_id}/review`

**Purpose**: Accept or reject a staged article.

**Auth**: Required (instructor or maintainer role).

**Body**:

```json
{
  "decision": "accept" | "reject",
  "reason": "Optional rejection reason",
  "topic_override": "Optional: reassign to different topic",
  "notes": "Reviewer notes"
}
```

**On accept**:
1. Move PDF from `quarantine/` to `pdf_collection/{topic}/`
2. Write sidecar `.json` with metadata
3. Update status to `accepted_for_extraction`
4. Write audit log entry

**On reject**:
1. Delete PDF from quarantine
2. Write rejection stub to `rejected/{YYYY-MM}/{article_id}.json`
3. Update status to `rejected_irrelevant` or `rejected_bad_file`
4. Write audit log entry

### 5.6 `POST /api/articles/check-duplicate`

**Purpose**: Quick duplicate check without full submission (used by frontend for real-time feedback).

**Auth**: Optional.

**Body**:

```json
{
  "doi": "optional",
  "title": "optional",
  "pdf_hash": "optional SHA-256"
}
```

**Response**:

```json
{
  "is_duplicate": false,
  "matches": [],
  "check_type": "doi+title"
}
```

### 5.7 `GET /api/articles/stats`

**Purpose**: Dashboard statistics for the article collection.

**Auth**: Optional (public stats); authenticated users see personal stats too.

**Response**:

```json
{
  "corpus": {
    "total_accepted": 760,
    "total_staged": 23,
    "total_rejected": 14,
    "by_topic": { "Lighting": 89, "Noise": 67, ... }
  },
  "personal": {
    "submitted": 8,
    "accepted": 5,
    "staged": 2,
    "rejected": 1
  }
}
```

---

## 6. Success Conditions

These are testable acceptance criteria for the module.

| ID | Condition | Verification |
|----|-----------|-------------|
| SC-AS-1 | A PDF uploaded via `/api/articles/submit` lands in `quarantine/` within 2 seconds | Automated test: submit PDF, check filesystem |
| SC-AS-2 | Magic-byte validation rejects non-PDF files (e.g., renamed `.exe`) | Automated test: submit JPEG renamed to .pdf |
| SC-AS-3 | Duplicate detection catches exact hash matches | Automated test: submit same PDF twice |
| SC-AS-4 | Duplicate detection catches DOI matches across different PDF files | Automated test: submit two PDFs with same DOI |
| SC-AS-5 | Anonymous submission succeeds without auth token | Automated test: POST without Authorization header |
| SC-AS-6 | Student submission is attributed to user when token provided | Automated test: submit with Bearer token, verify submitter_id |
| SC-AS-7 | Instructor can accept article; PDF moves to `pdf_collection/` | Automated test: submit → review(accept) → check filesystem |
| SC-AS-8 | Instructor can reject article; PDF deleted, audit stub retained | Automated test: submit → review(reject) → check quarantine empty, rejected/ has stub |
| SC-AS-9 | `/api/articles/my-submissions` returns correct counts per status | Automated test: submit 3, accept 1, reject 1 → verify counts |
| SC-AS-10 | Sidecar `.json` in `pdf_collection/` contains DOI, title, authors, year | Automated test: accept article → read sidecar → validate fields |
| SC-AS-11 | Files >100 MB are rejected at upload | Automated test: submit oversized payload |
| SC-AS-12 | Audit log records every state transition | Automated test: full lifecycle → count audit rows |

---

## 7. Security Requirements

Per `ARTICLE_INTAKE_POLICY_2026-03-24.md`:

1. **Magic-byte validation**: First 5 bytes must be `%PDF-`. Reject anything else regardless of file extension.
2. **Size limit**: 100 MB per file, 500 MB per batch submission.
3. **Quarantine-first**: No uploaded file touches `pdf_collection/` until explicitly promoted by instructor review.
4. **Hash on receipt**: SHA-256 computed immediately; stored in database for deduplication and integrity verification.
5. **Prompt deletion**: Rejected PDFs are deleted from quarantine within the review endpoint call. Only an audit stub (JSON metadata, no PDF content) is retained.
6. **No path traversal**: Uploaded filenames are sanitized (alphanumeric + hyphens only). The filesystem name is always `{article_id}.pdf`, never the original filename.
7. **Rate limiting**: Anonymous submissions limited to 10 per hour per IP. Authenticated submissions limited to 50 per hour.

---

## 8. Configuration

New environment variables (with defaults for local development):

```bash
# Storage
KA_STORAGE_ROOT=/mnt/ka_storage              # Production: 5TB mount
KA_QUARANTINE_DIR=$KA_STORAGE_ROOT/quarantine
KA_PDF_COLLECTION_DIR=$KA_STORAGE_ROOT/pdf_collection
KA_REJECTED_DIR=$KA_STORAGE_ROOT/rejected

# Limits
KA_MAX_FILE_SIZE_MB=100
KA_MAX_BATCH_SIZE_MB=500
KA_MAX_ANON_SUBMISSIONS_PER_HOUR=10
KA_MAX_AUTH_SUBMISSIONS_PER_HOUR=50

# Extraction pipeline integration
KA_WRITE_SIDECAR_JSON=true                   # Write metadata sidecar alongside promoted PDFs
KA_SIDECAR_FIELDS=doi,title,authors,year,journal,abstract,article_id,promoted_at
```

---

## 9. Integration Points

### 9.1 Frontend → Backend

`ka_contribute.html` and `ka_article_propose.html` must be updated to POST to `/api/articles/submit` instead of writing to `localStorage`. The `ka_article_collector.js` basket can remain as a client-side staging area, but the "Submit to ATLAS" action must trigger the server call.

### 9.2 Backend → Extraction Pipeline

Accepted PDFs in `pdf_collection/{topic}/` are in the format Article_Eater's `cmd_import_pdfs` expects. The sidecar JSON provides pre-extracted metadata so the pipeline can skip bibliographic parsing. The `article_id` field in the sidecar links back to the KA database for provenance tracking.

### 9.3 Backend → Student Dashboard

`/api/articles/my-submissions` provides the data for the student's contribution dashboard (counts by status, list of submissions with current state). The existing `ka_user_home.html` can query this endpoint to show progress toward article collection targets.

---

## 10. Migration Path

### Phase 1 (This sprint): Core endpoints
- `POST /api/articles/submit` (PDF + citation)
- `GET /api/articles/status/{id}`
- `POST /api/articles/check-duplicate`
- Database schema creation
- Quarantine storage

### Phase 2: Review workflow
- `GET /api/articles/pending-review`
- `POST /api/articles/{id}/review`
- PDF promotion to `pdf_collection/`
- Sidecar JSON generation

### Phase 3: Dashboard integration
- `GET /api/articles/my-submissions`
- `GET /api/articles/stats`
- Frontend wiring
- Student progress tracking

### Phase 4: Nightly automation
- Relevance scoring batch job
- Automatic metadata enrichment (CrossRef/DOI resolution)
- SQLite backup script
- Stale quarantine cleanup (>30 days without review → flag for attention)

---

## 11. Dependencies

| Dependency | Version | Purpose |
|-----------|---------|---------|
| FastAPI | ≥0.100 | Already in use |
| python-multipart | ≥0.0.6 | File upload parsing |
| aiofiles | ≥23.0 | Async file writes |
| hashlib | stdlib | SHA-256 computation |
| python-magic | ≥0.4.27 | Magic-byte validation (or fallback to manual check) |

---

## 12. Open Questions for David

1. **Relevance scoring**: Should the nightly job use a simple keyword-match heuristic, or should it call an LLM for relevance assessment? The policy says "asynchronous triage" but doesn't specify the method.
2. **DOI resolution service**: CrossRef API is free but rate-limited. Should we use it for metadata enrichment, or rely solely on what the PDF parser extracts?
3. **Track 2 special rules**: The AF integration contract mentions Track 2 students have stricter requirements (no orphan PDFs). Should the backend enforce this, or is it a frontend-only guideline?
4. **Batch citation file parsing**: The `.bib` and `.ris` parsers exist in Article_Eater (`ingest/citation_parser.py`). Should we import that code, or implement a minimal parser in the KA server?
