# Activity-Aware Architecture: Microvenues, External Representations, and the Future of Co-Adaptive Buildings

**David Kirsh**
Department of Cognitive Science, UC San Diego

---

## Abstract

AI is moving from laptop to the built environment. It is easy enough for sensors to tell it whether someone is present. What it really needs to know is what they are doing — and what it should do about it. This paper argues that adaptive buildings should be designed not as smart envelopes for occupancy, light, air and sound, but as activity-aware environments. The central unit of adaptation is the activity space: the temporally structured, socially situated, cognitively interpreted arena of action. The building's job is to maintain a working model of public activity spaces, to configure microvenues that support each activity's current phase, and learn from the participants' responses. Two registers of cognition matter: a predictive-processing register, in which the building shapes attention and supplies priors; and a thinking-with-external-representations register, in which the building supplies surfaces and persistence for externalised thought. Physical parameters such as air quality, sound, and light remain important — they interact with biological, cognitive, and social needs — but they must be coordinated with rather than substituted for activity-level support. The building of the future should be closer to a skilled studio assistant than a control system.

---

## 1. From smart buildings to activity-aware buildings

For several decades, adaptive architecture has been organised around a simple idea: a building should respond to who is in it. The lights come on when we enter; the temperature adjusts to our presence; the ventilation tracks the carbon dioxide we exhale; the blinds answer the angle of the sun and the position of the chair. This is now mature technology and increasingly mature theory (Achten, 2019; Tabadkani, Roetzel, & Li, 2021; Nguyen, Han, & Vande Moere, 2022). Yet the deepest claim about the human–building relation — that the building is *for* the activity, not merely for the body — has more often been stated than worked out.

Generative AI changes the situation. Once a building can integrate calendars, transcripts, surface content, gesture, gaze, sketches, and document histories, the question is no longer whether it knows that someone is present. The question is whether it knows *what they are doing*. And once that question is on the table, a second one follows immediately: if the building knows what they are doing, what should it do about it?

This paper makes three claims. The first is that the proper unit of adaptation is the *activity space* — the temporally structured, socially situated, cognitively interpreted arena in which human activity unfolds. The second is that activity space has a *public* dimension (what is shared, observable, and jointly constructed) and an *individual* dimension (each participant's enactive bubble); the building's proper object is the public dimension, and its design must respect what it cannot infer. The third is that human cognition in buildings operates in two distinct registers — a perceptual-motor-attentional register well described by predictive processing, and a constructive-and-representational register in which people use the material world to *think* — and that the two registers place different demands on architecture and AI.

A teaser worth stating at the outset: predictive processing has become the dominant theoretical framework for human cognition in built environments, and on its own terms it is doing real work. But there is a class of cognitive activity that predictive processing distorts when it tries to capture, and this class is exactly the activity that makes design studios, mathematics seminars, laboratory benches, kitchens, and writers' desks valuable. If activity-aware architecture is built on predictive processing alone, it will systematically over-serve the perceptual layer of cognition and under-serve the thinking-with-the-world layer that humans depend on.

A running example threads the argument: a small interdisciplinary design team in a university studio across an afternoon. The example is not the argument; the argument is general. But the example is the device by which every claim in what follows can be made concrete.

## 2. A running example: the design studio

A studio at UCSD on a late Thursday afternoon. Four people are working on the renovation of a community health clinic in South San Diego. Anna is the lead architect; Ben her junior designer; Camila a public-health consultant from the School of Medicine; Devi the community liaison who has run the resident-engagement sessions. The room is six by eight metres, with a long table, three writable walls, two large displays, a small acoustic enclosure, and a window onto a courtyard. The building is activity-aware: it can act on partitions, lighting, surface assignments, acoustic masking, display content, and the surfacing of artefacts the team has produced in previous sessions.

The afternoon unfolds across six phases. In *orientation*, Anna recovers where Tuesday's session ended. In *comparison*, the team compares three site-plan schemes — an organisational frontage, a courtyard scheme, and a hybrid — against the brief's constraints. In *critique*, Camila challenges the courtyard scheme on accessibility grounds and Devi raises community-meeting concerns. In *generation*, Ben proposes a hybrid that absorbs the critique, and the group sketches modifications on paper. In *convergence*, open questions are named and next steps assigned. In *resolution*, decisions are captured. The studio's envelope holds still throughout. Almost everything else changes.

## 3. Activity space and its three levels

The studio's geometry does not change, but the activity space changes throughout the afternoon. By *activity space* I mean what the world looks like, and how it is structured, *under the description of the ongoing activity* (Kirsh, 2025). It is not the floor plan. It is the layered organisation of action — the goals, the phases, the affordances, the attentional foreground, the shared references, the social positioning — that the participants are constructing as they work.

Activity space has three levels (Kirsh, 1995, 2025). The *logical* level is the goal structure of the activity: what counts as success, what phases the activity passes through, what subgoals depend on which, what counts as an appropriate action now. The *physical* level is the material substrate: layout, surfaces, seating, displays, lighting, sightlines, sound field, and tools at hand. The *cognitive* level is what each participant is treating as salient, remembering, externalising, or ignoring as they work.

The three levels are not separable. They co-evolve. A change at the logical level (the team decides to commit today) reorganises the physical level (the three displays come into comparison) and shifts the cognitive level (Camila switches from open exploration to evaluative scrutiny). A change in the physical substrate (the building dims a display) can shift the cognitive level (the team reads the dimming as a cue to converge). The activity space is the joint trajectory of all three.

The architectural significance is that adaptive buildings should not optimise variables defined only at the physical level. Comfort, energy use, occupancy, and air quality are all physical-level variables, and a great deal of contemporary smart-building practice treats them as the whole of the problem. But the room's job, on the activity-space view, is to support the trajectory through *all three levels*.

## 4. What the building can and cannot see

The cognitive level contains content the building cannot directly observe and content not equally shared by the participants. This forces a distinction the activity-space literature has not always made explicit. *Public* activity space is the organisation of action that the participants jointly construct and that the building can observe: the sketches on the wall, the schemes on the displays, the seating geometry, the audible discussion. *Individual* activity space is each participant's enactive bubble — Camila's remembered cases of inaccessible courtyards, Ben's gallery of hybrid precedents, Anna's awareness of the timeline, Devi's recall of the community meeting.

Historically philosophers drew the mind–world boundary at the skin. The extended-mind tradition and active inference have challenged that boundary; when Camila adds a perpendicular line to Ben's sketch, the cognitive system at that moment is *Camila-plus-marker-plus-paper-plus-Ben-plus-line*. But this distribution does not erase the individual–public distinction; it relocates it. The thinking is distributed, but Camila's remembered cases, aesthetic projections, and professional judgement are still hers alone. The individual activity space survives the extended-mind move; it is no longer body-bounded.

The two are coupled through *externalisation*. When Camila adds the perpendicular line, content moves from her individual activity space into the public activity space, where it becomes a shared reference. Conversely, when Ben looks at the line, the public mark generates new contents in his individual activity space. The traffic is continuous during active work.

The architectural consequences are three. First, the building's proper object is the public activity space, not the individual activity spaces of its occupants. Second, much of what later sections will call *thinking with external representations* is exactly the work of moving content from individual to public; the architectural support for that work is what makes a design studio valuable. Third, the privacy and first-person-gap arguments of §10 follow from this restriction: the building should support the activity, not surveil the participants.

## 5. Activity space as a latent space

The building's job, formally, is to maintain a working model of the public activity space — a structured guess about what is going on now, including its uncertainty — and to evaluate candidate interventions by their expected effect on the trajectory through that model. The public activity state at any moment can be summarised as the joint configuration of where the participants are, what social-pragmatic context they are in (the project, the role assignments, the standing norms), what activity phase they are in, what microvenue configuration the building has set, and the social-orientational state of who attends to whom. In notation, this is $z_t = (x_t, c_t, \varphi_t, m_t, s_t)$, inferred from observations $o_t$ via a generative model; the formal apparatus belongs to a separate paper on the cognitive-science of activity space (Kirsh, in preparation).

What matters for the architectural argument is what the formalism makes precise. *Maintaining a working model* means the building has a structured guess about the activity, with uncertainty bands on each component. *Evaluating interventions* means the building can ask whether raising a partition, surfacing yesterday's sketch, or dimming a display would make the activity state more likely to evolve toward a workable configuration. *Learning from consequences* means the building updates its working model when the team accepts, ignores, overrides, or appropriates what it offered.

Two caveats. The inferred model is the building's representation of the *public* activity space; it is not the activity itself, and it is not the individual activity spaces of the participants. Even within the public activity space, the model is necessarily approximate: sensor coverage is partial, phase boundaries are fuzzy, social-orientational state is genuinely contested some of the time. The architectural response is *graded confidence*: the building should offer rather than impose, suggest rather than enforce, and treat its own model as a working hypothesis rather than a settled fact.

## 6. Microvenues across the afternoon

The output of an activity-aware building is not a *setting* but a *microvenue*. A microvenue is a temporary, activity-specific place created by coordinating physical, digital, social, and sensory conditions. It may last five minutes or three hours.

Watch the studio across the six phases. In *orientation*, the building creates an attention-narrowing microvenue: the front display surfaces Tuesday's unresolved-issues list, the back walls dim, the table lighting brightens to draw the four bodies together. In *comparison*, the microvenue inverts: three site-plan schemes appear on three parallel walls, the table dims, yesterday's annotations are restored as translucent overlays. In *critique*, the microvenue contracts around the contested scheme: the courtyard option is centred, the others recede, the table-edge becomes writable, the acoustic field tightens so in-team intelligibility is high while external masking increases. In *generation*, the microvenue opens up: wall displays dim, a fresh paper sheet enters the table, a precedent panel appears quietly on a side display. In *convergence*, the microvenue stages summary: the hybrid sketch is photographed and placed on the central wall alongside a list of open questions. In *resolution*, the microvenue prepares the handoff.

Two features of this account deserve emphasis. First, none of these microvenues required dramatic architectural movement. Walls did not glide, ceilings did not lower, façades did not breathe. The envelope held still. What changed was the *coordinated configuration* of small variables: lighting balance, display content, surface assignment, acoustic field, and the visibility of past traces. Adaptive architecture has often been imagined as theatrical; much adaptive support, on this view, should be quieter and more reversible.

Second, the microvenues are not all of the same kind. The orientation, comparison, critique, convergence, and resolution microvenues are predictive-processing scaffolds: they shape attention, narrow uncertainty, supply priors, and make phase structure legible. The generation microvenue is different. It is a *thinking-with-external-representations scaffold*. It does not narrow uncertainty so much as create a surface on which new structure can be brought into existence.

## 7. Architectural jigs as predictive scaffolds

In skilled work, a *jig* is a structure that makes an action easier, more repeatable, or less cognitively demanding (Kirsh, 1995). A carpenter cuts boards to the same length not by re-measuring each but by setting a stop. Buildings can supply similar jigs. The studio's *comparison wall* — three side-by-side schemes with yesterday's annotations restored — is an architectural jig. So is the lighting balance that brightens the wall surfaces and dims the table during comparison. So is the acoustic field that supports silent reading during comparison and audible disagreement during critique.

These jigs are externalised priors and precision-shaping devices in predictive-processing terms (Clark, 2013, 2016; Friston, FitzGerald, Rigoli, Schwartenbeck, & Pezzulo, 2017). The comparison wall makes a particular interpretation of the current activity more probable. The dimming of the table relative to the walls narrows precision on the scheme content. The acoustic attenuation outside the team raises the signal-to-noise ratio for the in-team channel.

The jig is not the same as a script. Good architectural jigs are *open-textured*. The comparison wall offers three displays, but it does not insist on a particular comparison order. The jig increases agency by removing low-value cognitive work; it does not increase the building's authority. When a jig fails, it usually fails by over-scripting — by removing the freedom to compare in an unexpected order, or to use one wall as a parking lot for rejected detail. The participants will work around it, and the override is informative.

## 8. Microvenues for thinking — the second register

Consider the generation phase. Ben pulls a fresh sheet of large paper to the table, takes the marker, and begins to sketch a hybrid scheme. He does not have the hybrid in his head before he starts. The first line is a guess; the second is an adjustment; by the time he has six lines, he can *see* whether the hybrid resolves Camila's accessibility concern. Camila reaches over and adds a perpendicular line. Devi marks an X. Anna sketches a floor-plate boundary. By the time the sketch is half-formed, the four of them are thinking together by means of the sketch in a way none of them could think alone.

This is not the active-inference loop. It is something else, and it requires its own theoretical vocabulary (Kirsh, 2010). What the sketch offers — and what active inference does not capture cleanly — is *re-representation* (Anna can see the hybrid as a courtyard-with-a-frontage or as a frontage-with-a-courtyard), *persistence and re-identifiability* (Camila's line is still there in ten minutes), *operability* (Anna can measure with a ruler, Ben can photograph and overlay), *joint construction* (the four built the sketch together; the reference "this corner" is shared because the externalisation is shared), and *generativity* (the lines suggest other lines, primed visual associations no one brought to the conversation).

A defender of predictive processing will say that all of this can be cast as policy selection under expected free energy. The move is technically defensible and explanatorily empty: it generalises the formalism until it predicts everything and distinguishes nothing. The more honest theoretical position is that predictive processing is a powerful and partial account of cognition, that it captures some external-representation use (epistemic actions like Tetris rotation, where there is a fixed hidden state to disambiguate), and that it does not capture the re-representational, exploratory, and constructive uses that designers, mathematicians, choreographers, writers, and ordinary thinkers depend on. Those latter uses require a different architectural support.

The generation microvenue must support externalisation (a large reachable surface), persistence (no wiping between sessions), re-identification (yesterday's lines remain available with identity intact), rearrangement (the team can cut, photograph, overlay, move), shareability (all four can see and point), and — crucially — *protection of in-progress structure* against premature smoothing. AI assistance in this microvenue must not auto-clean, auto-complete, or auto-summarise the sketch. The roughness, the half-erased false starts, the contested marks, the ambiguities — these are not defects. They are how the externalisation works.

## 9. Physical parameters and biological needs

The activity-space argument should not be read as a dismissal of the physical parameters that smart-building practice has worked on for decades. Air quality, sound, light, thermal comfort, and personal control are not peripheral to activity-aware architecture; they are part of its substrate. They interact with biological, cognitive, and social needs of the participants in ways the building must respect.

Air quality and ventilation have measurable effects on cognitive performance and decision-making. Allen et al. (2016) and Satish et al. (2012) document substantial impairment of cognitive function scores under elevated CO₂ and reduced ventilation conditions; the effects are large enough that office productivity studies routinely treat ventilation as a primary variable. For the studio, this means the building must hold ventilation within a range that keeps Camila's accessibility-critique thinking and Ben's hybrid-generation thinking on solid biological ground. The activity-aware regime does not displace this; it adds to it.

Sound and speech intelligibility are major determinants of cognitive performance. Irrelevant speech impairs serial recall and working memory (Jones & Macken, 1993), and speech intelligibility often matters more than loudness alone (Hongisto, 2005). For the studio, the critique-phase tightening of in-team intelligibility and external masking is doing two kinds of work at once: it shapes precision in predictive-processing terms, and it satisfies the biological-cognitive demand that the four participants not be distracted by an adjacent open-plan conversation.

Light affects circadian physiology and alertness under some conditions (Brainard et al., 2001; Cajochen, Zeitzer, Czeisler, & Dijk, 2000). Daylight and view exposure are associated with restoration and stress recovery (Ulrich, 1984; Kaplan, 1995). Personal control over lighting improves satisfaction even when objective conditions are similar (de Dear & Brager, 1998). The activity-aware studio uses lighting both to shape attention (a phase-specific composition) and to respect the participants' biological pacing across an afternoon — warmer light as the afternoon wears on, brighter task light during convergence when the team needs energy for closure.

Thermal comfort, glare control, and biophilic elements (where present) operate similarly. None of these is sufficient on its own; none is dispensable. The activity-aware integration is that physical parameters are no longer optimised in isolation but coordinated for the activity. A studio that maximises ventilation efficiency by drawing too much air may make the conversation harder to hear; the building must balance the two. A studio that maximises daylight may produce glare on the courtyard scheme during critique; the building must balance again. The activity-aware regime is, at this layer, a coordination problem — and AI's role is to do the coordination work that human designers have done by intuition and rule-of-thumb. The empirical evidence base for these parameters individually is strong; the evidence for closed-loop, activity-coordinated regulation of them together is thin, and the design recommendations in this paper should be read as hypotheses to be tested by the system itself.

## 10. The return path, privacy, and the first-person gap

Every architectural intervention is a hypothesis. The building's models are by hypothesis incomplete; its interventions are educated guesses; the only way to know whether an intervention helped is to observe what the participants do next. The *return path* — sense, infer, intervene, observe response, revise the model — is therefore constitutive of activity-aware architecture, not optional.

The return-path evidence runs on two clocks. In the predictive register, evidence arrives in seconds to minutes: overrides, postural changes, voice attenuation, attention coherence. Override is the highest-quality signal the building gets in this register. In the thinking register, evidence arrives over days to weeks: which externalised structures are returned to, which are built on, which are consolidated into deliverables. A sketch useful for Thursday's generation may not be touched until Tuesday. The building must run both clocks.

A subtle category of return-path evidence crosses both registers: the participants' *appropriation* of the room. When Anna turns a chair sideways, when Devi blocks a partition, when Camila leaves a sketch up overnight that the building wanted to archive — the participants are teaching the building. Appropriation is not noise; it is what the participants know about the activity that the building does not.

Privacy and the first-person gap follow from §4's public–individual distinction. The building's proper object is the public activity space; the individual activity spaces are not in scope. The operational principle is *infer the least private state sufficient to support the activity*. The building needs to know that critique is happening; it does not need to know that Camila is frustrated. It needs to know that Devi has raised an objection; it does not need a persistent psychological profile of Devi.

There is a deeper limit. The building can observe behaviour, but it does not have first-person access. It may infer that Camila often turns toward the window after long meetings; it does not know what the break feels like. It may detect that Anna pauses before deciding; it does not feel the weight of the decision. Skilled action and considered judgement are body-specific, history-specific, and context-specific. AI can model external correlates of expertise; it does not thereby possess the expert's lived competence.

The right conclusion is not that AI is useless in architecture, but that architectural AI should be *modest*. It should support the conditions of action rather than claim ownership of experience. It should help stage the workshop without pretending to be the artisan.

## 11. Design principles

Several principles follow. *Design for activity, not occupancy*: presence is not the relevant variable. *Create microvenues, not settings*: the studio is reconfigured across six phase-specific places, not configured once for the afternoon. *Distinguish predictive microvenues from thinking microvenues*: the first narrow attention; the second supply surfaces and persistence; conflating them produces bad architecture. *Use architectural jigs*: open-textured constraints that reduce cognitive friction without scripting behaviour. *Coordinate physical parameters with activity*: air, sound, light, thermal comfort, and glare are not optimised in isolation but composed for the current phase. *Preserve appropriable slack*: leave more configuration possibilities than the model insists on. *Close the loop*: every intervention is a hypothesis; learn on two clocks. *Be legible*: occupants should understand what the building is doing and why. *Target the public activity space*: do not model individual activity spaces. *Infer the least private state*: activity-level inference suffices. *Respect the first-person gap*: the building stages; it does not author. *Protect in-progress externalisation*: AI must not auto-clean, auto-organise, or auto-summarise structures the participants are still building. *Run two clocks*: predictive scaffolding on seconds-to-minutes, thinking-register scaffolding on days-to-weeks.

## 12. Conclusion

AI is changing work because it is changing the organisation of cognitive effort. It is changing what is drafted, searched, summarised, delegated, checked, remembered, and coordinated. It would be strange to suppose this transformation will remain confined to the laptop. Human activity is spatial, embodied, social, and materially scaffolded. As AI becomes more capable of understanding activity, it will migrate into the physical environments where activity occurs.

The question is what kind of migration this should be. One path leads to overconfident automation: buildings that infer too much, decide too much, optimise crude proxies, and close down human improvisation. The better path is activity-aware architecture: buildings that infer just enough about the public activity space to be useful, respect the individual activity spaces they cannot see, create temporary microvenues for both predictive scaffolding and externalised thinking, coordinate physical parameters with activity-level needs, preserve shared memory and in-progress structure, and remain humble about what they know.

The building of the future should not be a boss, a therapist, or an invisible manipulator. It should be closer to a skilled studio assistant — preparing, staging, shielding, remembering, clearing, offering, withdrawing, and learning. It helps Anna and Ben and Camila and Devi create the local world in which they can do their work well: predictively, when prediction is what is needed; constructively, when the work is to think something into existence that none of them yet knows.

---

## References

Achten, H. H. (2019). Interaction narratives for responsive architecture. *Buildings*, 9(3), 66. https://doi.org/10.3390/buildings9030066 (Google Scholar: ~80)

Allen, J. G., MacNaughton, P., Satish, U., Santanam, S., Vallarino, J., & Spengler, J. D. (2016). Associations of cognitive function scores with carbon dioxide, ventilation, and volatile organic compound exposures in office workers. *Environmental Health Perspectives*, 124(6), 805–812. https://doi.org/10.1289/ehp.1510037 (Google Scholar: ~700)

Brainard, G. C., Hanifin, J. P., Greeson, J. M., Byrne, B., Glickman, G., Gerner, E., & Rollag, M. D. (2001). Action spectrum for melatonin regulation in humans. *Journal of Neuroscience*, 21(16), 6405–6412. (Google Scholar: ~1,500)

Cajochen, C., Zeitzer, J. M., Czeisler, C. A., & Dijk, D. J. (2000). Dose-response relationship for light intensity and ocular and electroencephalographic correlates of human alertness. *Behavioural Brain Research*, 115(1), 75–83. (Google Scholar: ~700)

Clark, A. (2013). Whatever next? Predictive brains, situated agents, and the future of cognitive science. *Behavioral and Brain Sciences*, 36(3), 181–204. https://doi.org/10.1017/S0140525X12000477 (Google Scholar: ~3,800)

Clark, A. (2016). *Surfing uncertainty: Prediction, action, and the embodied mind*. Oxford University Press. (Google Scholar: ~3,000)

Clark, A., & Chalmers, D. (1998). The extended mind. *Analysis*, 58(1), 7–19. https://doi.org/10.1093/analys/58.1.7 (Google Scholar: ~7,500)

de Dear, R. J., & Brager, G. S. (1998). Developing an adaptive model of thermal comfort and preference. *ASHRAE Transactions*, 104(1), 145–167. (Google Scholar: ~1,400)

Friston, K. J., FitzGerald, T., Rigoli, F., Schwartenbeck, P., & Pezzulo, G. (2017). Active inference: A process theory. *Neural Computation*, 29(1), 1–49. https://doi.org/10.1162/NECO_a_00912 (Google Scholar: ~3,200)

Hongisto, V. (2005). A model predicting the effect of speech of varying intelligibility on work performance. *Indoor Air*, 15(6), 458–468. https://doi.org/10.1111/j.1600-0668.2005.00391.x (Google Scholar: ~450)

Hutchins, E. (1995). *Cognition in the wild*. MIT Press. (Google Scholar: ~10,000)

Jones, D. M., & Macken, W. J. (1993). Irrelevant tones produce an irrelevant speech effect. *Journal of Experimental Psychology: Learning, Memory, and Cognition*, 19(2), 369–381. (Google Scholar: ~700)

Kaplan, S. (1995). The restorative benefits of nature: Toward an integrative framework. *Journal of Environmental Psychology*, 15(3), 169–182. (Google Scholar: ~6,000)

Kirsh, D. (1995). The intelligent use of space. *Artificial Intelligence*, 73(1–2), 31–68. https://doi.org/10.1016/0004-3702(94)00017-U (Google Scholar: ~1,400)

Kirsh, D. (2010). Thinking with external representations. *AI & Society*, 25(4), 441–454. https://doi.org/10.1007/s00146-010-0272-8 (Google Scholar: ~600)

Kirsh, D. (2025). Reimagining space: How activity space explains human behaviour in buildings. *Architectural Science Review*. https://doi.org/10.1080/00038628.2025.2542213

Kirsh, D. (in preparation). A formal theory of activity space: Filling a gap in the cognitive science of environments.

Nguyen, B. V. D., Han, J., & Vande Moere, A. (2022). Towards responsive architecture that mediates place. *Proceedings of the ACM on Human-Computer Interaction*, 6(CSCW2). https://doi.org/10.1145/3555568

Satish, U., Mendell, M. J., Shekhar, K., Hotchi, T., Sullivan, D., Streufert, S., & Fisk, W. J. (2012). Is CO2 an indoor pollutant? Direct effects of low-to-moderate CO2 concentrations on human decision-making performance. *Environmental Health Perspectives*, 120(12), 1671–1677. https://doi.org/10.1289/ehp.1104789 (Google Scholar: ~400)

Tabadkani, A., Roetzel, A., & Li, H. (2021). A review of occupant-centric control strategies for adaptive facades. *Automation in Construction*, 122, 103464. https://doi.org/10.1016/j.autcon.2020.103464 (Google Scholar: ~150)

Ulrich, R. S. (1984). View through a window may influence recovery from surgery. *Science*, 224(4647), 420–421. https://doi.org/10.1126/science.6143402 (Google Scholar: ~3,500)
