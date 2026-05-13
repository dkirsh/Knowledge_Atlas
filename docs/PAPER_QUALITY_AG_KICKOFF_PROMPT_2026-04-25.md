# Paper-Quality Testing — AG (Gemini) Kick-Off Prompt

**Document**: `PAPER_QUALITY_AG_KICKOFF_PROMPT_2026-04-25.md`
**Purpose**: the operational message DK posts to AG (via
COORDINATION.md and / or the coord server message system) to enrol
AG in the separated-auditor role for the paper-quality testing
pass.
**Authorising reviewer**: DK, 2026-04-25.
**Two-phase kick-off**:
  Phase 1 — handshake (post when Codex begins the build); 
  Phase 2 — execution (post when Codex finishes and AG should run
  the audit probes).

---

## How to use this document

There are two messages here, separated by markers. Post the first
when you start Codex's build pass, so AG has advance notice. Post
the second when Codex's build merges to `master` / `main`, so AG
knows to start the audit. AG can ACK the first message and stand
by; the second triggers the actual probes.

---

## Phase 1 — handshake (post when Codex begins)

### ===BEGIN PHASE 1===

AG — paper-quality testing pass requires your separated-auditor
role. This is a Phase 1 advance-notice so you can prepare; the
actual work starts after Codex's build merges.

**Your role**: separated auditor for testing-pass Probes 1, 2, and
5. These are the high-stakes probes that directly check the
failure modes the hardening was designed to prevent — heuristic
substitution, multi-LLM faking, threshold gaming. Per DK's
2026-04-25 decision (review answer to Q19), these three probes
must be re-run by an agent different from the one that built the
layer. Codex builds; you audit.

The other six probes (3, 4, 6, 7, 8, 9) are run by Codex from
within the testing branch. Your three probes are independent.

**Why Gemini-as-auditor matters**: the whole point of the
separated-auditor pattern is that builder and auditor must not
collude on the same shortcuts. Codex and Claude share enough of
their training lineage that an extraction shortcut that fools one
may fool the other. Gemini has different training data and a
different alignment regime; that independence is the signal we
need.

**Read first** (before Phase 2 arrives so you do not start
unprepared):

- `/Users/davidusa/REPOS/Knowledge_Atlas/docs/PAPER_QUALITY_TESTING_PROMPT_FOR_CODEX_2026-04-25.md`
  — the full testing-prompt specification. You will run §2 Probes
  1, 2, and 5 from this document. Read all nine probes for context
  but execute only those three.
- `/Users/davidusa/REPOS/Knowledge_Atlas/docs/PAPER_QUALITY_BUILD_PROMPT_FOR_CODEX_2026-04-23.md`
  — the build prompt. You audit against the Hard Rules in §4,
  particularly Rules 7, 8, and 9 (LLM-required fields,
  multi-LLM independence, distributional confidence).
- `/Users/davidusa/REPOS/Knowledge_Atlas/docs/PAPER_QUALITY_BLACKBOARD_DESIGN_2026-04-25.md`
  — the coordination architecture you and Codex both operate
  under. The blackboard tells you what Codex has built; you do not
  need Codex's status reports to know whether work is done.

**Repository access**: confirm you can read
`/Users/davidusa/REPOS/atlas_shared`,
`/Users/davidusa/REPOS/Knowledge_Atlas`, and
`/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1_recovery` from
your sandbox. If you can, the audit runs locally. If you cannot,
the audit runs against the GitHub remote after Codex pushes the
testing branch; reply with which mode you will use so DK can
confirm Codex pushes ahead of your audit.

**Coordination contract**:

1. ACK this message within your normal SLA window. Format:
   `ACK Phase 1 paper-quality auditor handshake — repo access
   [LOCAL|GITHUB] — Phase 2 awaited`.
2. Stand by. Codex's build runs for 2-3 working days. You will be
   pinged with the Phase 2 message when it merges.
3. During the build, do not claim or process any paper-quality
   batches. Your role is strictly audit; participating in the build
   would violate the adversarial-separation contract.
4. If you see Codex's build raise blockers in COORDINATION.md and
   you have substantive engineering advice, post it as an advisor
   message under `### AG paper-quality advisory` — but do not pick
   up the work yourself.

### ===END PHASE 1===

---

## Phase 2 — execution (post when Codex's build merges)

### ===BEGIN PHASE 2===

AG — Codex's paper-quality build has merged to master / main across
all three repos. The Phase 2 audit begins now.

**Your three probes** (from
`PAPER_QUALITY_TESTING_PROMPT_FOR_CODEX_2026-04-25.md` §2):

**Probe 1 — Heuristic-detection canary.** For each of the seven
LLM-required fields (construct claim, sample composition,
multiple-comparisons handling, COI disclosure, replication-record
search, rhetorical-flag detection, effect-size precision):
1. Run the extractor on a known-good fixture from the calibration
   set with normal subscription adapters.
2. Patch `atlas_shared.subscription_adapter.fire_claude_conversation`
   and `fire_chatgpt_conversation` to raise
   `RuntimeError("Subscription adapter disabled for canary test")`.
3. Re-run the extractor on the same fixture.
4. Assert the extractor either raises the RuntimeError or routes
   the field to adjudication with confidence 0.0. Any successful
   extraction under patched adapters is a fail.

Pass criterion: all seven fields fail under subscription-disabled
mode. Failure indicates Codex's build snuck a regex shortcut past
the build prompt's Hard Rule 7. Report which field, the call
stack, and what shortcut you found.

**Probe 2 — Conversation-transcript audit.** Instrument both
adapters' `fire_*_conversation` entry points to log every
conversation. Run the extractor across the 24-fixture set. Parse
the audit log and assert:
1. Every paper produced ≥ N Claude and ≥ N ChatGPT conversations
   where N = number of LLM-required fields.
2. No Claude `response_hash` appears as the `prompt_hash` (or
   substring) of any ChatGPT call on the same paper, and vice
   versa.
3. The `session_id` for Claude and ChatGPT on the same paper
   differ.
4. Per-paper `conversation_id` values do not overlap with any
   other paper's conversations.

Pass criterion: all four sub-assertions hold across all 24 papers.
Failure indicates Codex faked multi-LLM agreement (single-model
masquerading as dual) or batched papers in a way that contaminated
context.

**Probe 5 — Confidence-distribution audit.** Across the 24-fixture
set, collect every per-field point confidence. Bin into 20 bins
from 0.0 to 1.0. Assert:
1. The empirical distribution does not have a spike at any single
   bin in the 0.85–0.90 range (spike = bin count ≥ 1.5× neighbour
   mean).
2. Each field's confidence lands in at least 8 of 20 bins.
3. The sampling-based logprob proxy (across-five-sample agreement
   rate) correlates with the point confidence at Spearman ρ ≥ 0.5
   across the fixture set.

Pass criterion: all three sub-assertions hold. Failure indicates
confidence-gaming (fabricated values to bypass the 0.85
adjudication threshold) or confidences not grounded in the
sampling proxy.

**Mechanics**:

1. Check out the testing branch in each repo:
   ```bash
   cd /Users/davidusa/REPOS/atlas_shared && \
     git checkout paper-quality-testing-2026-04-25
   cd /Users/davidusa/REPOS/Knowledge_Atlas && \
     git checkout paper-quality-testing-2026-04-25
   cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1_recovery && \
     git checkout paper-quality-testing-2026-04-25
   ```
   (Or pull from GitHub if your sandbox does not have local repo
   access.)

2. Run each probe per the testing prompt §2. Each probe produces:
   - a pass / fail verdict
   - a diagnostic JSON at
     `reports/paper_quality_testing_probe<N>_<timestamp>.json`
   - a two-paragraph entry in
     `reports/paper_quality_testing_summary_2026-04-25.md`

3. Operate ballistically per build prompt §1.5 and §5: every probe
   runs regardless of earlier probe outcomes. Record state, do not
   halt. Failure of one probe does not stop the next.

4. Compare your verdicts to Codex's own verdicts (Codex will have
   run all nine probes from inside the build). Discordance on
   Probes 1, 2, or 5 between Codex and you forces a full re-run of
   the build — the discordance itself is the red flag, regardless
   of which side reported pass and which reported fail.

**Reporting**:

When your three probes finish, post to
`/Users/davidusa/REPOS/Knowledge_Atlas/COORDINATION.md` under
`### AG paper-quality audit — landed`. Include:

- Per-probe verdict (pass / fail) with metric.
- Path to the diagnostic JSON for each probe.
- Comparison with Codex's verdicts on the same three probes. If
  any discordance: mark `DISCORDANT` and stop the layer's go-live
  decision pending DK review.
- Wall-clock time per probe.
- Any deviations from this prompt and why.

Tag CW and DK on COORDINATION.md when done.

**Discordance protocol**: if you find any discordance on Probes 1,
2, or 5, post the discordance under `### AG paper-quality audit
— discordance` immediately with the specific assertion that
differs. DK reviews; build may be re-opened. Do not attempt to
resolve discordance yourself; the whole point of separated audit
is that the two verdicts stay independent.

**Out of scope for your audit**:

- Probes 3, 4, 6, 7, 8, 9 — these are Codex's responsibility.
- Real-paper extraction or fingerprinting. The retrofit on the
  1 400-paper corpus only begins after both gates clear; that work
  will be a separate enrolment.
- Modifying the build code or the testing prompts. If you find a
  rule that needs revision, file a rule-change request in
  COORDINATION.md and wait.

**Timeline**: roughly one working day for your three probes plus
the discordance comparison with Codex. If you exceed two working
days, post a progress message so DK and CW can intervene if
needed.

### ===END PHASE 2===

---

## Notes for DK before posting

A few coordination items to handle before AG starts.

**1. Confirm AG's sandbox access** to the three repos. Post Phase 1
as an explicit question — "can you read
/Users/davidusa/REPOS/atlas_shared, Knowledge_Atlas, and
Article_Eater_PostQuinean_v1_recovery from your current sandbox?"
— and wait for AG's ACK reply. If AG says no, the audit runs against
GitHub remote and Codex's build must `git push` before AG starts.

**2. Confirm AG has Gemini access** at the tier you specified
(high-tier, not free). The audit calls do not need many requests
(~100 across the 24-fixture set for Probe 5), so free tier would
likely suffice, but the higher tier gives faster turnaround.

**3. Phase 1 can be posted now** if you want AG to start preparing.
Phase 2 should not be posted until Codex's build has actually
merged to master / main and the testing branch exists in all three
repos.

**4. If AG has not worked with this codebase recently**, consider
adding a short orientation note to Phase 1 pointing at the most
recent COORDINATION.md activity log and the README files for the
three repos. AG's last recorded activity in the coord state was
2026-03-11; six weeks of work may have changed the landscape.

**5. Plan to post both messages via COORDINATION.md** AND the coord
server message system if it is still running. The coord server is
faster but the COORDINATION.md post is durable across sandbox
sessions. Lesson 1 from `CW_COORDINATION_NOTES.md` says cross-AI
coordination must not rely on the server alone.

**6. The adversarial-separation contract is the point**: if AG and
Codex converge on the same verdicts on Probes 1, 2, 5, the layer
ships. If they discord, the layer does not ship and the build is
re-opened. There is no "compromise" verdict — discordance is the
red flag, not the value of either verdict in isolation.

---

*End of AG kick-off prompt.*
