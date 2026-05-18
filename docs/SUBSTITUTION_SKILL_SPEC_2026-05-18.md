# Substitution-skill — build specification for Codex
*Date: 2026-05-18 · Author: CW · Reviewer: DK · Target implementer: Codex (Article_Eater_PostQuinean_v1_recovery + Knowledge_Atlas)*

## What this document is

A build specification for the *substitution skill* — the engine that drives Surface 4 (admit-mode) and Surface 4b (choice-mode) of the Knowledge Atlas Week-1 wireframe. The skill answers two questions for the student:

1. **Admit-mode**: given a paper's dependent-variable operationalisation, is there at least one VR-tractable measure that indexes the same construct? Yes/no, with rationale.
2. **Choice-mode**: given a topic and the set of admissible measures, rank them by suitability for a 7-to-10-week class project, with trade-offs articulated.

The skill is retrieval-and-ranking over a curated knowledge graph (the *substitution graph*), with a generative LLM layer that produces the prose. The generative layer is responsible only for explanation; it does not invent substitutions. This is the key failure-mode-prevention design — generative-only systems hallucinate substitutions the field has not validated, with consequences that derail student projects.

This is a Codex-owned build. CW supplies the spec, the data-extraction prompts, and the post-build review. Codex owns the implementation, the storage schema, and the integration with the Surface 4 / 4b front-end. AG owns the corpus-wide extraction pass that populates the knowledge graph.

The spec follows the panel synthesis at `docs/VOI_PANEL_SYNTHESIS_2026-05-18.md`. The synthesis's working positions on refusal criteria (Mayo, Machery) and confidence display (Pearl, Gelman, Bergstrom) are baked in.

## The substitution graph — data model

Three interlinked tables, all stored alongside `ae.db` in the recovery repo. CW recommends a new SQLite database `substitution_graph.db` for cleanliness; Codex may choose to merge into `ae.db` if that turns out to be operationally simpler.

### Table 1 — `constructs`

The set of constructs that the corpus's papers operationalise. One row per construct.

```sql
CREATE TABLE constructs (
    construct_id TEXT PRIMARY KEY,         -- 'attention_restoration', 'implicit_attitude', ...
    canonical_name TEXT NOT NULL,
    aliases JSON,                          -- alternative names from the literature
    family_theory_id TEXT,                 -- which theory this construct lives in
    proliferation_warning JSON             -- jingle-jangle flag set (see below)
);
```

The `proliferation_warning` field is a list of *related but distinct* constructs that share vocabulary; populated by the corpus-wide extraction pass per Machery's concern about construct proliferation. Example:

```json
{
  "construct_id": "attention_restoration",
  "jangle_with": ["mental_recovery", "cognitive_restoration"],  // same construct, different name
  "jingle_with": ["attention_capacity", "vigilance"]  // different construct, similar name
}
```

### Table 2 — `measures`

Every measure the corpus has used, plus the four VR-positive families and five exclusions from the measurability page. One row per measure.

```sql
CREATE TABLE measures (
    measure_id TEXT PRIMARY KEY,
    short_code TEXT NOT NULL,              -- e.g., 'f2.iat', 'f4.eda', 'x1.fmri'
    canonical_name TEXT NOT NULL,
    measurement_family TEXT NOT NULL,      -- f1 | f2 | f3 | f4 | x1 | x2 | x3 | x4 | x5
    vr_tractable BOOLEAN NOT NULL,
    vr_tractability_conditions JSON,       -- e.g., {"requires_headset": "Quest Pro+"}
    psychometric_profile JSON,             -- reliability, validity, known issues
    construct_validity_per_paper JSON,     -- per-paper construct linkages
    administration_time_min INTEGER,
    hardware_required JSON,
    principal_pitfall TEXT,
    canonical_references JSON              -- founding paper + key validation papers
);
```

The `vr_tractability_conditions` field carries the hardware tier (confirmed / maybe / request) from the measurability page. The `psychometric_profile` field is the substrate for the choice-mode ranking and is populated from corpus extraction plus AG's V2 severity field where applicable.

### Table 3 — `construct_measure_links`

The many-to-many relation between constructs and measures, with strength and provenance.

```sql
CREATE TABLE construct_measure_links (
    link_id INTEGER PRIMARY KEY AUTOINCREMENT,
    construct_id TEXT NOT NULL REFERENCES constructs(construct_id),
    measure_id TEXT NOT NULL REFERENCES measures(measure_id),
    construct_validity FLOAT NOT NULL,     -- [0, 1]; how well this measure indexes this construct
    field_acceptance INTEGER NOT NULL,     -- count of corpus papers that operationalise the construct with this measure
    canonical_paper_id TEXT,               -- which paper originally established the link
    citation_count INTEGER,                -- how many corpus papers cite this link
    severity_average FLOAT,                -- mean severity (AG V2) of papers establishing the link
    notes TEXT
);
```

The substitution graph is then implicit in this table: two measures are *substitutable for one construct* if both have rows in this table for that construct. The strength of the substitution is the product of the two construct-validities, weighted by field acceptance and severity. This is the substitution-ranking logic Codex should implement.

## Corpus-wide extraction pass (AG-owned) — to populate the three tables

AG runs the extraction over the corpus to populate the tables initially. CW writes the prompt; AG runs it; CW reviews the output before it ships to the substitution skill. The prompt template:

```
You are extracting the construct-to-measure relations from a scientific paper.

For the paper [PAPER_METADATA + ABSTRACT + METHODS_SECTION]:

1. List each dependent variable (DV) the paper measures.
2. For each DV, identify which construct it is claimed to index. Use the canonical construct name if known; otherwise propose one.
3. For each DV, provide:
   - the measure's canonical name (the one psychometric reviews use)
   - the measure's short code from the VR-measurability page if applicable (f1.head_pose, f2.iat, f4.eda, ...)
   - the construct-validity strength as the paper asserts it [0, 1]
   - whether the paper validates the measure or uses an already-validated measure
4. List the principal pitfalls of the measure as the paper discusses them.
5. Flag any cases where the paper's chosen measure has known psychometric issues
   that the paper does not acknowledge.

Return as structured JSON matching:
{
  "dv_extractions": [
    {
      "dv_canonical_name": "...",
      "construct_id": "...",
      "measure": {
        "canonical_name": "...",
        "short_code": "..." or null,
        "construct_validity": 0.0-1.0,
        "validated_in_this_paper": true|false,
        "principal_pitfall": "...",
        "unacknowledged_issue": "..." or null
      }
    }
  ]
}
```

AG should run this prompt over every paper in the corpus (estimated 1,428 papers per the migration status memory). AG batches in groups of 50 with multi-LLM independent extraction (per the rule against single-model agreement). Disagreements between LLMs are flagged for CW review.

After extraction, CW reviews:
- All `unacknowledged_issue` entries (these are the contentious cases)
- All construct_id assignments where multiple papers in the same topic use different construct_ids for the same DV (this is the jangle problem)
- The top-50 construct-measure links by `field_acceptance` to verify the strength estimates

The review takes ~3 days of CW time. After review, the tables are populated and the substitution skill is operational.

## Skill API — admit-mode

The Surface 4 admit-mode call:

```
POST /api/substitution_skill/admit_mode
Content-Type: application/json

{
  "paper_id": "PDF-XXXX",                  // if paper is in corpus
  "dv_descriptions": [                     // if paper is uploaded (V7-Lite output)
    {
      "name": "salivary cortisol",
      "type": "biomarker",
      "claimed_construct": "stress_response"
    },
    ...
  ]
}
```

The skill returns:

```json
{
  "per_dv_results": [
    {
      "dv_input": "salivary cortisol",
      "claimed_construct": "stress_response",
      "resolved_construct_id": "physiological_stress_response",
      "measure_short_code": "x5.biomarker",
      "vr_tractable_as_is": false,
      "substitution_candidates": [
        {
          "measure_short_code": "f4.eda",
          "construct_validity": 0.82,
          "field_acceptance": 47,         // corpus papers using this link
          "severity_average": 0.68,
          "psychometric_summary": "...",
          "principal_pitfall": "..."
        },
        {
          "measure_short_code": "f4.hrv",
          "construct_validity": 0.74,
          "field_acceptance": 28,
          "severity_average": 0.62,
          ...
        }
      ],
      "admit_verdict": "admit_with_substitution",
      "confidence": 0.81,
      "explanation": "[LLM-generated prose, ≤80 words]"
    },
    ...
  ],
  "paper_level_verdict": "admit_with_substitution",
  "paper_level_confidence": 0.78
}
```

The `admit_verdict` per DV is one of:
- `admit_as_is`: DV is VR-tractable as-is (in F1, F2, F3, or F4).
- `admit_with_substitution`: DV is not VR-tractable but ≥1 substitution exists.
- `reject`: DV is not VR-tractable and no substitution exists (see refusal criteria below).

The `paper_level_verdict` is computed from the per-DV verdicts:
- If every DV is `admit_as_is`, the paper is `admit`.
- If any DV is `reject`, the paper is `reject_dv_unmeasurable` (because the paper's design cannot be reproduced even with substitution).
- Otherwise, `admit_with_substitution`.

### Refusal criteria — when the skill returns `reject` for a DV

Per the Mayo + Machery positions in the panel synthesis, the skill refuses when:

1. **No construct match.** The DV's claimed construct cannot be resolved to any construct in the `constructs` table at confidence ≥ 0.4. This means the field has not previously studied this construct and the substitution skill has no basis for recommending. Recommend instructor consultation.

2. **No VR-tractable measure for the construct.** Every `construct_measure_links` row for this construct points to a measure in the `x1`–`x5` exclusion families. The skill should still surface those measures with their exclusion reasons so the student understands what is and is not possible.

3. **Low severity across the field for this construct-measure pairing.** Per Mayo's framing, if the candidate substitutions all have `severity_average < 0.50`, the skill should mark the admission as *low-confidence* and recommend the student consult the instructor. This is not strictly a refusal; it is a confidence flag.

4. **Construct proliferation warning is active.** If the resolved construct has `proliferation_warning` populated and the substitution candidates index a *jangle* construct rather than the original, the skill should flag this and request student attention. Per Machery, the jangle problem is a substantive methodological issue, not a UI nuance.

### Confidence display — how the skill exposes uncertainty

Per the Pearl + Gelman + Bergstrom convergent position on profile rather than score, the skill displays:

- The numerical `construct_validity` per substitution candidate (not "high/medium/low" — actual numbers, [0, 1]).
- The `field_acceptance` count (number of corpus papers establishing the link).
- The `severity_average` from AG's V2 schema (the mean severity of papers establishing the link).
- The `principal_pitfall` text.

The skill does *not* display a composite confidence score. Per the panel synthesis convergent position (profile, not score), the student is shown the components and trusted to weigh them. The LLM-generated `explanation` prose synthesises these into a brief recommendation but does not collapse them.

## Skill API — choice-mode

The Surface 4b choice-mode call:

```
POST /api/substitution_skill/choice_mode
Content-Type: application/json

{
  "topic_id": "attention_restoration",
  "project_constraints": {
    "weeks_available": 8,
    "lab_hardware": ["quest2", "eda", "hrv", "respiration", "wrist_accel"],
    "sample_pool": "ucsd_undergraduates",
    "n_participants_max": 60
  }
}
```

The skill returns:

```json
{
  "candidate_measures": [
    {
      "measure_short_code": "f2.sart_plus_f3.prs",  // composite recommendation
      "rank": 1,
      "construct_indexed": "attention_restoration",
      "estimated_administration_min": 17,
      "construct_validity_pooled": 0.79,
      "field_acceptance": 23,
      "severity_average_pooled": 0.71,
      "hardware_satisfied": true,
      "feasibility_score": 0.91,
      "trade_offs": "...",
      "principal_pitfalls": ["..."]
    },
    {
      "measure_short_code": "f4.pupil",
      "rank": 2,
      "construct_validity": 0.84,
      "field_acceptance": 18,
      "severity_average": 0.69,
      "hardware_satisfied": false,            // requires Quest Pro
      "feasibility_score": 0.55,
      "trade_offs": "..."
    },
    ...
  ],
  "recommendation_prose": "[LLM, ≤200 words]"
}
```

The ranking logic combines:
- `construct_validity` (primary weight)
- `field_acceptance` (the field's prior endorsement)
- `severity_average` (Mayo's preferred weighting)
- `hardware_satisfied` (boolean; non-satisfied measures drop in rank but are not removed)
- `time_within_budget` (boolean)

The combination is *displayed transparently* (the user sees each component) rather than reduced to a single feasibility number. The prose recommendation explains the ranking.

## Front-end integration

Surface 4 (admit-mode) calls the admit-mode endpoint and renders the per-DV results table per the wireframe mock at `#s4`. Surface 4b (choice-mode) calls the choice-mode endpoint and renders the side-by-side comparison table per the wireframe mock at `#s4b`.

The article-viewer page (Track-4 students' work) also calls the admit-mode endpoint when a student opens a paper from their short-list. The viewer renders a small "VR-evaluation panel" at the foot of the article showing the per-DV verdicts.

## Testing protocol

Before the skill ships, Codex should test against:

1. **Trivial admit.** A DV that is already in F2 (e.g., reaction time on a Stroop task). Expected: `admit_as_is`.
2. **Standard substitution.** A DV in X5 (salivary cortisol) with a well-known substitute (EDA). Expected: `admit_with_substitution` with EDA as top candidate.
3. **Refusal.** A DV with no construct match in the table (e.g., a newly named construct from a frontier paper). Expected: `reject` with the no-construct-match reason.
4. **Choice-mode top-rank stability.** Run choice-mode on the attention-restoration worked example with the lab's standard hardware constraints. Expected: SART+PRS pair ranks first (per the wireframe Surface 4b mock).
5. **Jangle warning.** Submit a paper whose DV claims to index "cognitive restoration" (a jangle term for attention restoration). Expected: the proliferation warning fires.

## Open questions for DK / panel-revision

1. The construct-validity-pooled formula for composite-measure recommendations (e.g., SART+PRS) is CW's reading. Codex should implement a simple geometric mean for v1; the real panel may propose a more principled aggregation.
2. The `severity_average < 0.50` threshold for low-confidence admission is provisional. AG and CW should review actual severity distributions in the corpus before locking the threshold.
3. The hardware-tier integration (Quest 2 vs Quest Pro) requires the lab to maintain a per-session hardware profile. CW proposes `data/lab_hardware_profile.json`; Codex implements.
4. The article-viewer page integration depends on Track-4 students' design completing. CW will write the URL contract once they have a complete proposal.

## Owner timeline

- Codex receives spec: 2026-05-18 (this commit)
- CW writes extraction prompts: 2 days
- AG corpus-wide extraction pass: 1 week (running in parallel with Codex implementation)
- CW review of extraction output: 3 days
- Codex implementation of skill API: 1.5 weeks
- Codex front-end wiring: 3 days
- Testing: 3 days
- DK review of refusal-criteria thresholds: 1 day
- Substitution skill live in production: ~3 weeks from now

The skill is independent of the real-panel round trip (Sprint UJ-F); panel revisions can come in v2.
