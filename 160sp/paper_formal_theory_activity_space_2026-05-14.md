# A Formal Theory of Activity Space: Filling a Gap in the Cognitive Science of Environments

**David Kirsh**
Department of Cognitive Science, UC San Diego

---

## Abstract

Cognitive science has mature theories of perception, action, attention, memory, and learning. It has Gibsonian theories of affordance. It has theories of distributed and extended cognition. What it does not have is a theory of the structured environment that *supports* cognitive activity — a theory of how the spatial, temporal, social, and material organisation of a setting is itself part of the cognitive system. This paper proposes such a theory. The central construct is the *activity space*: the temporally structured, socially situated, cognitively interpreted arena in which human activity unfolds. Activity space has both a public dimension, jointly constructed by participants and in principle observable, and an individual dimension, each agent's enactive bubble. The two are coupled through externalisation. I argue that the public activity space can be formalised as the latent state space of a partially observable generative model, $z_t = (x_t, c_t, \varphi_t, m_t, s_t)$, where each component captures a distinct aspect of the structure — agent–environment configuration, social-pragmatic context, activity phase, microvenue configuration, and social-orientational state. Each component admits computational treatment, can be inferred from sensor and contextual data, and supports policy evaluation by expected free energy or analogous formalisms. The framework integrates predictive processing, active inference, world-model agents, hierarchical reinforcement learning, and Bayesian theory of mind. It also identifies an explicit limit: a class of cognitive activity — thinking with external representations — that the predictive-processing component of the framework captures only by Procrustean stretching, and that requires complementary theoretical vocabulary. The framework is general; the most demanding application is the built environment, where activity is persistent, designed, multi-actor, and multi-scale. A companion paper applies the framework to adaptive architecture.

---

## 1. The gap: cognitive science lacks a theory of the structured environment

Cognitive science has spent a century on the agent. We have theories of how perception extracts information from sensory input, how action is planned and controlled, how attention selects, how memory stores and retrieves, how learning revises beliefs and skills. We have theories of how cognition is distributed across people and tools (Hutchins, 1995, ~10,000 citations), of how it extends beyond the skin (Clark & Chalmers, 1998, ~7,500), of how it minimises prediction error in active inference loops (Friston, 2010, ~12,000). These are mature lines of work.

What we do not have, with comparable maturity, is a *theory of the environment* — a theory of how the structured world that supports cognitive activity is itself organised. We have Gibson's theory of affordances (Gibson, 1979, ~30,000), which tells us that environments offer possibilities for action that perception detects directly. We have theories of the *niche* in evolutionary and developmental contexts (Laland, Odling-Smee, & Feldman, 2000). We have computational theories of *task space* in action-control research (Xiong & Proctor, 2018). But none of these gives us a sufficiently rich account of how the spatial, temporal, social, and material organisation of a particular setting structures the cognitive activity that takes place within it. Affordance theory is about possibilities for action; it is not about the temporal and phase organisation of activity. Niche-construction theory is about the long-run feedback between organism and environment; it is not about the moment-to-moment structure of an unfolding activity. Task-space theory is about action selection under task constraints; it does not extend cleanly to the social and material context.

The built environment is the limit case, and the case I shall use to drive the argument. Buildings are *designed* environments. They are *persistent*: a kitchen will be a kitchen tomorrow. They are *multi-actor*: a clinic room hosts patient, clinician, family member, and equipment, with overlapping and conflicting needs. They are *multi-scale*: a corridor is part of a wing is part of a building is part of a campus. And they are *adaptive in principle*: contemporary smart buildings already control lighting, ventilation, acoustic conditions, partitioning, and display content. The cognitive-science treatment of buildings has not kept pace with what buildings are now capable of doing. Architects need a vocabulary for what their adaptive systems should be doing; cognitive scientists need a vocabulary for what the structured environment is.

This paper proposes one. The central construct is the *activity space*: the temporally structured, socially situated, cognitively interpreted arena in which human activity unfolds. The activity space is what affordance theory points toward but does not develop; it is what distributed cognition operates within but does not characterise; it is what predictive processing assumes but does not formalise as an object of inquiry. The paper develops the construct theoretically, formalises it as the latent state space of a partially observable generative model, identifies its principal computational treatments, and notes the limit at which the formalism must be complemented by other vocabularies. The companion paper (Kirsh, in preparation, *Activity-aware architecture*) applies the framework to adaptive buildings.

## 2. Activity space defined

By *activity space* I mean what the world looks like, and how it is structured, *under the description of the ongoing activity* (Kirsh, 2025). It is not the floor plan. It is not the schedule. It is not the list of agents present. It is the layered organisation of action — the goals, the phases, the affordances, the attentional foreground, the shared references, the social positioning — that the participants are constructing as they work. The activity space changes continuously as the activity unfolds; the room may stay the same but the activity space does not.

Activity space has three levels of structure (Kirsh, 1995, 2025). The *logical* level is the goal structure of the activity: what counts as success, what phases the activity passes through, what subgoals depend on which, what counts as an appropriate action now. The *physical* level is the material substrate: layout, surfaces, seating, displays, lighting, sightlines, sound field, tools at hand, bodies of the participants. The *cognitive* level is what each participant is treating as salient, remembering, externalising, or ignoring as they work. The three levels are not separable; they co-evolve. A change at the logical level reorganises the physical level and shifts the cognitive level. A change in the physical substrate can shift the cognitive level. The activity space is the joint trajectory of all three.

Activity space is closely related to several existing constructs but is not identical to any of them. *Task space* in action-control research (Xiong & Proctor, 2018) captures the action repertoire and constraint structure of a single agent on a defined task; activity space generalises to multi-actor, phase-structured, socially situated activity. *Peripersonal space* in neuroscience (Brozzoli, Cardinali, Pavani, & Farnè, 2010; Bufacchi & Iannetti, 2018) is the action-relevant nearby space of a single body; activity space extends to surfaces, displays, partitions, and social configurations beyond peripersonal reach. *The niche* in niche-construction theory (Odling-Smee, Laland, & Feldman, 2003) is the long-run constructed environment of an organism or species; activity space is the moment-to-moment organisation of a single activity. *The situation* in situated-cognition theory (Robbins & Aydede, 2009) is the broadest construct and the most overlapping with activity space; the difference is that activity space is specifically *temporally structured* (phases, transitions) and *cognitively interpreted* (the same physical situation is different activity spaces for participants in different roles or phases).

The activity-space construct is needed because none of these adjacent constructs gives a sufficiently rich account of the *unfolding organisation of joint cognitive work in structured environments*. That is the gap.

## 3. Public and individual activity space

The cognitive level of activity space contains content that the building or another observer cannot directly observe and content that is not equally shared by the participants. This forces a distinction the activity-space literature has not always made explicit.

In one sense, activity space is a *public* object. It is the organisation of action that the participants jointly construct, that has shared reference points, and that an external observer (a building, another agent, an analyst) can in principle reach. The sketches, the displays, the seating geometry, the audible discussion, the visible gestures, the marks on the paper — these are part of activity space in the public sense. They have identity conditions that survive reidentification across time and across observers.

In another sense, activity space is *individual*. Each participant has their own enactive bubble (Kirsh, 2025) — what they are treating as salient, remembering, projecting onto the scene, inferring, ignoring. The personal contents — remembered cases, aesthetic projections, professional judgements, partial inferences — are part of *that participant's* activity space in the individual sense. They are not directly part of anyone else's.

Historically, philosophers drew the mind–world boundary at the skin. The extended-mind tradition (Clark & Chalmers, 1998; Clark, 2008), the active-inference tradition (Friston, 2010; Constant, Clark, Kirchhoff, & Friston, 2022), and the work on epistemic action (Kirsh & Maglio, 1994) have variously broken that boundary. When an agent uses a marker, a sheet of paper, or a sketch to externalise a thought, the cognitive system at that moment is not located inside the skull; it is constituted by the joint operation of the agent's perception, the agent's motor action, and the externalised marks. The marker, the paper, and the marks are not external props to a mental process; they are part of the process.

Yet the extended-mind move does not, by itself, resolve where the activity space ends. When an agent has a thought *about* an externalised structure — a thought that depends on the agent's personal history, aesthetic sensibilities, professional formation, or remembered cases — is that thought part of the activity space, or adjacent to it? It is closely coupled to the public activity space (it is *about* the externalised structure) and it has consequences within the public activity space (it will move the agent to mark, to speak, to point). But the thought itself, qua thought, is the agent's alone. It is not in the room in the way the externalised structure is in the room.

The right way to put this is to distinguish *public* and *individual* activity space and to be precise about how they are coupled.

The public activity space is the set of structures, surfaces, marks, configurations, traces, words, and gestures that the participants jointly construct and that have shared identity conditions. It is the proper target of the formal model developed in §4 below.

The individual activity space is each participant's enactive bubble — the set of contents they are treating as salient, the inferences they are running, the projections they are making onto the scene. Each participant has one; participants' individual activity spaces are different even when they are looking at the same wall.

The two are coupled through *externalisation* and *internalisation*. Externalisation moves content from individual to public; internalisation moves content from public into the individual activity spaces of those who perceive it. The traffic is more or less continuous during active joint work, and the productivity of joint work depends in part on how cheap, reliable, and well-protected that traffic is.

This distinction matters for the formal model in two ways. First, the formal model in §4 is a model of the *public* activity space; it cannot model the individual activity spaces directly. Second, the distinction sets up the limit of the predictive-processing framework discussed in §8: much of what we mean by *thinking with external representations* is exactly the work of moving content between individual and public, and the predictive-processing framework captures that work cleanly only when there is a fixed hidden state to be inferred, which is the special case rather than the general one.

## 4. Activity space as a latent state space: the formalism

The *public* activity space can be formalised as the latent state space of a partially observable generative model. Let the public activity state at time $t$ be
$$z_t = (x_t, c_t, \varphi_t, m_t, s_t)$$
where:
- $x_t$ is the **agent–environment configuration**: the positions, postures, gaze targets, and tool-grasps of all participants, together with their immediate surrounds;
- $c_t$ is the **social-pragmatic context**: the project assignment, role configuration, and standing norms under which the current activity is interpretable;
- $\varphi_t$ is the **activity phase**: the current logical phase of the activity, drawn from the activity's phase repertoire;
- $m_t$ is the **microvenue configuration**: the current configuration of any controllable variables in the environment (lighting, surface assignments, partitions, acoustic field, display content);
- $s_t$ is the **social-orientational state**: who attends to whom, who speaks, what is shared, what is hidden.

An external observer (a person, a building, an analyst) observes only $o_t$, a stream of multi-modal signals — sensor data, calendar entries, transcript content, surface state, and so on. The task is to maintain a posterior $q(z_t \mid o_{1:t})$ over the activity state, to use that posterior to evaluate policies $\pi$ in some intervention repertoire, and to update the posterior in response to observed consequences of intervention.

The generative model has the standard partially-observable form:
$$p(o_{1:T}, z_{1:T}, \pi) = p(\pi)\, p(z_1) \prod_{t=1}^{T} p(o_t \mid z_t)\, p(z_{t+1} \mid z_t, \pi).$$

Perception updates the posterior $q(z_t)$ to minimise variational free energy:
$$F[q] = \mathbb{E}_{q(z_t)}[\ln q(z_t) - \ln p(o_t, z_t)].$$

Policy selection minimises expected free energy $G(\pi)$, which decomposes into epistemic (information-gain) and extrinsic (utility-relative-to-preferences) components in the standard active-inference manner (Friston, FitzGerald, Rigoli, Schwartenbeck, & Pezzulo, 2017, ~3,200 citations):
$$G(\pi) = \underbrace{\mathbb{E}_q[D_{KL}(q(z \mid o, \pi) \| q(z \mid \pi))]}_{\text{epistemic value}} + \underbrace{\mathbb{E}_q[-\ln p(o \mid C)]}_{\text{pragmatic value relative to preferences } C}.$$

This is the formal apparatus. The substantive theoretical content is in the structured factorisation of $z_t$ into the five components above. Each component carries a different semantic and a different computational treatment, and the next section unpacks them.

## 5. The variables of the latent state, semantically and computationally

The five components of $z_t$ are not interchangeable. They differ in semantic content (what aspect of the public activity space they encode), in the observable signals from which they are inferred, in the computational machinery appropriate to that inference, and in their characteristic update rates.

**$x_t$ — Agent–environment configuration.** This is the physical-level state at the resolution of bodies and immediate surrounds. *Semantic content*: per-participant position, posture, gaze direction, tool grasp, attended surface. *Observable signals*: camera-based skeletal pose estimation, occupancy sensing, gaze tracking where ethically permitted, surface-touch sensors, microphone-array spatial audio localisation, tool-presence detection. *Inference method*: multi-modal sensor fusion via Kalman or particle filtering for body pose; deep pose-estimation networks for higher-level interpretation; privacy-preserving variants retain only abstract spatial pose without identifying features. *Characteristic update rate*: frame-rate (gaze, posture) to sub-second (position).

**$c_t$ — Social-pragmatic context.** This is the framing under which the moment is interpretable. *Semantic content*: project assignment, role configuration, standing norms. *Observable signals*: calendar integration, project-management software, organisational role data, prior session traces. *Inference method*: symbolic structured retrieval combined with role-and-norm priors learned from organisational data; Bayesian fusion with explicit user input in ambiguous cases. *Characteristic update rate*: session-rate (changes once per session or once per phase transition).

**$\varphi_t$ — Activity phase.** This is the current logical phase of the activity, drawn from a learned phase repertoire. *Semantic content*: which phase the activity is in (orientation, comparison, critique, generation, convergence, resolution, or whatever phases the activity admits); time-since-phase-onset; expected next phase. *Observable signals*: explicit phase labels in agenda when provided; transcript content patterns; surface-content patterns; spatial reorganisation patterns; audio-event patterns. *Inference method*: hierarchical reinforcement-learning option discovery to learn the phase repertoire offline (Bacon, Harb, & Precup, 2017, ~1,800; Sutton, Precup, & Singh, 1999, ~5,500); hidden-Markov-model or recurrent variational state-space model for online phase inference. *Characteristic update rate*: phase-rate (minutes to hours), with finer-grained sub-phase inference at sub-minute rate.

**$m_t$ — Microvenue configuration.** This is the only component the model does not infer; it is set by the building (or whatever environmental-control system is in scope). *Semantic content*: lighting balance, display content, surface assignment, partition position, acoustic field settings, AI-surfaced content. *Inference method*: none. *Characteristic update rate*: actuator-controlled.

**$s_t$ — Social-orientational state.** This is the interpersonal-dynamics state. *Semantic content*: attentional graphs (who is attending to whom and to what); speaker-listener configuration; sharedness ratings for visible content. *Observable signals*: gaze tracking, voice activity detection, turn-taking inference, posture analysis, proximity. *Inference method*: Bayesian theory-of-mind models (Baker, Saxe, & Tenenbaum, 2009, ~700; Baker, Jara-Ettinger, Saxe, & Tenenbaum, 2017, ~600) combined with multi-modal social-signal processing. *Characteristic update rate*: second-rate to phase-rate.

A useful factorisation of the posterior reflects these update rate differences:
$$q(z_t) = q(x_t)\, q(c_t)\, q(\varphi_t \mid c_t)\, q(s_t \mid x_t)\, \delta(m_t = \hat{m}_t)$$
where $\hat{m}_t$ is the (known) actuator state. The factorisation is approximate; in particular $\varphi_t$ depends on $x_t$ and $s_t$ as well as $c_t$, and a full implementation would model the dependencies as part of the learned generative model.

## 6. Operations on the latent state

Three operations on $z_t$ matter for the framework's claims.

*Posterior maintenance.* The model updates $q(z_t)$ continuously as new observations arrive. Each observation channel has a learned precision, scaling its contribution to the update. Component update rates vary; updates are asynchronous across components. The technical machinery is variational inference (Kingma & Welling, 2014, ~50,000 citations; Hafner, Lillicrap, Norouzi, & Ba, 2020, ~1,200), with the specific algorithm dictated by the model class. Successor representations or predictive maps (Stachenfeld, Botvinick, & Gershman, 2017, ~1,400) provide the transition-dynamics layer when state-space density makes Gaussian-state models impractical.

*Policy evaluation.* For each candidate intervention $\pi$ in the available repertoire — a lighting change, a partition adjustment, an AI surfacing, a re-display of a past sketch — the model computes the expected free energy $G(\pi)$ as in §4. Policies that minimise $G$ balance expected information gain with expected progress toward preferred states (preferences are either given or learned from past acceptance and override patterns). This is exactly the active-inference policy-selection structure (Friston et al., 2017); the substantive difference from typical active-inference applications is that the latent state $z_t$ is structured into the five components above rather than being a flat vector, so policies can be evaluated against their expected effect on each component separately.

*Posterior update from return-path evidence.* When an intervention is enacted, the model observes the participants' response and updates priors, precisions, and transition models accordingly. The model runs *two clocks* in parallel. The *fast clock* (seconds to minutes) updates the posterior over $x_t$, $s_t$, and $\varphi_t$ in response to immediate behaviour — overrides, postural changes, voice attenuation, attention coherence. The *slow clock* (hours to weeks) updates priors and transition models in response to longer-term behaviour — whether externalised structures are returned to, whether they are built on, whether they consolidate into deliverables. The two-clock structure follows directly from the dual-register argument of §8.

## 7. Connections to existing computational frameworks

The formalism integrates several existing lines of work without depending on any one of them being implemented exactly as cited. The integration is the substantive contribution; the cited frameworks are scaffolding.

*Predictive coding and active inference* (Rao & Ballard, 1999, ~7,000; Friston, 2010; Friston et al., 2017; Clark, 2013, 2016) provide the generative-model architecture, the precision-weighting machinery, and the policy-selection apparatus through expected free energy.

*World-model agents in deep reinforcement learning* (Ha & Schmidhuber, 2018, ~3,500; Hafner et al., 2020; Hafner, Pasukonis, Ba, & Lillicrap, 2023) provide the engineering substrate for learned latent representations of complex multi-modal observation streams, including the planning-in-latent-space machinery that activity-aware systems would use to evaluate candidate microvenue configurations.

*Successor representations and predictive maps* (Stachenfeld et al., 2017) provide the policy-dependent transition-dynamics layer; they are particularly well-suited to representing the temporal grain of activity (a participant standing at a whiteboard is likely to gesture next, then step back, then invite a critique).

*Hierarchical reinforcement learning with option discovery* (Sutton et al., 1999; Bacon et al., 2017) provides the phase-structure layer; phases of activity are option-like in the temporal-abstraction sense, and the phase repertoire of an activity can be learned by option-discovery methods applied to historical activity traces.

*Bayesian theory of mind* (Baker et al., 2009, 2017) provides the inference of the social-orientational state $s_t$; inferring who is attending to whom, who has which role, and what is shared between participants is a Bayesian-ToM inference problem.

*Probabilistic programming* (Goodman, Mansinghka, Roy, Bonawitz, & Tenenbaum, 2008) provides the right register when activity has a known logical form (a recipe, a protocol, a meeting agenda) but variable physical realisation; the logical level can be specified declaratively and Bayesian inference can fit the declarative structure to data.

*Extended active inference* (Constant et al., 2022; Kirchhoff, Parr, Palacios, Friston, & Kiverstein, 2018) provides the conceptual bridge to environmental scaffolding: the agent and the world together constitute a Markov blanket over which free-energy is minimised.

What none of these frameworks captures, by themselves, is the *integrated* structure proposed here: a latent state with five components, each with its own semantic and computational treatment, jointly inferred from multi-modal observation streams, used for activity-supportive policy selection, with explicit two-clock learning from return-path evidence. The integration is the contribution of the present paper.

## 8. The limit of predictive processing: thinking with external representations

The framework developed in §§4–7 inherits its policy-evaluation machinery from predictive processing and active inference. That machinery captures a substantial slice of human cognition cleanly: perception (Rao & Ballard, 1999), motor control (Adams, Shipp, & Friston, 2013), attention (Feldman & Friston, 2010), navigation (Kaplan & Friston, 2018), and epistemic action of the Tetris-rotation kind (Kirsh & Maglio, 1994, ~1,500 citations). It generalises with the *extended-active-inference* move (Constant et al., 2022) to environmental scaffolding more broadly: pencil-and-paper, whiteboards, sticky notes, and even institutional structures can be cast as part of the inference machinery, with the agent and the world jointly minimising free energy.

But there is a class of cognitive activity for which the active-inference framing distorts more than it illuminates, and this class is the one that makes design studios, mathematics seminars, laboratory benches, kitchens, and writers' desks valuable. I have argued elsewhere (Kirsh, 2010) that *thinking with external representations* involves at least the following operations, none of which is naturally cast as the reduction of error against a fixed external fact:

*Re-representation.* An agent replaces one representation (Roman numerals for arithmetic) with another (Arabic numerals). The numbers do not change. What changes is which operations are computationally tractable (Larkin & Simon, 1987, ~5,500). The choice is driven not by error reduction but by anticipated affordance of the representation for operations whose nature the agent may not yet fully know (Sloman, 1985).

*Exploratory externalisation.* An agent sketches on paper not to disambiguate a fixed external fact but to *bring into existence* a structure whose properties they will then discover by inspection. The constraints emerge as the agent draws; the cognitive content is partly created by the externalisation itself.

*Generative externalisation.* As marks accumulate on the paper, they suggest other marks. The triangle that emerges in a hybrid floor-plate sketch primes visual associations that none of the participants brought to the conversation. The externalisation is not a sensory observation; it is a structure that operates on the agents who attend to it.

*Re-identification and shareability.* An externalised structure has identity conditions that survive across observers and across time. The agents can refer to *this corner* with reliable shared reference because the externalisation is shared; without it, the same phrase would mean different corners to different agents (Goodwin, 1994, ~6,000).

*Persistence and operability.* Externalised structure can be measured, photographed, traced, rearranged, cut, recombined. None of this is available to a purely mental representation (Hutchins, 1995; Clark & Chalmers, 1998).

A defender of predictive processing will say that all of this can be cast as policy selection under expected free energy: each of these operations is taken because of its anticipated long-run effect on the agent's model. The move is technically defensible and explanatorily empty. It generalises the formalism to the point where it predicts everything and explains nothing specific; the distinction between glare-avoidance and exploratory sketching is lost. Andy Clark himself, in *Surfing Uncertainty* (Clark, 2016, ~3,000), notes that the framework's predictive power is in danger of becoming Procrustean when stretched to cover all of cognition.

The more honest theoretical position is that predictive processing is a powerful and partial account of cognition. It captures perception, attention, and the epistemic-action subset of external-representation use cleanly. It captures the *re-representational*, *exploratory*, *generative*, and *jointly constructive* uses of external representation only by stretching its core notion of *prediction error* until that notion loses its discriminative power. Those uses require a complementary theoretical vocabulary: one that talks about operational affordance of representations, cost structure of cognitive operations, re-identifiability of structure, shareability and joint construction, and the way representations enable thinking that would otherwise be impossible (Kirsh, 2010; Hutchins, 1995; Larkin & Simon, 1987; Zhang & Norman, 1994).

The framework of §§4–7 accommodates this limit by structure rather than by extension. The latent state $z_t$ models the public activity space — the externalised structures, the configurations, the social-orientational state — but it does not pretend to model the cognitive operations that produce the externalisations. The framework's policy-evaluation machinery decides which microvenue configurations to deploy, but the cognitive value of those configurations for thinking-with-external-representations work is something the framework treats *operationally* (does the configuration support re-representation? persistence? re-identifiability? rearrangement?) rather than as a function to be minimised. The two-clock structure of §6 is the formal trace of this concession: the slow-clock learning from return-path evidence is specifically the way the framework learns whether thinking-with-external-representations support has worked, on a timescale active inference does not naturally accommodate.

## 9. Implications for the cognitive science of the built environment

The framework has consequences for how cognitive science should approach the built environment as an object of study, and for how architecture should approach cognitive science as a partner discipline.

First, the framework gives architects, designers, and cognitive scientists a *shared vocabulary*. Activity space — with its three levels, its public–individual distinction, its five-component latent state, and its two registers of cognitive support — is general enough to be applicable across architectural settings and specific enough to make empirical predictions. An architectural team can ask: which microvenue configurations support the comparison phase of design critique? A cognitive science research team can ask: how does external-representation persistence affect re-identifiability of jointly constructed structure in design studios? The questions are not the same, but they are formulated in terms a common vocabulary licenses.

Second, the framework lets us pose *specific empirical questions* about built environments that the existing literature has been unable to ask cleanly. Examples: How does override rate in adaptive lighting depend on accuracy of phase inference? How does return-to-artefact rate for sketches depend on persistence of externalised structure across sessions? How does precision-shaping by acoustic-field reconfiguration interact with speech intelligibility for in-team versus out-of-team channels? Each of these has a measurable dependent variable and a manipulable independent variable; the framework supplies the theoretical motivation.

Third, the framework *bridges the gap between cognitive theory and architectural practice*. Architects have long known, by intuition and rule of thumb, that certain configurations support certain activities — that the comparison wall works, that the recovery niche helps, that the writable surface invites sketching. Cognitive theory has been able to confirm these intuitions only by indirect inference from sensory, motor, attentional, or social-cognitive findings. The activity-space framework gives the architectural intuitions a direct theoretical grounding: comparison walls work because they are externalised priors that shape precision; recovery niches work because they support phase transitions in the activity-state model; writable surfaces invite sketching because they support the externalisation traffic between individual and public activity spaces. The architect's tacit knowledge becomes explicit; the cognitive scientist's theoretical constructs become applicable.

Fourth, the framework *identifies a class of failure modes* that current adaptive-building practice has been unable to articulate. Buildings that script behaviour fail because they close the state space. Buildings that auto-summarise externalised structure fail because they smooth in-progress thinking. Buildings that optimise physical parameters in isolation fail because they ignore the activity-level coordination demands. Buildings that infer too much about occupants' inner states fail because they overstep the privacy implications of the public–individual distinction. Each of these failure modes is now nameable in the framework's terms, and each can be designed against.

## 10. Conclusion: filling the gap

Cognitive science has theories of agents and theories of cognition but has lacked a theory of the structured environment that supports cognitive activity. Affordance theory points toward but does not develop such a theory. Distributed and extended cognition operate within but do not characterise the structure they depend on. Predictive processing and active inference assume but do not formalise the environmental scaffolding that makes their explanatory claims work.

The activity-space framework developed in this paper proposes to fill the gap. The construct is the temporally structured, socially situated, cognitively interpreted arena of action. It has public and individual dimensions, coupled through externalisation. Its public dimension admits formal treatment as the latent state space of a partially observable generative model with five structured components. Each component is computationally tractable and admits inference from multi-modal observation streams. The framework integrates predictive processing, active inference, world-model agents, hierarchical reinforcement learning, and Bayesian theory of mind without depending on any one of them. It identifies an explicit limit at the boundary of thinking-with-external-representations work that predictive processing cannot capture without becoming Procrustean.

The built environment is the most demanding application because buildings are designed, persistent, multi-actor, and multi-scale. The companion paper (Kirsh, in preparation, *Activity-aware architecture*) applies the framework to adaptive buildings. But the framework is not specifically architectural. It applies wherever cognitive activity unfolds in a structured environment: in classrooms, laboratories, hospitals, kitchens, vehicles, studios, courtrooms, and the screens and devices around which much contemporary work is organised. The gap the framework fills is general; the architectural application is the natural first case.

---

## References

Adams, R. A., Shipp, S., & Friston, K. J. (2013). Predictions not commands: Active inference in the motor system. *Brain Structure and Function*, 218(3), 611–643. https://doi.org/10.1007/s00429-012-0475-5 (Google Scholar: ~1,600)

Bacon, P.-L., Harb, J., & Precup, D. (2017). The option-critic architecture. *Proceedings of the AAAI Conference on Artificial Intelligence*, 31(1), 1726–1734. (Google Scholar: ~1,800)

Baker, C. L., Saxe, R., & Tenenbaum, J. B. (2009). Action understanding as inverse planning. *Cognition*, 113(3), 329–349. https://doi.org/10.1016/j.cognition.2009.07.005 (Google Scholar: ~700)

Baker, C. L., Jara-Ettinger, J., Saxe, R., & Tenenbaum, J. B. (2017). Rational quantitative attribution of beliefs, desires and percepts in human mentalizing. *Nature Human Behaviour*, 1, 0064. https://doi.org/10.1038/s41562-017-0064 (Google Scholar: ~600)

Brozzoli, C., Cardinali, L., Pavani, F., & Farnè, A. (2010). Action-specific remapping of peripersonal space. *Neuropsychologia*, 48(3), 796–802. https://doi.org/10.1016/j.neuropsychologia.2009.10.009

Bufacchi, R. J., & Iannetti, G. D. (2018). An action field theory of peripersonal space. *Trends in Cognitive Sciences*, 22(12), 1076–1090. https://doi.org/10.1016/j.tics.2018.09.004 (Google Scholar: ~400)

Clark, A. (2008). *Supersizing the mind: Embodiment, action, and cognitive extension*. Oxford University Press. (Google Scholar: ~3,000)

Clark, A. (2013). Whatever next? Predictive brains, situated agents, and the future of cognitive science. *Behavioral and Brain Sciences*, 36(3), 181–204. https://doi.org/10.1017/S0140525X12000477 (Google Scholar: ~3,800)

Clark, A. (2016). *Surfing uncertainty: Prediction, action, and the embodied mind*. Oxford University Press. (Google Scholar: ~3,000)

Clark, A., & Chalmers, D. (1998). The extended mind. *Analysis*, 58(1), 7–19. https://doi.org/10.1093/analys/58.1.7 (Google Scholar: ~7,500)

Constant, A., Clark, A., Kirchhoff, M., & Friston, K. J. (2022). Extended active inference: Constructing predictive cognition beyond skulls. *Mind & Language*, 37(3), 373–394. https://doi.org/10.1111/mila.12330 (Google Scholar: ~150)

Feldman, H., & Friston, K. J. (2010). Attention, uncertainty, and free-energy. *Frontiers in Human Neuroscience*, 4, 215. https://doi.org/10.3389/fnhum.2010.00215 (Google Scholar: ~2,500)

Friston, K. J. (2010). The free-energy principle: A unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127–138. https://doi.org/10.1038/nrn2787 (Google Scholar: ~12,000)

Friston, K. J., FitzGerald, T., Rigoli, F., Schwartenbeck, P., & Pezzulo, G. (2017). Active inference: A process theory. *Neural Computation*, 29(1), 1–49. https://doi.org/10.1162/NECO_a_00912 (Google Scholar: ~3,200)

Gibson, J. J. (1979). *The ecological approach to visual perception*. Houghton Mifflin. (Google Scholar: ~30,000)

Goodman, N. D., Mansinghka, V. K., Roy, D. M., Bonawitz, K., & Tenenbaum, J. B. (2008). Church: A language for generative models. *Proceedings of the 24th Conference on Uncertainty in Artificial Intelligence*, 220–229. (Google Scholar: ~700)

Goodwin, C. (1994). Professional vision. *American Anthropologist*, 96(3), 606–633. https://doi.org/10.1525/aa.1994.96.3.02a00100 (Google Scholar: ~6,000)

Ha, D., & Schmidhuber, J. (2018). World models. *Advances in Neural Information Processing Systems*, 31, 2451–2463. (Google Scholar: ~3,500)

Hafner, D., Lillicrap, T., Norouzi, M., & Ba, J. (2020). Mastering Atari with discrete world models. *arXiv preprint arXiv:2010.02193*. (Google Scholar: ~1,200)

Hafner, D., Pasukonis, J., Ba, J., & Lillicrap, T. (2023). Mastering diverse domains through world models. *arXiv preprint arXiv:2301.04104*.

Hutchins, E. (1995). *Cognition in the wild*. MIT Press. (Google Scholar: ~10,000)

Kaplan, R., & Friston, K. J. (2018). Planning and navigation as active inference. *Biological Cybernetics*, 112(4), 323–343. https://doi.org/10.1007/s00422-018-0753-2 (Google Scholar: ~500)

Kingma, D. P., & Welling, M. (2014). Auto-encoding variational Bayes. *Proceedings of the 2nd International Conference on Learning Representations*. (Google Scholar: ~50,000)

Kirchhoff, M., Parr, T., Palacios, E., Friston, K., & Kiverstein, J. (2018). The Markov blankets of life: Autonomy, active inference and the free energy principle. *Journal of the Royal Society Interface*, 15(138), 20170792. https://doi.org/10.1098/rsif.2017.0792 (Google Scholar: ~700)

Kirsh, D. (1995). The intelligent use of space. *Artificial Intelligence*, 73(1–2), 31–68. https://doi.org/10.1016/0004-3702(94)00017-U (Google Scholar: ~1,400)

Kirsh, D. (2010). Thinking with external representations. *AI & Society*, 25(4), 441–454. https://doi.org/10.1007/s00146-010-0272-8 (Google Scholar: ~600)

Kirsh, D. (2025). Reimagining space: How activity space explains human behaviour in buildings. *Architectural Science Review*. https://doi.org/10.1080/00038628.2025.2542213

Kirsh, D. (in preparation). Activity-aware architecture: Microvenues, external representations, and the future of co-adaptive buildings.

Kirsh, D., & Maglio, P. (1994). On distinguishing epistemic from pragmatic action. *Cognitive Science*, 18(4), 513–549. https://doi.org/10.1207/s15516709cog1804_1 (Google Scholar: ~1,500)

Laland, K. N., Odling-Smee, J., & Feldman, M. W. (2000). Niche construction, biological evolution, and cultural change. *Behavioral and Brain Sciences*, 23(1), 131–146. https://doi.org/10.1017/S0140525X00002417

Larkin, J. H., & Simon, H. A. (1987). Why a diagram is (sometimes) worth ten thousand words. *Cognitive Science*, 11(1), 65–100. https://doi.org/10.1111/j.1551-6708.1987.tb00863.x (Google Scholar: ~5,500)

Odling-Smee, F. J., Laland, K. N., & Feldman, M. W. (2003). *Niche construction: The neglected process in evolution*. Princeton University Press.

Rao, R. P. N., & Ballard, D. H. (1999). Predictive coding in the visual cortex: A functional interpretation of some extra-classical receptive-field effects. *Nature Neuroscience*, 2(1), 79–87. https://doi.org/10.1038/4580 (Google Scholar: ~7,000)

Robbins, P., & Aydede, M. (Eds.). (2009). *The Cambridge handbook of situated cognition*. Cambridge University Press. (Google Scholar: ~700)

Sloman, A. (1985). Why we need many knowledge representation formalisms. In M. Bramer (Ed.), *Research and development in expert systems* (pp. 163–183). Cambridge University Press. (Google Scholar: ~400)

Stachenfeld, K. L., Botvinick, M. M., & Gershman, S. J. (2017). The hippocampus as a predictive map. *Nature Neuroscience*, 20(11), 1643–1653. https://doi.org/10.1038/nn.4650 (Google Scholar: ~1,400)

Sutton, R. S., Precup, D., & Singh, S. (1999). Between MDPs and semi-MDPs: A framework for temporal abstraction in reinforcement learning. *Artificial Intelligence*, 112(1–2), 181–211. https://doi.org/10.1016/S0004-3702(99)00052-1 (Google Scholar: ~5,500)

Xiong, A., & Proctor, R. W. (2018). The role of task space in action control: Evidence from research on instructions. In B. H. Ross (Ed.), *Psychology of Learning and Motivation* (Vol. 69, pp. 325–358). Elsevier.

Zhang, J., & Norman, D. A. (1994). Representations in distributed cognitive tasks. *Cognitive Science*, 18(1), 87–122. https://doi.org/10.1207/s15516709cog1801_3 (Google Scholar: ~1,500)
