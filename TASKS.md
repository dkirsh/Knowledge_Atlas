# TASKS.md — Knowledge_Atlas

*Last updated: 2026-03-24 (session 4)*
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
| KA-T9 | **Push session-3+4 commits to GitHub** | 2026-03-24 | Run `git push origin master` from Mac terminal (sandbox cannot auth HTTPS). Session-3 commits: 831f7cd, 0f5657e, 5afb8b5, f7291a2, 25b02a9. Plus new session-4 commit (see below). |

| KA-T11 | **Create Neural Underpinnings architecture and first pathway inventory** | 2026-03-24 | Add explicit neural-underpinnings lane, pathway-guide objects, and classic-paper reading-list structure. Seed from panel-proposed pathways. |
| KA-T12 | **Integrate neural-underpinnings literature work into article-finder track** | 2026-03-24 | Assign COGS 160 article finders to pathway families. Start from classic anchor papers proposed by panels, then expand with reviews, direct measurement papers, and pathway tests. |
| KA-T13 | **Add adaptive nav preferences to signup and post-login nav** | 2026-03-24 | Let users declare a primary preference at signup/login, then reorder nav emphasis without changing the underlying IA. |
| KA-T14 | **Add anonymous user-type mode selection before login** | 2026-03-24 | Let visitors choose a user type before login and adapt nav/featured entry points immediately, with a visible switch-mode control. |
| KA-T15 | **Wire Track 2 pathway assignment sheet into student setup and article-finder assignment** | 2026-03-24 | Use the first neural-pathway assignment model as part of Track 2 onboarding and collection work. |
| KA-T16 | **Implement visible mode-switch payoff on core pages** | 2026-03-24 | When a user tries a user type, the navbar, featured actions, and entry emphasis should change immediately so the benefit is obvious. |
| KA-T17 | **Redesign article intake for PDF-first batch upload with automatic citation extraction** | 2026-03-24 | Current `ka_article_propose.html` is misleading for Track 2 because it prefers DOI/manual APA before PDF upload. Replace with PDF-first and title/DOI-based citation resolution via metadata + API lookup. Duplicate test should be immediate; relevance triage should be asynchronous; rejected staged PDFs should be deleted promptly to save space. |
| KA-T18 | **Add secure quarantine + validation contract for public PDF uploads** | 2026-03-24 | Public-facing article suggestion means uploaded files are untrusted. Require magic-byte/MIME validation, parser validation, encrypted-file rejection, file hash, quarantine-before-promotion, isolated processing, and prompt deletion of rejected bad files. |
| KA-T19 | **Split public article suggestion from Track 2 intake steering** | 2026-03-24 | Keep `ka_article_propose.html` outward-facing, but steer COGS 160 Track 2 users toward the full search → screen → acquire → stage workflow from assignment/setup pages. |
| KA-T20 | **Unify intake modes across public and student users** | 2026-03-24 | Same core intake surface should support batch PDFs, pasted citations, citation files, and optional DOI/title enrichment. Identity affects attribution, quotas, and progress reporting, not the basic intake mechanism. |
| KA-T21 | **Audit KA pages for single-item / citation-first intake bias** | 2026-03-24 | `ka_datacapture.html` is still single-item and citation-first. Audit other contributor/student pages for the same bias and normalize them toward batch-capable intake. |
| KA-T22 | **Wire usability critic to real LLM endpoint (POST /api/critique)** | 2026-03-29 | `ka_usability_critic.js` currently does pure client-side rating + localStorage. Next step: POST the structured ratings + page URL + page title to an LLM endpoint that returns AI-generated suggestions per heuristic violation. Pattern: on "Get AI Suggestions" button click, send `{ heuristic, rating, note, pageTitle, pageUrl }` payload; receive `{ suggestion, priority, estimatedEffort }` per item. |
| KA-T23 | **Add server-side critique aggregation endpoint for instructor view** | 2026-03-29 | Add `POST /api/critique/submit` to `ka_auth_server.py` that stores student critique sessions server-side. Add `GET /api/critique/summary` (instructor-only) returning aggregate heuristic violation counts, most-flagged pages, and anonymous student breakdowns. Display in a new `ka_instructor_critique_view.html` page. |
| KA-T24 | **Tag critique sessions to authenticated students via ka_auth_server.py** | 2026-03-29 | When a logged-in student submits a critique, attach `student_id` (from JWT) to the session record. This enables per-student grading of heuristic evaluation work and aggregate class-level analytics. |
| KA-T25 | **Add screenshot capture capability to usability critic panel** | 2026-03-29 | Let students capture a screenshot of the current viewport (or a selected element) and attach it to a heuristic rating. Use `html2canvas` or a DOM-to-SVG approach. Screenshot stored as base64 in the session record and displayed as thumbnail in the Summary tab. |
| KA-T26 | **Add pin-point draggable critique mode to usability critic** | 2026-03-29 | Allow students to click any element on the page and "pin" a critique to it (like a comment bubble). The pin stores the element CSS selector + bounding box. Panel shows pins as an overlay layer, toggleable. This supports the "element-level critique" use case that the current panel-level flow does not. |

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
| KA-S3-1 | Fix `ka_register.html` — inline validation, localStorage, success screen | 2026-03-24 | field-level errors, password strength bar, track-name update, success screen, ka_logged_in set on submit. Commit 831f7cd. |
| KA-S3-2 | Create `ka_about_page.js` — always-visible About This Page anchor | 2026-03-24 | Injects #about-this-page section (objective, users, uses) + floating badge on all 22 pages. No login required. Links to function spec panel when logged in. Commit 0f5657e. |
| KA-S3-3 | Add `KA_ABOUT_PAGE` + `KA_PAGE_FUNCTION` to all 22 pages | 2026-03-24 | All 22 pages now have both specs defined. 8 pages that were missing ka_page_function.js now have it too. Commit 0f5657e. |
| KA-S3-4 | Archive DE pages — `COURSE_DESIGN_ARCHIVE_2026-03-24.html` | 2026-03-24 | Full inventory of 12 pre-4-track DE pages with rationale, carry-forward items, Track 4 eval questions. Plus "Previous pages" footer sections on 7 KA pages. Commit 5afb8b5. |
| KA-S3-5 | Add Contributor Tracks section to `ka_home.html` | 2026-03-24 | 4 track cards (T1–T4) with colour-coded pills, icons, descriptions, and assignment links. Register CTA bar. Register button in top nav. Commit f7291a2. |
| KA-S4-1 | Build `ka_student_setup.html` — Student Onboarding guide | 2026-03-24 | 7 sections: install, clone + personal branch, student DB copy, per-track Day 1 checklists (accordion, milestones), PR workflow, AI intro. Wired into all 3 assignment pages + sitemap + homepage. |
| KA-S4-2 | Build `ka_ai_methodology.html` — AI-Directed Development Methodology reference | 2026-03-24 | 6 methods: 5-component prompt structure (annotated + per-track examples), 5 failure modes, contracts/success conditions, trust calibration L0–L5, ruthless-prompt escalation, expert panel pattern. Wired into all 3 assignment pages + sitemap + homepage. |
| KA-T10 | Build `ka_vr_assignment.html` — Track 3 VR Production workbook | 2026-03-24 | 5-phase workbook: paradigm selection (6 candidate paradigms, memo form), protocol translation (8-field design spec), A-Frame scene build (starter template + build checklist), DV instrumentation (log-events component + 6 event types + schema), naïve-user validation (2-walkthrough protocol + PR checklist). Homepage Track 3 card updated to link directly. |

---

## Session Notes — 2026-03-24

### Repo consolidation completed
All KA UI files now in `Knowledge_Atlas/`. REPOS root is clean. DE legacy frontend moved to `Knowledge_Atlas/Designing_Experiments/` as subdirectory.

### Knowledge_Atlas awaits GitHub remote
Until David creates `github.com/dkirsh/Knowledge_Atlas` and CW runs `git remote add` + `git push`, all work is local-only. Files exist on Mac disk at `/Users/davidusa/REPOS/Knowledge_Atlas/`.

### Session 3 — 2026-03-24

**Registration flow fixed.** `ka_register.html` now has full inline validation (per-field error spans, password strength meter, duplicate-email check), persists `ka_pending_registrations[]` and `ka_logged_in='1'` to localStorage on submit, and shows a styled success screen in place of the old `alert()`. Setting `ka_logged_in` is what reveals the function spec button on all pages.

**"About this page" system.** `ka_about_page.js` is a new always-visible companion to the login-gated `ka_page_function.js`. It injects a `#about-this-page` section at the bottom of every page with the page's objective, primary users, and primary uses — plus a floating "⊕ About this page" badge. When logged in, the section also shows a "Full function spec →" link that opens the existing slide panel. All 22 KA pages now have both `KA_ABOUT_PAGE` and `KA_PAGE_FUNCTION` defined.

**Course design archive.** The 12 pre-4-track DE pages are documented in `Designing_Experiments/COURSE_DESIGN_ARCHIVE_2026-03-24.html`, with status (superseded/partial/data still active), rationale for the transition, carry-forward items, and Track 4 GUI evaluation questions. "Previous pages" footer links added to 7 KA pages pointing to their DE counterparts.

**4-track homepage integration.** `ka_home.html` now has a Contributor Tracks section (between hero and about) with 4 colour-coded track cards, each linking to the assignment page. A Register button was added to the top nav. Track 3 shows "Assignment coming soon" — the VR workbook (KA-T10) is next on the list.

**Push needed.** 4 commits (831f7cd, 0f5657e, 5afb8b5, f7291a2) are local only. Run `git push origin master` from Mac terminal.

### Session 4 — 2026-03-24

**Student onboarding pages.** Two new pages added to support students who use AI to write code and navigate the git+database workflow:

- `ka_student_setup.html` — Step-by-step getting-started guide covering tool install, personal branch creation (`track/N-staging/username`), student database copy, per-track Day 1 checklists (accordion with milestone table per track), PR submission workflow, and a pointer to the AI methodology page.
- `ka_ai_methodology.html` — Methodology reference covering: (1) chatbot vs. directed instrument distinction, (2) five-component prompt structure with annotated anatomy block and tabbed per-track worked examples (T1 tagging, T2 query generation, T4 GUI evaluation), (3) five failure modes with diagnostics and fixes, (4) contracts and success conditions, (5) trust calibration L0–L5, (6) ruthless-prompt escalation ladder, (7) expert panel pattern.

Both pages wired into: all three track assignment pages (Student Resources bar above each page's content), `ka_sitemap.html` (two new cards in Contributor Tools section), and `ka_home.html` (Get Started link in register CTA bar).

**Push needed.** All session-4 commits are local. Run `git push origin master` from Mac terminal.

### GUI agent (KA-T2) — design note
The planned GUI agent is distinct from `ka_gui_assignment.html` (a student workbook). The agent would: (1) autonomously navigate KA pages using browser tools; (2) run through defined user scenarios; (3) compare its path against the AI-suggested optimal path; (4) output a structured UX report flagging friction points, missing affordances, and copy issues. This is Track 4's analytical deliverable automated.

### Session 5 — 2026-03-29

**ka_usability_critic.js expanded to 5 tabs (35 dimensions).** Added a Viz V1–V17 tab implementing heuristics from Tufte (data-ink, lie factor, chartjunk, small multiples), Cleveland (perceptual hierarchy, grayscale test, baseline), Cairo (uncertainty, functionality, insightfulness, form/purpose), Knaflic (preattentive attributes, declutter, direct labeling, assertion title), and Shneiderman info-seeking mantra (overview→filter→details, persistent context). Auto-detection (`detectVizElements()`) scans for canvas, SVG, and chart-class elements; amber dot on Viz tab when elements found. Summary tab updated to show 35-dimension totals in 3 section scorecards. History tab shows 📊 viz pill on past sessions with viz data. Critic panel injected into `ka_dashboard.html`, `ka_home.html`, `ka_demo_v04.html`, `ka_user_home.html`, `ka_workflow_hub.html`. New TODOs KA-T22 through KA-T26 added for future capability expansion.

**Agent directory unified across both repos.** `Knowledge_Atlas/agents/` and `Article_Eater_PostQuinean_v1_recovery/agents/` now share the same 5-agent suite, best-of-both merged into GUI Agent v3 (32-item spec, dual-framework Streamlit+HTML/JS, 6 KA roles, 13-scholar panel, V1–V17 viz, 20-item checklist). New agents: `GUI_AGENT_V3.md`, `USABILITY_CRITIC_AGENT.md`, `README.md` (pipeline master). Mirrored: `SCIENCE_WRITER_AGENT.md`, `GUI_PRESENTATION_AGENT.md`, `EXPERIMENTAL_EVALUATE_AGENT.md` — both repos updated with KA-specific paths.

**Reference guides linked into DE student track pages.** `gui_track_overview.html` and `gui_wk05_expert_panel.html` now link `gui_visualization_guide.html` and `gui_design_experts_reference.html`.

**Active TODOs from this session:**
- [ ] Redesign `ka_student_setup.html` (A0) with contextual rationale + "Next Step →" CTAs (see detailed plan below)
- [ ] Audit all track assignment pages for explanation-adjacent-to-action pattern
- [ ] Expand GUI track from 3 pairs to 4 pairs — add D3b: In-Browser Usability Audit (ka_usability_critic.js on 8 priority pages) as Pair 4 deliverable
- [ ] Document agent unification in master doc (appropriate section in ATLAS theoretical foundations doc or new Part XXIII)
