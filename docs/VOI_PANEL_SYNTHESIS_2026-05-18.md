# VOI panel — CW-simulated synthesis
*Date: 2026-05-18 · Author: CW for DK · Status: Internal CW simulation pending real panel*

## Status statement (read first)

This document is **CW's internal simulation of the eight-panelist VOI consultation**, written by attributing positions to each panelist on the basis of their *published* work. It is not a real panel response. Real responses would require sending the briefing letters and waiting two weeks; that is Sprint UJ-F in the plan and is gated on DK approving the panel composition before letters go out.

The simulation is useful nonetheless. The eight panelists were chosen precisely because their published positions on the questions are well-articulated; their *likely* responses to a methodological question are recoverable from their writing. Where CW's confidence in a panelist's position is high — because they have written explicitly on the question — the synthesis flags it. Where the confidence is medium or low — extrapolation from related work — the synthesis flags that too. DK should treat the synthesis as a structured-thinking exercise rather than a panel verdict; the real panel may still revise. The output is meant to unblock the next round of implementation work (Sprints UJ-C and UJ-D) so Codex has well-grounded specs to build against rather than placeholders.

Each panelist's section runs ~700–900 words and addresses the questions most central to their expertise. The synthesis at the end identifies convergent positions, surfaces contested ones, and proposes a working operationalisation that DK can adjudicate. AG's V2 credence work (`Article_Eater_PostQuinean_v1_recovery/docs/CLAUDE_HANDOFF_V2_CREDENCE_2026-05-18.md`) provides the substrate — the three-credence display, the warrant-richness fields, the 670 weak-mechanism-link beliefs, the scope metadata, the theory entrenchment scores — and shows up in nearly every panelist's response because it is what the panel would actually be advising over.

---

## 1. Judea Pearl — causal inference and the do-calculus

*CW confidence in attribution: HIGH on causal-inference questions; MEDIUM on VOI presentation choices.*

Pearl would frame the VOI question structurally before any numerical operationalisation. His standing position (Pearl, 2009; Pearl & Mackenzie, 2018) is that the field's confusion about evidential value is a confusion of *correlation-warranted* claims with *causal-warranted* claims, and that the right starting point for any value-of-information computation is the causal diagram of the claim. A study has high VOI in Pearl's framework if and only if (a) it admits a clear identification claim — there is a causal estimand the study is targeting — and (b) the study's design closes the back-door paths that would otherwise confound the estimand.

For the ten VOI targets, Pearl would draw a sharp line through them. Target 4 (IV/DV confounds) is squarely his territory: the proper VOI signal on a confounded paper is the *expected reduction in identification ambiguity* that a deconfounded follow-up would produce. AG's warrant-richness fields can be made to do this work — a paper with `n_supporting = 14` and `defeat_status = UNDEFEATED` is a paper whose causal claim has survived scrutiny, while a paper with `confounding_warrant = 0.15` (low) is a candidate for the deconfounding follow-up. Pearl would push for the per-paper VOI signal to expose the *causal-structure assumptions* the study makes, not just summary statistics, so the student or researcher can see what would falsify them.

On Target 5 (weak mechanism links) Pearl would be vehement. The 670 weak-mechanism-link beliefs in the ae.db credence engine are *precisely* what his front-door criterion is designed to identify: places where the mediating mechanism has been hand-waved rather than directly measured. He would treat each weak link as a high-VOI target *only if* the study to fill it can satisfy the front-door identification conditions. That qualification matters: a follow-up that "measures" a mechanism by means of a proxy with its own back-door paths is not a real improvement.

Pearl would be sceptical of Target 7 (theory-paradigm questions) as VOI candidates without further structure. He has long argued that "paradigm-distinguishing" framings in psychology often hide the failure to specify what causal structure the competing paradigms commit to. His advice: do not let Target 7 launder paradigm-loyalty disputes as VOI; require the proposed experiment to identify which causal pathway it would estimate.

On the aggregation question (§4 of the panel context), Pearl would favour a *vector of structural flags* per topic over a composite score. His reasoning is that compositing across different causal-structural questions hides the very distinctions a researcher should be reasoning about. A topic might have high VOI on the deconfounding target (Target 4) and low VOI on the WEIRD-extension target (Target 10) for entirely different reasons that should not be averaged into a single number.

On the article-finder coupling (Question 8 in §6 of the panel context), Pearl would propose phrasing each finder query as a counterfactual: "has a study estimated *E*[*Y* | do(*X* = *x*)] for this topic?" rather than the looser "has anyone studied this?" The counterfactual form is harder for retrieval to match but disciplines the query.

The point on which Pearl's position is least clear is Question 4 (score vs flag vs profile). His writing strongly implies profile, but he has not engaged with VOI UI design directly. CW's modelling: he favours profile.

---

## 2. Andrew Gelman — Bayesian workflow and applied statistics

*CW confidence in attribution: HIGH; Gelman writes regularly on directly adjacent questions.*

Gelman would put the *garden of forking paths* (Gelman & Loken, 2014) and *Type-M and Type-S errors* (Gelman & Carlin, 2014) at the centre of the VOI discussion. His position would be that the question "what is the value of a new study?" cannot be answered without first asking "what is the value of the existing studies?", and that the existing literature on most topics in cognitive science is *less informative* than it looks because of selective reporting, multiple-comparison inflation, and underpowered designs. The credence values in ae.db (now ranging [0.12, 0.82] with stdev 0.106) are a substantial improvement on the previous flat distribution, but Gelman would still want to see them tied explicitly to a Bayesian model of the literature rather than treated as point estimates.

On the cross-cutting question of *aggregation* (§4 Question 3), Gelman's published work suggests strong preference for *multilevel* modelling over composite scores. The ten VOI targets, in his framework, are different sources of variation in a topic's information value; the natural Bayesian move is to put each on its own level of a hierarchical model and let the data speak about how they relate. The three-credence Cartwright structure already in ae.db (`as_tested`, `scope_adjusted`, `network`) is exactly the kind of decomposition he would endorse, with the addition of explicit uncertainty intervals around each component.

On Target 8 (replication priorities), Gelman has been a voice for the position that replications are most valuable when the original study has wide CIs and a surprising sign — not just any unreplicated study. He would propose operationalising the replication-priority VOI as a function of *Type-M error risk*: a topic where the replicable effect size estimate is much smaller than the published estimate has high VOI for replication.

On Target 1 (better stimuli) and Target 2 (better measures), Gelman's view tracks his concerns about measurement: a topic with measurement reliability below ~0.7 has high VOI for measurement improvement *not because the construct is wrong* but because the field cannot detect interesting effects with noisy measures. He would propose tying the VOI signal here to the warrant-richness data in ae.db plus the (planned) per-paper psychometric records.

On the temporal-decay question (§4 Question 5), Gelman has been explicit (in blog form, repeatedly) that "freshness dates" on quantitative summaries are oversold. He would advise stamping each VOI value with the date and the corpus size at computation time, rather than implementing automated decay. Users can decide for themselves whether a year-old VOI value is still informative.

The substantial point where Gelman's position is less recoverable from his writing is Question 11 (information-theoretic decomposition). He has written less explicitly on Shannon-information measures than on Bayesian-decision-theoretic ones; CW expects he would defer to Bergstrom on the information-theoretic side and push for the decision-theoretic side to stay primary.

---

## 3. Paul Thagard — coherentist philosophy of cognitive science

*CW confidence in attribution: HIGH on coherence-and-explanation questions; MEDIUM on operationalisation specifics.*

Thagard's contribution (Thagard, 1989, 1992, 2007; ECHO and its successors) would focus the panel on Question 11 (information-theoretic decomposition) and Question 3 (aggregation). His standing position is that explanatory coherence is the right unifying frame for evaluating evidential support across a network of claims, and that the ECHO algorithm — which propagates activation through a network of claims linked by explanatory and contradiction relations — produces coherence values that approximate what working scientists actually do.

For the VOI panel, Thagard would propose that VOI is *coherence-disruption potential*: a study has high VOI on a topic if its expected result would substantially raise or lower the coherence of the connected belief network. AG's V2 credence engine has produced a global coherence score (0.4201, down from 0.5417) and a tension count (55, down from 70); Thagard would treat these as the *substrate* over which VOI is computed. The 670 weak-mechanism-link beliefs are interesting to Thagard because each represents a place where the coherence calculation is making a structural assumption that a direct measurement could test.

On Target 7 (paradigm-distinguishing experiments), Thagard would be enthusiastic. His Conceptual Revolutions (1992) is precisely about how paradigm shifts happen through coherence reorganisation; an experiment that would force a coherence reorganisation has very high VOI in his framework. He would treat ART vs SRT not as a paradigm question but as a *coherence-network competition* — the two networks share many claims; a discriminating experiment would be one that the two networks predict differently.

On the score-vs-flag-vs-profile question (§4 Question 4), Thagard's framework points toward a *coherence-vector profile*: each VOI target maps to a particular way of disrupting or extending the coherence network. He would resist a single-number summary because it averages across distinct kinds of coherence move.

On Target 11 (the new information-theoretic decomposition question CW added), Thagard would partially agree: the coverage-gap targets (3, 8, 10) are indeed entropy-reductions over the question space, while the methodological-upgrade targets (1, 2, 4) are coherence-shift estimates. But he would push back on treating the two kinds as fundamentally separate; a methodological upgrade that survives is itself a coverage move, because the field gains a new operationalisation it can apply to further topics.

The position Thagard's writing leaves least clear is Question 7 (student vs researcher framing). His work has not engaged the pedagogical layer directly. CW expects he would advocate giving students a simplified profile rather than a single number, because exposure to the underlying structure is itself pedagogically valuable.

---

## 4. Deborah Mayo — error statistics and severe testing

*CW confidence in attribution: HIGH; Mayo's framework speaks directly to most of the questions.*

Mayo's framework (Mayo, 2018; Mayo & Spanos, 2010) would centre on the *severity* of the tests a study performs. Her position would be that the VOI question is incomplete without asking, of any candidate study, "what would count as a severe test of the claim it is investigating?" — and that the existing corpus's value should be estimated by how severely each member tested its central claim.

The `severity` field already in AG's V2 epistemic_v2 schema (ranging [0.35, 0.90]) is exactly her vocabulary. Mayo would push for that field to become a first-class input to every VOI computation. A topic where the corpus papers have mean severity around 0.45 has high VOI for *severe-retest* studies, regardless of which of the ten targets the retest happens to fill.

On Target 4 (confounded IV/DV), Mayo would convert the question into a severity question. A confounded study has failed to severely test its central claim; the deconfounding follow-up is high VOI precisely because severity is currently low. The severity-warrant decomposition in ae.db (mechanism, entrenchment, meta-analytic, confounding) gives the panel exactly the substrate to operationalise this.

On Target 7 (paradigm distinguishing), Mayo would be more sceptical than Thagard. Her standard line (against the Lakatosian or Kuhnian tradition) is that there is no such thing as a "test between paradigms" — there are only severe tests of individual claims. She would reframe Target 7 as: *which claims, currently held by competing theories with high entrenchment, would a severe test most disrupt?* AG's theory entrenchment scores (ART 1.000, PP 0.964, etc.) tell us which theories are currently safe; a Mayo-style VOI calculation would flag claims that are held jointly by multiple high-entrenchment theories and have low severity in their current evidence base.

On Question 11 (information-theoretic decomposition), Mayo would resist on principled grounds. Her framework is decision-theoretic but not Bayesian-decision-theoretic in the standard sense; she has been a public critic of Bayesian inference's treatment of *severity*. CW expects she would propose that the VOI computation use her error-statistical framework as a third pillar alongside Pearl's structural framework and Gelman's hierarchical framework.

On Question 6 (corpus completeness), Mayo would push for *severity-weighted coverage* rather than raw paper counts. A topic with twenty papers of mean severity 0.40 is *less* covered than a topic with five papers of mean severity 0.85.

The position least recoverable from her writing is Question 7 (student vs researcher). CW's modelling: Mayo's pedagogical writing has been spare; she would likely defer.

---

## 5. Edouard Machery — philosophy of psychology and replication

*CW confidence in attribution: HIGH on replication and cross-cultural questions; MEDIUM elsewhere.*

Machery (Machery, 2017, 2020) would put two questions at the centre: Target 8 (replication priorities) and Target 10 (WEIRD-extension), with a strong methodological gloss across the rest.

On Target 10 specifically, Machery has been a leading voice for the claim that the cross-cultural-replication problem is more serious than the WEIRD framing alone captures, because *concept variation* across cultures means that even successful behavioural replications can mask substantive differences in the construct being measured. He would propose that VOI Target 10 should be sub-decomposed into (a) sample-extension studies (same construct, new population) and (b) construct-validation studies (does the construct itself travel?). The scope metadata in ae.db (`population_type`: university_students, children, office_workers, clinical, elderly) is the substrate; Machery would push for a `culture` field to be added.

On Target 8 (replication), Machery's position aligns with the Open Science Collaboration's findings but extends them: a single failed replication is informative but not conclusive; the VOI of a third or fourth replication on an already-twice-failed effect is *higher* than the first replication, because that is where the field actually decides. He would propose tying replication-priority VOI to the *number of prior replications attempted* in a quadratic rather than linear way — the second replication is more informative than the first when the first failed.

On Question 9 (methodological-quality coupling with fingerprint), Machery would be specific. The paper-quality fingerprint should carry, beyond what AG already has, *construct-fidelity* fields: which construct does the paper claim to operationalise, with which scale, validated in which population. This is what the substitution skill needs; it is also what a Machery-style WEIRD-extension VOI signal needs.

On Question 7 (student vs researcher), Machery would advocate a *simpler interface for students with full-fidelity behind a click-through*. His pedagogical writing leans toward exposing students to the methodological reality of the field rather than protecting them from it.

Where Machery's writing leaves least guidance is the aggregation question (§4 Question 3). CW models him as favouring multilevel-Bayesian aggregation in the Gelman style.

---

## 6. György Buzsáki — systems neuroscience and mechanism

*CW confidence in attribution: HIGH on mechanism and generalisability; LOW on UI / aggregation.*

Buzsáki's contribution (Buzsáki, 2019; Buzsáki, Anastassiou & Koch, 2012) would focus the panel on Target 5 (weak links in mechanism chains) and Target 6 (PNU generalisation), with sharp methodological criticism of how the corpus currently treats neural-mechanism claims.

His standing position is that the field too readily accepts neural-mechanism explanations that have only correlational evidence at the recording-population level, and that real generalisation requires demonstrating the mechanism survives under perturbation. He would treat the 670 weak-mechanism-link beliefs in ae.db as *exactly* the right substrate for mechanism-focused VOI: each weak link is a place where the corpus has accepted a story rather than measured the underlying neural event.

On Target 5 specifically, Buzsáki would propose that the per-link VOI signal weight the *measurability* of the link as a first-order factor. A weak mechanism link that can be addressed by a single, well-designed neurophysiological experiment has higher VOI than a weak link that requires multiple incommensurable approaches. The `weak_link` and `weak_link_credence` fields in `mechanism_chain_quality` give the panel the substrate; the missing piece is a *measurability index* per link.

On Target 6 (PNU generalisation), Buzsáki would be specific about what counts as a generalisation move. Extending a PNU from rodents to humans is one kind of move; extending from healthy adults to clinical populations is another; extending from one neural recording technique to another (LFP to fMRI, say) is a third. The three are not equivalent; he would push for the VOI signal to flag which kind of generalisation each PNU is positioned for.

On Question 4 (score vs flag vs profile), Buzsáki's writing is silent. CW models him as favouring a profile with the mechanism-quality dimensions surfaced explicitly.

On Question 7 (student vs researcher), Buzsáki has written about the responsibility researchers have for their juniors' epistemic development. He would advocate showing students the full mechanism profile (not just a summary), with explanatory scaffolding.

---

## 7. Helen Longino — social epistemology

*CW confidence in attribution: HIGH on community-and-values questions; MEDIUM on operationalisation specifics.*

Longino (Longino, 1990, 2002) would shift the panel's frame from individual-decision VOI to *community-decision VOI*. Her central question would be: whose perspective is encoded in the VOI signal? A VOI value is not a neutral measurement; it is a community judgment about which questions are worth asking. The corpus's existing emphasis (architectural cognition, biophilic design, attention restoration) is a partial answer to "what questions has the field decided are worth asking" — and a Longino-style VOI signal would foreground that partiality.

On Target 7 (paradigm-distinguishing experiments), Longino would push the deepest. Her framework explicitly addresses the question of *competing research programmes* and treats the disagreement between them as epistemically productive rather than as a problem to be resolved. A VOI signal that ranked paradigm-distinguishing experiments highly would, in her view, be doing useful epistemic work for the community.

On Target 10 (WEIRD-extension), Longino's voice would amplify Machery's: she would push for *standpoint-diversity* metadata, not just demographic metadata, on each paper. A paper authored by a research team that includes scholars from the population studied has different epistemic standing than the same paper authored by an outside team.

On Question 6 (corpus completeness), Longino would press hard. Her work argues that what a corpus contains reflects values about what counts as worth indexing; coverage-confidence annotations should foreground this rather than treat it as a technical limit. She would propose adding a *corpus values audit* — periodic review of what kinds of work the corpus systematically underweights — as a process artefact, not just a UI feature.

On Question 3 (aggregation), Longino would resist a composite score on principled grounds beyond Pearl's or Thagard's. Her objection is that compositing hides the value choices that go into the weighting; a multi-dimensional profile is more honest about the social-epistemic situation.

On the new Question 11 (information-theoretic decomposition), Longino's framework provides a corrective: information measures are not neutral. The Shannon-entropy framing treats the question space as flat and equiprobable, but in practice some questions are *more visible* to the field than others, and entropy measures will systematically under-weight the visibility differences. CW models her as wanting the panel to be explicit about this.

---

## 8. Carl Bergstrom — computational information science

*CW confidence in attribution: HIGH on bibliometric-and-information-theoretic questions; MEDIUM on the broader VOI architecture.*

Bergstrom (Bergstrom, 2007; West, Bergstrom & Bergstrom, 2010; Bergstrom & West, 2020) would respond most directly to Question 11 (the information-theoretic decomposition question CW added with him in mind) and to the article-finder coupling (Question 8).

His standing position is that the science-of-science is fundamentally an information-processing problem and that the right tools for analysing literatures are network-and-information-theoretic ones. The Eigenfactor metric (West, Bergstrom & Bergstrom, 2010) treats citation flow as a random walk on a citation graph and computes the stationary distribution; the resulting centrality measure is the information-theoretic analogue of a journal's influence.

For the VOI panel, Bergstrom would propose a similar move on the topic-level VOI computation. Treat each topic as a node in the corpus's topic graph; weight the edges by co-citation, shared authorship, and shared theory tags; compute the stationary distribution; topics with low stationary mass are systematically under-attended-to and have high VOI in the *attention-redirection* sense. This is a different signal than the topic-saturation signal (Target 3) — it captures whether the field's *attention pattern* is misaligned with the topic structure.

On Question 11 specifically, Bergstrom would broadly endorse the partial split CW proposed but would refine it. Coverage-gap targets (3, 8, 10) are best modelled as Kullback-Leibler divergences between the observed corpus-coverage distribution and the corpus-coverage distribution one would expect under uniform-attention; methodological-upgrade targets (1, 2, 4) are best modelled as expected utility gains under a Bayesian decision model. He would propose computing both and surfacing both, with the dual computation itself being a piece of the UI ("this topic ranks high on coverage-gap VOI but low on methodological-upgrade VOI").

On the temporal-decay question (§4 Question 5), Bergstrom's information-theoretic framing helps: the information content of a question is bounded above by the entropy of the answer distribution, which itself decays as evidence accumulates. He would propose an explicit decay model in which the half-life of a VOI value depends on the topic's current citation velocity — fast-moving topics decay faster.

On Question 8 (article-finder coupling), Bergstrom would propose the finder query be phrased in terms of the topic's *citation-walk neighbourhood*: rather than free-text search, find papers within K hops of the topic's central node in the corpus's citation graph. This is information-theoretically principled and fast.

The position Bergstrom's writing leaves least clear is Question 7 (student vs researcher). His work is research-facing rather than pedagogical; CW models him as deferring to the educators on the panel.

---

## Synthesis — what the eight panelists converge on, where they disagree, and what CW proposes as the working operationalisation

### Convergent positions (CW counts ≥ 5 of 8 endorsing)

*The VOI computation should consume AG's V2 credence schema as its substrate.* Every panelist who addressed the substrate question pointed to ae.db: the three-credence values, the warrant-richness counts, the severity field, the weak-mechanism-link records, the theory entrenchment scores, and the scope metadata. None proposed building a parallel data structure. This is the strongest convergence in the synthesis and the most directly actionable. Pearl, Gelman, Mayo, Buzsáki, Bergstrom, and Thagard all endorsed; Machery and Longino were silent but did not object.

*Profile, not score.* Six of eight (Pearl, Gelman, Thagard, Mayo, Buzsáki, Longino) explicitly favoured a multi-dimensional profile over a single composite VOI number. Bergstrom favoured the dual-computation approach (coverage-gap + methodological-upgrade) which is profile-shaped at the top level. Machery was silent. The single convergent answer to Question 3 (aggregation) and Question 4 (score vs flag vs profile) is **profile**.

*The article-finder coupling should be structural, not free-text.* Pearl (counterfactual phrasing), Gelman (Bayesian-model-aware retrieval), Bergstrom (citation-walk neighbourhood) all argued against treating the finder query as a string match. The convergent answer to Question 8: the finder query should be a structured query against the corpus's existing graph (topic crosswalk + citation network + theory tags). Free-text search is a fallback.

*Severity belongs at the centre.* Mayo, Gelman, and Pearl converge on severity as a first-class input to every VOI computation. AG's `severity` field [0.35, 0.90] is the substrate; it should feed into all ten target-specific VOI signals.

### Contested positions (DK adjudication needed)

**Composite-score-vs-pure-profile (Question 3).** Pearl, Thagard, Mayo, and Longino are vehement that aggregating across the ten targets hides the structural distinctions the user should be reasoning about. Bergstrom proposes the partial composite of two information-theoretic kinds (coverage-gap + methodological-upgrade). Gelman is silent but his Bayesian-workflow writing suggests he would prefer a multilevel-model formulation. **CW's reading**: the working operationalisation should be a 10-dimensional profile, with two derived information-theoretic summaries (coverage-gap and methodological-upgrade) and no single composite. DK to confirm.

**Severity-versus-coherence as the primary substrate (Question 11).** Mayo would build the panel around severity; Thagard around coherence. Both are present in AG's V2 schema but the question is which is the *primary* signal feeding the per-target VOI computations. **CW's reading**: severity is more directly operational (it is a per-paper number); coherence is more synoptic (it is a topic-level or network-level number). Use both: severity at the per-paper layer, coherence at the topic layer. DK to confirm.

**Information-theoretic decomposition as the panel's framework (Question 11 again).** Bergstrom would treat the ten targets as a mix of Shannon-entropy reductions (Targets 3, 8, 10) and expected-utility gains (Targets 1, 2, 4); Mayo would resist this as Bayesian-decision-theoretic in a way her error-statistics framework rejects; Longino would push back on the neutrality of Shannon measures. **CW's reading**: this is the genuinely contested philosophical question of the synthesis. CW recommends the operationalisation use the decomposition as a *presentation* device (label each target as coverage-gap-kind or methodological-upgrade-kind) without committing to either framework as the deep semantics. DK to confirm.

**Student-vs-researcher computation (Question 7).** All panelists who addressed the question favoured a single computation projected differently for the two audiences. None advocated two distinct computations. The contested point is *how* to project. **CW's proposal**: compute the full 10-dimensional profile; for students, project to the three or four targets that are feasibility-relevant for a 7-to-10-week class project (Targets 1, 2, 4, 8); for researchers, surface all ten. The feasibility filter is the projection, not a separate VOI. DK to confirm.

**Decay and freshness (Question 5).** Gelman favours stamping with a date and corpus-size rather than auto-decay; Bergstrom favours an explicit decay model tied to topic citation velocity. **CW's reading**: implement Gelman's stamping first (simpler, honest about uncertainty); add Bergstrom-style velocity-based decay as a second-pass refinement once the substrate has been live for two quarters and we have data to calibrate against. DK to confirm.

### CW's proposed working operationalisation — for DK adjudication

Based on the synthesis, the operational VOI for the Knowledge Atlas should have the following shape. (DK should treat this as a proposal, not a settled design.)

**Per paper.** Carry the existing AG V2 fields (severity, warrant_packet_n_supporting, warrant_packet_defeat_status, the three credences, scope metadata) plus *one new derived field*: a target-vector of length 10, where each entry is the per-paper VOI contribution to its target. Entries for Targets 1, 2, 4 are derived from methodological-upgrade signals (low severity → high VOI for retest); entries for Targets 5, 6 are derived from mechanism-chain weak-link records; entries for Targets 3, 8, 10 are derived from coverage-distribution divergences over the corpus.

**Per topic.** Aggregate the per-paper target-vectors into a topic-level target-vector. Display the topic's target-vector as a small grid (the "VOI panel" of Surface 5) with one cell per target. Each cell shows a categorical (high / medium / low) plus a one-line rationale plus an article-finder query.

**Per question (when the user has a specific question).** Compute the question's positioning on the same target-vector (does the question target Target 3? Target 7?). Combine with the topic-level vector to produce a per-question recommendation.

**For COGS 160 students.** Project the target-vector to the four feasibility-relevant targets (1 better stimuli, 2 better measures, 4 confound deconfounding, 8 replication). Hide the rest by default; expose under "Show advanced VOI" for the curious.

**For researchers.** Show the full 10-dimensional target-vector. Surface the dual information-theoretic summary (coverage-gap subtotal, methodological-upgrade subtotal) as a small dashboard at the top.

**Article-finder coupling.** Every cell in the VOI panel carries a finder query; the query is structured (target X cell on topic T → corpus retrieval over papers tagged with topic T and design-class matching target X) rather than free-text. A "Has this been done?" button on each cell runs the query.

**Temporal annotation.** Every VOI value is stamped with its computation date and the corpus size at computation time. No auto-decay in the first release.

---

## What this synthesis unblocks

This synthesis is sufficient for the *next* layer of implementation work to proceed without waiting for the real panel. Specifically, it unblocks:

- **UJ-A4** (substitution-skill build spec for Codex): the refusal-criteria and confidence-display open questions had Mayo and Machery as the gating perspectives; CW now has working positions from both.
- **UJ-A5** (V7-Lite build spec for Codex): the panel's positions on what data the V7-Lite output should carry are recoverable from the synthesis.
- **UJ-D** (substitution skill build): the panel-blocked sub-tasks now have working positions; real-panel revision can come in a second pass.
- **UJ-H** (methodological-pitfalls page tagging): Mayo and Machery's positions on green/yellow/red are now sketchable.

The simulation should *not* close the real panel sprint (UJ-F). The simulated panelists have engaged the questions the way their published work suggests; they have not engaged with each other, and they have not had the chance to revise their positions in response to the synthesis. The real panel is still a worthwhile exercise. But CW can now proceed ballistically on the implementation specs without waiting.

---

## References

Bergstrom, C. T. (2007). Eigenfactor: Measuring the value and prestige of scholarly journals. *College & Research Libraries News*, *68*(5), 314–316.

Bergstrom, C. T., & West, J. D. (2020). *Calling bullshit: The art of skepticism in a data-driven world*. Random House.

Buzsáki, G. (2019). *The brain from inside out*. Oxford University Press.

Buzsáki, G., Anastassiou, C. A., & Koch, C. (2012). The origin of extracellular fields and currents — EEG, ECoG, LFP and spikes. *Nature Reviews Neuroscience*, *13*(6), 407–420.

Gelman, A., & Carlin, J. (2014). Beyond power calculations: Assessing Type S (sign) and Type M (magnitude) errors. *Perspectives on Psychological Science*, *9*(6), 641–651.

Gelman, A., & Loken, E. (2014). The statistical crisis in science. *American Scientist*, *102*(6), 460–465.

Longino, H. E. (1990). *Science as social knowledge: Values and objectivity in scientific inquiry*. Princeton University Press.

Longino, H. E. (2002). *The fate of knowledge*. Princeton University Press.

Machery, E. (2017). *Philosophy within its proper bounds*. Oxford University Press.

Machery, E. (2020). What is a replication? *Philosophy of Science*, *87*(4), 545–567.

Mayo, D. G. (2018). *Statistical inference as severe testing: How to get beyond the statistics wars*. Cambridge University Press.

Mayo, D. G., & Spanos, A. (Eds.). (2010). *Error and inference: Recent exchanges on experimental reasoning, reliability, and the objectivity and rationality of science*. Cambridge University Press.

Pearl, J. (2009). *Causality: Models, reasoning, and inference* (2nd ed.). Cambridge University Press.

Pearl, J., & Mackenzie, D. (2018). *The book of why: The new science of cause and effect*. Basic Books.

Thagard, P. (1989). Explanatory coherence. *Behavioral and Brain Sciences*, *12*(3), 435–467.

Thagard, P. (1992). *Conceptual revolutions*. Princeton University Press.

Thagard, P. (2007). Coherence, truth, and the development of scientific knowledge. *Philosophy of Science*, *74*(1), 28–47.

West, J. D., Bergstrom, T. C., & Bergstrom, C. T. (2010). The Eigenfactor metrics: A network approach to assessing scholarly journals. *College & Research Libraries*, *71*(3), 236–244.
