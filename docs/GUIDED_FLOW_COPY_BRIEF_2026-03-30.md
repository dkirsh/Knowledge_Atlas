# Guided Flow Copy Brief

Scope: wording and explanatory text only for:
- `/Users/davidusa/REPOS/Knowledge_Atlas/ka_user_home.html`
- `/Users/davidusa/REPOS/Knowledge_Atlas/ka_topics.html`
- `/Users/davidusa/REPOS/Knowledge_Atlas/ka_topic_hierarchy.html`
- `/Users/davidusa/REPOS/Knowledge_Atlas/ka_workflow_hub.html`

Objective: make the guided-flow logic plain, make topic authority and research-front status intelligible, and remove insider phrasing around fallback modes, hidden papers, and repair queues.

## Cross-Page Copy Rules

1. Say the same thing everywhere about navigation:
   `These are recommended paths, not required routes. You may browse freely from the navigation bar at any time.`

2. Keep topic authority distinct from research fronts:
   `The topic hierarchy is the base map. Research fronts are narrower overlays on top of that map.`

3. Replace internal or procedural language with user language:
   - Avoid: `prototype`, `stronger canonical ontology arrives`, `dominant IV or DV assignment`
   - Prefer: `current topic export`, `base map`, `hidden until topic assignment is repaired`

4. When the page is not live, say so directly:
   `You are viewing local demo data because this page was opened from disk rather than through the Atlas server.`

5. Use `papers`, not `articles assigned`, unless the page is specifically about article records.

## Page-Specific Recommendations

### 1. `ka_user_home.html`

Current intent is good, but the tone can be plainer and more assured.

Use this text for the guidance block:

`Choose an objective below if you want a recommended route through Atlas. Each route gives you a sensible page order and a Next/Back rhythm. You may leave the route at any time and browse freely from the navigation bar. Atlas will remember where you were.`

Recommended heading:

`How to use Atlas`

Recommended chips:
- `Choose an objective`
- `Follow the suggested route`
- `Browse freely`
- `Resume later`

If the role-specific welcome sentence needs tightening, prefer:

`This home page gives you recommended objective paths for your role. Use them when you want guidance; ignore them when you want to explore directly.`

### 2. `ka_workflow_hub.html`

The existing note is nearly right, but `not a cage` is too colloquial.

Use this text for the workflow hero note:

`This is a recommended route, not a requirement. Use Next and Previous if you want a guided sequence. You may open other Atlas pages at any time, and your place in this route will still be remembered.`

If a shorter variant is needed:

`Recommended route. Free browsing allowed. Your place will be saved.`

### 3. `ka_topics.html`

This page needs the clearest distinction between topic map and research fronts.

Replace the key explanatory sentence with this:

`These cards show live research fronts: tighter clusters of papers that share a topic, theory, or method strongly enough to count as an active line of work. They help you enter the corpus quickly, but they do not cover the whole topic map.`

Use this follow-on sentence:

`For full topic coverage, use the Topic Map. Research fronts are overlays on that broader map, not the map itself.`

For the live coverage note, use:

`Live research fronts currently cover X of Y papers. The remaining papers still appear through the broader Topic Map and per-paper topic assignments.`

For local-file fallback mode, use:

`You are viewing a local demo set because this page was opened from disk rather than through the Atlas server. Serve Atlas over HTTP to load the live corpus.`

Avoid:
- `front coverage is still narrower than full paper coverage`
- `research-front artifact`

Prefer:
- `research fronts cover only part of the corpus`
- `live research-front data`

### 4. `ka_topic_hierarchy.html`

This page needs the plainest authority wording.

Use this text for the authority card:

`Authority: this view uses the current topic-hierarchy export as its base map. Research fronts are shown separately as overlays. They highlight especially active clusters, but they are not the main taxonomy.`

If the canonical-source distinction must be preserved, use:

`Authority: this view uses the current topic export. When a newer canonical topic export is available, Atlas will use it automatically. Research fronts remain overlays rather than the base taxonomy.`

For hidden papers, replace the current sentence with:

`X papers are hidden from this view until their topic assignment is repaired.`

If a slightly fuller version is needed:

`X papers are temporarily hidden because their topic assignment is not yet reliable enough for public display.`

For the file-mode warning, use:

`This page expects live Atlas data. If you opened it as file:// rather than through the Atlas server, the browser may block the data files and the view will not match the live corpus.`

For the hierarchy explainer, prefer:

`Start with the compact hierarchy at the top. Then select a topic to see its nearby topics, shared outcome families, and supporting papers.`

## Recommended Label Changes

Prefer these shorter labels and microcopy where possible:

- `How To Use This Workspace` -> `How to use Atlas`
- `Recommended Objective Paths` -> `Recommended paths`
- `Hierarchy Strip` -> `Topic hierarchy`
- `Articles assigned` -> `Papers shown`
- `Fallback IV papers` -> `Hidden pending repair`
- `Topic hierarchy and relation map` -> `Topic hierarchy and relation map`
  Note: title is acceptable; the subtitle should do the explanatory work.
- `Most Active` -> `Most studied`
  Note: only if the product team wants plainer user-facing language.
- `Research Priorities` -> `Best next questions`
  Note: use only if that tab is meant to be more user-facing than internal.

## Preferred Definitions

Use these stable definitions across pages.

`Topic hierarchy`
: The base map of the corpus. It organizes papers by topic relations.

`Research front`
: A tighter cluster within the topic map: papers that share a topic, theory, or method strongly enough to count as an active line of work.

`Hidden pending repair`
: Papers that are excluded from a public view until their topic assignment is reliable enough to show.

`Local demo mode`
: A fallback state used when the page is opened from disk and cannot load live Atlas data.

## Tone Standard

The right tone is calm, direct, and public-facing. The pages should sound as though Atlas knows what it is doing, while still admitting where a view is partial, provisional, or in fallback mode.
