# Paper-Quality — Codex Next-Block Prompt (Pass 1 foundations)

**Document**: `PAPER_QUALITY_CODEX_NEXT_BLOCK_2026-05-13.md`
**Purpose**: the second operational message DK posts to Codex,
scoping the next chunk of work Codex can do without waiting on
DK's decision-tree annotations (M1).
**Authorising reviewer**: DK, 2026-05-13.
**Prior block**: `PAPER_QUALITY_CODEX_KICKOFF_PROMPT_2026-04-25.md`
plus Codex's commit `0da97e9` on branch
`codex/paper-quality-blackboard-schema` (E2 schema + migration; E4
blackboard initialiser; regression tests; dry-run report).

---

## How to use this document

Paste everything between `===BEGIN===` and `===END===` into Codex
as your next message. Codex picks up from where it left off and
moves into Pass 1 — atlas_shared foundations — which is pure Python
code and contract documents in `atlas_shared` and does not depend
on the eleven per-field extraction prompts (those still need M1).

---

## ===BEGIN===

Codex — the schema + blackboard initialiser work on
`codex/paper-quality-blackboard-schema` (commit `0da97e9`) is clean
and complete. The schema covers all ten tables, three views,
indices, and update triggers required by the design package. The
initialiser is idempotent and the synthetic 56-paper dry-run
verified the expected row counts (168 jobs, 6 batches, 56
progress-view rows).

Two follow-up housekeeping items on the Knowledge_Atlas side, then
the main work block.

### Housekeeping (Knowledge_Atlas branch)

1. **Merge** `codex/paper-quality-blackboard-schema` to `master`
   after DK's review. CW has reviewed the schema and finds it
   structurally complete; DK's review remains the gating step.
2. **No follow-up on the Knowledge_Atlas branch is required** until
   Pass 3 begins. The schema and initialiser are correct as
   landed.

### Main work block — Pass 1 atlas_shared foundations (Commits 1–4)

This is pure Python and contract work in the `atlas_shared`
repository. It does *not* depend on DK's M1 decision-tree
annotations (those gate Pass 2's extraction prompts, not these
foundations). It *does* depend on the blackboard schema already
landed, because the dataclass field set mirrors the SQL columns.

Open a new branch:

```bash
cd /Users/davidusa/REPOS/atlas_shared
git fetch origin && git checkout master && git pull --ff-only
git checkout -b codex/paper-quality-foundations-2026-05-13
```

### Commit 1 — `paper_quality.py` + `worker_loop.py`

Two new modules in `atlas_shared/src/atlas_shared/`.

**`paper_quality.py`** — the core dataclasses and Pydantic schema.
All dataclasses `frozen=True` per atlas_shared convention.
Exported from `atlas_shared/__init__.py` under a new group-import.
Module name added to `__all__`.

The dataclasses to ship:

- `PaperQualityFingerprint` — one-to-one with the
  `paper_quality_fingerprints` SQL table you already created.
  Includes the eleven extractable fields plus the four human-only
  sidecars. Round-trip serialisation to / from the SQL row tested.
- `FingerprintField[T]` — a generic wrapper carrying value,
  point-confidence, sampling-based logprob proxy (across-sample
  agreement rate), per-element agreement for list-valued fields,
  source-excerpt provenance (page, paragraph, quoted span), and
  the WEIGHTING_FUNCTION_VERSION at extraction time. The shape
  required by Hard Rules 9 and 8.
- `PreregRecord` — preregistration metadata: URL, timestamp,
  hypothesis text, registry kind (`osf` / `aspredicted` /
  `clinicaltrials_gov` / `journal_rr` / `unknown`), verified
  boolean.
- `EffectSize` — value, metric (`d` / `r` / `or` / `hr` /
  `bayes_factor`), CI lower, CI upper, computed-or-reported flag,
  origin (`reported` / `computed_from_t_and_n` /
  `computed_from_chi_square` / etc.).
- `PowerRecord` — value, origin (`a_priori_reported` /
  `retrospective_computed` / `not_reported`), the Hoenig-and-Heisey
  caveat flag for retrospective-power records.
- `HardRuleViolation` — `paper_id`, `rule_id`, `field_name`,
  `violation_state` (JSON), `violation_timestamp`,
  `requires_dk_review` — mirrors the `hard_rule_violations` SQL
  table.

Tests: round-trip every dataclass through JSON and through the SQL
representation; assert no field is lost. The 20-paper anchor-set
fixture is not yet curated by DK, so use the synthetic fixtures
from the existing Knowledge_Atlas dry-run for the round-trip
tests.

**`worker_loop.py`** — the shared blackboard worker-loop
implementation. Per build prompt §1.6 and
`PAPER_QUALITY_BLACKBOARD_DESIGN_2026-04-25.md` §4. The eight
helpers the three adapter wrappers (Claude CLI, Codex CLI, Gemini
verifier) will import:

- `claim_next_batch(worker_id, pass_type, my_pool) -> Batch | None`
  — atomic UPDATE on `paper_quality_batches` with the SQL pattern
  shown in design doc §4.
- `job_already_done(paper_id, pass_type) -> bool` — check
  `paper_quality_jobs` table.
- `mark_paper_done(batch, paper_id, artifact_path) -> None` —
  update job row, increment `papers_done` on batch, update
  `last_progress_at`.
- `mark_paper_failed_in_batch(batch, paper_id, reason) -> None`.
- `mark_paper_skipped_in_batch(batch, paper_id, reason) -> None`.
- `mark_batch_done(batch) -> None`.
- `record_hard_rule_violation(paper_id, rule_id, violation_state)
  -> None` — insert into `hard_rule_violations`.
- `refresh_mirror_for_paper(paper_id) -> None` — atomic temp-file-
  and-rename to `data/paper_quality_progress.json`.
- `commit_local(message) -> None` — `git add` + `git commit` on the
  mirror file.
- `push_to_github(message) -> None` — `git push` with fast-forward-
  failure recovery (re-pull, re-commit if needed, retry).
- `papers_since_last_push() -> int` — for the every-50-papers
  push cadence.

The worker loop itself (the `while True` from design doc §4) goes
in `worker_loop.py` as `run_worker(worker_id, pass_type, extractor)`
so the three adapters call into the same code path.

Tests: unit tests for atomic claim semantics (two workers racing on
the same batch; one wins, one retries); idempotency of `INSERT OR
IGNORE` paths; mirror-file write atomicity; git-push failure
handler.

### Commit 2 — `PAPER_QUALITY_FINGERPRINT_CONTRACT_2026-04-23.md`

Following the seven-section atlas_shared contract template (Scope
/ Inputs / Outputs / Success conditions / Non-promises / Test
coverage / References). Body text cribbed from the system design
document §2.

Also update `atlas_shared/AGENTS.md` with one new canonical-shared-
module line pointing at `atlas_shared.paper_quality.PaperQualityFingerprint`.

### Commit 3 — `claim_strengths.py`

`atlas_shared/src/atlas_shared/claim_strengths.py`. The
`ClaimStrengthsWeaknesses` dataclass + aggregation function:

```
def aggregate_claim_strengths(
    claim_id: str,
    warrants: Sequence[Warrant],
    fingerprints: Sequence[PaperQualityFingerprint],
    overlap_edges: Sequence[SampleOverlapEdge]
) -> ClaimStrengthsWeaknesses
```

Pure function, no database access. Inside:

- The weighting function with a `WEIGHTING_FUNCTION_VERSION`
  module-level constant (start at `"v1.0-2026-05-13"`). Per panel
  consultation §4 default weights.
- I² heterogeneity per Higgins & Thompson 2002.
- Egger funnel-plot-asymmetry test per Egger et al. 1997, with
  Sterne et al. 2011 caveats applied (test invalid when fewer than
  ten studies; record `egger_test_applicable = False` rather than
  reporting a misleading statistic).
- Sample-overlap deduplication using the `overlap_edges` graph
  (papers sharing more than 50% of participants count as a single
  warrant with the average effect, not two warrants).
- Prose-summary generation via a template with named slots, *not*
  an LLM (the prose is deterministic from the structured
  aggregation; the LLM is in the extractor, not in the
  aggregator).

Tests: a synthetic five-paper fixture in `atlas_shared/tests/` that
produces an expected claim-aggregate with specific I², Egger
statistic, and deduplication outcomes. Include a six-paper variant
where the sixth overlaps with the fifth at 70%; the deduplication
should merge them.

### Commit 4 — `literature_body.py`

`atlas_shared/src/atlas_shared/literature_body.py`. The
`LiteratureBodyQuality` dataclass + aggregator. Five summary
statistics per system-design §6:

1. Fraction of fingerprints with `preregistered = True`.
2. Median sample size, weighted by `design_type`.
3. Median effect-size CI width, by metric.
4. Replication-coverage fraction (papers with at least one entry
   in the replication-registry tables you have access to).
5. Open-data-availability fraction.

Pure function. Ship the companion contract
`atlas_shared/contracts/LITERATURE_BODY_QUALITY_CONTRACT_2026-04-23.md`
in the same commit.

Tests: synthetic ten-paper fixture in `atlas_shared/tests/`
asserting all five statistics.

### Pre-flight for this branch

```bash
cd /Users/davidusa/REPOS/atlas_shared
pytest -q 2>&1 | tail -5
```

Record the baseline pass/fail/skip count. Every commit below
preserves or improves it.

### Hard rules — restated for this block

The Hard Rules 7, 8, 9 of the build prompt apply to the extractor
(Pass 2). The atlas_shared foundations themselves have softer but
still meaningful constraints:

- **No database access in atlas_shared modules.** The aggregators
  are pure functions over Python objects. Database access happens
  in Knowledge_Atlas (Pass 3 endpoints) and Article_Eater (Pass 2
  extractor). atlas_shared is the type-and-logic core.
- **No LLM calls in atlas_shared modules.** Prose summaries are
  template-based, not LLM-generated. The LLM is in the extractor.
- **No I/O side-effects in the aggregators.** They take inputs,
  return outputs, no logging-as-state or write-throughs.

The worker-loop module is the exception: it does have I/O (DB
writes, mirror-file writes, git operations). Keep the I/O
contained to `worker_loop.py`; the dataclasses and aggregators
stay pure.

### Reporting

When the four commits land on
`codex/paper-quality-foundations-2026-05-13`, post to
`/Users/davidusa/REPOS/Knowledge_Atlas/COORDINATION.md` under
`### Codex paper-quality Pass 1 — landed`. Include:

- Four commit SHAs with messages.
- atlas_shared pytest counts pre and post.
- Notable design choices (e.g., what default weights ended up in
  the weighting function, whether the Egger test threshold was set
  at 10 studies or somewhere else).
- Any deviations from this prompt and why.

After Pass 1 merges, Codex stands by for either (a) DK's M1
annotations landing so Pass 2 (extraction service) can start, or
(b) a Pass-3 prompt for the HTTP endpoints + UI + overseer rollup,
which also does not need M1 and can be done in parallel with DK's
human work.

### Out of scope for this block

- The eleven per-field extraction prompts in
  `Article_Eater_PostQuinean_v1_recovery/prompts/paper_quality/`.
  These need DK's M1 annotations and ship in Pass 2.
- The HTTP endpoints in `Knowledge_Atlas/backend/app/api/v1/`.
  These ship in Pass 3 after Pass 1.
- The admin adjudication-queue UI in `160sp/ka_admin.html`. Pass 3.
- The claim-strengths UI block. Pass 3.
- The overseer rollup. Pass 3.
- The master-doc update. Pass 4 integration.
- The retrofit pass on the existing 1 400-paper corpus. After
  testing-pass clears.

Pass 1 stays scoped to the atlas_shared foundations. Resist
expanding scope; we will pick up the rest in subsequent prompts.

### Timeline

One working day for Pass 1, assuming the schema-to-dataclass
round-trip work goes cleanly. The aggregators (C3, C4) are
moderately involved because of the I² and Egger statistics, but
both are well-documented in the literature and the test fixtures
are small.

## ===END===

---

## Notes for DK before pasting

A few things to verify.

**1. DK's review of commit `0da97e9` is complete and the branch is
ready to merge.** CW reviewed the schema and found it structurally
complete. Your sign-off is the gating step before Codex moves
forward — though Pass 1 in `atlas_shared` does not strictly require
the Knowledge_Atlas branch to be merged, only that the SQL schema
is stable.

**2. The atlas_shared branch is clean.** Pull master before
starting; the don't-alter-atlas_shared rule from the deploy handoff
is paused for the paper-quality build (per build prompt Hard Rule
1), but only on this branch.

**3. Pass 1 work can happen in parallel with your decision-tree
annotations.** The four commits do not depend on M1. By the time
you finish the walkthrough, Pass 1 will likely have landed and
Codex can move directly into Pass 2.

**4. After Pass 1 merges, AG's audit role is not yet active.** AG
audits the *testing* pass, which follows the full build. The
separated-auditor role does not engage until Codex finishes Pass 4
and the testing branch exists.

**5. Pass 3 prompt is queued.** When Codex finishes Pass 1, the
natural next move is Pass 3 (HTTP endpoints + UI + rollup), which
also does not need M1. I can write that prompt next if you want
Codex to keep moving while you walk the decision tree. Pass 2
(extraction service) is the only block that genuinely requires M1.

---

*End of Codex next-block prompt.*
