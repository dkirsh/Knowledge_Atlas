# TASKS.md — Knowledge_Atlas

*Last updated: 2026-04-15 (session — article restructure + theory pages + Track 4 in-class exercise)*

---

## Newly Added — 2026-05-18 (User-journey design response)

These follow from DK's inline comments on `USER_JOURNEYS_THINKING_2026-05-17.md`. The design response lives at `docs/USER_JOURNEY_COMMENTS_RESPONSE_2026-05-18.md`; the VOI panel context (DK comment 7) lives at `docs/VOI_OPERATIONALISATION_PANEL_CONTEXT_2026-05-17.md`.

| ID | Task | Owner | Context |
|----|------|-------|---------|
| UJ-1 | **~~Draft the VR-measurability page~~** | CW | **COMPLETED 2026-05-18.** Page drafted as `160sp/ka_vr_measurability_content_2026-05-18.md` (~3,160 words, six APA references). Four positive families plus five exclusions, substitution-principle close, three-condition unpacking of "VR-tractable", week-by-week usage guidance, and a quick-reference table for machine consumption by the substitution skill. Commit `2da6ef5`. Next: render to HTML for the live Surface 6 (UJ-1b, new). |
| UJ-2 | **Substitution-skill data schema and refusal-criteria spec** | CW + Codex | Three knowledge-base tables (construct→measure, measure→VR-feasibility, measure→measure substitutability) plus generative-layer prompts and confidence-display design. Single point of failure for COGS 160 Fall pipeline — student who is told a substitution exists when it doesn't will design indefensible experiment. **Blocked on panel input** (Machery on construct proliferation; Mayo on refusal criteria). |
| UJ-1b | **Render VR-measurability markdown → `ka_vr_measurability.html`** | CW + Codex | Take `160sp/ka_vr_measurability_content_2026-05-18.md` and render to the canonical 160sp HTML template, with anchor IDs per family/exclusion so the substitution skill can deep-link. JSON sidecar (`data/vr_measurability_schema.json`) generated from the quick-reference table for machine consumption. Unblocked. |
| UJ-3 | **Differentiation-table HTML mockup for an 8-paper bibliography** | CW + Track 4 UX | Ten-column schema per `docs/USER_JOURNEY_COMMENTS_RESPONSE_2026-05-18.md` §3. Interactive faceting; LLM-generated "what differentiates these" paragraph on selected subsets. Pick one topic from the corpus (attention restoration is a good candidate per the worked example) and build the static mockup first; wire interactivity in a second pass. Unblocked. |
| UJ-4 | **Citation-graph minimal-viable view (researcher bibliography)** | CW + Track 1 | Three-layer build: (a) Connected-Papers-style force-directed graph; (b) Scite.ai-style supporting/contrasting/mentioning edge labels from corpus-internal extraction; (c) topic-cluster colouring. Open question: D3.js vs Cytoscape.js (latter has better network-specific affordances). Defer VOSviewer-style displays to an "advanced view" page. |
| UJ-5 | **~~Revise Week-1 wireframe: surface substitution skill in both admit-mode and choice-mode~~** | CW | **COMPLETED 2026-05-18.** Surface 4 re-labelled admit-mode (Week 1); new Surface 4b added for choice-mode (Week 3 hand-off) with worked example over attention-restoration topic and four candidate measures (pupillometry, SART, PRS, ANT) shown as a side-by-side comparison table with hardware/time/strengths/weaknesses. Substitution-skill ranking is plain-language prose with cross-links to the methodological-pitfalls page. Three new dependency annotations and three new design decisions added. Commit `2c7a49f`. |
| UJ-6 | **Methodological-pitfalls page (~5,000 words)** | CW | Six-section structure per `docs/USER_JOURNEY_COMMENTS_RESPONSE_2026-05-18.md` §6: Cook-Campbell validity threats; replication-crisis pitfalls; construct-validity beyond Campbell-Fiske; sample-related (WEIRD, convenience); VR-specific (presence confound, hardware effects, novel-medium); theory-and-explanation pitfalls (Lakatos, Kuhn, Orne, Rosenthal). Green/yellow/red tagging for student-tolerable vs researcher-required. **Blocked on panel review of tagging** (Mayo + Machery). |
| UJ-7 | **Per-panelist briefing letters for VOI panel (8 panelists)** | CW | One page each, tailored to which of the eleven panel questions each panelist's expertise is most central to. **Updated 2026-05-18: panel is now eight, with Carl Bergstrom added per DK directive (information-theoretic / computational-librarian seat).** Full panel: Pearl, Gelman, Thagard, Mayo, Machery, Buzsáki, Longino, Bergstrom. Each briefing must include the §9 Capabilities Appendix so the panelist's recommendation lands on operationalisable functions rather than blackboard formalisms. **Blocked on DK approval of panel composition** per `docs/VOI_OPERATIONALISATION_PANEL_CONTEXT_2026-05-17.md`. |
| UJ-8 | **Reconcile and push the 21-commit Knowledge_Atlas master branch backlog to origin** | DK | The local master is 21 commits ahead of origin/master, *and* origin is 2 commits ahead of local (as of 2026-05-18). Local includes user-journeys framing, Week-1 wireframe, VOI panel context with Bergstrom + capabilities appendix, user-journey design response, TASKS updates. Need to pull-rebase (or merge) the two origin commits in first, then push. Needs explicit DK go-ahead per `Forbidden Operations` and the global rule on push. |
| UJ-9 | **Triage three untracked-or-modified files left by other agents** | DK + CW | Local working tree has: `ka_article_view.html` modified, `tests/test_cross_page_journey_contract.py` modified, `data/ka_payloads/article_images/` and `data/ka_payloads/did_you_know_llm_overrides.json` untracked. These are likely Codex's in-progress work and were NOT touched by CW. Per coworker-boundaries memory, CW will not commit them; DK or Codex should resolve. |

---

## Newly Added — 2026-04-25 (Paper-quality follow-ups)

| ID | Task | Owner | Context |
|----|------|-------|---------|
| PQ-160F-001 | **Adapt the experimental-quality factors paper for COGS 160 Fall** | DK + CW | The academic paper at `docs/EXPERIMENTAL_PAPER_QUALITY_FACTORS_2026-04-23.md` is written for system-design rationale, not pedagogy. Produce a COGS 160 Fall-class version that re-orders the material around the *student designing an experiment* rather than evaluating one. Likely structure: pre-design checklist → Cook & Campbell's threats reframed as design choices → power and pre-registration as planning steps → open-science transparency as default lab habit → worked example walking through one student-designed experiment. Should sit alongside the existing seminar materials and link out to the panel-consultation document for the methodological backbone. |
| PQ-INTERP-001 | **Wire paper-quality fingerprint into the interpretation layer** | CW + Codex (after main build) | The interpretation layer produces a per-paper *gloss* — a reflective comment on what the paper shows, means, and suggests. The fingerprint is one input to that gloss but not the dominant one; the larger factor is the reflective synthesis. Specify the interaction in both directions: (a) the interpretation-layer prompt receives the structured fingerprint as context so the gloss is grounded in the paper's actual methodological profile rather than its prose flavour; (b) the interpretation layer's reflective verdicts (e.g., "construct claim is overreach", "result interesting but underpowered") are persisted as *interpretation cues* that surface alongside fingerprint fields on the paper page so the reader sees both layers. Schema work: add `interpretation_cue` and `interpretation_layer_version` columns to a new `paper_interpretation` table linked one-to-one with `paper_quality_fingerprints`. Update the design doc, build prompt, and overseer rollup before a separate "interpretation pass" build. |
| PQ-PRECONDS-001 | **Complete preconditions before invoking the Codex build prompt** | DK + CW | See response 2026-04-25 for the full precondition list. Headline items: 20-paper anchor set picked and rated, decision-tree DK-preference slots annotated, per-field extraction prompts drafted in `prompts/paper_quality/`, V7 pipeline migration tested in dry-run mode, three repos confirmed on clean branches. Until all are satisfied the prompt should not be handed to Codex. |
| PQ-TESTPROMPT-001 | **Write a separate testing prompt to harden against AG shortcutting** | CW | Build prompt does not currently catch the AG failure modes (Python heuristics replacing LLM calls, parallelisation that degrades quality, single-model agreement faked as multi-LLM). Write a companion `PAPER_QUALITY_TESTING_PROMPT_FOR_CODEX_2026-04-25.md` that includes adversarial tests (heuristic-detection probes, model-call audits, deterministic-output detection, paper-type variance checks) and is run *after* the build prompt completes but before the layer goes live. |
| PQ-WALKTHRU-001 | **Build interactive decision-tree walkthrough page** | CW | Current `PAPER_QUALITY_DECISION_TREE_2026-04-23.md` requires DK to scroll a 389-line markdown and edit underline slots in place. Build `ka_paper_quality_walkthrough.html` with three panes: full doc on the left (auto-scrolls to current node), single-node MCQ on the right (radio buttons + "Other — write in" + rationale field + confidence + flag-for-panel checkbox), header strip with progress indicator and prev/next. State persists to localStorage; exports to `data/paper_quality_dk_preferences.json` for Codex to parse. Replaces the manual markdown annotation pass. |
| PQ-COORD-CLEANUP-001 | **Demote coord_server to dashboard-only after blackboard lands** | CW or AG | Per `PAPER_QUALITY_BLACKBOARD_DESIGN_2026-04-25.md` §8: the HTTP coord server's task-claiming endpoints (`POST /claim`, `POST /release`, `POST /complete`) are no longer authoritative once the paper-quality build lands. Either remove them or convert to thin database proxies. Dashboard and message-passing endpoints stay. Defer until paper-quality build is live; scope is small (~half day). |
| PQ-COORD-NOTES-001 | **Append Lesson 7 (blackboard-not-heartbeat) to CW_COORDINATION_NOTES** | CW | Add the new lesson per `PAPER_QUALITY_BLACKBOARD_DESIGN_2026-04-25.md` §9. The 2026-04-25 paper-quality blackboard is the canonical example of the pattern. ~15 minutes work, do once paper-quality build is operational. |

---

## Newly Added — 2026-04-15

| ID | Task | Owner | Context |
|----|------|-------|---------|
| PNU-001 | **Add common-sense explanation column to PNU database** | Backend (Article_Eater) | The PNU database currently stores only the naked mechanism chain + citations. Add a column `common_sense_gloss` (markdown) plus `panel_reviewed_at` and `panel_reviewers`. Migrate existing rows with NULL; populate via the science-writer pass (PNU-002). Surfaced on `ka_neuro_elaboration.html`. |
| PNU-002 | **Science-writer pass on every PNU's naked sequence** | Science_Writer service | Ask the service: "what would it take to render this chain in everyday language without losing the constraints?" Expected output = analogies + concrete examples + numeric anchors per step. |
| PNU-003 | **Audit panel-of-record sources for each PNU** | Research agent | For each PNU, dispatch an agent to check whether the panel that originally introduced the sequence (e.g., Berson / Brainard / Hattar for the daylight–circadian PNU) has written follow-up papers that constrain or extend the listed edges. |
| PNU-004 | **Document the PNU identification process** | Docs | Write `docs/PNU_PROCESS.md`: how candidate PNUs are proposed, what evidence triggers inclusion, who reviews them, how stable a PNU has to be before it is shown to students. |
| EN-PCT-001 | **Compute live percentile for every article's EN score** | KA_Adapter | Currently the article page hard-codes a placeholder percentile. The adapter should compute percentile against the live distribution at build time and persist on the article record (`en_percentile`). Refresh every rebuild. |
| EN-WAR-001 | **Persist per-warrant scores on article records** | Backend | The `ka_en_warrants.html` page currently hard-codes the seven warrant rows for PDF-0011. The KA adapter should populate per-article warrant rows (source / method / statistical / replication / mechanism / coherence / defeater) from stage-17 outputs. |
| GUI-RQ-001 | **Rebuild the research-questions module on Topics page** | Track 4 (UX/GUI) | Current `ka_topics_v2.html` Questions tab is unsatisfactory: cards are noisy, filters are confusing, the answers are not anchored to a results page or accordion. Decide where the "answer" goes (new results page vs. inline accordion) and rebuild. Disaster banner is currently visible on the tab as a placeholder. |
| TOPICS-001 | **Decide answer-rendering pattern for Questions mode** | Design + Track 4 | Two candidates: (a) clicking a question opens a new results page that aggregates supporting articles, contested claims, and the active question's standing; (b) the question card accordions open in place. Document the pick + rationale. |
| ARTICLE-001 | **Auto-fetch real visual-cropping outputs for every article page** | KA_Adapter | The article page currently hard-codes paths into `data/ka_payloads/article_visuals/PDF-XXXX/`. The adapter should populate `visual_support_gallery` so the article template loops over real cutouts + OCR'd captions instead of hand-listed paths. |
| ARTICLE-002 | **Replace placeholder figure captions with OCR captions** | Article_Eater | Stage 12 (visual_cropping) currently produces filenames keyed by page+image index. Extend the stage to pair each cutout with its OCR'd caption text (likely available from stage 3's `.lines.json`). |
| RESOURCES-001 | **Server persistence for Track 2 / Track 3 resource pages** | Backend | `ka_track2_resources.html` and `ka_track3_resources.html` currently use localStorage with a "Local preview" badge. Add `POST /api/track_resources/{track}/{section}` and matching GET; keep localStorage as offline cache. |
| T4-PERSONA-001 | **Server persistence for Track 4 persona-panel prompt submissions** | Backend | `ka_track4_persona_panel.html` currently saves prompts to localStorage. Wire a `POST /api/exercises/persona_panel` endpoint that stores submissions for instructor critique without screen-share. |
| T4-PERSONA-002 | **Run the persona-panel exercise in class on 2026-04-16 and capture outcomes** | Instructor + Track 4 | Each Track 4 student should leave class with a critiqued prompt, a panel transcript, a one-page journey note, and at least one filed `ux-journey` issue. |
| THEORY-001 | **Build theory pages for all theories in corpus** | GUI + Backend | Template is at `ka_theory.html` (v0.1, demonstrated with ART). Need one page per theory (or parameterised via `?theory=` query string). At minimum: the top ~20 theories by corpus count (ART=31, Biophilic Design=23, Biophilia=23, Soundscape=21, SRT=16, Circadian Lighting=16, etc.). Each page needs: core claims, mechanism narrative, PNU (if available), principal references, corpus article list, competing/companion theories. |
| THEORY-PNU-001 | **Extend PNU generation (stage 13) to theory-level chains** | Article_Eater | Currently PNUs are generated per-article. Theory pages need theory-level PNU chains (e.g., ART → dorsal/ventral attention network switch). Generate or curate these and persist them so the theory template can pull them. |
| THEORY-MENTION-001 | **Full-text mention extraction for theory pages** | Article_Eater | The current `theories` metadata tag flags articles that engage with a theory, but doesn't distinguish active engagement from passing citation. Search OCR full text for each theory name and classify mention depth (framework / cited / passing). Add a `mention_type` column to the corpus table on each theory page. |
| THEORY-DASH-001 | **Empirical status dashboard per theory** | Backend + GUI | Aggregate effect sizes across corpus articles for each theory; generate funnel plot for publication bias; show on theory page §7. |
| THEORY-NET-001 | **Cross-theory network visualisation** | GUI + Backend | Build a graph (D3 or similar) showing theories connected by shared articles in the corpus. Link from each theory page §6. |
| THEORY-ANNOT-001 | **Student annotation space on theory pages** | Track 4 (UX/GUI) | Add a section where COGS 160 students can post critical commentary on a theory, linked to their article analyses. Requires server-side persistence. |
| STYLE-001 | **~~Create K-ATLAS visual style guide~~** | GUI | **COMPLETED 2026-04-15.** Written to `docs/KA_STYLE_GUIDE.md`. Covers all three regimes (Global KA, 160sp, legacy Designing_Experiments), full token set, component patterns, do/don't reference, and disambiguation table vs. Article_Eater and legacy palettes. Supersedes `docs/KA_BRAND_STYLE_GUIDE.md`. |
| SCSUMMARY-001 | **Batch re-generation of science summaries to meet 750–1250 word spec** | Article_Eater / AG | Only 29 of 833 standalone .md science summaries meet 750–1250 words. Mean is 317 words (median 253). The 60 ATLAS-chunk exemplars (mean 799) prove the current prompt works — the problem is legacy data, not the prompt. Batch re-run through current pipeline with tightened V2 patch (`prompts/SCIENCE_WRITER_TIGHTENED_V2.md`). |
| DB-SC-001 | **~~Add science_writer_results + figure_crops tables to pipeline DB~~** | Backend | **COMPLETED 2026-04-15.** Two new tables added to `pipeline_lifecycle_full.db`: `science_writer_results` (921 rows: word counts, PRS scores, output paths, figure counts) and `figure_crops` (10,253 rows: per-crop validation status, detection layer, bounding boxes, captions). Relational integrity verified — 0 orphans. |
| MANIFEST-SC-001 | **~~Create SC summary manifest~~** | Backend | **COMPLETED 2026-04-15.** Written to `data/science_writer_articles/MANIFEST.json` (833 summaries indexed with word counts, HTML status, exemplar links, crop counts). |
| MULTIMODAL-001 | **Add multimodal vision support to agent_core.py** | Backend | **COMPLETED 2026-04-15.** New `call_llm_multimodal(prompt, image_paths, cfg)` function added to `src/agents/agent_core.py`. Supports Anthropic, OpenAI, and Gemini multimodal APIs. Base64 encodes page images. Existing `call_llm()` unchanged for backward compatibility. |
| CROP-GAP-001 | **Close the 53% crop gap — generate missing page images** | AG / Backend | 5,462 of 10,253 VSG items (53.3%) are `skipped_no_image` — the page images don't exist. Of 751 papers processed, 676 have crop directories but only 46.7% of items succeeded. Root cause: missing page image PNGs for those pages. Need to run page image rendering for the missing papers/pages, then re-run the crop pipeline. |
| CROP-REVIEW-001 | **QA the 1,851 needs_manual_review crops** | AG / Track 4 | 1,851 VSG items (18.1%) are whole-page fallbacks flagged `needs_manual_review`. These used `L3_whole_page_fallback` because no Mathpix bbox was detected. Need manual or semi-automated review to either accept, re-crop, or flag for re-extraction. |
| SC-PIPELINE-001 | **Wire multimodal page images into science writer LLM calls** | Backend | `agent_core.py` now supports multimodal, but `science_writer_service.py` still calls text-only `call_llm()`. Update the summary generation flow to use `call_llm_multimodal()` with actual page image paths so the LLM reads the PDF pages directly, as the prompt requires. |
| CONTEXT-001 | **Surface context files on each track hub and setup page** | GUI | The prompt-scaffolding context files at `160sp/context/` (one per track) are hidden behind the technical setup page. Add a prominent "Start your AI session" card on each track hub linking to the appropriate context file, with instructions to drop it into the AI prompt. |
| REPO-001 | **Create `kirsh-lab/KA-Rooms` GitHub repo** | Instructor (David) | Track 3 setup page references `git@github.com:kirsh-lab/KA-Rooms.git` but the repo doesn't exist. Run `gh repo create kirsh-lab/KA-Rooms --public` from Mac terminal, push starter structure (base .uasset stubs, ai_harness/, .gitattributes for LFS). |

*Prior pending tasks below are unchanged.*

---

*Originally updated: 2026-03-24 (session 4)*
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
