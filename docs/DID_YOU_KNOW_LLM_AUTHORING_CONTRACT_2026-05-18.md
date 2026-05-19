# Did You Know LLM Authoring Contract

Date: 2026-05-18

This contract exists to prevent a common failure mode: using Python templates to
write public science prose merely because the task is repetitive. That is not
allowed for production Did You Know cards.

## Non-Negotiable Rule

Production Did You Know card prose MUST be authored by an LLM science-writer
pass or by a human editor. Python may select candidates, assemble source
packets, merge metadata, validate JSON, and run quality gates. Python MUST NOT
write the public-facing title, body, expanded summary, measurables explanation,
or short science summary for production cards.

## Allowed Python Work

Python may do the following:

- select candidate papers and claims;
- collect source-backed briefs from `article_details.json`, `evidence.json`,
  article metadata, figures, measures, and existing science summaries;
- create private evidence packets for the writer;
- check word counts, required fields, links, APA citation strings, and duplicate
  text;
- reject cards that lack provenance or quality markers;
- serialize validated cards into the payload.

## Forbidden Python Work

Python MUST NOT do any of the following for production cards:

- template public prose from fields such as topic, stimulus, response, outcome,
  source, or abstract;
- generate public prose with deterministic sentence patterns;
- fill missing card text by fallback rules;
- publish scaffold prose marked as draft, heuristic, template, fallback, or
  python-generated;
- convert source briefs directly into public card text without an LLM
  science-writer pass.

## Required Provenance

Every production card must carry all of these markers:

- `authoring_mode: "llm_authored"` or `authoring_mode: "human_authored"`;
- `writing_agent: "llm_science_writer"` or `writing_agent: "human_editor"`;
- `writing_contract: "DID_YOU_KNOW_SCIENCE_WRITING_CONTRACT_2026-05-16"`;
- for LLM-authored cards, an `llm_authoring` object with:
  - a non-empty `model`;
  - the same `prompt_contract`;
  - `quality_gate: "passed"`;
  - at least one `source_claim_ids` entry.

Cards lacking these markers are drafts. Drafts may be saved for review, but they
must not enter `data/ka_payloads/did_you_know_llm_overrides.json` or any payload
served as production.

## Writer Input

The LLM science writer must receive more material than the final card uses:

- the article title, authors, year, DOI, and KA paper id;
- the relevant source claim ids;
- the existing science summary when available;
- a longer source-backed brief of the finding;
- methods, measures, sample, and uncertainty notes when available;
- figure or illustration references when relevant;
- the intended topic tags.

The writer then produces the title, body, expanded summary, measurables text, and
short science summary. The verifier checks structure and provenance; it does not
substitute its own prose.

## Quality Rules

The public prose must satisfy these rules:

- the title states an intelligible claim, not a label;
- the first sentence identifies the phenomenon in ordinary language;
- the body explains what changes, under what condition, and why it matters;
- the expanded summary continues the explanation and does not repeat the body;
- the measurables text explains how the phenomenon is measured;
- the source is an APA-style citation and links to the KA article page;
- authorial instructions such as "this card should" or "the DYK should" are
  forbidden in public text.

## Mechanical Gate

`scripts/verify_dyk_llm_authoring_contract.py --strict` is the admission gate.
It must fail whenever production prose lacks LLM/human authorship provenance or
contains forbidden draft/template markers. Tests must exercise both acceptance
and rejection.
