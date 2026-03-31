# Topic Map Progressive-Disclosure Copy Note

Review scope: user-facing wording only in `ka_topic_hierarchy.html`.

## What the current page already does

- The page already states the rule of the strict map clearly: only papers with topic placement "stable enough to defend" are shown (`ka_topic_hierarchy.html:336`, `ka_topic_hierarchy.html:435`).
- The hidden state is visible in both the stat label and the explanatory note (`ka_topic_hierarchy.html:309`, `ka_topic_hierarchy.html:423-434`).
- I do not see a separate user-facing label yet for an expanded working-map state in this file.

## Recommendation

Use three plain labels, each with one short sentence beneath it.

- `High-confidence map`
  "This is the main map. It shows papers whose topic placement has been checked enough to trust."
- `Expanded working map`
  "This view includes likely topic placements that are still being checked. Use it to explore patterns, not to count settled coverage."
- `Hidden until reviewed`
  "These papers are kept out of the main map until their topic assignment is fixed."

## Rationale

- `High-confidence map` is plainer than "stable enough to defend" as a label. The stronger phrase can remain as secondary explanatory copy.
- `Expanded working map` names the provisional state plainly without implying that it is unreliable or unusable.
- `Hidden pending repair` sounds internal. `Hidden until reviewed` is easier for users to grasp at a glance, while still being honest about why the papers are absent.

In short: the disclosure ladder should read as trusted, broader but provisional, and temporarily withheld.
