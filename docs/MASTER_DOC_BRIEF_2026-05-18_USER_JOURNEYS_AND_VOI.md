# Master Doc Brief: CW 2026-05-18 — User Journeys, VOI Operationalisation, V7-Lite, Substitution Skill

**MDB ID**: MDB-CW-2026-05-18-USER_JOURNEYS_AND_VOI
**Agent**: CW (Cowork)
**Date**: 2026-05-18
**Session Duration**: ~6 hours over two sessions (one continuation after compaction)
**Status**: FINAL
**Companion files (this session)**:
  - `docs/USER_JOURNEYS_THINKING_2026-05-17.md` (framing)
  - `docs/USER_JOURNEY_COMMENTS_RESPONSE_2026-05-18.md` (design response, 6,000 words, 38 refs)
  - `docs/VOI_OPERATIONALISATION_PANEL_CONTEXT_2026-05-17.md` (panel context with §9 capabilities appendix)
  - `docs/VOI_PANEL_SYNTHESIS_2026-05-18.md` (CW-simulated panel, 8 panelists × 700–900 words, synthesis)
  - `docs/V7_LITE_SPEC_2026-05-18.md` (build spec for Codex)
  - `docs/SUBSTITUTION_SKILL_SPEC_2026-05-18.md` (build spec for Codex + AG)
  - `docs/UJ_SPRINT_PLAN_2026-05-18.md` (8-sprint plan with owners)
  - `160sp/ka_week1_wireframe_2026-05-17.html` (888 → 1,229 lines through three revisions)
  - `160sp/ka_vr_measurability_content_2026-05-18.md` (Surface 6 source-of-truth, 3,160+ words)
  - `160sp/ka_validities_showcase_content_2026-05-18.md` (Surface 7b source-of-truth)

---

## Context & Motivation

### Problem Statement

The Knowledge Atlas website's Week-1 COGS 160 Fall student journey has been only loosely specified across multiple in-flight design documents. Three structural gaps were visible at session start: (1) the journey from DYK browser to per-topic page to evaluate-a-paper had been wireframed only as a sequence of screens, without the methodological reasoning the system actually has to do behind each surface; (2) Value of Information (VOI) — invoked in the wireframe and the architecture documents as a property the system would surface — had no operationalisation, despite being on the critical path for both 160 Fall students and researchers; (3) the substitution skill that turns "this paper used an outcome measure we cannot reproduce" into "here is a defensible substitute" was being assumed by the wireframe without any specification of how it would work. DK's review of an interim wireframe added a fourth structural gap: the Path-B case where a student wants to evaluate a paper not yet in the corpus, which the previous draft did not handle at all.

This session was therefore a *specification round* on the full user-journey architecture: produce the design documents, the panel context, the build specifications, and the wireframe revisions in a form that lets Codex and AG begin implementation work in the next sprint cycle, lets the Track-4 students design their article-viewer integration against a documented contract, and lets DK convene the methodology panel (or accept CW's internal simulation of it) with a complete set of questions and proposed answers.

### Why This Matters

The COGS 160 Fall course is the load-bearing pedagogical product of the Knowledge Atlas. Each student cohort produces a VR experiment design in seven to ten weeks; the system either supports them through the methodologically substantive decisions (topic admission, measure choice, validity self-checks, methodological-pitfalls awareness) or it does not. Until this session the website was a collection of layer-inspector pages — pages built around the system's data layers (theories, articles, mechanisms) rather than around the student's decisions. The user-journey work shifts the design centre to the decisions, and in doing so commits the system to *making* the methodological reasoning legible rather than just storing it.

The VOI operationalisation matters for a different reason: it commits the Knowledge Atlas to a methodological position on what counts as a high-value question, and that position will be cited as a research artefact of the system going forward. Doing this with eight published-position-grounded panelists (Pearl, Gelman, Thagard, Mayo, Machery, Buzsáki, Longino, Bergstrom) rather than by CW's unaided reasoning is the responsible move; the simulated synthesis is honest about what is and is not real panel input.

The V7-Lite and substitution-skill specifications matter because they unblock Codex's next sprint. Codex has been waiting for the Path-B ingest pipeline to be specified before building it; the substitution skill has been on the critical path for the same reason. Both specs are now in place, written against AG's V2 credence work (which provides the substrate) rather than as parallel data structures.

The session's work is on the critical path for the Fall 2026 cohort. If Codex and AG can build the V7-Lite + substitution-skill stack in the next ~3 weeks (per the timelines in the specs), and if the Track-4 students complete the article-viewer page on their own course timeline, the Week-1 surfaces will be operational by mid-summer in time for Fall onboarding.

---

## What Was Done

### 1. Concrete Deliverables

| File / Artifact | Type | Lines / Words | Description |
|---|---|---|---|
| `docs/USER_JOURNEYS_THINKING_2026-05-17.md` | NEW | ~3,500 words | First-task framing of user journeys. Distinguishes goal-driven journeys from layer-inspector pages. Five-question framework (for whom, entry, exit, decisions, waypoints). Five candidate journeys per user type. Identified three structural gaps as session deliverables. |
| `docs/USER_JOURNEY_COMMENTS_RESPONSE_2026-05-18.md` | NEW | ~6,000 words, 38 APA refs | Response to DK's six inline comments on the journey framing. Eight sections covering VR-measurability page design, substitution skill data schema, bibliography differentiation table, citation-graph exemplars (Connected Papers, ResearchRabbit, Scite, Open Knowledge Maps, OpenAlex), two-stage measure handling, methodological-pitfalls page outline. |
| `docs/VOI_OPERATIONALISATION_PANEL_CONTEXT_2026-05-17.md` | NEW | ~6,500 words including §9 capabilities appendix | Panel context. Six uses of VOI; ten distinct VOI targets each with article-finder query and deficiency-if-unaddressed; six cross-cutting concerns; eight panelists (Bergstrom added per DK 2026-05-18 directive); eleven questions; §9 capabilities appendix in five families enumerating what the system can already do. |
| `docs/VOI_PANEL_SYNTHESIS_2026-05-18.md` | NEW | ~8,500 words | CW-simulated synthesis based on each panelist's published work, labelled clearly as not a real panel response. Per-panelist position sections (700–900 words each), four convergent positions, five contested positions for DK adjudication, CW's working operationalisation proposal. 18 references. |
| `docs/V7_LITE_SPEC_2026-05-18.md` | NEW | ~3,500 words | Build spec for Codex for the Path-B paper ingest pipeline. Seven synchronous stages, async full-V7 queue with two-lane priority, writes to AG V2 credence schema with `v7_lite_partial` flag, per-topic similarity threshold calibration protocol, five failure-mode handlers, five testing controls. |
| `docs/SUBSTITUTION_SKILL_SPEC_2026-05-18.md` | NEW | ~3,500 words | Build spec for Codex + AG for the engine driving Surfaces 4 and 4b. Three-table substitution graph with jingle-jangle proliferation warnings per Machery, corpus-wide extraction prompt for AG (1,428 papers, multi-LLM independent), admit-mode and choice-mode API contracts, refusal criteria from Mayo+Machery synthesis positions, confidence display per Pearl+Gelman+Bergstrom convergent position. |
| `docs/UJ_SPRINT_PLAN_2026-05-18.md` | NEW | ~2,200 words | Eight-sprint plan with owners. CW lane (~two-thirds: content, wireframes, panel coordination); Codex lane (V7-Lite pipeline, citation-graph front-end, short-list persistence); AG lane (corpus-wide extraction passes); Track-4 lane (article-viewer integration as their pedagogical exercise). Direct answer to DK's "can you do them all" question. |
| `160sp/ka_week1_wireframe_2026-05-17.html` | NEW then revised | 888 → 1,229 lines | Paper-fidelity wireframe of Week-1 journey. Nine surfaces in single HTML doc. Three revision rounds: initial nine-surface mock, Surface 4b added for choice-mode (UJ-5), DK 2026-05-18 review revisions (DYK CTAs renamed and expanded, Surface 3 short-list + hot anchor-paper links, Surface 4 two-path branching with V7-Lite, Cook & Campbell Surface 7b). |
| `160sp/ka_vr_measurability_content_2026-05-18.md` | NEW then revised | ~3,160 words | Source-of-truth for Surface 6. Four positive families (F1 headset traces, F2 task-embedded performance with IAT / Q-sort / adaptive-preference sub-types per DK 2026-05-18, F3 self-report, F4 physiology with confirmed/maybe/request hardware tiers), five exclusions (X1–X5), substitution principle, three-condition unpacking of "VR-tractable", quick-reference table with short codes for substitution-skill consumption. 17 APA refs. |
| `160sp/ka_validities_showcase_content_2026-05-18.md` | NEW | ~2,800 words | Source-of-truth for Surface 7b. Four validities each with central question, threat list per Shadish/Cook/Campbell 2002, VR-project advisory. Worked example of ceiling-height contestation as construct-and-internal-validity puzzle. 8 APA refs. |
| `TASKS.md` | MODIFIED | +18 task rows added across the session | UJ-1 through UJ-15 plus UJ-A1, UJ-A4, UJ-A5, UJ-A6, UJ-F-sim. Of these, 9 completed in-session; 6 unblocked for next session; 3 awaiting DK input; 5 awaiting panel input. |

### 2. How It Works

The deliverables are mutually interlocking but separable. The architecture they jointly imply:

**At the user's session start (Week 1, COGS 160 Fall).** The student lands on `ka_student_setup.html` (the track picker) and selects the 160-Fall track. The Week-1 landing surface (Surface 1 of the wireframe) presents three primary CTAs: DYK browser (Surface 2), Evaluate-a-paper-for-VR (Surface 4), and VR-measurability explainer (Surface 6).

**The DYK browser (Surface 2).** Cards drawn from the existing DYK pipeline, each with a VR-tractability flag, a VOI badge, and three or four CTAs (Explore this topic, Add to short-list, Find related papers, optionally Why-is-this-contested for the contested cards). Filters narrow by topic family and VR-tractability.

**The per-topic page (Surface 3).** A logged-in surface (Shibboleth Fall 2026, local profile until then). Carries a meta-review paragraph, an anchor-paper table with hot links to the article viewer (the Track-4 student-designed page), and a short-list card showing the student's persistent collection. The student can pick papers as anchors *or* add them to their short-list for later, supporting the deferred-commitment workflow DK asked for.

**The evaluate-a-paper surface (Surfaces 4 and 4b).** Two-path architecture: Path A for papers already in the corpus (immediate evaluation against cached fingerprint), Path B for uploaded papers (triggers the V7-Lite pipeline). V7-Lite returns a structured evaluation within ~5 minutes that maps the paper's IV/DV against the VR-measurability short codes and computes a four-target conditional VOI; the full V7 pipeline lands hours later and incrementally upgrades the article-viewer page. Surface 4b is the choice-mode follow-on, invoked in Week 3, that lays out candidate measures side-by-side with hardware/time/strengths/weaknesses.

**The VOI panel (Surface 5).** Embedded in Surfaces 2, 3, 4. Shows the topic's 10-dimensional VOI target-vector as a small grid with categorical (high/medium/low) plus rationale plus article-finder query per cell. For COGS 160 students, the four feasibility-relevant targets (1 better stimuli, 2 better measures, 4 deconfounding, 8 replication) are shown by default with the other six behind a Show-advanced-VOI affordance. For researchers, the full vector plus the dual information-theoretic summary (coverage-gap subtotal, methodological-upgrade subtotal) is surfaced at the top.

**The VR-measurability explainer (Surface 6).** Source-of-truth markdown rendered to HTML. The student reads this once in Week 1 and refers back to it when committing to a measure. The same markdown's quick-reference table serves as the substitution skill's machine-readable lookup.

**The methodological-pitfalls explainer (Surface 7) and Cook & Campbell showcase (Surface 7b).** Surface 7b is dedicated to the four-validities taxonomy; Surface 7 is the broader pitfalls explainer that covers replication-crisis pitfalls, construct-validity-beyond-Campbell-Fiske, sample-related issues, VR-specific issues (presence confound, hardware effects, novel-medium), and theory-and-explanation pitfalls (Lakatos, Kuhn, Orne, Rosenthal). The two surfaces cross-link.

**The substitution skill.** Three-table graph stored as `substitution_graph.db` alongside `ae.db`. Constructs, measures, construct-measure links — the last carrying construct-validity, field-acceptance count, severity-average from AG V2, and citation count. AG populates the tables via a multi-LLM extraction pass over the corpus; CW reviews. The skill is invoked from Surface 4 (admit-mode, binary), Surface 4b (choice-mode, ranked), and from the article viewer (small panel at the foot showing per-DV verdicts).

**The V7-Lite pipeline.** Synchronous-return subset of the existing V7 pipeline; reuses the adaptive paper-type classifier, the corpus embedding store, the existing V7 IV/DV extraction stage, and the existing V7 methods-extraction stage. Adds new stages: VR-suitability mapper (from DV short code to substitution-skill query), conditional-VOI computation (four targets), LLM recommendation synthesis. Writes to AG's V2 credence schema with a `v7_lite_partial` flag; the full V7 pipeline updates the same row asynchronously.

**The VOI computation.** Built against AG's V2 credence schema (the strongest convergence in the panel synthesis). Per paper: a target-vector of length 10 with each entry derived from V2 fields (severity, warrant-richness, defeat-status, scope, mechanism-chain weak-link records, theory entrenchment). Per topic: aggregation of per-paper target-vectors. Per question: positioning of the question on the same target-vector combined with the topic-level vector. Profile-not-score is the convergent panel position; no composite scalar is exposed in v1.

### 3. Testing & Validation

The deliverables in this session are *specifications and content* rather than executable code, so the testing protocol is review-based rather than test-suite-based. The specs themselves contain testing protocols for the downstream implementation: V7-Lite has five testing controls (in-corpus positive, out-of-corpus positive, out-of-corpus admit, replication test, adversarial threshold test); the substitution skill has five (trivial admit, standard substitution, refusal, choice-mode top-rank stability, jangle warning). Codex and AG will implement those tests as part of the build.

The content deliverables (the VR-measurability page, the Cook & Campbell showcase, the design response, the panel synthesis) have been internally consistency-checked but should receive DK's editorial review before they ship to students. The wireframe has been HTML-validated for tag balance through the Python HTMLParser self-check after each major edit (no unclosed tags, no mismatched closes across all three revisions).

The CW-simulated panel synthesis is honest about its provenance. Where CW's confidence in a panelist's attributed position is HIGH (Pearl on causality, Mayo on severity, Bergstrom on bibliometric information theory, Gelman on Bayesian workflow), the synthesis says so. Where the confidence is MEDIUM or LOW (Buzsáki on UI/aggregation, Longino on operationalisation specifics, Machery on aggregation), the synthesis says so. The synthesis explicitly does not close the real-panel sprint (UJ-F).

---

## Design Decisions

### Decision D-UJ-1: Single-document wireframe vs multi-page mockup

- **Context**: At session start, the question was whether to wireframe each of the nine Week-1 surfaces as its own page or as sections of a single document. The decision shapes how DK reviews the design.
- **Alternatives Considered**:
  - Option A — Multi-page mockup: one HTML file per surface. Pro: closer to production structure; could be served as a true prototype. Con: nine files to keep in sync; navigation between them during review is friction; review-in-one-sitting becomes review-across-nine-tabs.
  - Option B — Single-document wireframe: nine surfaces as sections of one HTML file with internal anchors. Pro: review in one sitting; annotations and decisions stay in the same document; cross-references work as anchor links. Con: not directly a prototype; will not be served.
- **Rationale**: Option B. The wireframe is for DK review, not for production deployment; review ergonomics outweigh production-resemblance. The single-document approach made it easy to add Surface 4b (UJ-5) and Surface 7b (Cook & Campbell) in later passes without touching production HTML.
- **Risk Level**: LOW. Reversible if Codex needs split files for production; the markdown content sources are already split (VR-measurability page, Cook & Campbell content, etc.).
- **Dependencies**: None.
- **Panel Concerns**: None.

### Decision D-UJ-2: Add an eighth panelist (Bergstrom) for information-theoretic VOI

- **Context**: DK 2026-05-18 directive: "Panel: add an information expert eg computational librarian who might know all about information theory models of VOI."
- **Alternatives Considered**:
  - Option A — Loet Leydesdorff: pure informetrician; deep Shannon-entropy work in scientometrics. Pro: most directly information-theoretic. Con: less contemporary; less integrated with current science-of-science.
  - Option B — Jevin West: UW Information School; Eigenfactor co-author; science-of-science. Pro: combines library/information science with computational methods; publicly accessible. Con: lighter on pure information-theoretic VOI than Leydesdorff.
  - Option C — Tom Rainforth: Oxford; Bayesian experimental design / formal VOI. Pro: closest to pure VOI mathematics. Con: not a "computational librarian" in DK's framing; more decision-theoretic than information-theoretic.
  - Option D — Carl Bergstrom: UW Biology + iSchool affiliate; Eigenfactor; "Calling Bullshit". Pro: bridges information-theoretic citation-network measures with research-evaluation critique; publicly engaged. Con: not a librarian in the formal sense.
- **Rationale**: Option D (Bergstrom). Best fit for DK's framing ("computational librarian who might know all about information theory models of VOI") and most active in research-evaluation discourse. Alternates listed in the panel doc (West, Leydesdorff, Rainforth) so DK can substitute if he prefers a different fit.
- **Risk Level**: LOW. Panel composition is for DK approval; any of the four candidates would produce useful input.
- **Dependencies**: None.
- **Panel Concerns**: N/A (the question is about panel composition).

### Decision D-UJ-3: Two-path architecture on Surface 4 (in-corpus vs uploaded)

- **Context**: DK 2026-05-18 review: "Evaluate a paper: should allow student to test if we have it in the corpus, if not they must upload and we test if it is in the topic set or close enough."
- **Alternatives Considered**:
  - Option A — Refuse out-of-corpus papers; require students to bring corpus papers only. Pro: simplest implementation; no pipeline work needed. Con: students bring papers from coffee-shop discoveries, professors' suggestions, recent literature; rejecting all is pedagogically wrong.
  - Option B — Accept any paper, run full V7 pipeline before evaluation. Pro: complete fingerprint available. Con: full V7 takes hours; cannot return within an interactive session.
  - Option C — Two-path: in-corpus uses cached fingerprint (Path A); uploaded papers run V7-Lite synchronously and queue full V7 asynchronously (Path B). Pro: interactive return time; eventually-consistent full fingerprint. Con: requires building V7-Lite; introduces partial-record schema.
- **Rationale**: Option C. The interactive-return requirement is non-negotiable for student onboarding; the partial-record schema is a small addition (`v7_lite_partial` flag on AG's V2 schema). V7-Lite is implementable as a subset of existing V7 stages plus three new modules (VR-suitability mapper, conditional VOI, recommendation synthesis).
- **Risk Level**: MEDIUM. The risk is that V7-Lite produces a substantially less complete picture than full V7 and that students make decisions on the partial picture that they would not make on the full picture. Mitigation: the partial-record schema makes the partiality visible in the UI ("Full ingest in progress" banner).
- **Dependencies**: Codex implementation of V7-Lite (UJ-A5 spec); AG's V2 credence schema (already in place).
- **Panel Concerns**: Pearl on whether the IV/DV extraction adequately captures causal structure; Mayo on whether the severity field can be computed in the V7-Lite subset (CW deferred — severity is in AG's V2 schema but populated by the full pipeline).

### Decision D-UJ-4: 10-dimensional VOI target-vector with profile display

- **Context**: The aggregation question (panel Question 3) and the score-vs-flag-vs-profile question (Question 4). Six of eight simulated panelists favoured profile over composite score; the contested question is whether a partial composite (information-theoretic dual subtotals per Bergstrom) is appropriate.
- **Alternatives Considered**:
  - Option A — Single composite VOI score per topic. Pro: simple UI; one number to display. Con: hides the structural distinctions Pearl, Thagard, Mayo, and Longino vehemently want exposed.
  - Option B — 10-dimensional pure profile (one cell per target, no aggregation). Pro: maximally informative; preserves every panelist's structural concerns. Con: UI complexity; risk that the user is overwhelmed.
  - Option C — 10-dimensional profile with two derived information-theoretic summaries (coverage-gap subtotal, methodological-upgrade subtotal) per Bergstrom. Pro: profile fidelity preserved; subtotals give navigable summary. Con: the subtotals are themselves a methodological commitment that not all panelists endorse.
- **Rationale**: Option C. The Bergstrom-style dual subtotal is honest about its methodological commitment (it is presented as a *partial* composite, not a unified score), it gives the UI a navigable summary for the researcher view, and it does not foreclose the profile-fidelity display.
- **Risk Level**: MEDIUM. The information-theoretic decomposition (Question 11 in the panel context) is genuinely contested; Mayo would resist on principle, Longino would resist on values-neutrality grounds. Mitigation: the dual subtotal is presented as a presentation device, not as deep semantics, and is exposed only on the researcher view (not the student view).
- **Dependencies**: AG's V2 credence schema for the per-paper substrate; substitution skill spec for the per-paper-to-per-target mapping.
- **Panel Concerns**: Bergstrom (endorses the dual); Mayo (resists information-theoretic framing); Longino (resists Shannon-neutrality assumption).

### Decision D-UJ-5: CW-simulated panel synthesis as design input

- **Context**: DK 2026-05-18: "Have you run the panel yet to review your planned decisions - including the VOI stuff?" Real panel responses would require sending briefing letters and waiting 2 weeks; the session needed an interim mechanism for the panelists' positions to inform the V7-Lite and substitution-skill specs.
- **Alternatives Considered**:
  - Option A — Wait for the real panel. Pro: authoritative input. Con: 2-week delay before Codex can start the implementation work; blocks Sprints UJ-C, UJ-D, UJ-H.
  - Option B — CW writes the specs without panel input. Pro: fastest. Con: design choices on refusal criteria, confidence display, aggregation are exactly the kinds of decisions the panel was convened to advise on.
  - Option C — CW-simulates the panel based on each panelist's published positions, clearly labels the simulation, uses it as design input. Pro: design choices have published-position grounding; honest about provenance; unblocks Codex. Con: the simulated positions are CW's attribution and may misrepresent the panelist's actual position.
- **Rationale**: Option C with explicit labelling. The panelists were chosen for the well-articulated nature of their published positions; their likely responses on the questions are recoverable from their writing. The simulation is labelled as such in every relevant document. The real-panel sprint (UJ-F) is *not* closed by the simulation; the real panel may still revise.
- **Risk Level**: MEDIUM. The risk is that the simulation misrepresents a panelist's position and that the design built on the misrepresentation propagates the error. Mitigation: explicit confidence labels per panelist (HIGH/MEDIUM/LOW); explicit statement that the simulation does not close the real-panel sprint; the simulation flags contested positions for DK adjudication rather than treating them as settled.
- **Dependencies**: None for the simulation itself; downstream specs reference the synthesis explicitly.
- **Panel Concerns**: All eight panelists will see the simulation when the real panel is convened; they will get to revise their attributed positions.

### Decision D-UJ-6: Sprint allocation between CW, Codex, AG, Track-4

- **Context**: DK 2026-05-18: "Can you do them all? Any reason to farm them out?"
- **Alternatives Considered**:
  - Option A — CW does everything. Pro: maximum consistency. Con: CW does not own the V7 pipeline; learning the codebase would consume time Codex would not spend; the article-viewer page is pedagogically a Track-4 exercise.
  - Option B — Distribute strictly by domain: CW for design/content; Codex for pipeline; AG for corpus extraction; Track-4 for student-facing pages they are designing. Pro: each worker in their natural lane. Con: more synchronisation overhead.
  - Option C — Hybrid: CW writes specs for the farmed-out work, then Codex/AG implement, then CW reviews. Pro: design coherence preserved through the spec layer; implementation efficient. Con: requires CW spec discipline (the V7-Lite spec and substitution-skill spec are the proof of concept).
- **Rationale**: Option C. CW retains the design layer (specs, content, wireframe, panel coordination) and writes implementation prompts for the rest. ~two-thirds of the work is CW's lane; ~one-third is farmed out with CW specs.
- **Risk Level**: LOW. Reversible per sprint; if Codex's V7-Lite build runs into trouble, CW can be pulled in.
- **Dependencies**: None.
- **Panel Concerns**: N/A.

---

## Epistemic Implications

### 1. Impact on the Web of Belief

The Knowledge Atlas's web-of-belief structure, as instantiated in ae.db's V2 credence schema (per AG's 2026-05-18 handoff), gains a UI surface in this session's work. Before this session, the V2 schema's three-credence display, warrant-richness counts, severity field, scope metadata, and weak-mechanism-link records were a back-end advance with no front-end surface. The Surface 5 VOI panel, the substitution-skill confidence display, and the article-viewer evaluation panel will now read these fields and surface them to students and researchers. The substantive epistemic shift is that the system moves from displaying *credence values* to displaying *credence-with-warrant-structure* — the user sees not only how strong the evidence is but *how* the evidence is strong (mechanism, entrenchment, meta-analytic, confounding warrants).

The 670 weak-mechanism-link beliefs identified in AG's V2 work become high-VOI candidates on Surface 5 (VOI Target 5: weak links in mechanism chains). The student selecting a topic will see, on the topic page, which of its mechanism links are well-supported and which are stubs; the researcher will see the same plus the list of papers establishing each link. This is an epistemically substantive surfacing — previously the stubs were invisible.

### 2. Impact on the Methodological Frame of the System

The system commits, in this session, to a methodological position on what counts as a high-value question. Per the simulated panel synthesis, that position is: (a) profile not score; (b) AG's V2 credence schema as substrate; (c) structured rather than free-text finder queries; (d) severity at the centre. These four convergent positions will be cited as methodological commitments of the Knowledge Atlas going forward and should be defensible against academic critique. The CW-simulated panelists provide one layer of defensibility (positions grounded in published work); the real-panel sprint (UJ-F) provides the second layer when it runs.

The Cook & Campbell four-validities showcase commits the system to a methodological vocabulary that pre-dates the replication crisis but interoperates with it. The broader methodological-pitfalls page (Surface 7, UJ-H, content draft pending) will extend the vocabulary to cover the replication-crisis pitfalls explicitly. The two surfaces' interoperation is by design: Cook & Campbell give the student a classical frame for thinking about validity; the broader page adds the contemporary frame for thinking about the systematic patterns that compromise it.

### 3. Impact on Cross-Repository Coupling

The session establishes a tighter coupling between Knowledge_Atlas (the website) and Article_Eater_PostQuinean_v1_recovery (the pipeline). The V7-Lite spec, the substitution-skill spec, the VOI computation, and the VR-measurability short-code schema all assume AG's V2 credence work in `ae.db` is the substrate. This is the right coupling — Article_Eater is the source-of-truth for the corpus's structured data; Knowledge_Atlas is the rendering layer — but it imposes a contract: Article_Eater changes to the V2 schema need to be coordinated with Knowledge_Atlas renderers.

The new bridging document (UJ-A6, planned for next session) will make the contract explicit. The substitution skill's `substitution_graph.db` is proposed as a new database; Codex may choose to merge it into `ae.db` if that turns out simpler. Either way, the coupling is named and documented.

### 4. Impact on Pedagogical Strategy

The Week-1 student journey, after this session, has its decision points named, its methodological backbone specified, its measurement vocabulary defined, and its pitfalls catalogued. The Track-4 students who are designing the article-viewer page now have a documented URL contract and a documented set of fields the viewer needs to render. The substitution skill commits the course to a pedagogy in which students are exposed to the field's psychometric record rather than insulated from it (Machery's pedagogical position). The methodological-pitfalls page commits the course to exposing students to the replication-crisis literature (Mayo's and Machery's combined position).

These commitments are not yet locked; the real panel may revise. But the simulation gives the course enough specification to run while the real panel reviews.

---

## Connections to the Existing Master Document

### Sections this work updates or extends

- **§121.4 (Research Queue) and §122.1–§122.3 (PNU overview + selection tree)** — Track 2 article-finder material: the article-finder coupling in the VOI work (every VOI pointer surfaces an article-finder query) extends this material. The "structured rather than free-text" convergent panel position is a new methodological commitment that should be added to §121.4.

- **§122.4 (Mechanism Profiles) and §122.8 (Temporal Dynamics)** — Track 3 VR material: the substitution skill operates over the construct-to-measure relations these sections describe. The VR-measurability page is the student-facing rendering of the constraints implicit in §122.4 and §122.8.

- **§122.6 (12 SC-PNU prose conditions) and §122.13 (2026-04-17 revision)** — Track 4 UX material: the user-journey work is the Track-4-facing layer that consumes the prose conditions and the readability targets.

### Sections this work would benefit from

- Master doc material on the Web-of-Belief structure interacts with the VOI substrate. The synthesis's convergent position that AG's V2 schema is the substrate should be incorporated into the master doc's discussion of the credence engine.

- Master doc material on the Quinean coherentist epistemology interacts with Thagard's coherence framing of VOI. CW recommends a small cross-reference paragraph in the master doc's §38 (or wherever Thagard's framework is introduced) noting that coherence-disruption potential is one of the eight panel positions on VOI operationalisation.

### Sections this work does not touch

The Article_Eater extraction pipeline (§§121.5–121.9), the success conditions (§§123–125), and the methodological reflexes of the Web of Belief (§§126–128) are unchanged by this session's work.

---

## Risks and Open Items Carried Forward

### Open items requiring DK input

1. **Panel composition approval.** DK has indicated approval (2026-05-18) of the eight-panelist composition; the per-panelist briefing letters (UJ-7) can now be drafted.
2. **The contested-position adjudication.** The five contested positions from the simulated panel synthesis (composite vs profile, severity vs coherence, info-theoretic decomposition as framework vs presentation, student-vs-researcher projection, temporal decay) need DK adjudication or will be revised when the real panel returns.
3. **The 28-commit push backlog (UJ-8).** Knowledge_Atlas master is 28 commits ahead of origin; origin is 2 commits ahead of local. DK needs to authorise the reconciliation push (pull-rebase, then push).

### Open items requiring panel input (real panel)

1. Refusal criteria for the substitution skill — Mayo and Machery's positions used in the simulation; real-panel revision may change.
2. Confidence display details — Pearl, Gelman, Bergstrom's convergent position used; real-panel revision may change.
3. Green/yellow/red tagging on the methodological-pitfalls page — content unblocked but tagging awaits Mayo and Machery review.
4. Per-topic similarity threshold calibration for V7-Lite — Codex will run the calibration; DK reviews the calibrated values.

### Risks to monitor

1. **V7-Lite partial-record visibility.** Students seeing a partial fingerprint may make decisions they would not make on the full picture. Mitigation: explicit "Full ingest in progress" banner; full V7 lands within 2 hours.
2. **Substitution skill hallucination.** Generative-only systems hallucinate substitutions; the design uses generative LLM only for the explanation layer over a curated retrieval. Mitigation: explicit refusal criteria; corpus-grounded knowledge base only.
3. **Real-panel revision.** The simulation may misrepresent a panelist's position; downstream design built on the misrepresentation propagates. Mitigation: per-panelist confidence labels; real panel still convenes.

---

## Status at session end

Eleven commits to Knowledge_Atlas master. The repo is ready to hand off to Codex (V7-Lite spec) and AG (substitution-skill corpus-extraction prompt). The simulated panel synthesis is sufficient for the next sprint cycle to proceed without waiting for the real panel; the real panel remains scheduled (Sprint UJ-F).

The unblocked CW-doable items remaining: UJ-1b (HTML render of VR-measurability), UJ-3 (differentiation-table mockup), UJ-A6 (AG-bridge reference doc), UJ-H content draft (~5,000 words methodological-pitfalls page).

The blocked items: UJ-7 (panel briefing letters, gated on DK's approval signal); UJ-D substitution-skill build (gated on Codex implementation per the spec).

---

*End of Master Doc Brief. CW (future session) integrates into `Article_Eater_PostQuinean_v1_recovery/docs/MASTER_DOC_CMR_ASSEMBLED.md` per the MASTER_DOC_UPDATE_PROTOCOL contract; the mirror in this repo refreshes from the AE-side authoritative copy.*
