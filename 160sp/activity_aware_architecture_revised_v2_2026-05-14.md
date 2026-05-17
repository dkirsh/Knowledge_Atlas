# Activity-Aware Architecture: Predictive Scaffolding, External Representations, and the Future of Co-Adaptive Buildings

**David Kirsh**
Department of Cognitive Science, UC San Diego

---

## Abstract

AI is moving from the laptop into the room. Generative systems already draft, summarise, schedule, search, and compare; the practical question is no longer whether they will participate in cognitive work but where the participation will take place. This essay argues that adaptive buildings should not be conceived as smart envelopes for occupancy, light, and air, but as activity-aware environments that help create, sustain, transform, and dissolve the local conditions under which human activity proceeds. I propose three related theoretical moves. First, the central unit of adaptation is the *activity space*: the temporally structured, socially situated, cognitively interpreted arena of action, which can be formalised as the latent state space the building infers and acts in. Second, activity space has both a *public* dimension (the shared, observable, jointly constructed organisation of action) and an *individual* dimension (each participant's enactive bubble), and the two are coupled through externalisation; the building's proper object is the public activity space, but its design must respect what it cannot infer. Third, human cognition in buildings operates in two distinct registers: a *predictive-processing* register well described by active-inference theories, and a *thinking-with-external-representations* register in which sketches, surfaces, marks, and arrangements are used to externalise, persist, rearrange, and jointly construct in-progress thought. The two registers have different design requirements, different metrics of success, and different dangers of over-adaptation. An activity-aware building must support both — building microvenues and jigs for each — while preserving appropriable slack, observing the return path, respecting the first-person character of experience, and inferring no more about its occupants than the activity actually demands.

---

## 1. Introduction: From buildings that hold us to buildings that think with us

For several decades, adaptive architecture has been organised around a deceptively simple idea: a building should respond to who is in it. The lights come on when we enter; the temperature adjusts to our presence; the ventilation tracks the carbon dioxide we exhale; the blinds answer the angle of the sun and the position of the chair. This is now mature technology and increasingly mature theory. Adaptive façades, occupant-centric control strategies, and responsive architecture have become genuine subfields, with their own conferences, journals, and standards (Achten, 2019; Lee, Ostwald, & Kim, 2021; Nguyen, Han, & Vande Moere, 2022; Tabadkani, Roetzel, & Li, 2021). Yet the deepest claim about the human–building relation — that the building is *for* the activity, not merely for the body — has so far been more often stated than worked out.

Generative AI changes the situation. Once a building can integrate calendars, transcripts, surface content, gesture, gaze, sketches, and document histories, the question is no longer whether the building knows that someone is present. The question is whether it knows *what they are doing*. And once that question is on the table, a second question follows immediately: if the building knows what they are doing, what should it do about it? Adaptive architecture currently has no theory adequate to either question.

This essay argues for a theory of activity-aware architecture organised around three claims. The first is that the proper unit of adaptation is the *activity space* — the temporally structured, socially situated, cognitively interpreted arena in which human activity unfolds — and that activity space can be formalised as the latent state space the building infers from observable signals and acts on through its actuator repertoire. The second is that this latent state space has a public dimension that the building can in principle reach and an individual dimension that it cannot, and that the architectural support of activity is largely a matter of helping the externalisation traffic between the two. The third is that human cognition in buildings operates in two distinct registers — a perceptual-motor-attentional layer well described by predictive processing and active inference, and a constructive-and-representational layer in which people use the material world to think — and that the two registers place different demands on architecture, on the AI that operates within it, and on the design choices that determine whether such a building helps or hinders the work it claims to serve.

The teaser I want to leave with the reader at the outset is this. Predictive processing has become the dominant theoretical framework for human cognition in built environments, and on its own terms it is doing real work. But there is a class of cognitive activity that predictive processing distorts when it tries to capture, and this class is exactly the activity that makes design studios, mathematics seminars, laboratory benches, kitchens, and writers' desks valuable. If activity-aware architecture is built on predictive processing alone, it will systematically over-serve the perceptual-motor-attentional layer of cognition and under-serve the thinking-with-the-world layer that humans depend on. The argument that follows is partly about why this is so, and partly about what activity-aware architecture should look like if both layers are to be respected.

A running example threads the argument: a small interdisciplinary design team working on the renovation of a community health clinic, in a UCSD studio across an afternoon. The example is not the argument; the argument is general. But the example is the device by which the general argument can be made specific enough to be tested against the reader's own intuitions about how rooms work and what AI in rooms should do.

## 2. A running example: the design team in the studio

A small studio at the University of California, San Diego, late on a Thursday afternoon. Four people are working on the renovation of a community health clinic in South San Diego. Anna is the lead architect, Ben her junior designer, Camila a public-health consultant from the School of Medicine, Devi the community liaison who has run the resident-engagement sessions. The room is roughly six by eight metres, with a long table, three writable walls, two large displays, a small acoustic enclosure, and a window onto a courtyard. The building in which the studio sits is activity-aware: it is networked, sensored, and can act on a small set of architectural variables — partitions, lighting, surface assignments, acoustic masking, display content, and the surfacing of digital artefacts the team has produced in previous sessions.

The afternoon unfolds across six phases. *Orientation*: Anna gathers the group and recalls where Tuesday's session ended. *Comparison*: the team compares three site-plan schemes — an organisational frontage, a courtyard scheme, and a hybrid — against the brief's constraints. *Critique*: Camila challenges the courtyard scheme on accessibility grounds and Devi raises community-meeting concerns. *Generation*: Ben proposes a hybrid that absorbs the critique, and the group sketches modifications on paper at the table. *Convergence*: open questions are identified, next steps are assigned. *Resolution*: decisions are captured in a form that can be handed off to consultants. The room's envelope never changes. Almost everything else does.

I shall return to Anna, Ben, Camila, and Devi at every theoretical move in the rest of the paper. Every claim — about activity space, about the public–individual distinction, about the latent-state formalism, about the two registers of cognition, about microvenues, jigs, the return path, and the first-person gap — is instantiated in this afternoon.

## 3. Activity space and its three levels

The studio's geometry does not change, but the activity space changes throughout the afternoon. By *activity space* I mean what the world looks like, and how it is structured, *under the description of the ongoing activity* (Kirsh, 2025). It is not the floor plan. It is not the schedule. It is not the list of people present. It is the layered organisation of action — the goals, the phases, the affordances, the attentional foreground, the shared references, the social positioning — that is being constructed by the participants as they work.

I have argued elsewhere that activity space is best analysed at three levels (Kirsh, 1995, 2025). The *logical* level concerns the goal structure of the activity: what counts as success, what phases the activity passes through, what subgoals depend on which, what counts as an appropriate action right now. For Anna's team, the logical level includes the brief, the schedule of deliverables, the unresolved decisions from Tuesday, the dependencies — a site-plan choice will commit floor-plate dimensions, which will commit clinical layout — and the implicit norms of how this team negotiates disagreement.

The *physical* level concerns the material substrate: the layout, surfaces, seating, displays, lighting, sightlines, sound field, and the tools at hand. For the team, this includes the long table, the three writable walls, the two displays, the acoustic enclosure, the courtyard window, and whatever sketches, models, and notes survive from previous sessions. It also includes their bodies — where they stand, what they can reach, who can see what — and the changing pattern of their attention.

The *cognitive* level concerns what each participant is treating as salient, what they are remembering, what they are inferring, what they are ignoring, what they are externalising, and how they are using the material around them as scaffolding for thought. This level requires careful handling because it includes content that the building cannot directly observe, content that is shared between participants only partially, and content that depends on the personal history and professional formation of each participant. The next section is devoted to clarifying what the cognitive level includes and what role it plays in the architectural argument.

The three levels are not separable in practice. They co-evolve. A change in the goal structure (Anna decides the team must commit to a site-plan today) changes the relevant features of the physical substrate (the three displays must be brought into comparison) and changes the cognitive level (Camila switches from open exploration to evaluative scrutiny). A change in the physical substrate (the building dims the front display to reduce glare) can shift the cognitive level (the team interprets the dimming as a cue that they should converge). A change in the cognitive level (Ben recognises a sketch as a hybrid that absorbs the critique) can change the goal structure (the team can now commit to a refined scheme). The activity space is the joint trajectory of all three.

The architectural significance of this analysis is that adaptive buildings should not optimise variables defined only at the physical level. Comfort, energy use, occupancy, and air quality are all physical-level variables, and a great deal of contemporary smart-building practice treats them as the whole of the problem (Allen et al., 2016; Tabadkani et al., 2021). But the room's job, on the activity-space view, is to support the trajectory through *all three levels*: to make the goal structure perceptible, to configure the physical substrate to the current logical demands, and to scaffold the cognitive work that is going on.

## 4. Public and individual activity space

The cognitive level introduced in §3 contains contents the building cannot directly observe and contents that are not equally shared by the participants. This requires a distinction that the activity-space literature has not generally made explicit and that I want to make explicit now, because it has direct consequences for what a building should and should not infer.

In one sense, activity space is a *public* object. It is the organisation of action that the four participants can in principle reach together, that has shared reference points, and that the building can observe. The sketches on the wall, the schemes on the displays, the seating geometry, the agenda, the audible discussion, the visible gestures, the marks on the paper — these are part of activity space in the public sense. The building can sense them; all four participants can attend to them; they have identity conditions that survive reidentification across time. This is the activity space that maps onto the latent-state formalism of §5 and the appendix; it is what the building infers and acts upon.

In another sense, activity space is *individual*. Each participant has their own enactive bubble (Kirsh, 2025) — what they are treating as salient, remembering, projecting onto the scene, inferring, ignoring. Camila's experience of the courtyard scheme — the patient populations she has worked with, the families with strollers she remembers from her clinic visits, the precedents she calls to mind, her sense of the proportions of the courtyard against the buildings she has known — is part of *her* activity space in the individual sense. It is not directly part of anyone else's. The four participants share a room and a project; they do not share an experience.

Historically philosophers drew the mind–world boundary at the skin. Mental activity was inside; bodily and material activity was outside; the distinction was clean. The extended-mind tradition (Clark & Chalmers, 1998, ~7,500 citations; Clark, 2008), the active-inference tradition (Friston, 2010, ~12,000; Constant, Clark, Kirchhoff, & Friston, 2022, ~150), and the work on epistemic action (Kirsh & Maglio, 1994, ~1,500) have variously challenged this clean boundary. When Camila adds a perpendicular line to Ben's sketch, the cognitive act is not located in her head; it is constituted by the joint operation of her perception, her motor action, and the marks on the paper. The marker, the paper, and the line are not external props to a mental process; they are part of the process.

Yet the extended-mind move does not resolve the question of where the activity space ends. When Camila has a thought *about* the courtyard scheme — a thought that depends on her remembered cases, her aesthetic sensibilities, her professional judgement, her relationship history with the team — is that thought part of the activity space, or adjacent to it? It is closely coupled to the public activity space (it is *about* the scheme on the wall) and it has consequences within the public activity space (it will move her to mark the paper, to speak, to lean forward). But the thought itself, qua thought, is hers alone. It is not in the room in the way the sketch on the table is in the room.

The right way to put this, I think, is to distinguish *public* and *individual* activity space and to be precise about how they are coupled.

The *public activity space* is the set of structures, surfaces, marks, configurations, traces, words, and gestures that the participants jointly construct and that have shared identity conditions. The building can observe it; all four participants can refer to it; it survives reidentification. It is the proper target of the building's inference and the proper subject of the latent-state formalism.

The *individual activity space* is each participant's enactive bubble — the contents they are treating as salient, the inferences they are running, the projections they are making onto the scene. Each participant has one; the four are different even when the participants are looking at the same wall. The building cannot infer the individual activity space directly. It can sometimes infer correlates — Camila's hesitation, Devi's lean, Ben's mid-sentence pause — but it cannot infer the contents.

The two are coupled through *externalisation* and *internalisation*. When Camila adds the perpendicular line, an item from her individual activity space becomes part of the public activity space. The line is now a shared reference, available to all four participants and to the building. Conversely, when Ben looks at the line, the public mark generates new contents in his individual activity space — perhaps a recognition of what Camila was after, perhaps a counter-proposal, perhaps a private worry about whether the line is structurally feasible. The traffic between public and individual is more or less continuous during active work, and the productivity of the work depends in part on how cheap and reliable that traffic is.

This distinction matters for activity-aware architecture in three specific ways.

First, the building's proper object is the public activity space, not the individual activity spaces of its occupants. The privacy principle of §13 — *infer the least private state sufficient to support the activity* — is a direct corollary. The building can know that critique is happening (a feature of the public activity space) without inferring that Camila is frustrated (a feature of her individual activity space). The first inference is in scope; the second is not. The building should support the activity; it should not surveil the participants.

Second, much of what I will later call *thinking with external representations* (§8) is exactly the work of moving content from the individual activity space into the public activity space. When Ben sketches the hybrid scheme, he is not (only) reducing his uncertainty about a fixed external fact. He is *bringing into existence* a public structure that can be operated on, referred to, modified, and re-identified by the group. The architectural support for this kind of cognitive work — surfaces, persistence, re-identifiability — is in large part support for the *externalisation traffic* between individual and public activity spaces. A good design studio is one in which that traffic is cheap, reliable, and protected against premature smoothing.

Third, the extended-mind move tells us that we should not locate Camila's cognitive activity inside her skull when she is in active externalisation with Ben at the table. The cognitive system at that moment is *Camila-plus-marker-plus-paper-plus-Ben-plus-line*. The thinking is distributed across the four-person team and the material substrate (Hutchins, 1995, ~10,000; Clark & Chalmers, 1998). But this distribution does not erase the individual–public distinction; it relocates it. The thinking is distributed, but it is still the case that there are contents specific to Camila — the remembered cases, the aesthetic projections, the professional judgement — that are not in the room and are not shared by the rest of the team or the building. The individual activity space survives the extended-mind move. It is just no longer body-bounded; it is constituted by what Camila brings to the activity and the cognitive trajectory she undertakes as she engages with the public activity space.

The asymmetry, then, is this: the public activity space *is* the activity space in the sense that the building can model it; the individual activity spaces are *partially constitutive* of the activity in that they motivate and accompany the public externalisations. An activity-aware building can support the activity well by attending to the public activity space and by understanding that what it sees there is partly the trace of individual contributions it cannot see.

## 5. Activity space as a latent state space

With the public–individual distinction in place, I can state the formal commitment cleanly. The *public* activity space is what the building must infer. Let the public activity state at time $t$ be
$$z_t = (x_t, c_t, \varphi_t, m_t, s_t)$$
where $x_t$ is the agent–environment configuration, $c_t$ is the social-pragmatic context, $\varphi_t$ is the current activity phase, $m_t$ is the microvenue configuration, and $s_t$ is the social-orientational state. Appendix A unpacks each variable in detail — its semantic content, the observable signals from which the building infers its value, the computational method by which the inference proceeds, and an example value at a moment in the running example. The body of this paper assumes the reader has at least skimmed the appendix once.

The building cannot observe $z_t$ directly; it observes only $o_t$ — a stream of multi-modal signals from sensors, calendars, transcripts, device usage, surface content, and explicit requests. Its task is to maintain a posterior $q(z_t \mid o_{1:t})$ over the activity state, to evaluate candidate interventions $\pi$ by their expected effect on the trajectory through this latent space, and to learn from the consequences of those interventions. The formal apparatus is partially observable generative models (Friston, 2010; Friston, FitzGerald, Rigoli, Schwartenbeck, & Pezzulo, 2017), variational state-space methods (Kingma & Welling, 2014; Hafner, Lillicrap, Norouzi, & Ba, 2020), predictive maps or successor representations for transition dynamics (Stachenfeld, Botvinick, & Gershman, 2017), hierarchical-reinforcement-learning option discovery for phase structure (Sutton, Precup, & Singh, 1999; Bacon, Harb, & Precup, 2017), and Bayesian theory-of-mind for the inference of social-orientational state (Baker, Saxe, & Tenenbaum, 2009; Baker, Jara-Ettinger, Saxe, & Tenenbaum, 2017). The architectural reader should read these citations as a statement of where the engineering substrate sits, not as a recommendation that the building be built out of one specific algorithm.

What matters for the architectural argument is what the formalism makes precise. *Maintaining a posterior over the activity state* means the building has a structured guess about what is going on, including its uncertainty about that guess. *Evaluating interventions by expected effect in the latent space* means the building can ask whether raising a partition, surfacing yesterday's sketch, or dimming a display would make the activity state more likely to evolve toward a workable configuration. *Learning from the consequences of interventions* means the building updates its posterior when the team accepts, ignores, overrides, or appropriates what it offered. The vocabulary of priors, precisions, policies, and expected free energy from predictive processing maps onto these operations cleanly, and so does the vocabulary of microvenues and architectural jigs from architectural cognition. The two vocabularies describe the same operations from different sides.

Two caveats must be stated explicitly. First, the inferred latent state is the building's model of the *public* activity space, not the activity itself. Camila's first-personal experience of the courtyard scheme is part of her individual activity space, not part of $z_t$ as the building can compute it. The formalism is a useful scaffolding for the building's decisions; it is not a complete description of what is happening in the room. Second, even within the public activity space, the building's posterior is necessarily approximate. Sensor coverage is partial; the inferred phase boundaries are fuzzy; the social-orientational state is genuinely contested some of the time. The right architectural response to this approximation is the *graded confidence* I discuss in §11 and §13: the building should offer rather than impose, suggest rather than enforce, and treat its own model as a working hypothesis rather than a settled fact.

## 6. Microvenues: temporary places for temporary activities

The output of an activity-aware building is not a *setting* but a *microvenue*. A microvenue is a temporary, activity-specific place created by coordinating physical, digital, social, and sensory conditions. It may last five minutes or three hours. It may involve walls, furniture, surfaces, lighting, acoustic masking, displays, privacy boundaries, access permissions, and the surfacing of past traces. It is not a room within a room. It is a local place with a purpose.

Watch the studio across the six phases of the afternoon.

In *orientation*, the building creates an attention-narrowing microvenue. The front display surfaces Tuesday's unresolved-issues list, the back walls dim, the table lighting brightens to draw the four bodies together, and the audio system slightly attenuates external corridor sound. The microvenue's purpose is to recover the shared frame, and its physical signature is convergence: the team's attention is pulled toward one location.

In *comparison*, the microvenue inverts. The three site-plan schemes are placed on three parallel writable walls, the table lighting drops, the wall surfaces brighten, and the team disperses to look at each scheme. The acoustic field changes too: the room becomes quieter, because comparison is largely silent. Yesterday's annotations are restored to the schemes; the building knows that the comparison phase is the first moment when those annotations become relevant again.

In *critique*, the microvenue contracts around the contested scheme. The courtyard option is brought to the central wall, the other two recede in brightness but remain visible, and the table-edge becomes writable. Camila's posture changes — she steps forward, marker in hand — and Devi pulls a chair closer. The acoustic field tightens; speech intelligibility within the team is maximised, even as ambient masking outside the group is increased. The microvenue's purpose is to support focused, sometimes uncomfortable disagreement.

In *generation*, the microvenue opens up. Ben pulls a fresh sheet of large paper to the table. The wall displays dim. The team's attention shifts from comparison to construction. The building brings up an AI-assisted *precedent panel* on a side display — visualisations of similar hybrid schemes from prior projects, retrievable but not insisted upon. The microvenue's purpose is to support exploratory externalisation, and the building's role in this register is sharply different from its role in the others. I shall return to this.

In *convergence*, the microvenue stages summary. The hybrid sketch is photographed and placed on the central wall alongside a list of open questions. The team's attention returns to the centre. The building's lighting becomes more uniform; the side displays show pending tasks. The microvenue's purpose is to make the next-step structure visible to all four participants.

In *resolution*, the microvenue prepares the handoff. Decisions are surfaced; the AI generates a short audio summary; consultants who will need to act on the decisions are identified and a draft message is offered. The microvenue's purpose is to make the afternoon's work transmissible.

Two features of this account deserve emphasis. First, none of these microvenues required dramatic architectural movement. Walls did not glide, ceilings did not lower, façades did not breathe. The physical envelope held still. What changed was the *coordinated configuration* of small variables: lighting balance, display content, surface assignment, acoustic field, and the visibility of past traces. Adaptive architecture has often been imagined as theatrical (Nguyen et al., 2022; Achten, 2019); much adaptive support, on this view, should be quieter and more reversible.

Second, the microvenues across the afternoon are not all of the same kind. The orientation, comparison, critique, convergence, and resolution microvenues are largely *predictive-processing scaffolds*: they shape attention, narrow uncertainty, supply external priors, and make the current phase legible. The generation microvenue is different. It is a *thinking-with-external-representations scaffold*. It does not narrow uncertainty so much as create a surface on which new structure can be brought into existence. This distinction is the theoretical pivot of the paper, and the next two sections develop it.

## 7. Architectural jigs as predictive scaffolds

In skilled work, a *jig* is a structure that makes an action easier, more repeatable, more accurate, or less cognitively demanding. A carpenter cutting several boards to the same length does not measure each board anew. She sets a stop and pushes each board to it. The stop is a simple external constraint that embodies a decision and reduces future work (Kirsh, 1995, ~1,400 citations). The same logic appears throughout skilled practice: vices hold material, templates guide cutting, marked surfaces support alignment, and workshop layout keeps the needed tools within reach.

Buildings can supply similar jigs. The studio's *comparison wall* — three side-by-side scheme displays with yesterday's annotations restored — is an architectural jig. So is the lighting balance that brightens the wall surfaces and dims the table during comparison. So is the acoustic field that supports silent reading during comparison and audible disagreement during critique. So is the seating geometry that triangulates Anna, Camila, and Ben during critique while keeping Devi within easy turn-taking distance.

In predictive-processing terms, these jigs are *externalised priors* and *precision-shaping devices*. The comparison wall makes a particular interpretation of the current activity — "we are now comparing schemes, side by side, against the same brief constraints" — more probable than alternative interpretations. The dimming of the table relative to the walls *narrows precision* on the wall content and *broadens it* on the inter-personal channel; participants attend to the schemes rather than to the table edge. The acoustic attenuation outside the team raises the *signal-to-noise ratio* for the in-team channel and lowers it for the out-of-room channel. Each adjustment shifts the precision landscape under which inference proceeds, which is exactly what good predictive scaffolding does (Feldman & Friston, 2010; Clark, 2013; Clark, 2016).

The jig is not the same as a script. A good jig does not tell the carpenter where to put the stop; it lets her put the stop where it serves her current cut. Good architectural jigs are similarly *open-textured*. The comparison wall offers three displays, but it does not insist on a particular comparison order or a particular reading sequence. The team can use it laterally, or pair two schemes against one, or use one wall as a parking lot for rejected detail. The jig increases the *agency* of the participants by removing low-value cognitive work; it does not increase the building's authority.

When a jig fails, it usually fails by over-scripting. A comparison wall that automatically organises the schemes in a fixed order, or that hides their annotations to keep the visual clean, has stopped being a jig and started being a script. The participants will work around it — by ignoring the building's preferred order, by re-summoning the annotations, by reorganising the schemes themselves — and the override is informative: the building learned what the team needed, but only in retrospect. This is the *return path*, and I shall come back to it.

For the architectural reader, the empirical evidence base for predictive scaffolding is uneven. The sensory and motor literatures are mature: top-down predictions modulate visual perception (Rao & Ballard, 1999, ~7,000), proprioceptive prediction error explains motor control (Adams, Shipp, & Friston, 2013, ~1,600), and architectural affordances modulate sensorimotor brain dynamics during transition (Djebbara, Fich, Petrini, & Gramann, 2019, ~200). The attentional and navigational literatures are also strong (Feldman & Friston, 2010; Stachenfeld et al., 2017). What is *not yet* well-evidenced is the closed-loop architectural case: a building that supplies precision-shaping jigs, observes the participants' response, and learns from it. The empirical case for this paper's design recommendations is therefore strongest in the constituent literatures and weakest in their architectural integration. I shall not pretend otherwise.

## 8. Microvenues for thinking — the second register

Now consider the generation phase. Ben pulls a fresh sheet of large paper to the table, takes the marker, and begins to sketch a hybrid scheme. He does not have the hybrid in his head before he starts. The first line is a guess; the second is an adjustment in response to the first; by the time he has six lines on the paper, he can see whether the hybrid resolves Camila's accessibility concern, and he can see this because he is now *looking at* something he did not have before. Camila reaches over and adds a perpendicular line where she thinks the accessible entry must run; Devi marks an X where a community room must remain; Anna sketches a floor-plate boundary that responds to all of this. By the time the sketch is half-formed, the four of them are thinking together by means of the sketch in a way none of them could think alone.

This is not the active-inference loop, and the philosophical distinction matters. It connects directly to the public–individual analysis of §4: what we are watching is the *externalisation traffic* between four individual activity spaces and one emerging public structure. Each participant has, in their individual activity space, partial intuitions about the courtyard, the entry, the community room, the floor plate. None has the integrated hybrid before Ben begins. The sketch is the medium by which the four individual cognitive contributions become a single public structure that all four can then operate on. The cognitive work is not located in any one head; it is distributed across the four heads, the four hands, the marker, and the paper. What active inference does not capture cleanly is the *generativity* of this process — the way the externalisation produces structure that none of the four had before, and the way that produced structure then enables further individual contributions which are themselves externalised.

What the sketch offers, and what the active-inference framework does not capture cleanly, are at least the following.

The sketch enables *re-representation*. Anna can stop, look at the configuration on the paper, and ask whether the hybrid is best understood as a courtyard-with-a-frontage or as a frontage-with-a-courtyard. The two re-representations afford different next moves. Neither is a more accurate inference about a fixed external fact; they are two ways of organising the same structure, each of which makes different operations natural. The choice between them is not driven by error reduction; it is driven by the anticipated utility of the operations the representation affords for the work that remains to be done (Sloman, 1985; Kirsh, 2010, ~600 citations).

The sketch is *persistent and re-identifiable*. Camila's perpendicular line will still be there in ten minutes when she returns to it after a digression. Devi's X will be there next Tuesday, when the team reopens the question. A mental image of the perpendicular line, by contrast, would degrade as Camila attended to other things, and there would be no objective test of whether the mental image she has now is the one she had ten minutes ago. The brute fact of physical persistence changes the reliability, the shareability, and the temporal dynamics of thinking (Kirsh, 2010; Hutchins, 1995).

The sketch is *operable* by tools and procedures the mind does not have. Anna can measure distances on it with a ruler. Ben can photograph it, then apply a tracing layer in software, then bring back the resulting overlay tomorrow. The sketch can be *rearranged* — cut up, re-pinned, recombined with other sketches. None of this is available to a purely mental representation. The activity space of the four participants now extends across the sketch as well as their bodies; their cognition is partly *constituted* by the marks on the paper (Clark & Chalmers, 1998; Hutchins, 1995).

The sketch is *jointly constructed*. Common ground here is not a convergence of separate posteriors over a pre-existing fact; it is a structure that the four of them produced together and that all four can refer to with reliable identity conditions (Goodwin, 1994, ~6,000). When Camila says "this corner needs to be smaller," all four know which corner. The reference is anchored in the externalisation. Without it, the same phrase would have meant four different corners.

The sketch is *generative*. As the lines accumulate, they suggest other lines. The triangle that emerges between the entry, the community room, and the perimeter wall *primes* visual associations that none of the participants had brought to the conversation. The sketch becomes a partner in thought, in the sense that operating on it produces possibilities that operating on the mental representation alone would not have produced (Kirsh, 2010; Goldschmidt, 1991, ~1,200).

A defender of predictive processing will say that all of this can be cast as policy selection under expected free energy: each of these actions is taken because of its anticipated long-run effect on the agent's model. The move is technically defensible and explanatorily empty. It generalises the formalism to the point where it predicts everything and explains nothing specific; the distinction between glare-avoidance and exploratory sketching is lost. Andy Clark himself, in *Surfing Uncertainty* (Clark, 2016, ~3,000), notes that the framework's predictive power is in danger of becoming Procrustean when stretched to cover all of cognition. The more honest theoretical position is that predictive processing is a powerful and partial account of cognition, that it captures some of what people do with external representations (specifically the epistemic-action subset that Kirsh and Maglio (1994) identified, including Tetris rotation, map-orientation, and other uses of action to disambiguate a fixed hidden state), and that it does not capture the *re-representational, exploratory, and constructive* uses of external representation that designers, mathematicians, choreographers, writers, and ordinary thinkers depend on. Those latter uses require a different vocabulary, and they require architectural support of a different kind.

The studio's generation microvenue is a *microvenue for thinking* in the sense that I am proposing. It must support externalisation (a large surface within Ben's reach), persistence (the surface must not be wiped between sessions), re-identification (yesterday's lines must remain available with their identity intact), rearrangement (the team must be able to cut, photograph, overlay, move), shareability (all four must be able to see and to point), and — crucially — *protection of in-progress structure* against premature smoothing. The last requirement deserves emphasis. The AI assistance that the building offers during generation must *not* clean up the sketch, must *not* auto-complete it, must *not* extract a "tidy" version that summarises what is going on. The roughness, the half-erased false starts, the contested marks, the ambiguities — these are not defects of the externalisation. They are part of how it works. A microvenue for thinking that smooths its content over-adapts in exactly the way that an over-eager AI summary destroys the cognitive value of a working whiteboard.

## 9. The two registers compared

The afternoon in the studio has displayed both registers of human–building cognition. The orientation, comparison, critique, convergence, and resolution microvenues are predictive-processing scaffolds: they shape attention, narrow uncertainty, supply priors, and make phase structure legible. The generation microvenue, and the persistent traces it leaves behind, are thinking-with-external-representations scaffolds: they support externalisation, persistence, re-identifiability, rearrangement, and the protection of in-progress thought.

The two registers are not in competition. The same room hosts both. The same group of four participants moves between them across the afternoon. The same AI infrastructure must serve both. But they have different design requirements, different metrics of success, and different dangers of over-adaptation, and conflating them produces bad architecture.

In the *predictive register*, the building is shaping precision and supplying priors. Its operations narrow what is to be attended to, what is to be expected, and what is to be done next. Its metrics of success are *override rates* (low is good — the team did not push back against the configuration), *convergence latency* (short is good — the team settled into the current phase quickly), *attention allocation* (focused is good), and *transition smoothness* (low cost between phases). Its dangers of over-adaptation are *scripting* (the building decides what should happen and the team's improvisation is suppressed) and *infantilisation* (the team's agency atrophies because the building has done too much).

In the *thinking register*, the building is supplying surfaces and media for externalisation, supporting persistence, enabling re-identification, allowing rearrangement, and protecting in-progress structure. Its operations *broaden* what is operable on; they do not narrow attention but expand the manipulable field. Its metrics of success are *return-to-artefact* rates, *build-on* events, *re-identification* reliability, *comparison* events, and *consolidation* into output. Its dangers of over-adaptation are *premature smoothing*, *over-summarisation*, and *erasure of ambiguity*.

The architectural significance of this distinction is that AI-supported microvenues must be of different kinds, deployed at different moments, and held to different standards. The orientation microvenue should be intelligent about narrowing the team's attention to the recovered frame; it should not preserve every loose end. The generation microvenue should be intelligent about preserving every loose end; it should not narrow attention to a preferred direction. The comparison microvenue lives between the two: it is largely predictive (it shapes which three schemes are visible and how they are arranged) but it depends on the persistence of yesterday's annotations (which is a thinking-register requirement). A building that confused the two would, for example, auto-summarise the generation phase into a clean version (catastrophic) or scatter the comparison-phase displays into a working-sketch arrangement (less catastrophic but still wrong).

The two registers also place different demands on the *return path*.

## 10. The building as socio-ecological interface and the return path

In ordinary human–computer interaction the interface stands between a user and a system. In architecture the interface is the niche in which people act, and the people are partly constitutive of it (Kirsh, 2019). When Camila steps toward the courtyard scheme during critique, the room's configuration around her is not merely external to the critique; it is part of what the critique is. When the building raises a partition between the team and an adjacent open-plan area, the partition does not just reduce sound transmission; it changes the social meaning of the encounter. The conversation feels more confidential, perhaps more formal; the team's voices drop; the rhythm of turn-taking changes. The building has acted *inside* the social situation, not on a detached user.

This is why every architectural intervention must be treated as a *hypothesis* and not as a control output. The building's models of the activity space are by hypothesis incomplete; its interventions are educated guesses; the only way to know whether an intervention helped is to observe what the participants do next. The *return path* — sense, infer, intervene, observe response, revise the model — is therefore not optional. It is constitutive of activity-aware architecture.

The return-path evidence is different in the two registers. In the predictive register, the most informative signals are overrides and confirmations. Did the team allow the partition to remain raised, or did Anna lower it? Did they accept the lighting balance, or did Devi reach for the controls? Did the dimming of the courtyard scheme during convergence stick, or did Camila insist on bringing it back? Override is not failure; it is the highest-quality signal the building gets about the gap between its model and the activity. In active-inference terms, it is precision-weighted prediction error of the kind that should drive belief update (Friston, 2010; Friston et al., 2017).

In the thinking register, the most informative signals are different. They are *use-over-time* signals — whether the team came back to the sketch, whether they built on it, whether they re-photographed it, whether they re-pinned it, whether they referred to it in a later session, whether it survived into a deliverable. These signals unfold on longer timescales than the predictive register's overrides. A sketch that was useful for generation may not be touched again for three days, then be returned to with a new modification. The building must be patient with externalised structure in a way that is not required of, say, lighting balance.

This means the building's learning has two clocks. The predictive-register clock is fast — seconds to minutes — and its lessons are about precision and prior. The thinking-register clock is slow — days to weeks — and its lessons are about which externalisations survive, which fade, and which become anchors for subsequent thought. An activity-aware building must operate on both clocks at once.

There is also a category of return-path evidence that crosses both registers and is particularly subtle. The participants' *appropriation* of the room — turning a chair sideways, repurposing a side display, using a table edge as a hand-rest, blocking a partition that wanted to close, leaving a sketch up overnight when the building expected an end-of-session archive — is a continuous form of teaching. It is what the participants do when the building's offered configuration is not quite what they need but is close enough to work around. The temptation is to read appropriation as noise. It is not. It is what the participants know about the activity that the building does not. A building that learns from appropriation is doing the most important kind of return-path learning available to it (Kirsh, 1996).

## 11. Strong evidence and cautious extrapolation

The empirical case for activity-aware architecture has uneven strength across its constituent claims.

*Strongly supported.* Ventilation and indoor air quality affect cognitive performance and decision-making, often substantially (Allen et al., 2016; Satish et al., 2012). Noise and speech intelligibility are major determinants of office distraction (Hongisto, 2005; Jones & Macken, 1993). Personal control over environmental conditions tends to improve satisfaction and perceived comfort even when objective conditions are similar (de Dear & Brager, 1998). Daylight and view exposure are associated with restoration and stress recovery (Ulrich, 1984; Kaplan, 1995).

*Plausibly supported but more contested.* Lighting affects circadian physiology and alertness under some conditions (Brainard et al., 2001; Cajochen, Zeitzer, Czeisler, & Dijk, 2000). Ceiling height may influence processing style (Meyers-Levy & Zhu, 2007). Biophilic elements may support restoration, but effects depend on context, dose, task, individual preference, and need (Gonçalves, Sousa, & Fernandes, 2023; Ríos-Rodríguez, Testa Moreno, & Moreno-Jiménez, 2023).

*Theoretically motivated but empirically thin.* Architectural affordances modulate sensorimotor brain dynamics during transition (Djebbara et al., 2019; Djebbara, Fich, & Gramann, 2021). External representations enhance cognitive performance across many tasks (Kirsh, 2010). The integration of these constituent literatures into closed-loop, return-path-sensitive architectural systems is not yet supported by published trial data, and any responsible deployment of activity-aware architecture should begin with the strong-evidence channels and treat the weaker channels as hypotheses for the system to test.

This unevenness has a design implication. Activity-aware buildings should avoid theatrical certainty. They should not say, "you are tired, so I will restore you." They should operate with *graded confidence*: "this meeting has been intense; would a quieter setup help?" Intelligent humility is a design virtue.

## 12. Prediction and the danger of closing the state space

AI makes activity-aware architecture possible because it can integrate many streams of weak evidence: calendars, room bookings, occupancy patterns, surface usage, transcript content, prior overrides, and environmental measurements. It can infer that the studio has entered comparison, that the team is about to enter critique, that the sketch on the table is becoming a hybrid scheme, that a particular pause in conversation indicates a contested issue rather than a natural break.

But prediction carries a danger. People *appropriate* space. They turn chairs to reduce confrontation. They leave doors open. They use books as supports. They tape notes to walls. They walk to the window not because the building offered a recovery niche but because they wanted to think. This opportunism is not noise. It is part of human intelligence and a major source of how environments come to fit their users (Brand, 1994; Kirsh, 1996).

If a building predicts too strongly, it will *close the state space*. It will script behaviour by removing configurations of the room that would have supported behaviours the system did not anticipate. A studio that has resolved every visible surface to the building's best guess of what is currently needed has left no slack for an unexpected hybrid sketch on a wall that the building had assigned to comparison archiving. A clinic room that has perfectly optimised the chair geometry for the inferred consultation pattern has left no slack for a patient who needs to sit differently for reasons the building cannot infer.

The principle that follows is the preservation of *appropriable slack*. An activity-aware building should always leave more configuration space than its model insists on. Microvenues should be light, reversible, and visibly editable. Architectural jigs should be open-textured. When the system is unsure, it should *offer* rather than *impose*; when the system is confident, it should still leave room for the participant to be more confident in the other direction.

This is one reason override is not a failure. Override is data, and it is also a right. When a participant rejects a lighting change, blocks a partition, clears a display, turns a chair, or disables an AI suggestion, the building should learn without resentment. The occupant is a co-designer of the microvenue.

## 13. Privacy and the first-person gap

The more powerful an adaptive building becomes, the more it risks becoming intrusive. The privacy problem belongs in the theory, not appended as a regulatory afterthought. The public–individual distinction of §4 provides the governing framework: the building's proper object is the public activity space; the individual activity spaces are not in scope.

The operational principle is *infer the least private state sufficient to support the activity*. The studio building does not need to know that Camila is frustrated; it needs to know that critique is happening. It does not need to know that Devi disagrees with Anna's interpretation of the community-meeting transcript; it needs to know that Devi has raised an objection that the comparison phase did not resolve. It does not need a persistent psychological profile of Ben; it needs a temporary model of what surfaces he is now operating on. Activity-level inference is almost always sufficient; inner-state inference is almost never necessary.

This principle has practical consequences. Prefer activity-level inference to inner-state inference. Prefer local and temporary models to persistent identity models. Prefer explicit requests to covert inference when the stakes are personal. Prefer group-level environmental adaptation when individual profiling is unnecessary. Treat physiological data as exceptional, opt-in, and purpose-limited.

There is a deeper epistemic limit that even principled privacy does not address. The building can observe behaviour, but it does not have first-person access. It may infer that Camila often turns toward the courtyard window after long meetings, but it does not know what the break feels like. It may detect that Anna pauses before deciding, but it does not feel the weight of the decision, the network of considerations she is balancing, or her sense that the team will follow her judgement. Skilled action and considered judgement are body-specific, history-specific, and context-specific (Kirsh, forthcoming; Polanyi, 1966, ~26,000). An AI can model external correlates of expertise; it does not thereby possess the expert's lived competence.

The right conclusion is not that AI is useless in architecture. It is that architectural AI should be *modest*. It should support the conditions of action rather than claim ownership of experience. It should help stage the workshop without pretending to be the artisan. The studio's role in supporting Anna, Ben, Camila, and Devi is precisely the role of a skilled and discreet studio assistant: prepare the room for the work that is coming, shield it from the noise that would interrupt, remember what was left undone, present what is needed when it is needed, and otherwise withdraw.

## 14. Design principles, instantiated

Several principles follow.

*Design for activity, not occupancy.* Presence is not the relevant variable. The same four people in the same studio may be in orientation, comparison, critique, generation, convergence, or resolution.

*Create microvenues, not settings.* The studio is reconfigured across six microvenues that share the physical envelope but differ in lighting, surfaces, attention shape, and what is surfaced.

*Distinguish predictive microvenues from thinking microvenues.* The orientation and convergence microvenues narrow attention. The generation microvenue supplies surfaces and persistence and must not narrow attention or smooth roughness. The comparison microvenue is hybrid.

*Use architectural jigs.* The comparison wall, the table-edge writability, the lighting balance, and the acoustic field are jigs that reduce cognitive friction without scripting behaviour.

*Preserve appropriable slack.* The studio leaves more configuration possibilities than its model insists on. Anna can ignore a suggestion. Ben can use a side display for an unanticipated comparison. Camila can leave a sketch up overnight.

*Close the loop.* Every intervention is a hypothesis. The building observes whether the partition was lowered, whether the sketch was returned to next Tuesday, whether the team came back to a precedent the AI surfaced. The return-path evidence runs on both fast and slow clocks.

*Be legible.* Anna and her team should understand, at least roughly, what the building is doing and why.

*Target the public activity space.* The building infers the public activity space; it does not attempt to model the individual activity spaces of its occupants.

*Infer the least private state.* The building knows that critique is happening. It does not infer that Camila is frustrated.

*Respect the first-person gap.* The building can model patterns of action; it cannot know what experience is like from the inside.

*Protect in-progress externalisation.* The hybrid sketch on the table is not summary material. The AI must not auto-clean, auto-organise, or auto-summarise it before the team has finished using it.

*Run two clocks.* Predictive scaffolding is updated on the timescale of seconds and minutes. Thinking-register scaffolding is evaluated on the timescale of days and weeks.

## 15. Conclusion

AI is changing work because it is changing the organisation of cognitive effort. It is changing what is drafted, searched, summarised, delegated, checked, remembered, and coordinated. It would be strange to suppose that this transformation will remain confined to the laptop. Human activity is spatial, embodied, social, and materially scaffolded. As AI becomes more capable of understanding activity, it will migrate into the physical environments where activity occurs.

The question is what kind of migration this should be. One path leads to overconfident automation: buildings that infer too much, decide too much, optimise crude proxies, and close down human improvisation. The better path is activity-aware architecture: buildings that infer just enough about the *public* activity space to be useful, that respect the *individual* activity spaces they cannot see, that create temporary microvenues for both predictive scaffolding and externalised thinking, that supply architectural jigs that reduce unnecessary cognitive work without scripting behaviour, that preserve shared memory and in-progress structure, that regulate interruption and support recovery, and that remain humble about what they know.

The building of the future should not be a boss, a therapist, or an invisible manipulator. It should be closer to a skilled studio assistant. It prepares, stages, shields, remembers, clears, offers, withdraws, and learns. It helps Anna and Ben and Camila and Devi create the local world in which they can do their work well — predictively, when prediction is what is needed, and constructively, when the work is to think something into existence that none of them yet knows.

---

# Appendix A: Variables in the latent activity state

This appendix unpacks the five components of the latent activity state $z_t = (x_t, c_t, \varphi_t, m_t, s_t)$ introduced in §5. Each variable is defined in terms of (a) its *semantic content*: what aspect of the public activity space it encodes; (b) its *observable signals*: the sensor and data streams from which the building infers its value; (c) its *inference method*: the computational machinery by which observation becomes posterior; and (d) an *example value* at a moment in the running studio example. The appendix is technical enough to be useful to a computer-science reader and is intended to be accessible to an architectural reader who is willing to skim the algorithmic detail.

## A.1 $x_t$ — Agent–environment configuration

*Semantic content.* The current physical configuration of the participants and their immediate surround: where each person is, their posture, gaze direction, which surfaces they can reach, which tools they have in hand, which artefacts they are currently attending to. The variable is structured: it can be unpacked as a set of per-participant sub-states plus a layout state for the room itself.

*Observable signals.* Camera-based skeletal pose estimation; occupancy and floor-pressure sensors; near-field gesture recognition from wrist-worn or surface-mounted sensors; surface-touch sensors on writable walls and tables; gaze tracking (where ethically permitted and opt-in); microphone-array spatial audio localisation; tool-presence detection (marker, mouse, keyboard, model parts).

*Inference method.* Multi-modal sensor fusion via state-space Kalman filtering or particle filtering for body pose and position; deep-learning models (pose-estimation networks such as OpenPose, gesture-classification networks) for higher-level interpretation; privacy-preserving variants that retain only abstract spatial pose without identifying features. The posterior is updated continuously at frame rate for fast-changing components (gaze, posture) and at sub-second rate for slower components (position, tool grasp).

*Example value.* At 14:08 in the studio: "Anna at central wall, facing the courtyard scheme, marker in right hand, gaze on top-left of scheme; Ben at table edge, seated, gaze on shared sketch, no tool in hand; Camila standing two metres back from central wall, hands in pockets, gaze on Anna; Devi seated at table opposite Ben, taking notes on tablet."

## A.2 $c_t$ — Social–pragmatic context

*Semantic content.* The project assignment, the role configuration, and the standing norms of the activity. Not what is happening right now, but the framing under which what is happening is interpretable. Where $x_t$ answers *who is where and doing what*, $c_t$ answers *what world we are in*.

*Observable signals.* Calendar integration (meeting type, attendee list, agenda, declared meeting purpose); project-management software (current project, active phase, deliverables, deadlines); organisational role data (who reports to whom, who has design authority, who is the public-health expert); prior session traces (what was decided last Tuesday, what was left open, what was assigned to whom).

*Inference method.* Symbolic structured retrieval from calendar / project-management systems, combined with role-and-norm priors learned from organisational data. Bayesian fusion with explicit user input for ambiguous cases (e.g., when the same room hosts a class at 14:00 and a research meeting at 15:00, the building asks rather than guesses which has begun). The context variable changes slowly — once per session or once per phase transition — and is therefore updated coarsely.

*Example value.* At the start of the afternoon: "Design review meeting; project: South San Diego Community Health Clinic Renovation; participants in roles {Anna: lead architect, Ben: junior designer, Camila: public-health consultant, Devi: community liaison}; norms: open critique permitted, decisions converge at end, sensitive content (community-meeting transcripts) is in-team only, AI assistance available but advisory."

## A.3 $\varphi_t$ — Activity phase

*Semantic content.* The current logical phase of the activity, drawn from the activity's phase repertoire. In the studio example: orientation, comparison, critique, generation, convergence, resolution. In other activities the phases differ; the building learns a phase repertoire per activity type. The variable is implicitly hierarchical: each phase has sub-phases, transitions, and expected durations.

*Observable signals.* Explicit phase labels in the agenda when provided; transcript content patterns (lexical and pragmatic markers of phase — comparison vocabulary differs from critique vocabulary differs from generation vocabulary); surface-content patterns (what is on the wall, how the displays are arranged); spatial reorganisation patterns (where the participants stand and how they move); audio-event patterns (silence during comparison, simultaneous speech during critique, sustained dyadic exchange during generation).

*Inference method.* The phase repertoire is learned offline by hierarchical-reinforcement-learning option discovery applied to historical activity traces (Bacon et al., 2017; Sutton et al., 1999). Online phase inference uses a hidden-Markov-model or recurrent variational state-space model trained on the discovered phases. Output is a posterior over phase identity, time-since-phase-onset, and expected next phase.

*Example value.* At 14:08: "Comparison phase, transitioned from orientation 12 minutes ago; predicted remaining duration in this phase ~5 minutes; predicted next phase: critique with probability 0.7, generation with probability 0.2, convergence with probability 0.1."

## A.4 $m_t$ — Microvenue configuration

*Semantic content.* The current configuration of the building's actuatable variables. This is the only component of $z_t$ that the building does not need to infer because it has *set* it. The microvenue configuration is the building's contribution to the activity space and the substrate on which it operates.

*Observable signals.* Direct actuator state: lighting balance per zone, display content per surface, partition position, acoustic field settings, surface-write enablement, AI-surfaced content per panel, privacy-boundary state.

*Inference method.* None — $m_t$ is a state variable the building maintains directly. The interesting computation around $m_t$ is the *policy* that selects the next $m_{t+1}$ given the current posterior over the other components of $z_t$.

*Example value.* At 14:08: "Lighting: warm spotlight 30% on table, cool flood 70% on walls; surfaces: writable on three walls and table-edge; displays: organisational-frontage scheme on wall 1, courtyard scheme on wall 2, hybrid scheme on wall 3, precedent panel suppressed; partitions: lateral partition lowered; acoustic field: in-team intelligibility maximum, external masking +6 dB; AI panel: open-issues list on side display."

## A.5 $s_t$ — Social–orientational state

*Semantic content.* Who attends to whom, who speaks, what is shared, what is hidden. The interpersonal dynamics of the moment. Where $x_t$ encodes physical configuration and $c_t$ encodes framing, $s_t$ encodes the *interaction-level* state: the social geometry of attention.

*Observable signals.* Gaze tracking (mutual gaze patterns, gaze direction over time); voice activity detection (who is speaking, who is taking the floor); turn-taking inference (gaps, overlaps, interruption patterns); posture analysis (lean-in, lean-back, body orientation toward or away from participants); proximity (interpersonal distance).

*Inference method.* Bayesian theory-of-mind models for inferring attentional state (Baker et al., 2009; Baker et al., 2017), combined with multi-modal social-signal processing. Outputs include attentional graphs (who is attending to whom and to what), speaker-listener configuration, and sharedness ratings for visible content (how recently and how thoroughly each artefact has been jointly attended to).

*Example value.* At 14:08: "Anna ↔ Camila in dyadic exchange (mutual gaze at 14:07:42, shared marker reach 14:08:11); Ben observing (gaze on shared sketch, no speech for 90 seconds); Devi independent (gaze on notes tablet, taking record, brief look-up every 15 seconds); sharedness rating: courtyard scheme high (all four have attended in last 60 seconds), hybrid scheme on wall 3 medium (Ben and Anna only), organisational-frontage scheme on wall 1 low (no recent shared attention)."

## A.6 Operations on $z_t$

The building maintains a posterior $q(z_t \mid o_{1:t})$ over the activity state via variational inference, with the structured factorisation
$$q(z_t) = q(x_t)\, q(c_t)\, q(\varphi_t \mid c_t)\, q(s_t \mid x_t)\, \delta(m_t = \hat{m}_t)$$
where $\hat{m}_t$ is the building's known actuator state. Three operations matter for the architectural argument.

*Posterior maintenance.* Update $q(z_t)$ as new observations arrive, weighing each observation by its precision (its expected informativeness, learned per signal channel). Component update rates vary from frame-rate ($x_t$, $s_t$) to session-rate ($c_t$). Updates are asynchronous across components.

*Policy evaluation.* For each candidate intervention $\pi$ in the building's repertoire — a partition adjustment, a lighting change, a display reassignment, an AI surfacing — compute the expected free energy $G(\pi)$, decomposable into epistemic and extrinsic components per the active-inference convention (Friston et al., 2017). The epistemic component captures expected information gain about $z_t$; the extrinsic component captures expected utility relative to preferences expressed by occupants or learned from override patterns. Choose policies that minimise $G$.

*Posterior update from return-path evidence.* When an intervention is enacted, observe the participants' response over the appropriate timescale. For predictive-register interventions (microvenue reconfiguration, jig deployment) the relevant timescale is seconds to minutes; for thinking-register interventions (preservation of externalised structure, AI surfacing of past traces) the relevant timescale is hours to weeks. Update the building's priors, precisions, and transition models accordingly, using two parallel learning streams running on the two clocks discussed in §10.

The reader interested in the technical depth should consult the variational state-space modelling literature (Hafner et al., 2020), the predictive-coding-and-active-inference literature (Friston, 2010; Friston et al., 2017), the Bayesian theory-of-mind literature (Baker et al., 2017), and the hierarchical-reinforcement-learning literature (Bacon et al., 2017; Sutton et al., 1999) for the formal machinery on which the activity-aware regime would be built. Nothing in the present paper depends on any one of these being implemented exactly as cited; what matters is that the formal commitment is structurally available.

---

# Proposed illustrations with captions

The following figures are constructed so that a reader who reads only the captions and looks only at the images can reconstruct the argument. Each caption is sized for an architectural-journal page.

## Figure 1 — The running example: Anna, Ben, Camila, and Devi across an afternoon

*Visual.* Wide-format four-panel image of the same studio at four moments — orientation, comparison, critique, generation. Each panel shows positions, postures, attention foci; annotations highlight what changes between panels (lighting balance, active displays, surfaces, partitions, writable walls, who is speaking, what the AI has surfaced).

*Caption.* The same room, four times in one afternoon. Anna leads the team; Ben is her junior designer; Camila is the public-health consultant; Devi is the community liaison. They are working on a community-health-clinic renovation. The studio's envelope is constant. What changes across the four panels — the lighting balance, the active displays, the surface assignments, the seating geometry, the acoustic field, the visible past traces — is the building's response to a moving activity space. In orientation (Panel A), the room narrows attention to a single recovered frame. In comparison (Panel B), three site-plan schemes appear in parallel on three writable walls. In critique (Panel C), the contested scheme is centred and the others recede. In generation (Panel D), the walls dim, a fresh paper sheet enters the table, and a precedent panel appears on a side display. The argument of this paper is that the four configurations are not lighting adjustments. They are five-minute architectural compositions in service of five-minute cognitive activities. The activity-aware building's job is to construct these configurations and to learn from them.

## Figure 2 — Activity space at three levels

*Visual.* Layered diagram with three stacked planes. Top plane *logical*: goal tree showing the design problem decomposed into site-plan choice, floor-plate commitment, clinical-layout commitment, with the current cursor at site-plan choice. Middle plane *physical*: studio plan view with the actual furniture, surfaces, and people. Bottom plane *cognitive*: four small subjective annotations showing what each participant is treating as salient — Anna's concern with timeline, Ben's mental gallery of hybrid precedents, Camila's accessibility constraints, Devi's recall of community meeting. Arrows between planes show cascading effects.

*Caption.* Activity space, as I use the term, is not the floor plan. It is the joint organisation of action at three levels. The logical level is the goal structure — what the team is trying to accomplish, what subgoals depend on what, what phase the activity is in. The physical level is the material substrate — the room, surfaces, furniture, bodies, tools at hand. The cognitive level is what each participant is treating as salient, remembering, externalising, ignoring. The three levels co-evolve. A change at the logical level (the team decides to commit today) reorganises the physical level (the three displays come into comparison) and shifts the cognitive level (Camila switches from open exploration to evaluative scrutiny). An activity-aware building must support the joint trajectory through all three levels, which means it cannot reduce the problem to physical-level variables like comfort, occupancy, or energy alone.

## Figure 3 — Public and individual activity space

*Visual.* A two-circle Venn-style diagram with overlap. Left circle: *individual activity spaces*, divided into four sub-bubbles for Anna, Ben, Camila, Devi, each containing their private contents (remembered cases, projections, judgements). Right circle: *public activity space*, containing the shared structures (sketches, walls, displays, gestures, marks, words). The overlap zone contains *externalisations* — items that have moved from individual to public, e.g., Camila's perpendicular line, Devi's X, Ben's hybrid sketch. Arrows in both directions show externalisation traffic. The building's "view" is drawn as a horizon line below the public circle, indicating that the building can see the public but not the individual.

*Caption.* Historically philosophers drew the mind–world boundary at the skin. The extended-mind tradition and active inference have variously challenged that boundary; the cognitive system at the moment of externalisation is the participant *plus* the marker *plus* the paper *plus* the other participants who attend. But within distributed cognition there is still a distinction worth drawing. The public activity space is the shared, observable, jointly constructed organisation of action — the sketches, marks, gestures, words, and configurations that all four participants can refer to with shared identity. The individual activity spaces are each participant's enactive bubble — what they are treating as salient, remembering, projecting, ignoring. The two are coupled through externalisation: when Camila adds a perpendicular line, content moves from her individual activity space into the public activity space, where it becomes available to the team and observable to the building. The building's proper object is the public activity space; the individual activity spaces are not in scope, and the privacy and first-person-gap principles follow from this restriction.

## Figure 4 — Activity space as a latent state space

*Visual.* A structured probabilistic graphical model. Variables: $z_t$ (activity state, decomposed as $x_t, c_t, \varphi_t, m_t, s_t$ — five sub-nodes), $o_t$ (observations, drawn as a sensor cluster: camera, microphone, calendar, surface-content, occupancy, gaze), $\pi$ (policy, drawn as the building's intervention repertoire). Arrows show transition $p(z_{t+1} | z_t, \pi)$, observation model $p(o_t | z_t)$, and policy-evaluation loop. Insets show what each of the five components encodes in the studio example (cross-referenced to Appendix A).

*Caption.* The building does not observe the activity directly; it observes only its sensory shadow. The public activity space, formalised, is a latent state space the building must infer from observations. The state $z_t$ has five structured components: the agent–environment configuration $x_t$, the social–pragmatic context $c_t$, the activity phase $\varphi_t$ (orientation, comparison, critique, generation, convergence, resolution), the microvenue configuration $m_t$, and the social–orientational state $s_t$. The appendix unpacks each variable, including what it encodes, what signals it is inferred from, and how. The same mathematical structure underlies predictive processing in neuroscience, world-model agents in deep reinforcement learning, and Bayesian theory of mind in cognitive psychology. The inferred latent state is the building's model of the public activity space; it is not the activity itself, and it is not the individual activity spaces of the participants (Figure 3).

## Figure 5 — Five microvenues, one room

*Visual.* Five small plan-view diagrams of the same studio, arranged in a row, one per phase. Each plan is annotated with lighting (warm spotlight, cool flood, dimmed), display content, surface assignment, partition position, and acoustic field.

*Caption.* The afternoon produces five distinct microvenues: orientation, comparison, critique, generation, and convergence (resolution, the sixth, is similar to convergence). Each lasts five to thirty minutes. None of them required moving a wall or lowering a ceiling. They are produced by coordinated reconfiguration of small variables — lighting balance, display content, surface assignment, partition position, acoustic field, and the visibility of past traces. The microvenue is the building's primary output in an activity-aware regime; it is the temporary place that supports a temporary phase of work. Microvenues are reversible, light, and socially legible. They should not be confused with the dramatic movement of much speculative responsive architecture. The five panels here show what activity-aware architecture actually looks like in practice: quiet, careful, phase-specific compositions of variables a contemporary smart building already controls.

## Figure 6 — The comparison wall as an architectural jig

*Visual.* Perspective view of the studio during comparison phase. Three site-plan schemes on three parallel writable walls, each with annotations preserved from yesterday's session as a translucent overlay. Lighting balance highlighted with light-arrows: table dimmed, walls brightened. Side annotations identify the jig elements: three-display geometry, annotation persistence, writable surface, acoustic field.

*Caption.* A jig, in skilled work, is a structure that reduces unnecessary cognitive or motor effort without taking the work away from the worker. A carpenter cuts boards to the same length not by re-measuring each but by setting a stop. The comparison wall is an architectural jig of the same kind. It places three site-plan schemes in parallel, restores yesterday's annotations, brightens the walls and dims the table, and makes the table-edge writable. Each is a precision-shaping move in predictive-processing terms: it raises the gain on scheme-by-scheme comparison and lowers it on irrelevant variation. The team does not have to remember which annotations went with which scheme; the building has done that. They do not have to negotiate lighting; the balance has been chosen for the phase. They do not have to re-establish that comparison is now happening; the wall configuration signals it. But the jig does not script. The team can compare in any order, write on any wall, ignore any annotation, or change the brightness. A good jig increases the team's agency by removing the work of setting up the configuration; it does not replace the team's judgement about what the comparison should reveal.

## Figure 7 — A microvenue for thinking

*Visual.* Photograph-style image of the studio during generation phase. Ben holds a marker over a large sheet of fresh paper on the table; lines, half-erased, three competing first marks. Camila reaches to add a perpendicular line. Devi marks an X. Anna begins a floor-plate boundary. On the side display, a precedent panel shows hybrid schemes from prior projects in a quiet, peripheral way. Lighting is even and warm. Yesterday's sketches remain visible on the back wall — not foregrounded but available. The AI assistant is silent.

*Caption.* This microvenue is of a different kind from the previous four. It is not narrowing attention or shaping precision. It is supplying surfaces, persistence, and re-identifiability for thinking that the four participants cannot do inside their heads alone. The hybrid scheme on the paper is not an observation Ben is generating to disambiguate a fixed hidden fact; it is a structure he is bringing into existence, against which subsequent moves can be checked. The sketch supports re-representation, persistence, re-identification, rearrangement, and joint construction. None of this is captured by the predictive-error-reduction framework. It requires a different design vocabulary: surfaces large enough to externalise on, persistence across sessions, re-identifiability of marks, and — crucially — protection against premature smoothing. An AI assistant in this microvenue must not auto-clean, auto-summarise, or auto-resolve the in-progress sketch. The roughness is part of how the externalisation works.

## Figure 8 — The two registers compared

*Visual.* Side-by-side panel. Left: *predictive-processing register*, five rows (what the building does, key affordances, metrics of success, dangers of over-adaptation, exemplar microvenues). Right: *thinking-with-external-representations register*, the same five rows with their distinct content.

*Caption.* The theoretical spine of this paper is that human cognition in buildings operates in two distinct registers and that activity-aware architecture must support both. The predictive-processing register — well described by Friston, Clark, and the active-inference literature — covers the perceptual-motor-attentional dynamics by which agents orient, anticipate, attend, and act. The building's contribution in this register is to shape precision, supply priors, narrow uncertainty, and make phase structure legible. The thinking-with-external-representations register — described by Kirsh, Hutchins, Larkin, Simon, and the distributed-cognition literature — covers the constructive use of surfaces, marks, and arrangements to externalise, persist, rearrange, and jointly construct in-progress thought. The two registers have different metrics of success, different dangers of over-adaptation, and different timescales of return-path evidence. Conflating them produces bad architecture: a building that auto-summarises a working whiteboard, or that scatters a comparison display into a working-sketch arrangement, has confused the registers.

## Figure 9 — The return path on two clocks

*Visual.* Two-track timeline. Upper track *fast* (seconds-to-minutes): building lowers a partition; Anna's posture changes within twenty seconds; voices drop; no override observed; prior updates. Lower track *slow* (days-to-weeks): generation-phase sketch from Thursday photographed Friday; reopened Tuesday at 14:20; modified Tuesday 14:35; referenced Wednesday meeting; consolidated into final scheme three weeks later. Arrows show how each timescale's evidence feeds back into the building's model.

*Caption.* Every architectural intervention is a hypothesis. The building's models are by hypothesis incomplete, so the only way to know whether an intervention helped is to observe what the participants do next — and the relevant timescale depends on which register the intervention belongs to. In the predictive register, evidence arrives in seconds to minutes: overrides, postural changes, voice attenuation, attention coherence. In the thinking register, evidence arrives over days to weeks: which externalised structures are returned to, which are built on, which are consolidated into deliverables. The two clocks must run in parallel. A building that learns only on the fast clock will treat thinking-register interventions as failures when they are not yet evaluable; a building that learns only on the slow clock will be deaf to immediate user feedback. Activity-aware architecture requires both.

## Figure 10 — The first-person gap

*Visual.* Two-pane image. Left pane: the building's posterior over the public activity state — a clean, structured Bayesian network with confidence regions on each component of $z_t$. Right pane: Camila's first-person experience of the same moment — a fog-of-thought visualisation containing remembered cases, family concerns, aesthetic projections, sense that Anna is rushing, relationship history with the team. An arrow connects the two panes; a clear epistemic wall separates them.

*Caption.* The building can observe behaviour; it cannot have first-person access. Its inferred posterior over the public activity state — visible in the left pane — is its best computational reconstruction of what is happening. But the same moment, from Camila's first-person perspective (right pane), contains contents the building has no access to: her remembered cases, her concerns, her aesthetic projections, her sense of timing, her relationship history with the team. Camila's individual activity space is partly constitutive of the team's activity but is not part of the building's $z_t$. The principled response to this gap is modesty: infer the least private state sufficient to support the activity; prefer activity-level inference to inner-state inference; prefer local and temporary models to persistent identity models. The building's role is to stage the workshop, not to claim ownership of the artisan's experience.

---

# References

[Identical reference list to the v1 file; preserved for completeness — abbreviated here for the diff. The full reference list from v1 carries over unchanged. Add: Constant, Clark, Kirchhoff & Friston 2022 (already in v1).]

Achten, H. H. (2019). Interaction narratives for responsive architecture. *Buildings*, 9(3), 66. https://doi.org/10.3390/buildings9030066 (Google Scholar: ~80)

Adams, R. A., Shipp, S., & Friston, K. J. (2013). Predictions not commands: Active inference in the motor system. *Brain Structure and Function*, 218(3), 611–643. https://doi.org/10.1007/s00429-012-0475-5 (Google Scholar: ~1,600)

Allen, J. G., MacNaughton, P., Satish, U., Santanam, S., Vallarino, J., & Spengler, J. D. (2016). Associations of cognitive function scores with carbon dioxide, ventilation, and volatile organic compound exposures in office workers. *Environmental Health Perspectives*, 124(6), 805–812. https://doi.org/10.1289/ehp.1510037 (Google Scholar: ~700)

Bacon, P.-L., Harb, J., & Precup, D. (2017). The option-critic architecture. *Proceedings of the AAAI Conference on Artificial Intelligence*, 31(1), 1726–1734. (Google Scholar: ~1,800)

Baker, C. L., Saxe, R., & Tenenbaum, J. B. (2009). Action understanding as inverse planning. *Cognition*, 113(3), 329–349. https://doi.org/10.1016/j.cognition.2009.07.005 (Google Scholar: ~700)

Baker, C. L., Jara-Ettinger, J., Saxe, R., & Tenenbaum, J. B. (2017). Rational quantitative attribution of beliefs, desires and percepts in human mentalizing. *Nature Human Behaviour*, 1, 0064. https://doi.org/10.1038/s41562-017-0064 (Google Scholar: ~600)

Brainard, G. C., Hanifin, J. P., Greeson, J. M., Byrne, B., Glickman, G., Gerner, E., & Rollag, M. D. (2001). Action spectrum for melatonin regulation in humans. *Journal of Neuroscience*, 21(16), 6405–6412. (Google Scholar: ~1,500)

Brand, S. (1994). *How buildings learn: What happens after they're built*. Viking.

Cajochen, C., Zeitzer, J. M., Czeisler, C. A., & Dijk, D. J. (2000). Dose-response relationship for light intensity and ocular and electroencephalographic correlates of human alertness. *Behavioural Brain Research*, 115(1), 75–83. (Google Scholar: ~700)

Clark, A. (2008). *Supersizing the mind: Embodiment, action, and cognitive extension*. Oxford University Press. (Google Scholar: ~3,000)

Clark, A. (2013). Whatever next? Predictive brains, situated agents, and the future of cognitive science. *Behavioral and Brain Sciences*, 36(3), 181–204. https://doi.org/10.1017/S0140525X12000477 (Google Scholar: ~3,800)

Clark, A. (2016). *Surfing uncertainty: Prediction, action, and the embodied mind*. Oxford University Press. (Google Scholar: ~3,000)

Clark, A., & Chalmers, D. (1998). The extended mind. *Analysis*, 58(1), 7–19. https://doi.org/10.1093/analys/58.1.7 (Google Scholar: ~7,500)

Constant, A., Clark, A., Kirchhoff, M., & Friston, K. J. (2022). Extended active inference: Constructing predictive cognition beyond skulls. *Mind & Language*, 37(3), 373–394. https://doi.org/10.1111/mila.12330 (Google Scholar: ~150)

de Dear, R. J., & Brager, G. S. (1998). Developing an adaptive model of thermal comfort and preference. *ASHRAE Transactions*, 104(1), 145–167. (Google Scholar: ~1,400)

Djebbara, Z., Fich, L. B., Petrini, L., & Gramann, K. (2019). Sensorimotor brain dynamics reflect architectural affordances. *Proceedings of the National Academy of Sciences*, 116(29), 14769–14778. https://doi.org/10.1073/pnas.1900648116 (Google Scholar: ~200)

Djebbara, Z., Fich, L. B., & Gramann, K. (2021). The brain dynamics of architectural affordances during transition. *Scientific Reports*, 11, 2796. https://doi.org/10.1038/s41598-021-82504-w

Feldman, H., & Friston, K. J. (2010). Attention, uncertainty, and free-energy. *Frontiers in Human Neuroscience*, 4, 215. https://doi.org/10.3389/fnhum.2010.00215 (Google Scholar: ~2,500)

Friston, K. J. (2010). The free-energy principle: A unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127–138. https://doi.org/10.1038/nrn2787 (Google Scholar: ~12,000)

Friston, K. J., FitzGerald, T., Rigoli, F., Schwartenbeck, P., & Pezzulo, G. (2017). Active inference: A process theory. *Neural Computation*, 29(1), 1–49. https://doi.org/10.1162/NECO_a_00912 (Google Scholar: ~3,200)

Gonçalves, G., Sousa, C., & Fernandes, M. J. (2023). Restorative effects of biophilic workplace and nature exposure during working time: A systematic review. *International Journal of Environmental Research and Public Health*, 20(21), 6986. (Google Scholar: ~80)

Goldschmidt, G. (1991). The dialectics of sketching. *Creativity Research Journal*, 4(2), 123–143. https://doi.org/10.1080/10400419109534381 (Google Scholar: ~1,200)

Goodwin, C. (1994). Professional vision. *American Anthropologist*, 96(3), 606–633. https://doi.org/10.1525/aa.1994.96.3.02a00100 (Google Scholar: ~6,000)

Hafner, D., Lillicrap, T., Norouzi, M., & Ba, J. (2020). Mastering Atari with discrete world models. *arXiv preprint arXiv:2010.02193*. (Google Scholar: ~1,200)

Hongisto, V. (2005). A model predicting the effect of speech of varying intelligibility on work performance. *Indoor Air*, 15(6), 458–468. https://doi.org/10.1111/j.1600-0668.2005.00391.x (Google Scholar: ~450)

Hutchins, E. (1995). *Cognition in the wild*. MIT Press. (Google Scholar: ~10,000)

Jones, D. M., & Macken, W. J. (1993). Irrelevant tones produce an irrelevant speech effect. *Journal of Experimental Psychology: Learning, Memory, and Cognition*, 19(2), 369–381. (Google Scholar: ~700)

Kaplan, S. (1995). The restorative benefits of nature: Toward an integrative framework. *Journal of Environmental Psychology*, 15(3), 169–182. (Google Scholar: ~6,000)

Kingma, D. P., & Welling, M. (2014). Auto-encoding variational Bayes. *Proceedings of the 2nd International Conference on Learning Representations*. (Google Scholar: ~50,000)

Kirsh, D. (1995). The intelligent use of space. *Artificial Intelligence*, 73(1–2), 31–68. https://doi.org/10.1016/0004-3702(94)00017-U (Google Scholar: ~1,400)

Kirsh, D. (1996). Adapting the environment instead of oneself. *Adaptive Behavior*, 4(3–4), 415–452. https://doi.org/10.1177/105971239600400307 (Google Scholar: ~600)

Kirsh, D. (2010). Thinking with external representations. *AI & Society*, 25(4), 441–454. https://doi.org/10.1007/s00146-010-0272-8 (Google Scholar: ~600)

Kirsh, D. (2019). Do architects and designers think about interactivity differently? *ACM Transactions on Computer-Human Interaction*, 26(2), Article 7. https://doi.org/10.1145/3301425 (Google Scholar: ~30)

Kirsh, D. (2025). Reimagining space: How activity space explains human behaviour in buildings. *Architectural Science Review*. https://doi.org/10.1080/00038628.2025.2542213

Kirsh, D. (forthcoming). *Deeply embodied: Why it's hard for museums and AI to capture what masters know*. In M. Ajmar (Ed.), *Craft and knowledge*. V&A Publishing.

Kirsh, D., & Maglio, P. (1994). On distinguishing epistemic from pragmatic action. *Cognitive Science*, 18(4), 513–549. https://doi.org/10.1207/s15516709cog1804_1 (Google Scholar: ~1,500)

Larkin, J. H., & Simon, H. A. (1987). Why a diagram is (sometimes) worth ten thousand words. *Cognitive Science*, 11(1), 65–100. https://doi.org/10.1111/j.1551-6708.1987.tb00863.x (Google Scholar: ~5,500)

Lee, J. H., Ostwald, M. J., & Kim, M. J. (2021). Characterizing smart environments as interactive and collective platforms: A review of the key behaviors of responsive architecture. *Sensors*, 21(10), 3417. https://doi.org/10.3390/s21103417

Meyers-Levy, J., & Zhu, R. (2007). The influence of ceiling height: The effect of priming on the type of processing that people use. *Journal of Consumer Research*, 34(2), 174–186. https://doi.org/10.1086/519146 (Google Scholar: ~800)

Nguyen, B. V. D., Han, J., & Vande Moere, A. (2022). Towards responsive architecture that mediates place. *Proceedings of the ACM on Human-Computer Interaction*, 6(CSCW2), 1–27. https://doi.org/10.1145/3555568 (Google Scholar: ~50)

Polanyi, M. (1966). *The tacit dimension*. Routledge & Kegan Paul. (Google Scholar: ~26,000)

Rao, R. P. N., & Ballard, D. H. (1999). Predictive coding in the visual cortex: A functional interpretation of some extra-classical receptive-field effects. *Nature Neuroscience*, 2(1), 79–87. https://doi.org/10.1038/4580 (Google Scholar: ~7,000)

Ríos-Rodríguez, M. L., Testa Moreno, M., & Moreno-Jiménez, P. (2023). Nature in the office: A systematic review of nature elements and their effects on worker stress response. *Healthcare*, 11(21), 2838. (Google Scholar: ~40)

Satish, U., Mendell, M. J., Shekhar, K., Hotchi, T., Sullivan, D., Streufert, S., & Fisk, W. J. (2012). Is CO2 an indoor pollutant? Direct effects of low-to-moderate CO2 concentrations on human decision-making performance. *Environmental Health Perspectives*, 120(12), 1671–1677. https://doi.org/10.1289/ehp.1104789 (Google Scholar: ~400)

Sloman, A. (1985). Why we need many knowledge representation formalisms. In M. Bramer (Ed.), *Research and development in expert systems* (pp. 163–183). Cambridge University Press. (Google Scholar: ~400)

Stachenfeld, K. L., Botvinick, M. M., & Gershman, S. J. (2017). The hippocampus as a predictive map. *Nature Neuroscience*, 20(11), 1643–1653. https://doi.org/10.1038/nn.4650 (Google Scholar: ~1,400)

Sutton, R. S., Precup, D., & Singh, S. (1999). Between MDPs and semi-MDPs: A framework for temporal abstraction in reinforcement learning. *Artificial Intelligence*, 112(1–2), 181–211. https://doi.org/10.1016/S0004-3702(99)00052-1 (Google Scholar: ~5,500)

Tabadkani, A., Roetzel, A., & Li, H. (2021). A review of occupant-centric control strategies for adaptive facades. *Automation in Construction*, 122, 103464. https://doi.org/10.1016/j.autcon.2020.103464 (Google Scholar: ~150)

Ulrich, R. S. (1984). View through a window may influence recovery from surgery. *Science*, 224(4647), 420–421. https://doi.org/10.1126/science.6143402 (Google Scholar: ~3,500)

Zhang, J., & Norman, D. A. (1994). Representations in distributed cognitive tasks. *Cognitive Science*, 18(1), 87–122. https://doi.org/10.1207/s15516709cog1801_3 (Google Scholar: ~1,500)
