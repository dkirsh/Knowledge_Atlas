# Operationalising Value of Information on the Knowledge Atlas — Panel Context

**Date**: 2026-05-17
**Author**: CW for DK, drafted as context for a methodology panel
**Status**: Context document — *not* a methods proposal. The methods are for the panel to recommend.
**Companion**: `docs/USER_JOURNEYS_THINKING_2026-05-17.md`, `160sp/ka_week1_wireframe_2026-05-17.html`
**Scope**: Frame the VOI problem; enumerate the distinct targets of VOI; identify the panelists whose perspectives we need; pose the questions for them to answer.

---

## 1. Why we need VOI, and why now

The Knowledge Atlas has been catalysed by two adjacent intuitions. The first is that not every empirical study makes the same contribution to a field: some studies replicate the well-replicated, some confirm what was already obvious, some address questions whose answer the field already has. The second is that *which* questions a field has not yet resolved is itself an analysable property of the literature, and a properly indexed corpus should be able to surface those questions to anyone designing a new study — whether a researcher choosing a thesis project or a 160 Fall student picking a topic for a seven-week experiment.

Value of Information is the natural framing. In its classical decision-theoretic statement (Howard, 1966; Raiffa & Schlaifer, 1961), VOI is the expected reduction in the cost of a decision that would follow from acquiring a piece of information. The classical statement is operationalised for situations where the decision is well-formed, the prior is known, and the utility function is given. Almost none of those conditions hold for choosing a research topic. Yet the underlying intuition — *which study would most reduce uncertainty about something we care about?* — is exactly what both our priority user types are asking when they sit down to plan.

The challenge is that VOI, in the Atlas context, is not one quantity. It is a family of quantities, and the family decomposes along several axes that the panel needs to help us think through. The architectural choice in front of us is whether to compute a single composite VOI score per topic, a small set of VOI flags by kind, or a richer multidimensional VOI profile per topic or per question. That choice has direct downstream consequences for the UI — what the VOI panel on Surface 5 of the Week-1 wireframe actually shows, what the researcher home page surfaces, how the article-finder query is shaped — and we should not make it before we have heard the panel.

A second pressure for now-ness. Codex's paper-quality build has begun extracting fingerprints across the corpus. Several of the fingerprint fields are directly relevant to VOI computation: preregistration status, replication record, sample composition, effect-size CI width, design type. If the fingerprint extraction proceeds without a VOI specification, we will land in the situation where the data is there but we do not yet know what to compute over it. Conversely, if we specify VOI first, we can guide the extraction to surface the fields VOI will need. The window for that influence is open right now.

A third pressure. The user-journey wireframe just landed (Surfaces 2, 3, 4, and 5 of `160sp/ka_week1_wireframe_2026-05-17.html`) treats the VOI panel as an upstream dependency. The wireframe shows the panel with placeholder content and explicit dependency flags. Until VOI is operationalised, those flags persist; until they persist, the journey cannot ship.

## 2. The different reasons we need VOI

Before naming targets, the distinct *uses* of VOI on the Atlas, because each use shapes what the operationalisation should optimise for.

*Choosing a topic for a thesis or a paper or a grant.* A researcher arrives at the system with a domain of interest and wants to identify the highest-leverage question they could ask in that domain. VOI here is forward-looking: it ranks open questions by the expected reduction in uncertainty their answer would produce. The user is making a one-off decision under uncertainty about which topic to commit a year (or seven weeks) to.

*Choosing a topic for a 160 Fall student project.* The student arrives with less domain knowledge and less time. VOI here is feasibility-conditioned: ranking topics by expected contribution *subject to* the project being completable in 7-to-10 weeks with class-internal pilot subjects. The student is making a one-off decision under tighter constraints.

*Avoiding redundant studies.* Both researchers and 160 students need to know whether the study they are about to design has already been done — or done so close to what they propose that their version adds little. This is the *Article-Finder coupling* DK named: every VOI pointer must give rise to a corresponding article-finder query of the form *has work close to this been done since [date]?*. A VOI signal that cannot be sanity-checked against the existing corpus is half a signal.

*Prioritising corpus expansion.* When the Atlas's curators decide which papers to acquire next, VOI is one of the inputs. Areas with high VOI are areas where new papers will be most valuable to surface. This use is internal-to-the-system but is real.

*Revealing contested or saturated areas to readers.* For a public-facing reader (researcher or interested layperson), VOI markings tell them where the field is still arguing and where it has converged. This is a presentational use that does not necessarily drive a new study.

*Framing thesis or grant proposals.* When a researcher writes a proposal, they justify their question's importance partly by reference to what is not yet known. The Atlas should be able to provide that justification in citable form: "according to the VOI panel for topic X, sub-question Y has the highest marginal information value, with the following supporting features..."

The six uses overlap but are not identical. The same VOI machinery can serve several of them; the question for the panel is which set the machinery should be optimised for, and whether some uses should be served by different machinery.

## 3. The different targets of VOI

This is the substantive enumeration. Each target is a distinct *kind* of opportunity the corpus can surface. I have made each into a paragraph that says (a) what it is, (b) why it matters, (c) the article-finder query that must accompany it, and (d) what is conspicuously deficient if the target is not handled. I am *not* solving the methods — that is the panel's job.

**Target 1 — Better stimuli for an existing topic.** A topic T has been studied with stimuli of a particular kind (static photographs of nature scenes, brief sound clips, ten-minute VR exposures) and the stimuli have known limitations (artificiality, short duration, narrow ecological range). A new study with better stimuli would test whether the original effects survive the methodological upgrade. The article-finder query: *has anyone tested topic T with [longer / more ecological / VR / field] stimuli in the past five years?* The deficiency if unaddressed: the field is full of effects that may or may not survive transition from impoverished lab stimuli to more representative ones, and the system has no way to tell which.

**Target 2 — Better measures than have been used.** Topic T has been studied predominantly with outcome measures M that have known deficiencies — short-form self-report scales with low reliability, single-item measures, scales validated only on undergraduates, behavioural measures with floor or ceiling effects, self-report when behavioural alternatives exist, indirect proxies when direct measurements are now available. *I am not naming what a better measure would be; the corpus knows what measures the field has used and what their known deficiencies are.* The article-finder query: *what alternative measures have been validated for the construct underlying topic T?* The deficiency if unaddressed: students and researchers reach for the convenient measure when a better one is reachable, and the cumulative literature drifts toward measures that are easy to administer rather than measures that are sound.

**Target 3 — Obviously understudied topics or sub-topics.** Intersections in the topic crosswalk that have zero or near-zero published papers. Topics on an emerging framework (predictive processing in architectural cognition, for example) where the framework has been articulated but not empirically tested. Sub-topics under a well-studied topic that have been mentioned in discussion sections but not directly examined. The article-finder query: *any work on this intersection in the past five years?* — and if no, why not? The deficiency if unaddressed: the field self-perpetuates around already-studied questions because researchers cannot easily see the empty cells; understudied areas remain understudied even when their VOI is obviously high.

**Target 4 — Questions arising from confounds in IV or DV.** When a paper's independent variable is operationalised in a way that conflates two underlying constructs (daylight studies that also vary thermal load; soundscape studies that also vary affective arousal), the disentangling experiment is a natural next study. When a paper's dependent variable is measured in a way that admits demand characteristics or experimenter expectancy, the deconfounded experiment is similarly natural. The article-finder query: *has anyone deconfounded [IV1, IV2] in a study of topic T?* The deficiency if unaddressed: confounded findings propagate through citations as if they were clean, and a generation of derivative studies builds on a foundation that the next careful experiment would have shaken.

**Target 5 — Weak links in mechanism chains and Plausible Neural Underpinnings.** The PNU (Plausible Neural Underpinning) registry in the Atlas describes mechanism chains — stimulus → perceptual stage → cognitive stage → autonomic stage → behavioural outcome — that connect inputs to effects. Some links in those chains are well-measured (the perceptual stage of nature-views-restoration has direct human neuroimaging evidence); others are stubs or speculation (the cognitive-stage link is often hand-waved). A study that directly measures a previously hand-waved intermediate stage has high VOI on the chain. The article-finder query: *any direct measurement of [intermediate stage] for the [PNU] chain?* The deficiency if unaddressed: mechanism chains in the Atlas accumulate stubs that get cited as if they were established, and the cumulative confidence in the chain is inflated.

**Target 6 — PNUs that might generalise beyond the existing corpus.** A PNU derived from animal studies that has not been tested in humans. A PNU derived from clinical populations not tested on healthy participants. A PNU established for one perceptual modality (visual nature exposure) that might generalise to another (auditory nature exposure) but has not been tested cross-modally. The article-finder query: *any study extending [PNU] from [original population] to [new population or modality]?* The deficiency if unaddressed: the Atlas surfaces PNUs as if they were universally applicable when their generalisation envelope is narrower than the surfacing suggests.

**Target 7 — Theory-paradigm questions in the Lakatos sense.** A research programme has a hard core (its constitutive theoretical commitments) and a protective belt (the auxiliary hypotheses adjusted in response to anomalies). Where does the protective belt of an active programme stop accommodating? What prediction does the hard core make that no current experiment has tested? Is there a crucial experiment that could distinguish two competing programmes (Attention Restoration Theory versus Stress Recovery Theory, for example)? The article-finder query: *any experimental test that distinguishes [theory A] from [theory B]?* The deficiency if unaddressed: competing programmes co-exist in the literature without empirical confrontation, students cannot see what is at stake between them, and the system cannot signal where a thesis project could move the dial.

**Target 8 — Replication priorities.** A study with a surprising result has not yet been replicated. A study with a low N (and therefore wide CIs) has not been re-run with adequate power. A study from a single lab has not been independently replicated. The article-finder query: *has [study X] been replicated?* The deficiency if unaddressed: the Atlas treats unreplicated effects with the same epistemic weight as replicated ones, and the marginal contribution of a replication study is invisible.

**Target 9 — Heterogeneity and moderator questions.** When effect sizes vary substantially across studies on the same topic, the moderators of that variation are themselves an open question. Why does X work in samples Y_1 and Y_2 but not Y_3? Does it depend on session duration, on prior expectation, on cultural context, on age? Each candidate moderator is a study. The article-finder query: *any study examining [proposed moderator] of topic T?* The deficiency if unaddressed: heterogeneity is averaged away in narrative summaries when it is the substantive finding.

**Target 10 — Cross-cultural and WEIRD-extension questions.** A topic has been studied exclusively in Western, Educated, Industrialised, Rich, Democratic samples (Henrich, Heine & Norenzayan 2010). The extension to non-WEIRD samples is its own question, with implications for the construct's universality. The article-finder query: *any non-WEIRD replication of topic T?* The deficiency if unaddressed: the Atlas misrepresents the universality of its findings.

These ten targets are not exhaustive; they are the kinds CW has been able to identify by looking at the existing corpus and the paper-quality fingerprint specification. The panel should add what they think is missing.

## 4. Cross-cutting concerns the panel should rule on

Six concerns cut across the ten targets. Each is a design choice with downstream consequences.

*Aggregation.* When a topic has high-VOI signals from multiple targets (Target 3 + Target 7, say — understudied *and* paradigm-distinguishing), how should the signals combine? A weighted sum? A vector of flags? A pareto-front analysis? The panel's recommendation here drives the UI choice between a single VOI score and a multi-dimensional profile.

*Score versus flag versus profile.* Should the user-facing VOI affordance be a single number (0–1, or some normalised analogue), a categorical (high/medium/low), a set of binary flags per target type, or a richer profile that names the kind of opportunity? Each has implications for how the system communicates uncertainty and how the journey design absorbs the output.

*Temporal decay.* VOI is not stationary. A question's marginal information value declines as the literature catches up. Today's high-VOI gap becomes tomorrow's filled space. How should VOI scores age? Should they be re-computed continuously from the corpus, recomputed periodically, or stamped with a freshness date the user reads explicitly?

*Sensitivity to corpus completeness.* The Atlas does not contain every paper in every field. Topics where our coverage is thin may *appear* understudied when in fact the literature outside the corpus has addressed them. How should VOI degrade gracefully when corpus coverage on a topic is incomplete? Should there be a "coverage-confidence" annotation on every VOI score?

*Student-facing versus researcher-facing.* The same underlying VOI machinery should serve both user types, but the framing differs. For a 160 Fall student, VOI must be feasibility-conditioned (a 7-to-10-week project cannot capitalise on every kind of VOI opportunity). For a researcher, the full menu is in play. Should the system compute one VOI and project it differently for each user type, or compute two separate VOIs?

*The article-finder coupling.* Every VOI pointer the system surfaces must accompany the article-finder query that would confirm or refute it ("has the work that would erase this opportunity already been done?"). What is the right form of that query — a structured search, a free-text query, a corpus-internal lookup followed by a web search? The panel should sanity-check that the coupling is workable.

## 5. The panel

CW proposes a panel of seven, drawing on the disciplines whose vocabularies bear on the VOI question. The composition is for DK's approval; CW will brief each panelist with this context document plus a tailored summary of what their perspective is being asked for.

*Judea Pearl* — causal inference and Bayesian DAGs. Pearl's framework lets us think rigorously about what counts as a deconfounded measurement (Target 4) and what experimental designs would distinguish causal hypotheses (relevant to Targets 4, 5, 7). His do-calculus is the natural formal apparatus for the kind of intervention reasoning VOI involves. (~250,000 Google Scholar citations on the body of work; Pearl, 2009, *Causality*, ~25,000.)

*Andrew Gelman* — Bayesian workflow, the garden of forking paths, applied statistics. Gelman has written directly on Bayesian decision-theoretic VOI in applied contexts and on the related problem of how to detect when a literature has been distorted by selective reporting. His framework is the most operational for what we are trying to build. (Gelman & Loken, 2014, ~1,800 citations on the garden-of-forking-paths essay alone; *Bayesian Data Analysis*, ~40,000.)

*Paul Thagard* — philosophy of cognitive science, computational philosophy of science, conceptual change. Thagard has spent decades thinking about how scientific concepts shift and which concepts are most ripe for revision. His perspective bears directly on which kinds of VOI targets are theoretically interesting and which are merely empirically open. (Thagard, 1992, *Conceptual Revolutions*, ~3,500; broader corpus ~30,000.)

*Deborah Mayo* — error statistics, severe testing. Mayo is the contemporary heir of the Popper-Lakatos line; her work on what counts as a severe test of a hypothesis is directly relevant to Target 7 (paradigm-distinguishing experiments) and to the question of when a replication adds methodological value. (Mayo, 2018, *Statistical Inference as Severe Testing*, ~1,000.)

*Edouard Machery* — philosophy of psychology, replication, cross-cultural variation. Machery has been a leading voice on what the replication crisis means and on how cross-cultural variation should inform the construction of psychological constructs. Directly relevant to Targets 8 (replication priorities) and 10 (WEIRD-extension). (Machery, 2017, *Philosophy Within Its Proper Bounds*, ~700.)

*György Buzsáki* — systems neuroscience, mechanism, generalisability of neural findings. Buzsáki has written incisively on the gap between recording-level neural findings and behavioural claims, and on the conditions under which a neural mechanism is generalisable. Directly relevant to Targets 5 (weak links in mechanism chains) and 6 (PNU generalisation). (Buzsáki, 2019, *The Brain from Inside Out*, ~1,500; broader corpus ~80,000.)

*Helen Longino* — social epistemology of science, contestation, diversity of perspectives. Longino's framework lets us think about how the *community* of inquiry assigns value to questions, not just how an individual researcher does. Relevant to the question of how VOI should weight controversy versus convergence (Target 7), and to the framing of cross-cutting concerns about who decides what counts as a research priority. (Longino, 1990, *Science as Social Knowledge*, ~5,500; 2002, *The Fate of Knowledge*, ~3,000.)

If DK wants to substitute or add panelists, candidates: *Karl Friston* (active inference, prediction error, free energy as an alternative formulation of information value); *Stanislas Dehaene* (cognitive neuroscience, generalisability across modalities, brain-as-Bayesian-machine); *Anjan Chatterjee* (neuroaesthetics, the architectural-cognition connection specifically); *Patricia Churchland* (philosophy of neuroscience, mechanism); *Heather Douglas* (values in science, what counts as a worthy question).

## 6. What we are asking the panel

The panel is asked to converge on answers to a small set of questions. The questions are deliberately not solved in this document; that is the panel's work.

**Question 1 — Which of the ten targets is genuinely a VOI target?** Are there targets here that should not be operationalised as VOI signals at all (because the kind of value involved is not the kind VOI captures)? Are there targets we are missing?

**Question 2 — For each target the panel accepts, what computational criterion best operationalises it?** Each target needs a criterion that can be computed from the corpus's already-extracted fingerprint data (preregistration status, sample composition, effect-size CI width, design type, replication count, citation pattern, COI, etc.) plus the structural data the system has (topic crosswalk, PNU registry, theory hierarchy). The panel does not need to propose code; they should propose the conceptual criterion and the data it requires.

**Question 3 — Aggregation.** Should the user see a single composite VOI score per topic, a vector of per-target flags, or a richer profile? If composite, how should the targets combine? If multidimensional, how should the UI present them?

**Question 4 — Score, flag, or profile.** What is the right user-facing format for the VOI affordance? The Week-1 wireframe assumed a categorical High/Medium/Low with a three-bullet rationale; the panel should confirm or revise this.

**Question 5 — Temporal decay.** How should VOI degrade as the literature catches up? Should the system stamp each score with a freshness date? Should there be a "stale VOI" alert when a topic's score is more than N months old?

**Question 6 — Sensitivity to corpus incompleteness.** How should the system communicate that a high-VOI signal might be an artefact of incomplete corpus coverage? Should there be a coverage-confidence annotation?

**Question 7 — Student versus researcher.** Should the system compute one VOI and project it differently for each user type, or compute two separate VOIs? Particularly: how should the feasibility constraint for 160 Fall students enter the computation — as a filter applied after VOI is computed, or as a modifier inside the computation?

**Question 8 — Article-finder coupling.** Each VOI pointer must give rise to an article-finder query that would confirm or refute it. What is the right form of that query, and what is the right interaction (does the user click "verify this is still open" and the system runs the query; or does the system pre-verify and surface only fresh opportunities)?

**Question 9 — The methodological-quality coupling.** The paper-quality fingerprint work in flight (Codex paper-quality build) is extracting the data VOI will need. Are there fingerprint fields the panel thinks we should add or refine before extraction proceeds further?

**Question 10 — What we are missing.** What problem with this VOI framing have we not thought of?

## 7. Process

CW will brief each panelist with this document plus a one-page tailored summary explaining which questions their perspective is most central to. The brief will request a short written response (~600–1,200 words per panelist) within two weeks.

After the responses arrive, CW will produce a *synthesis document* that:
- Catalogues each panelist's position on each question
- Identifies points of convergence (where the panel agrees) and contested questions (where panelists disagree)
- Proposes a working operationalisation that adopts the convergent answers and surfaces the contested ones for DK adjudication
- Lists the computational criteria the operationalisation requires
- Flags the upstream paper-quality fingerprint fields that would need to be added or refined

DK adjudicates the contested questions. Once DK has decided, CW writes the implementation prompts for Codex (the VOI panel component, the per-topic VOI computation, the article-finder coupling), and the wireframe's Surface 5 placeholder content gets replaced with real VOI machinery.

## 8. What this document does not do

To be precise about scope: this document is *not* a methods proposal. It deliberately stops short of recommending specific computational criteria for each target, specific aggregation schemes, specific decay models. Those are for the panel to recommend; the panel's judgement is more valuable than CW's because (a) the operationalisation will be cited as a methodological commitment of the Atlas going forward, and (b) the operationalisation needs to be defensible across the seven panelists' disciplinary perspectives. CW's job here is to frame the problem so the panel can do its work. The methods are theirs.

---

## References

Gelman, A., & Loken, E. (2014). The statistical crisis in science. *American Scientist*, 102(6), 460–465. (Google Scholar: ~1,800)

Henrich, J., Heine, S. J., & Norenzayan, A. (2010). The weirdest people in the world? *Behavioral and Brain Sciences*, 33(2–3), 61–83. https://doi.org/10.1017/S0140525X0999152X (Google Scholar: ~10,500)

Howard, R. A. (1966). Information value theory. *IEEE Transactions on Systems Science and Cybernetics*, 2(1), 22–26. https://doi.org/10.1109/TSSC.1966.300074 (Google Scholar: ~1,300)

Lakatos, I. (1970). Falsification and the methodology of scientific research programmes. In I. Lakatos & A. Musgrave (Eds.), *Criticism and the growth of knowledge* (pp. 91–196). Cambridge University Press. (Google Scholar: ~12,000)

Longino, H. E. (1990). *Science as social knowledge: Values and objectivity in scientific inquiry*. Princeton University Press. (Google Scholar: ~5,500)

Machery, E. (2017). *Philosophy within its proper bounds*. Oxford University Press. (Google Scholar: ~700)

Mayo, D. G. (2018). *Statistical inference as severe testing: How to get beyond the statistics wars*. Cambridge University Press. (Google Scholar: ~1,000)

Pearl, J. (2009). *Causality: Models, reasoning, and inference* (2nd ed.). Cambridge University Press. (Google Scholar: ~25,000)

Raiffa, H., & Schlaifer, R. (1961). *Applied statistical decision theory*. Harvard University Press. (Google Scholar: ~4,500)

Thagard, P. (1992). *Conceptual revolutions*. Princeton University Press. (Google Scholar: ~3,500)

---

*End of context document. Panel briefing pages and per-panelist invitation letters to follow when DK approves the panel composition.*
