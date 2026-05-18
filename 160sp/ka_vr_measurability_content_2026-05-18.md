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

Three sub-types in this family have particularly clear translations into VR and are worth describing in detail because the course will encourage their use.

*The Implicit Association Test (IAT) and its VR-adapted variants.* The IAT (Greenwald, McGhee & Schwartz, 1998) is a reaction-time task in which the participant sorts stimuli into categories using two response keys; the difference in response time between congruent and incongruent pairings is taken to index the strength of an implicit association. In VR the two response keys map naturally onto the two controller triggers, or onto two button positions on a single controller. Stimuli appear in the visual field; the participant responds as quickly as possible. The construct typically targeted is implicit attitude toward a category (objects, faces, environments, brands), and IAT-style designs are well suited to architectural-cognition questions where the explicit-versus-implicit attitude split is itself the substantive contrast. *Ease of use:* moderate. The task structure is well-documented and the timing logic is straightforward to implement in any engine; what is harder is reasoning about whether VR's millisecond-scale timing jitter (which can run 10–20 ms in consumer headsets) compromises the inference. For a first IAT in VR, build in a calibration check (a known-strong association as a sanity benchmark) and treat your effects above that benchmark as the substantive findings.

*Q-sort and the twenty-card sort.* Q-methodology (Stephenson, 1953; for a contemporary review, see Watts & Stenner, 2012) asks participants to sort a fixed set of items into a forced distribution — typically a quasi-normal grid of "most agree" to "most disagree" — and analyses the resulting matrix factorially. The twenty-card variant is a compact version: twenty items, sorted into ranks, no forced distribution required. Q-sort gives the experimenter access to the participant's *configuration* of preferences rather than just isolated ratings, which is what makes it the natural choice when you want to know how attitudes hang together rather than which way each one points. In VR the sort affordance translates beautifully: cards or 3D objects float in front of the participant; the participant grabs and places them in bins; the placement is logged. *Ease of use:* moderate. The task is intuitive for participants and the data is rich; the design work is in choosing the twenty items and writing them so they discriminate. Q-sort in VR is rarer in the literature than IATs and stands out as a methodological contribution if you do it well.

*Adaptive-preference and discrete-choice tasks.* In an adaptive-preference design, the participant makes a sequence of pairwise (or N-wise) choices between stimuli; the algorithm uses each response to choose the next pair so as to narrow the participant's preference structure efficiently (Toubia, Hauser & Garcia, 2007; for the adaptive-conjoint-analysis tradition, Green & Srinivasan, 1990). The classic application in psychophysics is the adaptive staircase, in which threshold estimation converges rapidly; in marketing and decision research, adaptive conjoint analysis estimates preference weights across attributes with far fewer trials than a non-adaptive design. In VR the affordance is natural — two scenes appear, the participant picks, the algorithm composes the next pair — and the cognitive load on the participant per trial is low. *Ease of use:* moderate to advanced. The task structure is simple; the design work is in writing the adaptation rule. For a first project, use one of the published adaptive-staircase or adaptive-choice protocols rather than inventing your own.

### Family 3 — Verbal and questionnaire-based self-report

A scale of established validity, administered to the participant either inside the headset or immediately on exit. Presence questionnaires — the Slater-Usoh-Steed presence questionnaire and its descendants (Schubert, Friedmann & Regenbrecht, 2001) — affective state inventories, perceived restorativeness scales, mood-and-stress checklists, the post-experimental open-ended interview. The substantive point about self-report in immersive contexts is that it is legitimate evidence of a specific kind: it indexes what the participant is willing and able to report about their experience, not the underlying processes that produced the experience (this is the longstanding lesson from introspectionist psychology and the careful work of contemporary phenomenology in cognitive science).

For your project: self-report is fast to administer and produces immediately comparable numbers across conditions. The risk is demand characteristics — the participant guesses what the experimenter wants and obliges them, sometimes unconsciously (Orne, 1962). The standard mitigation is to pair self-report with a behavioural measure: if both measures move in the same direction, the inference is stronger; if they diverge, you have a substantive finding to interpret rather than a methodological hole. Class projects that rely on self-report alone are weaker than they need to be. Plan to pair.

### Family 4 — Physiological and motion signals from wearable peripherals

For a more ambitious class project: a defined set of sensors is available in the lab, with a few more that can be added if the project warrants. The methodological appeal of physiological measures is that they are difficult for the participant to fake and that they index processes operating on timescales the behavioural measures cannot resolve. Below is the inventory of what we have, what each sensor measures, and how easy or hard it is to deploy responsibly in a class project.

**Confirmed available in the lab kit.** These sensors are on the shelf and can be combined with any VR scenario without additional procurement. Each entry lists what it indexes, the ease of use, and the principal pitfall a student should be aware of before adopting it.

*Electrodermal activity (EDA, also known as galvanic skin response).* A wrist- or finger-worn sensor measures skin conductance, which varies with sympathetic-nervous-system arousal (Boucsein, 2012). The signal is sensitive — a startle, a stressful image, a moment of effortful concentration all produce a measurable response — and the lineage of EDA in psychophysiology is long. *Ease of use:* easy to acquire signal; moderate to interpret. The hardware is forgiving and the data is clean if the participant's hand is reasonably still. The interpretive caution is that EDA is a non-specific arousal measure: it does not distinguish positive arousal from negative arousal, and it does not localise to a cognitive process. Pair it with a behavioural or self-report measure that tells you *what kind* of arousal you are seeing.

*Heart rate (HR) and heart-rate variability (HRV).* A chest strap (preferred for HRV) or wrist-worn device measures inter-beat intervals; HRV is the variation in those intervals across a recording window and indexes parasympathetic regulation and autonomic balance (Laborde, Mosley & Thayer, 2017). HR alone is a coarse measure of arousal; HRV is much richer but requires longer recordings (typically several minutes of stationary activity for a reliable estimate) and careful artefact handling. *Ease of use:* HR is easy; HRV is moderate. The principal pitfall with HRV in class projects is that the recording window required for a stable estimate often does not fit the within-trial design students initially propose. If you want HRV, plan blocks of 3–5 minutes per condition rather than trial-by-trial sampling.

*Respiration.* A chest band or thermistor at the nostrils measures breathing rate and amplitude (Grossman & Taylor, 2007). Respiration is mechanistically coupled to HRV (respiratory sinus arrhythmia) and indexes effortful versus relaxed breathing patterns. *Ease of use:* moderate. The chest-band hardware is reliable; the analysis is well-documented. The pitfall is that participants modulate their breathing voluntarily when they become aware of the sensor — instruct participants to breathe normally, and where possible obscure the moment when the sensor begins recording.

*Three-axis (3D) wrist accelerometers.* The wrist devices in the lab record acceleration in three orthogonal axes at a high sampling rate. The signal captures fine motor activity, hand movement during interaction, fidgeting, and gesture (Bonomi et al., 2009). *Ease of use:* easy to acquire signal; moderate to analyse. The analysis question is what derived measure to compute — root-mean-square acceleration over a window, jerk (the time derivative of acceleration), or counts of suprathreshold events — and the choice depends on the construct you are indexing. The pitfall is over-interpreting raw acceleration as a behavioural measure when it is mediated by hand-controller use; isolate periods of controller interaction from periods of free hand movement before computing the derived measure.

**Uncertain availability — confirm before planning.** Two capabilities depend on which headset model the lab assigns to you.

*Eye tracking (gaze direction).* On a Meta Quest Pro, HTC Vive Pro Eye, Varjo XR-3, or Pico Neo 3 Pro Eye, gaze is sampled continuously and can be logged as an additional behavioural trace. On a consumer Quest 2 or Quest 3, no eye-tracking is available. *Ease of use, when available:* easy to acquire; moderate to analyse. The fixation-extraction step (turning a raw gaze stream into a sequence of fixations on objects of interest) is the analysis bottleneck; choose your software pipeline early. The pitfall is calibration drift across long sessions — re-calibrate between blocks.

*Pupillometry.* The same eye-tracking headsets also provide pupil diameter at the same sampling rate. Pupillometry indexes mental effort, arousal, and reward-related processes (Mathôt, 2018). *Ease of use, when available:* easy to acquire; moderate to interpret. The principal pitfall is luminance confound: pupil diameter changes dramatically with the brightness of the visual field, and any condition that varies brightness will produce pupil changes that are not about cognitive effort. Either equate luminance across conditions, or measure ambient luminance and partial it out statistically.

**Available on request — talk to the instructor early.** Two further capabilities can be added if the project's design genuinely requires them.

*Additional motion-tracking sensors.* External markers (Vive Trackers, body-mounted inertial measurement units, OptiTrack camera systems if the lab has access) extend the wrist-accelerometer capability to whole-body or limb-level motion tracking. Useful for studies that need to record posture, gait, or whole-body gesture. *Ease of use:* moderate to advanced. The setup is more involved and the data pipeline is more complex; plan an extra week for it.

*Surface electromyography (EMG) for muscle tension.* Skin-surface electrodes record the electrical activity of an underlying muscle group; the standard targets in psychophysiological research are the corrugator (frowning, negative affect) and zygomaticus (smiling, positive affect) muscles of the face, and the trapezius (shoulder tension under stress) on the upper back (Tassinary, Cacioppo & Vanman, 2007). *Ease of use:* advanced. EMG requires careful electrode placement, skin preparation, and noise control. It is feasible for a class project but only if the project leans on it for a substantive contribution; do not add EMG to a project that is otherwise complete.

**The honest counsel on physiology.** Be candid with yourself about the cost. Physiological instrumentation in a 7-to-10-week class project trades reliability for ambition. The signals named above are all real measures that real research labs use to real effect, but they are also signals that require attention to acquisition quality before the substantive analysis can begin. If your design plan includes physiology, budget two of your seven-to-ten weeks for getting the signal acquisition right before you start collecting data, and plan to pair the physiological measure with a behavioural or self-report measure so that you have a second source of evidence if the physiology is noisier than expected. If your topic does not genuinely require physiology, do not add it because it sounds advanced; a clean task-embedded performance measure (Family 2) plus a self-report (Family 3) is usually a stronger class deliverable than a noisy physiological signal.

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

## Quick reference — measures available, with ease-of-use ratings

The table below is the machine-readable shelf for the Knowledge Atlas substitution skill. Each measure named here can be referred to by its short code; ease-of-use is rated *easy / moderate / advanced* on the dimensions that matter for a 7-to-10-week class project (signal acquisition difficulty, analysis effort, interpretive risk).

| Family · Measure | Short code | What it indexes | Hardware needed | Ease of use | Principal pitfall |
|---|---|---|---|---|---|
| F1: Head pose / locomotion | `f1.head_pose`, `f1.locomotion` | Spatial attention, exploration | Headset only | Easy | Construct-mapping; gaze ≠ attention always |
| F1: Hand pose / interaction events | `f1.hand_pose`, `f1.interaction` | Reach, gesture, choice action | Controllers | Easy | Engine-specific event logging quirks |
| F2: Response latency / accuracy | `f2.rt`, `f2.acc` | Cognitive processing speed, attention | None beyond headset | Easy | Floor/ceiling effects depending on dosage |
| F2: IAT (Implicit Association Test) | `f2.iat` | Implicit attitudes between two categories | Controller two-key | Moderate | Consumer-VR ~10–20 ms timing jitter |
| F2: Q-sort / twenty-card sort | `f2.qsort`, `f2.20card` | Configurational preferences / attitudes | Controllers (drag/place) | Moderate | Item selection is the design problem |
| F2: Adaptive preference / discrete-choice | `f2.adaptpref`, `f2.dchoice` | Preference weights, thresholds | Controllers | Moderate–advanced | Adaptation-rule design |
| F3: Presence questionnaires | `f3.presence` | Subjective immersion | None | Easy | Established scales only; do not invent |
| F3: Affect / mood inventories | `f3.affect`, `f3.prs` | Reportable affective state | None | Easy | Demand characteristics — pair with F2 |
| F3: Construct-specific scales | `f3.{construct}` | Whatever the scale was validated for | None | Easy | Validate the scale for your population |
| F4 (confirmed): EDA | `f4.eda` | Sympathetic arousal | Wrist/finger sensor | Easy → Moderate | Non-specific arousal; pair with another signal |
| F4 (confirmed): HR | `f4.hr` | Cardiac arousal | Chest strap / wrist | Easy | Coarse measure; HRV is richer |
| F4 (confirmed): HRV | `f4.hrv` | Parasympathetic regulation | Chest strap preferred | Moderate | 3–5 min recording blocks required |
| F4 (confirmed): Respiration | `f4.resp` | Breathing rate / depth | Chest band | Moderate | Voluntary modulation when participant aware |
| F4 (confirmed): 3D wrist accelerometer | `f4.accel3d` | Fine motor activity, gesture | Wrist device | Easy → Moderate | Choice of derived measure (RMS, jerk, counts) |
| F4 (maybe): Eye tracking | `f4.gaze` | Gaze direction, fixations | Quest Pro / Vive Pro Eye / Varjo | Easy → Moderate | Calibration drift; need fixation pipeline |
| F4 (maybe): Pupillometry | `f4.pupil` | Mental effort, arousal | Same as eye tracking | Easy → Moderate | Luminance confound; equate or partial out |
| F4 (request): Motion-tracking add-ons | `f4.motion_ext` | Whole-body / limb motion | Vive Trackers / OptiTrack | Moderate → Advanced | Extra setup week |
| F4 (request): Surface EMG | `f4.emg` | Muscle activation (corrugator, zygomaticus, trapezius) | Skin electrodes | Advanced | Electrode placement, noise control |

**Exclusions (the five negative-list items).**

| Exclusion | Short code | Why excluded |
|---|---|---|
| fMRI BOLD | `x1.fmri` | Cannot wear headset in scanner |
| Long-term field outcomes | `x2.longfield` | Course window is 7–10 weeks |
| Naturalistic multi-party (>2) social signals | `x3.multiparty` | Synchronisation hardware not available |
| Real-world transfer claims | `x4.transfer` | Within-VR study cannot test transfer |
| Pharmacological / biomarker outcomes | `x5.biomarker` | IRB + lab-support not available |

---

## References

Bohil, C. J., Alicea, B., & Biocca, F. A. (2011). Virtual reality in neuroscience research and therapy. *Nature Reviews Neuroscience*, *12*(12), 752–762. https://doi.org/10.1038/nrn3122

Bonomi, A. G., Goris, A. H. C., Yin, B., & Westerterp, K. R. (2009). Detection of type, duration, and intensity of physical activity using an accelerometer. *Medicine and Science in Sports and Exercise*, *41*(9), 1770–1777. https://doi.org/10.1249/MSS.0b013e3181a24536

Boucsein, W. (2012). *Electrodermal activity* (2nd ed.). Springer. https://doi.org/10.1007/978-1-4614-1126-0

Green, P. E., & Srinivasan, V. (1990). Conjoint analysis in marketing: New developments with implications for research and practice. *Journal of Marketing*, *54*(4), 3–19. https://doi.org/10.2307/1251756

Greenwald, A. G., McGhee, D. E., & Schwartz, J. L. K. (1998). Measuring individual differences in implicit cognition: The implicit association test. *Journal of Personality and Social Psychology*, *74*(6), 1464–1480. https://doi.org/10.1037/0022-3514.74.6.1464

Grossman, P., & Taylor, E. W. (2007). Toward understanding respiratory sinus arrhythmia: Relations to cardiac vagal tone, evolution and biobehavioral functions. *Biological Psychology*, *74*(2), 263–285. https://doi.org/10.1016/j.biopsycho.2005.11.014

Laborde, S., Mosley, E., & Thayer, J. F. (2017). Heart rate variability and cardiac vagal tone in psychophysiological research — Recommendations for experiment planning, data analysis, and data reporting. *Frontiers in Psychology*, *8*, 213. https://doi.org/10.3389/fpsyg.2017.00213

Loomis, J. M., Blascovich, J. J., & Beall, A. C. (1999). Immersive virtual environment technology as a basic research tool in psychology. *Behavior Research Methods, Instruments, & Computers*, *31*(4), 557–564. https://doi.org/10.3758/BF03200735

Mathôt, S. (2018). Pupillometry: Psychology, physiology, and function. *Journal of Cognition*, *1*(1), 16. https://doi.org/10.5334/joc.18

Orne, M. T. (1962). On the social psychology of the psychological experiment: With particular reference to demand characteristics and their implications. *American Psychologist*, *17*(11), 776–783. https://doi.org/10.1037/h0043424

Pan, X., & Hamilton, A. F. de C. (2018). Why and how to use virtual reality to study human social interaction: The challenges of exploring a new research landscape. *British Journal of Psychology*, *109*(3), 395–417. https://doi.org/10.1111/bjop.12290

Parsons, T. D. (2015). Virtual reality for enhanced ecological validity and experimental control in the clinical, affective and social neurosciences. *Frontiers in Human Neuroscience*, *9*, 660. https://doi.org/10.3389/fnhum.2015.00660

Schubert, T., Friedmann, F., & Regenbrecht, H. (2001). The experience of presence: Factor analytic insights. *Presence: Teleoperators and Virtual Environments*, *10*(3), 266–281. https://doi.org/10.1162/105474601300343603

Stephenson, W. (1953). *The study of behavior: Q-technique and its methodology*. University of Chicago Press.

Tassinary, L. G., Cacioppo, J. T., & Vanman, E. J. (2007). The skeletomotor system: Surface electromyography. In J. T. Cacioppo, L. G. Tassinary, & G. G. Berntson (Eds.), *Handbook of psychophysiology* (3rd ed., pp. 267–299). Cambridge University Press.

Toubia, O., Hauser, J., & Garcia, R. (2007). Probabilistic polyhedral methods for adaptive choice-based conjoint analysis: Theory and application. *Marketing Science*, *26*(5), 596–610. https://doi.org/10.1287/mksc.1060.0257

Watts, S., & Stenner, P. (2012). *Doing Q methodological research: Theory, method and interpretation*. SAGE Publications.

---

*This page is the source of truth for the Knowledge Atlas substitution skill. Updates to the page propagate to the skill's knowledge base via the build pipeline. If you find a measure that should be on the positive list and is not, or a measure that should be on the negative list and is not, file an issue or speak to the instructor.*
