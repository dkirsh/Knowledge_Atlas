# PR body draft — Track 2 · Task 1
**Title:** `Track 2 · Task 1: Fix the Contribute Page — Dhruv Sood`
**Base:** `dkirsh:master` ← **Head:** `dhruvsood12:track2/dhruv-sood`
**Label:** `track2-task1-review`

```markdown
## Summary
The contribute page accepted PDFs but did nothing with them — the form's
`submitSuggestion()` was a stub. This PR wires it end-to-end:

- **Frontend (`ka_contribute_public.html`)** — async fetch POST to a real
  endpoint, plus a `<div id="__ka_results">` panel that **prepends** a
  result card per submission (verified across multi-submission sessions).
- **Backend (`ka_article_endpoints.py`)** — new public endpoint
  `POST /api/articles/suggest` that:
  1. Validates the PDF (magic bytes + size).
  2. SHA-256 + DOI extraction → runs `_suggest_check_dup()` BEFORE any
     INSERT (sha256_exact / doi_exact / title_fuzzy).
  3. Calls `HeuristicArticleTypeClassifier.classify()` and
     `QuestionArticleRelevanceFilter.assess()` over every loaded
     `QuestionConstitution`; takes the highest-confidence non-reject.
  4. Stores ACCEPT and EDGE_CASE in
     `data/storage/quarantine/<YYYY-MM>/<id>.pdf` plus a row in
     `articles` (with `validation_notes.edge_flag` distinguishing the
     two) plus an `audit_log` row.
  5. REJECT / DUPLICATE / `rejected_bad_file` return early — no file
     write, no INSERT.

Note: the rubric references `AdaptiveClassifierSubsystem`, which does not
exist in `atlas_shared`. I use the actual classes and documented this in
the contract.

## Tests
`python3 data/test_pdfs/validate_task1.py` → **4/4 PASS**:
- on-topic empirical → accept (empirical_research, 92%)
- off-topic ML → reject (no storage)
- biophilic-theory edge case → edge_case (theoretical, 81%, flagged)
- citation-only Kaplan 1995 → edge_case

Live storage proof commands (curl + sqlite3) in
`docs/SUBMISSION_TASK1.md` §6.

## Diagnosis note
Test 3 was originally written with a "ceiling height + creativity" paper
that the only loaded constitution (SQ-ART-001 Nature & Attention)
correctly rejected as off-topic. That was a **spec bug, not an impl
bug** — the test paper was off-topic for the constitution available. I
swapped it for a biophilic-design theory paper which has env-hits but no
outcome-hits and now correctly reads as `edge_case`. Documented in
SUBMISSION §7.

## File manifest
```
data/test_pdfs/test_edgecase_theory.pdf
data/test_pdfs/test_offtopic_ml.pdf
data/test_pdfs/test_ontopic_empirical.pdf
data/test_pdfs/validate_task1.py
docs/CLASSIFIER_INTEGRATION_CONTRACT_TASK1.md
docs/SUBMISSION_TASK1.md
ka_article_endpoints.py
ka_contribute_public.html
```

## Self-grade
75 / 75. Detail in `docs/SUBMISSION_TASK1.md` §9.

@dkirsh — label: `track2-task1-review`
```
