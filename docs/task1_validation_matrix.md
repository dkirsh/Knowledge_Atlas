# Task 1 — Validation Matrix
**Author:** Dhruv Sood · **Date:** 2026-05-03

Run command: `python3 data/test_pdfs/validate_task1.py`
Result: **26/26 PASS** (Layer A: 6/6 · Layer B: 20/20)

The validator has two layers. Layer A drives the same classifier code path
the endpoint uses, in-memory. Layer B runs the actual HTTP endpoint via
FastAPI's `TestClient` against a tempdir-isolated DB and quarantine, so
storage assertions are real (file exists, row exists, audit row exists).

---

## Rubric matrix (Phase 4 four-test minimum, expanded)

| # | Input | Expected verdict | Actual verdict | Expected type | Actual type | Stored? | DB entry? | PASS? |
|--:|---|---|---|---|---|---|---|---|
| 1 | On-topic empirical PDF (nature + green space + attention RCT) | accept | **accept** | empirical_research | **empirical_research** | yes | yes (row + quarantine PDF + audit_log) | **PASS** |
| 2 | Off-topic ML PDF (Deep learning ImageNet) | reject | **reject** | — | empirical_research (heuristic) | no | no | **PASS** |
| 3 | Edge-case theory PDF (biophilic-design workplace, no empirical data) | edge_case | **edge_case** | theoretical | **theoretical** | yes (flagged `edge_case:true`) | yes | **PASS** |
| 4 | Citation only — Kaplan, S. (1995) | accept / edge_case | **edge_case** | varies | unknown | yes | yes (`input_mode=citation_text`) | **PASS** |
| 5 | Same PDF as #1 submitted twice | duplicate (2nd) | **duplicate** | — | — | no new row | no new row | **PASS** |
| 6 | 3 distinct on-topic PDFs in one session | 3 separate verdicts, 3 rows | **3 items, 3 rows** | empirical_research × 3 | — | yes × 3 | yes × 3 | **PASS** |
| 7 | Bad PDF (non-PDF magic bytes) | rejected_bad_file | **rejected_bad_file** | — | — | no | no | **PASS** |

---

## Storage proof (terminal output)

The validator's Layer B emits a path for the on-disk quarantine PDF on Test
B1. Sample line from the latest run:

```
PASS  B1 · quarantine PDF on disk
      (/var/folders/.../ka_task1_xxx/storage/quarantine/2026-05/KA-ART-XXXXXXXX.pdf)
PASS  B1 · audit_log row exists  (n=1)
PASS  B1 · status=staged_pending_review
PASS  B1 · edge_flag=edge_case:false
```

Test B3 asserts the EDGE_CASE row's `validation_notes.edge_flag` is
`edge_case:true` — i.e. distinguishable from ACCEPT. Test B2 asserts no DB
row was inserted for the off-topic PDF and no quarantine file was written.

For a live run against the running KA backend, see the curl + sqlite3
recipe in `docs/SUBMISSION_TASK1.md` §6B.

---

## Diagnosis of the only "near-miss" during development

**Initial Test 6 (5 near-duplicate submissions)** failed: 0 inserts of 5
expected. This was a **test bug, not an implementation bug** — the 5
PDFs all started with the same on-topic phrase, so the fuzzy-title-match
in `_suggest_check_dup` correctly classified submissions 2–5 as duplicates
(which is what the duplicate-check is supposed to do).

The test was rewritten with truly distinct titles (urban parks / forest
bathing / daylight in offices). 3/3 inserts. This validates both:

- multi-submission accumulation (3 items in API response)
- distinct papers don't get incorrectly merged
- near-duplicates DO get correctly merged (Test B5 covers that path)

Diagnosis writeup also in `docs/task1_bug_review.md` B6.
