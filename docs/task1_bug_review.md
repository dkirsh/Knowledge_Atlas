# Task 1 — Bug Review (audit pass)
**Author:** Dhruv Sood · **Date:** 2026-05-03

Bugs found while auditing my own submission against the rubric and the
GitHub Copilot AI review. Each entry has Before / Fix / File. All fixed in
the audit-pass commit.

---

### B1 — `_suggest_next_id` race condition (HIGH)

**Before**
```python
def _suggest_next_id(conn, prefix):
    seq = (conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0] or 0) + 1
    return f"{prefix}{seq:06d}"
```
Two concurrent submissions reading the same `COUNT(*)` mint the same
`article_id`. The second `INSERT` fails with a PK collision OR (worse, in
older SQLite versions) silently overwrites.

**Fix** — generate a random hex token and verify uniqueness before returning;
retry up to 8 times.
```python
candidate = f"{prefix}{secrets.token_hex(4).upper()}"
exists = conn.execute("SELECT 1 FROM articles WHERE article_id=? LIMIT 1", (candidate,)).fetchone()
```

**File** — `ka_article_endpoints.py:2880`

---

### B2 — Connection leak on exception (MEDIUM)

**Before** — `conn = _suggest_db()` … `conn.close()` only at the bottom of the
function. Any exception in the body (validation, classifier, INSERT) leaves
the connection open and partial inserts uncommitted in the caller's view.

**Fix** — wrapped the body in `try / except Exception: rollback / finally:
close`. Rollback ensures partial commits don't survive a mid-flight failure.

**File** — `ka_article_endpoints.py:3015–3201`

---

### B3 — `database is locked` under concurrent submissions (LOW–MED)

**Before** — `_suggest_db()` only set `PRAGMA journal_mode=WAL`. Without
`busy_timeout`, two concurrent writers can throw "database is locked" on the
loser thread instead of waiting briefly.

**Fix** — added `PRAGMA busy_timeout=5000` and `PRAGMA foreign_keys=ON`.

**File** — `ka_article_endpoints.py:2803`

---

### B4 — `email` and `citation` form fields not persisted on PDF path (LOW)

**Before** — when a contributor submitted a PDF together with their email
and a citation hint, the PDF branch only persisted `why_it_matters` (in
`submitter_notes`). The email and citation hint were silently discarded;
reviewer couldn't follow up.

**Fix** — on the PDF path, `validation_notes` JSON now includes
`contact_email` and `submitter_citation_hint` (truncated to 500 chars). On
the citation path, `contact_email` is also stored. The citation branch is
skipped when a PDF is present so we don't accidentally insert two rows for
the same paper.

**File** — `ka_article_endpoints.py:3081–3104`

---

### B5 — Validator claimed "checks storage" but only ran the classifier (HIGH)

**Before** — `data/test_pdfs/validate_task1.py` had a docstring of "runs all 4
test cases and checks storage", but the script only invoked
`HeuristicArticleTypeClassifier` and `QuestionArticleRelevanceFilter` in
memory. It never POSTed to the endpoint, never wrote a file, never
inspected `articles` or `audit_log`. The Phase 4 storage-proof rubric line
was effectively unproven.

**Fix** — split into two layers. Layer A is the original cheap
classifier-only check (still useful when FastAPI isn't installed). Layer B
spins up the suggest endpoint with `KA_QUARANTINE_DIR` and `KA_WORKFLOW_DB`
pointed at a tempdir, posts every test case via FastAPI's `TestClient`, and
asserts:

| Assertion | Test |
|---|---|
| ACCEPT response → `articles` row exists with `status='staged_pending_review'` | B1 |
| ACCEPT → `validation_notes.edge_flag = 'edge_case:false'` | B1 |
| ACCEPT → quarantine PDF on disk with matching bytes | B1 |
| ACCEPT → `audit_log` row exists | B1 |
| REJECT → no DB insert, no file written | B2 |
| EDGE_CASE → DB row with `edge_flag = 'edge_case:true'` (distinguishable) | B3 |
| Citation-only → exactly one item produced | B4 |
| Same PDF twice → 2nd verdict='duplicate' | B5 |
| 3 distinct submissions → 3 distinct DB rows | B6 |
| Bad PDF (non-PDF magic) → `rejected_bad_file`, no insert | B7 |

26/26 PASS.

**File** — `data/test_pdfs/validate_task1.py`

---

### B6 — Initial validator B6 caught a *real* fuzzy-dedup boundary case (NIT)

**Before** — first version of B6 minted 5 PDFs whose titles all started with
the same on-topic phrase, expecting 5 inserts. Got 0 inserts because the
fuzzy-title matcher correctly identified them as near-duplicates.

**Fix** — rewrote B6 to use 3 truly-distinct titles (urban parks / forest
bathing / daylight). 3 inserts. Test now confirms both:
(a) the API returns 3 items per submission (no UI-overwrite-style merge),
(b) 3 distinct rows land in `articles`.

The original "duplicate detection works" intent is now covered by the more
explicit B5 (re-submit same PDF → duplicate verdict).

**File** — `data/test_pdfs/validate_task1.py`
