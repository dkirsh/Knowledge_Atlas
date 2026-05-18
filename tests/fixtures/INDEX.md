# Fixture index — Classifier Integration Contract

Spec: `Track 2/Phase 1 & 2/contracts/CLASSIFIER_INTEGRATION_CONTRACT_2026-05-09.md`

This directory holds every fixture the validation script
(`validate_classifier_integration.py`) needs. Each subdirectory is named
after the test case or threshold it serves. Filenames are not part of
the contract — only the *property* listed below is. The validator picks
the first file in each directory that satisfies the property.

## Layout

```
tests/fixtures/
├── INDEX.md                          # this file
├── tc1_clean_accept/                 # TC-1 (one PDF; on-topic)
├── tc3_bad_magic/                    # TC-3 (≥ 1 non-PDF renamed to .pdf)
├── tc7_off_topic/                    # TC-7 (one PDF; clearly outside scope)
├── tc8_mixed_batch/                  # TC-8 (one accept + one bad-magic + one SHA-dup)
├── edge_cases/                       # TC-2 (5 PDFs + reviewer label JSONs)
├── labeled_20.json                   # T-1, T-2, I-2b — 20-paper labeled fixture
├── dups_exact.json                   # T-3 — 50 SHA/DOI pairs
├── dups_fuzzy.json                   # T-4 — 30 fuzzy-title pairs
└── baseline.json                     # captured day-1 baseline (T-1, T-2, T-8)
```

## Required property per fixture

### `tc1_clean_accept/`
A real peer-reviewed PDF on architecture-and-cognition (daylight,
lighting, ceiling height, acoustics, biophilia, …). At test start its
SHA-256, DOI, and title MUST NOT be present in the `articles` table.

### `tc3_bad_magic/`
At least one file with a `.pdf` extension whose first 5 bytes are NOT
`%PDF-`. Any of: a `.docx` renamed; a `.zip` renamed; a 0-byte file; a
text file. Use 20 such files for T-5/T-6 thresholds.

### `tc7_off_topic/`
A real peer-reviewed PDF whose subject is unambiguously outside
architecture-and-cognition. Acceptable domains: chemistry, agricultural
economics, sports medicine, particle physics. Magic bytes must pass.

### `tc8_mixed_batch/`
Three files: `accept.pdf` (a clean accept-quality PDF, can reuse
`tc1_clean_accept/`), `bad.pdf` (reuse `tc3_bad_magic/`), and a SHA-256
duplicate of an article already staged in the test DB.

### `edge_cases/`
A pool of 5 PDFs plausibly adjacent to architecture-and-cognition but
not squarely within it. Each PDF is paired with
`<paper_id>.labels.json`:

```json
{
  "paper_id": "edge_001",
  "filename": "tourism_city_squares_2019.pdf",
  "reviewers": [
    {"id": "A", "label": "edge_case", "notes": "topic touches public space but study is methodologically about wayfinding"},
    {"id": "B", "label": "edge_case", "notes": ""},
    {"id": "C", "label": "accept",    "notes": "I think this counts — they measure cognition outcomes"}
  ],
  "majority": "edge_case"
}
```

Paper qualifies for TC-2 only if 2-of-3 reviewers labeled it
`edge_case`. A paper is dropped from the pool if it does not.

### `labeled_20.json`
20 papers spanning all 6 article types, each pre-labeled with the
ground truth and a human-rated topic-relevance rank (1 = most relevant
to its primary topic; 20 = least). Schema:

```json
{
  "version": "1.0",
  "papers": [
    {
      "paper_id": "lbl_001",
      "filename": "boubekri_2014.pdf",
      "expected_article_type": "experimental",
      "expected_primary_topic": "daylight_and_cognition",
      "human_relevance_rank": 1,
      "doi": "10.1016/j.jenvp.2014.02.003"
    }
  ]
}
```

Used by T-1, T-2, and I-2b. Rank ordering matters for I-2b's Spearman
correlation.

### `dups_exact.json`
50 pairs of papers known to be the same article (re-uploads, preprint
+ published, mirror PDFs). Each pair lists either a SHA-256 match, a
DOI match, or both. Used by T-3.

### `dups_fuzzy.json`
30 pairs with title overlap of ≤ 1 word edit distance but no SHA / DOI
match (e.g., subtitle variations, dropped articles, preprint-vs-final
titles). Used by T-4.

### `baseline.json`
Created on day 1 of the implementation PR by running the validation
script against `labeled_20.json`. Captures `B_1`, `B_2`, `B_8` and the
derived `T_1`, `T_2`, `T_8` numbers. Schema:

```json
{
  "captured_at": "2026-05-09T18:30:00Z",
  "captured_by": "kaden",
  "classifier_backend": "atlas_shared",
  "classifier_git_sha": "<commit-sha-of-atlas_shared-at-measurement>",
  "B_1_article_type_accuracy":   0.90,
  "B_2_topic_accuracy":          0.78,
  "B_8_p95_latency_ms":          1850,
  "T_1": 0.85,
  "T_2": 0.73,
  "T_8": 2220,
  "formula": "T_1 = floor(B_1*100 - 5)/100; T_2 = floor(B_2*100 - 5)/100; T_8 = ceil(B_8 * 1.20)"
}
```

Re-baselining (changing these numbers after merge) requires bumping
`contract_version` in
`Track 2/Phase 1 & 2/contracts/schemas/classifier_response.json`.

## Recruiting reviewers for `edge_cases/`

The TC-2 ground-truth requires labels from three independent reviewers.
This is the contract's only fixture that depends on humans rather than
files-on-disk. To unblock TC-2:

1. Pick 5 candidate edge-case PDFs from the KA candidate pool.
2. Send each candidate to three reviewers (yourself + 2 classmates,
   or 3 COGS 160 Article Finder reviewers).
3. Collect their `accept | edge_case | reject` labels into the JSON
   schema above.
4. Drop any candidate that does not reach 2-of-3 `edge_case` majority.
5. If fewer than 5 candidates survive, repeat with additional candidates
   until you have a 5-paper qualifying pool.
