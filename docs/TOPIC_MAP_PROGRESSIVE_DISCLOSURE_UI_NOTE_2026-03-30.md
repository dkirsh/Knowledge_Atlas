# Topic Map Progressive Disclosure UI Note

Date: 2026-03-30
Scope: concept review only for progressive disclosure on the topic map

## Core judgment

The current page already explains the defended layer clearly: it shows only papers whose placement is stable enough to defend, and it reports the hidden remainder as `Hidden pending repair`.

What is missing is a user-facing disclosure control that distinguishes:

- the public, stable map
- the broader but provisional working map
- the hidden repair queue

## Recommended labels

Use one control label: `Map view`

Use these visible options:

- `Defended map`
  Helper copy: `Public view. Only topic placements stable enough to defend.`
- `Working map`
  Helper copy: `Broader working view. Includes provisional placements still under review.`
- `Hidden pending repair`
  Helper copy: `Papers withheld from the map until topic repair is complete.`

## Control recommendation

Do not make all three states look equivalent.

Use:

- a two-option segmented control for `Defended map` and `Working map`
- a separate adjacent button or drawer trigger for `Hidden pending repair (N)`

Recommended pattern:

`Map view: [Defended map] [Working map]   [Hidden pending repair: 75]`

This is clearer because `Hidden pending repair` is not really a map view. It is an omitted set that the user may inspect.

## Why this matters

`Expanded working map` is conceptually right, but too long and slightly awkward as a control label. Use `Working map` in the UI, and explain in helper text that it is the expanded, provisional view.

`Hidden pending repair` works well as a status phrase and drawer title. It should not be reduced to vague labels such as `Show more`, `Include hidden`, or `Expand`, because those labels hide the epistemic distinction between defended material and provisional or withheld material.

## Interaction rule

Default to `Defended map`.

When the user switches to `Working map`, show one short status line such as:

`You are viewing provisional topic placements that are still under review.`

When the user opens `Hidden pending repair`, show the queue in a side panel or secondary list, not as if it were simply another layer of the same map.
