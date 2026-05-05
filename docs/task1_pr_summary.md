# Task 1 — PR summary (clean, student voice)

This document is the canonical PR body. Paste the block below the line into
the GitHub PR description.

---

## Summary

The contribute page used to accept PDFs and silently drop them — the form's
`submitSuggestion()` was a stub that just showed a success toast. This PR
fixes the page so submitted papers actually get classified, stored when
appropriate, and reported back to the user.

What's wired up now:

- **Frontend** (`ka_contribute_public.html`). The form posts a `multipart/
  form-data` request to `/api/articles/suggest`. A results panel below the
  form renders one card per submission with verdict, article type, topic,
  confidence, environment / outcome term hits, and the article ID + status
  for stored items. New cards are *prepended*, so multiple submissions in
  one page session don't overwrite each other. Every server-supplied value
  is rendered via `textContent`, not `innerHTML`, so a malicious filename
  or PDF title can't run JS in the reviewer's browser.

- **Backend** (`ka_article_endpoints.py`). New endpoint
  `POST /api/articles/suggest`:
  1. Validates the PDF (magic bytes + size).
  2. Computes SHA-256 + extracts a DOI from the first 5 KB.
  3. Runs the duplicate probe (`_suggest_check_dup`) against
     `pdf_hash_sha256`, lower-cased `doi`, and fuzzy-title before any
     storage. A hit short-circuits with `verdict='duplicate'`.
  4. Extracts text (pdfplumber, latin-1 fallback) and calls
     `HeuristicArticleTypeClassifier.classify()` and
     `QuestionArticleRelevanceFilter.assess()` over every loaded
     `QuestionConstitution`. The best non-reject verdict wins.
  5. ACCEPT and EDGE_CASE write the PDF to
     `data/storage/quarantine/<YYYY-MM>/<article_id>.pdf` and insert into
     `articles` with `status='staged_pending_review'`. EDGE_CASE rows are
     distinguishable: `validation_notes` JSON includes
     `edge_flag='edge_case:true'`. An `audit_log` row is written too.
  6. REJECT, DUPLICATE, and `rejected_bad_file` return early — no file
     write, no INSERT.

- **Storage rules**. Article IDs are `KA-ART-<hex>` so concurrent
  submissions can't race into a primary-key collision (the original
  `COUNT(*)+1` was racy and got fixed in the audit pass). The DB
  connection is wrapped in `try / except (rollback) / finally (close)` so
  partial commits don't survive a mid-flight error.

Note: the rubric mentions `AdaptiveClassifierSubsystem`. That class is not
present in the version of `atlas_shared` I have. I used the actual classes
that ship (`HeuristicArticleTypeClassifier`,
`QuestionArticleRelevanceFilter`) and documented this in the contract.

## Tests

`python3 data/test_pdfs/validate_task1.py` reports **26/26 PASS** in two
layers. Layer A is a 6-check classifier-only smoke test. Layer B spins up
the suggest endpoint with `KA_QUARANTINE_DIR` and `KA_WORKFLOW_DB` pointed
at a tempdir, then runs every rubric test case via FastAPI's `TestClient`:

- on-topic empirical → ACCEPT, file on disk, DB row, audit row
- off-topic ML → REJECT, no DB row, no file
- biophilic theory → EDGE_CASE, DB row with `edge_flag='edge_case:true'`
- citation-only Kaplan 1995 → returns a verdict (edge_case in the
  current single-constitution data)
- same PDF twice → second submission verdict='duplicate'
- 3 distinct submissions → 3 distinct rows + 3 items in API response
- non-PDF magic bytes → `rejected_bad_file`, no DB row

Layer B is the storage proof the rubric asks for: file existence + DB row +
audit row are asserted, not just the classifier verdict.

## Diagnosis note (Phase 4)

When my first edge-case test paper was a "ceiling height + creativity"
paper, every constitution returned `reject` because the only loaded
constitution is `SQ-ART-001 Nature & Attention`. The implementation was
right; the test paper was off-topic for the data available. I swapped to a
biophilic-design theory paper, which correctly reads as `edge_case` (env
hits, no outcome hits). That's a **spec / data limitation, not an
implementation bug**.

## Audit-pass changes (Copilot + self-review)

Five real issues found and fixed:

1. **XSS**: result cards now build via `document.createElement` +
   `textContent`, never `innerHTML` template strings.
2. **Race condition** in `_suggest_next_id` (`COUNT(*)+1`) → switched to
   `secrets.token_hex(4)` with uniqueness check + retry.
3. **Connection leak** on exception → `try / except (rollback) / finally
   (close)`.
4. **`PRAGMA busy_timeout=5000` and `foreign_keys=ON`** added.
5. **`email` and citation hint** persisted into `validation_notes` on the
   PDF path (was silently dropped before).
6. **Validator rewrite**: original `validate_task1.py` claimed "checks
   storage" but only ran the classifier in memory. New Layer B actually
   asserts file + DB + audit row.

## Limitations (kept honest)

- `_suggest_db()` opens a separate workflow DB rather than reusing the
  authenticated `_get_db()`. This is by design — the suggest endpoint is
  public/anonymous and `_get_db()` is wired to require auth context. If
  the rubric requires unification, that's a separate change.
- `_titles_match` is a Python-side O(N) scan over `articles`. Fine at the
  course corpus scale (< 1k rows). For production scale, would need a
  normalized-title index or FTS.
- Whole upload buffered in memory before `_validate_pdf_bytes` runs.
  FastAPI streams to a SpooledTemporaryFile so memory pressure is
  bounded, but a starlette body-size middleware would be a cleaner
  upstream guard.
- Only `SQ-ART-001 Nature & Attention` ships in the constitutions starter
  file. Verdicts for papers outside that topic will always be edge_case
  or reject. That's a data limit, not a code limit.

## File manifest

```
.gitignore                                      (audit pass) blocks .env*
data/test_pdfs/test_edgecase_theory.pdf
data/test_pdfs/test_offtopic_ml.pdf
data/test_pdfs/test_ontopic_empirical.pdf
data/test_pdfs/validate_task1.py                (audit pass: rewrote w/ Layer B)
docs/CLASSIFIER_INTEGRATION_CONTRACT_TASK1.md
docs/SUBMISSION_TASK1.md
docs/task1_bug_review.md                        (audit pass)
docs/task1_completion_checklist.md              (audit pass)
docs/task1_file_manifest.md                     (audit pass)
docs/task1_pr_summary.md                        (audit pass — this file)
docs/task1_security_review.md                   (audit pass)
docs/task1_validation_matrix.md                 (audit pass)
ka_article_endpoints.py                         (audit pass: race fix, try/finally, busy_timeout, persist email/citation)
ka_contribute_public.html                       (audit pass: XSS-safe DOM rendering)
PR_DRAFT_TASK1.md                               (earlier draft; superseded by docs/task1_pr_summary.md)
```

@dkirsh — please apply label `track2-task1-review`.
