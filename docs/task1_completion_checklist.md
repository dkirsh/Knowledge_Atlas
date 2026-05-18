# Task 1 — Completion Checklist (audit pass)
**Author:** Dhruv Sood · **Last updated:** 2026-05-03

A brutally honest pass/partial/missing check on every rubric line. After the
audit pass, every item below is **DONE** unless explicitly marked partial.

## Phase 1 — Diagnose
- [x] **DONE** — Boxology diagram of contribute page data flow (`docs/SUBMISSION_TASK1.md` §1A)
- [x] **DONE** — Boxology diagram of classifier internals (`docs/SUBMISSION_TASK1.md` §1B)
- [x] **DONE** — Gap statement (`docs/SUBMISSION_TASK1.md` §2): X / Y / Z / W form

## Phase 2 — Spec (Classifier Integration Contract)
- [x] **DONE** — Inputs (PDF, citation, both) — `docs/CLASSIFIER_INTEGRATION_CONTRACT_TASK1.md` §1
- [x] **DONE** — Processing (evidence object, classifier call) — §2
- [x] **DONE** — Outputs on the page (verdict, type, topic, confidence) — §2 step 7
- [x] **DONE** — Storage rules per verdict (accept / edge_case / reject) — §2 step 6 + §3
- [x] **DONE** — Duplicate check before storage — §2 step 2
- [x] **DONE** — At least 3 specific test cases — §4
- [x] **DONE** — Concrete storage paths — §3
- [x] **DONE** — Concrete database column values — §3
- [x] **DONE** — Lifecycle stage/status (`status='staged_pending_review'`) — §3

## Phase 3 — Fix
- [x] **DONE** — Backend endpoint receives form, runs classifier, returns JSON — `ka_article_endpoints.py:3008`
- [x] **DONE** — Frontend posts to real endpoint — `ka_contribute_public.html:258`
- [x] **DONE** — Storage logic for ACCEPT/EDGE_CASE — file + DB row + audit log
- [x] **DONE** — REJECT / DUPLICATE / rejected_bad_file return early — no file write, no INSERT
- [x] **DONE** — Verification log (6 questions × surfaced bugs × fixes) — `docs/SUBMISSION_TASK1.md` §4

## Phase 4 — Prove
- [x] **DONE** — At least 4 test cases (now 7 + 6 in two layers) — `data/test_pdfs/validate_task1.py`
- [x] **DONE** — Validation matrix with input / expected / actual / stored? — `docs/task1_validation_matrix.md`
- [x] **DONE** — Storage proof — Layer B asserts file on disk + DB row + audit_log
- [x] **DONE** — Diagnosis notes (spec bug vs impl bug) — `docs/SUBMISSION_TASK1.md` §7

## Files & submission
- [x] **DONE** — File manifest — `docs/task1_file_manifest.md`
- [x] **DONE** — PR summary — `docs/task1_pr_summary.md` (and `PR_DRAFT_TASK1.md`)
- [x] **DONE** — PR opened on GitHub against `dkirsh:master`

## Audit-pass code-quality items
- [x] **DONE** — XSS in result-card rendering fixed (was: raw `innerHTML` interpolation of user-controlled `filename`/`citation`)
- [x] **DONE** — `_suggest_next_id` race condition fixed (was: `COUNT(*)+1`; now `secrets.token_hex(4)`)
- [x] **DONE** — Connection lifecycle wrapped in try/except/finally with rollback on exception
- [x] **DONE** — `PRAGMA busy_timeout=5000` and `PRAGMA foreign_keys=ON` set
- [x] **DONE** — `email` and full citation hint persisted into `validation_notes` JSON for PDF path
- [x] **DONE** — Frontend reads API base from `window.__KA_CONFIG__.apiBase` per repo contract
- [x] **DONE** — Validator no longer claims "checks storage" without doing so — Layer B proves it

## Known limitations (kept honest)
- [ ] **PARTIAL** — `_suggest_db()` opens a separate DB rather than reusing the injected `_get_db()`. This is per-design (the suggest endpoint is public/anonymous; `_get_db()` requires auth wiring). Documented; not changed in audit pass to avoid breaking existing A0-student endpoints.
- [ ] **PARTIAL** — Title fuzzy-match (`_titles_match` with `max_word_distance=1`) is O(N) over the articles table. Fine for the course corpus (< 1k rows). For production, would need a normalized-title index or FTS. Not changed in audit pass.
- [ ] **PARTIAL** — Whole upload buffered into memory before validation (`await file.read()`). FastAPI streams to a SpooledTemporaryFile by default so memory pressure is bounded, but a starlette config could add an explicit max-body-size. Not changed in audit pass.
- [ ] **PARTIAL** — Only one constitution (`SQ-ART-001 Nature & Attention`) ships with `atlas_shared`. Test 3 (edge case) is correctly classified by my code given that data limit; if more constitutions land, the same code yields ACCEPT for more papers without code changes.
