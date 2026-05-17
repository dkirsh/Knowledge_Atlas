# Making Sense of User Journeys on the Knowledge Atlas — A Framing

**Date**: 2026-05-17
**Author**: CW for DK deliberation
**Status**: First-task framing document — to be reviewed before any implementation prompt is written
**Scope**: How to think about user journeys for the two priority user types (COGS 160 Fall students and researchers), with attention to the shared affordances (topic selection, bibliography building, alternative measures, VOI pointers) and the differences (researchers want neural underpinnings; the 160 Fall course runs as a sequenced process; researchers move non-linearly).

---

## 1. What already exists on this site, and what each piece is actually doing

Before I propose any new framework, three orienting facts.

**First**, there is a substantial body of journey-related work in the repository. Eight design documents under `docs/` carry "journey" in their name; a ninth — the Track 4 student deliverable at `160sp/Docs/user_journey_design.docx` — is a serious essay on journey principles by students in your GUI design track; sixteen HTML pages under `ka_journey_*.html` are live; the audit at `docs/USER_JOURNEY_AUDIT_2026-04-01.md` enumerates which journeys are complete and which are broken; the architecture at `docs/USER_TYPE_HOME_PAGES_AND_JOURNEY_ARCHITECTURE_2026-04-03.md` sketches per-user-type home pages with governing questions, topic checklists, and 2–4 journey entry points; the inventory at `docs/COMPLICATED_PAGES_JOURNEYS_AND_PANELS_2026-04-19.md` lists roughly 27 candidate layer surfaces. The April 20 ruthless brief plus AG's verification cleared thirteen P0/P1 fixes on the journey-page infrastructure.

**Second**, the sixteen live `ka_journey_*.html` pages are not user journeys in the goal-driven sense the Track 4 students articulated. They are *layer inspectors with a pedagogical scaffold*: each page introduces one layer of the Atlas (EN, BN, argumentation, interpretation, evidence, gaps, mechanism, neuro, fronts, ontology, QA, theory, topic-inspector, plus the three AF — Article Finder — pages) and walks through a standard pattern of *spec, naive solution, critique*. They teach the reader what each layer *is* and what its naive implementations get wrong. They are not goal-driven paths from a user's purpose to a user's outcome. The naming is unfortunate; the work is valuable, but the inheritance of the word "journey" has been doing some hidden work in the design that needs to be unwound.

**Third**, the Track 4 students' design document at `160sp/Docs/user_journey_design.docx` already supplies the right framework. They distinguish navigation (a map of what exists) from journeys (paths through what matters, selected, sequenced, and paced for a specific user with a specific goal). They name the five structural elements of a well-formed journey: entry condition, decision points, progressive disclosure, waypoints, exit condition. They name two risks specific to multi-user sites: cross-user contamination and the shared-information-divergent-needs problem. Their vocabulary is sound; I shall use it.

I take this as the starting framing.

## 2. Two senses of "journey" coexist on the site, and they should be kept distinct

Right now the site is using one word for two different objects. The first object is the *layer inspector* (the sixteen `ka_journey_*.html` pages) — pedagogical surfaces, each introducing one layer of the architecture with a spec / naive / critique scaffold. The second object is the *user journey* in the Track 4 sense — a goal-driven, sequenced, customised path from where a user is to what they came for.

These are different artefacts. They need different names, different design criteria, different metrics of success, and different surfaces in the navigation.

A clean linguistic move would be to call the existing sixteen pages **layer pages** (or **layer-inspector pages**) and to reserve **journey** for the goal-driven Track 4 sense. The audit doc and the architecture doc effectively did this — the architecture doc names "journey choices" as questions the user might be trying to answer ("Does the evidence support my prediction?", "Can I find ten experimental articles on my assigned topic?") — but the current site implementation conflates the two. The conflation makes it hard to design either kind well.

For the rest of this document, *journey* means the goal-driven Track 4 sense. The layer pages are a separate kind of artefact and I shall name them as such.

## 3. A working framework: five questions per journey

Each goal-driven user journey on the Atlas should be specified by answering five questions, in order. The first three are about the journey as an object; the last two are about how the journey is wired into the site.

1. **For whom?** Which user type and which sub-profile within that user type. (A 160 Fall student in Week 1 has a different journey than a 160 Fall student in Week 4. A first-year graduate researcher with a hypothesis has a different journey than a tenured researcher with a corpus of their own.)

2. **From what entry state?** What the user has when they arrive: a vague interest, a paper they read, a topic name, a hypothesis, a partly-formed bibliography, a measure they suspect is inadequate, a critique of their own draft. The entry state is the starting point of the path.

3. **To what exit state?** What the user should have when they finish: a defended topic with a one-paragraph rationale, a starter bibliography of N papers with annotations, a confirmed or replaced measure, a hypothesis with named mechanism and falsifiability conditions, a list of VOI-ranked open questions in their domain. The exit state is the success condition.

4. **What decisions, and which ones can the system make on the user's behalf?** Track 4's design document is sharp on this: every decision the user must make adds cognitive load and risk of abandonment. The system should default what it can default (based on what it already knows about the user — user type, prior visits, current course week) and ask only the decisions whose two branches are genuinely different in a way that matters to the user.

5. **What waypoints, and how does progress get visible?** The user should be able to answer where am I, how did I get here, what happens next at every step. For the 160 Fall student, the waypoints align with course weeks. For the researcher, the waypoints are intellectual milestones (topic claimed, bibliography assembled, measures confirmed, hypothesis articulated).

A journey design is incomplete if any of these five is missing. The Track 4 students were right.

## 4. The two priority user types, side by side

You named two priority user types: COGS 160 Fall students and researchers. They share five goals (find a topic, build a bibliography, find alternative measures, evaluate evidence, identify high-VOI questions) but differ in how they should be served.

The 160 Fall course runs as a 7.5-week sequenced process. The schedule at `fall160_schedule.html` lays it out: Week 1 is *orientation, research landscape, topic selection*; Week 2 is *theory, hypothesis, what are you actually testing*; Week 3 is *VR stimulus specification*; Week 4 is *VR scene assembly*; subsequent weeks cover execution and analysis. The journey of a 160 Fall student is therefore largely *linear with checkpoints*. The system can know what week the student is in and tailor the surface accordingly. The student's tolerance for friction is low: they need to finish each week's deliverable, the AI assistance can and should be generous, and the output is a checklist-shaped artefact.

A researcher's journey is largely *non-linear and tree-shaped*. They arrive with a hypothesis, a paper they read, or a vague interest in a region of the literature; they make many local decisions in any order; their tolerance for friction is medium (they are exploring); their output is an annotated working note for themselves. AI assistance should be available but not insistent — the researcher is the expert and the system is the librarian.

The five shared goals look different in each register.

*Find a topic.* For the 160 Fall student this happens in Week 1 of the course; the system can offer a curated subset of topics that fit the VR-experiment constraint of the course (the student cannot study a topic that requires fMRI or longitudinal follow-up; the system should default away from those even if the student requests them). The output is a defended topic with a paragraph of rationale. For the researcher, find-a-topic is open-ended exploration of the topic crosswalk, the gaps map, the contradictions dashboard, and the VOI panel; the output is a topic on which they intend to write a paper or grant.

*Build a bibliography.* For the 160 Fall student this happens across Weeks 1–2; the bibliography is starter-sized (maybe 8–12 papers); the system should rank highly the papers that the course's earlier cohorts have used productively. For the researcher, the bibliography may run to 50–200 papers; the system should expose its citation graph, its replication structure, its theoretical diversity, and its methodological span.

*Find alternative measures.* For the 160 Fall student this happens when they get to Week 3 (VR stimulus specification) and discover that their original outcome measure is impossible to operationalise in VR. The system needs to know the constraints of VR and offer plausible substitutions with their psychometric histories. For the researcher, find-alternative-measures is a methodological move that runs across the bibliography — when a measure has known reliability problems, or known cultural specificity, or known floor/ceiling effects, the researcher needs the alternatives with their trade-offs.

*Evaluate evidence quality.* For the 160 Fall student this is paired with the experimental-quality fingerprint work — the student should be able to look at a paper and see whether its design clears Cook-and-Campbell's threats. For the researcher, evidence quality is finer-grained: they want the construct-validity verdict, the WEIRD-sample flag, the preregistration status, the replication record, and the rhetorical-flag list.

*Identify high-VOI questions.* This is the most under-served of the five right now, and arguably the most important. Both user types care about VOI. For the 160 Fall student, VOI pointers should help them avoid choosing a topic where the literature is saturated (low marginal value of another study) or where the methodological gap is too large for a 7-week project. For the researcher, VOI pointers should rank the open questions in their domain by the expected reduction in uncertainty that a well-designed study would produce. The architecture doc lists a "VOI Map" card on the researcher home page; the surface that backs that card is not yet built.

## 5. The candidate journey set, per user type

A first pass at the journeys each user type should be able to choose. For each: name, entry state, exit state, the decisions the system should default, the decisions the user must make. I expect this list to change as the design matures; treat it as a working enumeration.

### 5.1 COGS 160 Fall student — five journeys aligned with course weeks

1. **Week 1: Find your topic.** Entry: nothing. Exit: a defended topic with one-paragraph rationale and a starter list of ~6 anchor papers. Default: subset topics to those VR-tractable in seven weeks. User chooses: topic from a curated list of 12–20.

2. **Week 2: Find your hypothesis.** Entry: a topic. Exit: a falsifiable hypothesis with named mechanism, predicted direction, and one falsifying observation. Default: surface the theoretical frameworks most associated with the chosen topic. User chooses: which theoretical framework anchors their hypothesis; what falsifies it.

3. **Week 3: Specify your VR conditions.** Entry: a hypothesis. Exit: two named experimental conditions (the contrast), what varies, what is held constant. Default: surface the VR base-scenes the system has built or templated; surface the measures that have been operationalised in VR. User chooses: their two conditions; their primary outcome measure.

4. **Week 4: Build your scenes.** Entry: a specification. Exit: two A-Frame scenes that render in the browser. Default: A-Frame templates for the chosen base-scenes. User chooses: scene parameters within the templates.

5. **Weeks 5–7: Run, analyse, write.** Entry: a built experiment. Exit: a defensible report. Default: power calculations, analysis plan templates, write-up scaffolds.

The crucial property of the 160 Fall student journey is that it is *known in advance* and *aligned with the course week*. The system can read the calendar and know what the student should be doing now. The user's choice points are the substantive ones (which topic, which hypothesis, which conditions); the system absorbs the procedural decisions.

### 5.2 Researcher — five journeys, non-linear, decision-driven

1. **Find a topic for a new paper or grant.** Entry: a region of interest, often loosely defined. Exit: a topic the researcher commits to. The journey is exploratory across the topic crosswalk, the contradictions dashboard, the gaps map, and the VOI panel; the system should surface neural-underpinnings findings prominently because researchers often have a mechanism intuition driving topic choice.

2. **Build a bibliography for a topic I have.** Entry: a topic. Exit: an annotated bibliography of N papers. The system should expose citation structure, theoretical diversity, methodological span, replication record, and WEIRD-sample flags. The researcher decides which papers to include; the system suggests pruning candidates and additions.

3. **Find alternative measures.** Entry: a measure I am using or considering. Exit: a ranked list of alternatives with trade-offs. The system uses the instrument registry to surface psychometric histories, known reliability, known cultural specificity, and operational compatibility (laboratory vs field; brief vs sustained; self-report vs behavioural).

4. **Evaluate the evidence around one claim.** Entry: a claim, often phrased as a hypothesis. Exit: a summary of where the evidence stands, with named contestants, replication record, mechanism candidates, and VOI for the unresolved sub-questions. This is the most direct fit with the existing paper-quality fingerprint work — the fingerprint of each paper feeds the summary.

5. **Find high-VOI questions in my domain.** Entry: a domain (or my checked-topics filter). Exit: a VOI-ranked list of open questions, each with the studies that would resolve it, the population it would generalise to, and the methodological feasibility. This is the most directly underbuilt journey on the current site and arguably the most valuable for a researcher choosing where to put their next study.

The researcher journeys are not week-aligned. A researcher chooses among them, switches between them mid-flow, and often combines them. The site should treat them as five entry points from a researcher home page that the researcher can return to and recombine.

## 6. Shared affordances that cut across journeys

Some affordances are not journey-specific; they need to be present on every journey-relevant page for both user types.

*VOI pointers.* You named this as something both user types care about. The honest current state is that VOI is mentioned in the architecture doc and in the topics literature, but it is not yet a visible affordance anywhere on the site. A first deliverable on the journey work should be a *VOI panel component* — a small card or sidebar element that ranks the open VOI-worthy questions for the user's current topic. The panel can appear on the topic page, on the article page, on the journey landing page for both user types. The same data backs it; the framing differs slightly per user type (the student sees it as topic-feasibility guidance, the researcher sees it as where-to-put-the-next-study guidance).

*Topic-and-measure crosswalk.* The five topic-page variants we already have render the underlying 102×18×9 crosswalk in five different ways. For both user types, a journey that touches topic-and-measure choice should land on one of those variants by default — the public-visitor variant for the researcher, the student variant for the 160 Fall student — with the option to switch.

*Neural underpinnings panel.* You said researchers want this. The architecture doc names a "Neural Underpinnings" card on the researcher home page. The underlying data structure (the PNU registry) exists; the panel surface is partly built (`ka_neural.html`, the PNU pages). A first-class affordance for the researcher journeys is a *neural-underpinnings panel* on every topic and claim page that surfaces the relevant PNUs with their mechanism chain. For the 160 Fall student this panel should be available but defer; for the researcher it should be on by default.

*Evidence-quality fingerprint summary.* The paper-quality fingerprint work just landed in Article_Eater and is in build for Knowledge_Atlas. When it deploys, each paper view should carry a summary fingerprint (preregistration status, sample composition, effect-size precision, multiple-comparisons handling, COI, replication record). Both user types benefit; the 160 student uses it to learn methodology, the researcher uses it to weigh evidence.

*Provenance footer.* Every page should carry a brief footer recording how the content was assembled (which extraction stage, which AI model, which human review). This is a Track 4 concern (one of their heuristic-audit items) and a methodological-honesty concern.

## 7. What's missing and what to design first

Putting the framework against the current state of the site, three gaps stand out.

The first gap is **the goal-driven journey surface itself**. The user-type home pages described in the architecture doc are not yet built (no `ka_home_researcher.html`, no `ka_home_student_fall.html`). The "Journey Choices" tables in that doc are concept; the surfaces that render them are not implemented. The journey-relevant page taxonomy currently goes: public home → user home (one-size-fits-all) → topic / article / layer pages. The missing layer between the user home and the topic/article pages is the *goal-driven journey landing*. This is what should be designed first.

The second gap is **the VOI panel**. It is named, agreed-upon, and not yet built. Both user types need it. Its build is bounded: a data backend (the VOI ranks per topic and per question) plus a card component.

The third gap is **the 160 Fall integration**. The existing 160sp work is all Spring. The Fall syllabus is documented (`fall160_schedule.html`, `docs/COGS160_FALL_DESIGNING_EXPERIMENTS_QUALITY_2026-04-25.md`) but the journey wiring that makes Week 1 surface different affordances from Week 4 is not yet built. The system needs to *know* what week the Fall student is in and surface the corresponding journey landing.

The other journey-related issues (broken CTAs, layer-page polish) are tracked in the existing journey-fix roadmap and in the April 20 ruthless brief; they continue but are not the gating items for the new work you are now framing.

## 8. Track 4 students: what they have given us and what they still need

The Track 4 students' user-journey design document gives us the conceptual framework I have used here. Their deliverable T4.b asks them to write scenario walkthroughs for three archetypes (160sp student, public visitor, admin). Their T4.b.2 deliverable asks them to put each of the five topic-page variants through their three archetype scenarios and produce a comparative usability evaluation. These are valuable inputs.

What the Track 4 students do not yet have, and what would help them produce more useful Week-4–5 work, is:

- A clear distinction between layer pages and journeys (the linguistic correction in §2 above). If their walkthroughs treat the existing `ka_journey_*.html` pages as user journeys, they will produce evaluations that are misaligned with what those pages are actually for. The distinction should be made explicit in the rubric.

- A working enumeration of the candidate goal-driven journeys per user type. The §5 lists above are first passes; a refined version, even at the level of one-line names, would let the Track 4 students walkthrough specific journeys rather than only generic topic-page interactions.

- The VOI affordance as a thing to look for. Their heuristic audits currently do not have a category for "is the value-of-information signal visible to this user?" because the affordance is not yet on the site. Naming it as a thing the journeys should have lets the Track 4 audits include it.

- The 160 Fall context. If the students are doing T4.b and T4.b.2 in Spring on Spring artefacts, they will not exercise the Fall course's journey-by-week alignment. The rubric could include a Fall scenario when the Fall course launches.

## 9. Recommended next steps

In rough priority:

1. **Validate this framing with you.** Read this document; mark up the §5 candidate journey lists; tell me what is wrong, what is missing, which journeys should be combined or split.

2. **Lock the layer-page-versus-journey vocabulary distinction.** Rename or relabel where needed. Update the Track 4 rubric to use the distinction.

3. **Design the goal-driven journey landing surface.** This is the missing layer. Probably one HTML template instantiated per (user type × journey), or a parameterised page. Roughly five surfaces per user type, two user types of immediate priority, ten surfaces total — a manageable build.

4. **Build the VOI panel component.** Data backend plus card component. Card lands on the journey landings, on topic pages, and on claim pages. Both user types benefit immediately.

5. **Wire the Fall student journey to course week.** The fall160_schedule.html already names the weeks; the system needs to read the student's current week and route them to the corresponding journey landing.

6. **Surface the neural-underpinnings panel on researcher journeys.** The data exists; the panel needs design.

7. **Test the journey landings against the Track 4 students' walkthroughs.** Their T4.b scenarios and T4.b.2 comparative evaluation become the empirical validation.

Each of these is a deliverable that can become a Codex prompt once the framing settles. I have written none of those prompts yet because the framing should settle first.

---

*End of framing. To be reviewed before any implementation prompt is written.*
