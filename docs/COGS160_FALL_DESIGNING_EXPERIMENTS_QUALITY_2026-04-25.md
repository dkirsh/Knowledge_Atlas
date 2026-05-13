# Designing High-Quality Experiments — A COGS 160 Fall Guide

**Document**: `COGS160_FALL_DESIGNING_EXPERIMENTS_QUALITY_2026-04-25.md`
**Audience**: COGS 160 Fall students who are designing — not yet
conducting — an experiment for their seminar project or thesis.
**Companion**: `EXPERIMENTAL_PAPER_QUALITY_FACTORS_2026-04-23.md`,
which covers the same five quality axes from an *evaluator's* point
of view (reading a finished paper). This document covers them from
a *designer's* point of view (planning a study before you collect
data).
**Authorising reviewer**: DK, 2026-04-25.

---

## Foreword — why design-time decisions matter most

There is a useful asymmetry in experimental work that is worth
naming at the start. The cost of a methodological problem rises
sharply with how late in the process it is discovered. A confound
spotted at design time is a free correction. The same confound
spotted at analysis time forces a complicated explanation in the
discussion section. The same confound spotted by a reviewer of a
submitted manuscript forces a revision and resubmission, often with
new data. The same confound spotted after publication, by someone
who tried to build on the finding and could not, costs both the
original authors and the field. The five quality axes a paper is
*evaluated* on (Cook & Campbell 1979 — internal, external,
construct, statistical conclusion validity; plus open-science
transparency from the post-2015 reform literature) are the same
five axes the experiment should be *designed* against. The further
forward in the process you put these considerations, the cheaper
they are to satisfy.

This guide walks each axis as a design problem rather than as an
analysis problem. For each axis, it names the threats Cook and
Campbell identified, the mitigations that address them, the
contemporary additions from the methodological-reform literature,
and a small set of concrete planning prompts you can answer for
your own experiment. The intended use is iterative: read this once
when you are sketching the design, again when you are writing the
preregistration, again when you are presenting to the seminar, and
once more before you collect a single data point. Each pass should
take less time than the one before, because each pass moves more of
the work into the design and leaves less for the rescue afterwards.

A second framing worth naming. The five axes are not a checklist of
constraints imposed by methodology pedants. They are the
specification of what *believability* means in an empirical paper.
Believability is not a stylistic property of the prose; it is a
structural property of the design. A paper whose design is sound on
all five axes is believable even when the writing is dry, and a
paper whose design is weak on internal validity is not believable
even when the writing is luminous. Designing for quality is
therefore designing for credibility — your own future paper's, and
your own future career's.

## 1. Designing for internal validity

Internal validity is the question of whether your experiment lets
you draw the causal inference you intend to draw. Cook and Campbell
(1979, ~37 000 citations on Google Scholar) identified eight threats
that arise in field and quasi-experimental work; Shadish, Cook, and
Campbell (2002) refined but did not displace the list. Most
internal-validity problems are *design* problems — they arise from
not having a comparison group, not having random assignment, not
controlling the timing of measurement — and the design phase is
where they should be addressed.

The first three threats — **history**, **maturation**, and
**testing** — are about events other than your manipulation that
could explain the change you observed. History is external events
(your experiment ran during a campus emergency that changed
participants' baseline state). Maturation is internal change in
participants over the experiment's duration (in a study lasting
several weeks, participants get older and may grow more skilled at
the task regardless of your manipulation). Testing is the effect of
having taken the measure before (a pre-test on a knowledge
assessment teaches participants, biasing the post-test). The design
mitigation for all three is the same: include a control group that
experiences the same history, the same duration, and the same
pre-measurement, but not your manipulation. The control group
absorbs the alternative explanations and leaves only the
manipulation as the unique difference.

The fourth threat is **instrumentation**: changes in the measure
itself between pre- and post-test, or between conditions. A
manual coder whose criteria drift over a long study; a sensor that
loses calibration; a survey whose Likert anchors are reworded in a
new version. The mitigation is calibration at design time: lock the
measurement procedure before data collection begins, document any
adjustment you anticipate making, and apply the same instrument
identically across conditions.

The fifth threat is **statistical regression** (often called
"regression to the mean"). Extreme scores on a pre-test tend to be
less extreme on re-measurement simply because of measurement error.
A study that selects only the lowest-scoring participants and shows
their scores improved after treatment cannot attribute the
improvement to the treatment — regression to the mean predicts it
whether the treatment did anything or not. The mitigation is to
avoid selecting on the pre-test, or to include a control group of
similarly-extreme participants who do not receive the treatment.

The sixth and seventh threats — **selection** and **attrition** —
are about who is in your conditions. Selection is the threat that
people in different conditions differ at baseline (in
quasi-experimental designs without random assignment). Attrition is
the threat that people drop out of different conditions differently
(a stressful condition may produce more dropouts, leaving only the
hardier remainder). Random assignment addresses selection at design
time. Pre-registering an analytic plan that handles attrition (by
intention-to-treat analysis, by multiple imputation, by Heckman
correction where appropriate) addresses attrition at design time.

The eighth threat is **diffusion of treatments**: participants in
different conditions communicate with each other and adopt features
of the other condition. The mitigation is to separate conditions in
space and time, to brief participants on confidentiality, and where
the manipulation involves training, to time-stagger conditions so
training cannot diffuse during the experimental window.

For your design, a small set of planning prompts.

*Does your design have a control group that experiences the same
history, maturation, testing, and instrumentation as the treatment
group?* If no, what alternative explanations does this leave open,
and can you live with them?

*Is assignment to condition random, or quasi-random (matched pairs,
regression discontinuity, instrumental variables)?* If
quasi-random, what selection threat are you accepting and how will
you address it in analysis?

*What is your plan for attrition?* Pre-specify the intent-to-treat
versus per-protocol analysis. If attrition is anticipated to differ
between conditions, plan a sensitivity analysis.

## 2. Designing for external validity

External validity asks whether your causal inference generalises
beyond the conditions of your experiment. Bracht and Glass (1968)
named the populations to which inferences must extend: people,
settings, times, measures, and treatments. Yarkoni (2020,
~700 citations) re-named this the *generalisability crisis* and
argued forcefully that researchers routinely overclaim
generalisability — drawing inferences to "humans" or "behaviour"
from samples and settings that warrant only much narrower claims.

The five generalisation domains map to five design choices.

**People.** Who is in your sample? The WEIRD critique (Henrich,
Heine & Norenzayan 2010, ~10 500 citations) is now the standard
reference: psychology's data are drawn overwhelmingly from Western,
Educated, Industrialised, Rich, Democratic populations, primarily
US undergraduates, and the inferences are routinely extended to
"humans" in a way the sample does not warrant. The design
mitigation is one of three: narrow your claim to match your sample
("WEIRD US undergraduates"), broaden your sample to match your
claim, or design a multi-site replication built in. UCSD's location
gives you some access to diverse sampling that smaller institutions
do not.

**Settings.** Where will the experiment run? A laboratory
environment offers control but limits generalisation to other
settings; a field experiment offers ecological validity but absorbs
more uncontrolled variation. Many designs do better with both:
demonstrate the effect in the lab and then test whether it survives
in the field. If you can only afford one setting, name the
generalisation envelope explicitly in your discussion section
before you write it.

**Times.** When does the experiment run? Effects that depend on
current events, cultural moments, or technology generations may
not generalise to other times. The design mitigation is to
characterise the time of measurement (Spring 2026, in the wake of
specific events, with specific technology in use) so that future
readers can decide whether your finding is likely to hold for them.

**Measures.** Does the effect show up on multiple operationalisations
of the dependent variable? A single-measure effect is fragile;
converging measures are robust. The design mitigation is to include
two or three theoretically-grounded measures of your outcome and to
predict not just that they will all show the effect but in what
relative order or magnitude.

**Treatments.** Does the effect survive variations of the
manipulation? If your manipulation is "exposure to a brief
mindfulness exercise," does it survive shortening the exercise from
ten minutes to five, or substituting one mindfulness tradition for
another? Pre-specifying that you will test treatment-strength
gradient is design-time work that produces a much more credible
paper.

Planning prompts.

*To whom does your inference extend?* Write a single sentence:
"this finding should hold for [population], in [settings], over
[time-range], on [measures], for [manipulation-variants]." The
sentence is your discussion-section's bounded claim.

*Is your sample matched to that claim?* If not, narrow the claim or
broaden the sample.

*Are you running multiple measures of the dependent variable?* If
not, what is your fallback if the single measure proves to have a
measurement problem you did not anticipate?

## 3. Designing for construct validity

Construct validity is the hardest of the four Cook-and-Campbell
axes because it is about *meaning*, not about procedure. The
classic statement is Cronbach and Meehl (1955, ~16 000 citations):
"construct validity is involved whenever a test is to be
interpreted as a measure of some attribute or quality which is not
'operationally defined.'" Borsboom (2008) extended this with a
specific challenge: the standard psychometric machinery — reliability,
factor analyses, criterion correlations — measures the *test's*
properties, not the *construct's*. If the construct itself is
contested or poorly specified, no amount of reliability evidence
saves the inference.

For your design, three construct-validity decisions matter most.

**The operationalisation choice.** You measure attention by reaction
time on a flanker task. Is reaction time on the flanker task
attention? Reaction-time differences could reflect attention,
motor speed, motivation, fatigue, or working-memory load. The
design mitigation is one of two: cite the psychometric literature
that justifies the measure for your population and your use, or
include a second measure that picks up attention through a different
mechanism (e.g., pupillometry or self-report) and predict
convergence. Convergence across measures is the strongest design-
time defence of construct validity available.

**The construct's stability in the literature.** Some constructs
have a long psychometric history and a settled operationalisation
(working memory measured by N-back; heart rate variability measured
by RMSSD). Others are contested with no convergence
(mindfulness measured several incompatible ways; "presence" in VR
research). The design mitigation when working with a contested
construct is to declare your operationalisation, justify it against
the alternatives, and report the result in a way that lets readers
re-interpret if their preferred operationalisation differs.

**The construct's match to your manipulation.** If you manipulate
"cognitive load" by adding digits to remember, are you
manipulating cognitive load, working-memory capacity utilisation,
attentional resources, or attentional control? Different theories
of attention predict different patterns of effect. The design
mitigation is to predict at design time how each candidate
construct would behave in your manipulation and to design the
measures so they discriminate.

Planning prompts.

*What single sentence specifies the construct your DV measures?*
Avoid jargon; use the most precise lay term.

*What evidence supports that your operationalisation captures that
construct in your population?* Cite at least one psychometric
study; if none exists for your population, that is itself a finding
worth surfacing in your introduction.

*What alternative interpretations of your IV-DV link are you
designing to rule out?* List them; this list goes into your
preregistration and into your discussion section.

## 4. Designing for statistical conclusion validity

Statistical conclusion validity asks whether the inference from
data to claim is supported by the statistics, properly applied.
Cook and Campbell named several threats here; the post-2010
methodological-reform literature has added several more. The most
important design-time decisions are about power and about analytic
flexibility.

**Power**. The probability that, if your hypothesised effect is
real and of the size you expect, your study will detect it at your
chosen significance threshold. A study with 50 % power has a 50 %
chance of missing a real effect. The conventional target is 80 %
power, and the conventional analysis is *a priori* power analysis:
specify the expected effect size and the significance threshold,
solve for the required N. The tooling for this is mature (G*Power
3.1; Faul, Erdfelder, Lang & Buchner 2007, ~64 000 citations);
there is no methodological excuse for not running it. The honest
issue is that you often do not know the expected effect size at
design time. The contemporary practice is to take the *smallest
effect size of interest* — the smallest effect you would care to
detect — and power for that. This is more conservative and more
defensible than guessing the true effect.

**The garden of forking paths**. Gelman and Loken (2014) named the
problem: researchers make many small analytic decisions during
analysis (which subjects to exclude, which covariates to include,
which transformation to apply, which subset to focus on), and the
freedom to make these decisions inflates the false-positive rate
even without any conscious p-hacking. Simmons, Nelson, and Simonsohn
(2011, ~6 500 citations) showed that the inflation can be
substantial — a study with no real effect can produce significant
results 60 % of the time given enough researcher-degrees-of-freedom.
The design-time mitigation is pre-registration: write down the
analytic plan before you see the data. Every analytic decision made
ahead of time is a forking path you closed.

**Multiple comparisons**. If you run twenty tests at α = 0.05,
you expect one significant by chance. Corrections (Bonferroni
on the most conservative end; false-discovery rate à la Benjamini &
Hochberg 1995, ~120 000 citations, on the more permissive end) reduce
the false-positive rate but cost power. The design-time
mitigation is to pre-specify your primary hypothesis (or two) and
limit corrected α to those primary tests, treating the rest as
exploratory.

**Effect-size reporting and confidence intervals**. The American
Psychological Association's publication manual has required
confidence intervals for two decades, but the requirement is
unevenly enforced. The design-time mitigation is to plan effect-
size reporting from the start: which effect size metric matches your
design (Cohen's d for two-group comparison; partial η² for ANOVA;
odds ratio for binary outcomes; standardised regression coefficient
for continuous), and what confidence interval method you will use.

Planning prompts.

*What is the smallest effect size you would care to detect?* Solve
G*Power for required N at that effect, your design, and 80 % power.
The answer is your sample target.

*What is your pre-registered analytic plan?* It should specify:
inclusion / exclusion criteria, primary outcome variable, primary
test, secondary tests, correction for multiple comparisons, handling
of missing data, transformations, and any planned exclusions of
participants for reasons that are not the experimental manipulation.

*What effect-size statistic will you report, and with what
confidence interval?* Pre-specify, so the analysis section writes
itself.

## 5. Open-science transparency from the start

The fifth quality axis was not in Cook and Campbell's original
framework. It emerged from the post-2010 methodological-reform
movement — the replication crisis, the TOP guidelines (Nosek et al.
2015, ~3 000 citations), the manifesto for reproducible science
(Munafò et al. 2017, ~3 000 citations) — and has become a standard
expectation in many subfields. The design-time work for open-
science transparency is small and well-bounded, and it makes the
rest of your paper much more defensible.

**Pre-registration.** Write your hypothesis, design, and analytic
plan before data collection, and time-stamp it via OSF, AsPredicted,
or your field's equivalent. A registered report (which has the
introduction and methods peer-reviewed before data collection and
the results section conditionally accepted) is the strongest form,
and a growing number of journals support them. Pre-registration is
not a constraint on your science; it is a defence of it — a
preregistered null is publishable; an unregistered null often is
not.

**Open data.** Plan, at design time, where your data will live after
the paper is published. OSF, Zenodo, and journal-specific repositories
are standard. The language "available from the authors on reasonable
request" has been shown (Gabelica, Bojčić & Puljak 2022) to comply
roughly six per cent of the time; this is effectively a denial of
access. Decide before you collect data what privacy or IRB
constraints actually apply, and pre-register the data-release plan
accordingly.

**Open materials and code.** Your stimuli, your analysis script,
your experimental software — all should be deposited alongside the
data. The cost is small; the gain in replication probability is
substantial.

**Conflict-of-interest disclosure.** Plan disclosure language at
design time. If your work has commercial implications, this matters
more, not less.

Planning prompts.

*Where will your pre-registration live, and on what date will it be
posted?* The date is part of the credibility — a pre-registration
posted the week before data collection is more credible than one
posted the day after.

*What will be public when the paper is published?* Specify: data,
materials, analysis code, pre-registration link. If anything is not
public, why?

*What is your COI disclosure?*

## 6. Researcher-degrees-of-freedom and how design closes them

Simmons, Nelson and Simonsohn's *False-Positive Psychology* (2011)
named four common researcher-degrees-of-freedom: (i) flexibility in
choosing dependent variables, (ii) flexibility in choosing covariates,
(iii) flexibility in deciding to stop or continue data collection,
(iv) flexibility in selecting from multiple manipulations. All four
collapse if pre-registered. The design-time work is to write down
exactly what you will report and exactly when you will stop
collecting data.

A complementary literature on *p-hacking* (Head, Holman, Lanfear,
Kahn & Jennions 2015, ~2 500 citations) shows that even well-
intentioned researchers produce statistically inflated results when
the rules of analysis are decided after seeing the data. The
mitigation is the same: pre-specify.

A subtler version of the problem is *HARKing* — hypothesising after
results are known (Kerr 1998, ~3 000 citations). A hypothesis
formed after seeing the data, but presented as the original
hypothesis, inflates apparent confirmation. The mitigation is to
distinguish exploratory analyses (allowed and useful, but flagged
as such) from confirmatory analyses (limited to the pre-registered
hypotheses).

Planning prompts.

*What stopping rule have you specified?* "We will collect N = X
participants" is a rule. "We will collect data until the effect is
significant" is not a rule.

*Which of your planned analyses are confirmatory and which are
exploratory?* Label every analysis in your preregistration with one
of the two tags. Confirmatory analyses test pre-registered
hypotheses; exploratory analyses generate new hypotheses for
future work.

## 7. A worked example — a hypothetical COGS 160 thesis

Suppose your thesis is about how the temperature of a learning
environment affects retention of new material. You hypothesise that
cooler rooms (~20 °C) produce better retention than warmer ones
(~26 °C), via a route through sustained attention. The walk-through
below shows how the five quality axes inform the design before any
data are collected.

*Internal validity.* You design a between-subjects experiment with
random assignment to two temperature conditions. The same room is
used at both temperatures (different days), with the same
instructor, same lesson, same testing procedure, same time of day,
to control history, maturation, instrumentation. Participants are
told the study is about "learning environments" generically — the
temperature manipulation is not announced — to control diffusion.
You plan an intention-to-treat analysis: anyone who completes the
pre-test enters the analysis regardless of post-test completion.

*External validity.* Your population sentence: "The finding should
hold for university undergraduate-aged learners in a typical
classroom-sized room, on lesson content of moderate difficulty,
with measurement via a knowledge post-test, for temperature
variations within the 20–26 °C range." This is narrower than
"humans learning anything anywhere" and that is intentional. You
will sample at UCSD; you note that your population is therefore
WEIRD and recommend in the discussion that a non-WEIRD replication
should be a follow-up.

*Construct validity.* "Retention" is measured by performance on a
delayed knowledge test at one week. You add a second measure —
performance on a transfer task at one week — to test convergence;
your prediction is that the cooler-room group will outperform on
both, and you make explicit that if they outperform on knowledge
but not transfer, you will interpret as superficial retention; if
they outperform on transfer but not knowledge, as deep
understanding; if they outperform on both, as broad attention-
mediated retention. The construct distinction is in the
preregistration.

*Statistical conclusion validity.* You expect a moderate effect
(Cohen's d ≈ 0.4) based on prior literature; G*Power tells you
n = 100 per cell for 80 % power at α = 0.05. You pre-register the
ANOVA, the planned comparisons, the handling of missing data
(intent-to-treat), the inclusion/exclusion criteria (must complete
pre-test, must be present at post-test, no exclusions on the basis
of performance), the multiple-comparisons correction (Bonferroni
on the two primary tests; FDR on the exploratory ones). You report
Cohen's d with bootstrap 95 % CI.

*Open-science transparency.* The pre-registration goes on OSF
before data collection begins. The deidentified data, the stimuli,
the analysis script, and the preregistration link will all be
public on OSF on the day of submission. Your COI statement notes no
financial interest in temperature-control systems.

*Researcher-degrees-of-freedom.* Your stopping rule is "100 per
cell, recruited consecutively, with a maximum 30 % over-recruit if
attrition exceeds 25 %." Your confirmatory analyses are the two
primary tests on knowledge and transfer; everything else is labeled
exploratory.

That design, before any data is collected, is publishable as a
registered report. The paper that emerges will be defensible on all
five axes by construction. If the predicted effect does not
materialise, the paper still publishes as an informative null with
a credible design. This is the goal of design-time quality work:
the paper is good before the data exist.

## 8. Pre-flight checklist

Before you collect a single data point, every one of the following
should have a defensible answer. If any one does not, the question
is whether your design needs to change or whether your claim does.

1. What population does your inference extend to, and is your
   sample matched to it?
2. What setting does your inference extend to, and is your
   experimental environment matched to it?
3. What is your operationalisation of the dependent construct, and
   what evidence supports that operationalisation?
4. Do you have a second measure of the same construct for
   convergence?
5. What is your sample-size justification, derived from an a priori
   power analysis for the smallest effect size of interest?
6. What are your pre-registered confirmatory hypotheses and analyses?
7. What is your handling of multiple comparisons?
8. What is your stopping rule?
9. What is your inclusion / exclusion plan, pre-specified?
10. What is your data-availability plan, and to which repository
    will it go?
11. What is your COI statement?
12. What single sentence in your discussion section names the
    population, setting, time, measure, and manipulation envelope
    of your claim?

The pre-flight checklist is the design-time analogue of the paper-
quality fingerprint that the Knowledge Atlas extracts from finished
papers. A study whose pre-flight checklist is complete will produce
a paper whose fingerprint is strong by construction. A study whose
checklist has gaps will produce a paper whose fingerprint flags the
same gaps after the fact — when they are much more expensive to
address.

## 9. Closing — designing-as-credibility

The recurring theme of this document is that the quality of an
experimental paper is set at design time, not at write-up time. The
five axes of quality are five sets of decisions that the experimenter
makes before any participant is run. Cook and Campbell's framework
plus the open-science additions give you the vocabulary to think
those decisions through systematically; pre-registration gives you
the discipline to commit to them; the worked example shows what a
defensible design looks like in practice.

The Knowledge Atlas exists in part to help readers — including your
future readers — quickly see which papers were designed well and
which were designed poorly. The paper-quality fingerprint is the
Atlas's record of those decisions. You can use this guide in two
modes: as a pre-flight checklist for your own design, and as a
mental model when reading any other paper through the Atlas. In
either mode, the same axes apply, and the same standards of
believability hold.

A study designed against this guide is a study its author can
defend. A study not designed against this guide is a study that
will need rescuing later. Design-time work is the cheapest work in
experimental research; it is also the only work that fully
preserves your inferential options. Use it.

---

## References

Benjamini, Y., & Hochberg, Y. (1995). Controlling the false
discovery rate: A practical and powerful approach to multiple
testing. *Journal of the Royal Statistical Society. Series B*,
57(1), 289–300. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x
(Google Scholar: ~120 000)

Borsboom, D. (2008). Latent variable theory. *Measurement:
Interdisciplinary Research and Perspectives*, 6(1–2), 25–53.
https://doi.org/10.1080/15366360802035497 (Google Scholar: ~600)

Bracht, G. H., & Glass, G. V. (1968). The external validity of
experiments. *American Educational Research Journal*, 5(4),
437–474. https://doi.org/10.3102/00028312005004437
(Google Scholar: ~2 500)

Cook, T. D., & Campbell, D. T. (1979). *Quasi-experimentation:
Design and analysis issues for field settings*. Houghton Mifflin.
(Google Scholar: ~37 000)

Cronbach, L. J., & Meehl, P. E. (1955). Construct validity in
psychological tests. *Psychological Bulletin*, 52(4), 281–302.
https://doi.org/10.1037/h0040957 (Google Scholar: ~16 000)

Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007).
G*Power 3: A flexible statistical power analysis program for the
social, behavioral, and biomedical sciences. *Behavior Research
Methods*, 39(2), 175–191. https://doi.org/10.3758/BF03193146
(Google Scholar: ~64 000)

Gabelica, M., Bojčić, R., & Puljak, L. (2022). Many researchers
were not compliant with their published data sharing statement: A
mixed-methods study. *Journal of Clinical Epidemiology*, 150,
33–41. https://doi.org/10.1016/j.jclinepi.2022.05.019
(Google Scholar: ~250)

Gelman, A., & Loken, E. (2014). The statistical crisis in science.
*American Scientist*, 102(6), 460–465. (Google Scholar: ~1 800)

Head, M. L., Holman, L., Lanfear, R., Kahn, A. T., & Jennions, M.
D. (2015). The extent and consequences of p-hacking in science.
*PLoS Biology*, 13(3), e1002106.
https://doi.org/10.1371/journal.pbio.1002106
(Google Scholar: ~2 500)

Henrich, J., Heine, S. J., & Norenzayan, A. (2010). The weirdest
people in the world? *Behavioral and Brain Sciences*, 33(2–3),
61–83. https://doi.org/10.1017/S0140525X0999152X
(Google Scholar: ~10 500)

Kerr, N. L. (1998). HARKing: Hypothesizing after the results are
known. *Personality and Social Psychology Review*, 2(3), 196–217.
https://doi.org/10.1207/s15327957pspr0203_4 (Google Scholar: ~3 000)

Munafò, M. R., Nosek, B. A., Bishop, D. V. M., et al. (2017). A
manifesto for reproducible science. *Nature Human Behaviour*, 1(1),
0021. https://doi.org/10.1038/s41562-016-0021
(Google Scholar: ~3 000)

Nosek, B. A., Alter, G., Banks, G. C., et al. (2015). Promoting an
open research culture. *Science*, 348(6242), 1422–1425.
https://doi.org/10.1126/science.aab2374 (Google Scholar: ~3 000)

Open Science Collaboration. (2015). Estimating the reproducibility
of psychological science. *Science*, 349(6251), aac4716.
https://doi.org/10.1126/science.aac4716 (Google Scholar: ~7 500)

Shadish, W. R., Cook, T. D., & Campbell, D. T. (2002).
*Experimental and quasi-experimental designs for generalized
causal inference*. Houghton Mifflin. (Google Scholar: ~46 000)

Simmons, J. P., Nelson, L. D., & Simonsohn, U. (2011).
False-positive psychology: Undisclosed flexibility in data
collection and analysis allows presenting anything as significant.
*Psychological Science*, 22(11), 1359–1366.
https://doi.org/10.1177/0956797611417632 (Google Scholar: ~6 500)

Yarkoni, T. (2020). The generalizability crisis. *Behavioral and
Brain Sciences*, 45, e1. https://doi.org/10.1017/S0140525X20001685
(Google Scholar: ~700)

---

*End of guide. For a worked example or coaching on a specific
design, bring it to office hours.*
