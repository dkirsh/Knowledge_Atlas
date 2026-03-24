# GUI Design Process And Repairs

Date: 2026-03-24
Repo: `/Users/davidusa/REPOS/Knowledge_Atlas`

## Purpose

Define how the GUI design agent should be used in practice.

## Standard flow

1. Define the page or flow.
2. Gather page purpose, persona, and data contract.
3. Run the GUI design agent spec.
4. Choose framework with explicit rationale.
5. Implement the page.
6. Run the local contract checker.
7. Repair failures or warnings that matter.
8. Review with a human before broad rollout.

## Required inputs

At minimum:
- page purpose
- primary persona(s)
- expected data sources
- likely next page / handoff
- whether the page is public, teaching-facing, or research-facing

Preferred:
- benchmark journey
- example pages
- aesthetic references
- science-copy pack

## Framework decision rules

Choose Streamlit when:
- the page is tool-like
- the surface is evidence-heavy
- rapid iteration matters
- stateful filtering / compare workflows dominate

Choose static HTML when:
- the page is mostly informational
- the experience is lightweight and public-facing
- deployment simplicity matters more than app machinery

Choose a richer framework only when:
- routing/state complexity clearly exceeds Streamlit
- or collaborative / app-shell behavior requires it
- and the team can maintain it

## Required review questions

1. Is the first action obvious?
2. Is the page type obvious?
3. Where is provenance visible?
4. Where is uncertainty visible?
5. What survives the next handoff?
6. Is the framework choice justified?
7. Is the page expressive enough to guide attention?
8. Is it still accessible and usable?

## Local checker

Run:

```bash
python3 /Users/davidusa/REPOS/Knowledge_Atlas/scripts/check_gui_design_contract.py
```

This checker is intentionally limited.
It catches structural omissions, not product wisdom.
Use it as a floor, not as a substitute for review.

## Repair categories

### Orientation failure
Symptoms:
- unclear page purpose
- no obvious first action

Repairs:
- strengthen hero/page header
- add explicit first-step cue
- reduce competing CTAs

### Provenance failure
Symptoms:
- evidence or source path buried

Repairs:
- add provenance drawer / source links / evidence affordance
- make source lineage one click away

### Uncertainty failure
Symptoms:
- claims read as absolute

Repairs:
- add confidence / caveat / evidence-strength treatment
- distinguish direct evidence from synthesis

### Framework-choice failure
Symptoms:
- page fights the chosen framework

Repairs:
- simplify into Streamlit if custom plumbing is not paying off
- move beyond Streamlit only when necessary and justified

### Visual-language failure
Symptoms:
- generic app chrome
- weak hierarchy
- decorative clutter

Repairs:
- reassert palette, typography, spacing, and emphasis hierarchy
- remove novelty that does not improve comprehension

### Responsiveness/accessibility failure
Symptoms:
- crowded layouts
- poor touch targets
- low contrast

Repairs:
- add breakpoints
- increase target sizes and spacing
- strengthen contrast and alignment

## Completion rule

A page is not complete because it looks good.
A page is complete when:
- the design spec exists
- the framework decision is justified
- the contract checker passes or warnings are understood
- provenance/uncertainty behavior is explicit where relevant
- human review finds the page usable for its intended persona
