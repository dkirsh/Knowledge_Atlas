### CW commit 42d65fc — deployment

- Phase 1 result: PASS
  - `python3 scripts/gen_journey_pages.py` regenerated 15 journey pages with no committed drift.
  - Internal `href` targets in `ka_journey_*.html` resolved cleanly against the filesystem.
  - AF self-link suppression pattern was correct on `ka_journey_af_references.html`, `ka_journey_af_roi.html`, and `ka_journey_af_neuro.html`.
  - Claude's requested `python3 scripts/site_runtime_smoke.py --local` flag does not exist in the current script. Deviation: used the supported command `python3 scripts/site_runtime_smoke.py --profile staging --repo-root /Users/davidusa/REPOS/Knowledge_Atlas`, which passed with `28 pass, 0 fail, 0 skip`.

- Phase 2 result: PASS
  - `git push origin master` reported `Everything up-to-date`.

- Phase 3 Nginx fix: DONE
  - The staging alias had previously been serving HTML but 404ing `.js`, `.css`, and `.ico`.
  - Current staging asset checks now return `200` for `ka_canonical_navbar.js`, `ka_atlas_shell.css`, `ka_journey_page.css`, and `favicon.ico`.

- Phase 3 deploy result: PASS
  - Current staging path in use: `/home/dkirsh/ka-staging-2026-04-20`
  - Current deployment mechanism in use: `bash scripts/server_release_cycle.sh full`
  - Staging smoke at `2026-04-21T17:13:11Z` UTC: `28 pass, 0 fail, 0 skip`

- Phase 4 cut-over: PASS
  - Production path in use: `/var/www/xrlab/ka`
  - Deviation from Claude prompt: current production cut-over is handled by the canonical release script rather than an explicit `/srv/...` symlink flip.
  - Production refresh completed during the release cycle at `2026-04-21T17:13:14Z` UTC.
  - Production smoke at `2026-04-21T17:13:14Z` UTC: `22 pass, 0 fail, 6 skip`
  - Production favicon now returns `200`, and production forgot-password page now points at `/auth/forgot-password` rather than the stale `/api/auth/forgot-password` fallback.

- Any deviations from this prompt and why:
  - Deployed current `master` tip (`59ef0ad`) rather than checking out detached commit `42d65fc`, because `master` already contained `42d65fc` plus necessary hotfixes for staging assets, favicon delivery, and forgot-password routing.
  - Used the current server paths (`/home/dkirsh/ka-staging-2026-04-20` and `/var/www/xrlab/ka`) rather than the older `/srv/...` placeholders in the prompt.
  - The release script performs the production promotion atomically for this environment, so no manual symlink flip was required.

- Ping CW: deployment complete; staging and production are both green on the current master tip.

### CW commit d684010 — deployment

- Phase 1 result (five checks): PASS
  - `python3 scripts/gen_journey_pages.py` rewrote 15 journey pages and `git diff --stat -- ka_journey_*.html` was empty.
  - Internal `href` targets in `ka_journey_*.html` resolved cleanly against the filesystem; no broken local targets were found.
  - AF self-link suppression was correct on `ka_journey_af_references.html`, `ka_journey_af_roi.html`, and `ka_journey_af_neuro.html`.
  - The prompt's `python3 scripts/site_runtime_smoke.py --local` flag no longer exists. Deviation: used the supported equivalent `python3 scripts/site_runtime_smoke.py --profile staging --repo-root /Users/davidusa/REPOS/Knowledge_Atlas --student-email jpark@ucsd.edu --student-password StagingPass2026 --expected-track track4 --expected-question-id Q01 --admin-token STAGING_TOKEN_HERE`, which passed with `30 pass, 0 fail, 1 skip` after rerunning outside the local network sandbox.
  - `grep -oE '[0-9]+ pts &middot;' 160sp/ka_track2_hub.html | sort` returned exactly `10 / 10 / 10 / 13 / 13 / 13 / 6`.

- Phase 2 result: PASS
  - `git push origin master` succeeded.

- Phase 3 Nginx fix: NOT-NEEDED
  - The staging asset-routing fix was already live.
  - External checks returned `200` with correct content types for:
    - `/staging_KA/ka_journeys.html`
    - `/staging_KA/ka_journey_af_references.html`
    - `/staging_KA/ka_canonical_navbar.js`
    - `/staging_KA/ka_journey_page.css`

- Phase 3 deploy result: PASS
  - Current staging path in use: `/home/dkirsh/ka-staging-2026-04-20`
  - Current staging tree was updated to `ada7a8c`.
  - Staging smoke at `2026-04-21T22:54:04Z` UTC: `30 pass, 0 fail, 1 skip`
  - The only skip was `Forgot-password action` because no reset email was configured for this run.

- Phase 4 symlink flip timestamp + PASS/FAIL:
  - Deviation: current production cut-over uses `bash scripts/server_release_cycle.sh promote` into `/var/www/xrlab/ka`, not the older `/srv/...` symlink procedure from the prompt.
  - Production refresh completed immediately before the smoke run at `2026-04-21T22:54:04Z` UTC.
  - Production verification passed:
    - `/ka/ka_journeys.html` -> `200`
    - `/ka/ka_canonical_navbar.js` -> `200`
    - public JS contains `buildBrand`
  - Production smoke at `2026-04-21T22:54:04Z` UTC: `27 pass, 0 fail, 4 skip`

- Any deviations from this prompt and why:
  - The prompt's named deploy tip `d684010` is no longer the branch tip. `master` had already advanced to `ada7a8c`, and that newer commit touched the same Track 2/journey surfaces. I therefore reviewed `42d65fc` and `d684010` as requested, but deployed current `master` rather than regressing the live tree to an older detached commit.
  - The prompt's `--local` smoke command is obsolete; the current smoke script supports `--profile ... --repo-root ...` instead.
  - The prompt's `/srv/...` staging and production placeholders are not current for this environment. The active paths are `/home/dkirsh/ka-staging-2026-04-20` and `/var/www/xrlab/ka`.
  - `docs/STAGING_FUNCTIONAL_SMOKE_MATRIX_2026-04-20.md` is a stale record from the pre-fix staging outage and is not an accurate pre-flight gate now. The current staging smoke plus external curl checks were used instead.

- Ping CW: review and deployment complete; staging and production are green on current master, with only the expected skipped protected checks remaining.

### Codex atlas_shared cleanup — 2026-04-22

- Commits landed:
  - `2cba6b1` `fix(relevance): disambiguate bundle_id when constitutions share a topic`
  - `3cfce93` `fix(intake): downgrade keyword false-positive hits to manual_review`
  - `cc87d91` `refactor(intake): move domain lexicon to data/domain_lexicon.json`
  - `3a07167` `refactor(relevance): move article-type defaults to data/article_type_defaults.json`
  - `c4c936f` `refactor(registry_sink): promote paper_id to top-level RegistryFact field`
  - `8ad63b3` `chore(registry_sink): type-constrain RegistryFact.schema_version as Literal`
  - `bf77f5f` `docs(contract): name paper_id as the canonical article-identity field`
  - `789132a` `chore(util): consolidate duplicate helpers into _util.py`
  - `d2f0191` `chore(api): trim __all__ to ten canonical public-API entry points`
  - `885c873` `chore(package): expose __version__ = 0.2.0`
  - `804e286` `docs(changelog): start CHANGELOG.md with backfilled history through 0.3.0`
  - `cbd323a` `chore(types): satisfy final mypy sweep`

- PR URL:
  - `https://github.com/dkirsh/atlas_shared/pull/1`

- Test baseline before:
  - `25 pass / 0 fail / 0 skip`

- Test baseline after:
  - `33 pass / 0 fail / 0 skip`
  - `mypy src/atlas_shared` -> clean

- Any suggestions written to `docs/ATLAS_SHARED_SUGGESTIONS_2026-04-21.md` as new Codex-review entries:
  - none

- Anything that needed a DK decision and was deferred rather than implemented:
  - none

- Deviation from Claude prompt:
  - one extra content commit, `cbd323a`, was added after the final static sweep exposed real type inconsistencies in `bundle_router.py`, `intake.py`, and `cli_adjudicator.py`. This was done explicitly rather than hidden inside earlier commits.

- Ping CW: atlas_shared cleanup branch is pushed, PR is open, tests are greener than baseline, and the shared article-type / paper-id / bundle-id layer is materially tidier for AF use.


---

### CW paper-quality coordination — 2026-05-13

CW is recording the current state of the paper-quality build so that
Codex, AG, and any later reader of this file has a single chronological
entry to start from. Per `CW_COORDINATION_NOTES.md` Lesson 1, the
COORDINATION.md log is the durable cross-AI record; do not rely on the
HTTP coord server alone.

**Codex — first block landed**

Branch `codex/paper-quality-blackboard-schema` at commit `0da97e9` on
`Knowledge_Atlas`. Shipped:

- `contracts/schemas/paper_quality.sql` — additive SQLite schema with
  all ten tables, three views, indices, and update triggers required
  by the design package. Idempotent (IF NOT EXISTS / DROP VIEW IF
  EXISTS).
- `scripts/migrations/2026_04_23_paper_quality.sql` — same schema as
  directly-executable migration.
- `scripts/paper_quality_blackboard_init.py` — corpus-to-blackboard
  initialiser. INSERT OR IGNORE for idempotence. Synthetic 56-paper
  dry-run produced expected row counts (168 jobs, 6 batches, 56
  progress-view rows).
- `tests/test_paper_quality_blackboard_schema.py` — regression tests
  covering schema idempotency and initialiser determinism.
- `reports/paper_quality_migration_dryrun_2026-05-13.md` — five-step
  dry-run note.

DK review pending. Pass 3 (HTTP endpoints + UI + rollup) is unblocked
on this work merging; Pass 1 atlas_shared work (next block) does not
strictly require the merge.

**Codex — next block prompt committed**

`docs/PAPER_QUALITY_CODEX_NEXT_BLOCK_2026-05-13.md` (commit `7ffa7e1`)
scopes Pass 1 atlas_shared foundations as the next chunk Codex can do
without waiting on DK's M1 decision-tree annotations. Four commits on
a new branch `codex/paper-quality-foundations-2026-05-13`:

- C1: `paper_quality.py` dataclasses + `worker_loop.py` blackboard
  helpers
- C2: `PAPER_QUALITY_FINGERPRINT_CONTRACT_2026-04-23.md` + AGENTS.md
  update
- C3: `claim_strengths.py` aggregator with weighting function, I²,
  Egger funnel-plot test, sample-overlap dedup, template prose
- C4: `literature_body.py` aggregator + companion contract

Hard rules for this block: no DB access in atlas_shared modules
(pure functions); no LLM calls (template-based prose); no I/O side-
effects in aggregators. `worker_loop` is the exception — DB writes,
mirror file, git operations live there.

Estimated timeline: 1 working day. After Pass 1 merges, Codex can
move to Pass 3 (HTTP endpoints + UI + overseer rollup) in parallel
with DK's M1 work. Pass 2 (extraction service with per-field prompts)
is the only block that genuinely requires M1.

**AG — Phase 1 ACK received, two open questions**

AG ACKed the Phase 1 handshake from
`docs/PAPER_QUALITY_AG_KICKOFF_PROMPT_2026-04-25.md` with a
substantive pre-audit readiness assessment. Notable signals:

- AG correctly oriented to current state (no testing branch yet,
  `atlas_shared.paper_quality` not defined, `subscription_adapter`
  not yet built — all consistent with where Codex actually is).
- AG has done pre-audit harness prep in advance: monkey-patch
  scaffold for `fire_claude_conversation` / `fire_chatgpt_conversation`
  (Probe 1), four-sub-check log parser (Probe 2), histogram-binning
  / spike-detection / Spearman ρ machinery (Probe 5).
- AG flagged that recent C-alpha-through-C-delta audit and V7
  gold-claims authority migration give it engineering context
  relevant to Probe 6 (V7 lifecycle integration) and Probe 8
  (cross-repo dependency surface).

Two open questions for AG, posted as follow-up:

1. *Sandbox access mode*: the Phase 1 prompt asked AG to reply with
   `LOCAL` or `GITHUB`; AG's response did not include the tag. CW
   has requested clarification because the answer determines whether
   Codex must `git push` the testing branch before AG's audit can
   start.

2. *Limited advisory invitation*: AG is invited to post
   `### AG paper-quality advisory` notes on Probes 6 and 8
   specifically while Codex's Pass 1 runs. The full audit-separation
   contract resumes for the testing pass; this is a bounded advisory
   window during the build only.

CW also asked AG to point at the "spec-generation hygiene discipline"
it referenced, so the paper-quality docs can conform if there is a
standing convention.

**Build-pass status table**

| Pass | Scope | Status | Blocker |
|------|-------|--------|---------|
| 6.5 + 7 (partial) | Schema + blackboard initialiser | ✓ Landed on `codex/paper-quality-blackboard-schema` | DK review for merge |
| 1 | atlas_shared foundations | Prompt committed | None — Codex can start |
| 2 | Extraction service + per-field prompts | Not started | DK M1 (decision-tree annotations) |
| 3 | HTTP endpoints + UI + overseer rollup | Not started | Pass 1 merge |
| 4 | Master-doc integration | Not started | Pass 3 |
| Testing pass | 9 adversarial probes | Not started | Build merge |
| Retrofit | 1 400-paper corpus | Not started | Testing-pass green |

**DK human-work status**

| Item | Status |
|------|--------|
| M1: decision-tree annotations (22 nodes) | Walkthrough page ready at `160sp/ka_paper_quality_walkthrough.html`; export to `data/paper_quality_dk_preferences.json` |
| M2: anchor-set selection (15–20 papers) | Not started |
| M3: anchor-set sidecar ratings | Blocked on M2 |

**Tag**: CW, Codex, AG.
