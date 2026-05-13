# Paper-Quality Build — Preconditions Checklist

**Document**: `PAPER_QUALITY_PRECONDITIONS_2026-04-25.md`
**Companions**: `PAPER_QUALITY_BUILD_PROMPT_FOR_CODEX_2026-04-23.md`,
`PAPER_QUALITY_TESTING_PROMPT_FOR_CODEX_2026-04-25.md`,
`PAPER_QUALITY_BLACKBOARD_DESIGN_2026-04-25.md`,
`PAPER_QUALITY_DECISION_TREE_2026-04-23.md`.
**Authorising reviewer**: DK, 2026-04-25.

---

## Purpose

The paper-quality build is gated on items that are not engineering
work but coordination, judgement, and access checks. This document
inventories every precondition, names its owner, and gives a
verification step so that when Codex is finally handed the build
prompt, no item turns out to be missing mid-run.

The document is intentionally a checklist rather than prose: it
should be readable at a glance, and each item should be either
checked or unchecked. Items in the *Methodological*, *Engineering*,
*Coordination*, and *Access* groups must all be satisfied before
Codex begins.

---

## Methodological preconditions (DK)

These require DK's judgement. They cannot be substituted, deferred,
or generated automatically.

### M1 — Decision-tree annotations complete

- [ ] All 22 nodes in `PAPER_QUALITY_DECISION_TREE_2026-04-23.md`
      have a DK preference recorded.
- [ ] Each annotation is either (a) a listed option selected, (b) a
      modification of a listed option, or (c) an "Other — write in"
      with two-to-four sentences of rationale.
- [ ] The interactive walkthrough at
      `160sp/ka_paper_quality_walkthrough.html` has exported a
      JSON file to `data/paper_quality_dk_preferences.json`.
- **Owner**: DK
- **Time estimate**: 2–3 hours
- **Verification**: open the walkthrough page; progress indicator
  shows 22/22 answered; export produces a JSON file with 22 entries.

### M2 — Anchor-set papers selected

- [ ] 15–20 papers chosen from the existing 1 400-paper corpus.
- [ ] The set spans the five document types (lab experiment, field
      study, secondary analysis, meta-analysis, theoretical paper).
- [ ] The set spans the four eras (pre-2010, 2010–2014, 2015–2019,
      2020+).
- [ ] The set spans the relevant sub-areas of the corpus
      (cognitive-architecture, environment-and-cognition, neuroscience,
      methodology).
- [ ] The selection is committed to
      `atlas_shared/tests/fixtures/paper_quality_calibration/anchor_set_manifest.json`.
- **Owner**: DK
- **Time estimate**: 1–2 hours of reading and selection
- **Verification**: file exists; spans verified by a script that
  reads the manifest and prints distribution by type / era /
  sub-area.

### M3 — Anchor-set sidecar ratings

- [ ] For each anchor paper, DK has rated the four human-only
      sidecar fields: construct-validity verdict, generalisation
      envelope, methodological severity, theoretical importance.
- [ ] Ratings stored in
      `atlas_shared/tests/fixtures/paper_quality_calibration/dk_sidecar_ratings.json`.
- **Owner**: DK
- **Time estimate**: 4–6 hours of focused reading (≈ 20 min per
  paper)
- **Verification**: file exists with 15–20 entries; each entry has
  all four sidecar values populated.

---

## Engineering preconditions (CW / Codex)

These are infrastructure pieces that must exist before Codex's
build script can start. CW can stage most of them; some are
Codex's responsibility once it begins.

### E1 — Per-field extraction prompts drafted

- [ ] Eleven prompt files in
      `Article_Eater_PostQuinean_v1_recovery/prompts/paper_quality/`,
      one per fingerprint field.
- [ ] Each prompt file contains: input format spec, output JSON
      schema, edge cases, at least three few-shot examples.
- [ ] Prompts informed by the DK preferences from M1 — the
      annotated decision tree is the source for what each field's
      prompt should ask.
- **Owner**: CW (drafts) → DK (review) → Codex (uses in build)
- **Time estimate**: 4–6 hours
- **Verification**: 11 files exist under the prompts directory; a
  prompt-lint script confirms each has the required sections.

### E2 — V7 pipeline migration dry-run validated

- [ ] Migration script
      `scripts/migrations/2026_04_23_paper_quality.sql` applied
      against a *copy* of `pipeline_lifecycle_full.db`.
- [ ] Idempotency confirmed (script can re-run on the same DB
      without error or row duplication).
- [ ] Renumbering of existing stages 18–28 → 20–30 verified not to
      break existing lifecycle queries.
- [ ] Auxiliary tables (`fingerprint_staging`,
      `quality_adjudication_queue`, `quality_calibration_history`,
      `hard_rule_violations`, `holding_pen`, `paper_interpretation`,
      `paper_quality_batches`, `paper_quality_jobs`) all created with
      expected schema.
- **Owner**: CW (drafts) → Codex (re-validates in build)
- **Time estimate**: 1 hour
- **Verification**: dry-run report committed under
  `reports/paper_quality_migration_dryrun_<date>.md`.

### E3 — Subscription-adapter availability

- [ ] `claude -p --output-format json` is installed and authenticated
      on DK's Mac.
- [ ] `codex exec -m <model>` is installed and authenticated.
- [ ] `atlas_shared.cli_adjudicator` invokes both successfully on a
      synthetic test prompt.
- [ ] No `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` environment
      variables are set during build (test asserts this).
- **Owner**: CW + DK (auth)
- **Time estimate**: 30 minutes
- **Verification**: a smoke test in
  `atlas_shared/tests/test_subscription_adapter_smoke.py` fires one
  conversation through each CLI and asserts a non-empty JSON
  response.

### E4 — Blackboard initialiser draft

- [ ] `scripts/paper_quality_blackboard_init.py` exists in CW's
      working tree.
- [ ] Script generates the 4 200-job manifest from the corpus list.
- [ ] Script produces an empty mirror at
      `data/paper_quality_progress.json`.
- **Owner**: CW (drafts) → Codex (uses in Commit 6.5)
- **Time estimate**: 2 hours
- **Verification**: running the script on a 10-paper dummy corpus
  produces 30 job rows and a mirror file.

---

## Coordination preconditions

These ensure the multi-AI workflow does not collide.

### C1 — AG availability for separated-auditor role

- [ ] AG has been asked (via COORDINATION.md or coord server
      message) whether it can take the auditor role for testing-pass
      Probes 1, 2, and 5.
- [ ] AG has responded affirmatively.
- [ ] AG's sandbox has read access to the three repos
      (`atlas_shared`, `Article_Eater_PostQuinean_v1_recovery`,
      `Knowledge_Atlas`) at `/Users/davidusa/REPOS/...`, *or* a
      GitHub-based audit path has been agreed.
- **Owner**: DK + AG
- **Time estimate**: 1–2 messages, plus AG's response window
- **Verification**: AG's reply visible in COORDINATION.md or coord
  server message log.

### C2 — Codex availability and Pro-tier access confirmed

- [ ] Codex CLI authenticated against DK's ChatGPT Pro account.
- [ ] Concurrent Codex CLI invocation tested (4 simultaneous
      `codex exec` calls succeed without rate-limit errors).
- **Owner**: DK + Codex
- **Time estimate**: 30 minutes
- **Verification**: a Bash one-liner spawns 4 parallel `codex exec`
  calls on trivial prompts; all 4 return non-empty results.

### C3 — Claude CLI Max-tier access confirmed

- [ ] `claude -p` authenticated against DK's Claude Max account.
- [ ] Concurrent `claude -p` invocation tested (4 simultaneous calls
      succeed).
- **Owner**: DK + CW
- **Time estimate**: 15 minutes
- **Verification**: same as C2 with `claude -p` substituted.

### C4 — Gemini access confirmed

- [ ] Gemini API or subscription access available to AG.
- [ ] Rate limits sufficient for verification load (estimated 1 400
      verifications × 1 call each, well within high-tier limits).
- **Owner**: DK + AG
- **Time estimate**: 15 minutes
- **Verification**: a test verification call returns a non-empty
  result.

### C5 — Repos on clean branches

- [ ] `atlas_shared` on `master`, fast-forwarded.
- [ ] `Knowledge_Atlas` on `master` (or `main`), fast-forwarded.
- [ ] `Article_Eater_PostQuinean_v1_recovery` on
      `codex/recovery-cc-migration-artifacts`, fast-forwarded.
- [ ] No uncommitted changes in any of the three working trees.
- [ ] No untracked files that another worker would expect to find
      committed.
- **Owner**: DK + CW
- **Time estimate**: 5 minutes
- **Verification**: `git status` clean in all three repos.

### C6 — Baseline test counts recorded

- [ ] `pytest -q` run in each of the three repos before the build
      starts.
- [ ] Pass / fail / skip counts recorded in
      `reports/paper_quality_baseline_test_counts_<date>.md`.
- [ ] Every commit in the build's 12-commit (now 13-commit) plan
      preserves or improves these counts.
- **Owner**: CW or Codex (pre-flight script)
- **Time estimate**: 15 minutes
- **Verification**: baseline file exists.

---

## Access preconditions

These are about DK's accounts and the lab's services.

### A1 — Disk and DB capacity

- [ ] `pipeline_lifecycle_full.db` has at least 100 MB of free space
      (the new tables expand the DB by an estimated 30–50 MB once
      the 1 400-paper corpus is fingerprinted).
- [ ] The 5 TB external disk is mounted and has > 100 GB free for
      anchor-set fixture PDFs and per-paper conversation transcripts.
- **Owner**: DK
- **Time estimate**: 5 minutes
- **Verification**: `df -h` shows expected free space; `sqlite3` can
  open the DB.

### A2 — GitHub push access

- [ ] DK's Mac can `git push` to the three repos without
      reauthentication during the run.
- [ ] If 2FA tokens are expired, refresh them.
- **Owner**: DK
- **Time estimate**: 5 minutes
- **Verification**: a no-op commit on each repo pushes successfully.

### A3 — Recent backups

- [ ] The three repos backed up in the last 24 hours (Time Machine,
      or `git push` to GitHub, whichever serves as the recovery
      point).
- [ ] `pipeline_lifecycle_full.db` backed up in the last 24 hours.
- **Owner**: DK
- **Time estimate**: 5 minutes if Time Machine is current; longer if
  manual.
- **Verification**: backup timestamps visible.

---

## Pre-flight summary

The Codex build is ready to start when every box in the four groups
above is checked. The critical path is:

1. **DK's human work** (M1, M2, M3) — roughly 8 hours of focused
   time, spread over however many sessions DK wants.
2. **Engineering prep** (E1, E2, E3, E4) — roughly 8 hours of CW
   work, can run in parallel with DK's human work.
3. **Coordination handshakes** (C1–C6) — roughly 1 day calendar
   time (AG and Codex response windows).
4. **Access verification** (A1–A3) — roughly 30 minutes of DK time.

Items can run in parallel; the gating chain is M1 → E1 (because the
per-field prompts are informed by the decision-tree annotations) and
M2 → E2 (because the anchor-set manifest determines the calibration
fixtures).

When every box is checked, Codex receives:

- `PAPER_QUALITY_BUILD_PROMPT_FOR_CODEX_2026-04-23.md`
- `PAPER_QUALITY_BLACKBOARD_DESIGN_2026-04-25.md`
- `PAPER_QUALITY_DECISION_TREE_2026-04-23.md` (with annotations)
- `data/paper_quality_dk_preferences.json`
- `atlas_shared/tests/fixtures/paper_quality_calibration/anchor_set_manifest.json`
- `atlas_shared/tests/fixtures/paper_quality_calibration/dk_sidecar_ratings.json`
- pointer to the eleven per-field prompts under
  `Article_Eater_PostQuinean_v1_recovery/prompts/paper_quality/`

After the build completes and merges, AG receives:

- `PAPER_QUALITY_TESTING_PROMPT_FOR_CODEX_2026-04-25.md`
- the testing branch in each repo
- a message via COORDINATION.md pointing at the verification probes
  it is responsible for (Probes 1, 2, 5).

---

## Current status (snapshot 2026-04-25)

| Group | Item | Status | Owner | Blocker |
|-------|------|--------|-------|---------|
| Methodological | M1 — Decision tree annotations | ⊘ Not started | DK | Walkthrough page ready (PQ-WALKTHRU-001 ✓) |
| Methodological | M2 — Anchor-set papers selected | ⊘ Not started | DK | None |
| Methodological | M3 — Anchor-set sidecar ratings | ⊘ Blocked | DK | M2 |
| Engineering | E1 — Per-field extraction prompts | ⊘ Blocked | CW | M1 |
| Engineering | E2 — V7 migration dry-run | ⊘ Not started | CW | None |
| Engineering | E3 — Subscription-adapter smoke | ⊘ Not started | CW + DK | None |
| Engineering | E4 — Blackboard initialiser | ⊘ Not started | CW | None |
| Coordination | C1 — AG auditor handshake | ⊘ Not asked | DK + AG | None |
| Coordination | C2 — Codex Pro confirmation | ⊘ Not tested | DK + Codex | None |
| Coordination | C3 — Claude Max confirmation | ⊘ Not tested | DK + CW | None |
| Coordination | C4 — Gemini access | ⊘ Not tested | DK + AG | None |
| Coordination | C5 — Clean branches | ⊘ Likely OK | DK + CW | None |
| Coordination | C6 — Baseline test counts | ⊘ Not done | CW or Codex | None |
| Access | A1 — Disk and DB capacity | ⊘ Not checked | DK | None |
| Access | A2 — GitHub push | ⊘ Likely OK | DK | None |
| Access | A3 — Recent backups | ⊘ Not confirmed | DK | None |

Of the sixteen items, two are CW-doable now without DK input (E2,
E4); two more are CW-doable but bounded by DK's human-work outputs
(E1 depends on M1; the per-field prompts will be drafted as
placeholders that DK reviews after M1 lands). The remaining twelve
are DK or DK + coordinating-AI handshakes.

The single highest-leverage item DK can do *right now* is M1 — the
decision-tree annotations — because it unblocks E1, which is the
largest engineering item still gating Codex.

---

*End of preconditions. Update the status table as items complete.*
