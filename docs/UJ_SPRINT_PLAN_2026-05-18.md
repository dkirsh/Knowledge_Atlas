# User-journey sprint plan and farming-out recommendations
*David Kirsh's question on the wireframe-revision dependencies, 2026-05-18*

DK's question after reviewing the wireframe: "Dependencies define a set of sprints. Fine by me. Can you do them all? Any reason to farm them out?" This document is the direct answer.

The short version: of the user-journey work that DK's review now puts on the table, roughly two-thirds is CW's natural lane — design specifications, content drafts, wireframe revisions, panel coordination, and the academic-register prose that the user-preference profile asks for. Roughly one-third should be farmed out to Codex (for pipeline and back-end work where Codex owns the codebase and will move faster than CW could in a strange repo) and to the Track-4 students (for the article-viewer page that is their pedagogical exercise). A small slice is AG's natural lane — corpus-wide extraction passes that benefit from AG's parallel-batch strengths.

The argument for *not* farming out the design and content work is that the eight-surface wireframe, the VR-measurability page, the VOI panel context, the user-journey design response, and the methodological-pitfalls page all need to read as one document by the time the design is locked. Single-authorship of the conceptual layer is the cheap way to keep them coherent; multi-authorship would force a synchronisation phase between every increment.

The argument for *farming out* the pipeline-and-front-end implementation work is that the existing pipeline (the V7 pipeline, the adaptive paper-type classifier, the visual-cropping stage, the science-writer service) is Codex's territory and that CW would consume a disproportionate amount of time learning it relative to Codex who already knows where every stage's outputs land. Pedagogically, the article-viewer page belongs to the Track-4 students whose work it is.

The plan is therefore eight sprints, distributed across the three workers with explicit owners and explicit handoff points. The sprints are sized to be runnable in parallel where the dependencies allow, and they include the work that is already complete so the reader can see where CW is on the curve.

---

## Sprint UJ-A — Content drafts (CW, ~1 week, partially in flight)

The content layer of the user-journey work. Each piece is a piece of polished prose; the academic register and reference accuracy is the natural CW lane.

| Piece | Status | Notes |
|---|---|---|
| `docs/USER_JOURNEYS_THINKING_2026-05-17.md` | done (commit 8379385) | First-task framing |
| `docs/USER_JOURNEY_COMMENTS_RESPONSE_2026-05-18.md` | done (commit 12e6e4a) | Response to DK's six other comments |
| `docs/VOI_OPERATIONALISATION_PANEL_CONTEXT_2026-05-17.md` | done; updated with Bergstrom + capabilities appendix (commit c98775f) | Panel context, ten targets, eight panelists, eleven questions |
| `160sp/ka_vr_measurability_content_2026-05-18.md` | done (commits 2da6ef5, bb3c316) | Includes Family-2 IATs / Q-sort / adaptive preference and Family-4 specific sensor inventory per DK 2026-05-18 |
| Cook &amp; Campbell four-validities content | drafted inside the wireframe (commit 1178cd8 Surface 7b); needs lifting into a standalone markdown file | UJ-A1 task |
| Methodological-pitfalls page (UJ-6) — content draft | not yet drafted; blocked on panel tagging review | UJ-A2 task; ~5,000 words; CW writes the draft, panel approves the green/yellow/red tagging |
| Per-panelist briefing letters (UJ-7) | not started; blocked on DK panel-composition approval | UJ-A3 task; eight one-page letters; each includes the §9 capabilities appendix |
| Substitution-skill design spec (UJ-2 written content) | partial — described in `docs/USER_JOURNEY_COMMENTS_RESPONSE_2026-05-18.md` §2; needs a fuller spec doc for Codex | UJ-A4 task |
| V7-Lite spec doc for Codex | not yet drafted | UJ-A5 task; specifies which V7 stages run synchronously vs queued, plus the topic-similarity threshold calibration protocol |

**Owner**: CW. **Reason not to farm out**: design and content coherence; one-author voice across the seven documents that comprise the user-journey work. **Timeline if pursued sequentially**: ~5 days of CW time for the unblocked items (UJ-A1, UJ-A4, UJ-A5); UJ-A2 and UJ-A3 wait on panel and DK respectively.

---

## Sprint UJ-B — Wireframe and HTML renders (CW + Track 4 UX, ~1 week)

The visual prototype layer. The single-doc wireframe (`160sp/ka_week1_wireframe_2026-05-17.html`) is the design artefact; production HTML pages are the next step.

| Piece | Status | Owner |
|---|---|---|
| Week-1 single-doc wireframe with all DK 2026-05-18 revisions | done (commit 1178cd8) | CW |
| `ka_vr_measurability.html` render of the markdown source (UJ-1b) | not started | CW (markdown→HTML rendering is straightforward) |
| `ka_validities_showcase.html` rendered from the wireframe Surface 7b | not started | CW |
| `ka_evaluate_paper_for_vr.html` (Surface 4 admit-mode + Path B) | not started; specifies the two-path branching | CW for first pass; back-end wiring blocked on UJ-C |
| `ka_choose_measure_for_vr.html` (Surface 4b choice-mode) | not started; spec exists | CW for first pass; back-end wiring blocked on UJ-D |
| `ka_dyk_browser.html` with new CTAs and short-list write path | partial (Surface 2 mock); needs full HTML | CW for HTML; wiring waits on UJ-E |
| Differentiation-table HTML mockup (UJ-3) | not started | CW + Track 4 UX |

**Owner**: CW for the HTML drafts; Track 4 UX involvement is optional for the differentiation-table mockup if they want the exercise. **Reason to keep with CW**: continuity with the wireframe author, fast iteration on the 160sp style guide. **Reason for Track 4 involvement**: the differentiation-table is exactly the kind of interactive surface a Track 4 student should be designing in class as the exercise.

---

## Sprint UJ-C — V7-Lite pipeline (Codex, ~2 weeks) → FARM OUT

The Path-B ingest pipeline for uploaded papers. The pipeline reuses existing V7 stages but as a synchronously-returning subset.

**This is the canonical farm-out.** Codex owns the V7 pipeline (`Article_Eater_PostQuinean_v1_recovery`), knows where each stage's outputs land, and has the blackboard-coordination infrastructure already in place. CW would have to spend substantial time learning a codebase Codex knows intimately, and the work would still be done less well than Codex would do it. The right move is for CW to write the V7-Lite specification document (UJ-A5 above) and hand it to Codex.

| Sub-task | Owner | Notes |
|---|---|---|
| Spec doc for V7-Lite (which stages, in what order, what cached) | CW (UJ-A5) | Inputs that Codex needs |
| Paper-type classification endpoint | Codex | `atlas_shared.AdaptiveClassifierSubsystem` exists; just an API exposure |
| Embedding-similarity-to-corpus stage | Codex | Reuse existing embedding store from the topic-crosswalk work |
| IV/DV extraction stage (subset of V7) | Codex | Existing V7 stage 7 |
| Methods-extraction stage | Codex | Existing V7 stage 8 |
| VR-suitability mapper from DV → measurability short codes | Codex + CW (CW writes the mapper logic; Codex wires it) | New module |
| Topic-similarity threshold calibration | AG | AG has run similar held-out-validation passes before |
| New-topic-seed queue interface | Codex | Small; a flag-for-instructor table plus a notification |

**Timeline**: ~2 weeks for the full pipeline once Codex picks up the spec. Calibration is concurrent with build.

---

## Sprint UJ-D — Substitution skill (Codex + CW, ~2 weeks, panel-blocked) → FARM OUT (with CW spec)

The substitution skill that drives Surface 4 admit-mode and Surface 4b choice-mode. The skill is a retrieval-and-ranking system over the construct-to-measure-to-VR-feasibility-to-substitute graph (see `docs/USER_JOURNEY_COMMENTS_RESPONSE_2026-05-18.md` §2).

| Sub-task | Owner | Notes |
|---|---|---|
| Refusal-criteria and confidence-display design | CW + Panel | UJ-A4 + Mayo/Machery input |
| Construct-to-measure knowledge base | AG + Codex | AG runs the corpus-wide LLM extraction; Codex stores |
| Measure-to-VR-feasibility lookup (from measurability short codes) | CW + Codex | Derived from `ka_vr_measurability_content_2026-05-18.md` quick-reference table |
| Measure-to-measure substitution graph | AG + CW | AG extracts; CW edits the curated subset |
| Generative explanation layer | Codex | Wraps the retrieval result in prose |
| Front-end surface (admit-mode and choice-mode tabs) | CW (HTML) + Codex (wiring) | UJ-B continuation |

**Timeline**: blocked until UJ-F panel responses return on confidence display and refusal criteria. Once unblocked, ~2 weeks.

---

## Sprint UJ-E — Short-list + article-viewer wiring (Codex + Track-4 students, ~1–2 weeks) → FARM OUT (CW spec)

The logged-in deferred-commitment workflow DK asked for on Surface 3, plus the hot anchor-paper links that open the article viewer.

| Sub-task | Owner | Notes |
|---|---|---|
| Short-list persistence schema | CW (spec) + Codex (build) | Schema sketch in wireframe Surface 3 dependencies |
| Local-profile authentication (pre-Shibboleth) | Codex | Per grading-and-policy memory: Shibboleth deferred to Fall 2026 |
| Shibboleth integration | Codex (Fall 2026) | Deferred |
| Short-list write paths from DYK browser, per-topic page, article viewer | Codex | Three call sites |
| Article-viewer URL contract (`ka_article_view.html?id=PDF-XXXX`) | Track-4 students | The article viewer is their pedagogical exercise |
| Article-viewer graceful-degradation for un-ingested papers | Track-4 + Codex | Show partial fingerprint where full extraction has not yet landed |

**Pedagogical reason to farm to Track-4**: the article viewer is a Track-4 student-designed page; making them own the URL contract and the graceful-degradation behaviour is the right pedagogy. CW writes the contract document; Track-4 implements. The instructor's hand on this is light.

---

## Sprint UJ-F — VOI panel (CW + DK + eight external panelists, ~4 weeks round-trip)

The slowest sprint, because the response time is set by the external panelists. The eight panelists are: Pearl, Gelman, Thagard, Mayo, Machery, Buzsáki, Longino, Bergstrom. Each receives the panel-context document, a one-page briefing tailored to which questions their perspective is most central to, and the capabilities appendix.

| Step | Owner | Timeline |
|---|---|---|
| DK approves panel composition | DK | This week |
| CW drafts the eight briefing letters | CW | 3–4 days after approval |
| DK reviews briefings, sends or authorises transmission | DK + CW | 2 days |
| Panel response window | Panelists | 2 weeks |
| CW writes synthesis | CW | 3 days after responses |
| DK adjudicates contested questions | DK | as available |
| Implementation prompts for Codex | CW | 2 days after adjudication |

**Owner**: CW with DK adjudication. **Reason not to farm out**: academic-correspondence-register work; reference accuracy; the synthesis is the kind of analytical writing CW is best at among the three workers.

---

## Sprint UJ-G — Citation-graph MVP (CW + Codex, decision pending)

The researcher-facing bibliography view (per `docs/USER_JOURNEY_COMMENTS_RESPONSE_2026-05-18.md` §4). Three-layer build (citation graph; Scite-style edge labels; topic-cluster colouring).

| Sub-task | Owner | Notes |
|---|---|---|
| Library choice (D3.js vs Cytoscape.js) | CW + Codex | Cytoscape.js has better network-specific affordances; D3 has more customization. Lean Cytoscape for the network layer |
| Force-directed graph build | Codex | Front-end JS; Codex faster than CW here |
| Scite-style edge label extraction (from corpus-internal citations) | AG | Corpus-wide extraction pass; LLM classifies citing-sentence as supporting/contrasting/mentioning |
| Topic-cluster colouring | Codex + AG | Topic-model output already exists for the topic crosswalk |

**Timeline**: ~1–2 weeks once library choice is made.

---

## Sprint UJ-H — Methodological-pitfalls page (CW, panel-blocked)

The six-section page per `docs/USER_JOURNEY_COMMENTS_RESPONSE_2026-05-18.md` §6: Cook-Campbell, replication-crisis, construct-validity-beyond-Campbell-Fiske, sample-related (WEIRD, convenience), VR-specific (presence confound, hardware effects, novel-medium), theory-and-explanation (Lakatos, Kuhn, Orne, Rosenthal).

| Sub-task | Owner | Notes |
|---|---|---|
| Content draft | CW | ~5,000 words |
| Green/yellow/red tagging draft | CW | First pass |
| Panel review of tagging | Mayo + Machery | UJ-F output |
| Final publication and HTML render | CW | After panel review |

**Owner**: CW. **Reason not to farm out**: academic-register prose; reference accuracy; consistency with the Cook-Campbell showcase already drafted as wireframe Surface 7b.

---

## The summary table

| Sprint | Owner | Weeks | Blocked on |
|---|---|---|---|
| UJ-A · Content drafts | CW | 1 | UJ-A2 + UJ-A3 wait on panel/DK |
| UJ-B · Wireframe + HTML renders | CW (+ Track-4 optional) | 1 | UJ-A |
| UJ-C · V7-Lite pipeline | **Codex** | 2 | UJ-A5 spec |
| UJ-D · Substitution skill | **Codex + AG** + CW (spec) | 2 | Panel input on refusal criteria |
| UJ-E · Short-list + article-viewer | **Codex + Track-4** | 1–2 | CW spec |
| UJ-F · VOI panel | CW + **8 external panelists** | 4 (round-trip) | DK approval of panel |
| UJ-G · Citation-graph MVP | **Codex + AG** + CW | 1–2 | Library choice |
| UJ-H · Methodological-pitfalls page | CW | 1 | Panel review of tagging |

**Direct answer to DK's question.** I can do all the design, content, wireframe, and panel-coordination work standalone — Sprints A, B, F, H, plus the specification documents for Sprints C, D, E. That is the natural CW lane and the work that benefits most from a single-author voice. The implementation-heavy sprints (C, D, E) and the corpus-wide extraction passes (D, G) should be farmed to Codex and AG respectively. Track-4 students should own the article-viewer integration in Sprint E because that page is their pedagogical exercise.

If I were given everything to do solo, the plan would still execute but the V7-Lite pipeline alone would consume two weeks of CW time that Codex would do in three days — a poor allocation given that Codex is sitting next to me on the blackboard architecture. The farming-out is not a delegation of authority; it is a placement of work where the natural lane lives.

---

## What I propose to do immediately (without further DK input)

Three unblocked items in Sprint UJ-A:
1. **UJ-A1** — lift the Cook & Campbell content out of the wireframe into a standalone markdown file (`160sp/ka_validities_showcase_content_2026-05-18.md`) so the surface has the same separation of content-source-of-truth that the VR-measurability page has.
2. **UJ-A4** — fuller substitution-skill spec doc for Codex (`docs/CODEX_SUBSTITUTION_SKILL_BUILD_SPEC_2026-05-18.md`), so Codex has the build prompt waiting when the panel returns on refusal criteria.
3. **UJ-A5** — V7-Lite spec doc for Codex (`docs/CODEX_V7_LITE_BUILD_SPEC_2026-05-18.md`), so the Path-B pipeline can be built in parallel with the Sprint-UJ-A content work.

I will continue to do these and update TASKS.md as each lands. If DK wants me to redirect — to begin UJ-B HTML renders sooner, to draft the methodological-pitfalls page (UJ-H) in advance of panel tagging review, or to switch to one of the unrelated workstreams (paper-quality build, anchor paper sidecars, the 22-decision-tree-node walkthrough) — say so and I will redirect.
