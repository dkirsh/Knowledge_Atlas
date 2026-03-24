# Sprint Status Summary

Date: 2026-03-24
Primary plan source:
- `/Users/davidusa/REPOS/Knowledge_Atlas/docs/GUI_UNIFICATION_AND_REBUILD_SPRINT_PLAN_2026-03-24.md`

## Current position

We are not in a single clean sequential sprint anymore.
We are in:
- Sprint 1 mostly complete at the architecture/spec level
- Sprint 2 in progress through CW
- Sprint 3 partially implemented
- Sprint 6 partially architected early because theory/neural requirements were clarified before live data hookup

## Sprint-by-sprint status

### Sprint 0 — Severe audit and canon definition
Status:
- effectively complete

Completed artifacts:
- `GUI_RUTHLESS_AUDIT_2026-03-24.md`
- `CANONICAL_SITE_FAMILY_MAP_2026-03-24.md`
- `DUPLICATE_PAGE_DISPOSITIONS_2026-03-24.md`

Remaining gap:
- none major at the planning layer

### Sprint 1 — Information architecture unification
Status:
- mostly complete in specs
- partially implemented in live pages

Completed artifacts:
- `UNIFIED_NAV_MODEL_2026-03-24.md`
- `EMBEDDED_DE_PAGE_DISPOSITIONS_2026-03-24.md`
- updated `ka_sitemap.html`
- mode-switch spec and initial implementation

Live implementation already done:
- immediate user-type mode switch on `ka_home.html`
- immediate user-type mode switch on `ka_topics.html`
- contributor/intake pages normalized conceptually into the unified IA

Remaining gap:
- consistent shared nav across more live pages
- actual `Explore the Literature` dropdown implementation

### Sprint 2 — Class site revision
Status:
- in progress

Completed / unblocked:
- track staging branches created and pushed
- `Knowledge_Atlas/master` pushed so students can clone
- branch/sandbox model documented
- student setup and Track 2 assignment updated

Remaining gap:
- CW still needs to finish revising the class-facing site and getting-started flow
- final course/Atlas page boundary still needs one pass

### Sprint 3 — Data contract and adapter layer
Status:
- in progress

Completed:
- `GUI_DATA_CONTRACTS_2026-03-24.md`
- unified intake policy
- AF intake integration contract
- quarantine/validation script
- AF intake adapter script
- citation+PDF unified intake UI on `ka_article_propose.html`

Remaining gap:
- real backend hookup for article intake
- real DB-backed page adapters for topics/evidence/article detail/gaps

### Sprint 4 — Rebuild hardening and theoretical alignment
Status:
- not started as a full sprint

Completed pre-work:
- subject-count debugging
- methods exact/plain split
- theory frame work
- results structuring work
- AF API operations note

Remaining gap:
- full corpus freeze
- full checked rebuild
- SC audit and pass/fail reporting against latest theory commitments

### Sprint 5 — First live data hookup
Status:
- not started as a full sprint

Completed precursor work:
- page-level contracts exist
- target pages identified

Remaining gap:
- real rebuilt content wired into `ka_topics`, `ka_evidence`, article detail, and `ka_gaps`

### Sprint 6 — Theory guides and neural underpinnings
Status:
- architected early, not yet fully surfaced

Completed:
- theory-guide integration plan
- older-theories placement concept
- neural-underpinnings architecture
- initial pathway inventory
- Track 2 pathway assignment sheet

Remaining gap:
- live theory-guide landing page
- live neural-underpinnings landing page
- actual article linking into those layers

### Sprint 7 — Image tagger integration
Status:
- conceptually placed, not yet fully integrated

Completed:
- image tagger recognized as a main contributor workflow in IA

Remaining gap:
- visible integration into the main site flow
- data/status surfaces

### Sprint 8 — Iteration loop to gold
Status:
- not started

Reason:
- this depends on Sprint 4/5 live rebuild hookup first

## Immediate practical priorities

1. finish Sprint 2 class-site revision with CW
2. continue Sprint 3 actual adapters and intake backend wiring
3. start Sprint 5 with the first real rebuilt data hookup
4. then run Sprint 4 as a disciplined rebuild hardening pass rather than more ad hoc fixes
