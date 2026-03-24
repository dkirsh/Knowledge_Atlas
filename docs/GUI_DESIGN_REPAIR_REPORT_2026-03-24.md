# GUI Design Repair Report

Date: 2026-03-24
Repo: `/Users/davidusa/REPOS/Knowledge_Atlas`

## Checker status

Command run:

```bash
python3 /Users/davidusa/REPOS/Knowledge_Atlas/scripts/check_gui_design_contract.py
```

Current result:
- required failures: `0`
- warning failures: `10`

## Interpretation

The contract floor is now met across the scanned HTML pages.
The remaining warnings are not structural breakages.
They are content / UX-documentation improvements, mostly around making page purpose more explicit on some pages.

## Current warning classes

### Missing explicit page-purpose marker
Pages flagged:
- `Designing_Experiments/bn_navigator.html`
- `Designing_Experiments/en_navigator.html`
- `Designing_Experiments/knowledge_navigator.html`
- `Designing_Experiments/methods_taxonomy.html`
- `ka_article_propose.html`
- `ka_demo.html`
- `ka_question_maker.html`
- `ka_register.html`
- `ka_tag_assignment.html`

Recommended repair:
- add a brief visible page-purpose or workflow cue near the top of the page

### Sparse evidence/source language on login page
Page flagged:
- `ka_login.html`

Recommended repair:
- likely no action needed unless the page evolves into a more explanatory entry surface
- this warning is low-value for a pure auth page

## Repairs completed in this pass

Three pages were repaired to add explicit primary heading structure:
- `ka_article_propose.html`
- `ka_dashboard.html`
- `ka_evidence.html`

These fixes were deliberate because they were true structural misses, not checker noise.
