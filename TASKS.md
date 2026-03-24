# TASKS.md — Knowledge_Atlas

*Last updated: 2026-03-24 (session 2)*
*Owner repo: `/Users/davidusa/REPOS/Knowledge_Atlas/`*
*This file is the canonical task log for all GUI / frontend work.*

---

## Repo Assignment Rules (MANDATORY — all AI workers)

| Repo | Purpose | GUI work goes here? |
|------|---------|-------------------|
| `Knowledge_Atlas` | Live GUI · site · frontend | **YES — all new GUI work here** |
| `Article_Eater_PostQuinean_v1_recovery` | Extraction · JSON · EN/BN · summaries · rebuild logic | No |
| `Designing_Experiments` | Course docs · planning · legacy frontend (retiring) | No — migrate to KA |

**Rules:**
1. All new HTML, JS, CSS files go in `Knowledge_Atlas/`. Never in REPOS root or AE recovery.
2. `Designing_Experiments/frontend/` is legacy. Files there are superseded by KA equivalents. Do not add new UI files there.
3. When moving UI assets, record: old path · new path · whether old copy deleted/deprecated.
4. Commit by workstream — GUI commit separate from backend/docs commits.
5. Keep Knowledge_Atlas backed up to GitHub and avoid letting local-only work pile up.

---

## Pending

| ID | Task | Added | Context |
|----|------|-------|---------|
| KA-T2 | **Build GUI evaluation / design agent (Track 4 tool)** | 2026-03-24 | Autonomous agent that navigates KA pages, runs user scenarios, compares actual vs. AI-optimal path, outputs structured UX report (friction, missing affordances, copy issues). |
| KA-T7 | **Create GitHub remote and push AE recovery pending changes** | 2026-03-24 | 30 tracked modified files in AE recovery await push to `origin/codex/recovery-cc-migration-artifacts`. Awaiting David's go-ahead. |

---

## In Progress

| ID | Task | Started | Notes |
|----|------|---------|-------|

---

## Completed

| ID | Task | Completed | Outcome |
|----|------|-----------|---------|
| KA-C1 | Move KA HTML files from REPOS root to `Knowledge_Atlas/` | 2026-03-24 | 22 HTML + 3 JS files moved. Zero broken links (verified by link checker script). |
| KA-C2 | Move DE frontend files to `Knowledge_Atlas/Designing_Experiments/` | 2026-03-24 | 12 HTML + `data/en_navigator_data.json` moved. DE repo move recorded with git commit 8f90267. |
| KA-C3 | Initialize git in Knowledge_Atlas, first commit | 2026-03-24 | 39 files, commit 8b48ffb. No remote yet — see KA-T1. |
| KA-C4 | Wire new pages into contributor nav + NAV_MAP | 2026-03-24 | Tag Bundles, Question Maker, Propose Article, Article Finder, GUI Assignment, Topic Browser all wired. |
| KA-C5 | Build `ka_topics.html` — 20-cluster topic browser | 2026-03-24 | VOI-sorted grid, priority banner, category filter tabs, 4 action buttons per card. |
| KA-C6 | Complete QUERY_BANK — 12 missing DYK topics | 2026-03-24 | All 15 topics now have full answer entries in `ka_demo_v04.html`. |
| KA-C7 | Build `ka_article_finder_assignment.html` (Track 2) | 2026-03-23 | 5-phase workflow, Query Diary, tool orientation, pipeline steps. |
| KA-C8 | Build `ka_question_maker.html` | 2026-03-23 | 20 clusters, 4 tools, quality-gate queue, VOI panel. |
| KA-C9 | Build `ka_article_propose.html` | 2026-03-23 | DOI lookup, 4-step intake, PDF upload, queue sidebar. |
| KA-C10 | Fix two bugs in `ka_hypothesis_builder.html` | 2026-03-23 | Bug 1: sum-signals replace chain (all 8 IDs). Bug 2: Stage 6 gauge not updated by credence slider. |
| KA-C11 | Build `ka_tag_assignment.html` (Track 1) | 2026-03-23 | 5 algorithm bundles (A–E), claim modal, Phase 0 reference table. |
| KA-C12 | Build `ka_gui_assignment.html` (Track 4) | 2026-03-23 | 4-phase workbook: User Types · Scenarios · Walkthrough · Spec Wall. |
| KA-C13 | Push Knowledge_Atlas to GitHub remote | 2026-03-24 | Repo now tracks `origin/master` at `github.com/dkirsh/Knowledge_Atlas`. |
| KA-C14 | Canonicalize GUI design agent in KA repo | 2026-03-24 | Added repo-local design agent spec, panel review, process/repairs doc, prompt, checker, and tests. |
| KA-T3/T8 | Update `ka_article_finder_assignment.html` — Weeks 3–8 with milestone table | 2026-03-24 | Hero pill, 5-phase milestone table, workflow bar labels, phase callouts, quantity targets (15/20/50/150), PHASE_STATUS strings. Commit 53d6b9d. |
| KA-T4 | Add `howItWorks` paragraphs to all 27 measures in `ka_sensors.html` | 2026-03-24 | Mechanistic explanations covering transduction, neural pathway, and methodological constraints. New expand-section rendered conditionally. Commit 4bd5c0a. |
| KA-T5 | Verify all 15 QUERY_BANK entries in `ka_demo_v04.html` | 2026-03-24 | Script audit: all 15 topic keys (sleep, replication, attention … exercise) present with all 5 required fields (queryText, title, bodyHTML, evidenceHTML, followups). ✅ All verified. |
| KA-T6 | Wire `ka_topics.html` into all standalone page navs | 2026-03-24 | Topics link added to 7 pages: ka_article_search, ka_sensors, ka_gaps, ka_question_maker, ka_hypothesis_builder, ka_evidence, ka_dashboard (both top nav + sidebar). Commit 0930943. |

---

## Session Notes — 2026-03-24

### Repo consolidation completed
All KA UI files now in `Knowledge_Atlas/`. REPOS root is clean. DE legacy frontend moved to `Knowledge_Atlas/Designing_Experiments/` as subdirectory.

### Knowledge_Atlas awaits GitHub remote
Until David creates `github.com/dkirsh/Knowledge_Atlas` and CW runs `git remote add` + `git push`, all work is local-only. Files exist on Mac disk at `/Users/davidusa/REPOS/Knowledge_Atlas/`.

### GUI agent (KA-T2) — design note
The planned GUI agent is distinct from `ka_gui_assignment.html` (a student workbook). The agent would: (1) autonomously navigate KA pages using browser tools; (2) run through defined user scenarios; (3) compare its path against the AI-suggested optimal path; (4) output a structured UX report flagging friction points, missing affordances, and copy issues. This is Track 4's analytical deliverable automated.
