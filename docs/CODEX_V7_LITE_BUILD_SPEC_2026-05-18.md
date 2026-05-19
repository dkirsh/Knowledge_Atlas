# V7-Lite ingest pipeline — build specification for Codex
*Date: 2026-05-18 · Author: CW · Reviewer: DK · Target implementer: Codex (Article_Eater_PostQuinean_v1_recovery)*

## What this document is

A build specification for the *V7-Lite ingest pipeline* — the synchronous-return subset of the existing V7 paper-processing pipeline, used by the Knowledge Atlas Week-1 wireframe's Surface 4 Path B (paper-not-in-corpus → student-uploads-PDF → system-evaluates). The full V7 pipeline (visual cropping, science-writer summary, full PNU extraction, full Toulmin warrants) is too slow for the in-session student interaction; V7-Lite is the minimal subset that returns within ~5 minutes and produces a structured evaluation matching the student-facing schema in `160sp/ka_week1_wireframe_2026-05-17.html#s4`.

The spec is built against the existing V2 credence architecture in `Article_Eater_PostQuinean_v1_recovery/ae.db` (per AG's handoff at `docs/CLAUDE_HANDOFF_V2_CREDENCE_2026-05-18.md`). It assumes the schema described there — the three-credence fields, the warrant-richness fields, the severity field, the scope metadata, the mechanism-chain-quality records, and the theory entrenchment table — is the substrate. V7-Lite writes into this schema as a partial-row first pass; the full V7 pipeline lands hours later and incrementally completes the row.

This is a Codex-owned build. CW supplies the spec; Codex owns the implementation, the testing, and the integration with the existing pipeline infrastructure.

## Caller contract

V7-Lite is invoked from the Knowledge Atlas web tier when a student on Surface 4 enters a DOI or paper title that the corpus does not contain. The caller supplies:

```
POST /api/v7_lite/ingest
Content-Type: multipart/form-data

doi: string (optional)
title: string (optional)
authors: string (optional)
year: int (optional)
pdf: file (required if not in corpus)
session_id: string (student session, for queue tracking)
```

The endpoint returns within ~5 minutes with one of three structured responses:

```
{
  "status": "admitted",
  "paper_id": "PDF-XXXX",
  "evaluation": { ... see "Evaluation schema" below ... },
  "queued_for_full_v7": true,
  "queue_eta_minutes": 90-180
}

{
  "status": "rejected_out_of_scope",
  "reason": "Topic-similarity below threshold; closest match was 'attention restoration' at 0.41 vs threshold 0.55",
  "nearest_topics": [ ... three corpus topics with similarity scores ... ],
  "new_topic_seed_offered": true,
  "new_topic_seed_id": "SEED-2026-018"
}

{
  "status": "error",
  "error_code": "PDF_PARSE_FAILED" | "CLASSIFIER_TIMEOUT" | "EMBEDDING_DOWN" | ...,
  "message": "human-readable",
  "retryable": true | false
}
```

The third response (`error`) should be rare. The first two are the normal cases.

## Pipeline stages (synchronous; return within ~5 min)

### Stage S1 — paper-type classification

Use the existing `atlas_shared.AdaptiveClassifierSubsystem`. Call interface (per the reference-paths memory):

```python
from ka_article_endpoints import classify_single_paper
result = classify_single_paper(pdf_path=path, doi=doi)
# result.paper_type ∈ {empirical, theoretical, review, meta_analysis, replication, ...}
# result.design_subtype ∈ {between_subjects, within_subjects, observational, RCT, ...}
# result.confidence: float
```

The classifier should run before the embedding step; its `paper_type` output filters which downstream stages run. *Empirical* papers run the full V7-Lite path. *Reviews* and *meta-analyses* skip IV/DV extraction (they don't have one) and instead extract their *covered topics*. *Theoretical* papers skip IV/DV and extract only their *central claims*. *Replications* run the full path plus a *replication-target* link extraction.

Failure mode: if the classifier confidence is below 0.5, fall back to running the empirical path but flag the paper_type as "unclassified-confidence" and surface this in the student response.

### Stage S2 — embedding-based topic-fit check

Compute the paper's text embedding (use the existing embedding store from the topic-crosswalk work — Codex knows the location). Compute cosine similarity against each topic centroid in the corpus. The topic centroid is the mean of the embeddings of papers tagged with that topic.

Output:

```python
topic_similarities = [
    (topic_id="nature_views_cognitive_recovery", cosine=0.82),
    (topic_id="biophilic_design", cosine=0.78),
    ...
]
```

If the maximum cosine similarity exceeds the per-topic threshold (default 0.55; calibrate per below), the paper is admitted to that topic. If the maximum is below threshold across all topics, return `status: rejected_out_of_scope` immediately and offer the paper as a new-topic seed (see Stage S6).

The threshold calibration protocol (one-time, run by Codex against the existing corpus):

```python
# For each topic T:
#   Hold out 10 papers known to be in topic T (or all of them if N<10)
#   For each held-out paper p:
#     Compute cosine(p, centroid(T))
#   Set threshold(T) = 5th percentile of those cosines
# Persist: threshold per topic in data/v7_lite_topic_thresholds.json
```

This makes the threshold per-topic rather than a global constant. Topics with tight clusters (most papers similar to each other) have higher thresholds; topics with diffuse clusters (papers more variable) have lower thresholds. The calibration runs once when V7-Lite is initialised and is re-run when the corpus grows by more than 10% or when a new topic is added.

### Stage S3 — IV/DV extraction (empirical and replication papers only)

Reuse the existing V7 stage that extracts IV and DV operationalisations (Codex knows which stage; CW believes it is stage 7 in the current V7 pipeline, but Codex should confirm against the live code).

Output fields:

```python
iv = {
    "operationalisation": "Biophilic VR scene (real-vegetation photogrammetry) vs urban-VR scene",
    "levels": ["biophilic", "urban"],
    "exposure_duration_min": 12,
    "confound_flags": []  # e.g., ["thermal_load", "lighting_variation"]
}
dv = [
    {
        "name": "salivary cortisol",
        "type": "biomarker",
        "measurement_window": "pre vs post"
    },
    {
        "name": "backward digit span",
        "type": "task_embedded_performance",
        "measurement_window": "pre vs post"
    },
    {
        "name": "Perceived Restorativeness Scale",
        "type": "self_report_questionnaire",
        "measurement_window": "post"
    }
]
```

The `type` field on each DV is critical for Stage S5 (VR-suitability mapping).

### Stage S4 — methods extraction

Reuse the existing V7 methods-extraction stage. Output:

```python
methods = {
    "design": "between_subjects",  # or within_subjects, mixed, etc.
    "sample_n": 120,
    "sample_composition": {
        "age_range": "18-22",
        "sex_split": "62% female",
        "population": "university_students",
        "country": "South Korea"
    },
    "statistical_test": "two-way ANOVA",
    "preregistered": False,
    "open_data": False
}
```

This output feeds the scope metadata field in AG's V2 schema and the methodological-quality fingerprint.

### Stage S5 — VR-suitability mapping (NEW; CW will provide the mapper)

For each DV extracted in S3, map to the short-code taxonomy defined in `160sp/ka_vr_measurability_content_2026-05-18.md`. Per DV, output one of:

```python
{
    "dv_name": "salivary cortisol",
    "short_code": "x5.biomarker",
    "vr_tractable": False,
    "substitution_candidates": [
        {"short_code": "f4.eda", "construct_validity": 0.8, "rationale": "..."},
        {"short_code": "f4.hrv", "construct_validity": 0.7, "rationale": "..."}
    ]
}
```

The mapping logic uses a small lookup table from `data/vr_measurability_schema.json` (CW to derive from the quick-reference table in the measurability markdown; UJ-1b task). The substitution candidates are not computed by V7-Lite directly; they come from the substitution-skill API (see `docs/CODEX_SUBSTITUTION_SKILL_BUILD_SPEC_2026-05-18.md`).

### Stage S6 — conditional VOI (NEW)

Compute the paper's conditional VOI on its admitted topic. Per the VOI panel synthesis, the VOI is a 10-dimensional target vector. For V7-Lite the synchronous return only needs to compute the four targets most relevant to the recommendation:

- Target 1 (better stimuli): does the paper use better stimuli than the topic's existing corpus? Yes if the paper's stimulus class is more ecologically valid than the topic's mode.
- Target 2 (better measures): does the paper use better measures? Yes if the paper's DVs include a higher-reliability or higher-construct-validity measure than the topic's mode.
- Target 4 (confound deconfounding): does the paper deconfound a known confound in the topic? Yes if the paper's IV explicitly addresses one of the topic's known confound_flags.
- Target 10 (WEIRD-extension): is the paper's sample composition non-WEIRD? Yes if the country is non-OECD or the population is non-university-students.

Each evaluates to high / medium / low / na. The four-cell output is what the recommendation summary uses. The remaining six targets are computed by the asynchronous full V7 pipeline.

### Stage S7 — recommendation synthesis (generative)

Call an LLM through DK's **subscription CLI** (`claude -p` for the Claude subscription, or `codex exec` for the GPT subscription, whichever Codex elects for this stage) to synthesise the recommendation prose. **Subscription-CLI only, no APIs** per DK's standing constraint (grading-and-policy memory: "AI grader on Claude subscription not API" — the constraint applies project-wide, not just to grading). Prompt the LLM with the structured outputs from S1–S6 and the topic's existing meta-review (from the topic page); ask it to produce:

1. A summary line (≤25 words): "Admit", "Admit with substitution", or "Reject — out of scope".
2. A rationale paragraph (≤120 words) that explains the recommendation and references the conditional VOI cells.
3. A "next step" line that links to either the topic page (admit), the substitution-choice surface (substitute), or the new-topic-seed flow (out-of-scope).

The recommendation is *part of* the structured evaluation response, not a separate field; the front-end renders it at the top of the V7-Lite results card.

## Evaluation schema (the structured response object)

The full `evaluation` object returned in the `admitted` response:

```json
{
  "paper_id": "PDF-XXXX",
  "paper_type": "empirical",
  "paper_type_confidence": 0.91,
  "design_subtype": "between_subjects",
  "topic_fit": {
    "admitted_to": "nature_views_cognitive_recovery",
    "max_cosine": 0.82,
    "threshold": 0.55,
    "nearest_corpus_papers": [
      {"paper_id": "PDF-0007", "cosine": 0.79},
      {"paper_id": "PDF-0034", "cosine": 0.74},
      {"paper_id": "PDF-0211", "cosine": 0.71},
      {"paper_id": "PDF-0011", "cosine": 0.68},
      {"paper_id": "PDF-0089", "cosine": 0.66}
    ]
  },
  "iv": { ... S3 output ... },
  "dv": [ ... S3 output ... ],
  "methods": { ... S4 output ... },
  "vr_suitability_mapping": [ ... S5 output per DV ... ],
  "conditional_voi": {
    "target_1_better_stimuli": "medium",
    "target_2_better_measures": "na",
    "target_4_deconfounding": "low",
    "target_10_weird_extension": "high"
  },
  "recommendation": {
    "summary": "Admit with substitution",
    "rationale": "...",
    "next_step_url": "/ka_choose_measure_for_vr.html?paper_id=PDF-XXXX"
  },
  "ae_db_write_status": "partial",
  "computation_date": "2026-05-18T14:32:00Z",
  "corpus_size_at_computation": 1428
}
```

## Database integration — writes to ae.db

V7-Lite writes a partial belief record to ae.db on first ingest. The schema follows AG's V2 layout but with subset fields populated:

```sql
INSERT INTO beliefs (
    belief_id, paper_id, credence_value, epistemic_v2,
    -- ... etc, per AG V2 schema
)
VALUES (
    'belief_for_PDF-XXXX_claim_1',
    'PDF-XXXX',
    NULL,  -- credence_value computed later by full V7
    JSON_OBJECT(
        'severity', NULL,
        'mechanism_warrant', NULL,
        'entrenchment_warrant', NULL,
        'meta_analytic_warrant', NULL,
        'confounding_warrant', NULL,
        'warrant_packet_defeat_status', NULL,
        'scope', JSON_OBJECT(
            'stimulus_context', '...',
            'setting_type', '...',
            'sample_n', 120,
            'population_type', '...'
        ),
        'v7_lite_partial', true,
        'v7_lite_evaluation_date', '2026-05-18T14:32:00Z'
    )
);
```

The `v7_lite_partial` flag tells the front-end that the belief is a partial record; the article-viewer page should render it with a "Full ingest in progress" banner.

When the full V7 pipeline lands hours later, it updates the same row with the missing fields. The substitution skill and the topic page can read the partial record immediately for the four conditional-VOI fields and the V7-Lite-extracted IV/DV; everything else waits for full ingest.

## Asynchronous full V7 queue

The async queue processes the same paper through the full V7 pipeline. The queue is FIFO with two priority lanes:

- **Lane A — student-uploaded papers.** Higher priority; should land within ~2 hours so students can return the same day.
- **Lane B — bulk-ingest backfill.** Lower priority; runs overnight when Lane A is empty.

Codex owns the queue infrastructure; the existing blackboard architecture provides the substrate. Per the coordination notes, the queue uses ae.db as the source of truth for which papers are pending which stages.

## Failure modes and recovery

| Failure | Detection | Recovery |
|---|---|---|
| PDF parse failed | Stage S1 returns error | Return `status: error` with `PDF_PARSE_FAILED`; ask student to upload a different PDF version |
| Classifier timeout (>30s) | Stage S1 timeout | Return `status: error` with `CLASSIFIER_TIMEOUT`; mark retryable |
| Embedding service down | Stage S2 503 | Return `status: error` with `EMBEDDING_DOWN`; mark retryable |
| Topic similarity below threshold | Stage S2 cosine < threshold | Return `status: rejected_out_of_scope` with `new_topic_seed_offered: true`; this is normal, not an error |
| IV/DV extraction failed | Stage S3 LLM returns malformed | Retry once; if still failed, return `status: admitted` with `iv: null, dv: null` and flag for manual review |
| LLM recommendation synthesis failed | Stage S7 LLM returns malformed | Retry once; if still failed, generate a template recommendation from the structured fields without LLM and return |

All failures should be logged to the blackboard with the session_id so AG / Codex can debug after the fact.

## Testing protocol

Before V7-Lite ships, Codex should test against:

1. **In-corpus positive control.** Submit the DOI of a paper already in the corpus. Expected behaviour: short-circuit before Stage S1, return Path-A response directly from cached data.
2. **Out-of-corpus positive control.** Submit a paper known to be off-topic (e.g., a fMRI study of default-mode connectivity). Expected: `status: rejected_out_of_scope`.
3. **Out-of-corpus admit control.** Submit a paper known to be on-topic but not in corpus. Expected: `status: admitted` with appropriate topic and conditional VOI.
4. **Replication test.** Submit a paper that explicitly replicates a corpus paper. Expected: replication-target link extracted; recommendation flags as Target 8 (replication priority).
5. **Adversarial test.** Submit a paper with deliberately ambiguous topic-fit. Expected: borderline cosine; system returns whichever side of threshold it lands on with the rationale.

Each test should be runnable as a standalone CLI command so AG / Codex can re-run after future changes.

## Open questions for DK / panel-revision

1. The 0.55 default cosine threshold is illustrative. Codex's calibration run (per Stage S2) will produce per-topic thresholds; DK should review the calibrated values before V7-Lite goes live.
2. The four-target conditional VOI subset (Targets 1, 2, 4, 10) is CW's reading of the panel synthesis on what is feasible in Stage S6. Some panelists (notably Pearl) might push for Target 5 (mechanism weak-links) to be included synchronously; CW deferred it because the mechanism-chain extraction is the slowest V7 stage. DK to confirm the subset.
3. The new-topic-seed flow (when a paper falls below threshold for every topic but is otherwise plausible) needs UI design. CW proposes a simple instructor queue; details to be specified by Codex and approved by DK.
4. Lane A priority assumes student-uploaded papers go through V7-Lite plus full V7 in ~2 hours. If Codex's actual full-V7 throughput is slower, the SLA needs revision.

## Owner timeline

- Codex receives spec: 2026-05-18 (this commit)
- Codex implementation: ~2 weeks
- Codex testing: 3 days
- DK review of calibrated thresholds: 1 day
- V7-Lite live in production: ~3 weeks from now

This timeline is independent of the real-panel (Sprint UJ-F) round trip, because the CW-simulated synthesis is sufficient for the immediate implementation. Real-panel revision can come in V7-Lite v2.
