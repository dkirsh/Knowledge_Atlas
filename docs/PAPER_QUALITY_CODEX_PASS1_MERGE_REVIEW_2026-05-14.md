# Codex Prompt — Walk DK Through Pass 1 Merge Review

**Document**: `PAPER_QUALITY_CODEX_PASS1_MERGE_REVIEW_2026-05-14.md`
**Purpose**: a Codex prompt that walks DK through the four
rubric checks for the Pass 1 atlas_shared foundations merge,
pauses for DK approval at decision points, and executes the merge
with DK's explicit go-signal.
**Authorising reviewer**: DK, 2026-05-14.
**Companion**: the rubric itself is documented in CW's chat answer
to DK on 2026-05-14; Codex follows it verbatim.

---

## How to use

Paste the content between `===BEGIN===` and `===END===` into
Codex CLI as your message. Codex runs Checks 1-3 autonomously,
presents Check 4 as questions for DK, then either executes the
merge or stops pending DK's responses.

---

## ===BEGIN===

Codex — DK wants help reviewing and merging your Pass 1
atlas_shared foundations work. You completed Pass 1 on branch
`codex/paper-quality-foundations-2026-05-13` and reported it in
COORDINATION.md under `### Codex paper-quality Pass 1 — landed`.

Your job in this prompt is to *walk DK through the merge review*,
not to merge autonomously. Run the mechanical checks (Checks 1-3),
present findings to DK with clear PASS / FAIL / NEEDS-DK verdicts,
present Check 4 (methodological judgement) as a small set of
questions DK answers, then execute the merge only on DK's explicit
"merge" instruction.

The review rubric is the one CW wrote in chat on 2026-05-14. Four
checks, in order:

### Check 1 — Tests pass

This was already verified by DK: `pytest -q` reported `47 passed
in 0.18s` on `codex/paper-quality-foundations-2026-05-13`. Confirm
by re-running and showing the count:

```bash
cd /Users/davidusa/REPOS/atlas_shared
git checkout codex/paper-quality-foundations-2026-05-13
pytest -q 2>&1 | tail -3
```

Report the result inline. If 47 passes, mark Check 1 ✓ PASS. If
fewer pass or any fail, mark Check 1 ✗ FAIL and stop — do not
proceed to Check 2.

### Check 2 — Four expected commits

The four-commit sequence per the next-block prompt:

- `8ec7ea2` Add paper-quality fingerprint and worker loop (C1)
- `080e763` Document paper-quality fingerprint contract (C2)
- `922f823` Add claim-strength aggregation (C3)
- `5317ff7` Add literature-body quality aggregation (C4)

Verify presence and order:

```bash
git log --oneline main..HEAD
```

For each commit, show its `--stat` output so DK can see what files
landed in each:

```bash
git show --stat 8ec7ea2
git show --stat 080e763
git show --stat 922f823
git show --stat 5317ff7
```

What DK wants to see per commit:

- C1: new files `src/atlas_shared/paper_quality.py`,
  `src/atlas_shared/worker_loop.py`, plus an update to
  `src/atlas_shared/__init__.py` exporting them. Tests in
  `tests/`.
- C2: new file
  `contracts/PAPER_QUALITY_FINGERPRINT_CONTRACT_2026-04-23.md`
  plus update to `AGENTS.md`.
- C3: new file `src/atlas_shared/claim_strengths.py` plus tests
  covering weighting, I², Egger test, sample-overlap dedup.
- C4: new file `src/atlas_shared/literature_body.py` plus
  companion contract `contracts/LITERATURE_BODY_QUALITY_CONTRACT_2026-04-23.md`
  plus tests.

If everything matches, mark Check 2 ✓ PASS. If a deliverable is
missing or substituted, mark Check 2 ⚠ NEEDS-DK with a one-line
explanation of what is different, and continue to Check 3.

### Check 3 — AG advisory constraints

Five constraints per the next-block prompt §1.6. Verify each
empirically; do not just cite your earlier COORDINATION entry's
self-report.

**3a. paper_id normalisation (raw PDF-NNNN).**

```bash
grep -n "bel_" src/atlas_shared/paper_quality.py
grep -n "paper_id" src/atlas_shared/paper_quality.py | head -10
```

You want to see a normalisation function or property that strips
`bel_` prefix. Show DK the grep output and identify the
normalisation logic.

**3b. attached_via_short_circuit field.**

```bash
grep -n "attached_via_short_circuit" src/atlas_shared/paper_quality.py
```

Expect: a field `attached_via_short_circuit: bool = False` on
`PaperQualityFingerprint`.

**3c. No shadow definitions of PaperQualityFingerprint.**

```bash
# In atlas_shared (expect exactly 1 match — the canonical class)
grep -rn "class PaperQualityFingerprint" src/atlas_shared/

# In Knowledge_Atlas (expect 0 matches)
grep -rn "class PaperQualityFingerprint" /Users/davidusa/REPOS/Knowledge_Atlas/

# In Article_Eater (expect 0 matches)
grep -rn "class PaperQualityFingerprint" /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1_recovery/
```

One match in atlas_shared, zero elsewhere. Any other count is a
shadow-definition violation per Hard Rule 8 + AG's advisory.

**3d. Egger test gated at ≥10 studies.**

```bash
grep -n -A 3 "egger" src/atlas_shared/claim_strengths.py | head -30
```

Look for a gate like `if len(studies) < 10: egger_test_applicable
= False`. Show the relevant block to DK.

**3e. No on-disk artefact persistence.**

```bash
grep -n "open(" src/atlas_shared/paper_quality.py \
                src/atlas_shared/claim_strengths.py \
                src/atlas_shared/literature_body.py \
                src/atlas_shared/worker_loop.py
grep -n "to_disk\|write_to\|persist\|json\.dump" \
        src/atlas_shared/paper_quality.py \
        src/atlas_shared/claim_strengths.py \
        src/atlas_shared/literature_body.py
```

Pass 1 should not write fingerprints to disk under
`data/papers/<paper_id>/`. The worker_loop module can have I/O for
the mirror file and git operations, which is allowed; the
fingerprint dataclasses and aggregators should be pure.

Mark Check 3 ✓ PASS if all five sub-checks pass. Mark ⚠ NEEDS-DK
if any sub-check produces an unexpected result; show DK exactly
what was unexpected.

### Check 4 — Methodological choices

These are the choices you made in Pass 1 that DK should sanity-
check. Present each as a question, with the choice clearly stated
and a default if DK does not respond.

**4a. Weighting function**: You chose inverse-variance weights
when CIs are present, otherwise equal weights. Weighting function
version is `v1.0-2026-05-13`.

Question for DK: *Accept inverse-variance + equal-weight fallback
for v1, or switch to Hartung-Knapp-Sidik-Jonkman for the random-
effects case before merging?*

Default if DK does not answer: accept inverse-variance for v1;
file a TASKS entry to revisit at v2.

**4b. Sample-overlap merge threshold**: You merge papers connected
by overlap edges with confidence > 0.50.

Question for DK: *Accept 0.50 as the threshold, or change to 0.75
(merge only on high-confidence overlap) or 0.30 (merge more
aggressively)?*

Default if DK does not answer: accept 0.50 for v1.

**4c. Egger test threshold**: You gate at ≥10 studies per Sterne
2011.

Question for DK: *Accept 10 as the threshold, or use a different
floor?*

Default if DK does not answer: accept 10 as the threshold (the
standard recommendation).

**4d. Literature-body design weighting**: You weight median sample
size by design type (meta-analyses count more than primaries).

Question for DK: *Accept this design-weighted approach (matches
DK's Q1 decision on 2026-04-25), or revisit the tier multipliers?*

Default if DK does not answer: accept (matches the prior decision).

Present these four questions to DK in a clear bulleted list, with
each question's default answer noted. Wait for DK's responses.
If DK says "accept defaults" or "merge", proceed with all four
defaults. If DK answers any question with a different choice,
note the choice and stop — the changed choice requires an
amendment commit before merge.

### After Checks 1-4

Synthesise the four checks into a single PASS / MERGE-READY / NEEDS-
DK-CHANGE verdict. Present it to DK clearly.

If MERGE-READY (Check 1 ✓, Check 2 ✓, Check 3 ✓, Check 4
accepted-defaults or DK explicit "merge"), execute the merge:

```bash
cd /Users/davidusa/REPOS/atlas_shared
git checkout main
git merge --ff-only codex/paper-quality-foundations-2026-05-13
git push origin main
```

After the merge:

1. Confirm the merge landed on main and was pushed.
2. Post to COORDINATION.md under `### Codex paper-quality Pass 1
   — merged to main`:

   ```
   Pass 1 atlas_shared foundations merged to main and pushed.
   Four-commit sequence: 8ec7ea2, 080e763, 922f823, 5317ff7.
   Tests: 47 passed.
   Check 4 design choices accepted as defaults (or with DK
   amendments: <list>).
   Pass 3 (HTTP endpoints + UI + overseer rollup) is now unblocked.
   ```

3. Tell DK the merge is complete and the Pass 3 prompt at
   `Knowledge_Atlas/docs/PAPER_QUALITY_CODEX_PASS3_PROMPT_2026-05-14.md`
   is now ready to be handed to you (Codex) as the next work
   block.

If NEEDS-DK-CHANGE, do not merge. Post the specific change
requests to COORDINATION.md and stop until DK directs.

### Constraints on this prompt

- **No merging without DK's explicit "merge" instruction.** DK is
  the arbitrator. Even if all four checks pass, do not auto-merge.
  Present the verdict and wait.
- **No fixes on the branch during this review.** If Check 2 or 3
  surfaces a problem, present it to DK rather than silently fixing
  it. The review is the gate; fixes happen as a separate cycle.
- **No new contracts, no new docs, no new tests.** This is review
  work. Code changes only happen if DK directs a fix.
- **Honest about uncertainty.** If a check's result is ambiguous
  (e.g., the paper_id normalisation is present but only partial),
  mark ⚠ NEEDS-DK and let DK decide rather than forcing a binary
  PASS/FAIL call.

### Timeline

Roughly 15-30 minutes of Codex work. Checks 1-3 are fast (each is
a small sequence of grep + git commands). Check 4 is the wait-for-
DK part; budget depends on DK's response speed.

If Check 4 takes more than an hour of DK silence, stop and
remind DK that Pass 3 is blocked on this merge. Do not auto-merge
on a timeout.

## ===END===

---

## Notes for DK before pasting

A few items.

**1. You should be at your terminal** when you paste this prompt
because Codex will pause for your answers on Check 4. The pause
is brief (four questions, defaults provided), but it is
interactive.

**2. The defaults for Check 4 are all "accept as-is for v1"**.
If you trust Codex's choices and want to move fast, you can
answer "accept defaults, merge" and Codex will execute the merge
in roughly 30 seconds.

**3. If you want to change a Check 4 choice**, name the change
explicitly. For example: "merge with 4b changed to 0.75 threshold"
or "merge with all defaults except change 4a to Hartung-Knapp-
Sidik-Jonkman". Codex will then either land a small amendment
commit on the foundations branch and re-run Check 1 before merge,
or stop and produce a separate prompt for the amendment if it is
substantial.

**4. After Codex confirms the merge**, post the Pass 3 prompt at
`Knowledge_Atlas/docs/PAPER_QUALITY_CODEX_PASS3_PROMPT_2026-05-14.md`
to Codex as the next message. Pass 3 will execute against the now-
merged Pass 1 types.

---

*End of Pass 1 merge review prompt.*
