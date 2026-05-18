# Response to DK's Comments on the User-Journeys Framing
*David Kirsh, 2026-05-17 inline comments → CW design response, 2026-05-18*

This document is the working reply to DK's seven inline comments on `USER_JOURNEYS_THINKING_2026-05-17.md` and `ka_week1_wireframe_2026-05-17.html`. Comment 7 (VOI operationalisation) is addressed by the separately committed panel-context document `docs/VOI_OPERATIONALISATION_PANEL_CONTEXT_2026-05-17.md`. The remaining six comments are taken in order.

The response is written in the design-document register: each section names the underlying design problem, sketches what the surface or skill should contain, identifies the literature that informs the design, and where appropriate distinguishes settled science from active disagreement. None of the proposals are presented as final. Where the proper move is to consult the expert panel rather than decide here, that is said explicitly.

---

## §1. The VR-measurability page (DK comment 1)

**DK's point.** The Week-1 student must be told, explicitly and as a distinct lesson, what VR can and cannot measure. The current draft implies this is implicit in the pruning step; DK is correct that it must be its own surface.

**What the page should do.** Two things, in this order. First, give the student a *positive* taxonomy of measures that are deployable in a 7-week classroom VR project. Second, give the student a *negative* taxonomy of measures that are not deployable in that envelope and a brief justification for each exclusion. Both taxonomies are necessary; an exclusion list alone is dispiriting and incomplete.

**Positive taxonomy (what VR *can* measure in a classroom envelope).** I propose four families, organised by the substrate of the measurement rather than by the construct it indexes, because students will reason from "what hardware do I have" not from "what construct do I want."

The first family is *behavioural traces from the headset and controllers themselves*. Head pose, locomotion path, gaze direction (on the better commercial headsets — Quest Pro, Vive Pro Eye, Varjo XR-3 — and absent on the consumer Quest 2/3), hand pose where available, and time-stamped interaction events. These are essentially free; the engine records them. Foundational work establishing that these traces are valid behavioural measures rather than mere telemetry includes Loomis, Blascovich and Beall (1999) and the more recent review by Pan and Hamilton (2018).

The second family is *task-embedded performance measures*. Response latency on a probe, accuracy on a recognition or change-detection task, error rate on a navigation task, memory accuracy after a delay, choice fraction on a forced-choice task. These do not require any sensor beyond the headset; they require only that the experimenter design a task whose performance produces a number. The literature on VR-as-cognitive-laboratory (Bohil, Alicea & Biocca 2011; Parsons 2015) is the relevant background; the lineage extends from controlled-stimulus presentation in the 1970s but the move into immersive contexts is more recent.

The third family is *verbal and questionnaire-based self-report*. The student presents a validated scale within the headset or immediately on exit. This includes presence questionnaires (the Slater-Usoh-Steed questionnaire and its successors; Schubert, Friedmann & Regenbrecht 2001), affective state inventories, perceived restorativeness scales, and so on. The page must warn the student that self-report in immersive contexts is a legitimate but specific kind of evidence — it indexes the participant's reportable experience, not the underlying processes that produced it.

The fourth family is *physiological signals from wearable peripherals*. Heart rate and heart-rate variability from a chest strap or wrist-worn device, galvanic skin response from a wristband, pupillometry from an eye-tracking headset, and on the more capable systems, EEG via integrated dry electrodes (the Galea project, the Looxid Labs Link). The page should be candid that physiological instrumentation in a 10-week class project trades reliability for ambition; a student attempting EEG will likely produce uninterpretable data.

**Negative taxonomy (what VR *cannot* measure in a classroom envelope).** Here the page should be specific rather than gestural. The exclusions, with brief justifications:

* *fMRI BOLD signals.* The participant cannot be in a head-mounted display and a scanner simultaneously in any setup the student has access to. A small literature on simulated-display fMRI exists, but the substitution is poor.
* *Long-term field outcomes.* Measures that require weeks or months of follow-up (real-world reduction in clinical symptoms, long-term cognitive change, behavioural change in everyday life) cannot be obtained in a 7-week window.
* *Naturalistic social signals beyond the dyad.* VR can support two-person interaction studies (Pan & Hamilton 2018), but multi-party social-physiological synchrony requires coupled hardware that classes typically lack.
* *Real-environment cross-validation.* Studies whose claim is precisely that the effect transfers to the real world cannot be settled with VR alone; the student should be warned that they are testing a within-VR claim, not a transfer claim.
* *Pharmacological or clinical biomarkers* requiring blood, saliva, or other tissue sampling without lab support.

**Substitution principle.** The page must close with a transition into the substitution skill (§2): the fact that the original paper's measure is on the negative list does not necessarily mean the *underlying construct* is unmeasurable. If the construct can be indexed by a measure on the positive list, the project remains viable.

**Open question for panel.** What is the right level of formality for the validity argument the student must make when substituting a measure? Researchers would invoke construct-validity arguments in the Cronbach-Meehl (1955) tradition; class projects probably need a lighter touch. This belongs in the Machery / Mayo review of the methodological pitfalls page.

---

## §2. The substitution skill (DK comment 2)

**DK's point.** A paper that tests a conjecture with an unusable measure may still be testable in VR if the student can substitute a usable measure. We need an agent or skill that proposes acceptable substitutions.

**What the skill is, formally.** Given a target construct $C$ and an unusable measure $m_{\text{orig}}$ in a candidate paper, return a ranked list of VR-feasible measures $m_1, m_2, \ldots$ that index $C$, each annotated with: (a) the construct-validity warrant linking $m_i$ to $C$, (b) reliability information where available, (c) known weaknesses of $m_i$, and (d) a recommendation strength.

The skill is not a generative-text dressing on a knowledge base; it is fundamentally a *retrieval and ranking* problem over a curated measure-substitution graph. The generative layer is responsible only for the natural-language explanation, not the substantive recommendation. This matters because the failure modes of generative-only systems in this kind of task (Bender et al. 2021; the hallucination literature more broadly) are unacceptable in pedagogical use: a student who is told a substitution exists when it does not will design an experiment that cannot be defended.

**What the knowledge base needs.** Three interlinked tables.

The first is a *construct-to-measure* table: for each construct in the corpus, the list of measures the field has used to index it, with citations. This is the same kind of structure that the Inventory of Construct Measures (Bandalos 2018) and the EMBASE-style measurement dictionaries produce, but corpus-specific to the Knowledge Atlas papers.

The second is a *measure-to-VR-feasibility* table: for each measure, a Boolean (or graded) judgement of whether the measure can be obtained in a classroom VR project, with the rationale that places it on the positive or negative list of §1.

The third is a *measure-to-measure substitutability* graph: an edge from $m_i$ to $m_j$ when the psychometric literature treats them as alternative operationalisations of the same construct, with citations to studies that have used them interchangeably or compared them directly.

Building this knowledge base is itself a substantial project. The honest answer is that the literature on measurement equivalence (Vandenberg & Lance 2000; Flake & Fried 2020) is the place to start, but the corpus-specific population of the tables will require LLM-assisted extraction over the Knowledge Atlas papers, with panel review of the resulting graph. Construct proliferation — different labels for what is arguably the same construct — is endemic in psychology (Block 1995; Le, Schmidt, Harter & Lauver 2010), and a substitution skill that takes paper-reported labels at face value will recommend false substitutions.

**Risk and the role of the panel.** The substitution skill is the single point in the COGS 160 Fall pipeline where a generative-AI failure can derail an entire student project. The panel should weigh in on: (a) the right level of confidence-display in the recommendation, (b) the criteria for refusing to recommend any substitution (rather than recommending a poor one), and (c) whether to make the skill's reasoning transparent to the student or to abstract it behind a graded recommendation.

**Pedagogical wrinkle.** DK has previously said that a class project should not become a measurement-development project. The substitution skill therefore has an upper bound on novelty: it should propose substitutions the field has already accepted, not invent new ones. The skill's affordances should reflect this: "this substitution has been used in N peer-reviewed studies" should be a recommendation-strength input.

---

## §3. Bibliography differentiation and meta-review tables (DK comment 3)

**DK's point.** Building a bibliography must be an interactive process. We should facilitate this by differentiating papers in a collection, possibly with a short meta-review that includes tables showing what distinguishes them.

**The underlying design problem.** A student in Week 2 of COGS 160 has been handed (or has selected) a set of 8–12 papers on their topic. The default presentation — title, abstract, citation count, year — is uninformative about the kinds of differences that will shape their experimental design choice. The student does not yet know what features of a paper are decision-relevant. The bibliography page should both *show* the differentiating features and *teach* the student which features to attend to.

**The schema for the differentiation table.** Each paper in the collection gets a row. Columns, in order of pedagogical priority:

* *Theoretical framework.* Which theory does the paper test, instantiate, or extend? Where multiple theories are at stake (the common case), all are listed with the dominant one first.
* *Population.* Sample size, age range, sex composition, cultural background, recruitment channel. The WEIRD-or-not classification (Henrich, Heine & Norenzayan 2010) is a single derived column from this; it should be visible.
* *Stimulus class.* What was actually shown to participants? Natural images, generated images, VR environments, lab apparatus, narrative text, video. This column is unusually important for Knowledge Atlas because the corpus is heterogeneous in stimulus type.
* *Design.* Cross-sectional vs longitudinal; between-subjects vs within-subjects; observational vs experimental; pre-registered or not. The taxonomy follows the Shadish, Cook and Campbell (2002) inheritance.
* *Outcome measures.* The canonical battery, in technical language with a hover-tooltip plain-language gloss. Where measures fall on the negative VR list of §1, the cell is flagged.
* *Statistical strategy.* The headline test (ANOVA, regression, multilevel model, Bayesian model). Open-data status if available.
* *Effect direction and magnitude.* The headline finding, in the paper's own terms (positive/null/negative effect on the primary DV) and the reported effect size translated to a common metric where possible (Cohen's $d$, $\eta^2$, OR, depending on the design). Where the paper reports no effect size, the cell shows the test statistic and the conventional translation.
* *Sample-size adequacy.* A derived flag — was the study likely powered to detect the effect it reports? This invokes the Maxwell (2004) and Button et al. (2013) literature on underpowered psychology and neuroscience studies.
* *Replication record.* Has the study been included in a replication attempt? If so, what was the outcome? This column borrows from the Scite.ai approach (Nicholson et al. 2021) of labelling citations as supporting, contrasting, or mentioning.
* *Methodological strengths and weaknesses.* Two short prose cells — what the paper does well and what it does poorly. These are the most LLM-generated cells in the table and the cells most in need of panel review for accuracy.

**Interactive facets.** The student should be able to filter or group on any column and have the table re-sort. When the student selects a subset (say, "the four papers using VR stimuli"), the system runs a short LLM-assisted differentiation pass that produces a paragraph: "These four papers share VR delivery but differ on the following dimensions...". The differentiation paragraph is a synthesis output, not a header — it is generated on demand from the row data the student has filtered.

**Why this works pedagogically.** The systematic-review tradition (Higgins & Thomas 2019, the Cochrane Handbook; Cooper, Hedges & Valentine 2019, the Handbook of Research Synthesis) shows that the discipline of building such a table forces the student to confront methodological differences they would otherwise glide over. The classic finding from research-synthesis methodology is that the act of operationalising the inclusion criteria — what counts as the same construct, what counts as the same design — is where the genuine intellectual work happens.

**What this is not.** This is *not* a meta-analysis. The differentiation table is descriptive: it surfaces heterogeneity so the student can reason about it. The further step of pooling effect sizes formally (Borenstein, Hedges, Higgins & Rothstein 2009) is researcher work, not class work.

**Open question for panel.** What is the right balance between automatic differentiation and student-built differentiation? An LLM that fills the table from the paper PDF is fast but trains the student in passive consumption; a template that the student fills with the LLM as a sounding board is slower but more pedagogically valuable. This is a curriculum question, not a software question, and belongs in the Thagard/Machery exchange on epistemic virtues.

---

## §4. Citation-graph exemplars for the researcher view (DK comment 4)

**DK's point.** The researcher-facing bibliography view promises to "expose its citation graph, its replication structure, its theoretical diversity, and its methodological span." DK observes this is going to be hard to do in an easy-to-understand manner and asks for exemplars.

**The state of the art, by feature.** There is no single tool that does all four things well. I survey what exists, by feature, with brief commentary on what works visually.

*Citation graph as a first-glance affordance.* The clearest exemplar is **Connected Papers** (connectedpapers.com), which produces a force-directed graph in which nodes are papers, edges encode co-citation similarity rather than direct citation, node size is a citation-count proxy, and node colour encodes year. The user reaction is immediate: clusters are visible, central papers are large, recent papers are dark. The downside is that it is built on Semantic Scholar's data and inherits any indexing gaps, and that it works one paper at a time rather than over a curated set. **ResearchRabbit** (researchrabbitapp.com) is its main competitor; it offers an explicit "earlier work" and "later work" pivot, integrates Zotero, and is, in practice, more usable for building a bibliography rather than exploring around a single paper. Both tools are evidence that the bare citation graph is comprehensible to non-specialists when the visualisation is simple. **Inciteful** (inciteful.xyz) does similar work with a cleaner network-centrality readout.

*Citation graph as bibliometric analysis.* **VOSviewer** (van Eck & Waltman 2010) is the academic-grade tool. It does co-citation, co-authorship, co-word, and bibliographic-coupling analyses; the visualisations are dense and information-rich but require training to read. For a researcher who already knows bibliometric conventions, this is the gold standard. For a researcher who is bibliometrically naive, it is not. The Knowledge Atlas researcher view should probably not lead with VOSviewer-style displays, but it should offer them as an "advanced view."

*Replication structure.* The clearest exemplar is **Scite.ai** (scite.ai), which annotates each citation with one of three labels — *supporting*, *contrasting*, or *mentioning* — derived from the citing-sentence context (Nicholson, Mordaunt, Lopez et al. 2021). At a paper level, the user sees a small bar chart of incoming citation-types and can drill into the actual citing sentences. This is the closest analogue to "replication structure" in the wild, although strict replication is rarer than the *supporting / contrasting* split implies. A complementary tool is **Curate Science** (curatescience.org; LeBel, Vanpaemel, Cheung & Campbell 2018), which is more narrowly focused on tracking direct and conceptual replications and is exactly what a researcher building a replication-aware bibliography needs. The Z-curve approach of Schimmack (replicationindex.com) is a more statistical signal of replication-likelihood across a literature; it is not, however, easy to read.

*Theoretical diversity.* This is the hardest feature to visualise. The closest exemplar is **Open Knowledge Maps** (openknowledgemaps.org; Kraker, Schramm & Kittel 2018), which uses text-mining on a search-result corpus to produce a cluster-bubble map in which each bubble is a topical sub-area. The visualisation is intuitive — researchers grasp the affordance within seconds. For a Knowledge Atlas-specific instantiation, the relevant analogue would be to run topic modelling over the abstracts of a researcher's curated bibliography and present the resulting clusters as a bubble map.

*Methodological span.* No widely-used tool surfaces this directly. The literature's standard artefact is the PRISMA flow diagram (Page, McKenzie, Bossuyt et al. 2021), which is static and built for systematic reviews. A faceted-search affordance over the differentiation table of §3 — where one of the facets is "design type" — is probably the most tractable route. Colour-coding the citation-graph nodes by design type (RCT vs observational vs simulation, for instance) gives the researcher a quick sense of how methodologically diverse the literature is.

**Recommendation for the Knowledge Atlas researcher view.** Build in three layers, not all at once. The first layer is a Connected-Papers-style citation graph over the user's selected bibliography, with no analytical overlay — the goal is orientation. The second layer adds Scite.ai-style citation-type labels (supporting / contrasting / mentioning) on the edges, derived from our own corpus-internal extraction; this gives the replication-structure feature. The third layer adds topic-cluster colouring on the nodes, derived from a corpus-wide topic model. VOSviewer-style multi-network displays are deferred to an "advanced views" page that the researcher opts into.

**Caveat on what we can build natively versus link out to.** Many of these tools are not open-source; we cannot legally embed them. We can: (a) link out from the researcher view to Connected Papers / ResearchRabbit / Scite for the relevant paper-set, (b) build our own simplified analogue using D3.js or Cytoscape.js (Smoot, Ono, Ruscheinski, Wang & Ideker 2011) over our extracted citation data, or (c) ingest open bibliometric data via OpenAlex (Priem, Piwowar & Orr 2022). My recommendation is the combination: build our own minimal graph and link out for the deep dive. That respects the time budget and avoids reimplementing tools that already work well.

---

## §5. Two-stage measure handling (DK comment 5)

**DK's question.** DK says: "I thought this [finding alternative measures] was impossible owing to your pruning in week 1. But choosing among possible measures remains a big deal."

**The clarification.** The pruning and the choice operate on different things, at different stages, and they interlock rather than substitute for each other.

*Week 1 pruning operates on topics.* A topic is admitted to the student's candidate list if and only if there exists *at least one* VR-feasible measure that indexes its central construct. A topic is pruned if its construct can only be indexed by measures on the negative list of §1 — fMRI BOLD signals, multi-month longitudinal follow-up, real-world clinical endpoints. Pruning is binary at the topic level.

*Week 3 choice operates on measures, within an admitted topic.* The student has settled on a topic; the topic has multiple admissible measures; the student must pick one. The choice is not binary: each admissible measure has its own profile of psychometric strengths and weaknesses, and the trade-offs surface only when the student examines the candidate measures side by side.

*Why both stages exist.* The substitution skill (§2) is invoked at both stages but answers different questions. At the pruning stage it answers: *Is there any admissible measure?* At the choice stage it answers: *Among the admissible measures, which is most defensible given the trade-offs?* The first question is yes/no; the second is ranking-with-rationale.

*Worked example: attention restoration theory.* A student is interested in whether immersive natural-scene VR produces attention restoration (Berman, Jonides & Kaplan 2008; Kaplan 1995). The Week-1 pruning operates as follows. The construct "attention restoration" is admissible because at least the following VR-feasible measures index it: pupillometric markers of mental effort, sustained-attention task accuracy (variants of the Sustained Attention to Response Task; Robertson, Manly, Andrade, Baddeley & Yiend 1997), subjective restoration scales (the Perceived Restorativeness Scale; Hartig, Kaiser & Bowler 1997), and reaction time on attention-network tasks (Fan, McCandliss, Sommer, Raz & Posner 2002). Topic admitted.

The Week-3 choice operates as follows. The student now must pick among these measures. Pupillometry requires a headset with eye-tracking — Quest 2 cannot, Quest Pro can. The sustained-attention task is robust but boring and may produce floor or ceiling effects depending on dosage. The Perceived Restorativeness Scale is convenient but subjective and vulnerable to demand characteristics. The Attention Network Task is sensitive but long. The student must trade these off given the hardware they have, the participant pool they can recruit, and the precision they need. This is the choice problem.

*Implication for the wireframe.* The Week-1 surface should mention the substitution skill but only in its admit/reject mode. The Week-3 surface should expose the substitution skill in its ranking mode and pair each candidate measure with the relevant psychometric history. This is a minor revision to the existing wireframe, not a structural change.

---

## §6. Methodological pitfalls page — beyond Cook and Campbell (DK comment 6)

**DK's point.** A separate explanatory page on methodological pitfalls is needed. It should cover not just Cook and Campbell's threats but other pitfalls. Even if 160 students cannot meet all the restrictions a researcher would, they should know of the restrictions and meet them where they can.

**Architecture of the page.** I propose a five-section structure. Each section names a family of pitfalls, lists the canonical sources, gives the brief gloss, and ends with a *student-tolerable / researcher-required* tag for each pitfall — making explicit which the 160 student is expected to address and which they are merely expected to know about.

**Section 1: Validity threats (Cook & Campbell's framework).** The canonical taxonomy (Cook & Campbell 1979; updated in Shadish, Cook & Campbell 2002) decomposes validity into four kinds and lists threats to each. *Internal validity* (history, maturation, testing, instrumentation, regression to the mean, selection, attrition, ambiguous temporal precedence). *External validity* (interaction of selection with treatment, of setting with treatment, of history with treatment). *Construct validity* (inadequate explication of constructs, mono-operation bias, mono-method bias, confounding of constructs with levels, experimenter expectancies, novelty effects). *Statistical conclusion validity* (low power, violated assumptions, unreliable measures, restriction of range). The student should be able to annotate their own proposal against this list and identify which threats their design controls for.

**Section 2: The replication-crisis pitfalls.** These are not in Cook and Campbell because they were not yet salient when the framework was written. The relevant literature emerged from the early 2010s and is now broadly settled in its empirical claims, though contested in its remedies.

The *underpowered-study problem* (Maxwell 2004; Button, Ioannidis, Mokrysz et al. 2013) — most published psychology and neuroscience studies have power well below the conventional 0.80 threshold to detect their reported effect sizes, with the consequence that even successful replications produce inflated effect estimates.

The *garden of forking paths* (Gelman & Loken 2014) — analytical flexibility, when undisclosed, inflates false-positive rates regardless of the researcher's intent. The student version is: pre-register, or document analytical choices, or both.

*p-hacking and HARKing* (Simmons, Nelson & Simonsohn 2011; Kerr 1998) — the explicit or implicit reshaping of hypotheses after observing data. This is a single norm but it generates multiple downstream problems.

The *file-drawer problem* (Rosenthal 1979) — the literature systematically over-represents positive findings because negative findings are less likely to be published, with the consequence that any reading of "the field" overstates the strength of the effect.

For 160 students, the practical norm should be: state your hypothesis before running the experiment; do not change it post hoc; report what you did, not what your analysis would have looked like in a counterfactual world; pre-register if you have time. None of these requires extensive infrastructure.

**Section 3: Construct-validity pitfalls beyond Campbell-Fiske.** Cook and Campbell inherited the construct-validity framework from Campbell and Fiske (1959), but the contemporary literature has elaborated it considerably.

*Jingle-jangle fallacies* (Block 1995; Marsh 1994) — the same label applied to different constructs (jingle) and different labels applied to the same construct (jangle). Both are epidemic in psychology; the student building a bibliography on a topic will encounter this almost immediately.

*Construct proliferation* (Le, Schmidt, Harter & Lauver 2010) — the tendency of research traditions to multiply nominally distinct constructs that are empirically nearly-identical. The diagnostic is a high correlation between purportedly distinct scales.

*Measurement schmeasurement* (Flake & Fried 2020) — the broader pattern of underspecified construct claims, ad-hoc scale construction, and insufficient psychometric reporting. This paper is the field's contemporary statement of the problem and is appropriate as the page's recommended reading.

For 160 students, the practical norm is: when you choose a measure, justify it as a measure *of the construct* you care about — not merely as something the prior paper used.

**Section 4: Sample-related pitfalls.** *WEIRD bias* (Henrich, Heine & Norenzayan 2010) — psychological samples are disproportionately drawn from Western, Educated, Industrialised, Rich and Democratic populations, and many findings do not generalise outside this base. The student should record their sample's WEIRD profile in the differentiation table (§3) and be candid in the write-up about what that means for generalisation.

*Convenience sampling* — the standard undergraduate-pool sample has well-known limitations on age, prior exposure, and motivation. This is a "researcher-required" not a "student-tolerable" pitfall in the strict sense — class projects almost always use convenience samples — but the student should still report it as a limitation.

**Section 5: VR-specific pitfalls.** These are pitfalls the broader literature does not yet treat as canonical but which are well-known in the VR research community.

*The presence confound* (Slater, Lotto, Arnold & Sanchez-Vives 2009; Slater 2009) — VR-specific outcomes may be driven by participants' degree of presence in the virtual environment rather than by the manipulation of interest. A study comparing two virtual environments may be measuring relative presence rather than relative effect of the content. The standard remedy is to measure presence as a covariate.

*Hardware-specific effects* — different headsets, different field-of-view, different refresh rates, and different controller-tracking quality produce different baselines. A study run on Quest 2 does not straightforwardly replicate on Vive Pro.

*The novel-medium effect* — participants unfamiliar with VR show inflated responses to almost any VR content, simply because the medium itself is novel. After two or three sessions the effect attenuates. The remedy is either pre-exposure or explicit treatment of the first-VR-session-effect as a confound.

**Section 6: Theory and explanation pitfalls.** Cook and Campbell are silent on theory-level pitfalls; the relevant literature is in philosophy of science.

*Ad hoc auxiliary hypotheses* (Lakatos 1970; Popper 1959) — when a theory's central claim is protected from disconfirmation by patching with auxiliary hypotheses, the result is what Lakatos called a degenerative research programme. The student should be alert to the move "the effect didn't appear because of [auxiliary]" and ask whether the auxiliary is itself testable.

*Theory-ladenness of observation* (Hanson 1958; Kuhn 1962) — the data the student records are shaped by the framework they use to interpret them. The pedagogical move is awareness, not avoidance.

*Demand characteristics and experimenter effects* (Orne 1962; Rosenthal 1966) — the participant's reading of what the experimenter wants, and the experimenter's unwitting differential treatment of conditions, shape outcomes. Standard remedies are blinding and standardised protocols; class projects can usually achieve at least the latter.

**Student-tolerable versus researcher-required tagging.** Each pitfall in the page should carry a small tag: green for "student-tolerable; class project is fine without addressing this," yellow for "student should address but may have to compromise," red for "student must address." A reasonable first-pass distribution: replication-crisis norms (pre-registration, power, transparent analysis) are yellow at minimum; presence-confound is red for VR projects; WEIRD-bias is yellow (cannot fully address but must report); Cook-Campbell threats are mixed (most are red within VR but some, like maturation in short studies, are green by default).

This pagewill be substantial — likely 5,000–7,000 words of curriculum content. It is not a single afternoon's writing; it is the textual companion to the Cook-and-Campbell-style decision tree work already underway in COGS 160 Fall planning. The expert panel (Mayo on severe testing, Machery on psychological methodology) should review the student-tolerable / researcher-required tagging before it goes live.

---

## §7. VOI — pointer to panel document

DK's comment 7 — "Review the ideas of VOI again and how we can operationalise them in the repo. Call a panel or check to see if one has already commented explicitly on this, Make a list of the VOI criteria and opportunities and then a plan as to how to operationalise them and put them together into natural groupings" — is handled in the separately committed document `docs/VOI_OPERATIONALISATION_PANEL_CONTEXT_2026-05-17.md`. That document enumerates ten VOI targets, six cross-cutting concerns, and seven panelists, and frames ten questions for panel review. Per DK's directive, it explicitly does not propose methods; that is the panel's job. The next step on the VOI workstream is DK's approval of the panel composition before per-panelist briefings are drafted.

---

## §8. What this response *does not* do

This response is a design document. It does not:

* Write the VR-measurability page in full prose; it specifies what should be in it.
* Build the substitution skill; it specifies the data and the failure modes the panel must rule on.
* Produce the differentiation tables for any specific bibliography; it specifies the schema.
* Implement any citation-graph view; it surveys the exemplar tools and recommends a layered build.
* Resolve the two-stage measure question with a normative recommendation; it clarifies what each stage is doing.
* Write the methodological-pitfalls page in full; it specifies the five-section structure and the canonical citations.

The next sub-tasks are written-out below. Each is sized for an independent piece of work and most can be parallelised across CW, AG, and Codex once the panel returns its recommendations on the contested parts.

---

## §9. Concrete next tasks

| ID | Task | Suggested owner | Blocker |
|----|------|-----------------|---------|
| UJ-1 | Draft the VR-measurability page (~2,500 words, four positive + five negative measure families, substitution-principle close) | CW | None |
| UJ-2 | Sketch the substitution-skill data schema (construct-to-measure, measure-to-VR-feasibility, measure-to-measure substitutability) | CW + Codex | Panel input on confidence display and refusal criteria |
| UJ-3 | Build the differentiation-table HTML mockup for a single topic's 8-paper bibliography | CW + Track 4 UX | None |
| UJ-4 | Specify the citation-graph minimal-viable view (D3 force-directed; Scite-style edge labels; topic-cluster colouring) | CW + Track 1 | Open-source library choice (D3 vs Cytoscape.js) |
| UJ-5 | Revise the Week-1 wireframe to make the substitution skill present in both admit-mode and choice-mode | CW | None |
| UJ-6 | Draft the methodological-pitfalls page (~5,000 words, six-section structure, green/yellow/red tagging) | CW | Panel review of tagging |
| UJ-7 | Per-panelist briefing letters for the VOI panel (one page each, tailored to each panelist's expertise) | CW | DK approval of panel composition |

Tasks UJ-1, UJ-3, UJ-5 are unblocked and can begin immediately. UJ-2, UJ-6, UJ-7 await panel input or DK approval. UJ-4 awaits a small technical decision.

---

## References

All references follow APA 7th-edition conventions. Google Scholar citation counts (denoted *gs:N*) are accurate as of late 2024 / early 2025 according to my prior knowledge cut-off and may have drifted; cite the count as approximate when using.

Bandalos, D. L. (2018). *Measurement theory and applications for the social sciences*. Guilford Press. *gs: ≈ 1,200.*

Bender, E. M., Gebru, T., McMillan-Major, A., & Shmitchell, S. (2021). On the dangers of stochastic parrots: Can language models be too big? In *Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency* (pp. 610–623). https://doi.org/10.1145/3442188.3445922 *gs: ≈ 6,000.*

Berman, M. G., Jonides, J., & Kaplan, S. (2008). The cognitive benefits of interacting with nature. *Psychological Science*, *19*(12), 1207–1212. https://doi.org/10.1111/j.1467-9280.2008.02225.x *gs: ≈ 3,500.*

Block, J. (1995). A contrarian view of the five-factor approach to personality description. *Psychological Bulletin*, *117*(2), 187–215. https://doi.org/10.1037/0033-2909.117.2.187 *gs: ≈ 2,600.*

Bohil, C. J., Alicea, B., & Biocca, F. A. (2011). Virtual reality in neuroscience research and therapy. *Nature Reviews Neuroscience*, *12*(12), 752–762. https://doi.org/10.1038/nrn3122 *gs: ≈ 1,800.*

Borenstein, M., Hedges, L. V., Higgins, J. P. T., & Rothstein, H. R. (2009). *Introduction to meta-analysis*. Wiley. https://doi.org/10.1002/9780470743386 *gs: ≈ 36,000.*

Button, K. S., Ioannidis, J. P. A., Mokrysz, C., Nosek, B. A., Flint, J., Robinson, E. S. J., & Munafò, M. R. (2013). Power failure: Why small sample size undermines the reliability of neuroscience. *Nature Reviews Neuroscience*, *14*(5), 365–376. https://doi.org/10.1038/nrn3475 *gs: ≈ 6,200.*

Camerer, C. F., Dreber, A., Holzmeister, F., Ho, T.-H., Huber, J., Johannesson, M., et al. (2018). Evaluating the replicability of social science experiments in Nature and Science between 2010 and 2015. *Nature Human Behaviour*, *2*(9), 637–644. https://doi.org/10.1038/s41562-018-0399-z *gs: ≈ 1,900.*

Campbell, D. T., & Fiske, D. W. (1959). Convergent and discriminant validation by the multitrait-multimethod matrix. *Psychological Bulletin*, *56*(2), 81–105. https://doi.org/10.1037/h0046016 *gs: ≈ 20,000.*

Cook, T. D., & Campbell, D. T. (1979). *Quasi-experimentation: Design and analysis issues for field settings*. Houghton Mifflin. *gs: ≈ 25,000.*

Cooper, H., Hedges, L. V., & Valentine, J. C. (Eds.). (2019). *The handbook of research synthesis and meta-analysis* (3rd ed.). Russell Sage Foundation. *gs: ≈ 6,000 (for editions cumulative).*

Cronbach, L. J., & Meehl, P. E. (1955). Construct validity in psychological tests. *Psychological Bulletin*, *52*(4), 281–302. https://doi.org/10.1037/h0040957 *gs: ≈ 11,500.*

Fan, J., McCandliss, B. D., Sommer, T., Raz, A., & Posner, M. I. (2002). Testing the efficiency and independence of attentional networks. *Journal of Cognitive Neuroscience*, *14*(3), 340–347. https://doi.org/10.1162/089892902317361886 *gs: ≈ 5,400.*

Flake, J. K., & Fried, E. I. (2020). Measurement schmeasurement: Questionable measurement practices and how to avoid them. *Advances in Methods and Practices in Psychological Science*, *3*(4), 456–465. https://doi.org/10.1177/2515245920952393 *gs: ≈ 1,400.*

Gelman, A., & Loken, E. (2014). The statistical crisis in science. *American Scientist*, *102*(6), 460–465. *gs: ≈ 2,300.*

Hanson, N. R. (1958). *Patterns of discovery*. Cambridge University Press. *gs: ≈ 6,500.*

Hartig, T., Kaiser, F. G., & Bowler, P. A. (1997). *Further development of a measure of perceived environmental restorativeness* (Working Paper No. 5). Uppsala University Institute for Housing Research. *gs: ≈ 700.*

Henrich, J., Heine, S. J., & Norenzayan, A. (2010). The weirdest people in the world? *Behavioral and Brain Sciences*, *33*(2–3), 61–83. https://doi.org/10.1017/S0140525X0999152X *gs: ≈ 12,000.*

Higgins, J. P. T., & Thomas, J. (Eds.). (2019). *Cochrane handbook for systematic reviews of interventions* (2nd ed.). Wiley. *gs: ≈ 70,000.*

Kaplan, S. (1995). The restorative benefits of nature: Toward an integrative framework. *Journal of Environmental Psychology*, *15*(3), 169–182. https://doi.org/10.1016/0272-4944(95)90001-2 *gs: ≈ 12,500.*

Kerr, N. L. (1998). HARKing: Hypothesizing after the results are known. *Personality and Social Psychology Review*, *2*(3), 196–217. https://doi.org/10.1207/s15327957pspr0203_4 *gs: ≈ 4,300.*

Kraker, P., Schramm, M., & Kittel, C. (2018). Open Knowledge Maps: Visual discovery based on the principles of open science. *Mitteilungen der Vereinigung Österreichischer Bibliothekarinnen und Bibliothekare*, *71*(1), 99–106. *gs: ≈ 30.*

Kuhn, T. S. (1962). *The structure of scientific revolutions*. University of Chicago Press. *gs: ≈ 130,000.*

Lakatos, I. (1970). Falsification and the methodology of scientific research programmes. In I. Lakatos & A. Musgrave (Eds.), *Criticism and the growth of knowledge* (pp. 91–196). Cambridge University Press. *gs: ≈ 16,000.*

LeBel, E. P., Vanpaemel, W., Cheung, I., & Campbell, L. (2018). A brief guide to evaluate replications. *Meta-Psychology*, *2*, MP.2018.843. https://doi.org/10.15626/MP.2018.843 *gs: ≈ 200.*

Le, H., Schmidt, F. L., Harter, J. K., & Lauver, K. J. (2010). The problem of empirical redundancy of constructs in organizational research: An empirical investigation. *Organizational Behavior and Human Decision Processes*, *112*(2), 112–125. https://doi.org/10.1016/j.obhdp.2010.02.003 *gs: ≈ 600.*

Loomis, J. M., Blascovich, J. J., & Beall, A. C. (1999). Immersive virtual environment technology as a basic research tool in psychology. *Behavior Research Methods, Instruments, & Computers*, *31*(4), 557–564. https://doi.org/10.3758/BF03200735 *gs: ≈ 1,500.*

Marsh, H. W. (1994). Sport motivation orientations: Beware of jingle-jangle fallacies. *Journal of Sport and Exercise Psychology*, *16*(4), 365–380. https://doi.org/10.1123/jsep.16.4.365 *gs: ≈ 700.*

Maxwell, S. E. (2004). The persistence of underpowered studies in psychological research: Causes, consequences, and remedies. *Psychological Methods*, *9*(2), 147–163. https://doi.org/10.1037/1082-989X.9.2.147 *gs: ≈ 1,800.*

Nicholson, J. M., Mordaunt, M., Lopez, P., Uppala, A., Rosati, D., Rodrigues, N. P., et al. (2021). Scite: A smart citation index that displays the context of citations and classifies their intent using deep learning. *Quantitative Science Studies*, *2*(3), 882–898. https://doi.org/10.1162/qss_a_00146 *gs: ≈ 250.*

Open Science Collaboration. (2015). Estimating the reproducibility of psychological science. *Science*, *349*(6251), aac4716. https://doi.org/10.1126/science.aac4716 *gs: ≈ 7,500.*

Orne, M. T. (1962). On the social psychology of the psychological experiment: With particular reference to demand characteristics and their implications. *American Psychologist*, *17*(11), 776–783. https://doi.org/10.1037/h0043424 *gs: ≈ 8,000.*

Page, M. J., McKenzie, J. E., Bossuyt, P. M., Boutron, I., Hoffmann, T. C., Mulrow, C. D., et al. (2021). The PRISMA 2020 statement: An updated guideline for reporting systematic reviews. *BMJ*, *372*, n71. https://doi.org/10.1136/bmj.n71 *gs: ≈ 90,000.*

Pan, X., & Hamilton, A. F. de C. (2018). Why and how to use virtual reality to study human social interaction: The challenges of exploring a new research landscape. *British Journal of Psychology*, *109*(3), 395–417. https://doi.org/10.1111/bjop.12290 *gs: ≈ 600.*

Parsons, T. D. (2015). Virtual reality for enhanced ecological validity and experimental control in the clinical, affective and social neurosciences. *Frontiers in Human Neuroscience*, *9*, 660. https://doi.org/10.3389/fnhum.2015.00660 *gs: ≈ 1,000.*

Popper, K. R. (1959). *The logic of scientific discovery*. Hutchinson. *gs: ≈ 60,000.*

Priem, J., Piwowar, H., & Orr, R. (2022). OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. *arXiv* preprint. https://doi.org/10.48550/arXiv.2205.01833 *gs: ≈ 200.*

Robertson, I. H., Manly, T., Andrade, J., Baddeley, B. T., & Yiend, J. (1997). 'Oops!': Performance correlates of everyday attentional failures in traumatic brain injured and normal subjects. *Neuropsychologia*, *35*(6), 747–758. https://doi.org/10.1016/S0028-3932(97)00015-8 *gs: ≈ 3,000.*

Rosenthal, R. (1966). *Experimenter effects in behavioral research*. Appleton-Century-Crofts. *gs: ≈ 6,500.*

Rosenthal, R. (1979). The file drawer problem and tolerance for null results. *Psychological Bulletin*, *86*(3), 638–641. https://doi.org/10.1037/0033-2909.86.3.638 *gs: ≈ 12,000.*

Schubert, T., Friedmann, F., & Regenbrecht, H. (2001). The experience of presence: Factor analytic insights. *Presence: Teleoperators and Virtual Environments*, *10*(3), 266–281. https://doi.org/10.1162/105474601300343603 *gs: ≈ 2,000.*

Shadish, W. R., Cook, T. D., & Campbell, D. T. (2002). *Experimental and quasi-experimental designs for generalized causal inference*. Houghton Mifflin. *gs: ≈ 35,000.*

Simmons, J. P., Nelson, L. D., & Simonsohn, U. (2011). False-positive psychology: Undisclosed flexibility in data collection and analysis allows presenting anything as significant. *Psychological Science*, *22*(11), 1359–1366. https://doi.org/10.1177/0956797611417632 *gs: ≈ 8,300.*

Slater, M. (2009). Place illusion and plausibility can lead to realistic behaviour in immersive virtual environments. *Philosophical Transactions of the Royal Society B: Biological Sciences*, *364*(1535), 3549–3557. https://doi.org/10.1098/rstb.2009.0138 *gs: ≈ 2,500.*

Slater, M., Lotto, B., Arnold, M. M., & Sanchez-Vives, M. V. (2009). How we experience immersive virtual environments: The concept of presence and its measurement. *Anuario de Psicología*, *40*(2), 193–210. *gs: ≈ 400.*

Smoot, M. E., Ono, K., Ruscheinski, J., Wang, P.-L., & Ideker, T. (2011). Cytoscape 2.8: New features for data integration and network visualization. *Bioinformatics*, *27*(3), 431–432. https://doi.org/10.1093/bioinformatics/btq675 *gs: ≈ 6,000.*

van Eck, N. J., & Waltman, L. (2010). Software survey: VOSviewer, a computer program for bibliometric mapping. *Scientometrics*, *84*(2), 523–538. https://doi.org/10.1007/s11192-009-0146-3 *gs: ≈ 10,000.*

Vandenberg, R. J., & Lance, C. E. (2000). A review and synthesis of the measurement invariance literature: Suggestions, practices, and recommendations for organizational research. *Organizational Research Methods*, *3*(1), 4–70. https://doi.org/10.1177/109442810031002 *gs: ≈ 9,000.*

---

*End of design response. The follow-on work — drafting the VR-measurability page, the substitution-skill data schema, the differentiation-table mockup, the citation-graph minimal-viable view, and the methodological-pitfalls page — should be discussed at the next planning checkpoint.*
