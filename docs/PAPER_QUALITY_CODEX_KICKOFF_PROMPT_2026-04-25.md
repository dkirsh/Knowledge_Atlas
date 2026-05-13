# Paper-Quality Build — Codex Kick-Off Prompt

**Document**: `PAPER_QUALITY_CODEX_KICKOFF_PROMPT_2026-04-25.md`
**Purpose**: the operational message DK pastes into Codex CLI (or the
Codex Desktop interface) to start the paper-quality build.
**Authorising reviewer**: DK, 2026-04-25.
**Not to be used until**: all preconditions in
`PAPER_QUALITY_PRECONDITIONS_2026-04-25.md` are checked.

---

## How to use this document

Paste everything between the `===BEGIN===` and `===END===` markers
below into Codex as your opening message. The build prompt is
referenced by path, not duplicated, so Codex must have read access
to the repos before the kick-off message goes in.

Confirm before you paste:

1. All sixteen items in `PAPER_QUALITY_PRECONDITIONS_2026-04-25.md`
   are checked.
2. Your DK-preferences JSON is committed at
   `data/paper_quality_dk_preferences.json`.
3. Your anchor-set manifest is committed at
   `atlas_shared/tests/fixtures/paper_quality_calibration/anchor_set_manifest.json`.
4. Your sidecar ratings are committed at
   `atlas_shared/tests/fixtures/paper_quality_calibration/dk_sidecar_ratings.json`.
5. The three repos are on clean branches, fast-forwarded, with
   baseline pytest counts recorded.

If any of those is not done, Codex will halt at pre-flight and post
a blocker. That is fine but wastes a round-trip.

---

## ===BEGIN===

You are Codex, terminal worker ID `codex-term` in the K-ATLAS multi-AI
coordination system. DK has authorised you to execute the paper-
quality build, a substantial multi-repo engineering task.

### Your job

Build the paper-quality fingerprint layer end to end across three
repositories: `atlas_shared`, `Article_Eater_PostQuinean_v1_recovery`,
and `Knowledge_Atlas`. The deliverable is thirteen sequenced commits
that ship the dataclass, contracts, extraction service, schema,
HTTP endpoints, UI block, overseer rollup, master-doc update, and
the blackboard coordination infrastructure.

The complete specification is in
`/Users/davidusa/REPOS/Knowledge_Atlas/docs/PAPER_QUALITY_BUILD_PROMPT_FOR_CODEX_2026-04-23.md`.
Read it in full before writing any code. Read also:

- `PAPER_QUALITY_PANEL_CONSULTATION_2026-04-23.md` — the
  methodological backbone the panel of Ioannidis, Nosek, Borsboom,
  Glasziou, and Simmons settled.
- `PAPER_QUALITY_SYSTEM_DESIGN_2026-04-23.md` — the ground-truth
  specification (file paths, contracts, tests, SQL tables). If the
  design document and the build prompt disagree, the design
  document wins.
- `PAPER_QUALITY_BLACKBOARD_DESIGN_2026-04-25.md` — the
  coordination architecture you are using instead of the legacy
  heartbeat-based coord server. The blackboard is the source of
  truth for what work has been done.
- `PAPER_QUALITY_V7_PIPELINE_INTEGRATION_2026-04-23.md` — how the
  two new lifecycle stages (18: `paper_quality_extraction`, 19:
  `paper_quality_finalisation`) attach to the existing 28-stage V7
  pipeline.
- `PAPER_QUALITY_DECISION_TREE_2026-04-23.md` — DK's annotated
  preferences (via the export at `data/paper_quality_dk_preferences.json`)
  set policy for every node-level choice the extractor encounters.
- `atlas_shared/AGENTS.md` — the "Do Not Reinvent" contract. Reuse
  what exists; do not add modules that duplicate atlas_shared
  primitives.

### Where to start

Run the pre-flight section of the build prompt verbatim, in this
order:

```bash
# Read the canonical specs first
cd /Users/davidusa/REPOS/Knowledge_Atlas
cat docs/PAPER_QUALITY_BUILD_PROMPT_FOR_CODEX_2026-04-23.md \
    docs/PAPER_QUALITY_BLACKBOARD_DESIGN_2026-04-25.md \
    docs/PAPER_QUALITY_DECISION_TREE_2026-04-23.md

# Confirm DK's annotations and anchor set are committed
cat data/paper_quality_dk_preferences.json | python3 -m json.tool | head -40
cat /Users/davidusa/REPOS/atlas_shared/tests/fixtures/paper_quality_calibration/anchor_set_manifest.json | python3 -m json.tool | head -20
cat /Users/davidusa/REPOS/atlas_shared/tests/fixtures/paper_quality_calibration/dk_sidecar_ratings.json | python3 -m json.tool | head -20

# Pre-flight commands per build prompt §2
cd /Users/davidusa/REPOS/atlas_shared
git fetch origin && git checkout master && git pull --ff-only
git checkout -b paper-quality-2026-04-25

cd /Users/davidusa/REPOS/Knowledge_Atlas
git fetch origin && git checkout master && git pull --ff-only
git checkout -b paper-quality-2026-04-25

cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1_recovery
git fetch origin && git checkout codex/recovery-cc-migration-artifacts && git pull --ff-only
git checkout -b paper-quality-2026-04-25

# Baseline test counts — record into reports/paper_quality_baseline_test_counts_2026-04-25.md
cd /Users/davidusa/REPOS/atlas_shared && pytest -q 2>&1 | tail -5
cd /Users/davidusa/REPOS/Knowledge_Atlas/backend && pytest -q 2>&1 | tail -5
cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1_recovery && pytest -q 2>&1 | tail -5
```

Record the baseline pass/fail/skip counts before touching any code.
Every commit you ship preserves or improves these counts. Any
regression stops the work pending DK review.

### Execution plan

Thirteen commits sequenced across three repos. The detailed spec
for each commit is in the build prompt §3. Headline summary:

**Pass 1 — atlas_shared foundations (Commits 1–4)**
- C1: `paper_quality.py` dataclass + `worker_loop.py` blackboard
  helper
- C2: `PAPER_QUALITY_FINGERPRINT_CONTRACT_2026-04-23.md`
- C3: `claim_strengths.py` aggregator with weighting function
- C4: `literature_body.py` aggregator + companion contract

**Pass 2 — Article_Eater extraction (Commits 5–6)**
- C5: `paper_quality_extraction.py` with per-field prompts in
  `prompts/paper_quality/`. Adapters are
  `atlas_shared.cli_adjudicator` patterns: `claude -p` for the
  Claude-class adapter, `codex exec` for the OpenAI-class adapter.
  **No API endpoints.** See build prompt §1.5.
- C6: golden-file tests including the four adversarial fixtures
  (multi-effect, OSF-mentioned-not-prereg, scattered-sample,
  hedged-construct). If any of the four adversarial fixtures passes
  without flags, the extractor is using shortcuts and the build
  halts.

**Pass 2.5 — Blackboard initialiser (Commit 6.5)**
- `scripts/paper_quality_blackboard_init.py` — generates the
  4 200-job manifest from the 1 400-paper corpus, populates
  `paper_quality_jobs` and `paper_quality_batches`, writes the
  empty mirror at `data/paper_quality_progress.json`. Idempotent.

**Pass 3 — Knowledge_Atlas storage + surface + UI (Commits 7–11)**
- C7: schema migration creating all the new tables, views, and the
  `paper_interpretation` stub (per Q21).
- C8: HTTP endpoints for claim strengths, literature-body quality,
  per-paper fingerprint.
- C9: Admin adjudication queue UI in `160sp/ka_admin.html`.
- C10: claim-strengths UI block on the journey-interpretation and
  journey-evidence pages.
- C11: overseer rollup script
  `scripts/overseer_paper_quality_rollup.py` (daily / weekly /
  monthly per Q18).

**Pass 4 — integration (Commit 12)**
- Master doc update, audit README update, route registration,
  full three-repo test matrix.

### Hard rules — non-negotiable

Per build prompt §4, nine hard rules. The three you are most likely
to be tempted to violate are restated here.

**Hard Rule 7**: seven of the eleven fields *must* be LLM-extracted.
No regex, keyword match, or heuristic shortcut. The unit tests
assert the LLM was actually invoked. A future PR that swaps in a
regex breaks the suite by construction.

**Hard Rule 8**: multi-LLM agreement runs both adapters as
independent processes. No skip-second-when-first-confident. No
re-using the first model's output as context for the second. The
adjudication step's input must be two structurally-independent
fingerprint records.

**Hard Rule 9**: confidence reporting includes five-sample
self-consistency at the chat interface's nearest-equivalent
sampling, plus the sampling-based logprob proxy (across-sample
agreement rate). Subscription chat interfaces do not expose
per-token logprobs; the proxy is the documented alternative.

### Failure handling — log and continue, don't halt

Per build prompt §5 (revised 2026-04-25):

- *Per-paper hard-rule violations* — record to
  `hard_rule_violations` table, mark the paper `held_for_review`,
  proceed to the next paper. Do not halt the build.
- *Calibration-set precision below 70 %* — halt. The extractor is
  not trustworthy for that field on any paper.
- *Schema-migration or test-suite regression* — halt. Subsequent
  commits cannot land cleanly on broken foundations.
- *Subscription rate limits or auth expiry* — retry with backoff
  up to three attempts; a fourth failure records a hard-rule
  violation and proceeds.

### Coordination — blackboard, not heartbeat

You do not heartbeat into the HTTP coord server for work-claiming
purposes. The blackboard tables (`paper_quality_batches`,
`paper_quality_jobs`) are the source of truth. Atomic UPDATE wins
the claim; failed claims retry the next batch. After each paper
completion, refresh the JSON mirror at
`data/paper_quality_progress.json` and commit locally. Every ~50
papers, push to GitHub so AG and other-sandbox workers can see
progress.

The HTTP coord server may stay running for the dashboard but you do
not depend on it.

### Reporting

When you finish (or when you blocker-halt), post to
`/Users/davidusa/REPOS/Knowledge_Atlas/COORDINATION.md` under the
heading `### Codex paper-quality build — landed` (or
`### Codex paper-quality build — blocker` if you halted). Include:

- Thirteen commit SHAs (one per commit above) with repo and
  message.
- Three-repo pytest counts pre and post.
- Calibration-report baseline numbers for every field.
- Per-field LLM call counts across the 24-fixture calibration run
  (Claude conversation count, ChatGPT conversation count, mean
  tokens per call, total wall-clock seconds).
- Five-sample self-consistency variance per LLM-required field.
- Confidence-distribution histogram per LLM-required field.
- Hard-rule-violation tally from `hard_rule_violations`.
- Subscription-interface error tally.
- Adjudication-queue depth after the synthetic smoke test (expect
  zero).
- Any deviations from this prompt and why.

Tag CW on COORDINATION.md when done. The next gate is the testing
pass, which AG runs from the kick-off prompt
`PAPER_QUALITY_AG_KICKOFF_PROMPT_2026-04-25.md`.

### Out of scope

- Retrofitting the existing 1 400-paper corpus. The blackboard
  initialiser generates the manifest including the existing corpus,
  but the actual retrofit run is a separate execution after the
  testing pass clears.
- The interpretation-layer integration (PQ-INTERP-001). You stub
  the `paper_interpretation` table in C7 and stop. The interpretation
  build is a separate pass.
- Demoting the existing HTTP coord server (PQ-COORD-CLEANUP-001).
  Out of scope for this build; queued as a follow-up.

### Timeline

Two-to-three working days for the build itself, assuming
subscription rate limits do not bind. The calibration run in Pass 2
(24 fixtures × 11 fields × 5 samples × 2 model families = 2 640
conversations) is the longest single step; budget half a day for it
and post progress if it takes longer than four hours of wall-clock
time.

After the build merges, AG runs the testing pass. Real-paper work
starts only after the testing pass is green.

### One final reminder

The hardening rules look paranoid (see build prompt §9). They exist
because a previous generation of automation in this lab has shown a
reliable habit of substituting Python heuristics for LLM calls when
work feels repetitive, faking multi-LLM agreement via single-model
runs, and converging confidence onto threshold-adjacent values that
bypass adjudication. The rules are written so that each shortcut, if
attempted, fails a specific test rather than slipping through. Do
not relax them from inside the build branch. If a rule looks
genuinely unworkable in a specific case, post the case under
`### Codex paper-quality build — rule challenge` and wait for DK.

Begin pre-flight now.

## ===END===

---

## Notes for DK before pasting

A few things to verify on your end before the kick-off goes in.

**1. The Codex CLI is authenticated**. Run `codex auth status`
(or whatever the current command is). You want to see ChatGPT Pro
authentication active. If it has expired, refresh it.

**2. The Claude CLI is authenticated** in the same way. Run
`claude auth status`. The Codex build needs both adapters working
because Hard Rule 8 forbids single-model agreement faking.

**3. The Anthropic and OpenAI API keys are *not* in your shell
environment**. Codex's pre-flight test will fail loudly if they
are. Run `env | grep -E "ANTHROPIC|OPENAI"` and make sure neither
`*_API_KEY` is set. If they are, `unset` them for the build's
shell session.

**4. The HTTP coord server can stay running** for the dashboard.
Codex does not depend on it but the dashboard is useful for you to
watch progress on `localhost:8420`.

**5. Plan for the build to run for two or three days**, with you
not needing to supervise. Codex will report back via
COORDINATION.md. If it halts, it halts loudly under the named
heading; if it does not, you see the green-light message.

**6. AG should be kicked off in parallel** to receive Probes 1, 2,
5 once Codex's build merges. Use the AG kick-off prompt
(`PAPER_QUALITY_AG_KICKOFF_PROMPT_2026-04-25.md`) to enrol AG.

**7. The walkthrough page** at
`160sp/ka_paper_quality_walkthrough.html` is your tool for the
22-node decision-tree pass. Open it locally in any browser; it
needs no server. Export the JSON when done; commit the exported
file at `data/paper_quality_dk_preferences.json`.

---

*End of Codex kick-off prompt.*
