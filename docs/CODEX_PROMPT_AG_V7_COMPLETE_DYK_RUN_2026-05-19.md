# Prompt For AG: V7-Complete DYK Batch Run

Date: 2026-05-19

You are AG, running the offline V7-complete pipeline over the selected KA corpus.
Codex has now added the DYK production machinery in `Knowledge_Atlas`:

- `ka_llm_dispatch.py`
- `ka_dyk_writer.py`
- `scripts/run_v7_complete_with_dyk.py`
- `scripts/verify_dyk_llm_authoring_contract.py` provenance extension
- `tests/test_v7_complete_dyk_run.py`
- `docs/AG_DYK_V7_PRODUCTION_REQUIREMENTS_2026-05-19.md`

Your job is to run the production pass while honoring every contract below.

## Correction To Your Current Plan

Do not put production DYK cards directly inside
`science_writer_summary.did_you_know_snippets` as the final artifact. The
science-writer summary is an upstream dependency. The DYK card is a separate
downstream production object with its own schema, provenance, retry path,
validator, per-paper file, consolidated payload, and front-end destination.

Acceptable relationship:

```text
V7 extraction
  -> validated science-writer summary
    -> DYK source packet
      -> DYK LLM writer
        -> verifier
          -> data/v7_complete_dyk_cards/PDF-XXXX.json
            -> data/ka_payloads/did_you_know_llm_overrides.json
```

If you also want to store non-production teaser notes inside the science-writer
summary, mark them explicitly as draft/internal. They must not be promoted to
the public DYK payload unless they pass through `ka_dyk_writer.py` and
`scripts/verify_dyk_llm_authoring_contract.py --strict`.

## Non-Negotiable Contracts

1. Public DYK prose must be LLM-authored. Python may select claims, assemble
   packets, validate, retry, persist, and consolidate. Python must not write the
   title, body, expanded summary, measurables, or short science summary.
2. DYK generation runs only after the upstream science-writer summary for that
   paper exists and is usable.
3. The API-credit path is an offline V7-complete exception only. It is not a KA
   browser/runtime precedent.
4. Every card must pass:
   `python3 scripts/verify_dyk_llm_authoring_contract.py --strict <payload>`
5. Existing cards in
   `data/ka_payloads/did_you_know_llm_overrides.json` must be preserved.
6. Failed or malformed cards must remain in per-paper files for inspection and
   must not be silently promoted into the consolidated payload.
7. The default is one DYK card per paper. Generate two or three only when the
   paper has distinct, high-credence findings, is a review with multiple
   separable claims, or is a methodological landmark. Do not inflate card count
   just to improve coverage.
8. The Gemini 2.5 API run is an explicit offline batch exception for this V7
   complete job. Subscription CLI remains the default for V7 and for KA runtime.
   Do not silently switch future jobs to API mode.

## Preflight

Run from `/Users/davidusa/REPOS/Knowledge_Atlas`:

```bash
pytest -q tests/test_v7_complete_dyk_run.py tests/test_dyk_llm_authoring_contract.py
python3 scripts/verify_dyk_llm_authoring_contract.py --strict
python3 scripts/verify_subscription_ai_only_contract.py --strict
```

Expected:

- the new DYK batch test passes;
- the existing 50-card payload validates;
- KA runtime subscription-only verification remains green.

## Corpus List

Use a reviewed paper-id file such as:

```text
data/v7_complete_run_2026-05-19/paper_ids.txt
```

Do not run against all corpus papers unless DK has approved the exact list. The
runner is idempotent by per-paper file, so it can resume a partially completed
run.

## Run Command

If DK confirms the API-credit exception for this offline run with Gemini 2.5:

```bash
LLM_INVOCATION_MODE=api \
LLM_PROVIDER=google \
LLM_MODEL=gemini-2.5-pro \
GOOGLE_API_KEY="$GOOGLE_API_KEY" \
python3 scripts/run_v7_complete_with_dyk.py \
  --corpus-list data/v7_complete_run_2026-05-19/paper_ids.txt \
  --batch-size 50 \
  --concurrency 10 \
  --cost-ceiling-usd 250 \
  --mode api \
  --provider google \
  --model gemini-2.5-pro \
  --max-cards-per-paper 3 \
  --output-dir data/v7_complete_dyk_cards \
  --consolidate-into data/ka_payloads/did_you_know_llm_overrides.json
```

Use the exact Gemini 2.5 model identifier available in AG's API environment if
it differs from `gemini-2.5-pro`; record that exact string in
`llm_authoring.model`.

If DK does not confirm the exception, use subscription CLI mode:

```bash
LLM_INVOCATION_MODE=subscription_cli \
KA_DYK_LLM_COMMAND="claude -p" \
python3 scripts/run_v7_complete_with_dyk.py \
  --corpus-list data/v7_complete_run_2026-05-19/paper_ids.txt \
  --batch-size 25 \
  --concurrency 2 \
  --cost-ceiling-usd 0 \
  --mode subscription_cli \
  --provider subscription \
  --max-cards-per-paper 3 \
  --output-dir data/v7_complete_dyk_cards \
  --consolidate-into data/ka_payloads/did_you_know_llm_overrides.json
```

Do not write provider credentials to a config file or repository file. Read the
API key only from the process environment.

## Success Conditions

The run is successful only when:

1. At least 95% of selected papers have at least one valid DYK card.
2. The consolidated payload passes strict verification.
3. The run stays under the approved cost ceiling.
4. The generated cards include LLM provenance:
   `invocation_mode`, `invocation_provider`, `invocation_timestamp`,
   `tokens_in`, `tokens_out`, and `cost_estimate_usd`.
5. DK spot-reviews a random sample of at least 20 cards across topic clusters.
6. The run report states how many papers produced one card, two cards, and
   three cards, and gives examples of why any paper received more than one.
7. Any database provenance logging in `v7_gold_extraction_registry.db` must
   record the DYK stage as downstream of a passed science-writer summary, not as
   an undifferentiated field inside the summary stage.

## Failure Handling

- Missing science summary: skip the paper, record `dyk_skipped_no_science_summary`.
- Malformed JSON: retry once. If still malformed, mark generation failed.
- Word-count or contract failure: retry once with validation feedback. If still
  invalid, mark generation failed.
- Cost ceiling exceeded: abort cleanly. Do not consolidate partial failed
  batches without DK approval.
- API outage: pause and retry. Do not switch providers or modes without logging
  the change.
- Contract bypass attempt: stop the run. Do not accept Python-authored fallback
  prose, draft snippets, missing provenance, or cards that pass only because a
  verifier was weakened.

## Final Verification

After the run:

```bash
python3 scripts/verify_dyk_llm_authoring_contract.py --strict data/ka_payloads/did_you_know_llm_overrides.json
pytest -q tests/test_v7_complete_dyk_run.py tests/test_dyk_llm_authoring_contract.py
git status --short
```

Report:

- number of papers attempted;
- number skipped and why;
- number of valid cards written;
- total estimated API cost;
- one/two/three-card distribution;
- strict verifier result;
- path to the consolidated payload;
- whether DK's spot-review sample has been prepared.
