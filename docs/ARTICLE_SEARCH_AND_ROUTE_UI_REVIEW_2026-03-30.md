# Article Search And Route UI Review

Scope: product-design review only for [ka_article_search.html](/Users/davidusa/REPOS/Knowledge_Atlas/ka_article_search.html), [ka_user_home.html](/Users/davidusa/REPOS/Knowledge_Atlas/ka_user_home.html), and [ka_workflow_hub.html](/Users/davidusa/REPOS/Knowledge_Atlas/ka_workflow_hub.html). Focus: make article search easier to understand, make search modes visually legible, make objective routes feel like journeys rather than utilities, and keep the work achievable in the current HTML/CSS/JS stack.

## 1. Main Judgment

The underlying product logic is sound. Atlas already has a curated paper-search page, a role-based objective-path chooser, and a guided route view with saved progress. The weakness is continuity.

[ka_article_search.html](/Users/davidusa/REPOS/Knowledge_Atlas/ka_article_search.html) uses a warm editorial visual language, while [ka_user_home.html](/Users/davidusa/REPOS/Knowledge_Atlas/ka_user_home.html) and [ka_workflow_hub.html](/Users/davidusa/REPOS/Knowledge_Atlas/ka_workflow_hub.html) use a blue application shell. When a route sends the user into Article Search, the experience feels like a jump into a different product. The route loses force at exactly the point where it should feel most useful.

The right move is not a framework migration. It is a stricter shared surface: one route vocabulary, one clearer search model, and one thin layer of shared framing across these pages.

## 2. Article Search: Make The Page Self-Explanatory

Current strength:
- The page already has the right search primitives: construct, instrument or sensor, and combined search.
- The result cards already contain enough information to support useful scanning.

Current problem:
- The page asks the user to choose a mode before making the difference among the modes visually obvious.
- The corpus boundary is too quiet. A first-time user can still read the page as though it were a general web-search tool.
- Measurement language shifts among `instrument`, `sensor`, `signal`, and `measuring instrument`.
- Data-status language is tied too closely to empty-state messaging rather than shown as a persistent page condition.
- The result cards still feel metadata-heavy before they feel intelligible.

Implementation direction:
- Put a compact status strip directly under the hero or mode selector: `Searching Atlas paper corpus` or `Local fallback only`.
- Reframe the chooser from `Search by ...` to `What do you know?`
- Add a plain-language query summary above results: `24 papers for Stress measured with EDA`.
- Keep one measurement phrase visible across the page. `Instrument or sensor` is the safest choice.
- Strengthen the card reading order so it answers, in sequence: what the paper is about, how it measured the question, and whether it is worth opening. The tag cloud should support that order, not compete with it.

Expected result:
- A first-time user can tell what this page searches, what each mode does, and what kind of result set to expect before searching.

## 3. Search Modes: Make The Differences Visible, Not Merely Stated

Current problem:
- The three modes share nearly the same layout, button treatment, and hierarchy.
- The active tab changes colour, but the active panel itself does not feel materially different.
- `Construct + Instrument` is conceptually blurred because the UI says "both" while the logic still allows one field to be blank and broadens the search.
- Quick-select chips compete visually with the mode choice rather than serving it.

Implementation direction:
- Treat each mode as a small search card with four visible cues:
  - mode name
  - best-use sentence
  - example inputs
  - expected result type
- Tint the active panel, not just the tab. A light mode-specific background or top border is enough.
- Make the search button label reflect the mode: `Find papers by construct`, `Find papers by instrument`, `Find matching papers`.
- Either require both fields in `Construct + Instrument`, or relabel that mode to `Combine filters`. At present the label promises more specificity than the behaviour enforces.
- Keep quick-select chips only for the active mode and relabel them `Popular starting points`.

Expected result:
- The user understands, by sight, which mode is broad, which is measurement-led, and which is the narrowest.

## 4. Objective Routes: Make Them Feel Like Paths With A Destination

Current strength:
- The route data in [ka_workflows.js](/Users/davidusa/REPOS/Knowledge_Atlas/ka_workflows.js) is already good. Titles, objectives, step order, and estimated time are strong enough to support a guided experience.
- Resume and progress persistence are already useful.

Current problem:
- The chooser page still reads partly as a dashboard of utilities.
- The route page still uses `workflow` language in visible places, which sounds operational rather than guided.
- The route hero states the objective, but it does not show the arc of the route.
- When a route opens Article Search, there is no visible cue that the user is still inside a larger path.

Implementation direction:
- Use one user-facing model consistently: `Objective paths` on the chooser page, `recommended route` inside a chosen path, and no `workflow` in visible UI labels.
- On each path card, show three journey anchors: where the path starts, what the user leaves with, and how long it takes.
- Keep whole-card click if desired, but add an explicit primary CTA so entering a path feels deliberate.
- In the route hub, replace decorative placeholder imagery with a simple step map or stage ribbon built from the existing `wf.steps` data.
- Rename the most mechanical labels where useful: `Start this path`, `Next stop`, `Return to path`, `Route complete`.
- If the user enters [ka_article_search.html](/Users/davidusa/REPOS/Knowledge_Atlas/ka_article_search.html) from a route, show a small route banner with the route title, current step, and a return link.

Expected result:
- Atlas feels like it is taking the user through a sequence with a beginning, middle, and end, rather than sending them to disconnected tools.

## 5. Achievable Without Migration

These changes fit the current stack. They require HTML restructuring, shared CSS tokens, tighter microcopy, and small vanilla-JS state cues. They do not require React, a design-system rebuild, or a route-engine rewrite.

Recommended order:
1. Unify visible vocabulary and top-of-page framing across the three pages.
2. Make search-mode semantics honest and visually distinct.
3. Add a persistent data-status strip and plain-language query summary to Article Search.
4. Use existing workflow data to render a clearer route arc on home and hub.
5. Add route-context cues when a guided route hands off to Article Search.

That sequence would remove most of the current confusion without changing the underlying architecture.
