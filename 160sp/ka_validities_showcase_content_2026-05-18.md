# Cook & Campbell's classic four validities — Week-1 reference for COGS 160 Fall

*Last updated: 2026-05-18. Source-of-truth content for `ka_validities_showcase.html` (Surface 7b of the Week-1 wireframe). The content here is rendered to HTML by the build pipeline; edits land in production when the page rebuilds.*

---

## What this page is

A standalone showcase of the four-validities taxonomy that descends from Campbell & Stanley (1963), reached its canonical statement in Cook & Campbell (1979), and is updated in Shadish, Cook & Campbell (2002). The taxonomy organises the threats a study faces into four categories — *internal*, *external*, *construct*, and *statistical conclusion* validity — and is the standard frame Cognitive Science methodology courses use.

The page is intentionally separated from the broader methodological-pitfalls explainer (Surface 7) because Cook & Campbell's framework deserves direct exposure rather than being subsumed. The broader page covers replication-crisis pitfalls, construct-proliferation, WEIRD bias, demand characteristics, and VR-specific issues that Cook & Campbell do not cover — because they predate them.

In Week 1, read this page once, in full, before you commit to a topic. The four validities are not optional decoration; they are the dimensions on which your project will be evaluated.

---

## How to read the four validities

Every experimental claim can be challenged on four independent grounds. The taxonomy below organises those grounds. Each card names the validity, states the *question* it asks of your study, lists the canonical threats from Shadish, Cook & Campbell (2002) §2, and closes with a "for your VR project" advisory line.

Read each card in sequence; do not stop after the first two. Students who skip construct validity and statistical conclusion validity tend to produce designs that fail at the analysis stage.

---

## Validity 1 — Internal validity

*Did the manipulation cause the change in the outcome, within this study?*

Internal validity is the question of whether the change you observed in the dependent variable was caused by your manipulation of the independent variable, as opposed to by something else that happened to vary alongside it. Cook & Campbell's list of *threats* to internal validity is the canonical inventory of "something elses."

### Classic threats

- **History.** An event other than the manipulation co-occurs with it and may have caused the effect. (A loud fire-alarm during one condition; a heat wave that breaks midway through data collection.)
- **Maturation.** Participants change over time independently of the manipulation. Fatigue, learning, hunger, mood drift across a long session.
- **Testing.** The pre-test itself changes the post-test score. Familiarity with the task is a confound.
- **Instrumentation.** The measure changes between pre and post — a different rater, a different calibration, a software update.
- **Statistical regression to the mean.** Extreme baseline scores naturally regress toward the mean on retest.
- **Selection.** Groups differed before the manipulation began. The classic between-subjects threat.
- **Attrition.** Participants drop out differentially between conditions, biasing the comparison.
- **Ambiguous temporal precedence.** Unclear which variable changed first. The classic correlational threat.

### For your VR project

Random assignment to condition is the strongest single defence against most internal-validity threats. Blinding the experimenter to condition addresses experimenter effects (which technically belong to construct validity but interact with internal). Equating exposure duration across conditions blocks maturation effects within session. Within-subjects designs, with proper counterbalancing, give you the smallest sample requirements and the cleanest internal-validity argument — but be careful that the order itself does not become a confound.

---

## Validity 2 — External validity

*Does the effect generalise — to other people, other settings, other times?*

External validity is the question of whether the effect you observed within your study population, your laboratory, and your time period would also appear in other populations, other settings, and other times. Cook & Campbell's list of threats here is shorter than for internal validity but conceptually deeper.

### Classic threats

- **Interaction of selection with treatment.** The effect works only for the kind of person you sampled. Your effect is real among UCSD undergraduates; it may not transfer to children, to older adults, to clinical populations, or to non-Western populations.
- **Interaction of setting with treatment.** The effect works only in your lab or your VR. Real-world transfer is a separate empirical question.
- **Interaction of history with treatment.** The effect works only at this point in time. Pandemic-era social-distance effects, for example, may not generalise to other periods.

### For your VR project

Report your sample's demographic composition explicitly and acknowledge the VR-specific scope. Do not over-claim transfer to the real world unless your design tests it (this is the X4 exclusion from the VR-measurability page). The honest framing is that your project tests a within-VR effect; whether it transfers is a separate study. Treating the project this way is not a limitation to apologise for — it is methodological precision.

---

## Validity 3 — Construct validity

*Are your independent and dependent variables actually measuring what you say they are?*

Construct validity is the question of whether the *operationalisations* you used — the specific stimuli, instructions, and measures — actually correspond to the *constructs* you claim to be studying. This is often the validity that students think the least about and that grading attends to the most.

### Classic threats

- **Inadequate explication of constructs.** The construct is too vague to operationalise unambiguously. "Stress," "attention," "well-being" all have this problem unless you tighten them.
- **Mono-operation bias.** Only one operationalisation of the IV — other operationalisations might not produce the effect, so the effect is bound to the specific operationalisation you used.
- **Mono-method bias.** Only one measurement method for the DV — biases shared across methods inflate the result; convergent evidence from multiple methods is stronger.
- **Confounding constructs with levels.** Different levels of the IV co-vary with different constructs. A "high vs low ceiling" manipulation also varies brightness, spaciousness, sometimes ventilation; which construct produces the effect?
- **Experimenter expectancies.** The experimenter unconsciously cues participants toward the expected pattern.
- **Novelty and disruption effects.** The participant responds to the novelty of the situation rather than the substantive manipulation.

### For your VR project

Pair a behavioural measure (Family 2 from the measurability page) with a self-report measure (Family 3). If they converge, your construct claim is stronger; if they diverge, you have a substantive finding to interpret. Single-method designs are weaker than they need to be. If your IV is a complex stimulus (a VR scene, a soundscape, a lighting condition), articulate which dimension of it you intend to manipulate and what other dimensions might covary; this is where construct validity is most often lost.

---

## Validity 4 — Statistical conclusion validity

*Given your data, is the inference to "there is an effect" statistically warranted?*

Statistical conclusion validity is the question of whether the statistical inferences you draw — typically "there is an effect" or "there is no effect" — are supported by the data. This is the validity that the replication-crisis literature has been most focused on.

### Classic threats

- **Low statistical power.** Too few participants to detect the effect you are after. Underpowered studies are the most common single failure mode in the cognitive-science literature (Maxwell, 2004; Button et al., 2013).
- **Violated assumptions of statistical tests.** Normality, independence, equal variances. Often defensible by recourse to non-parametric or robust alternatives, but always check.
- **Fishing and the error rate problem.** Multiple comparisons inflate false-positive rates. If you run 20 tests at α = 0.05, you expect 1 false positive by chance.
- **Unreliability of measures.** Noisy measurement attenuates the effect estimate. A measure with reliability 0.6 cannot detect effects that a measure with reliability 0.9 detects easily.
- **Restriction of range.** A truncated IV or DV reduces detectable variance and inflates effect-size estimates artefactually.
- **Unreliability of treatment implementation.** The manipulation was not delivered the same way every time. Common when the experimenter is also the participant-recruiter.

### For your VR project

Do a power calculation in Week 2 — Cohen (1988) standard tables suffice for a class project, or use G*Power if you want software. The power calculation tells you the minimum sample size for which the effect size you expect would be detectable at conventional α. If the minimum sample size exceeds what you can recruit, change either the design (within-subjects designs require fewer participants) or the expected effect size (be more conservative). Pre-specify your statistical test before you collect data and stick with it; if you change your mind after seeing the data, you have entered the garden of forking paths. Report effect sizes with confidence intervals, not just p-values.

---

## Worked example — why the ceiling-height finding is contested

The Meyers-Levy & Zhu (2007) finding that ceilings ≥ 3.0 m bias participants toward divergent thinking and that ceilings ≤ 2.4 m bias toward analytic thinking is a *construct-validity-and-internal-validity* puzzle. The DYK browser flags it as "Contested" for substantive reasons that the four-validities framework lets us name precisely.

### The construct-validity challenge

The manipulation in the original study is *photographs of high vs low ceilings*. But high-ceiling photographs differ from low-ceiling photographs on multiple dimensions: perceived spaciousness, brightness (high ceilings often correlate with greater light exposure in the photographs), and the visible-vegetation fraction in some image sets. The reported divergent-thinking effect could index any of these constructs — spaciousness, brightness, naturalness — not specifically *ceiling height*. This is *confounding constructs with levels*, the classical construct-validity threat. Until a study varies ceiling height while holding other room properties constant, the field cannot distinguish "ceiling height affects thinking" from "the variables co-varying with ceiling height affect thinking."

### The internal-validity challenge in the replications

The failed replication studies have used different image sets, different presentation durations, and different participant populations. Whether the failures are evidence *against* the effect or evidence *against the operationalisation* is itself contested. From an internal-validity standpoint, the original study's effect could be real *in the original operationalisation* and absent *in the replications' operationalisations* without contradiction — because the operationalisations differ on multiple confounded dimensions.

### What you would have to do to settle it

A within-subjects design that varies ceiling height in VR, holding lighting, vegetation, perceived spaciousness, and other room properties constant — with an independent measure of perceived spaciousness as a covariate. The within-subjects element addresses internal-validity (each participant is their own control, eliminating selection); the constant-other-properties element addresses construct-validity (the manipulation is more nearly *ceiling height alone*).

This is a tractable Week-1 topic if you accept that you are testing a more carefully specified version of the original claim rather than the loose original claim itself. Methodologically, the more carefully specified study is the more valuable study; it tells the field what the effect's true scope is.

---

## Self-check (planned follow-on page)

A separate page (`ka_validities_self_check.html`) is contemplated as a Track-4-style interactive exercise. The student enters their design — IV, DV, sample, statistical plan — and the page guides them through annotating each card with how their design addresses or fails to address each threat. The output is a one-page self-evaluation the student can attach to their Week-1 deliverable.

Scope: UJ task to be specified later. Not part of this page's source-of-truth content.

---

## References

Button, K. S., Ioannidis, J. P. A., Mokrysz, C., Nosek, B. A., Flint, J., Robinson, E. S. J., & Munafò, M. R. (2013). Power failure: Why small sample size undermines the reliability of neuroscience. *Nature Reviews Neuroscience*, *14*(5), 365–376. https://doi.org/10.1038/nrn3475

Campbell, D. T., & Stanley, J. C. (1963). *Experimental and quasi-experimental designs for research*. Rand McNally.

Cohen, J. (1988). *Statistical power analysis for the behavioral sciences* (2nd ed.). Lawrence Erlbaum Associates.

Cook, T. D., & Campbell, D. T. (1979). *Quasi-experimentation: Design and analysis issues for field settings*. Houghton Mifflin.

Gelman, A., & Loken, E. (2014). The statistical crisis in science. *American Scientist*, *102*(6), 460–465.

Maxwell, S. E. (2004). The persistence of underpowered studies in psychological research: Causes, consequences, and remedies. *Psychological Methods*, *9*(2), 147–163. https://doi.org/10.1037/1082-989X.9.2.147

Meyers-Levy, J., & Zhu, R. (2007). The influence of ceiling height: The effect of priming on the type of processing that people use. *Journal of Consumer Research*, *34*(2), 174–186. https://doi.org/10.1086/519146

Shadish, W. R., Cook, T. D., & Campbell, D. T. (2002). *Experimental and quasi-experimental designs for generalized causal inference*. Houghton Mifflin.

---

*The four validities are not a checklist to be ticked. They are four independent ways your study can fail, and four independent ways it can succeed. Read them in Week 1; return to them in Weeks 2, 3, and 9 when you write the hypothesis, the design, and the discussion.*
