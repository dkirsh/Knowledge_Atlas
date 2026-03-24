# GUI Design Panel Review

Date: 2026-03-24
Repo: `/Users/davidusa/REPOS/Knowledge_Atlas`
Purpose: consolidate internal and external design judgment into one current review for the GUI design agent

## Panel composition

Internal lineage reviewed:
- K-ATLAS GUI Agent v1
- GUI agent critique / repairs
- ATLAS site functional spec
- ATLAS personas UI strategy
- experiment-builder pedagogy architecture
- existing Knowledge Atlas pages in this repo

Contemporary external guidance reviewed:
- Apple UI Design Dos and Don'ts
  - <https://developer.apple.com/design/tips/>
- Google PAIR guidebook patterns
  - <https://pair.withgoogle.com/guidebook-v2/patterns>
- Material 3 Expressive research and launch material
  - <https://design.google/library/expressive-material-design-google-research>
  - <https://blog.google/products-and-platforms/platforms/android/material-3-expressive-android-wearos-launch/>

Advisory voices synthesized:
- Bret Victor
- Giorgia Lupi
- Don Norman
- Katie Dill
- Julie Zhuo
- Leah Buley
- Google PAIR patterns
- Apple HIG / design guidance
- Material Design / Expressive research

## What the current KA work already gets right

1. Strong page identity.
2. A non-generic visual language.
3. Good use of warm tones and analytic seriousness.
4. Explicit page purpose in several flows.
5. A willingness to use dense views when the task requires it.

## Where the current work is still fragile

1. Framework drift.
   - Some pages are static HTML prototypes while future tool surfaces likely belong in Streamlit.
   - This is fine, but it needs explicit governance.

2. Process drift.
   - Good instincts exist, but the design judgment is still carried in people and scattered docs.

3. AI behavior specification.
   - The older agent knew AI mattered, but did not fully specify inspectability, confirmation, and failure recovery.

4. Large-system coherence.
   - The product is a suite, not a single page.
   - Navigation, handoff, and shared interaction patterns need to stay stable as the system grows.

## Consolidated panel judgment

### 1. Streamlit is the default, not the prison

Use Streamlit first for internal tools and analytic workspaces because:
- it speeds iteration
- it fits evidence-heavy work
- it lowers plumbing cost

But Streamlit is only acceptable if the team actively imposes:
- typography
- spacing
- palette
- state visibility
- intentional layout

The panel rejects stock Streamlit look-and-feel as a default product style.

### 2. Expressive design is appropriate here

The system is large and cognitively heavy.
Flat neutral UI would hide structure.

The panel endorses expressive design when it:
- directs attention
- groups meaningfully
- improves glanceability
- strengthens hierarchy

This follows current Material guidance: expressiveness is legitimate when it improves comprehension and action, not only aesthetics.

### 3. AI should rarely be the only interface

For Knowledge Atlas, AI is usually strongest when paired with structure:
- starter questions
- faceted tables
- compare panes
- topic cards
- evidence drawers
- result tables
- workspace state

The panel rejects chat-only surfaces for most serious research tasks.

### 4. Retrieval / synthesis boundaries must stay visible

PAIR's guidance is directly relevant here.
The user must know:
- what came from the corpus directly
- what the system synthesized
- what is interpretive or inferential
- what to do if the system is wrong

### 5. Big systems need stable page grammar

Each page should answer quickly:
- what am I doing here?
- what kind of page is this?
- what is the first action?
- where can I inspect evidence?
- what is the next likely move?

### 6. Result display needs a dual form

For research outputs, the panel recommends:
- thoughtful science-writer prose
- structured results tables
- article figures/tables or rewritten explanatory captions where helpful

This avoids forcing the user to choose between readability and inspectability.

### 7. Theory should be explicit but disciplined

The UI should surface theory frames, but should not pretend weak theory attachment is strong theory fidelity.
Theory views should distinguish:
- paper terms
- canonical theories
- theory role
- theory confidence / fidelity

### 8. The visual language should remain human and serious

The panel rejects two extremes:
- dry enterprise gray
- toy-like over-animation

The target is:
- deliberate
- contemporary
- warm
- legible
- rigorous

## Practical recommendations

1. Make Streamlit the default implementation target for interactive internal tools.
2. Keep static HTML for lightweight public/course/demo surfaces when it is the simpler choice.
3. Require a framework-choice rationale in every serious design proposal.
4. Require an AI behavior contract for every AI-assisted page.
5. Require a results display strategy for every evidence-heavy page.
6. Require a theory display strategy where theory is surfaced.
7. Run a local contract checker before calling a page complete.

## Bottom line

There was already a good GUI-design lineage.
What was missing was:
- a canonical repo-local spec
- Streamlit-first policy
- current AI-UI guidance
- a repeatable repair/check loop

This panel review supports that consolidation.
