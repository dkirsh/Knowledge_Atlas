# T2 Task 1 — Completion Checklist

**Author:** Kaden Leung
**Date:** 2026-05-19
**Branch:** `track/2-staging/kaden-leung`
**PR:** https://github.com/dkirsh/Knowledge_Atlas/pull/9

A per-rubric-line audit. Every item is `DONE`, `PARTIAL`, or `DEFERRED` with a citation to the file or commit that satisfies it. `DEFERRED` items are explicitly tracked under contract §11.2 (FINAL-tier polish, not grader-blocking).

---

## Phase 1 — Diagnose

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 1.1 | Boxology diagram of contribute-page data flow (current state) | DONE | `160sp/contracts/Track_2_Context.md` §"Part 1 — The Web Form" + box diagram around line 117-168 |
| 1.2 | Boxology diagram of classifier internals | DONE | `160sp/contracts/Track_2_Context.md` §"Classifier System" + box diagram lines 277-395 |
| 1.3 | Gap statement (one paragraph: what exists, what's missing, what to build) | DONE | `Track_2_Context.md` §"Integration Gap Statement" line 399-401 |
| 1.4 | Addendum after re-reading code (intellectual honesty) | DONE | `Track_2_Context.md` lines 405-413 documenting two stale claims corrected |

---

## Phase 2 — Spec (Classifier Integration Contract)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 2.1 | Inputs section (PDF, citation, both) | DONE | Contract §2 |
| 2.2 | Processing pipeline specified | DONE | Contract §3 (post-merge response shape) + §4 (storage rules) |
| 2.3 | Outputs on the page specified per verdict | DONE | Contract §5 (invariants I-3, I-9, I-10, I-11 on UI behavior) |
| 2.4 | Storage rules per status (accept/edge_case/reject/bad_file/duplicate) | DONE | Contract §3.3 (decision tree) + §4.0 (column enumeration) |
| 2.5 | Duplicate check before any INSERT | DONE | Contract I-12 + §3.3 Branch D |
| 2.6 | At least 3 specific test cases with expected outcomes | DONE | Contract §8 — 8 test cases (TC-1 through TC-8) |
| 2.7 | Concrete storage paths in contract | DONE | Contract §4.0 + I-3 (quarantine path scheme) |
| 2.8 | Concrete database column values | DONE | Contract §4.0 column enumeration table |
| 2.9 | Lifecycle status enum specified | DONE | Contract §3.1 schema `status` enum + §4 routing decision tree |
| 2.10 | Invariants enumerated (rules that must always hold) | DONE | Contract §5 — 14 invariants (I-1, I-2a, I-2b, I-3 through I-13) |
| 2.11 | Thresholds enumerated (acceptance bars) | DONE | Contract §6 — 12 thresholds (T-1 through T-12) with derivation procedure §6.1 |
| 2.12 | Failure modes documented | DONE | Contract §7 |
| 2.13 | Open verification gaps acknowledged honestly | DONE | Contract §10 — 7 gaps, each tagged with grader-relevance |
| 2.14 | JSON Schema for response body | DONE | `160sp/contracts/schemas/classifier_response.json` (194 lines) + legacy schema at `classifier_response.legacy.json` |

---

## Phase 3 — Fix (working code + verification)

### Code

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 3.1 | Backend handler calls the classifier | DONE | `ka_article_endpoints.py:2043` calls `_get_shared_article_classifier().classify(...)` |
| 3.2 | Classifier integration via existing `_classify_article_payload` wrapper | DONE | `ka_article_endpoints.py:2028` (helper) called from `submit_articles` |
| 3.3 | Routing function with documented decision tree | DONE | `ka_article_endpoints.py:722` `_route_classifier_verdict()` — 5 routing steps + constants |
| 3.4 | Frontend posts to real endpoint via `fetch()` | DONE | `ka_contribute_public.html:324` `await fetch(apiBase + "/api/articles/submit", ...)` |
| 3.5 | Frontend uses FormData (real PDF bytes, not filename) | DONE | `ka_contribute_public.html:312-320` `FormData` construction + `chosenFiles.forEach(f => fd.append("files", f, f.name))` |
| 3.6 | Storage: ACCEPT writes file + DB row + audit log | DONE | `ka_article_endpoints.py:978-1027` (file write) + INSERT + `_write_audit` |
| 3.7 | Storage: REJECT / bad_file / duplicate writes DB row but NO file | DONE | `ka_article_endpoints.py:986-994` (rejected_bad_file path); `ka_article_endpoints.py:1095-1145` (duplicate_existing path) — both INSERT without `quarantine_path` |
| 3.8 | LocalStorage dead-end removed (invariant I-9) | DONE | Verified zero `localStorage.setItem("ka.public_suggestions"` matches in `ka_contribute_public.html` |
| 3.9 | XSS-safe rendering of classifier outputs | DONE | `ka_contribute_public.html:234-296` uses only `textContent` and `createElement`, no `innerHTML` |
| 3.10 | Multi-file batch supported (rubric Q6) | DONE | `ka_contribute_public.html:312-320`: `chosenFiles[]` array; multiple `fd.append("files", ...)` calls |
| 3.11 | Results accumulate across submissions in one page session | DONE | `ka_contribute_public.html:240-258`: prior content kept; `<hr>` and `<h3>Submission #N · timestamp</h3>` separators added |
| 3.12 | Atomic ID generation (race-free) | DONE | `ka_article_endpoints.py:332-365` `_next_id()` uses `UPDATE id_sequences SET counter = counter + 1 RETURNING counter` |
| 3.13 | Retry-on-IntegrityError on INSERT | DONE | `ka_article_endpoints.py:1030-1040` |
| 3.14 | Off-topic detection at routing layer (Phase-4 fix) | DONE | `ka_article_endpoints.py:719` `_OFF_TOPIC_PRIMARY_TOPIC_THRESHOLD = 0.40`; routing at line 752 |
| 3.15 | `next_action` override for human-review cases (Q4 fix) | DONE | `ka_article_endpoints.py:705-718` `_NEXT_ACTIONS_NEEDING_REVIEW` frozenset; routing at line 760 |
| 3.16 | Defensive disk-write error handling | DONE | `ka_article_endpoints.py:980-994` `try/except OSError` on `month_dir.mkdir` and `quarantine_path.write_bytes` |
| 3.17 | DB PRAGMAs set at startup | DONE | `ka_auth_server.py:227-231` — WAL + foreign_keys + busy_timeout |

### Verification log (rubric requires this)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 3.18 | Q1 asked + answered (PDF save path) | DONE | `160sp/verification_log.md` §Q1 |
| 3.19 | Q2 asked + answered (classifier evidence object) | DONE | `verification_log.md` §Q2 |
| 3.20 | Q3 asked + answered (database writes + PK collision) | DONE | `verification_log.md` §Q3 |
| 3.21 | Q4 asked + answered (next_action handling) | DONE | `verification_log.md` §Q4 |
| 3.22 | Q5 asked + answered (accept vs edge_case distinguishability) | DONE | `verification_log.md` §Q5 |
| 3.23 | Q6 asked + answered (multi-file session) | DONE | `verification_log.md` §Q6 |
| 3.24 | ≥ 2 of 6 verification questions surface real bugs | DONE | 15 of 15 bugs surfaced (all 6 questions); 14 fixed, 1 declined by design |

---

## Phase 4 — Prove (validation)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 4.1 | ≥ 3 of 4 test papers produce correct results | DONE | `160sp/validation_matrix.md` — **4/4 PASS** (T1 on-topic, T2 off-topic, T3 edge-case, T4 citation-only) |
| 4.2 | Validation matrix (input / expected / actual / stored / DB / PASS) | DONE | `validation_matrix.md` main matrix |
| 4.3 | Storage proof — terminal output showing files exist and DB has rows | DONE | `validation_matrix.md` §"Final state" + §"Phase C — Cross-test invariants" with sqlite outputs |
| 4.4 | Per-test response JSON captured | DONE | `validation_T1_response.json` through `validation_T4_response.json` |
| 4.5 | Diagnosis of failures (spec bug vs implementation bug) | DONE | `validation_matrix.md` §D1, D2, D3, D4 — full triage |
| 4.6 | Off-topic detection (Phase-4 fix) end-to-end verified | DONE | Test 2 PASS after fix; routing reason `off_topic:edge_case_with_weak_topic_match_0.26_below_0.4` |
| 4.7 | Cross-test invariants (grader auto-tests 6, 7, 8, 9) pass | DONE | `validation_matrix.md` §"Phase C" — all PASS with SQL output |

### Supplementary (beyond-rubric)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 4.8 | TC-3 from contract §8 (bad PDF magic bytes) | DONE | `validation_matrix.md` §"Supplementary contract validation"; `validation_TC3_response.json` |
| 4.9 | TC-4 from contract §8 (SHA-256 duplicate) | DONE | Same matrix + `validation_TC4_response.json`; KA-ART-000006 → KA-ART-000001 |
| 4.10 | TC-5 from contract §8 (DOI duplicate, different bytes) | DONE | Supplementary matrix + `validation_TC5_first_response.json` + `validation_TC5_second_response.json` |
| 4.11 | TC-8 from contract §8 (per-item independence in mixed batch) | DONE | Supplementary matrix + `validation_TC8_response.json`; 1 valid + 1 bad + 1 dup all handled independently |
| 4.12 | 20-PDF expanded validation against the live endpoint | DONE | `validation_matrix.md` §"Expanded validation — 20 additional papers"; KA-ART-000013 through KA-ART-000032 |
| 4.13 | Every routing branch in `_route_classifier_verdict` exercised at least once | DONE | 20-PDF run hit all branches (off-topic detection, next_action override, reject, edge_case, accept with confidence threshold) |

### Optional contract §11.2 polish items (DEFERRED — not grader-blocking)

| # | Item | Status | Note |
|---|------|--------|------|
| 4.14 | TC-6 frontend network-failure unit test (vitest/jsdom) | DEFERRED | §11.2 polish. Code path reviewable at `ka_contribute_public.html:308-337` (try/catch + finally that re-enables submit) |
| 4.15 | Working validator script (replace skeleton with full Layer A + Layer B harness) | DEFERRED | §11.2 polish. `tests/validate_classifier_integration.py` is currently a skeleton; the validation matrix + grader pre-run already cover the same evidence |
| 4.16 | `schemas/baseline.json` for thresholds T-1, T-2, T-8 | DEFERRED | §11.2 polish per contract §6.1 |

---

## Phase 5 — Submission artifacts

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 5.1 | File manifest with one-line purpose per file | DONE | `160sp/MANIFEST.md` |
| 5.2 | `git diff --name-only origin/master..HEAD` output included | DONE | `MANIFEST.md` §"Files changed vs origin/master" |
| 5.3 | Storage proof (sqlite query output) | DONE | `MANIFEST.md` §"Storage proof" — full SQL + output for `articles`, `audit_log`, quarantine dir listing |
| 5.4 | PR body draft | DONE | `160sp/PR_BODY.md` — structured to rubric headings |
| 5.5 | PR opened against `dkirsh/Knowledge_Atlas:master` | DONE | https://github.com/dkirsh/Knowledge_Atlas/pull/9 |
| 5.6 | Branch rebased onto current origin/master (no spurious deletions) | DONE | Confirmed in earlier audit — branch tip is on top of `7fb7539`; diff shows only added/modified files, no Track 2/3 deletions |
| 5.7 | Commit emails use GitHub noreply alias (no private email exposure) | DONE | All 30 commits use `kaden-leung@users.noreply.github.com` (rewritten during submission) |

---

## Grader auto-tests (`160sp/rubrics/t2/t2_task1_grader.py --auto-only`)

| # | Test | Weight | Status |
|---|------|--------|--------|
| G-1 | Classifier integration (`AdaptiveClassifierSubsystem` + `.classify(` in `ka_article_endpoints.py`) | critical | PASS |
| G-2 | Duplicate detection logic (`duplicate` OR `check_duplicate` OR `pdf_hash` substring) | important | PASS |
| G-3 | Contribute page modified (results keyword + `fetch(`) | critical | PASS |
| G-4 | Corrupt PDF handling (`%PDF` OR `validate`) | critical | PASS |
| G-5 | DB field completeness (0 rows with `status IS NULL OR created_at IS NULL`) | important | PASS |
| G-6 | Audit log presence (0 orphan articles) | minor | PASS |
| G-7 | Storage path correctness (rejected → NULL quarantine; received/staged/validated → non-NULL) | critical | PASS |
| G-8 | Edge-case distinguishability (≥ 2 distinct statuses or relevance scores) | important | PASS |
| **Weighted total** | **15 / 15** | | **8 / 8** |

Latest grader run logged in `160sp/rubrics/t2/GRADE_REPORT.md`.

---

## Audit-pass code-quality items

| # | Item | Status | Commit |
|---|------|--------|--------|
| A.1 | Off-topic detection threshold (Phase-4 fix) | DONE | `4dd9866` |
| A.2 | Primary-topic confidence clamp to [0, 1] | DONE | `4dd9866` |
| A.3 | `id_sequences` atomic counter (race condition fix) | DONE | `00f8e06` |
| A.4 | Retry-on-IntegrityError around INSERT | DONE | `1cabb0a` |
| A.5 | OSError defensive wrap on disk write | DONE | `3adeeb8` |
| A.6 | Naming consistency: audit-action matches status; `routing_reason` JSON key | DONE | `4aad484` |
| A.7 | Title extraction heuristic | DONE | `b743a5d` |
| A.8 | Abstract extraction handles multi-line | DONE | `06d1dfd` |
| A.9 | `paper_id` propagated to ClassificationEvidence | DONE | `a2b2ef4` |
| A.10 | `next_action` override in router (Q4 fix) | DONE | `ed20ad3` |
| A.11 | Classifier outputs persisted into `validation_notes` (Q5 fix) | DONE | `08edb41` |
| A.12 | Multi-file batch + accumulating results (Q6 fix) | DONE | `a6ca4a5` |

---

## Known limitations (kept honest, all out of grader scope)

| # | Limitation | Status | Note |
|---|---|---|------|
| L.1 | DOI extraction returns NULL for all 23 real PDFs in our fixture pool | KNOWN | Fixture limitation (DOI text format not detected by `_extract_doi_from_pdf` regex on our PDFs); TC-5 verified via constructed minimal-PDF fixtures with embedded DOI string |
| L.2 | Constitutions data is sparse (limited topic coverage in `atlas_shared.data.question_constitutions_starter.json`) | KNOWN | Classifier-side limitation; documented in `validation_matrix.md` §D1 — affects classification accuracy but NOT routing correctness |
| L.3 | Dedup probe + INSERT race window (S14) | DOCUMENTED | `160sp/contracts/SECURITY_REVIEW_2026-05-19.md` §S14 — retry-on-IntegrityError catches worst case; documented |
| L.4 | Large-upload memory pressure (S4) | DOCUMENTED | `SECURITY_REVIEW_2026-05-19.md` §S4 — FastAPI SpooledTemporaryFile bounds memory; production should add starlette `--limit-max-body` |

---

## Self-grade summary

Every rubric line is **DONE** or **DEFERRED** (with §11.2-polish justification). No grader-blocking items remain open.

**Auto-tests:** 8/8 PASS → 15/15 weighted
**Manual rubric (TA-scored):** R-1 through R-6 evidence shipped with citations

Total Phase-1 through Phase-5 deliverables in this PR: see `MANIFEST.md` for the file-by-file inventory.
