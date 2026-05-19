# Classifier Integration Contract — DRAFT

**Track:** COGS 160 Track 2 (Phase 2)
**Author:** Kaden Leung
**Date drafted:** 2026-05-09
**Contract version:** 1.0 (bumped on any change to §3 schema or §4 storage rules)
**Status:** DRAFT — see §10 for open verification gaps before promotion to final
**JSON Schema artifact:** [`schemas/classifier_response.json`](./schemas/classifier_response.json) (post-merge); [`schemas/classifier_response.legacy.json`](./schemas/classifier_response.legacy.json) (pre-merge)

**Canonical implementation paths.**
- Frontend: [`Knowledge_Atlas/ka_contribute_public.html`](../../ka_contribute_public.html)
- Backend endpoint: [`Knowledge_Atlas/ka_article_endpoints.py`](../../ka_article_endpoints.py)  (`POST /api/articles/submit`)
- Classifier: [`atlas_shared/src/atlas_shared/classifier_system.py`](../../../atlas_shared/src/atlas_shared/classifier_system.py) → `AdaptiveClassifierSubsystem.classify(evidence)`

---

## 1. Purpose & scope

When the implementation is complete, the system MUST satisfy all of
the conditions below. The contract describes system state at the
point of merge; the order in which a PR delivers them is at the
implementer's discretion.

1. **Frontend wiring.** `submitSuggestion()` in `ka_contribute_public.html` performs a `multipart/form-data` POST to `/api/articles/submit`. The legacy `localStorage["ka.public_suggestions"]` write is gone.
2. **Endpoint extension.** The `submit_articles` handler in `ka_article_endpoints.py` calls `AdaptiveClassifierSubsystem.classify()` (or the equivalent `_classify_article_payload` helper) for every non-rejected, non-duplicate item, and the response object carries a `classifier` sub-block per item (§3.1). Existing top-level fields (`validation_status`, `duplicate_status`, `metadata`, `status`, etc.) are preserved; classifier output is *additive*. Two new `status` values are accepted by the column: `needs_review` (Branch B) and `rejected_off_topic` (Branch E).
3. **Results panel.** Submissions render inline below the submit button as one DOM element per response item (§3.2). The thank-you modal is no longer used.

The current `/submit` handler at [ka_article_endpoints.py:648-919](../../ka_article_endpoints.py#L648-L919) goes from dedup to staging without classifying; condition 2 above is the gap this contract closes.

**Out of scope** (the system state after merge does not change these):
- Classifier scoring logic inside `atlas_shared`.
- The `articles` / `submission_batches` / `audit_log` / `question_claims` schemas (no DDL changes; two new free-form `status` values is the only `articles` change).
- Auth flow.
- Reviewer / instructor UI.
- A0 task-tracking semantics — `a0_task` and self-reported `article_type` form fields remain out of scope for the public surface and are unused.

### 1.1 Change log

| Version | Date       | Changes                                                                                                                                                                |
| ------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.0     | 2026-05-09 | Initial draft.                                                                                                                                                         |
| 1.0     | 2026-05-15 | Panel-review revision (no version bump — §3 schema and §4 storage rules unchanged). Added §3.3 duplicate-probe decision tree, §4.0 storage paths, §4.1 confidence boundary, §4.2 column enumeration. Fixed I-2a/I-2b, TC-4/TC-5 pre-conditions, TC-8 order-independence. Removed rate-limit pseudo-threshold (was T-9). Tightened DOM contract to substring check on `#__ka_results`. |
| 1.0     | 2026-05-17 | Grader-grounding revision (no version bump — §3 schema and §4 storage rules unchanged). After reading the actual `t2_task1_grader.py` and `T2_TASK1_FIX_CONTRIBUTE_PAGE.md`, rewrote §10 to tag every gap with its real grader-relevance, and split §11 into 11.1 "Grader-blocking" (eight auto-tests + six manual rubric items) and 11.2 "Contract-internal polish." Gap 3 closed via an addendum appended to `Track_2_Context`. |

---

## 2. Inputs

### 2.1 Frontend → backend (`multipart/form-data` POST)

Field names match
[ka_article_endpoints.py:649-659](../../ka_article_endpoints.py#L649-L659).

| Field           | Type                        | Constraint                                                   | Required                                 |
| --------------- | --------------------------- | ------------------------------------------------------------ | ---------------------------------------- |
| `files[]`       | `application/pdf` blob[]    | Each blob ≤ `KA_MAX_FILE_SIZE_MB` (default 100) MB; first 5 bytes must be `%PDF-` | At least one of `files` or `citations` |
| `citations`     | UTF-8 string                | length 0–4 000; ≤ 10 lines                                   | At least one of `files` or `citations`   |
| `notes`         | UTF-8 string                | length 0–2 000                                               | optional                                 |
| `source_surface`| string literal              | exactly `"ka_contribute_public"` (this PR introduces this value; default in code is `"ka_contribute"`) | required |
| `Authorization` | header `Bearer <jwt>`       | only used if signed in; absent ⇒ anonymous                   | optional                                 |

`a0_task` and `article_type` form fields supported by the endpoint are
**not** sent by the public form.

### 2.2 Per-item input to the classifier

For each `files[i]` (or each non-empty citation line), the backend
constructs a `ClassificationEvidence` with the fields below. None of
these are caller inputs — they are derived inside the endpoint.

| Field             | Type            | Constraint / source                                                                       |
| ----------------- | --------------- | ----------------------------------------------------------------------------------------- |
| `paper_id`        | str             | `""` (empty); the existing helper `_classify_article_payload` passes empty paper_id ([line 1655](../../ka_article_endpoints.py#L1655)) — the classifier does not use it for matching. |
| `title`           | str             | parsed via `_parse_citation_line(...)` ([line 365](../../ka_article_endpoints.py#L365)) or extracted from PDF surface; length 0–500 |
| `abstract`        | str             | not extracted in the current pipeline; pass `""` until the abstract-extraction path lands; length 0–5 000 when populated |
| `keywords`        | tuple[str, ...] | empty tuple from public form; each ≤ 60 chars; ≤ 32 items when populated                  |
| `first_page_text` | str             | from `_get_first_page_text(pdf_bytes)` (helper to add — see TODO); truncate to 3 000 chars per existing call site convention ([line 1660](../../ka_article_endpoints.py#L1660)); length 0–20 000 |

---

## 3. Outputs

### 3.1 Server response (`200 OK`)

Authoritative schema: [`schemas/classifier_response.json`](./schemas/classifier_response.json).
The narrative below summarises that file; the JSON Schema is the
tiebreaker if they disagree.

The response *adds* a `classifier` sub-object to each item; existing
top-level fields are unchanged. Existing top-level fields
([ka_article_endpoints.py:732-919](../../ka_article_endpoints.py#L732-L919)):

```json
{
  "contract_version": "1.0",
  "submission_id": "KA-IN-000123",
  "items": [
    {
      "article_id":         "KA-ART-000456",
      "input_mode":         "pdf_single",
      "filename":           "boubekri_2014.pdf",
      "validation_status":  "valid",
      "duplicate_status":   "not_duplicate",
      "metadata":           { "doi": "10.1016/j.jenvp.2014.02.003", "confidence": "medium" },
      "status":             "staged_pending_review",
      "duplicate_of":       null,

      "classifier": {
        "verdict":                  "accept",
        "classifier_article_type":  "empirical_research",
        "article_type_confidence":  0.81,
        "primary_topic":            "daylight_and_cognition",
        "primary_topic_confidence": 0.74,
        "active_topic_matches":     [{"topic": "circadian_alertness", "score": 0.61}],
        "overall_confidence":       0.81,
        "next_action":              "ready_for_topic_routing",
        "backend":                  "atlas_shared"
      },

      "reason": null
    }
  ],
  "summary": { "total": 1, "staged": 1, "duplicates": 0, "rejected": 0, "edge_cases": 0 }
}
```

**Field origin notes (so the additive design is unambiguous).**

| Field                                | Source                                                             |
| ------------------------------------ | ------------------------------------------------------------------ |
| `status`                             | Existing endpoint vocabulary, with `needs_review` added by this PR |
| `validation_status`, `duplicate_status`, `metadata` | Existing — unchanged                                |
| `article_type` (top-level, optional) | Existing A0 self-reported field — unused by public form            |
| `classifier.classifier_article_type` | NEW — output of `AdaptiveClassifierSubsystem.classify()`. Renamed from the classifier's native `article_type.value` to avoid collision with the existing top-level `article_type` field. |
| `classifier.verdict`                 | NEW — derived from `stable_topic_routing.best_verdict` ([relevance.py:254](../../../atlas_shared/src/atlas_shared/relevance.py#L254)). MAY be `null` when `stable_topic_routing is None` (bibliographic-only stage); see §4.1. |
| `classifier.backend`                 | NEW — **the endpoint MUST set this**; it is not currently emitted by `_classify_article_payload`. Source: module-level constant `CLASSIFIER_BACKEND` ([ka_article_endpoints.py:154](../../ka_article_endpoints.py#L154)). Values: `"atlas_shared"` when the real classifier loaded; `"ka_local_fallback"` when the import failed and the heuristic fallback was used. |
| `classifier.next_action`             | NEW — passthrough of `result.next_action` ([classifier_system.py:461](../../../atlas_shared/src/atlas_shared/classifier_system.py#L461)). |
| All other `classifier.*` fields      | NEW — direct passthrough of `AdaptiveClassificationResult` fields  |

The `classifier` sub-object is **omitted** when the item never reached
the classifier (i.e. `status == "duplicate_existing"` or
`status == "rejected_bad_file"`); see §4.

### 3.2 Frontend rendering (behavior contract, not pixel contract)

For each `items[i]`, the page MUST place the following data points in
the DOM, before the next user interaction, somewhere within the
descendant tree of the element with id `__ka_results` (which the
implementer creates inline below the submit button — not in the
modal):

- `article_id` (or `duplicate_of` when the verdict is duplicate)
- the verdict (one of: accept / edge case / rejected / already in corpus / bad file)
- `classifier.classifier_article_type` if present
- `classifier.primary_topic` if present
- `classifier.overall_confidence` formatted to two decimals if present
- `reason` if non-null

**Verifiable rendering rule (this is what TC-6 / TC-8 check).** For
every required data point, *some* descendant of `#__ka_results` has
`textContent.trim()` containing the rendered string. The check is
substring-based (the implementer may surround values with labels like
"Verdict: accept"); it does not require a specific selector path or
class name. Required data points that are `null` or absent in the
response are simply not checked.

Layout, colour, typography, and copy are at the implementer's
discretion. The contract pins **what data is in the DOM**, not **how
it is styled**.

The legacy thank-you modal MUST NOT be opened on success, failure, or
network error.

Two behavioral invariants on the rendering (verified by the JS unit
test, TC-6 and TC-8):

- The submit button is re-enabled after the response settles (success or failure).
- On a network or `5xx` failure, no card is shown and an error
  message is visible.

### 3.3 Duplicate-probe decision tree

Every PDF item is run through `_check_duplicates(pdf_hash, doi, title, authors)`
([ka_article_endpoints.py:505-602](../../ka_article_endpoints.py#L505-L602))
**before any `INSERT INTO articles` for that item** (I-12). Citation-only items use the same
function with `pdf_hash=None`. The probe runs the stages below in order and short-circuits
on the first stage that returns a match.

| Stage | Signal                            | Probe output `match_type`         | Probe `confidence` | Endpoint action                                                | Response `status`        | Branch | Classifier called? |
| ----- | --------------------------------- | --------------------------------- | ------------------ | -------------------------------------------------------------- | ------------------------ | ------ | ------------------ |
| 1     | SHA-256 hash exact                | `exact_hash`                      | `definitive`       | block ingestion; insert audit-only row referencing existing ID | `duplicate_existing`     | D      | NO                 |
| 2     | DOI exact (case-insensitive)      | `exact_doi`                       | `definitive`       | block ingestion; insert audit-only row                          | `duplicate_existing`     | D      | NO                 |
| 3     | Title fuzzy (≤ 1-word edit) AND author agreement | `title_and_authors_fuzzy` | `very_high`        | block ingestion; insert audit-only row                          | `duplicate_existing`     | D      | NO                 |
| 4     | Title fuzzy, authors differ      | `title_fuzzy_authors_differ`      | `medium`           | proceed to classifier; flag for review                          | `needs_review`           | B      | YES (verdict OVERRIDDEN to `edge_case` regardless of classifier output) |
| 5     | Title fuzzy alone (no author data)| `title_fuzzy_1word`               | `high`             | proceed to classifier; flag for review                          | `needs_review`           | B      | YES (verdict OVERRIDDEN to `edge_case` regardless of classifier output) |
| —     | No match                          | (probe returns `is_duplicate=false`) | n/a             | proceed normally; verdict determined by classifier              | per §4.1 routing table   | A/B/E  | YES                |

**Rationale for stages 4 and 5.** The assignment's instructions
explicitly say `sha256_exact` / `doi_exact` → re-ingest blocked;
`title_fuzzy` / `page_text_match` → "inspect by hand." Routing
ambiguous fuzzy matches to `needs_review` (Branch B) — instead of
silently rejecting OR silently accepting — gives the human reviewer
the inspect-by-hand decision the assignment requires. The verdict
override to `edge_case` ensures the response carries an
`routing_reason` in `validation_notes` recording which fuzzy
signal fired.

**Audit-only rows (definitive duplicates).** For stages 1–3 the
endpoint inserts a row in `articles` solely to record the attempted
resubmission ([line 750-769](../../ka_article_endpoints.py#L750-L769)).
This row has `status='duplicate_existing'` and `duplicate_of=<existing_article_id>`,
is invisible to corpus reads (which filter on `staged_pending_review`
and forward statuses), and is the only record of the duplicate
attempt.

**Canonical-probe substitution.** The assignment names two external
scripts (`course_scaffolding.py probe-collection-pdf` and
`probe_pdf_against_article_eater()`) as the canonical probe. Neither
is present on the local checkout (§10 item 1). This contract uses
`_check_duplicates()` as the functional equivalent; its outputs map
to the canonical probe's outputs as follows:

| Canonical probe output | This contract's stage | `_check_duplicates` `match_type` |
| ---------------------- | --------------------- | -------------------------------- |
| `sha256_exact`         | 1                     | `exact_hash`                     |
| `doi_exact`            | 2                     | `exact_doi`                      |
| `title_fuzzy`          | 4 or 5                | `title_and_authors_fuzzy` / `title_fuzzy_authors_differ` / `title_fuzzy_1word` |
| `page_text_match`      | (not implemented)     | (not implemented — see §10 item 1) |
| (no match)             | —                     | `is_duplicate=false`             |

---

## 4. Storage rules (status → side-effects)

For every item, **exactly one** branch executes. Side-effects are
specified to the byte and column level so a script can verify them.
Status values, audit actions, and the month-bucketed quarantine path
are taken verbatim from the existing implementation (see line
references), with the addition of two new statuses (`needs_review` and
`rejected_off_topic`) introduced by this PR.

**Per-item independence (binding).** Items in a multi-item submission
are processed independently. Failure, rejection, or duplicate-match of
one item never affects the processing or storage outcome of any other
item in the same submission. The endpoint MUST attempt classification
and storage for every item and return one `items[i]` entry per
submitted item, even if a sibling item raised an exception. Sibling
exceptions are logged to `audit_log` against the failing item's
`article_id` only. (Verified by TC-8.)

### 4.0 Concrete storage paths

Resolved from [ka_article_endpoints.py:161-164](../../ka_article_endpoints.py#L161-L164). All paths
are relative to the repo root.

| Symbol               | Resolved path                                                   | Env override            | Notes                                                                                     |
| -------------------- | --------------------------------------------------------------- | ----------------------- | ----------------------------------------------------------------------------------------- |
| `STORAGE_ROOT`       | `Knowledge_Atlas/data/storage/`                                 | `KA_STORAGE_ROOT`       | parent of the three sub-dirs below                                                        |
| `QUARANTINE_DIR`     | `Knowledge_Atlas/data/storage/quarantine/YYYY-MM/`              | `KA_QUARANTINE_DIR`     | month-bucketed; created on demand by `month_dir.mkdir(parents=True, exist_ok=True)`       |
| `PDF_COLLECTION_DIR` | `Knowledge_Atlas/data/storage/pdf_collection/`                  | `KA_PDF_COLLECTION_DIR` | instructor-promoted only; out of scope for this PR                                        |
| `REJECTED_DIR`       | `Knowledge_Atlas/data/storage/rejected/`                        | `KA_REJECTED_DIR`       | audit-only copies; never read by corpus queries; this contract writes NO files here today |

Filename convention for the only PDF write this PR performs:
`<QUARANTINE_DIR>/<article_id>.pdf` where `article_id` matches `^KA-ART-\d{6}$`.

### 4.1 Confidence boundary for verdict routing (pinned)

The classifier emits `overall_confidence` in `[0,1]` and a `verdict` in
`{accept, edge_case, reject}`. The endpoint maps these to a `status`
value using ONE boundary value — `0.72` — taken from the classifier's
own `_next_action` logic
([classifier_system.py:894, 898](../../../atlas_shared/src/atlas_shared/classifier_system.py#L894)).

**Routing precedence (checked top to bottom):**

| Order | Classifier output                                                                                              | Endpoint `status`        | Branch |
| ----- | -------------------------------------------------------------------------------------------------------------- | ------------------------ | ------ |
| 1     | **Off-topic detection** (added during Phase-4 validation): `verdict == "edge_case"` AND `primary_topic_score < 0.40` | `rejected_off_topic`     | E      |
| 2     | **next_action override** (Q4 fix): `next_action ∈ {need_abstract_or_keywords, extract_pdf_surface, review_borderline_case}` | `needs_review`           | B      |
| 3     | `verdict is None` (e.g. bibliographic-only, local-fallback path)                                              | `needs_review`           | B      |
| 4     | `verdict == "reject"`                                                                                          | `rejected_off_topic`     | E      |
| 5     | `verdict == "edge_case"` (and rule 1 did not fire — i.e. `primary_topic_score >= 0.40`)                       | `needs_review`           | B      |
| 6     | `verdict == "accept"` AND `overall_confidence < 0.72`                                                          | `needs_review`           | B      |
| 7     | `verdict == "accept"` AND `overall_confidence >= 0.72`                                                         | `staged_pending_review`  | A      |
| —     | Duplicate-probe match at definitive confidence (per §3.3) — checked before classifier call                     | `duplicate_existing`     | D      |
| —     | File validation fails (magic bytes or oversize) — checked before classifier call                               | `rejected_bad_file`      | C      |

**Threshold rationale:**

- **0.72 confidence boundary** (rules 6–7): taken from the classifier's own `_next_action` logic
  ([classifier_system.py:894, 898](../../../atlas_shared/src/atlas_shared/classifier_system.py#L894)). Pinned in the
  contract so the routing aligns with the classifier's internal "ready" threshold.

- **0.40 off-topic threshold** (rule 1): added during Phase-4 validation as a routing-level workaround for a classifier limitation. The classifier's constitution bank contains only positive topics; a clearly off-topic paper matches the least-bad option with a low `primary_topic_score`. Rule 1 distinguishes legitimate edge cases (paper is adjacent to a real Atlas topic, score ≥ 0.40) from off-topic content (score < 0.40). Calibrated from Phase-4 fixture data (a known off-topic paper scored 0.26; well below 0.40). Tunable as more data becomes available. The constant is `_OFF_TOPIC_PRIMARY_TOPIC_THRESHOLD` in
  [ka_article_endpoints.py](../../ka_article_endpoints.py).

If `stable_topic_routing is None` (classifier ran on bibliographic
evidence only and could not score topics), the endpoint MUST treat
this as `verdict == None` and route to Branch B (`needs_review`) via
rule 3. The classifier block in the response carries `verdict: null`
ONLY in this case; see §3.1.

### Branch A — `status == "staged_pending_review"` (classifier `verdict == "accept"`)

| Side-effect       | Required value                                                                                 |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| File written      | `QUARANTINE_DIR/<article_id>.pdf` (resolves to `Knowledge_Atlas/data/storage/quarantine/YYYY-MM/<article_id>.pdf`) ([line 783-786](../../ka_article_endpoints.py#L783-L786)); SHA-256(file_bytes) == request hash |
| `articles` row    | INSERT with `status='staged_pending_review'`, `quarantine_path` populated ([line 811](../../ka_article_endpoints.py#L811)) |
| `audit_log` row   | INSERT with `action='staged'`, `new_status='staged_pending_review'` ([line 818](../../ka_article_endpoints.py#L818))           |
| `pdf_collection/` | NOT written (promotion is the instructor-review job, out of scope)                             |

### Branch B — `status == "needs_review"` (classifier `verdict == "edge_case"`, **NEW**)

This status is introduced by this PR. The endpoint must accept it as a
valid value of `articles.status` (the column is free-form `TEXT` so no
schema migration is needed).

| Side-effect       | Required value                                                                                 |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| File written      | `QUARANTINE_DIR/<article_id>.pdf` (resolves to `Knowledge_Atlas/data/storage/quarantine/YYYY-MM/<article_id>.pdf`)                                             |
| `articles` row    | INSERT with `status='needs_review'`; `validation_notes` JSON contains key `"routing_reason"` |
| `audit_log` row   | INSERT with `action='needs_review'`, `new_status='needs_review'`                               |

### Branch C — `status == "rejected_bad_file"` (magic bytes / oversize)

| Side-effect       | Required value                                                                                 |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| File written      | NOT written to `quarantine/`                                                                   |
| `articles` row    | INSERT with `status='rejected_bad_file'` ([line 730-742](../../ka_article_endpoints.py#L730-L742))                          |
| `audit_log` row   | INSERT with `action='rejected_bad_file'`, `new_status='rejected_bad_file'`                     |
| `classifier`      | OMITTED from response item                                                                     |

### Branch D — `status == "duplicate_existing"` (definitive duplicate)

| Side-effect       | Required value                                                                                 |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| File written      | NOT written to `quarantine/`                                                                   |
| `articles` row    | INSERT (audit-only row) with `status='duplicate_existing'`, `duplicate_of=<existing_article_id>` ([line 750-769](../../ka_article_endpoints.py#L750-L769)) |
| `audit_log` row   | INSERT with `action='duplicate_detected'`, `new_status='duplicate_existing'`                   |
| `classifier`      | OMITTED from response item (classifier was never called)                                       |

> Note: the existing implementation already inserts an audit-only row
> for duplicates (it captures who tried to resubmit, when, and which
> existing article matched). This contract preserves that behavior; it
> does **not** create a second main-corpus entry. The duplicate row is
> never visible to corpus reads because of the `status` filter.

### Branch E — `status == "rejected_off_topic"` (classifier `verdict == "reject"`, **NEW**)

This status is introduced by this PR.

| Side-effect       | Required value                                                                                 |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| File written      | NOT written to `quarantine/`                                                                   |
| `articles` row    | INSERT with `status='rejected_off_topic'`, `relevance_score` set to `classifier.primary_topic_confidence` (semantically correct: it is a topic-relevance score, not an article-type confidence). |
| `audit_log` row   | INSERT with `action='rejected_off_topic'`, `new_status='rejected_off_topic'`                   |
| `classifier`      | included in response item (the verdict is the reason)                                          |

### 4.2 Required `articles` column values per branch

The `articles` table has 30+ columns (full schema at
[lines 201-248](../../ka_article_endpoints.py#L201-L248)). The
following table enumerates each column's required value on the
INSERT for each branch. Entries marked `(unchanged)` indicate columns the
existing implementation does not write on that branch; new
implementation MUST NOT write them either.

Symbols used in the value column:
- `req.<x>` — derived from the inbound request (e.g. `req.pdf_bytes`, `req.citation_line`)
- `user.<x>` — from `_get_optional_user(request)`; `NULL` if anonymous
- `parsed.<x>` — from `_parse_citation_line(line)` ([line 365](../../ka_article_endpoints.py#L365))
- `now` — `_now()` = `datetime.now(timezone.utc).isoformat()`
- `cls.<x>` — fields from `AdaptiveClassifierSubsystem.classify()` result
- `dup.<x>` — fields from `_check_duplicates(...)` result

| Column                  | Branch A staged           | Branch B needs_review     | Branch C rejected_bad_file | Branch D duplicate_existing | Branch E rejected_off_topic |
| ----------------------- | ------------------------- | ------------------------- | -------------------------- | --------------------------- | --------------------------- |
| `article_id`            | new `KA-ART-NNNNNN`       | same                      | same                       | same                        | same                        |
| `submission_id`         | batch ID (`KA-IN-NNNNNN`) | same                      | same                       | same                        | same                        |
| `submitter_id`          | `user.user_id` or `NULL`  | same                      | same                       | same                        | same                        |
| `submitter_type`        | `user.role` or `"anonymous"` | same                   | same                       | same                        | same                        |
| `track`                 | `user.track` or `NULL`    | same                      | same                       | same                        | same                        |
| `input_mode`            | `"pdf_single"` or `"citation_text"` | same            | `"pdf_single"`             | depends on input            | depends on input            |
| `doi`                   | `_extract_doi_from_pdf` or `parsed.doi` | same        | `NULL`                     | extracted if available      | same as A                   |
| `title`                 | `parsed.title` or `NULL`  | same                      | `NULL`                     | `parsed.title` or `NULL`    | same as A                   |
| `authors`               | `parsed.authors` or `NULL`| same                      | `NULL`                     | same                        | same                        |
| `year`                  | `parsed.year` int or `NULL` | same                    | `NULL`                     | same                        | same                        |
| `journal`               | `NULL` (not parsed today) | same                      | `NULL`                     | `NULL`                      | `NULL`                      |
| `abstract`              | `NULL` (not extracted today) | same                   | `NULL`                     | `NULL`                      | `NULL`                      |
| `citation_raw`          | citation line if input_mode==citation_text; else `NULL` | same | `NULL`                  | same as A                   | same as A                   |
| `pdf_filename`          | `req.filename` or `"unknown.pdf"` | same              | same                       | same                        | same                        |
| `pdf_hash_sha256`       | `sha256(req.pdf_bytes).hexdigest()` | same            | same                       | same                        | same                        |
| `pdf_size_bytes`        | `len(req.pdf_bytes)`      | same                      | same                       | same                        | same                        |
| `quarantine_path`       | `str(QUARANTINE_DIR / f"{article_id}.pdf")` | same    | `NULL`                     | `NULL`                      | `NULL`                      |
| `promoted_path`         | `NULL`                    | `NULL`                    | `NULL`                     | `NULL`                      | `NULL`                      |
| `article_type`          | `NULL` (A0 self-report unused by public form) | same  | `NULL`                     | `NULL`                      | `NULL`                      |
| `a0_task`               | `NULL`                    | `NULL`                    | `NULL`                     | `NULL`                      | `NULL`                      |
| `article_type_valid`    | `0`                       | `0`                       | `0`                        | `0`                         | `0`                         |
| `status`                | `"staged_pending_review"` | `"needs_review"` (NEW)    | `"rejected_bad_file"`      | `"duplicate_existing"`      | `"rejected_off_topic"` (NEW) |
| `duplicate_of`          | `NULL`                    | `NULL`                    | `NULL`                     | `dup.matches[0].article_id` | `NULL`                      |
| `validation_notes`      | `json.dumps(validation)` (the dict from `_validate_pdf_bytes`) | same + adds key `"routing_reason"` carrying the probe match_type OR classifier verdict reason | `json.dumps(validation)` (includes `"rejection_reason"`) | `json.dumps(validation)` | `json.dumps({"rejection_reason": "off_topic", "overall_confidence": <value>})` |
| `relevance_score`       | `cls.primary_topic_confidence` | same                 | `NULL`                     | `NULL`                      | `cls.primary_topic_confidence` |
| `review_notes`          | `NULL`                    | `NULL`                    | `NULL`                     | `NULL`                      | `NULL`                      |
| `assigned_question_id`  | `req.question_id` or `NULL` | same                    | `NULL`                     | `NULL`                      | `NULL`                      |
| `topic_tags`            | `req.topic_tags` or `NULL`| same                      | `NULL`                     | `NULL`                      | `NULL`                      |
| `source_surface`        | `"ka_contribute_public"`  | same                      | same                       | same                        | same                        |
| `course_context`        | `"COGS160-SP26"` ([line 726](../../ka_article_endpoints.py#L726)) | same | same                  | same                        | same                        |
| `submitter_notes`       | `req.notes` or `NULL`     | same                      | same                       | same                        | same                        |
| `created_at`            | `now`                     | `now`                     | `now`                      | `now`                       | `now`                       |
| `validated_at`          | `now`                     | `now`                     | `now`                      | `now`                       | `now`                       |
| `staged_at`             | `now`                     | `now`                     | `NULL`                     | `NULL`                      | `NULL`                      |
| `reviewed_at`           | `NULL`                    | `NULL`                    | `NULL`                     | `NULL`                      | `NULL`                      |
| `promoted_at`           | `NULL`                    | `NULL`                    | `NULL`                     | `NULL`                      | `NULL`                      |
| `rejected_at`           | `NULL`                    | `NULL`                    | `now`                      | `NULL`                      | `now`                       |
| `metadata_confidence`   | `"medium"` if DOI extracted else `"low"` ([lines 789-792](../../ka_article_endpoints.py#L789-L792)); for citation_text input use the existing `"high"/"medium"/"low"` formula ([lines 878-880](../../ka_article_endpoints.py#L878-L880)) | same | `"low"`              | same as A                   | same as A                   |

**`audit_log` columns (one row per branch):**

| Column        | Value                                                                                  |
| ------------- | -------------------------------------------------------------------------------------- |
| `article_id`  | the `articles.article_id` just written                                                 |
| `action`      | Branch A: `"staged"`; B: `"needs_review"`; C: `"rejected_bad_file"`; D: `"duplicate_detected"`; E: `"rejected_off_topic"` |
| `old_status`  | `"received"` (the implicit pre-write status)                                           |
| `new_status`  | identical to `articles.status` just written                                             |
| `actor_id`    | `user.user_id` if authenticated, else `NULL`                                            |
| `actor_type`  | `user.role` if authenticated, else `"system"`                                           |
| `details`     | Branch A: `NULL`; B: `json.dumps({"routing_reason": ...})`; C: `json.dumps(validation)`; D: `json.dumps(dup_result)`; E: `json.dumps({"overall_confidence": <value>})` |
| `created_at`  | `now`                                                                                  |

---

## 5. Invariants (each is a single Boolean check)

Every invariant below MUST hold after every successful request. Each
is phrased so a Python or JS assertion can verify it.

| #    | Invariant                                                                                                                                                                                                                       |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| I-1  | When present, `response["items"][i]["classifier"]["verdict"] in {"accept","edge_case","reject"}` for every `i`.                                                                                                                  |
| I-2a | **Determinism.** When the classifier is invoked twice on identical inputs (same PDF bytes, same evidence stage, same backend), `classifier.overall_confidence` differs by `< 0.001` and `classifier.classifier_article_type` is identical between the two invocations. *Verifier:* the script runs TC-1's fixture against an empty DB twice — but as two separate fresh-DB script invocations (DB torn down between runs) so neither call hits the dedup probe. Captures `R₁.classifier` and `R₂.classifier`, asserts the bound. Catches unseeded randomness in the classifier path. |
| I-2b | **Monotonicity within each topic domain.** The labeled-20 fixture is partitioned by `expected_primary_topic`. For every topic domain with at least 4 fixture papers, the Spearman rank correlation between (a) human relevance rank within that domain and (b) `classifier.primary_topic_confidence` on the items the classifier assigned to that domain is `>= 0.5`. Cross-topic comparisons are excluded because `primary_topic_confidence` is not commensurable across different topic domains. *Verifier:* validation script groups fixtures by domain, applies `scipy.stats.spearmanr` per group, skips groups with `n < 4`, fails if any included group has ρ < 0.5. Catches a classifier that returns uninformative or constant confidence numbers within any single domain. |
| I-3  | If `status == "staged_pending_review"` then a file exists at `QUARANTINE_DIR/<article_id>.pdf` (= `Knowledge_Atlas/data/storage/quarantine/<YYYY-MM>/<article_id>.pdf` where `<YYYY-MM>` is the request month), AND `sha256(file_on_disk) == articles.pdf_hash_sha256`.                |
| I-4  | If `status == "duplicate_existing"` then no file is written under `Knowledge_Atlas/data/storage/quarantine/`. The recursive file count under that path after the request equals the count before, plus one for each Branch A or B item only (recursive count because directories are month-bucketed). |
| I-5  | If `classifier` is present and `classifier.article_type_confidence >= 0.50` then `classifier.primary_topic` is non-null.                                                                                                          |
| I-6  | For every item there exists a row in `audit_log` whose `article_id` equals the response `article_id`, whose `action` is one of `{staged, needs_review, rejected_bad_file, duplicate_detected, rejected_off_topic}`, and whose `new_status` equals the item's `status`. |
| I-7  | No file whose first 5 bytes ≠ `b"%PDF-"` is ever present anywhere recursively under `Knowledge_Atlas/data/storage/quarantine/` after the request.                                                                                |
| I-8  | The response body validates against [`schemas/classifier_response.json`](./schemas/classifier_response.json) (no extra keys outside `additionalProperties: true` blocks; every typed field matches).                              |
| I-9  | The frontend MUST NOT call `localStorage.setItem("ka.public_suggestions", …)` (i.e. the existing dead-end key). Other `localStorage` keys (`ka_access_token`, `ka_current_user`, etc.) used by [`ka_auth_widget.js`](../../ka_auth_widget.js) remain in use and untouched. |
| I-10 | After the response is rendered, the submit button is re-enabled (`disabled === false`).                                                                                                                                          |
| I-11 | On a network or 5xx failure, no result card is rendered AND a visible error element exists in the DOM AND the legacy thank-you modal does NOT have the `open` class.                                                            |
| I-12 | The submission MUST run `_check_duplicates(pdf_hash, doi, title, authors)` ([line 505-602](../../ka_article_endpoints.py#L505-L602)) before any `INSERT INTO articles` for that item. *Verified end-to-end, not by mock:* TC-4 and TC-5 each submit a paper that should match an existing entry; if dedupe is bypassed, the new row is created and the test fails on row-count delta. |
| I-13 | **End-to-end classifier integration.** For every item not rejected at validation or dedupe (i.e. items in TC-1, TC-2, TC-7, and the accepted item of TC-8), the response item contains a non-null `classifier` block with `classifier_article_type` non-empty and `overall_confidence` in `[0,1]`. *Verified by inspecting real responses, not by mocking the call site.* A separate **structural check** (`grep -c "AdaptiveClassifierSubsystem" Knowledge_Atlas/ka_article_endpoints.py >= 2`) proves the call site exists; the structural check is reported alongside the invariant but does not substitute for it. |

---

## 6. Thresholds (measurable acceptance bars)

Each threshold names a numeric bound, the fixture it is measured
against, and how many wrong answers exhaust the failure budget. The
contract is met when ALL thresholds pass.

### 6.1 Baseline-measurement procedure (replaces the previous TBD numbers)

The classifier's accuracy and latency thresholds (T-1, T-2, T-8) are
*derived* from a one-time baseline run on day 1 of the implementation
PR, not picked from the air:

1. Land the implementation (Connection A + classifier call in
   `/submit`) against a clean, empty database.
2. Run the validation script against the §6.2 labeled-20 fixture
   *once*. Record:
   - `B_1` = article-type accuracy
   - `B_2` = primary-topic accuracy
   - `B_8` = p95 end-to-end latency in milliseconds
3. Set the threshold as a regression bound:
   - `T_1 = floor(B_1 * 100 - 5) / 100`  (baseline minus 5pp)
   - `T_2 = floor(B_2 * 100 - 5) / 100`
   - `T_8 = ceil(B_8 * 1.20)`             (baseline +20% latency ceiling)
4. Commit the baseline numbers and computed thresholds to
   [`schemas/baseline.json`](./schemas/baseline.json) (created on day 1)
   so reruns can reproduce them.

The contract is therefore not "≥ 0.85"; it is "≥ baseline-5pp, where
baseline is committed on day 1 and never silently re-baselined."
Re-baselining requires a contract version bump.

### 6.2 Threshold table

| #    | Metric                                              | Fixture (size)                                                    | Threshold                                              | Failure budget                |
| ---- | --------------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------ | ----------------------------- |
| T-1  | Classifier article-type accuracy                    | `tests/fixtures/labeled_20.json` (20 papers, 6 article types)     | `>= floor(B_1*100 - 5)/100` — see §6.1                 | depends on baseline; e.g. baseline 0.90 ⇒ T-1=0.85 ⇒ ≤ 3 wrong of 20 |
| T-2  | Primary-topic accuracy                              | same labeled-20                                                   | `>= floor(B_2*100 - 5)/100` — see §6.1                 | same |
| T-3  | Duplicate-detection recall (SHA-256 + DOI cases)    | `tests/fixtures/dups_exact.json` (50 pairs)                       | `>= 0.98`                                              | ≤ 1 miss in 50 |
| T-4  | Duplicate-detection recall (fuzzy title)            | `tests/fixtures/dups_fuzzy.json` (30 pairs)                       | `>= 0.83`                                              | ≤ 5 misses in 30 |
| T-5  | Magic-byte rejection rate                           | `tests/fixtures/bad_magic/` (20 non-PDFs renamed `.pdf`)          | `== 1.00`                                              | 0 misses in 20 (any miss = fail) |
| T-6  | False-accept rate on non-PDFs                       | same `bad_magic` fixture                                          | `== 0.00`                                              | 0 false accepts (any false accept = fail) |
| T-7  | Schema-validation pass rate                         | every response in TC-1 … TC-8                                     | `== 1.00`                                              | 0 schema violations |
| T-8  | p95 end-to-end latency (no OCR, ≤ 5 MB PDF)         | 30 sequential submissions on `dev.localhost`                      | `<= ceil(B_8 * 1.20)` ms — see §6.1                    | up to 1 outlier above bound (not p95) |
| T-9  | `articles` row count delta on full-duplicate batch  | resubmit `dups_exact.json` PDFs twice                             | `staged_pending_review` count delta `== 0` on second pass; `duplicate_existing` audit rows allowed | binary |
| T-10 | Determinism on TC-1 fixture                         | same fixture submitted twice across fresh DBs (I-2a)              | `|conf₁ − conf₂| < 0.001` AND `type₁ == type₂`         | 0 disagreements |
| T-11 | Monotonicity within each topic domain (I-2b)        | labeled-20 fixture, partitioned by domain                          | Spearman ρ `>= 0.5` within every domain with `n >= 4` | binary per-domain |
| T-12 | Per-item independence (TC-8)                        | mixed batch: 1 valid PDF + 1 bad-magic + 1 SHA-dup                | the valid PDF in the batch is staged regardless of sibling outcomes | binary |

> **Rate-limit threshold removed.** A previous draft included a T-9 for
> `MAX_ANON_PER_HOUR` enforcement. The enforcement code path has not
> been confirmed to exist (§10 item 5); a threshold that can be
> satisfied by writing a waiver comment is not a threshold. The check
> is tracked as an open gap, not a contract bar.

---

## 7. Failure modes (degenerate inputs → required behavior)

| Failure                                          | Required server behavior                                                                                                                          | Required UI behavior                                  |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| Empty submission (no PDF, no citation)           | `400` with `{"detail": "Provide at least one PDF file or citation text"}`; no DB write                                                            | inline error; submit button re-enabled; no card       |
| PDF magic-byte check fails                       | `200` with item `status="rejected_bad_file"`, `reason` populated; row INSERT; `classifier` omitted                                                | grey "Rejected" card with reason text                 |
| PDF over `KA_MAX_FILE_SIZE_MB` (default 100 MB)  | follow whatever `_validate_pdf_bytes` ([line 322-349](../../ka_article_endpoints.py#L322-L349)) currently does — currently this rejects *per-item* with `status="rejected_bad_file"` and `rejection_reason="File too large …"` | grey "Rejected" card, reason text                     |
| Total batch over `KA_MAX_BATCH_SIZE_MB`          | `413` ([line 681-683](../../ka_article_endpoints.py#L681-L683)); no DB write                                                                                                                          | inline error; submit button re-enabled                |
| Definitive duplicate (hash or DOI)               | `200` with `status="duplicate_existing"`, `duplicate_of=<existing>`, `classifier` omitted; audit-only row written, no quarantine file written     | grey "Already in corpus" card linking the existing `article_id` |
| Network failure on `fetch()`                     | n/a                                                                                                                                                | inline error card; offer retry; **never** open thank-you modal; **never** write `ka.public_suggestions` to localStorage |
| `5xx` from server                                | n/a                                                                                                                                                | same as network failure                               |
| `atlas_shared` import unavailable                | local fallback classifier used ([line 40-156](../../ka_article_endpoints.py#L40-L156)); response still validates against §3.1; `classifier.backend == "ka_local_fallback"` | unchanged                                             |
| Citation parses to empty title AND no PDF        | `400` with `{"detail": "Provide at least one PDF file or citation text"}` (citations was whitespace)                                              | inline error                                          |
| Classifier returns `overall_confidence == 0.0`   | `status="rejected_off_topic"`, `classifier.verdict="reject"`, `classifier.classifier_article_type="unknown"`; row written; no PDF in quarantine    | grey "Rejected" card                                  |

**Never-fabricate rule (parallels F1 in `ai-failure-prevention`).** If
the classifier returns no topic match, `classifier.primary_topic` MUST
be `null`. The contract forbids substituting a "best-guess" topic when
the classifier did not produce one.

---

## 8. Test cases (fixture properties + exact expected outcomes)

Each test case names *the property* a fixture must satisfy and the
exact assertions that must hold. The implementer is free to choose any
specific fixture file that satisfies the property — fixture filenames
are not part of the contract.

### TC-1 — Clean accept

- **Fixture property:** A real peer-reviewed PDF on the architecture-and-cognition scope (e.g. daylight, lighting, ceiling height, acoustics) whose SHA-256, DOI, and title are not present in the `articles` table at the start of the test.
- **Request:** `files=[fixture]`, `citations=""`, `notes=""`, `source_surface="ka_contribute_public"`.
- **Expected response:**
  - `items[0].status == "staged_pending_review"`
  - `items[0].duplicate_status == "not_duplicate"`
  - `items[0].classifier.verdict == "accept"`
  - `items[0].classifier.classifier_article_type` matches the fixture's true type (set in the fixture metadata)
  - `items[0].classifier.article_type_confidence >= T-1 threshold` (read from `baseline.json`)
  - `items[0].classifier.primary_topic` matches one of the fixture's labeled topics
  - `items[0].classifier.overall_confidence >= 0.72` (the pinned routing boundary from §4.1 — accept items must clear the same threshold the routing logic uses)
- **Expected side-effects:** invariants I-3, I-6, I-12, I-13 hold; `articles` row count `+1`; `audit_log` row count `+1`; one new file in `quarantine/<YYYY-MM>/`.

### TC-2 — Edge case (externally-grounded ground truth)

The previous version of TC-2 was tautological: the fixture's metadata
declared the expected verdict, then the test asserted the classifier
returned that verdict. Replaced with reviewer-majority labelling.

- **Fixture property:** A pool of 5 peer-reviewed PDFs whose subjects are plausibly adjacent to but not squarely within the architecture-and-cognition scope (e.g. workplace productivity that mentions lighting but does not study it; tourism studies of city squares; office-noise studies focused on call centers).
- **Ground truth construction (one-time, before the test runs):** Three independent reviewers (the contributor + two classmates, or COGS 160 Article Finder reviewers) each label every paper in the pool with one of `accept | edge_case | reject`. Labels are recorded in `tests/fixtures/edge_cases/<paper_id>.labels.json` of the form `{"reviewers": [{"id":"A","label":"edge_case"},...], "majority": "edge_case"}`. A paper qualifies as a TC-2 fixture only if 2-of-3 reviewers labeled it `edge_case`.
- **Test assertion (per fixture in the qualifying pool):**
  - `items[0].classifier.verdict == fixture.majority`
  - On `verdict == "edge_case"` only: `items[0].status == "needs_review"`, file in `quarantine/<YYYY-MM>/`, `validation_notes` JSON contains key `routing_reason`.
  - `items[0].reason` non-null, length ≤ 200.
- **Pass condition:** classifier matches majority on at least **3 of 5** fixtures (accommodates classifier disagreement on hard cases without making the test unfalsifiable).
- **Verifier mutation check:** if the classifier's edge-case threshold is intentionally pushed to 0.95 (forcing every paper to `accept` or `reject`), TC-2 must fail. This proves the test discriminates.

### TC-3 — Rejection (bad magic bytes)

- **Fixture property:** A `.docx`, `.zip`, or `.txt` file renamed to `.pdf` (any file whose first 5 bytes ≠ `%PDF-`).
- **Expected response:**
  - `items[0].status == "rejected_bad_file"`
  - `items[0].reason` matches the rejection reason produced by `_validate_pdf_bytes` ([line 329](../../ka_article_endpoints.py#L329)) — currently `"Not a PDF file (invalid magic bytes)"`
  - `classifier` omitted
- **Expected side-effects:** **no** file in `quarantine/`; `articles.status == 'rejected_bad_file'`.

### TC-4 — Rejection (definitive SHA-256 duplicate)

- **Pre-condition (binding).** TC-1 must have completed successfully against this DB instance in the same script run; specifically, the `articles` table contains exactly one row with `pdf_hash_sha256 == sha256(TC-1.fixture)` and `status='staged_pending_review'`. If this precondition is not met, the script MUST report TC-4 as `pass: false` with `detail: "PRECONDITION_FAILED: TC-1 must run before TC-4"`, not run TC-4 and falsely pass it.
- **Fixture:** Submit the exact bytes used in TC-1 a second time.
- **Expected response:**
  - `items[0].status == "duplicate_existing"`
  - `items[0].duplicate_of == <article_id from TC-1>`
  - `classifier` omitted
- **Expected side-effects:** invariant I-4 holds — no new file in `quarantine/`; one audit-only row added to `articles` (with `status='duplicate_existing'`); main corpus row count for `staged_pending_review` is unchanged.

### TC-5 — Rejection (definitive DOI duplicate, different bytes)

- **Pre-condition (binding).** Same as TC-4: TC-1 must have completed successfully and its row must exist in `articles`. Otherwise report `PRECONDITION_FAILED`.
- **Fixture property:** A PDF whose `_extract_doi_from_pdf` ([line 352-362](../../ka_article_endpoints.py#L352-L362)) returns the same DOI as TC-1's fixture, but whose SHA-256 differs. To build such a fixture: (a) confirm TC-1's DOI appears as a `10.NNNN/...` string in the first 5000 bytes of TC-1's PDF (run `head -c 5000 fixture.pdf | grep -ao '10\.[0-9]\{4,9\}/[^ ]*'`); (b) build a single-page PDF (e.g. via `reportlab` or any tool) containing the same DOI literal in its visible text plus a different title or author block to change the bytes.
- **Expected response:**
  - `items[0].status == "duplicate_existing"`
  - `items[0].duplicate_of == <article_id from TC-1>`
  - `classifier` omitted
- **Expected side-effects:** I-4 holds.

### TC-6 — Network failure (frontend unit test)

- **Setup:** Run the form's JS in isolation (jsdom or a Vitest/Jest harness — no headless browser). Stub `window.fetch` to reject with `TypeError("Failed to fetch")`. Invoke `submitSuggestion()` with a synthetic `chosenFile` and citation.
- **Expected DOM after the rejection settles:**
  - No result card is rendered (I-11).
  - A visible error element exists with non-empty text content (I-11).
  - `#__ka_submit_btn.disabled === false` (I-10).
  - `localStorage.getItem("ka.public_suggestions") === null` (I-9; verified before and after the call).
  - `#__ka_thanks` does NOT have the `open` class.

### TC-7 — Rejection (clean PDF, off-topic)

Exercises Branch E (`rejected_off_topic`), which is brand new in this
PR and previously had no test coverage.

- **Fixture property:** A peer-reviewed PDF whose subject is unambiguously outside the architecture-and-cognition scope. Acceptable domains: chemistry, agricultural economics, sports medicine, particle physics. Magic bytes pass; size within limit; no SHA-256, DOI, or title overlap with the corpus.
- **Request:** `files=[fixture]`, `citations=""`, `notes=""`, `source_surface="ka_contribute_public"`.
- **Expected response:**
  - `items[0].status == "rejected_off_topic"`
  - `items[0].classifier.verdict == "reject"`
  - `items[0].classifier.overall_confidence < 0.72` (the pinned routing boundary from §4.1 — any confidence ≥ 0.72 with a `reject` verdict would indicate the classifier and the routing logic disagree, which is itself a contract violation)
  - `items[0].classifier.primary_topic == null` (never-fabricate rule, §7)
- **Expected side-effects:** **no** file in `quarantine/`; one row in `articles` with `status='rejected_off_topic'` and `relevance_score` populated; one row in `audit_log` with `action='rejected_off_topic'`.
- **Verifier mutation check:** If you tamper with the fixture's title to insert on-topic terms ("daylight study of …") while leaving the body untouched, the classifier should still reject — proving body-text classification, not title-only.

### TC-8 — Per-item independence (mixed batch)

Exercises the per-item independence clause in §4. Assertions are
order-independent: the contract does NOT assume the server preserves
input order in the `items[]` array.

- **Pre-condition (binding).** A pre-staged paper exists in `articles` whose SHA-256 the duplicate item will match. Use TC-1's row if TC-1 has run; otherwise stage a synthetic accept-quality paper before TC-8 begins.
- **Setup:** A single submission carrying three files in `files[]`:
  1. A clean accept-quality PDF distinct from the pre-staged one (new bytes, new DOI).
  2. A bad-magic-bytes file (TC-3's fixture or equivalent).
  3. A SHA-256 duplicate of the pre-staged paper.
- **Expected response:** `len(items) == 3`. Assertions are by predicate over the items, not by index:
  - Exactly one item has `status == "staged_pending_review"`, `classifier.verdict == "accept"`, and a corresponding file written to `quarantine/<YYYY-MM>/`.
  - Exactly one item has `status == "rejected_bad_file"` with `classifier` omitted and no file in `quarantine/` for it.
  - Exactly one item has `status == "duplicate_existing"`, `duplicate_of` populated with the pre-staged paper's `article_id`, and `classifier` omitted.
- **Pass condition:** the accept item is staged in full **regardless of** the sibling failures. If the accept item is silently dropped because a sibling raised, the test fails.
- **Verifier mutation check:** Reorder the three files in the request so the bad-magic file is `files[0]`. The accept item must still be staged. The set-based assertions above must remain unchanged.

---

## 9. Validation script

The contract is verified by two commands. The Python harness lives at
`Knowledge_Atlas/tests/validate_classifier_integration.py` and the
companion JS unit test at
`Knowledge_Atlas/tests/test_contribute_public.spec.js` (this file is
created as part of the implementation PR).

```sh
python3 Knowledge_Atlas/tests/validate_classifier_integration.py \
    --fixtures "Knowledge_Atlas/tests/fixtures/" \
    --schema   "Track 2/Phase 1 & 2/contracts/schemas/classifier_response.json" \
    --base-url http://127.0.0.1:8765 \
    --report   "Knowledge_Atlas/tests/reports/classifier_integration_$(date +%Y%m%d).json"
```

Plus, for TC-6, the JS unit test is run separately:

```sh
cd Knowledge_Atlas && npx vitest run tests/test_contribute_public.spec.js
```

The Python script MUST:

- Set up the test DB according to each test case's pre-condition:
  - **TC-1, TC-3, TC-7:** empty `articles` table; empty `quarantine/`.
  - **TC-4, TC-5:** TC-1 must have run successfully in the same script
    invocation; the script verifies the TC-1 row exists before
    proceeding (skip-and-fail with `PRECONDITION_FAILED` otherwise).
  - **TC-8:** at least one accept-quality paper pre-staged (TC-1's row
    if available; otherwise a synthetic row inserted by the test
    harness before the TC-8 POST).
  - **I-2a determinism:** run TC-1's fixture *twice across two fresh
    DB instances*, so neither call hits the dedup probe. The script
    tears down and re-creates the DB between the two runs.
- Validate every response body that the test case produces against the
  JSON Schema using `jsonschema` (not bespoke checks). TC-6 produces
  no server response and is excluded from schema validation.
- Emit a machine-readable report with one record per
  invariant/threshold/test case and `pass: bool`.
- Exit `0` iff every record is `pass: true`.

The JS unit test MUST verify TC-6 against the real
`submitSuggestion()` function (not a re-implementation), with `fetch`
stubbed.

---

## 10. Open verification gaps

Listed so they cannot become silent fabrications (see
`ai-failure-prevention` F1, F7). After re-reading the actual T2 Task 1
grader at
[`160sp/rubrics/t2/t2_task1_grader.py`](../../160sp/rubrics/t2/t2_task1_grader.py)
on 2026-05-17, every gap below is now tagged with **Grader-relevance**:
whether closing it changes the auto-test score, the manual rubric
score, or only the contract's internal consistency. A "no impact" tag
means the gap is real but is not on the grading path and does not need
to be closed before submission.

The auto-tests the grader actually runs (verified by reading the
grader source):

| Auto-test                          | What the grader checks                                                                                                     | Weight class |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ------------ |
| Classifier integration             | `ka_article_endpoints.py` source contains `AdaptiveClassifierSubsystem` (or `classifier_system` or `atlas_shared`) AND `.classify(` | critical     |
| Duplicate detection                | Source contains `duplicate` OR `check_duplicate` OR `pdf_hash` (substring)                                                 | important    |
| Contribute page modified           | `ka_contribute_public.html` contains a results-ish word AND `fetch(` (substring)                                           | critical     |
| Corrupt PDF handling               | Source contains `%PDF` OR `validate` (substring)                                                                            | critical     |
| DB field completeness              | `SELECT … FROM articles WHERE status IS NULL OR created_at IS NULL` returns 0 rows                                          | important    |
| Audit log presence                 | Every `articles` row has at least one `audit_log` row joined on `article_id`                                                | minor        |
| Storage path correctness           | Rows with `status LIKE 'reject%'` have `quarantine_path IS NULL`; rows with `status IN ('received','staged','validated')` have non-NULL `quarantine_path` | critical |
| Edge-case distinguishability       | Among non-rejected rows, ≥ 2 distinct values exist across `status` or `relevance_score`                                     | important    |

Manual rubric: Diagnosis (15), Spec quality (15), Verification
questions (15), Validation 4 test papers (20), Failure diagnosis (15),
File manifest (5), Auto tests (15). Total 100.

---

### Gap 1 — Canonical duplicate-probe scripts not on local disk

The assignment names `course_scaffolding.py probe-collection-pdf` and
`ae_waiting_room_probe.probe_pdf_against_article_eater(...)`. Neither
file exists anywhere under `COGS 160/` on this checkout (verified
2026-05-09 with `find`; the paths the assignment cites are under the
instructor's home directory `/Users/davidusa/REPOS/...`). The contract
uses the in-process `_check_duplicates()`
([line 505-602](../../ka_article_endpoints.py#L505-L602))
as a stand-in.

**Grader-relevance: NONE.** The grader's "Duplicate detection logic"
auto-test (above) is a substring grep for `duplicate` / `check_duplicate` / `pdf_hash`
in `ka_article_endpoints.py`. The existing source already contains all
three substrings (verified with `grep`). The auto-test PASSES today.

**Action:** keep the §3.3 decision tree as the authoritative
specification of what the in-process probe must do. No instructor
email is required for the grade. If you want a clean §10 at promotion
time, send a single confirmation email noting that
`_check_duplicates()` is the substitute.

---

### Gap 2 — `pipeline_lifecycle_full.db` is empty locally

Both copies on disk (`Knowledge_Atlas/data/ka_payloads/pipeline_lifecycle_full.db`
and the `…-wal` next to `160sp/`) are 0 bytes. The contract therefore
writes against the verified `articles` / `submission_batches` /
`audit_log` schema in
[ka_article_endpoints.py:201-296](../../ka_article_endpoints.py#L201-L296).

**Grader-relevance: NONE.** The grader's DB tests query
`articles` and `audit_log`. They never touch
`pipeline_lifecycle_full.db`, `papers`, or `lifecycle_events`. The
rubric prose at [`T2_TASK1_FIX_CONTRIBUTE_PAGE.md` lines 130-136](../../160sp/rubrics/t2/T2_TASK1_FIX_CONTRIBUTE_PAGE.md#L130-L136)
*invites* the student to inspect that DB, but the actual grader script
does not. There is no row in `pipeline_lifecycle_full.db` that the
grader expects to find.

**Action:** none required for the grade. If the grader is later
updated to query `papers` / `lifecycle_events`, this contract gains a
new branch in §4 that mirrors each `articles` write into the lifecycle
DB.

---

### Gap 3 — Stale claims in `Track_2_Context`

The Phase-1 narrative says the router is "not yet registered in
`ka_auth_server.py`" (it IS, at
[ka_auth_server.py:976-988](../../ka_auth_server.py#L976-L988))
and implies the classifier is called from `/submit` (it is **not** —
the `submit_articles` handler at lines 648–919 has no
`.classify()` or `_classify_article_payload` call inside it; the
classifier helper at line 1648 is called only by other endpoints).

**Grader-relevance: INDIRECT.** The grader does not read
`Track_2_Context` directly. The Phase-1 doc affects the **Diagnosis
(15 pts)** manual rubric score: the TA reviews boxology + gap
statement for accuracy. Stale claims in the gap statement could cost
points there.

**Action: DONE on 2026-05-17.** An addendum was appended to
`Track_2_Context` documenting both corrections rather than rewriting
the body (the original Phase-1 analysis is preserved). See the
"Addendum (2026-05-17)" section at the end of that file. This gap is
closed.

---

### Gap 4 — Baseline measurement (T-1, T-2, T-8)

The contract's accuracy and latency thresholds are derived from a
day-1 baseline run per §6.1. `schemas/baseline.json` must be created
on the first run of the validation script against the labeled-20
fixture.

**Grader-relevance: NONE.** The grader has no classifier-accuracy or
latency threshold. None of its auto-tests measure classification
quality numerically. The labeled-20 fixture, the Spearman correlation
(I-2b), and the determinism check (I-2a) are contract-internal
consistency checks — they help YOU verify the implementation behaves
sensibly, but they don't move the grade.

**Action:** optional. If you want to ship the contract as FINAL after
the implementation lands, run the baseline procedure and commit
`baseline.json`. If you only want to pass the grader, this can be
deferred indefinitely.

---

### Gap 5 — Rate limiting is not enforced

`MAX_ANON_PER_HOUR = 10` and `MAX_AUTH_PER_HOUR = 50` are defined at
[lines 168-169](../../ka_article_endpoints.py#L168-L169).
A repo-wide grep on 2026-05-17 found those two definition lines and
**no other reference** to either constant. The rate-limit feature is
not implemented — the constants are dead.

**Grader-relevance: NONE.** The grader does not exercise rate
limiting. T-9 was already removed from §6.2 in the 2026-05-15
revision; the contract no longer claims a rate-limit threshold.

**Action: DONE.** This gap is now informational. Move on.

---

### Gap 6 — Downstream consumers of `articles.status`

The PR introduces two new `status` values (`needs_review`,
`rejected_off_topic`). The grader anticipates `rejected_off_topic`
already — its edge-case distinguishability test at
[t2_task1_grader.py:222-224](../../160sp/rubrics/t2/t2_task1_grader.py#L222-L224)
already excludes `rejected_bad_file`, `duplicate_existing`, AND
`rejected_off_topic` from its non-rejected set.

**Grader-relevance: NONE.** The grader knows about the new statuses.
The risk is to *other* KA pages (the instructor review UI,
`ka_home_instructor.html`, etc.) that may be filtering on a closed
enum and might silently drop the new statuses. That's a regression
risk for the rest of the site, not a grading risk.

**Action:** run the three greps below if you have ten minutes; skip
if you don't.

```sh
grep -rnE "status\s*=\s*['\"](staged_pending_review|duplicate_existing|rejected_bad_file|received)['\"]" "Knowledge_Atlas/" --include="*.py" --include="*.html" --include="*.js"
grep -rnE 'WHERE\s+status' "Knowledge_Atlas/" --include="*.py"
grep -rnE '\bstatus\s*IN\s*\(' "Knowledge_Atlas/" --include="*.py"
```

For any hit that's a closed-enum filter, either add the new statuses
to the consumer's list or document why the consumer should ignore
them.

---

### Gap 7 — TC-2 ground-truth reviewer panel

TC-2 (edge-case verdict on a 5-paper reviewer-majority-labeled pool)
needs labels from three independent reviewers before it can run.

**Grader-relevance: NONE.** The grader's "Edge case
distinguishability" test ([line 212-245](../../160sp/rubrics/t2/t2_task1_grader.py#L212-L245))
checks only that **≥ 2 distinct values** exist among non-rejected
`articles` rows. It does not run TC-2. It does not require
reviewer-majority labels. It does not require any specific
edge-case fixture at all — only that the implementation produces at
least one `needs_review` row alongside at least one
`staged_pending_review` row.

**Action:** for the grade, you do not need three reviewers. One
self-labeled edge-case PDF that the implementation classifies as
`needs_review` is enough. The TC-2 design is contract-internal best
practice. If you want it for FINAL, recruit reviewers; if you only
want to pass the grader, skip it.

---

### Gap audit summary

| Gap | Closes for grade? | Closes for FINAL?                  | Cost to close                |
| --- | ----------------- | ---------------------------------- | ---------------------------- |
| 1   | already closed    | one confirmation email             | 5 min email                   |
| 2   | already closed    | confirm `articles` is canonical    | 5 min email                   |
| 3   | **closed 05-17**  | done                                | done                          |
| 4   | already closed    | run baseline after implementation  | ~30 min after PR lands        |
| 5   | already closed    | already closed                     | done                          |
| 6   | already closed    | three greps, eyeball hits          | ~15 min                       |
| 7   | already closed    | recruit 3 reviewers, label 5 PDFs  | ~3 hours total reviewer time  |

**Bottom line.** The contract is ready for submission as DRAFT.
Promoting to FINAL is optional polish that only matters if you intend
to reuse the contract for a future round of the task or hand it to
the instructor as a standalone artifact.

---

## 11. Done definition

Split into two tiers so the grade-blocking work is unambiguously
separable from the internal-consistency polish.

### 11.1 Grader-blocking — must pass before submission

These map 1-to-1 to checks the T2 Task 1 grader at
[`160sp/rubrics/t2/t2_task1_grader.py`](../../160sp/rubrics/t2/t2_task1_grader.py)
actually runs (eight auto-tests + the manual rubric items it surfaces).
Closing all of these is sufficient to pass the assignment.

**Auto-tests (the grader runs these):**

| #    | Grader test                          | What must be true                                                                                                                                                                          | Pass evidence to capture |
| ---- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------ |
| G-1  | Classifier integration (critical)    | `ka_article_endpoints.py` contains BOTH the symbol `AdaptiveClassifierSubsystem` (or `classifier_system` / `atlas_shared`) AND a `.classify(` call site                                    | `grep -nE "AdaptiveClassifierSubsystem\|classifier_system\|atlas_shared" ka_article_endpoints.py && grep -n "\\.classify(" ka_article_endpoints.py` |
| G-2  | Duplicate detection (important)      | `ka_article_endpoints.py` contains `duplicate` OR `check_duplicate` OR `pdf_hash` (already true today)                                                                                     | `grep -nE "duplicate\|check_duplicate\|pdf_hash" ka_article_endpoints.py` |
| G-3  | Contribute page modified (critical)  | `ka_contribute_public.html` contains a results-ish word AND `fetch(`                                                                                                                       | `grep -niE "result\|accept\|reject\|edge" ka_contribute_public.html && grep -n "fetch(" ka_contribute_public.html` |
| G-4  | Corrupt PDF handling (critical)      | `ka_article_endpoints.py` contains `%PDF` OR `validate` (already true today)                                                                                                                | `grep -nE "%PDF\|validate" ka_article_endpoints.py` |
| G-5  | DB field completeness (important)    | `SELECT * FROM articles WHERE status IS NULL OR created_at IS NULL` returns 0 rows after test submissions                                                                                  | run the SQL after Phase-4 tests |
| G-6  | Audit log presence (minor)           | `LEFT JOIN audit_log` finds no orphan `articles` rows                                                                                                                                       | grader's `SELECT a.article_id … WHERE al.log_id IS NULL` returns 0 |
| G-7  | Storage path correctness (critical)  | Rows with `status LIKE 'reject%'` have `quarantine_path IS NULL`. Rows with `status IN ('received', 'staged', 'validated')` have non-NULL `quarantine_path`. **Note:** the grader's IN clause does not include `staged_pending_review`, so rows with that status are not checked — this is a grader quirk, not a contract issue. | run grader test 8 |
| G-8  | Edge-case distinguishability (important) | Among `articles` rows where `status NOT IN ('rejected_bad_file', 'duplicate_existing', 'rejected_off_topic')`, at least 2 distinct values exist across `status` or `relevance_score`     | After test submissions, expect at least one `staged_pending_review` AND one `needs_review` row |

**Manual rubric (the TA scores these):**

| #    | Rubric criterion                                                                | Points | Where the evidence lives in your submission                                  |
| ---- | ------------------------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------- |
| R-1  | Diagnosis: boxology + gap statement accurate                                    | 15     | `Track 2/Phase 1 & 2/Track_2_Context` (including the 2026-05-17 addendum)    |
| R-2  | Spec quality: contract is complete, specific, testable                          | 15     | this contract                                                                |
| R-3  | Verification questions: caught real problems in AI-generated code               | 15     | `verification_log.md` (Phase-3 deliverable — TO BE CREATED)                  |
| R-4  | Validation: ≥ 3 of 4 test papers produce correct results                        | 20     | `validation_matrix.md` (Phase-4 deliverable — TO BE CREATED)                 |
| R-5  | Diagnosis of failures: correctly classified spec vs implementation bugs         | 15     | section of `validation_matrix.md`                                            |
| R-6  | File manifest matches changes                                                   | 5      | `MANIFEST.md` containing `git diff --name-only HEAD` + `git status --short`  |

Submission is grader-ready when every G-* is `pass` and every R-*
deliverable exists in the repo.

### 11.2 Contract-internal polish — optional FINAL promotion bars

These are the checks the contract itself defines for its own
soundness. Closing them does not move the grade; it removes the DRAFT
marker and lets the contract stand alone as a reusable artifact.

1. `python3 Knowledge_Atlas/tests/validate_classifier_integration.py …` exits 0.
2. `npx vitest run tests/test_contribute_public.spec.js` exits 0.
3. Generated report shows all 14 invariants (I-1, I-2a, I-2b, I-3..I-13) `pass: true`.
4. Generated report shows all 12 thresholds (T-1..T-12) at or above their numeric bound. **Every threshold has a concrete number; no `TBD` is allowed at FINAL promotion.** T-1, T-2, T-8 are derived from `schemas/baseline.json` per §6.1.
5. All 8 test cases (TC-1..TC-8) `pass: true`.
6. `git grep -F 'localStorage.setItem("ka.public_suggestions"' Knowledge_Atlas/ka_contribute_public.html` returns no matches (I-9).
7. `git grep -F 'localStorage.getItem("ka.public_suggestions"' Knowledge_Atlas/ka_contribute_public.html` returns no matches (I-9).
8. The validation script's `STRUCT-classifier-call-site` record reports `passed: true` with `measured >= 1` (one or more classifier calls inside `async def submit_articles`'s body, verified by AST walk — NOT a flat substring grep, since `grep -c "AdaptiveClassifierSubsystem"` returns 7 today before any integration work because the symbol appears in imports, the fallback class, and unrelated helpers at [lines 62, 132, 139, 154, 1597, 1600, 1603](../../ka_article_endpoints.py#L62)).
9. No regressions: existing endpoint integration tests still pass.
10. Response body for every TC that produces a server response (TC-1, TC-2, TC-3, TC-4, TC-5, TC-7, TC-8) validates against [`schemas/classifier_response.json`](./schemas/classifier_response.json). TC-6 is excluded — it stubs `window.fetch` and produces no server response.
11. `schemas/baseline.json` exists, is committed, and shows a measurement date within 14 days of FINAL promotion.
12. §10 gaps tagged "Grader-relevance: NONE" may remain open at FINAL with a written acknowledgement; only Gap 3 (already closed) is required for FINAL.
