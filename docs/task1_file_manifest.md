# Task 1 — File Manifest
**Author:** Dhruv Sood · **Date:** 2026-05-03

Generated from:
```bash
git diff --name-only $(git merge-base HEAD upstream/master)..HEAD
git status --short
```

| File | Change | What it does |
|---|---|---|
| `ka_contribute_public.html` | modified | Frontend — replaced the old stub `submitSuggestion()` with an async fetch POST to `/api/articles/suggest`, added a results-card panel below the form. The audit-pass commit replaced the original innerHTML template with safe DOM construction (textContent / createElement) to close an XSS hole. API base is read from `window.__KA_CONFIG__.apiBase` per the repo's frontend contract. Multiple submissions stack via `prepend()` so older results stay visible. |
| `ka_article_endpoints.py` | modified | Backend — added: `POST /api/articles/suggest` (the new public endpoint), `_suggest_db()` (DB connection helper for the suggest path; sets `journal_mode=WAL`, `busy_timeout=5000`, `foreign_keys=ON`), `_suggest_next_id()` (collision-resistant `KA-ART-<hex>` IDs, audit-pass replaced `COUNT(*)+1` race), `_suggest_check_dup()` (sha256 / DOI / fuzzy-title duplicate probe), `_extract_pdf_text()` (pdfplumber → latin-1 fallback), `_run_classifier_and_assess()` (calls `HeuristicArticleTypeClassifier` + `QuestionArticleRelevanceFilter` over every loaded `QuestionConstitution`). Endpoint body wrapped in `try / except (rollback) / finally (close)`. ACCEPT and EDGE_CASE rows persist to `articles` + write to `audit_log`; REJECT and rejected_bad_file return early. |
| `data/test_pdfs/test_ontopic_empirical.pdf` | new | Test fixture — on-topic empirical paper (nature × directed-attention RCT). Drives Test 1 + B1. |
| `data/test_pdfs/test_offtopic_ml.pdf` | new | Test fixture — off-topic ML paper (deep learning ImageNet). Drives Test 2 + B2. |
| `data/test_pdfs/test_edgecase_theory.pdf` | new | Test fixture — biophilic-design theoretical review (env hits but no outcome hits). Drives Test 3 + B3. |
| `data/test_pdfs/validate_task1.py` | new (rewritten in audit pass) | Two-layer validator. Layer A drives the classifier in-memory (6 checks). Layer B spins up the suggest endpoint with `KA_QUARANTINE_DIR` and `KA_WORKFLOW_DB` redirected to a tempdir, posts every test case via FastAPI `TestClient`, and asserts file-on-disk + DB-row + audit-row + verdict + edge-flag (20 checks). 26/26 PASS. |
| `docs/CLASSIFIER_INTEGRATION_CONTRACT_TASK1.md` | new | The Phase 2 contract — Inputs / Processing / Outputs / Storage rules / Success conditions / Test checklist. |
| `docs/SUBMISSION_TASK1.md` | new | The Phase 1–4 submission narrative — boxology diagrams, gap statement, verification log of 6 questions × surfaced bugs × fixes, validation table, storage proof, diagnosis notes, file manifest, self-grade. |
| `docs/task1_completion_checklist.md` | new (this audit pass) | Per-rubric-line DONE / PARTIAL / MISSING checklist. |
| `docs/task1_bug_review.md` | new (this audit pass) | Bugs found in audit pass + fixes (race condition, conn leak, busy_timeout, persistence, weak validator). |
| `docs/task1_security_review.md` | new (this audit pass) | Strict security pass — XSS (fixed), path traversal (not vulnerable), DoS (partial), SQL injection (not vulnerable), etc. |
| `docs/task1_validation_matrix.md` | new (this audit pass) | The 7-row test matrix with PASS results from `validate_task1.py`. |
| `docs/task1_file_manifest.md` | new (this audit pass) | THIS FILE. |
| `docs/task1_pr_summary.md` | new (this audit pass) | Updated PR body in plain student voice — supersedes the marketing-tone version in `PR_DRAFT_TASK1.md`. |
| `PR_DRAFT_TASK1.md` | new (earlier) | Original copy-pasteable PR body. Kept for traceability; `docs/task1_pr_summary.md` is now the canonical version. |
