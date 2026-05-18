# What VR can and cannot measure — a Week-1 reference for COGS 160 Fall

*Last updated: 2026-05-18. This is the source-of-truth for the Knowledge Atlas substitution skill and for the student-facing Surface 6 of the Week-1 wireframe. The page is written in human-readable prose for the student and in structured form (heading-level taxonomy, measure-by-measure tables) for the substitution skill to parse.*

---

## Why this page exists

If you are designing a virtual-reality experiment for COGS 160 Fall, the most consequential decision you will make in the first two weeks is which *outcome measure* your study will use to detect the effect you care about. The choice is not free. Some measures are routinely deployable in a classroom VR project; others require equipment, time, or participant access that the seven-to-ten-week envelope of the course does not allow. This page lays out the distinction explicitly. The first half is a positive taxonomy of measures that *can* be obtained in a class VR project. The second half is a negative list of measures that *cannot*, with a brief explanation in each case so you understand the constraint rather than just registering it. The closing section addresses the practical question that will come up almost immediately: *what do I do when the paper I am replicating used a measure on the negative list?* The answer is the substitution principle, and it is the foundation of the Week-1-to-Week-3 measure-handling pipeline that the substitution skill is built around.

## Positive taxonomy — measures available in a class VR project

There are four families of measures you can plan around. They are ordered roughly by how much extra hardware they require beyond the base headset, beginning with the family that is essentially free.

### Family 1 — Behavioural traces from the headset and controllers themselves

The headset is recording you constantly. Head pose, locomotion path, hand pose (on the better controllers), gaze direction (on the headsets with built-in eye-tracking — Meta Quest Pro, HTC Vive Pro Eye, Varjo XR-3; the consumer-grade Quest 2 does not), and time-stamped interaction events (button presses, object grabs, teleport events) are all logged by the engine without any additional instrumentation. These traces are valid behavioural measures rather than mere telemetry — the founding methodological argument for using VR as a behavioural laboratory was precisely that these traces give you a degree of stimulus and recording control that the natural environment does not (Loomis, Blascovich & Beall, 1999), and the substantial body of work that has followed treats them as the natural-history record of the participant's interaction (Pan & Hamilton, 2018).

For your project this means: if your dependent variable can be expressed as a function of where the participant looks, how long they look, how they move through the environment, or what they reach for, you can collect the data without buying a single peripheral. This is the cheapest path to a defensible measure. The price you pay is that the *interpretation* of these traces is not always straightforward — head pose is a proxy for attention only under specific conditions, locomotion is a proxy for exploration only when the environment affords it, and so on. Use the traces; do not over-claim what they index.

### Family 2 — Task-embedded performance measures

A more deliberate kind of behavioural measure: design a task that the participant performs inside the VR environment, and record their performance. The task can be anything that produces a number. Response latency on a probe; accuracy on a change-detection or recognition task; choice fraction on a forced-choice task; memory accuracy after a delay; error rate on a navigation task. These measures do not require any sensor beyond the headset; they require only that you design the task and arrange for its performance to produce data the engine can log. The lineage is the long tradition of cognitive-psychology task-design — the Stroop task, the flanker task, the Posner cueing paradigm — moved into immersive contexts (Bohil, Alicea & Biocca, 2011; Parsons, 2015).

For COGS 160 specifically, task-embedded performance measures are usually the strongest combination of feasibility, defensibility, and clarity. You design a task whose performance maps to a construct, you collect the numbers across conditions, you compare. The grading-relevant property is that the resulting data are unambiguously yours to interpret rather than being mediated by a piece of unfamiliar hardware. Among the families on this page, this is the one we will encourage you to use unless you have a reason not to.

### Family 3 — Verbal and questionnaire-based self-report

A scale of established validity, administered to the participant either inside the headset or immediately on exit. Presence questionnaires — the Slater-Usoh-Steed presence questionnaire and its descendants (Schubert, Friedmann & Regenbrecht, 2001) — affective state inventories, perceived restorativeness scales, mood-and-stress checklists, the post-experimental open-ended interview. The substantive point about self-report in immersive contexts is that it is legitimate evidence of a specific kind: it indexes what the participant is willing and able to report about their experience, not the underlying processes that produced the experience (this is the longstanding lesson from introspectionist psychology and the careful work of contemporary phenomenology in cognitive science).

For your project: self-report is fast to administer and produces immediately comparable numbers across conditions. The risk is demand characteristics — the participant guesses what the experimenter wants and obliges them, sometimes unconsciously (Orne, 1962). The standard mitigation is to pair self-report with a behavioural measure: if both measures move in the same direction, the inference is stronger; if they diverge, you have a substantive finding to interpret rather than a methodological hole. Class projects that rely on self-report alone are weaker than they need to be. Plan to pair.

### Family 4 — Physiological signals from wearable peripherals

For a more ambitious class project: heart rate and heart-rate variability from a chest strap or wrist-worn device, electrodermal activity (galvanic skin response) from a wristband, pupillometry from the eye-tracking headsets named in Family 1, and on the most capable systems integrated electroencephalography via dry electrodes (the Galea project's prototype; the Looxid Labs Link). The methodological appeal of physiological measures is that they are difficult for the participant to fake and that they index processes operating on timescales the behavioural measures cannot resolve.

Be candid with yourself about the cost. Physiological instrumentation in a 10-week class project trades reliability for ambition. Heart-rate variability is well-validated in calm, seated participants over short intervals, and somewhat well-validated under cognitive load; consumer-grade wristband EDA is noisier than the dedicated psychophysiology laboratory's setup; classroom EEG (when available) typically produces data dominated by movement artefacts unless the protocol is meticulously controlled. If your design plan includes physiology, you should budget two of your seven-to-ten weeks for getting the signal acquisition right before you start collecting data. If you are willing to do that and your topic genuinely requires a physiological signal, the families are open to you. If your topic does not require physiology, do not add it because it sounds advanced. A clean task-embedded performance measure (Family 2) plus a self-report (Family 3) is usually a stronger dataset than a noisy physiological signal.

## Negative taxonomy — measures *not* available in a class VR project

The exclusions matter as much as the inclusions, because the most common derailing of class projects is choosing a topic whose canonical outcome measure is on this list and only realising late that the measure cannot be obtained. Read this list before you commit to a topic.

### Exclusion 1 — fMRI BOLD signals

Functional magnetic-resonance imaging requires the participant to be inside a large, narrow-bore magnet that excludes any head-mounted display we can use. Studies in the literature that combine VR with fMRI exist, but they use either projection-screen-into-the-scanner setups that we do not have or dedicated MR-compatible headsets that we cannot afford. If your paper uses fMRI to localise the effect, you cannot replicate the fMRI measurement in our setting. The path forward, if there is one, is via substitution to a behavioural or psychophysiological measure of the same construct (see the closing section). If no such substitute exists for your topic, that is the signal to change topics.

### Exclusion 2 — Long-term field outcomes

Measures that require weeks or months of follow-up to detect — reductions in real-world clinical symptoms, long-term cognitive change, durable behavioural change in everyday life, any outcome whose unit of observation is "the next month of the participant's life" — are not obtainable in seven to ten weeks. The course's timeline forces a within-session or near-session measurement window. If your paper's central claim depends on the *duration* of the effect rather than its *presence*, the duration claim is outside what you can test. You can still test whether the effect is detectable at all in a within-session design, but you must be explicit that you are testing presence, not persistence.

### Exclusion 3 — Naturalistic multi-party social signals

VR can support two-person interaction studies. The technical infrastructure for synchronised multi-headset experiments is real, well-developed in published research (Pan & Hamilton, 2018), and within reach of a class project if the project explicitly plans for it. What is not within reach is multi-party (three-plus) social-physiological synchrony in unrestricted interaction. Studies that measure heart-rate coupling across three or more interacting participants, or pupillometric synchrony in a group conversation, or shared neural signals across a small crowd — those depend on coupled hardware and high-fidelity time-synchronised acquisition that classroom labs typically lack. If your topic requires this, you need to either scale down to a two-participant design or change topics.

### Exclusion 4 — Real-world transfer claims

Many papers' central claim is that an effect demonstrated in the lab transfers to the real world: that restorative VR exposure improves attention in subsequent real-world tasks; that VR training improves real-world motor skill; that VR exposure to a stressor inoculates the participant against real-world stressors. These claims cannot be settled within VR alone. The within-VR study can test whether the effect is *present* in VR; it cannot test whether the effect *transfers*. If your paper's claim is specifically about transfer, your project will not be able to test the transfer claim. You can still test the within-VR effect — that is a respectable contribution — but you must be candid in your write-up about what you are and are not testing.

### Exclusion 5 — Pharmacological and clinical biomarkers

Measures that require blood draws, saliva collection, urine analysis, or other tissue sampling fall outside what classes can do without dedicated lab support. The IRB envelope for class projects is also tighter than for full research studies; collecting biological samples introduces compliance and consent requirements the course will not approve. If your paper's outcome is salivary cortisol, plasma oxytocin, or a similar biomarker, the path is again either substitution to a behavioural or self-report measure of the same construct, or a change of topic.

## The substitution principle — what to do when your paper's measure is on the negative list

This is the section to read carefully if your candidate paper uses an excluded measure. The principle, briefly: the fact that the original paper's measure is on the negative list does *not* automatically mean the underlying construct is unmeasurable in your project. If the construct can be indexed by a measure on the positive list, the project remains viable. The question is whether a defensible *substitute* exists.

A defensible substitute satisfies two conditions. First, the field has used both the original measure and the substitute to index the same construct, in studies that compare them or treat them as alternative operationalisations. Second, the substitute is in one of the four positive families above. Both conditions must hold; either alone is not enough. A measure that the field treats as a valid alternative but that is on the negative list does not help you. A measure that is on the positive list but that the field treats as indexing a different construct does not help you either.

When both conditions hold, you have a substitution path. The substitution skill in the Knowledge Atlas — invoked through the *Evaluate-a-paper-for-VR* surface (Week 1, admit-mode) and the *Choose-a-measure* surface (Week 3, choice-mode) — automates this check across the corpus's papers and produces a ranked list of admissible substitutes, with the construct-validity arguments that link each substitute to your target construct and the psychometric profile (reliability, known weaknesses, hardware requirements) of each.

What you should *not* do is invent your own substitute on the fly. The class project envelope does not permit measurement-development as a side-project; you have neither the time nor the population access to validate a new measure. Your substitute should be one the field has already accepted as indexing your construct, and the justification you write into your project proposal should cite the paper or papers that established the substitute as valid.

What you *should* do, the first time you encounter the substitution question, is bring the candidate paper to the *Evaluate-a-paper-for-VR* surface. The skill will tell you whether a substitution path exists, what the candidate substitutes are, and what trade-offs you would be making by choosing one. If no substitution path exists for your paper, the skill says so explicitly, and the recommendation is to switch papers within the same topic or to switch topics. Both are honest moves at Week 1; both are very expensive at Week 4.

## A short note on what "VR-tractable" really means

Throughout this page, and across the Knowledge Atlas wireframes, you will see the term *VR-tractable*. It is a compressed term and it means three things at once. First, the *hardware* required to obtain the measure is available to the class. Second, the *time* required to administer the measure across a sample of the size you can recruit is within the course envelope. Third, the *interpretation* of the measure does not depend on infrastructure (a longitudinal follow-up, a clinical population, an fMRI scanner) that we cannot provide. A measure that fails any of the three is not VR-tractable for our purposes. A measure that satisfies all three is VR-tractable and admissible into your project.

The reason to make the three conditions explicit is that students sometimes encounter measures that satisfy two of the three and not the third, and the mismatch is easy to overlook. A measure that is technically deployable in VR (hardware available) but takes ninety minutes per participant (time-infeasible for a class sample) is *not* VR-tractable; a measure that takes ten minutes per participant (time-feasible) but requires comparing the participant's score to a normative database we do not have (interpretation-infeasible) is *not* VR-tractable. The substitution skill checks all three. You should too.

## How to use this page in Weeks 1, 2, and 3

In Week 1, read this page once, in full. It is the foundation for the rest of the course's measurement decisions. After you have read it, you do not need to read it again unless you are revisiting a measure you had not previously considered.

In Week 1, when you have selected a candidate paper for your project, bring it to the *Evaluate-a-paper-for-VR* surface (Surface 4 of the Week-1 wireframe). The surface will tell you whether the paper's outcome measure is on the positive list (admit), on the negative list with a defensible substitute (substitute), or on the negative list without a defensible substitute (reject). If the paper is admitted or substituted, the surface produces a brief justification that you can copy into your project notes.

In Week 3, when you are committing to a specific measure for your study, bring the topic to the *Choose-a-measure* surface (Surface 4b of the Week-1 wireframe, conceptually a Week-3 surface). The surface lays out the candidate measures side by side and produces a ranked recommendation with the trade-offs articulated. You can override the recommendation if your topic or your access to hardware warrants it, but the override should be a deliberate decision rather than an oversight.

In Weeks 4–7, this page is no longer your primary reference; the methodological-pitfalls page is. But the measure you committed to in Week 3 should be the measure you actually run, and any reason for changing it should be documented.

---

## Quick reference — the four positive families and the five exclusions

| Family / Exclusion | Examples | What it costs | What it gives |
|---|---|---|---|
| **F1: Headset / controller traces** | Head pose, gaze direction, locomotion, hand pose, interaction events | Engine logging only (free) | Behavioural traces; interpretation requires construct-mapping |
| **F2: Task-embedded performance** | Response latency, accuracy, choice fraction, memory probes, navigation error | Task design time | Strong combination of feasibility and defensibility |
| **F3: Verbal / questionnaire self-report** | Presence questionnaires, affect inventories, perceived-restorativeness scales | ~5–10 min per administration | Fast; vulnerable to demand characteristics; pair with F2 |
| **F4: Wearable physiology** | Heart rate / HRV, EDA, pupillometry, integrated EEG | Hardware + 2 weeks of signal-acquisition setup | Hard to fake; resolves processes F1–F3 cannot |
| **X1: fMRI BOLD** | — | — | Substitute to F1–F4 or change topic |
| **X2: Long-term field outcomes** | Multi-month follow-up; clinical endpoints | — | Test presence, not persistence |
| **X3: Naturalistic multi-party social signals** | 3+ participant synchrony | — | Scale to two-party or change topic |
| **X4: Real-world transfer claims** | Lab-effect transfers to real-world | — | Test within-VR; cannot test transfer |
| **X5: Pharmacological / biomarker outcomes** | Cortisol, oxytocin, blood markers | — | Substitute to behavioural or self-report |

---

## References

Bohil, C. J., Alicea, B., & Biocca, F. A. (2011). Virtual reality in neuroscience research and therapy. *Nature Reviews Neuroscience*, *12*(12), 752–762. https://doi.org/10.1038/nrn3122

Loomis, J. M., Blascovich, J. J., & Beall, A. C. (1999). Immersive virtual environment technology as a basic research tool in psychology. *Behavior Research Methods, Instruments, & Computers*, *31*(4), 557–564. https://doi.org/10.3758/BF03200735

Orne, M. T. (1962). On the social psychology of the psychological experiment: With particular reference to demand characteristics and their implications. *American Psychologist*, *17*(11), 776–783. https://doi.org/10.1037/h0043424

Pan, X., & Hamilton, A. F. de C. (2018). Why and how to use virtual reality to study human social interaction: The challenges of exploring a new research landscape. *British Journal of Psychology*, *109*(3), 395–417. https://doi.org/10.1111/bjop.12290

Parsons, T. D. (2015). Virtual reality for enhanced ecological validity and experimental control in the clinical, affective and social neurosciences. *Frontiers in Human Neuroscience*, *9*, 660. https://doi.org/10.3389/fnhum.2015.00660

Schubert, T., Friedmann, F., & Regenbrecht, H. (2001). The experience of presence: Factor analytic insights. *Presence: Teleoperators and Virtual Environments*, *10*(3), 266–281. https://doi.org/10.1162/105474601300343603

---

*This page is the source of truth for the Knowledge Atlas substitution skill. Updates to the page propagate to the skill's knowledge base via the build pipeline. If you find a measure that should be on the positive list and is not, or a measure that should be on the negative list and is not, file an issue or speak to the instructor.*
