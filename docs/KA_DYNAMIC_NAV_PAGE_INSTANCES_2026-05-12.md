# KA Dynamic Nav Page Instances

These pages are actual KA-site HTML pages, not Streamlit sketches. They use the shared `ka_dynamic_pages.js` renderer, `ka_dynamic_pages.css`, the canonical navbar, and live JSON payloads under `data/ka_payloads`.

## Pages

- `ka_dynamic_topics.html` - browse-oriented topic entry page.
- `ka_dynamic_theories.html` - theory lattice and warrant page.
- `ka_dynamic_mechanisms.html` - mechanism chain page.
- `ka_dynamic_neural.html` - plausible neural underpinnings page.
- `ka_dynamic_papers.html` - paper destination page.
- `ka_dynamic_evidence.html` - evidence and warrant inspection page.
- `ka_dynamic_argumentation.html` - challenge and Toulmin-style argumentation page.
- `ka_dynamic_search.html` - mixed search-result page with browsing pivots.

## Shared Interaction Pattern

Each page has:

- a page-specific narrative spine;
- search across the relevant payload;
- user-journey lens selection;
- evidence and novelty sliders;
- taxonomy lane filtering;
- Did You Know entry card;
- selectable result cards;
- a sticky detail panel with warrant language, representative papers, related theories or lenses, and next moves.

The point is to evaluate page layout and information design before replacing production pages. The current implementation deliberately keeps the pages separate from the existing canonical URLs so the older pages remain available for comparison.

## Local Review URL

When served from the KA repo root, use:

`http://localhost:8777/ka_dynamic_topics.html`

Then substitute the page filename above.
