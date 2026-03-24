# GUI Design Agent Memo

Date: 2026-03-24
Repo owner: `/Users/davidusa/REPOS/Knowledge_Atlas`
Purpose: explain the reasoning behind the Knowledge Atlas GUI design agent, including the key debates and the design principles carried into the agent contract

## Why this memo exists

The GUI design agent should not be a thin prompt with a checklist.
It needs a theory of the product.

Knowledge Atlas is not a small app.
It is a large evidence-and-reasoning system with:
- public discovery pages
- student-facing teaching pages
- research workspaces
- evidence inspection surfaces
- theory and argument views
- AI-assisted explanation and synthesis layers

That means the design agent has to do more than style pages.
It has to make serious judgments about:
- page type
- framework choice
- information density
- interaction structure
- provenance and uncertainty visibility
- how AI participates in the interface

## Existing lineage

The current agent did not begin from scratch.
It grows out of:
- the original K-ATLAS GUI agent spec
- the critique-and-repair document that hardened that spec
- the ATLAS site functional spec
- the ATLAS personas and UI strategy
- the experiment-builder architecture and panel notes
- the best current Knowledge Atlas pages in this repo

The problem was not lack of ideas.
The problem was dispersion.
The design reasoning was spread across multiple repos and documents, and it did not yet fully encode:
- Streamlit as the current preferred framework
- contemporary AI-interface judgment
- explicit framework-governance rules
- a local check-and-repair loop

## The key debates

### Debate 1: Should the system optimize for simplicity or research power?

This was the oldest and most important debate.

One side of the design lineage insisted that the interface must remain readable and approachable.
The other side insisted that a research system becomes useless if it hides evidence, provenance, and qualification behind simplified cards.

The right answer was not to choose one side.
The right answer was to distinguish page types.

What came out of that debate:
- some pages should be guided, sparse, and public-facing
- some pages should be dense, faceted, and inspectable
- the agent must explicitly state what kind of page it is designing

This is why the agent now requires the page to be typed as:
- retrieval-first
- synthesis-first
- workflow-first
- comparison-first
- teaching-first

Without that, the system keeps oscillating between oversimplification and overload.

### Debate 2: Should AI be the interface, or part of the interface?

The contemporary temptation is to make everything chat-first.
That would be a mistake here.

The internal design lineage already leaned away from chat-only UX.
The newer AI-UX guidance confirms that instinct.
PAIR's patterns push toward:
- setting the right expectations
- clarifying what the system can and cannot do
- being accountable for errors
- giving the user a way forward

For Knowledge Atlas, the strongest conclusion is:
- AI should usually be paired with structure

That means:
- faceted evidence tables
- pinned result cards
- compare trays
- source drawers
- result tables
- topic grids
- command palettes
- guided question entry

The agent therefore treats AI as a collaborator inside a structured interface, not as a replacement for interface structure.

### Debate 3: Should Streamlit be temporary, or a first-class implementation target?

This debate is live.

One view says Streamlit is a prototype tool and serious systems should migrate away from it quickly.
The other view says Streamlit is the right substrate for evidence-heavy internal tools if the team is disciplined about design.

Your stated preference resolves this for now.
The design agent therefore treats Streamlit as:
- the default framework
- not the only framework
- not a permission slip for generic styling

The debate matters because Streamlit has real tradeoffs.

What Streamlit gives us:
- speed
- low plumbing cost
- strong support for data-heavy workspaces
- good iteration velocity for research tools

What Streamlit threatens:
- generic app chrome
- excessive vertical stacking
- weak page identity
- accidental loss of visual hierarchy

So the design agent does not merely prefer Streamlit.
It imposes conditions on its use:
- explicit design system layer
- explicit navigation identity
- intentional containers/columns/tabs
- preserved state visibility
- no lazy acceptance of stock layout patterns

### Debate 4: How expressive should the visual language be?

There was a real risk of falling into one of two bad extremes:
- dead enterprise minimalism
- overstylized novelty that hurts analytic work

The current KA pages already show a useful middle path:
- warm palette
- strong headers
- serif/sans contrast
- serious but approachable tone

Recent Google/Material guidance strengthens the argument that expressive design is legitimate when it helps users notice what matters.
That is important for a system like this, because the interface must surface:
- importance
- disagreement
- uncertainty
- evidence density
- next action

The debate resolved into a principle:
- use expressive design to clarify function and emphasis, not to decorate emptiness

### Debate 5: Should evidence and explanation be merged into a single reading surface?

This is a recurring problem in science communication systems.
A purely inspectable interface becomes hard to read.
A purely narrative interface becomes hard to trust.

The panel logic, the science-writer work, and the UI docs all point to the same answer:
- dual-form presentation

That means:
- readable science-writer prose
- inspectable result structures
- figures/tables when useful
- rewritten explanatory captions where needed
- one-click access to provenance

This debate directly shaped the agent's insistence on provenance behavior and uncertainty behavior.

### Debate 6: Should theory be treated as a background garnish or a first-class layer?

Theory is central to the product, but theory assignment is not always clean.
That creates a design tension.
If theory is hidden, the system looks shallow.
If theory is overstated, the system becomes dishonest.

The resolution was to surface theory, but with discipline.
The UI should distinguish:
- paper terms
- canonical theory tags
- theory role
- theory fidelity or confidence

The agent therefore must reason about what the page is allowed to imply.
Theory should not be shown as stronger than the evidence warrants.

## The most important justifications

### Why page-type typing was carried forward

Because the same design pattern is not correct for every page.
A teaching page and an evidence-audit page should not have the same information hierarchy.
The old spec was strong, but this distinction needed to become explicit.

### Why framework choice is now mandatory output

Because otherwise the decision happens by inertia.
Large systems drift when framework choice is implicit.
The agent must explain why Streamlit, static HTML, or a richer framework is appropriate.

### Why provenance and uncertainty remain non-negotiable

Because Knowledge Atlas is not only trying to answer questions.
It is trying to show how it knows, what is uncertain, and where the argument could fail.
If the design loses that, the product loses its core character.

### Why AI behavior needed a more explicit contract

Because modern interfaces increasingly mix retrieval, synthesis, and inference.
Without a contract, users cannot tell what kind of output they are looking at.
That is especially dangerous in a research system.

### Why the repair loop was included

Because good taste does not scale.
A repeatable system needs:
- a spec
- a review frame
- a checker
- repair categories

The checker is intentionally narrow.
It does not replace design review.
But it creates a floor and reduces preventable omissions.

## The design principles incorporated into the agent

1. Design from tasks, not from component libraries.
2. Type the page before laying it out.
3. Default to Streamlit for internal tools, but style it aggressively and intentionally.
4. Use richer frameworks only when they pay for themselves.
5. Keep AI inside a structured interface whenever possible.
6. Preserve the retrieval / synthesis / inference boundary.
7. Keep provenance inspectable and uncertainty visible.
8. Let expressive design direct attention, not dilute seriousness.
9. Use dual-form result presentation: readable prose plus structured evidence.
10. Preserve context across handoffs.
11. Treat theory as explicit but defeasible.
12. Build for large-system coherence, not only page-local polish.
13. Treat loading, empty, and failure states as product behavior.
14. Make the first action obvious.
15. Design for laptop and tablet widths at minimum.

## What the memo changes in practice

It changes the agent from a page-writer into a design-governance tool.

That means the agent now helps answer:
- what kind of page is this
- what framework should build it
- what should be visible immediately
- what is deferred
- how should AI appear here
- what must remain inspectable
- how does the page hand off to the next one

## Where this should live

### Canonical ownership

The canonical GUI design agent should live in the repo that owns GUI implementation.
Right now that is:
- `/Users/davidusa/REPOS/Knowledge_Atlas`

That keeps the spec close to:
- the active pages
- the checker
- the tests
- the implementation surface

### Shared discoverability

But agent specs should also be discoverable in a common place.
The right model is:
- canonical spec in the owning repo
- shared registry in a cross-repo index

That avoids two bad outcomes:
- orphaned specs with no implementation owner
- duplicated specs that drift apart

## Bottom line

There was already a strong GUI-design intuition in this project.
The work here was to make it operational:
- one canonical spec
- one explicit panel synthesis
- one process and repair loop
- one shared registry entry
- one local checker and tests

That is enough to make future GUI work more disciplined without freezing it into a rigid style manual.
