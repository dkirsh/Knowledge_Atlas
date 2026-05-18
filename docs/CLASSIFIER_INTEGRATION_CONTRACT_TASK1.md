# Classifier Integration Contract — Task 1
**Author:** Dhruv Sood
**Date:** 2026-05-03
**Repo:** Knowledge_Atlas
**Task:** Track 2 · Task 1 — Fix the Contribute Page

---

## 0. Substitutions & Limitations (read first)

| Topic | Canonical | Substitute / actual | Justification |
|---|---|---|---|
| Classifier import path | `atlas_shared.classifier_system.AdaptiveClassifierSubsystem` | the same — loaded by `_load_classifier_backend()` at module import (`ka_article_endpoints.py:154`). If `atlas_shared.classifier_system` is unavailable, a same-API local fallback `LocalAdaptiveClassifierSubsystem` is used (line 62). | Both code paths build a `ClassificationEvidence` and call `.classify(evidence, allow_surface_creation=False)`. The endpoint path is identical regardless of which class is live; `evidence_stage` and `next_action` come back in both cases. |
| DB connection | injected `_get_db()` (auth-context) | separate `_suggest_db()` opening `KA_WORKFLOW_DB` (env-overridable) | The `/suggest` endpoint is public/anonymous; `_get_db()` requires an auth context. `_suggest_db()` enables `WAL` + `busy_timeout=5000` + `foreign_keys=ON` for the same hygiene. |
| Question constitutions | full catalogue | only `SQ-ART-001 Nature & Attention` ships with `atlas_shared` in `question_constitutions_starter.json` | Data limitation; not a code limitation. Adding more constitutions changes verdicts without touching the endpoint. |
| `article_id` minting | `_next_id()` (the rest of the file) | `_suggest_next_id()` — `KA-ART-<8 hex>` via `secrets.token_hex(4).upper()` with uniqueness check + retry | Original `COUNT(*)+1` pattern races under concurrent submissions. Random-token-with-check eliminates the race without requiring a `SEQUENCE` table. |

Manual artifacts required: **none** — `data/test_pdfs/validate_task1.py` proves every storage assertion in-process.

---

## 1. Inputs

| Source | Field | Format | Required |
|--------|-------|--------|----------|
| Multipart form upload | `file` | PDF binary, ≤ 100 MB | Optional (at least one of file or citation) |
| Form field | `citation` | Free-text APA/DOI/title string, newline-separated | Optional |
| Form field | `why_it_matters` | Free text | Optional |
| Form field | `email` | Email address | Optional |

At least one of `file` or `citation` must be present; otherwise the endpoint returns HTTP 400.

---

## 2. Processing

### Step 1 — Validate the PDF (if present)
- Check magic bytes (`%PDF-`). If invalid → mark `rejected_bad_file`, skip all further steps for this file.
- Check file size ≤ 100 MB. If over → reject.
- Compute SHA-256 hash.

### Step 2 — Duplicate probe (before any storage)
Run `_check_duplicate()` in `ka_article_endpoints.py`:
- SHA-256 hash match → definitive duplicate, do not store.
- DOI match (extracted from first 5 KB of PDF) → definitive duplicate, do not store.
- Fuzzy title match (≤ 1 word edit distance) → probable duplicate, do not store.

Any duplicate match sets `verdict = "duplicate"` and bypasses classification and storage.

### Step 3 — Extract text for classification
Attempt to read title + abstract from the PDF:
- Use `pdfplumber` (if available) to extract the first page's text.
- Fall back to decoding the first 4 KB of raw PDF bytes as latin-1.
- For citation-only submissions, use the parsed title and authors from `_parse_citation_line()`.

### Step 4 — Classify article type
Build a `ClassificationEvidence(paper_id, title, abstract, keywords, first_page_text)` and call `AdaptiveClassifierSubsystem.classify(evidence, allow_surface_creation=False)` via the existing `_classify_article_payload()` wrapper at `ka_article_endpoints.py:1648`. The wrapper returns `{article_type, canonical_article_type, confidence, signals, source, evidence_stage, next_action}`. The classifier resolves to `atlas_shared.classifier_system.AdaptiveClassifierSubsystem` when importable, else the local same-API fallback in `_build_local_classifier_backend()`.

The endpoint propagates `next_action` and `evidence_stage` to the response. When `next_action == "need_abstract_or_keywords"` AND no abstract was supplied, the verdict is overridden to `needs_more_info` and storage is skipped — the user is told we can't decide yet, rather than silently flagged as edge_case.

### Step 5 — Assess relevance
Load `QuestionConstitution` objects from  
`atlas_shared/src/atlas_shared/data/question_constitutions_starter.json`.  
Call `QuestionArticleRelevanceFilter().assess(constitution, article)` for each.  
Take the constitution with the highest-confidence non-reject verdict.  
Result: `RelevanceAssessment {verdict, confidence, question_id, topic, environment_hits, outcome_hits}`.

### Step 6 — Decide verdict and storage tier
| Condition | Verdict | Store? | Status |
|-----------|---------|--------|--------|
| Best assessment = `accept`, confidence ≥ 0.55 | `accept` | Yes — quarantine dir + DB row | `staged_pending_review` |
| Best assessment = `edge_case`, OR accept with confidence < 0.55 | `edge_case` | Yes — quarantine dir + DB row with `validation_notes` flag `"edge_case:true"` | `staged_pending_review` |
| All constitutions return `reject` | `reject` | No storage | — |
| `AdaptiveClassifierSubsystem.classify()` returned `next_action='need_abstract_or_keywords'` AND no abstract was supplied | `needs_more_info` | No storage | `needs_more_info` |
| Duplicate match | `duplicate` | No new storage | — |
| Bad PDF | `rejected_bad_file` | No storage | — |

REJECT papers are returned in the API response for display but never written to disk or DB.

### Step 7 — Return response
JSON response per submission item:
```json
{
  "filename": "paper.pdf",
  "verdict": "accept | edge_case | reject | duplicate | rejected_bad_file | needs_more_info",
  "article_type": "empirical_research",
  "article_type_confidence": 0.78,
  "next_action": "accept | review_if_uncertain | need_abstract_or_keywords",
  "evidence_stage": "heuristic | structured",
  "topic": "Nature and Attention",
  "question_id": "SQ-ART-001",
  "topic_confidence": 0.90,
  "environment_hits": ["nature", "green space"],
  "outcome_hits": ["attention", "directed attention"],
  "reasons": ["matches environment side: nature", "matches outcome side: attention"],
  "article_id": "KA-ART-3D3A956E",
  "status": "staged_pending_review | needs_more_info | rejected_not_stored"
}
```

---

## 3. Outputs

### On the page
A results section (`<div id="__ka_results">`) below the form renders one card per submitted item showing:
- Verdict badge (green = accept, yellow = edge_case, red = reject/duplicate)
- Article type + confidence percentage
- Matched topic + question ID
- Environment and outcome term hits
- Classifier reasons

Results accumulate across submissions in the same session (new results append, old results stay visible).

### Storage (for ACCEPT and EDGE_CASE only)
- PDF binary written to `data/storage/quarantine/<YYYY-MM>/<article_id>.pdf`
- Row inserted into `articles` table in `data/ka_workflow.db` with:
  - `article_id`, `submission_id`, `input_mode = "pdf_single"`
  - `article_type`, `status = "staged_pending_review"`
  - `validation_notes` includes `"edge_case:true"` for EDGE_CASE items
  - `metadata_confidence` derived from whether DOI was extractable
- Audit row written to `audit_log`

---

## 4. Success Conditions

1. **Schema validity**: the `/api/articles/suggest` endpoint returns valid JSON matching the response format above for all four test-paper types.
2. **On-topic empirical PDF** → verdict = `accept`; row exists in DB; PDF on disk.
3. **Off-topic PDF** (ML paper) → verdict = `reject`; NO row in DB; NO file on disk.
4. **Edge-case PDF** (architectural theory, no empirical data) → verdict = `edge_case`; row in DB with `validation_notes` containing `"edge_case:true"`; PDF on disk.
5. **Citation-only submission** → verdict assigned (accept/edge_case/reject); for accept/edge_case a DB row is inserted with `input_mode = "citation_text"` and no PDF path.
6. **Duplicate submission** → any paper submitted twice returns `verdict = "duplicate"` on the second submission; no new DB row is created.
7. **Multi-submission session** → submitting 3 papers in one page session shows 3 result cards without any being overwritten.
8. **Classifier confidence** → `article_type_confidence` is always between 0.0 and 1.0.
9. **Results persist on refresh** — results section is reset on page load (not persisted across page refreshes; session-only).

---

## 5. Test Checklist

- [ ] On-topic empirical PDF → `accept`, PDF saved at quarantine path, DB row exists
- [ ] Off-topic PDF → `reject`, NO file in `data/storage/`, NO DB row
- [ ] Edge-case PDF (theory/review) → `edge_case`, DB row has `validation_notes` with `edge_case:true`
- [ ] Citation-only → endpoint handles, returns verdict, DB row for accept/edge_case
- [ ] Same PDF submitted twice → second call returns `duplicate`, no duplicate row
- [ ] Bad/non-PDF file → `rejected_bad_file`, no storage
- [ ] Multiple submissions in one session → all result cards visible simultaneously
- [ ] `article_type_confidence` in [0, 1] for every response
- [ ] `article_id` is absent from response for reject/duplicate/bad-file verdicts
