# Codex Handoff: Article Submission Module

**Date**: 2026-03-30
**From**: CW (Claude Code)
**To**: Codex (or any AI worker picking up frontend/integration work)
**Priority**: HIGH — this module must be wired before COGS 160 Week 2

---

## What Was Built

### 1. Specification & Contract
**File**: `docs/ARTICLE_SUBMISSION_MODULE_SPEC_2026-03-30.md`

Complete contract covering: database schema (3 new tables), 7 API endpoints, PDF storage layout, success conditions (SC-AS-1 through SC-AS-12), security requirements, and configuration variables.

### 2. Backend Code
**File**: `ka_article_endpoints.py` (new, ~500 lines)

A FastAPI `APIRouter` that gets imported by `ka_auth_server.py`. Provides:

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/articles/submit` | POST | Optional | Upload PDFs and/or citation text |
| `/api/articles/status/{id}` | GET | None | Check article status |
| `/api/articles/my-submissions` | GET | Required | Student's own submissions |
| `/api/articles/pending-review` | GET | Instructor | Articles awaiting review |
| `/api/articles/{id}/review` | POST | Instructor | Accept or reject staged article |
| `/api/articles/check-duplicate` | POST | None | Real-time duplicate probe |
| `/api/articles/stats` | GET | Optional | Corpus + personal statistics |

### 3. Server Integration
**File**: `ka_auth_server.py` (modified, 2 edits)

- Added `import ka_article_endpoints` block after the health endpoint
- Added `_init_article_tables()` call at startup
- Graceful degradation: if `ka_article_endpoints.py` is missing, server runs auth-only

---

## What Was NOT Built (Your Work)

### Frontend Wiring

The two intake pages currently write to `localStorage` only. They need to POST to `/api/articles/submit` instead.

**Files to modify**:

1. **`ka_contribute.html`**
   - The upload zone (drag-and-drop) needs to collect files into a `FormData` object
   - The "Submit" action must `fetch('/api/articles/submit', { method: 'POST', body: formData })`
   - If user is logged in (has JWT in `localStorage['ka_access_token']`), attach `Authorization: Bearer <token>` header
   - Show the response: how many staged, how many duplicates, how many rejected
   - Error handling: show validation errors (bad file, too large, etc.)

2. **`ka_article_propose.html`**
   - Same wiring but for batch mode: multiple files + citation text + citation file
   - The batch results table (Step 2) should populate from the `/api/articles/submit` response
   - The "Stage non-duplicates" button triggers the submit call
   - Individual item status pills (`.s-extracted`, `.s-duplicate`, `.s-staged`) map to response `status` fields

3. **`ka_article_collector.js`**
   - The "Submit to ATLAS →" link in the floating panel should trigger a server submission
   - Collect all basket items, package as citation text (one per line), POST to `/api/articles/submit`
   - Clear basket on successful submission

### Student Dashboard

**File**: `ka_user_home.html`

Add a "My Submissions" section that queries `/api/articles/my-submissions` and shows:
- Count badges: staged / accepted / rejected / duplicate
- List of recent submissions with status pills
- Link to each article's detail (could just show `article_id` + status for now)

### Instructor Review Interface

**New or existing page** (you choose):

The instructor needs a way to review staged articles. The endpoint `/api/articles/pending-review` returns them. The review action is `POST /api/articles/{id}/review` with `{ decision: "accept" | "reject", reason: "..." }`.

Minimum viable UI:
- Table of pending articles: title (or filename), DOI, submitter, date
- "Accept" and "Reject" buttons per row
- Reject requires a reason (dropdown or free text)
- On accept: show success message with promoted path
- On reject: show confirmation

---

## Database Schema (for reference)

Three new tables added to `data/ka_auth.db`:

```sql
articles            -- One row per submitted item (PDF or citation)
submission_batches  -- Groups items submitted together
audit_log           -- Immutable record of state transitions
```

Full schema is in `docs/ARTICLE_SUBMISSION_MODULE_SPEC_2026-03-30.md` §3.

---

## PDF Storage Layout

```
$KA_STORAGE_ROOT/
├── quarantine/{YYYY-MM}/{article_id}.pdf     # Uploaded, not yet reviewed
├── pdf_collection/{topic_slug}/{article_id}_{title}.pdf  # Accepted
│   └── {article_id}_{title}.json             # Sidecar metadata for extraction pipeline
└── rejected/{YYYY-MM}/{article_id}.json      # Metadata stub only (PDF deleted)
```

Default `KA_STORAGE_ROOT` for local dev: `data/storage/` (relative to repo root).
Production: `/mnt/ka_storage` on the university VM (5TB mount).

Set via environment variable `KA_STORAGE_ROOT`.

---

## How to Test

### Start the server
```bash
cd /path/to/Knowledge_Atlas
pip3 install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] python-multipart aiofiles --break-system-packages
python3 ka_auth_server.py
```

You should see:
```
[KA-AUTH] Article submission module loaded ✓
[KA-AUTH] Article tables initialized ✓
```

### Submit a test PDF via curl
```bash
curl -X POST http://localhost:8765/api/articles/submit \
  -F "files=@test.pdf" \
  -F "question_id=Q01" \
  -F "notes=Test submission"
```

### Submit citation text
```bash
curl -X POST http://localhost:8765/api/articles/submit \
  -F "citations=Boubekri, M. (2014). Impact of windows... 10.1016/j.jenvp.2014.02.003"
```

### Check duplicate
```bash
curl -X POST http://localhost:8765/api/articles/check-duplicate \
  -H "Content-Type: application/json" \
  -d '{"doi": "10.1016/j.jenvp.2014.02.003"}'
```

### Review as instructor
```bash
# Login first
TOKEN=$(curl -s -X POST http://localhost:8765/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"dkirsh@ucsd.edu","password":"atlas2026"}' | jq -r .access_token)

# List pending
curl -H "Authorization: Bearer $TOKEN" http://localhost:8765/api/articles/pending-review

# Accept
curl -X POST http://localhost:8765/api/articles/KA-ART-000001/review \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"decision": "accept", "topic_override": "Lighting"}'
```

### Interactive API docs
Open `http://localhost:8765/docs` — all new endpoints appear under the "articles" tag.

---

## Configuration Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KA_STORAGE_ROOT` | `data/storage/` | Root directory for all PDF storage |
| `KA_QUARANTINE_DIR` | `$ROOT/quarantine` | Where uploaded PDFs land initially |
| `KA_PDF_COLLECTION_DIR` | `$ROOT/pdf_collection` | Where accepted PDFs are promoted |
| `KA_REJECTED_DIR` | `$ROOT/rejected` | Where rejection stubs go |
| `KA_MAX_FILE_SIZE_MB` | 100 | Max single file size |
| `KA_MAX_BATCH_SIZE_MB` | 500 | Max total batch size |

---

## Dependencies Added

| Package | Purpose | Install |
|---------|---------|---------|
| `python-multipart` | Parse `multipart/form-data` (file uploads) | `pip3 install python-multipart` |
| `aiofiles` | Async file I/O (optional, for future async writes) | `pip3 install aiofiles` |

All other dependencies (`fastapi`, `uvicorn`, `python-jose`, `passlib`) are already required by the auth server.

---

## Integration with Extraction Pipeline

The extraction pipeline (Article_Eater) expects PDFs in a directory it can scan. When an article is accepted:

1. PDF moves from `quarantine/` to `pdf_collection/{topic}/`
2. A sidecar `.json` file is written next to the PDF with pre-extracted metadata
3. The sidecar contains: `article_id`, `doi`, `title`, `authors`, `year`, `journal`, `abstract`, `promoted_at`, `pdf_hash_sha256`
4. Article_Eater's `cmd_import_pdfs` or `cmd_inbox` can consume this directory

The backend does NOT run extraction. It only stages files for the pipeline to pick up.

---

## Existing Policy Documents

Read these if you need to understand the business rules:

- `docs/ARTICLE_INTAKE_POLICY_2026-03-24.md` — Intake states, security gates, audit rules
- `docs/ARTICLE_INTAKE_AF_INTEGRATION_CONTRACT_2026-03-24.md` — Adapter request/response objects, AF capabilities, identity model
- `docs/GUI_DATA_CONTRACTS_2026-03-24.md` — Frontend data shapes for all KA pages

---

## Files Changed in This Sprint

| File | Action | Description |
|------|--------|-------------|
| `ka_article_endpoints.py` | NEW | Article submission APIRouter (~500 LOC) |
| `ka_auth_server.py` | MODIFIED | Added router import + table init (2 small edits) |
| `docs/ARTICLE_SUBMISSION_MODULE_SPEC_2026-03-30.md` | NEW | Full contract/spec |
| `docs/CODEX_HANDOFF_ARTICLE_SUBMISSION_2026-03-30.md` | NEW | This document |

---

## Known Limitations & Future Work

1. **No metadata enrichment**: DOI resolution via CrossRef is not implemented. The server extracts DOI from PDF bytes but does not call external APIs. This is Phase 4 work.
2. **No relevance scoring**: The `relevance_score` column exists but is never populated. Nightly batch scoring is future work.
3. **Title duplicate detection is naive**: Uses substring containment, not Levenshtein distance. Good enough for Phase 1; improve if false positive rate is high.
4. **No citation file parsing**: `.bib`/`.ris` files are accepted as uploads but not parsed into individual citations. Article_Eater has `ingest/citation_parser.py` that could be imported for this.
5. **No rate limiting implemented**: The constants exist but no middleware enforces them. Add `slowapi` or similar if abuse is a concern.

---

## Questions for David (Flagged from Spec)

1. Should nightly relevance scoring use keyword-match or LLM-based assessment?
2. Should we use CrossRef API for DOI metadata enrichment?
3. Should Track 2 "no orphan PDF" rule be enforced server-side?
4. Should we import Article_Eater's citation parser or write a minimal one?
