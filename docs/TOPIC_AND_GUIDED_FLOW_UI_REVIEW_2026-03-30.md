# Topic And Guided Flow UI Review

Scope: product-design and information-architecture review only for [ka_user_home.html](/Users/davidusa/REPOS/Knowledge_Atlas/ka_user_home.html), [ka_topics.html](/Users/davidusa/REPOS/Knowledge_Atlas/ka_topics.html), [ka_topic_hierarchy.html](/Users/davidusa/REPOS/Knowledge_Atlas/ka_topic_hierarchy.html), and [ka_workflow_hub.html](/Users/davidusa/REPOS/Knowledge_Atlas/ka_workflow_hub.html), with minimal-note implications for [ka_article_search.html](/Users/davidusa/REPOS/Knowledge_Atlas/ka_article_search.html).

## 1. User-Home Objective Paths

Current strength:
- The home page already understands the right model: users choose an objective, follow a recommended sequence, and may browse freely.
- The workflow hub already says, correctly, that the path is recommended rather than compulsory.

Current problem:
- The home page still presents the path system partly as "workflows" and partly as "objective paths". The idea is right, but the naming is not yet singular.
- The cards look like task options, but not yet like distinct journeys with a beginning, middle, and end.

Implementation direction:
- Make "Objective Paths" the single phrase everywhere. Remove "workflow" from user-facing labels except where it is strictly internal.
- Treat each path card as a compact journey card with five visible elements:
  - objective
  - who this path is for
  - expected outcome
  - number of steps and estimated time
  - first page in the sequence
- Keep the existing guidance block, but sharpen its visual hierarchy:
  - one short rule sentence
  - one sentence on freedom to browse
  - three chips only: `Choose an objective`, `Follow Next / Back`, `Browse freely anytime`
- On the user home, the primary visual action should be `Start this path`, not merely the card itself.

Expected result:
- The page reads less like a dashboard of tools and more like a set of intelligible routes through the site.

## 2. Topic Hierarchy: Authority, Provenance, Coverage

Current strength:
- [ka_topic_hierarchy.html](/Users/davidusa/REPOS/Knowledge_Atlas/ka_topic_hierarchy.html) already says that research fronts are overlays, not the base taxonomy.
- It already surfaces hidden-paper counts, which is the correct instinct.

Current problem:
- Provenance is present, but still reads like a technical aside rather than a first-class truth-condition for the page.
- Visible and hidden coverage is stated, but not framed as a trust contract with the user.

Implementation direction:
- Treat provenance as a compact "data status" strip directly under the hero, with four explicit fields:
  - `Base topic authority`
  - `Research-front overlay source`
  - `Visible papers`
  - `Hidden pending repair`
- Phrase the hidden set positively and plainly:
  - not "missing"
  - rather "withheld from the map until IV/DV repair is complete"
- Add one sentence defining the page's epistemic rule:
  - "This map shows only papers whose topic placement is stable enough to defend."
- Distinguish three states visually:
  - canonical authority
  - provisional / heuristic authority
  - local-file fallback

Expected result:
- Users understand what the map is, what it is not, and why some papers are intentionally absent.

## 3. Research Fronts As Overlay, Not Taxonomy

Current strength:
- The code and copy already point in the right direction: research fronts are narrower than full topic coverage.

Current problem:
- On the topics side, fronts still risk being read as if they are the topic system itself.
- On the hierarchy side, fronts are listed as another tag row, which weakens the conceptual distinction.

Implementation direction:
- Define a research front, in visible UI language, as:
  - "a tighter active line of inquiry that sits on top of the broader topic map"
- Visually separate fronts from topic structure:
  - topic structure = tree and graph skeleton
  - research front = tinted overlay, halo, or front badge layer
- Every front mention should answer three questions:
  - what broader topic area it sits inside
  - how many papers it covers
  - what makes it a front rather than just a topic
- In topic cards and hierarchy detail panels, front language should read as:
  - `This topic participates in 2 research fronts`
  - not `This topic is a research front`

Expected result:
- Users can hold two ideas at once: the taxonomy is the map; fronts are active concentrations on that map.

## 4. Minimal Moves To Reduce Confusion On Topic And Article Pages

### ka_topics.html

Primary issue:
- The page mixes three concepts without enough separation:
  - broad topic browsing
  - research-front browsing
  - VOI-based prioritisation

Minimal UI moves:
- Rename the hero promise from generic "topic clusters" to `topic areas and active fronts`.
- Replace the current mode note with a two-part status sentence:
  - corpus coverage
  - front coverage
- Add one short explainer above the tabs:
  - `Browse the broad map below. Research fronts are the denser, more active subset.`
- Rename `What's New` to `Emerging Fronts` if that tab is in fact front-oriented.

### ka_article_search.html

Primary issue:
- The page asks the user to choose among three search modes before telling them which mode is appropriate for which question.
- It also bundles construct search, instrument search, and sensor-family search into one visual tier.

Minimal UI moves:
- Add a one-line chooser under the search-mode tabs:
  - `Use Construct to explore a question area, Instrument/Sensor to find measurement families, and Both to find precise study sets.`
- Relabel `Both Together` to `Construct + Instrument` for directness.
- Merge `instrument` and `sensor` in the visible vocabulary everywhere, since that is how the page actually behaves.
- Put the current data-status sentence near the search controls, not only in the empty/prompt area.
- In results, promote `Primary topic` above the tag cloud so the page answers "what is this paper about?" before "what metadata does it carry?"

Expected result:
- Users can tell, before searching, what kind of query each mode serves and what sort of answer the page will return.

## 5. Recommended Sequence

If only a small amount of UI work is possible now, do these in order:
1. Unify all user-facing language to `Objective Paths`.
2. Add a clear provenance-and-coverage strip to the hierarchy page.
3. Reword topic/front copy so fronts are consistently described as overlays.
4. Clarify the search-mode purpose on [ka_article_search.html](/Users/davidusa/REPOS/Knowledge_Atlas/ka_article_search.html).

This would produce a cleaner system without changing the underlying architecture.
