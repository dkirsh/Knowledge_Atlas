# AG — DYK Production Requirements for V7-Complete Run

*David Kirsh, 2026-05-19. Authoritative spec for AG's 800-paper V7-complete pipeline pass. Companion to `DID_YOU_KNOW_LLM_AUTHORING_CONTRACT_2026-05-18.md` (the style contract) and `CODEX_CLAUDE_UPDATE_SUBSCRIPTION_DYK_V7_SUBSTITUTION_2026-05-18.md` (the subscription-AI contract update Codex landed on 2026-05-18). Read those two first; this document specifies the *production* requirements that sit on top of them.*

---

## Authorisation flag — read first

DK has indicated that the 800-paper V7-complete run may use **Gemini 2.5 API credits** for the LLM calls. This is a deliberate exception to the durable subscription-only rule (`feedback_subscription_only_no_apis.md` in CW auto-memory). The exception is:

- Scope: this run, the 800-paper V7-complete pass.
- Reason: throughput. Subscription-CLI pacing is too slow for the corpus size.
- Bounds: API mode authorised for this offline V7-complete prose/DYK generation job only. Subscription-CLI remains the default for V7 and for KA runtime AI calls (`ka_critique_endpoints.py`, `ka_search_synthesis.py`, the future Built-Environment-IAT validator, and anything else served from a browser). DK confirmation strongly recommended before AG starts the run.

The spec below supports both modes. The default in code stays subscription-CLI; the V7-complete run sets `--mode=api` explicitly via env var or CLI flag, and the verifier records `llm_authoring.invocation_mode` in the card provenance.

---

## What gets produced

For each of the 800 papers in scope, the V7-complete run produces:

1. **One full V7 belief row** in `ae.db`, with the existing V2 credence schema fields plus the V7-complete additions (10-target VOI packet, structured argumentation scaffold, mechanism-chain trace). This is the existing V7 contract; the spec below does not change it.

2. **One science-writer summary** (750–1,250 words per the existing science-summary spec in `prompts/SCIENCE_WRITER_TIGHTENED_V2.md`), persisted to `pipeline_lifecycle_full.db` `science_writer_results` table.

3. **One to three DYK cards** (depending on the paper's number of source claims and topic salience), persisted as a per-paper file at `data/v7_complete_dyk_cards/PDF-XXXX.json` and rolled up into `data/ka_payloads/did_you_know_llm_overrides.json` at the end of the run.

The *new* deliverable, and the focus of this spec, is item 3 — the DYK cards.

---

## Where DYK generation fits in the pipeline

DYK generation runs as the **final stage** of the per-paper V7-complete pass, after the science-writer summary has been produced and validated. Production DYK cards must not be treated as casual `science_writer_summary.did_you_know_snippets`; they are downstream production objects with their own schema, provenance, verifier, and payload destination. The dependency chain is:

```
V7-Lite (synchronous, partial)
   → V7-complete async worker (ka_v7_async_worker.py)
         → science-writer summary (LLM call #1)
              → DYK card generation (LLM call #2)
                   → validate + persist
```

The reason for this ordering: the DYK card's `short_science_summary` field draws on (and may include modified excerpts from) the science-writer summary, and the card's `body` and `expanded_summary` need the same source-backed brief that the science writer received. Producing the science summary first means the DYK pass has all the material it needs, and the two stages share the same source packet.

A failed science-writer call MUST abort the DYK stage for that paper; DYK cards are never generated without a passing science summary upstream.

---

## Card schema (frozen from existing contract)

Every production card is a JSON object with these required fields, exactly as the existing 50 cards in `did_you_know_llm_overrides.json` have:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `dyk_` + 10-char hex, generated from `paper_id` + `source_claim_ids[0]` |
| `paper_id` | string | `PDF-XXXX` |
| `source_claim_ids` | list[string] | Non-empty; at least one evidence-row id from `evidence.json` for this paper |
| `title` | string | One sentence stating an intelligible claim, not a label. ≤ 100 chars |
| `body` | string | 3–4 sentences. First sentence identifies the phenomenon in ordinary language. Subsequent sentences say what changes, under what condition, why it matters. 50–110 words |
| `expanded_summary` | string | Continues the explanation; does not repeat the body. < 82% word overlap with `body` (verifier-enforced). 80–160 words |
| `measurables` | string | One paragraph stating how the phenomenon was measured: instruments, sample, key parameters. 30–80 words |
| `short_science_summary` | string | Longer summary, may draw on the science-writer summary. 250–450 words |
| `writing_agent` | string | `llm_science_writer` |
| `authoring_mode` | string | `llm_authored` |
| `writing_contract` | string | `DID_YOU_KNOW_SCIENCE_WRITING_CONTRACT_2026-05-16` |
| `llm_authoring` | object | See below |
| `science_summary_dependency` | string | Reference to the science-writer summary row that informed this card |
| `longer_summary_link` | string | `ka_article_view.html?id=PDF-XXXX` |
| `source_link` | string | `ka_article_view.html?id=PDF-XXXX` |
| `apa_citation` | string | Full APA citation of the paper |

The `llm_authoring` object:

```json
{
  "model": "claude-3-5-sonnet-20241022",       // or whatever was used
  "prompt_contract": "DID_YOU_KNOW_SCIENCE_WRITING_CONTRACT_2026-05-16",
  "quality_gate": "passed",
  "source_claim_ids": ["252", ...],            // duplicate of top-level for verifier
  "invocation_mode": "api",                     // NEW for this run: "api" | "subscription_cli"
  "invocation_provider": "anthropic",          // NEW: "anthropic" | "openai" | "google" | "subscription"
  "invocation_timestamp": "2026-05-19T14:23:01Z",
  "tokens_in": 4231,                            // NEW
  "tokens_out": 1247,                           // NEW
  "cost_estimate_usd": 0.0291                  // NEW; estimated, for budget tracking
}
```

The four `NEW` fields are additions to the existing schema. Codex needs to update `scripts/verify_dyk_llm_authoring_contract.py` to accept them (as optional, so the existing 50 cards remain valid). I would recommend that addition be made *before* the AG run starts, not retrofitted afterwards.

---

## Per-card prompt template

The LLM call for each card receives a structured prompt assembled by Python from these inputs:

```
SYSTEM:
You are a science writer for the Knowledge Atlas, writing public-facing
"Did You Know" cards about peer-reviewed research on the built environment
and human experience. Your audience is undergraduate Cognitive Science
students and curious practitioners — informed but not specialised.

You will receive a source-backed brief on one specific claim from one paper.
Produce a single DYK card in the JSON schema specified below. The fields
title, body, expanded_summary, measurables, and short_science_summary are
required and must satisfy the quality rules at the end of this prompt.

USER:
=== Paper metadata ===
paper_id: PDF-XXXX
title: <paper title>
authors: <authors>
year: <year>
doi: <doi>
venue: <venue>
apa_citation: <full APA>

=== Source claim ===
claim_id: <claim id from evidence.json>
claim_text: <the finding>
warrant_class: <empirical_association | mechanism | review | ...>
credence: <numeric credence>

=== Existing science summary (if available) ===
<the science-writer summary for this paper, full text>

=== Source-backed brief ===
<a 300-500 word brief assembled from article_details.json, evidence.json,
methods, measures, sample, uncertainty notes, figure captions; everything
the writer needs in order to produce all five prose fields without
hallucinating>

=== Methods and measures ===
<inventory of instruments and constructs measured>

=== Sample ===
<sample size, population, setting>

=== Topic tags ===
<the topic_ontology nodes this card sits under>

=== Quality rules (must all hold) ===
1. title states an intelligible claim, not a label.
2. body's first sentence identifies the phenomenon in ordinary language.
3. body explains what changes, under what condition, why it matters.
4. expanded_summary continues the explanation; does not repeat the body
   (< 82% large-word overlap).
5. measurables describes how the phenomenon is measured.
6. NO authorial instructions in any public field ("this card should",
   "the DYK should", "users should", etc.). The verifier rejects these.
7. NO Python-template phrasing or fallback markers.
8. Stay within the word-count bands per field (see schema above).

Return ONLY a JSON object with the five prose fields and source_claim_ids.
Python will merge metadata, generate the id, validate, and persist.
```

The prompt template is the same regardless of invocation mode (API or subscription-CLI). The wrapper code in `ka_subscription_llm.py` should be extended (or duplicated as `ka_llm_dispatch.py`) to dispatch on mode.

---

## How many cards per paper

Default rule: produce **one card per paper**, drawn from the highest-credence claim that has not already been used in an earlier card.

Exceptions to make 2–3 cards:

- The paper has multiple distinct findings, each at credence ≥ 0.70, with non-overlapping construct pairs. Up to 3 cards.
- The paper is a review (`warrant_class` includes `review`) and has at least 3 distinct claims at credence ≥ 0.65. Up to 3 cards.
- The paper is a methodological landmark (e.g. Ulrich 1984, de Dear & Brager 1998). Mark as `landmark: true` in source-claim selection; up to 3 cards.

The Python selector — already permitted under the existing contract — implements these rules. The LLM is called once per selected claim, not once per paper. The selector must not inflate card count merely to increase volume; two- and three-card papers require a recorded reason: `multi_finding_high_credence`, `review_multi_claim`, or `methodological_landmark`.

For an 800-paper corpus, the expected card volume is roughly **900–1,200 cards** under these rules.

---

## API vs subscription invocation modes

The wrapper accepts a `--mode` flag and an `LLM_INVOCATION_MODE` environment variable, with `--mode` taking precedence. Values:

- `api` (this run's authorised exception). Routes through the chosen provider's API. The script must read the API key from an environment variable (never the browser, never a config file checked into the repo) and must respect the provider's rate limits.
- `subscription_cli` (default; KA runtime mode). Routes through `claude -p`, `codex exec`, or `gemini-subscription-cli` per the subscription-AI contract.

Provider choice within API mode is set by `LLM_PROVIDER` env var: `google` for DK's Gemini 2.5 credit run, with `anthropic` and `openai` available only if DK explicitly redirects the run. The same prompt template works for all three.

Multi-provider independence (the AG Hard Rule 8 from `prompts/AG_SUBSTITUTION_GRAPH_EXTRACTION_2026-05-18.md`) does NOT apply to DYK production. DYK cards are intended to be authored by one writer per card; multi-LLM cross-checking is reserved for the substitution-graph extraction where disagreement is itself signal.

---

## Batch behaviour, rate limits, and retry

The 800-paper run requires throughput discipline:

- **Batch size**: 50 papers per checkpoint. After each batch, persist the per-paper card files, run the validator, log the batch summary.
- **Concurrency**: up to 10 concurrent API calls (Anthropic's default tier supports this; reduce to 5 for OpenAI tier-1).
- **Rate limit handling**: on 429 response, exponential backoff starting 30 s, max 5 retries. After 5 failed retries on the same paper, mark the paper as `dyk_generation_failed` and continue. Halt the entire run if more than 5% of papers in a batch fail this way.
- **Cost ceiling**: a per-run cap of $250 USD (estimated; assumes Sonnet at ~$3/M input, $15/M output, ~5K input + 1.5K output tokens per card, ~1,000 cards). Set `--cost-ceiling-usd 250`; the wrapper aborts the run if cumulative estimated cost crosses the ceiling.
- **Idempotency**: the per-paper file is the unit of resumability. On restart, the script skips papers whose `data/v7_complete_dyk_cards/PDF-XXXX.json` already exists and validates. Re-running with `--regenerate=stale` regenerates cards whose science-summary upstream has been updated since the card was authored (timestamp comparison).

---

## Validation gates

Every batch of 50 papers passes through two validation gates before the next batch starts:

1. **Schema gate**: every card matches the schema above. Missing fields, wrong types, or word-count violations fail.
2. **Contract gate**: `python3 scripts/verify_dyk_llm_authoring_contract.py --strict <batch_consolidated.json>` exits 0.

A batch that fails either gate is **not rolled up** into `data/ka_payloads/did_you_know_llm_overrides.json`. The failed cards remain in the per-paper files for human review; the run continues with the next batch, but the consolidated payload is not updated until the failed batch is repaired.

At the end of the full run, a final consolidation step:

1. Loads the existing 50 cards from `did_you_know_llm_overrides.json` (preserve them — they are CW's repaired set, do not regenerate).
2. Loads all per-paper card files from `data/v7_complete_dyk_cards/`.
3. Concatenates, deduplicates by `id`, sorts by `paper_id`.
4. Writes the consolidated file with an updated `generation_note` recording the date, run id, total card count, and the V7-complete run id.
5. Runs the contract validator one final time against the consolidated file.
6. Updates `data/ka_payloads/did_you_know_index.json` (the index used by the DYK browser surface).

---

## Failure modes the script must handle

- **Upstream science-summary missing**: skip the paper, log `dyk_skipped_no_science_summary`.
- **Upstream science-summary present but malformed**: skip, log `dyk_skipped_malformed_science_summary`. Do NOT attempt to repair from Python.
- **LLM returns malformed JSON**: retry once with the same prompt; if still malformed, mark the paper `dyk_generation_failed_json` and continue.
- **LLM returns forbidden phrasing** (caught by the contract verifier): retry once with an appended note in the prompt naming the violation; if still failing, mark `dyk_generation_failed_contract` and continue.
- **Word-count out of band**: retry once with explicit instruction to expand or compress the offending field; if still out, mark `dyk_generation_failed_wordcount`.
- **Cost ceiling hit mid-run**: abort cleanly. The per-paper files for completed papers remain; the consolidated payload is not updated until DK approves continuation.
- **API outage**: pause, retry after 5 minutes, escalate to subscription_cli mode if outage persists > 30 minutes (set `LLM_FALLBACK_MODE=subscription_cli` in env to enable).

---

## Run command

The expected invocation, run from the `Article_Eater_PostQuinean_v1_recovery/` working tree by AG:

```bash
GOOGLE_API_KEY="$(cat ~/.keys/google_ag)" \
LLM_INVOCATION_MODE=api \
LLM_PROVIDER=google \
LLM_MODEL=gemini-2.5-pro \
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
  --consolidate-into ../Knowledge_Atlas/data/ka_payloads/did_you_know_llm_overrides.json \
  --log-file logs/v7_complete_run_2026-05-19.jsonl
```

The script `scripts/run_v7_complete_with_dyk.py` does not exist yet; Codex is to build it from the existing `ka_v7_async_worker.py` plus a new DYK module `ka_dyk_writer.py`. The build is item 1 of the immediate Codex queue below.

---

## What Codex must build before AG starts

Six items, in order:

1. `ka_dyk_writer.py` — the LLM-dispatch module for DYK card generation. Accepts the source-backed brief, returns the validated card object, raises on contract violation.
2. `ka_llm_dispatch.py` — extend `ka_subscription_llm.py` to handle both `api` and `subscription_cli` modes, with provider selection. Cost-estimation per call.
3. `scripts/run_v7_complete_with_dyk.py` — the orchestrator: batch loop, concurrency, retry, idempotency, consolidation.
4. Extend `scripts/verify_dyk_llm_authoring_contract.py` to accept the four new `llm_authoring` fields (`invocation_mode`, `invocation_provider`, `invocation_timestamp`, `tokens_in`, `tokens_out`, `cost_estimate_usd`).
5. `tests/test_v7_complete_dyk_run.py` — end-to-end test with 3 mock papers; exercises the success path, malformed JSON retry, word-count retry, cost ceiling abort.
6. `data/v7_complete_run_2026-05-19/paper_ids.txt` — the explicit list of 800 paper ids in scope, generated by a Python selector from the corpus, reviewed by DK before the run starts.

Estimated build time: 4–6 days for Codex. AG's run starts after item 6 lands and DK signs off.

---

## What AG owns versus what Codex owns

| Stage | Owner |
|-------|-------|
| Build the orchestrator and writer modules | Codex |
| Build the verifier extensions | Codex |
| Build the test suite | Codex |
| Select the 800 paper ids | Codex (selector) + DK (sign-off) |
| Run the 800-paper pass | AG |
| Monitor for rate-limit and quality issues | AG |
| Repair contract-failed batches | AG (re-run) or CW (manual repair, as for the existing 50) |
| Final consolidation and payload update | Codex (script does it automatically; CW reviews) |
| Front-end display of the new cards | Track 4 students (existing DYK browser surface) |

---

## Cost model

At Sonnet 2024-10-22 rates ($3.00/M input, $15.00/M output) and the prompt size described above:

- Per-card cost: ~$0.029 (5K input × $3/M + 1.5K output × $15/M = $0.015 + $0.023 = $0.038, slightly lower in practice due to caching)
- 1,000 cards: ~$29-$40 actual
- Plus the science-writer pass (already specified, ~$0.07/paper at 800 papers = ~$56)
- Plus retries (estimated 10% overhead): ~$10
- **Total expected: $100–$120 USD**
- **Cost ceiling set at $250 USD** for safety margin

This is well below DK's typical research-credit budget. If DK is using OpenAI or Google instead of Anthropic, the per-card cost will vary but the magnitude does not change materially.

---

## Acceptance criteria for the run

The run is accepted when:

1. ≥ 95% of papers in the 800-paper corpus have at least one valid DYK card.
2. The consolidated payload validates `strict` against the contract verifier.
3. The total cost is within the $250 ceiling.
4. The cards cover the full IV × DV space: at least one card per IV root (spatial, luminous, thermal, acoustic, biophilia, material, social-spatial, control, multisensory) per major DV root (cog, affect, physio, neural, behav, health, social).
5. DK has spot-reviewed at least 20 cards randomly sampled across topic clusters and approved them as production-ready.

The acceptance criterion #4 may force AG to re-run a small subset of papers if a topic cluster is under-represented in the first pass. The selector should be tuned to balance coverage from the start.

---

## Open questions for DK

1. Is the $250 USD ceiling correct, or should it be higher to allow re-runs?
2. Provider preference: Anthropic Sonnet is the default in this spec. Confirm or substitute.
3. Should we generate cards for papers that have `dyk_eligible: false` in any future article-level flag, or is the existing source-claim-credence threshold sufficient?
4. After the run, should the front-end DYK browser surface (Surface 2 in the Week-1 wireframe) get a re-render to pick up the new cards immediately, or is that a separate sprint?

---

*End of spec. Updates to TASKS.md to follow under POE-* track if not under a new V7-COMPLETE-* track.*
