# T2 Task 1 — File Manifest

**Assignment:** Track 2 / Task 1 — Fix the Contribute Page  
**Branch:** `track/2-staging/kaden-leung`  
**Author:** Kaden Leung (`kaden-leung`)  
**Fork:** `https://github.com/kaden-leung/Knowledge_Atlas`  
**PR target:** `dkirsh/Knowledge_Atlas:master`  
**HEAD at submission:** see `git log -1 --oneline`  
**Generated:** 2026-05-18

---

## Commands run to produce this manifest

```sh
# Changes vs upstream (canonical — shows what this PR adds/modifies)
git diff --name-only origin/master..HEAD

# Unstaged changes (clean working tree — output is empty; all changes committed)
git diff --name-only HEAD

# Untracked files (output is empty; all changes committed)
git status --short
```

`git diff --name-only HEAD` and `git status --short` both return empty because
every change is committed. The informative comparison is against `origin/master`.

**Pre-rebase note:** `git diff --name-status origin/master..HEAD` currently also
shows 8 files as `D` (deleted) under `160sp/track2/` and `160sp/track3/`. These
are NOT deletions introduced by this branch. Our branch was cut from merge-base
`ea942bb`; `origin/master` added those files in two subsequent commits
(`3e859dc Put Track 3 under 160sp`, `7fb7539 created track 2 folder`) that we
haven't yet rebased onto. After Phase F rebase the `D` entries disappear entirely.
`git log --diff-filter=D origin/master..HEAD -- 160sp/track2/ 160sp/track3/`
returns empty — confirmed no commit on this branch deletes any file.

---

## Files changed vs `origin/master` (post-rebase expected set)

### Modified (2)

| File | What changed |
|---|---|
| `ka_article_endpoints.py` | Core implementation: `_route_classifier_verdict` helper; classifier call inside `submit_articles`; `_classify_article_payload` extended with `verdict`, `topic`, `backend` fields; `paper_id` propagation; `id_sequences` table + atomic `_next_id`; retry-on-IntegrityError around articles INSERT; naming consistency (audit action = status, `routing_reason` JSON key); multi-line abstract extraction; stronger title heuristic; off-topic-detection threshold; score clamp to [0,1]; `contract_version` field in response |
| `ka_contribute_public.html` | Replace `localStorage` dead-end with `fetch()` POST to `/api/articles/submit`; inline results panel replacing the fake thank-you modal; multi-file support (`multiple` attribute + `chosenFiles[]`); accumulating results across sequential submissions |

### Added — deliverables (12)

| File | Phase | Rubric item | What it is |
|---|---|---|---|
| `160sp/contracts/Track_2_Context.md` | 1 | R-1 (15 pts) | Diagnosis: boxology of contribute page + classifier + gap statement; 2026-05-17 addendum correcting two stale claims |
| `160sp/contracts/CLASSIFIER_INTEGRATION_CONTRACT_2026-05-09.md` | 2 | R-2 (15 pts) | 959-line spec: 13 invariants, 12 thresholds, 8 test cases, done-definition split into grader-blocking §11.1 and FINAL-polish §11.2 |
| `160sp/contracts/schemas/classifier_response.json` | 2 | R-2 | JSON Schema v1.0 for `POST /api/articles/submit` response (post-merge); enforces `contract_version`, `classifier` block presence, field types |
| `160sp/contracts/schemas/classifier_response.legacy.json` | 2 | R-2 | Pre-merge response schema for validators that branch on `contract_version` |
| `160sp/verification_log.md` | 3 | R-3 (15 pts) | Q1–Q6 verification dialog: 15 bugs surfaced, 14 fixed, 1 declined by design; each fix includes a commit reference and end-to-end verification |
| `160sp/validation_matrix.md` | 4 | R-4 + R-5 (35 pts) | 4/4 PASS matrix; per-test detail; D1–D4 diagnosis notes classifying each outcome as SPEC/IMPL/FIXTURE |
| `160sp/validation_T1_response.json` | 4 | R-4 | Full HTTP response body for Test 1 (`Building_Environment.pdf` → `staged_pending_review`) |
| `160sp/validation_T2_response.json` | 4 | R-4 | Full HTTP response body for Test 2 (`Cell_Reports_Methods.pdf` → `rejected_off_topic`) |
| `160sp/validation_T3_response.json` | 4 | R-4 | Full HTTP response body for Test 3 (`Symbolic_Interaction_Theory_and_Architecture.pdf` → `needs_review`) |
| `160sp/validation_T4_response.json` | 4 | R-4 | Full HTTP response body for Test 4 (Granovskii citation-only → `needs_review`) |
| `160sp/MANIFEST.md` | — | R-6 (5 pts) | This file |
| `tests/validate_classifier_integration.py` | — | §11.2 | Contract validation harness (FINAL-tier polish; not grader-blocking) |
| `tests/fixtures/INDEX.md` | — | — | Fixture index for the validation harness |
| `160sp/contracts/SECURITY_REVIEW_2026-05-19.md` | — | R-2 supplement | 14-section security audit (S1-S14) covering XSS, path traversal, SQL injection, secret leakage, CSRF, DoS, etc. — every finding cited to file:line |
| `160sp/COMPLETION_CHECKLIST_2026-05-19.md` | — | self-audit | Per-rubric-line DONE/PARTIAL/DEFERRED audit with citations to the file or commit that satisfies each requirement |
| `160sp/validation_TC3_response.json` | 4 supplement | R-4 supplement | TC-3 (bad PDF magic bytes) HTTP response — supplementary contract test |
| `160sp/validation_TC4_response.json` | 4 supplement | R-4 supplement | TC-4 (SHA-256 duplicate) HTTP response — supplementary contract test |
| `160sp/validation_TC5_first_response.json` | 4 supplement | R-4 supplement | TC-5 reference submission (DOI dedup setup) |
| `160sp/validation_TC5_second_response.json` | 4 supplement | R-4 supplement | TC-5 DOI-duplicate-with-different-bytes verification |
| `160sp/validation_TC8_response.json` | 4 supplement | R-4 supplement | TC-8 (mixed batch, per-item independence) HTTP response — 3 items: staged + bad_file + duplicate, all handled independently |

---

## Storage proof

All classifier outputs are persisted to `data/ka_auth.db` (gitignored; present on
the submission machine). Run `python3 ka_auth_server.py` first, then query.

### `articles` table (4 rows after Phase-4 test run)

```
article_id    | status                | verdict   | article_type | primary_topic   | confidence | backend      | routing_reason                                          | pdf_stored | relevance
--------------+-----------------------+-----------+--------------+-----------------+------------+--------------+---------------------------------------------------------+------------+----------
KA-ART-000001 | staged_pending_review | accept    | meta_analysis| Biophilia       | 0.82       | atlas_shared |                                                         | YES        | 1.0
KA-ART-000002 | rejected_off_topic    | edge_case | commentary   | Color Psychology| 0.58       | atlas_shared | off_topic:edge_case_with_weak_topic_match_0.26_below_0.4| NO         | 0.26
KA-ART-000003 | needs_review          | reject    | unknown      | (null)          | 0.88       | atlas_shared | next_action:review_borderline_case                      | YES        | 0.0
KA-ART-000004 | needs_review          | (null)    | (null)       | (null)          | 0.00       | atlas_shared | citation_only_no_pdf_text                               | NO         | (null)
```

Query used:
```sql
SELECT
  article_id,
  status,
  json_extract(validation_notes, '$.classifier_verdict')           AS verdict,
  json_extract(validation_notes, '$.classifier_article_type')      AS article_type,
  json_extract(validation_notes, '$.classifier_primary_topic')     AS primary_topic,
  printf('%.2f', json_extract(validation_notes,
    '$.classifier_overall_confidence'))                            AS confidence,
  json_extract(validation_notes, '$.classifier_backend')           AS backend,
  json_extract(validation_notes, '$.routing_reason')               AS routing_reason,
  CASE WHEN quarantine_path IS NOT NULL THEN 'YES' ELSE 'NO' END   AS pdf_stored,
  relevance_score
FROM articles ORDER BY article_id;
```

### `audit_log` table (1 row per article — no orphans)

```
article_id    | action             | new_status            | created_at
--------------+--------------------+-----------------------+---------------------------
KA-ART-000001 | staged             | staged_pending_review | 2026-05-18T10:30:17.205013
KA-ART-000002 | rejected_off_topic | rejected_off_topic    | 2026-05-18T10:30:17.804282
KA-ART-000003 | needs_review       | needs_review          | 2026-05-18T10:30:18.042521
KA-ART-000004 | needs_review       | needs_review          | 2026-05-18T10:30:18.086521
```

### Quarantine files on disk (only accepted/edge-case papers have files)

```
data/storage/quarantine/2026-05/KA-ART-000001.pdf   5.7 MB  (Building_Environment.pdf)
data/storage/quarantine/2026-05/KA-ART-000003.pdf  43.0 MB  (Symbolic_Interaction_Theory_and_Architecture.pdf)
```

`KA-ART-000002` (`rejected_off_topic`) and `KA-ART-000004` (citation-only) have no
quarantine files — correct per contract §3.3 Branch D and E.

### Grader auto-test results (run `python3 160sp/rubrics/t2/t2_task1_grader.py . --auto-only`)

| Test | Weight | Expected | Basis |
|---|---|---|---|
| Classifier integration | critical | PASS | `AdaptiveClassifierSubsystem` + `.classify(` both present in `ka_article_endpoints.py` |
| Duplicate detection | important | PASS | `duplicate`, `check_duplicate`, `pdf_hash` all present |
| Contribute page modified | critical | PASS | `fetch(` + results keywords in `ka_contribute_public.html` |
| Corrupt PDF handling | critical | PASS | `%PDF-` magic-byte check at `ka_article_endpoints.py:384` |
| DB field completeness | important | PASS | 0 rows with `status IS NULL OR created_at IS NULL` |
| Audit log presence | minor | PASS | 0 orphan `articles` rows (all 4 have `audit_log` entries) |
| Storage path correctness | critical | PASS | 0 rejected rows with non-NULL `quarantine_path` |
| Edge-case distinguishability | important | PASS | 2 distinct statuses among non-rejected rows |

---

## Commit history (21 commits on branch)

```
84b81ce [T2-Task1] Import Phase 1 & 2 deliverables into repo
4dd9866 [T2-Task1] Phase-4 fix: off-topic detection + score clamp → 4/4 PASS
80b003d [T2-Task1] Phase-4 (rubric): validation matrix + 4 test responses
64f9081 [T2-Task1] Add Phase-4 verification log
a6ca4a5 [T2-Task1] Phase-4 Q6 fix: multi-file batch + accumulating results panel
08edb41 [T2-Task1] Phase-4 Q5 fix: persist classifier outputs into validation_notes JSON
ed20ad3 [T2-Task1] Phase-4 Q4 fix: explicit next_action override in router
1cabb0a [T2-Task1] Retry-on-IntegrityError around the articles INSERT (bug a)
00f8e06 [T2-Task1] id_sequences table + atomic _next_id (subsumes bugs b + c)
4aad484 [T2-Task1] Naming consistency: audit-action matches status, routing_reason JSON key
06d1dfd [T2-Task1] Phase-4 Q2 fix 3: abstract extraction handles multi-line + no garbage fallback
b743a5d [T2-Task1] Phase-4 Q2 fix 2: stronger title extraction heuristic
a2b2ef4 [T2-Task1] Phase-4 Q2 fix 1: propagate article_id as ClassificationEvidence.paper_id
3adeeb8 [T2-Task1] Defensive write: catch OSError on quarantine mkdir/write_bytes
397a9c9 [T2-Task1] Wire contribute page to /api/articles/submit; render results inline
e333096 [T2-Task1] Mirror classifier routing in citation-only path
76eaee0 [T2-Task1] Branch INSERT by classifier verdict; emit classifier block + contract_version
18719f2 [T2-Task1] Call classifier in PDF submit path (with skip-on-empty-text guard)
62735fb [T2-Task1] Extend _classify_article_payload with verdict/topic/backend (additive)
e5f70c8 [T2-Task1] Add _route_classifier_verdict helper
598fd49 [T2-Task1] Add contract validation scaffolding
```
