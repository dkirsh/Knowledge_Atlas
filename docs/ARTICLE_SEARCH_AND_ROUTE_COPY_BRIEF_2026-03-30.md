# Article Search And Route Copy Brief

Scope: wording and explanatory text only for:
- `/Users/davidusa/REPOS/Knowledge_Atlas/ka_article_search.html`
- `/Users/davidusa/REPOS/Knowledge_Atlas/ka_user_home.html`
- `/Users/davidusa/REPOS/Knowledge_Atlas/ka_workflow_hub.html`

Objective: make article search understandable before first use, keep route language consistent, state live versus local status plainly, and make result cards easier to scan.

## Cross-Page Copy Rules

1. Use `objective path` on the home page and `recommended route` inside a chosen path.

2. Use `instrument or sensor` as the main measurement phrase. Do not alternate among `signal`, `measuring instrument`, and `sensor family` in the same block unless one term is being defined.

3. Say `Atlas paper corpus`, `live Atlas data`, and `local fallback data`. Avoid internal phrases such as `payload`, `rebuild-backed`, `front-backed`, and `gold registry`.

4. Say directly that Article Search looks inside Atlas, not the open web.

## Recommended Copy

### 1. Search Modes

Use this explainer under the mode tabs:

`Use Construct to explore a topic or question area. Use Instrument or Sensor to find papers by how the construct was measured. Use Construct + Instrument to find the most specific set of papers.`

Use these field hints:

- Construct: `Find papers in the Atlas corpus tagged to this construct.`
- Instrument or Sensor: `Find papers in the Atlas corpus that use this instrument or sensor family.`
- Construct + Instrument: `Find papers that match both the construct and the instrument or sensor. Leave one field blank only if you want a broader set.`

Use this idle prompt above the results area:

`Choose a construct, an instrument or sensor, or both, then select Search. Atlas searches its own paper corpus, not the open web.`

Use this no-results message:

`No papers matched this search. Remove one filter or switch to a broader search mode.`

### 2. Route Guidance

Use this guidance block on `ka_user_home.html`:

`Choose an objective path if you want a recommended sequence through Atlas. Each path suggests a sensible page order. You may leave the path at any time and browse freely. Atlas will remember your place.`

Recommended chips:
- `Choose an objective path`
- `Follow Next / Back`
- `Browse freely`
- `Resume later`

Use this note on `ka_workflow_hub.html`:

`This is a recommended route, not a requirement. Use Next and Previous if you want a guided sequence. You may open other Atlas pages at any time, and your place in this route will still be remembered.`

If Article Search gets a route-entry cue, use:

`You reached Article Search from a recommended route. Search here, then return to the route when you are ready.`

### 3. Live Vs Local Data Status

Put a short status line near the search controls, not only inside the empty state.

Use this live-data message:

`Data status: Live Atlas data loaded. Search includes the current Atlas paper corpus and available instrument and sensor terms.`

Use this local fallback message:

`Data status: Local fallback only. This page was opened from disk, so the browser could not load live Atlas data. Serve Atlas over HTTP to search the live paper corpus.`

If a shorter local variant is needed:

`You are viewing local fallback data because this page was opened from disk rather than through the Atlas server.`

If topic labels need explanation, use:

`When Atlas has topic data for a paper, its main topic appears first in the result card.`

### 4. Result-Card Wording

Use these result-count patterns:

- Default: `24 papers found`
- Construct only: `24 papers for Stress`
- Instrument only: `24 papers using EEG`
- Both: `24 papers for Stress measured with EEG`

Add this helper line above the card list if the click-to-expand behavior remains:

`Click a card to expand the abstract.`

Prefer these labels and terms:

- `Main topic` rather than `Primary topic`
- `Challenges` rather than `Attacks`
- `Supports`
- `DOI`
- `Study type`

Replace `Sensor profile` with:

`Sensors used`

Use this fallback abstract line:

`Abstract not yet available for this paper record.`

Card intent:

`Each result card should answer, in order: what the paper is about, how it measured the question, and whether it is worth opening.`

## Tone Standard

The copy should sound calm, public-facing, and definite. Atlas may admit that a page is in fallback mode, but it should never describe that state in internal pipeline language.
