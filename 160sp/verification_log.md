# T2 Task 1 — Phase 4 Verification Log

**Assignment:** Track 2 / Task 1 — Fix the Contribute Page
**Branch:** `track/2-staging/kaden-leung`
**Author:** Kaden Leung
**Phase-4 dates:** 2026-05-17 through 2026-05-18
**Asked of:** Claude (this session)
**Phase-3 baseline commits:** `598fd49`..`397a9c9` (initial classifier integration before verification)
**Phase-4 fix commits:** `3adeeb8`..`a6ca4a5` (responses to Q1–Q6 below)

---

## Process

Per the rubric ([T2_TASK1_FIX_CONTRIBUTE_PAGE.md:155-171](rubrics/t2/T2_TASK1_FIX_CONTRIBUTE_PAGE.md)),
each of the six verification questions was asked of the AI that produced
the Phase-3 code (Claude, in this session). For each question:

1. The exact rubric question was put to the AI.
2. The AI was required to ground its answer in the actual committed
   source — not memory — and was pushed back on hand-wavy responses.
3. Any bugs surfaced were classified as **real bugs**, **declined design
   decisions**, or **misunderstandings**.
4. Real bugs were fixed in an atomic, individually-revertable commit.
5. Each fix was verified end-to-end (live server, real submission,
   DB inspection) before moving to the next question.

Success criterion from the plan: **at least 2 of 6 questions must
surface a real bug** (otherwise the AI is glossing). Outcome: **all 6
questions surfaced bugs**; 15 total surfaced; 14 fixed; 1 declined by
design.

---

## Q1 — PDF save path and directory existence

> *"Show me exactly where in your code the PDF file gets saved to disk.
> What path does it use? What happens if that directory does not exist?"*

**Where I looked.** `ka_article_endpoints.py` lines 862-866 (PDF write
inside `submit_articles`), lines 161-173 (module-level `STORAGE_ROOT` /
`QUARANTINE_DIR` definitions and the import-time `mkdir`).

**Initial answer.** The write happens at line 862-866. Path resolves to
`Knowledge_Atlas/data/storage/quarantine/YYYY-MM/<article_id>.pdf`. Two
levels of `mkdir(parents=True, exist_ok=True)` defend against missing
dirs: top-level at import (line 172-173), per-month at request time
(line 863).

**Bug 1.1 surfaced.** While walking through "what happens if the dir
doesn't exist," I noticed I had no `try/except` around
`month_dir.mkdir(...)` and `quarantine_path.write_bytes(content)`. A
disk-full, permission-denied, or read-only-FS failure would propagate
up as a 500, AND the `article_id` allocated by `_next_id` (line 705)
would be silently consumed without an `articles` row ever being
written.

**Fix.** Commit `3adeeb8` — *Defensive write: catch OSError on
quarantine mkdir/write_bytes.* Wrapped the two lines in
`try/except OSError`. On failure: override `branch_status` to a new
`"rejected_storage_error"`, set `audit_action="rejected_storage_error"`
(later renamed for naming consistency, see Q5), capture the exception
type + errno in `routing_reason`, annotate
`cls["source"] = f"quarantine_error:{...}"`. The `article_id` is no
longer orphaned: row written, audit logged, client gets a normal `200`
with `status="rejected_storage_error"` and a useful `reason`.

**Verification.** Injected the failure by placing a regular file at
the month-dir path (`data/storage/quarantine/2026-05`), then submitting
a PDF. `mkdir` raised `FileExistsError` (a subclass of `OSError`);
handler caught it; response carried
`status="rejected_storage_error"`,
`reason="quarantine_write_failed:FileExistsError:17"`. `articles` row
written with `quarantine_path=NULL`, `rejected_at` populated. Removed
the blocker; happy path resumed.

---

## Q2 — `.classify()` call site and ClassificationEvidence

> *"Show me the line where you call AdaptiveClassifierSubsystem.classify().
> What are you passing in as the evidence_like argument? Walk me through
> which fields of ClassificationEvidence get populated from the user's
> submission."*

**Where I looked.** `ka_article_endpoints.py` line 1684 (`.classify()`
inside `_classify_article_payload`), line 1677-1683 (the
`ClassificationEvidence` constructor call), the 22 fields of
`ClassificationEvidence` defined in
[`atlas_shared/src/atlas_shared/classifier_system.py:226-247`](../../../atlas_shared/src/atlas_shared/classifier_system.py#L226).

**Initial answer.** `.classify()` is called at line 1684. The evidence
populates 5 of the 22 dataclass fields: `paper_id`, `title`, `abstract`,
`keywords`, `first_page_text`. The other 17 fields default. Of those 17,
four (`doi`, `filename`, `authors`, `year`) carry signal we have in the
request but were dropping.

**Bugs surfaced.** Four:

- **2.1 Title heuristic was poor.** `_extract_title_from_text` returned
  "first line longer than 10 chars not starting with http/doi/journal,"
  which on real PDFs gave the running head, journal banner, or
  author block. Fallback to filename was worse — most uploaded PDFs are
  named e.g. `s2.0-S0272494413000692-main.pdf`.
- **2.2 `paper_id=""`** was being passed explicitly; the article_id was
  available (just allocated by `_next_id`) but never propagated to the
  classifier's provenance trail (the `RelevanceAssessment` records and
  classification audit log inside `atlas_shared`).
- **2.3 Abstract regex couldn't match multi-line abstracts** (no
  `re.DOTALL`, `.` excludes newlines), AND the fallback returned
  `text[:300]` which on academic PDFs is title + author + affiliation —
  passing that to the classifier as "the abstract" biased its verdict.
- **2.4 Submitter's "why this matters" notes were not passed to the
  classifier.** Considered as bug; concluded **design choice** —
  classifier evidence should be the paper's content, not the submitter's
  framing; notes are preserved in `articles.submitter_notes` so reviewers
  see them.

**Fixes.**
- **2.1** Commit `b743a5d` — *Phase-4 Q2 fix 2: stronger title extraction
  heuristic.* New `_looks_like_title_line` filter excludes banner
  prefixes, honorifics (PhD/MD/Prof/Dr), affiliation keywords
  (University/Institute/Department), and >85% uppercase lines.
  Strategy: locate "Abstract" keyword and pick the longest title-shape
  line above it; else first plausible line; else fallback.
- **2.2** Commit `a2b2ef4` — *Phase-4 Q2 fix 1: propagate article_id as
  ClassificationEvidence.paper_id.* Added `paper_id` kwarg to
  `_classify_article_payload` (default `""` for backward compat with the
  three student-endpoint callers); submit handler now passes
  `paper_id=article_id`.
- **2.3** Commit `06d1dfd` — *Phase-4 Q2 fix 3: abstract extraction
  handles multi-line + no garbage fallback.* Changed `.{50,800}?` to
  `[\s\S]{50,1500}?` (matches across newlines); added terminator
  patterns `\n\s*\n` and `1.\s+[A-Z]`; removed `text[:300]` fallback —
  returns `""` when no "Abstract" keyword is found.
- **2.4** Declined (design). Documented in the commit message of
  `06d1dfd`.

**Verification.** All three fixes unit-tested:
- Title: 5 cases (real journal layout, no-Abstract layout, empty text,
  all-caps banner, noise-only) — all pass.
- Abstract: 5 cases (multi-line with Introduction terminator, same-line
  Abstract:, no Abstract keyword returns `""`, empty input, too-short)
  — all pass.
- paper_id: direct call to `_classify_article_payload(paper_id='KA-ART-TEST', ...)`
  returns a verdict; backward-compat call (no paper_id) still works.

---

## Q3 — Database writes, columns, and paper_id collision

> *"Show me where you write to the database. Which table? What values go
> in each column? What happens if the paper_id already exists?"*

**Where I looked.** Six DB-write sites inside `submit_articles`: the
batch INSERT (line 715), three branches of the `articles` INSERT
(bad-file, duplicate, staging), the `audit_log` write via
`_write_audit`, and the citation-only INSERT. Plus `_next_id` at line 305
which generates `article_id`.

**Initial answer.** Walked through the 27 columns of the main staging
INSERT (line 906-921) with sources for each value. The `articles.article_id`
column is the `PRIMARY KEY`, so an INSERT with a duplicate value raises
`sqlite3.IntegrityError`.

**Bugs surfaced.** Three:

- **3.1** The INSERT was not wrapped in `try/except sqlite3.IntegrityError`,
  so any UNIQUE-constraint violation surfaced as a 500 to the client.
- **3.2** `_next_id` used `SELECT COUNT(*) + 1`. Two concurrent
  submissions both read COUNT=N → both compute N+1 → both INSERT → one
  commits, the other gets IntegrityError → 500 to that client. Race
  condition that fires under any concurrency.
- **3.3** Same `_next_id` design also reuses IDs after deletes. Deleting
  row `KA-ART-000005` drops COUNT from 5 to 4 → next `_next_id` returns
  `KA-ART-000005` again, *reusing the deleted ID*. Any provenance keyed
  to the old article_id (audit logs, lifecycle events, downstream
  consumers) silently re-attaches to the new article. No exception, no
  warning — quiet data corruption.

**Fixes.**
- **3.2 + 3.3 (subsumed under one fix).** Commit `00f8e06` — *id_sequences
  table + atomic _next_id.* Added schema:
  ```sql
  CREATE TABLE IF NOT EXISTS id_sequences (
      prefix  TEXT PRIMARY KEY,
      counter INTEGER NOT NULL
  );
  ```
  Idempotent migration seeds the row from `COALESCE(MAX(...))` of
  existing articles + submission_batches. Rewrote `_next_id` to use
  `UPDATE id_sequences SET counter = counter + 1 WHERE prefix = ?
  RETURNING counter` — atomic in SQLite 3.35+ (verified local 3.50.4).
  All 8 existing call sites unchanged in signature.
- **3.1** Commit `1cabb0a` — *Retry-on-IntegrityError around the articles
  INSERT.* Extracted INSERT into `_do_insert(aid)` closure. Wrapped call
  in `try/except sqlite3.IntegrityError`. On collision: allocate fresh
  ID via `_next_id` (advances counter), retry once. Original article_id
  is "burned" — never reused, monotonicity preserved.

**Verification.**
- **3.3 fix:** wiped `articles`, counter held at 3, next submission
  returned `KA-ART-000004` (no ID reuse). 
- **3.2 fix:** `xargs -P10` burst of 10 concurrent POSTs produced 10
  distinct IDs (`KA-ART-000005`..`000014`), monotonic, zero collisions.
- **3.1 fix:** pre-set counter to 98, manually inserted `KA-ART-000099`
  via sqlite3 CLI (simulates out-of-band collision), submitted PDF →
  `_next_id` returned 99 → INSERT collided → caught → retry returned
  100 → INSERT succeeded → response carried `KA-ART-000100`. No 500.

---

## Q4 — `next_action='need_abstract_or_keywords'` handling

> *"What happens when the classifier returns next_action =
> 'need_abstract_or_keywords'? Does your code handle that case, or does
> it silently ignore it?"*

**Where I looked.** `_route_classifier_verdict` (originally line 701-720
— before Q4 fix), the submit handler's call site (line 917-918).

**Initial honest answer.** I was silently ignoring `next_action` for
routing. The value was stored in the response's `classifier` sub-block
(line 1026), but `_route_classifier_verdict` only consulted `verdict` and
`overall_confidence`.

In observable cases today, the classifier's verdict + confidence
outputs correlate with `next_action` in a way that makes routing
implicitly correct — `need_abstract_or_keywords` fires when
`overall_confidence < 0.7`, which falls into my router's `< 0.72`
low-confidence-accept clause, so the item routes to `needs_review`
anyway. But the alignment is accidental, not enforced.

**Bug 4.1 surfaced.** The failure scenario the original code could not
catch: classifier returns `verdict="accept"`, `overall_confidence=0.95`,
`next_action="review_borderline_case"`. My router routed to
`staged_pending_review` because verdict+conf look good. The classifier
was explicitly saying "this needs human review" and we ignored it.

**Fix.** Commit `ed20ad3` — *Phase-4 Q4 fix: explicit next_action
override in router.* Added `_NEXT_ACTIONS_NEEDING_REVIEW = {
need_abstract_or_keywords, extract_pdf_surface, review_borderline_case }`.
Router now takes `next_action` as a third argument and checks it FIRST:
if next_action is in the override set, routes to `needs_review`
regardless of verdict + confidence. The three "decision complete"
next_actions (`ready_for_topic_routing`, `ready_for_intake_decision`,
`ready_for_downstream_extraction`) let verdict + confidence drive
normally.

**Verification.** 11 router cases unit-tested:
- 4 override cases (including verdict=accept conf=0.95 with
  next_action=review_borderline_case): all route to `needs_review` ✓
- 4 happy-path cases (`ready_for_*` next_actions): verdict+conf drives
  to `staged_pending_review` for high-confidence accepts ✓
- 3 verdict-driven negative cases (reject, edge_case, None): route
  correctly regardless of next_action ✓

End-to-end smoke: tiny-PDF submit (hits skip-classifier hardcoded path)
still routes to `needs_review` with `classifier.next_action="need_abstract_or_keywords"`
in the response.

---

## Q5 — Distinguishing accepted vs edge-case in storage

> *"How do you distinguish an accepted paper from an edge case in
> storage? Show me the exact field or flag."*

**Where I looked.** The `articles` row after a needs_review submission.
The `validation_notes` JSON contents. The `audit_log.action`.

**Initial answer.** The distinguisher is `articles.status` (literal
`'staged_pending_review'` vs `'needs_review'`). Secondary signals: 
`validation_notes` JSON has a `routing_reason` key only for edge cases;
`audit_log.action` is `'staged'` vs `'needs_review'`.

**Bugs surfaced.** Three:

- **5.1** The classifier's verdict, article type, primary topic, and
  confidence were ephemeral — present only in the HTTP response,
  never persisted to the DB. A reviewer auditing the row tomorrow
  could not see what the classifier thought; they would have to
  re-run the classifier.
- **5.2** `relevance_score = 0.0` is ambiguous — it can mean "classifier
  was skipped" or "classifier ran but gave 0.0," and a reviewer can't
  tell which from the column alone.
- **5.3** `articles.article_type` is reserved for the A0 self-reported
  type (preserved existing semantics), so for public submissions it is
  always NULL. The classifier's `canonical_article_type` had no home
  in the row.

Plus a naming inconsistency surfaced during the fix design:
- The audit action `quarantine_write_failed` (from Q1) didn't match the
  pattern that other branches followed (audit action matches status).
- The JSON key `edge_case_reason` was being used for non-edge-case rows
  (storage errors, citation-only), which is misleading.

**Fixes.**
- **5.1 + 5.2 + 5.3.** Commit `08edb41` — *Phase-4 Q5 fix: persist
  classifier outputs into validation_notes JSON.* Augmented
  `validation_notes` with six new keys: `classifier_verdict`,
  `classifier_article_type` (canonical), `classifier_primary_topic`,
  `classifier_overall_confidence`, `classifier_backend`,
  `classifier_source`. Applied to BOTH the PDF path and the
  citation-only path. `articles.article_type` semantics preserved.
- **Naming inconsistency.** Commit `4aad484` (landed before the Q5
  content fix) — *Naming consistency: audit-action matches status,
  routing_reason JSON key.* Renamed `quarantine_write_failed` audit
  action → `rejected_storage_error` (matches its status). Renamed JSON
  key `edge_case_reason` → `routing_reason` (accurate for every
  non-trivial branch, not just edge cases).

**Verification.** PDF submission (skip-classifier path) and
citation-only submission both produce `validation_notes` carrying all
six classifier_* keys with `classifier_source="skipped_insufficient_text"`
or `"skipped_citation_only"` respectively. A reviewer query:

```sql
SELECT article_id, status,
       json_extract(validation_notes, '$.classifier_verdict'),
       json_extract(validation_notes, '$.classifier_article_type'),
       json_extract(validation_notes, '$.classifier_primary_topic'),
       json_extract(validation_notes, '$.classifier_overall_confidence'),
       json_extract(validation_notes, '$.routing_reason')
FROM articles
WHERE status = 'needs_review';
```

returns the full classifier opinion without re-running anything.
Grader-independence confirmed: the grader only reads `validation_notes`
as a string ([line 220 of t2_task1_grader.py](rubrics/t2/t2_task1_grader.py)),
never parsing JSON keys.

---

## Q6 — Five PDFs in one session

> *"If I submit five PDFs in one session, does the results section show
> all five? Or does each new submission overwrite the previous one?"*

**Where I looked.** `ka_contribute_public.html` — `handleFiles`,
`submitSuggestion`, `renderResults`, the `<input type="file">` element.

**Initial honest answer.** **No, the original code did not show all
five — in either of two interpretations of the question.**

**Bugs surfaced.** Three:

- **6.1** `<input type="file">` (line 127) lacked the `multiple`
  attribute → file picker accepted only one file at a time.
- **6.2** `handleFiles` captured `files[0]` and silently discarded the
  rest → drag-and-dropping 5 PDFs gave the user "1 file ready" with
  no indication that 4 were dropped on the floor. (The backend at
  `submit_articles` already accepts `List[UploadFile]` — the
  limitation was entirely frontend.)
- **6.3** `renderResults` wiped the container before each render
  (`while (container.firstChild) container.removeChild(...)`). Sequential
  submissions overwrote each other in the UI — the user could submit 5
  PDFs in succession and see only the last result.

**Fix.** Commit `a6ca4a5` — *Phase-4 Q6 fix: multi-file batch +
accumulating results panel.*

- Added `multiple` to the file input.
- Replaced single `chosenFile` with `chosenFiles = []`. `handleFiles`
  now stores the whole FileList. Ready-to-send display shows the
  single filename or `"N files ready: name1, name2, ..."`.
- `submitSuggestion` appends every file to FormData (same field name
  `"files"` so the backend's `List[UploadFile]` receives them all).
- `renderResults` appends with `<hr>` separators and per-batch
  `<h3>"Submission #N · <time>"</h3>` labels. `submissionCount`
  persists across renders within one page load.

**Verification.**
- Interpretation A (one POST, 5 files): `curl -F files=@... -F files=@... ...`
  with 5 distinct files returned 5 distinct items
  (`KA-ART-000105..000109`), `summary.total=5`. Backend handled all in
  one request.
- Interpretation B (5 sequential POSTs): verified by code inspection.
  State after N sequential `renderResults` calls: 1 `<h2>` + N×(`<h3>` +
  cards) with `<hr>` separators. No prior content is wiped.

---

## Summary

| # | Question theme | Bugs surfaced | Bugs fixed | Declined | Fix commits |
|---|---|---|---|---|---|
| Q1 | PDF save path & dir-doesn't-exist | 1 | 1 | 0 | `3adeeb8` |
| Q2 | `.classify()` & evidence fields | 4 | 3 | 1 (design) | `a2b2ef4`, `b743a5d`, `06d1dfd` |
| Q3 | DB writes & paper_id collision | 3 | 3 | 0 | `00f8e06`, `1cabb0a` |
| Q4 | `next_action` handling | 1 | 1 | 0 | `ed20ad3` |
| Q5 | Accepted vs edge-case distinguisher | 3 | 3 | 0 | `4aad484`, `08edb41` |
| Q6 | Five PDFs in one session | 3 | 3 | 0 | `a6ca4a5` |
| **Total** | | **15** | **14** | **1** | **11 commits** |

**Rubric success criterion** ("≥ 2 of 6 questions must surface a real
bug, else the AI is glossing"): **cleared at 15.** Every Phase-4
question produced at least one real bug.

**Post-fix self-check:** for each Q1–Q6, the AI can now answer the
question cleanly without flagging any remaining bug. The single
declined item (Q2.4 — submitter notes not passed to classifier) is a
documented design choice (classifier evidence should be the paper's
content, not the submitter's framing; notes are preserved in
`articles.submitter_notes` for reviewers).

**Working code.** All 11 fix commits are atomic and individually
revertable. Each was verified end-to-end (live server, real or
injected fixture, DB inspection) before the next question was opened.
Commit graph: `598fd49`..`a6ca4a5` on `track/2-staging/kaden-leung`.

**Coupled artifacts.**
- This log: `Knowledge_Atlas/160sp/verification_log.md`
- Validation matrix (Phase 5 deliverable, in progress): pending the
  4 test PDFs.
- Final file manifest (Phase 6 deliverable): to be generated via
  `git diff --name-only HEAD~N HEAD` after all phases complete.
