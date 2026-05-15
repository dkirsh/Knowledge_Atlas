# Codex Pass 3 Prompt — HTTP Endpoints, Admin UI, Claim-Strengths Block, Overseer Rollup

**Document**: `PAPER_QUALITY_CODEX_PASS3_PROMPT_2026-05-14.md`
**Purpose**: the operational message DK posts to Codex for the
Knowledge_Atlas surface work — HTTP endpoints, admin adjudication
UI, claim-strengths UI block, overseer rollup, plus two small
side tasks (argumentation-layer Toulmin projection and
subscription-adapter smoke).
**Authorising reviewer**: DK, 2026-05-14.
**Precondition**: Pass 1 atlas_shared foundations must have merged
to `main` (per `docs/PAPER_QUALITY_CODEX_NEXT_BLOCK_2026-05-13.md`)
before this prompt is given to Codex. Pass 3 imports
`atlas_shared.paper_quality.PaperQualityFingerprint` and
`atlas_shared.claim_strengths.ClaimStrengthsWeaknesses`; without
those types in atlas_shared.main, Pass 3 cannot land.

---

## How to use

After Pass 1 has merged to `atlas_shared` main, paste everything
between `===BEGIN===` and `===END===` into Codex CLI. The four
commits below are the §3 Pass 3 work from the original build prompt
(`PAPER_QUALITY_BUILD_PROMPT_FOR_CODEX_2026-04-23.md`); this prompt
operationalises them with the AG advisory constraints applied and
two small side tasks folded in.

---

## ===BEGIN===

Codex — Pass 1 atlas_shared foundations have merged. The dataclass
and aggregator types are now importable from `atlas_shared` on
`main`. You can begin Pass 3 (Knowledge_Atlas surface) immediately;
this does not depend on DK's M1 (decision-tree annotations), which
gates Pass 2 (extraction service) separately.

### Read first

These are the canonical references for Pass 3 work:

- `docs/PAPER_QUALITY_BUILD_PROMPT_FOR_CODEX_2026-04-23.md` §3
  Commits 8-11 — the original Pass 3 specification.
- `docs/PAPER_QUALITY_SYSTEM_DESIGN_2026-04-23.md` — ground-truth
  specification (file paths, contract sketches, SQL tables, HTTP
  endpoint shapes, UI block layout).
- `docs/PAPER_QUALITY_BLACKBOARD_DESIGN_2026-04-25.md` — the
  coordination architecture. The HTTP endpoints query the same
  blackboard tables (`paper_quality_fingerprints`,
  `quality_adjudication_queue`, `hard_rule_violations`,
  `holding_pen`) that Codex's schema commit (`0da97e9`) created.
- The just-merged Pass 1 atlas_shared modules — `paper_quality.py`,
  `claim_strengths.py`, `literature_body.py`, `worker_loop.py`.
  Pass 3 imports from these.
- `docs/KA_STYLE_GUIDE.md` — the K-ATLAS visual style guide. The
  admin UI and the claim-strengths UI block follow regime 1b
  (160sp palette + nav) and regime 1a (Global K-ATLAS) respectively.

### Branch

Open a new branch on `Knowledge_Atlas`:

```bash
cd /Users/davidusa/REPOS/Knowledge_Atlas
git fetch origin && git checkout master && git pull --ff-only
git checkout -b codex/paper-quality-pass3-2026-05-14
```

### Execution plan — four primary commits

Per the original build prompt §3 Commits 8-11.

#### Commit 1 (build-prompt Commit 8) — HTTP endpoints

`backend/app/api/v1/routes/quality.py`. Three endpoints:

1. `GET /api/v1/quality/claim/{claim_id}/strengths` — returns
   `ClaimStrengthsWeaknesses` per atlas_shared aggregator output,
   computed at request time over the claim's warrants + fingerprints
   + sample-overlap edges. Pydantic `response_model` per the atlas's
   existing F3 convention.
2. `GET /api/v1/quality/literature-body` — returns
   `LiteratureBodyQuality` per atlas_shared aggregator output, with
   optional query parameters to filter by topic / era / design type.
3. `GET /api/v1/quality/paper/{paper_id}/fingerprint` — returns the
   per-paper fingerprint from `paper_quality_fingerprints`.

Per system design §5: endpoints return HTTP 503 with a
`Retry-After` header when the materialised view is refreshing
(roughly hourly in the planned production schedule). The retry
header is informational; the client may retry.

Pydantic `response_model` for each, with shapes derived from the
atlas_shared dataclasses (do not redefine the dataclass shape in
the route module — import from atlas_shared and use Pydantic's
`from_attributes` or equivalent).

Pytest fixtures: seed a five-paper fixture corpus and assert each
endpoint's response shape against the imported Pydantic models. Use
the same five-paper fixture from atlas_shared's Pass 1 test suite
to keep test data consistent across repos.

Register the new route in `backend/app/api/v1/routes/__init__.py`
so the endpoints are exposed.

#### Commit 2 (build-prompt Commit 9) — Admin adjudication queue UI

`160sp/ka_admin.html`. Add an "Adjudication Queue" tab.

Per system design §3: the tab shows every fingerprint routed to
adjudication, with the LLM suggestion, the source excerpt, and the
confidence score visible for every field. The tab also surfaces
the `hard_rule_violations` table and the `holding_pen` view so DK
or an instructor can see what is pending and why.

Per Hard Rule 8 (build prompt §4) the adjudication UI is the
*sanctioned exception* where both model verdicts may sit
side-by-side for human review. The UI displays the Claude verdict
and the ChatGPT verdict in two columns; the human adjudicator picks
one (or "neither, write in") and provides rationale.

Adjudication writes back via:

```
POST /api/v1/admin/paper_quality/adjudicate
```

The endpoint records the decision in `quality_adjudication_queue`
with the WEIGHTING_FUNCTION_VERSION from the moment of decision.

Authorization is gated by the existing instructor-tier JWT check.
Style: regime 1b (160sp palette + nav).

#### Commit 3 (build-prompt Commit 10) — Claim-strengths UI block

`ka_claim_quality.js` plus an expandable block on
`ka_journey_interpretation.html` and `ka_journey_evidence.html`.

The block renders strengths-and-weaknesses on every claim-detail
page. Layout follows the existing `ka_journey_surface.js` style —
expandable card pattern with three sub-sections:

1. *Strengths*: aggregated from the claim's fingerprints, surfaced
   as a prose summary (template-generated, not LLM) + a bulleted
   list of supporting fingerprint references.
2. *Weaknesses*: same shape, drawn from the aggregator's weakness
   slot.
3. *Heterogeneity / disagreement*: I² statistic, Egger funnel-plot
   test result with Sterne et al. 2011 caveat applied (test invalid
   below ten studies; record `egger_test_applicable = False` in
   that case), sample-overlap deduplication note.

Hover tooltips on each listed field link to the glossary. Add four
new glossary entries:

- "Construct validity" — Cronbach & Meehl 1955 definition; Borsboom
  2008 extension on the construct-vs-test distinction.
- "Egger test" — the funnel-plot asymmetry test (Egger et al.
  1997); cite Sterne et al. 2011 caveat.
- "I² heterogeneity" — Higgins & Thompson 2002 definition; quote
  the standard interpretation thresholds.
- "WEIRD sample" — Henrich, Heine & Norenzayan 2010; one-line
  definition with link to the source.

Style: regime 1a (Global K-ATLAS palette).

#### Commit 4 (build-prompt Commit 11) — Overseer rollup

`scripts/overseer_paper_quality_rollup.py`.

Three modes per DK's 2026-04-25 Q18 decision (runtime monitoring):

**Daily** (`--daily`):
- Adjudication-queue depth at end of day, by field.
- Hard-rule violation count from `hard_rule_violations`, by rule
  and field.
- Any field whose live-confidence distribution shifts more than 1σ
  from the calibration baseline → flag as drifting field.
- Subscription-interface error tally (rate-limit retries, auth
  expiries, context overflows) from the worker-loop logs.

**Weekly** (`--weekly`):
- Per-field histogram of confidences over the past seven days,
  alongside the calibration histogram for visual comparison.
- Per-field self-consistency variance over the past seven days,
  flagging any field with variance dropped to near-zero.
- Per-field hard-rule-violation rate, flag if any rule exceeds 5%
  of papers processed.

**Monthly** (`--monthly --sample 10`):
- Selects 10 papers at random from those processed in the past
  month (biased toward holding-pen + adjudication-queue residents).
- Presents them to DK with the model's fingerprint and four
  sidecar verdicts pre-filled.
- DK re-rates the four sidecar fields; model agreement recorded in
  `quality_calibration_history` as fresh ground truth.
- If agreement on any sidecar drops below the anchor-set threshold
  (per Probe 7 of the testing prompt), posts a calibration-drift
  alert to `COORDINATION.md` under `### Paper-quality drift alert`.

Outputs:
- `docs/PAPER_QUALITY_OVERSEER_LOG_<date>.md` for the rollup text
- Append to `COORDINATION.md` under `### Paper-quality rollup`
  with one-line summary linking to the full log

Cron-entry example in the docstring. The rollup script does not
auto-schedule itself — DK adds the cron entry once the server is
provisioned per `Article_Eater_PostQuinean_v1_recovery/docs/PORTING_TO_SERVER_2026-05-13.md`.

### Two side tasks

While you are working on Pass 3, two small bounded items that
have been queued and can fold in here.

#### Side task A — Argumentation-layer Toulmin projection

The `paper_quality_blackboard_schema` commit already added Toulmin
sidecar fields to `Constraint` in
`src/services/web_of_belief_components/graph_models.py` (per DK's
2026-05-13 both/and decision on Toulmin fields,
Article_Eater commit `c68cf63`). The follow-up task filed as
TASKS entry `c1f0bb5` is:

Extend `src/services/rebuild_argumentation_layer.py` (in
`Article_Eater_PostQuinean_v1_recovery`) to consume the new Toulmin
sidecar fields and aggregate them into the argumentation-layer
projection. Readers of the argumentation layer should see
per-constraint backing references and rebuttal conditions, both
raw (the sidecar) and aggregated (the projection).

Roughly 4 hours of Codex work. Land as a separate commit on its
own branch in Article_Eater
(`codex/argumentation-toulmin-projection-2026-05-14`) so it does
not get tangled with Pass 3 work in Knowledge_Atlas.

#### Side task B — Subscription-adapter smoke test

Precondition E3 from
`Knowledge_Atlas/docs/PAPER_QUALITY_PRECONDITIONS_2026-04-25.md`.
A small test that confirms the subscription-based CLI adapters
work and that no API keys are accidentally being used.

Write `atlas_shared/tests/test_subscription_adapter_smoke.py`
that:

1. Fires one conversation through `claude -p --output-format json`
   via the cli_adjudicator pattern (existing).
2. Fires one conversation through `codex exec -m gpt-5.2-codex`
   via the same pattern.
3. Asserts both return non-empty JSON responses.
4. Asserts that during the test, no `ANTHROPIC_API_KEY` or
   `OPENAI_API_KEY` environment variables are read (use a
   monkey-patched `os.environ.get` to detect access).

Land on the same `paper-quality-foundations-2026-05-13` branch as
Pass 1 if it has not yet merged, otherwise on a new branch
`codex/subscription-adapter-smoke-2026-05-14`. Roughly 30 minutes
of Codex work; satisfies a precondition that otherwise lurks.

### Hard rules (carry over from build prompt §4)

The hard rules from the build prompt apply to Pass 3 as written.
Restated for the rules most likely to bite:

- **Hard Rule 8 — Multi-LLM agreement** does not apply to Pass 3
  directly because Pass 3 has no extraction. But the adjudication
  UI display in Commit 2 is the sanctioned exception; do not
  re-use that pattern anywhere outside the UI render path.
- **Hard Rule 5 — Every schema change ships its migration.** If
  Commit 1 (the endpoints) needs a schema tweak (an index for
  endpoint performance, say), the migration ships in the same
  commit with a later-dated migration filename than the existing
  `2026_04_23_paper_quality.sql`.
- **No force-push, no rebase of shared history, no fast-path
  bypasses of the adjudication queue.**

### AG advisory constraints (carry from next-block prompt §1.6)

These five constraints applied to Pass 1 and continue to apply
through Pass 3 where relevant:

1. **paper_id format** is raw `PDF-NNNN`, not `bel_PDF-NNNN`. The
   HTTP endpoints accept and return the raw form; if any client
   passes a `bel_`-prefixed identifier, the endpoint normalises
   before storing or querying.
2. **Stage 18/19 monotonicity** — the overseer rollup queries the
   lifecycle DB; ensure queries respect the stage_number monotonic
   invariant per paper.
3. **No shadow definitions** of `PaperQualityFingerprint` or
   `ClaimStrengthsWeaknesses` in Knowledge_Atlas — import from
   atlas_shared.
4. **Spec-generation hygiene** — if any of the four commits
   produces a new on-disk artefact family (e.g., the overseer
   rollup writes `docs/PAPER_QUALITY_OVERSEER_LOG_<date>.md` per
   day), confirm whether the artefact qualifies as a semantic slot
   needing registration in `spec_generation_registry.py`. Daily
   rollups under a date-stamped filename probably do not need
   slot registration (they are frozen historical records, not
   current-spec artefacts); confirm and note in the commit message.

### Failure handling — log and continue

Per build prompt §5 (revised 2026-04-25, Q15) and the same pattern
used in Pass 1: hard-rule violations and per-paper errors during
the rollup process get recorded in `hard_rule_violations` and the
rollup proceeds to the next paper. The rollup does not halt; it
produces a complete report at the end with the violations called
out.

Build-time errors (schema migration failure, test-suite regression,
or precision below 70% on the calibration set) still halt the
build per the original failure-handling semantics.

### Reporting

When the four primary commits + side task B land on
`codex/paper-quality-pass3-2026-05-14` and side task A lands on
`codex/argumentation-toulmin-projection-2026-05-14`, post a single
message to `COORDINATION.md` under `### Codex paper-quality Pass 3
— landed`:

```
Pass 3 commit SHAs (Knowledge_Atlas):
  C1 (endpoints):           <sha>
  C2 (admin adjudication):  <sha>
  C3 (claim-strengths UI):  <sha>
  C4 (overseer rollup):     <sha>

Side task A (Article_Eater argumentation projection): <sha>
Side task B (atlas_shared adapter smoke): <sha>

Knowledge_Atlas pytest counts pre/post: <pre> / <post>
Article_Eater pytest counts pre/post:   <pre> / <post>
atlas_shared pytest counts pre/post:    <pre> / <post>

Glossary entries added: 4 (construct validity, Egger test,
I² heterogeneity, WEIRD sample).
New endpoints registered under /api/v1/quality/...

Manual smoke: admin adjudication queue rendered correctly with a
synthetic low-confidence fingerprint; claim-strengths UI block
rendered on a fixture claim with synthetic warrants.

Deviations from this prompt: <list any>.
```

Tag CW and DK.

### Timeline

Pass 3 is roughly 1.5 working days for Codex:
- Commit 1 (endpoints): half a day
- Commit 2 (admin UI): half a day
- Commit 3 (claim-strengths UI block): half a day
- Commit 4 (overseer rollup): half a day
- Side task A: 4 hours (separate branch)
- Side task B: 30 minutes (separate branch)

If the run exceeds two working days, post progress to
COORDINATION.md and continue.

### Out of scope for Pass 3

- **Pass 2 (extraction service + per-field prompts).** Still
  waits on DK's M1 (decision-tree annotations export at
  `Knowledge_Atlas/data/paper_quality_dk_preferences.json`). Do not
  start Pass 2 in this run.
- **Pass 4 (integration commit).** Comes after Pass 2 and Pass 3
  both land.
- **The retrofit pass** on the existing 1,400-paper corpus. Only
  after the testing pass clears (AG Probes 1, 2, 5 plus Codex
  Probes 3, 4, 6, 7, 8, 9).
- **Any modification to the paper-quality contracts** committed in
  the 2026-05-13 cleanup session. Those are now standing
  infrastructure (V7_EN_BIDIRECTIONAL_WARRANT_AUTHORITY,
  V7_PANEL_CONVOCATION_PROTOCOL, the
  REBUILD_PROMOTION/V7_CANONICAL_REBUILD_OPERATION pair, the EN
  warrant success conditions).

### Standing-by after Pass 3

When Pass 3 merges:
- If DK's M1 is done, write the Pass 2 prompt referencing the
  actual preferences in
  `Knowledge_Atlas/data/paper_quality_dk_preferences.json`. Begin
  Pass 2.
- If DK's M1 is not yet done, stand by. The argumentation-Toulmin
  projection and adapter smoke (side tasks) are already done; no
  further work for Codex until M1 lands or DK directs.

## ===END===

---

## Notes for DK before pasting

A few items.

**1. Hold on pasting until Pass 1 is merged.** Pass 3's HTTP
endpoints and UI block import from atlas_shared.paper_quality and
atlas_shared.claim_strengths, which are produced by Pass 1. Codex's
Pass 1 prompt (`PAPER_QUALITY_CODEX_NEXT_BLOCK_2026-05-13.md`) is
already in flight; once Pass 1 lands on atlas_shared main, paste
this Pass 3 prompt.

**2. The two side tasks are bonuses.** They are not blocking
anything else. If you want Codex to focus only on the four primary
commits, strike the "Two side tasks" section before pasting. They
are included because they are short, bounded, and naturally fit
the Pass 3 window.

**3. The argumentation-Toulmin projection (side task A)** lands on
Article_Eater, not Knowledge_Atlas. Codex switches repos briefly
for that one. The atlas_shared smoke test (side task B) lands on
atlas_shared. The four primary commits land on Knowledge_Atlas.

**4. AG remains in standby** during Pass 3. The Phase 2 trigger is
end-of-Pass-4 merge, which is still future.

**5. After Pass 3 + Pass 2 + Pass 4, the next gate is AG's
testing pass.** That uses the existing AG kick-off prompt's
Phase 2 text — you post it to AG when the testing branch exists.

---

*End of Pass 3 prompt.*
