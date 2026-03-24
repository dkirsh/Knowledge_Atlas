# Article Finder API Operations

Date: 2026-03-24
Purpose: operational rules for API-backed literature search during the current COGS 160 / KA build period

## Keys and services currently in play

### OpenAlex
- temporary premium/trial key is available
- treat it as expiring on `2026-04-02`
- do not build the student workflow around paid OpenAlex assumptions after that date

### Crossref
- no private key required
- students should use the normal developer/polite-pool workflow with email identification
- reference:
  - [Crossref developer info](https://www.crossref.org/community/developers#:~:text=Trying%20to%20get%20data%20from,up%20with%20one%20of%20those.)

### Semantic Scholar
- key available
- use through local-only config / secrets, never in tracked files

## Operating rule

Use the OpenAlex trial aggressively now for:
1. broad article discovery
2. citation chasing
3. bibliography expansion
4. gap-filling around theory / mechanism / neural-pathway fronts

But do not make long-term KA or course assumptions that require paid OpenAlex access.

## Student guidance

Students should be taught:
1. Crossref is stable and should remain part of the default toolkit
2. OpenAlex is excellent right now but may need to fall back to polite-pool / lower-rate behavior after the trial period
3. Semantic Scholar is useful but should be treated as a complement, not the only discovery source

## Engineering rule

Secrets belong only in:
- local config
- environment variables

Never in:
- tracked YAML defaults
- HTML / JS page code
- docs that will be committed

## Cost / rate guardrails

1. prefer batch runs with explicit limits
2. log usage by source and query family
3. cap large search sweeps unless intentionally approved
4. keep a post-trial fallback mode:
   - Crossref
   - polite-pool OpenAlex
   - Semantic Scholar
   - manual Google AI / Elicit supplementation

## Live smoke findings

1. A constrained AF bibliographer run reached live search providers once executed outside the sandbox.
2. The currently configured OpenAlex premium key was transmitted but returned `401 Unauthorized`.
3. AF still found papers from other providers during the same run, so discovery is not entirely blocked by the OpenAlex failure.
4. The first failed scoring run was caused by invoking AF with the system `python3` instead of the AF repo virtualenv interpreter.
5. Re-running with `/Users/davidusa/REPOS/Article_Finder_v3_2_3/venv/bin/python` successfully loaded `sentence-transformers` on Apple `mps` and executed real scoring.
6. A bounded single-cell rerun (`env.luminous_out.neural.eeg`) completed successfully, found `2` candidate papers, and rejected them after scoring rather than failing structurally.

## Immediate implications

1. validate or replace the OpenAlex key before relying on premium OpenAlex throughput
2. always run AF CLI commands through the repo virtualenv, not bare `python3`
3. treat the OpenAlex failure and the actual bibliographer relevance thresholding as separate issues
