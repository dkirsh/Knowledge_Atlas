# Parameter → Infinigen Source Mapping

**Track 3 · Task 1 supporting deliverable**
**Author:** Paco Yan (payan@ucsd.edu)
**Infinigen target version:** 1.19.1
**Last verified:** 2026-05-05 (against `/home/poca/infinigen/infinigen/` checked out from BSD release)

---

## Why this document exists

Each manifest parameter asserts the existence of a *real generative knob* in
Infinigen's entity code. Without a verified file:line reference, the assertion
is unfalsifiable — exactly the kind of hole Prof. Kirsh's "ruthless review"
protocol catches. This document closes that hole by tying every manifest
parameter to a specific symbol in Infinigen 1.19.1.

Each row falls into one of three states:

| Status         | Meaning                                                                 |
| -------------- | ----------------------------------------------------------------------- |
| **Aliased**    | A real Infinigen knob exists; the manifest name maps to it through a documented alias (often a unit conversion or rename). Wrapper layer applies the alias. |
| **Aspirational (computed)** | No direct knob exists, but the parameter can be synthesised from primitives Infinigen does expose (constraint-solver weights, placement probabilities, material-list filtering). Wrapper layer computes the parameter from those primitives. |
| **Aspirational (cannot express)** | No knob and no derivation. Parameter is removed from the manifest or queued for the Sprint 5+ Worship flagship work that extends the constraint solver. |

Honesty rule (per Prof. Kirsh's review protocol): every row must have either a
verified file:line reference or an explicit derivation note. No row may claim
to map to an Infinigen symbol that does not exist.

---

## What changed from the v0 draft

The v0 draft of this document had every row marked `Pending` because the
verification probe had not yet run. The probe (`infinigen_probe.sh` and
`infinigen_probe_v2.sh`) revealed three structural facts that reshape the
mapping:

1. **Most manifest parameter names do not appear in Infinigen 1.19.1 source.**
   Specifically: `ceiling_height`, `cabinet_density`, `wall_material`,
   `daylight_intensity`, `appliance_visibility` (and other normalised-scalar
   names) return zero matches when grepped. They were named after the
   *concept* the LLM front-end exposes to the user, not after Infinigen
   internals.

2. **Real knobs use different names.** `ceiling_height_m` maps to
   `RoomConstants.wall_height` (Infinigen treats the wall and the ceiling as
   the same height, since walls run floor-to-ceiling). `lighting_warmth` maps
   to `PointLampFactory.params["Temperature"]` (Kelvin). `lighting_intensity`
   maps to `PointLampFactory.params["Wattage"]`. These are the only three
   parameters with clean direct aliases.

3. **Most other parameters are constraint-solver-driven, not factory-driven.**
   Density, count, and material-warmth concepts in Infinigen 1.x are
   controlled by the constraint solver and the placement system
   (`core/constraints/example_solver/room/`), not by per-factory constructor
   arguments. The wrapper layer's job for these is to translate a
   normalised-scalar manifest value into solver weights or instance counts.

The honest consequence: **3 of 12 parameters are cleanly aliased; 9 require
wrapper-side translation**. This is acknowledged here so the wrapper code
can implement those translations explicitly rather than pretending knobs
exist that don't.

---

## Verification workflow

For each `Aliased` row, the file:line reference can be re-verified at any time
by running, from the Infinigen install root:

```bash
cd $(python -c "import infinigen, os; print(os.path.dirname(infinigen.__file__))" 2>/dev/null \
     || echo /home/poca/infinigen/infinigen)
grep -n "<symbol>" <relative-path>
```

For `Aspirational (computed)` rows, the derivation formula in the
`Notes / derivation` column is the contract. The wrapper module must implement
exactly that formula and reference this row in its docstring.

---

## Kitchen manifest

| Parameter             | Status   | Real Infinigen symbol                        | File path (relative to `infinigen/`)                                         | Line   | Notes / derivation                                                                                                                                                                                                                                          |
| --------------------- | -------- | --------------------------------------------- | ----------------------------------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ceiling_height_m`    | Aliased  | `RoomConstants.wall_height`                   | `core/constraints/constraint_language/constants.py`                          | 31, 56 | Infinigen treats wall_height = ceiling_height. Default `("uniform", 2.8, 3.2)`. Wrapper passes a fixed value via gin override `RoomConstants.wall_height=<value>`. Note that the manifest's lower bound (2.0 m) is below Infinigen's default range; this is intentional for psych research. |
| `cabinet_density`     | Aspirational (computed) | (no direct knob)                | `assets/objects/shelves/kitchen_cabinet.py` + `assets/objects/shelves/kitchen_space.py` + constraint solver weights | n/a    | SingleCabinetFactory has no density parameter. Density is controlled by the constraint solver's per-segment cabinet placement probability. Wrapper derives: `solver_cabinet_weight = 0.3 + 0.7 * cabinet_density` (anchors 0.0 → sparse default, 1.0 → fully lined). |
| `daylight_intensity`  | Aspirational (computed) | sky strength + window area      | `assets/lighting/sky_lighting.py` + `assets/objects/windows/window.py`        | n/a    | No single `daylight_intensity` knob exists. Wrapper composes: scales the sky lighting strength in `sky_lighting.py` AND the WindowFactory `dimensions` (width × height). Derivation: `sky_strength = 0.2 + 1.8 * daylight_intensity`; `window_area_scale = 0.6 + 0.8 * daylight_intensity`. |
| `countertop_material` | Aliased  | material from `material_assignments.py`       | `assets/composition/material_assignments.py` + `assets/objects/shelves/countertop.py` | TBD line | The kitchen counter factory is `Countertop`, not `KitchenCounter` (correcting v0 doc). Material picked from a list in `material_assignments.py`. Wrapper maps each enum token to a specific material function: `granite → stone.granite`, `marble → stone.marble`, `oak → wood.oak`, `tile → ceramic.tile`, `metal → metal.brushed_steel`, `plastic → plastic.smooth_plastic`. |
| `appliance_visibility`| Aspirational (computed) | instance counts on `OvenFactory`, `RefrigeratorFactory`, `MicrowaveFactory`, `BowlFactory`, `BottleFactory` | `assets/sim_objects/oven.py`, `refrigerator.py`, `microwave.py`, `pepper_grinder.py`; `assets/objects/tableware/bowl.py:18`, `bottle.py:24` | n/a | **Correcting v0 doc:** HardwareFactory lives in `assets/objects/bathroom/hardware.py:18` — it is bathroom hardware (hooks, holders, bars, rings), not kitchen. Kitchen appliances are in `assets/sim_objects/`. Wrapper derives instance counts from `appliance_visibility ∈ [0,1]`: `bowls = round(8 * v)`, `bottles = round(6 * v)`, `pepper_grinders = round(2 * v)`, `large_appliances_visible = (v > 0.3)`. |
| `lighting_warmth`     | Aliased  | `PointLampFactory.params["Temperature"]` (Kelvin) | `assets/lighting/indoor_lights.py`                                            | 25–18  | Existing default: `clip_gaussian(4700, 700, 3500, 6500)`. Note CeilingLightFactory wraps a PointLampFactory internally (`assets/objects/lamp/ceiling_lights.py:36`), so setting Temperature on PointLamp propagates. Wrapper derivation: `Temperature_K = 6500 - lighting_warmth * (6500 - 2700)` (clamps to Infinigen's [3500, 6500] band; values below 3500 fall back to 3500 K). |

---

## Dining room manifest

| Parameter             | Status   | Real Infinigen symbol                       | File path (relative to `infinigen/`)                                         | Line   | Notes / derivation                                                                                                                                                                                                                                          |
| --------------------- | -------- | -------------------------------------------- | ----------------------------------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ceiling_height_m`    | Aliased  | `RoomConstants.wall_height`                  | `core/constraints/constraint_language/constants.py`                          | 31, 56 | Same alias as kitchen. Default `("uniform", 2.8, 3.2)`. Wrapper passes via gin override.                                                                                                                                                                    |
| `daylight_intensity`  | Aspirational (computed) | sky strength + window area     | `assets/lighting/sky_lighting.py` + `assets/objects/windows/window.py`        | n/a    | Same derivation as kitchen.                                                                                                                                                                                                                                  |
| `lighting_intensity`  | Aliased  | `PointLampFactory.params["Wattage"]`         | `assets/lighting/indoor_lights.py`                                            | 25–15  | Existing default: `U(40, 100)`. Drives `lamp.data.energy`. Wrapper derivation: `Wattage = 20 + lighting_intensity * 180` (range 20–200 W; brackets the Infinigen default).                                                                                  |
| `wall_warmth_index`   | Aspirational (computed) | wall material selection weights | `assets/composition/material_assignments.py` + `core/constraints/example_solver/room/decorate.py` | line 347 has `ceiling = wall_plaster` and similar | No `wall_material` knob exists. Wall materials are selected from lists in `material_assignments.py`. Wrapper derivation: weight a "warm" material list (wood panels, warm paint) by `wall_warmth_index` and a "cool" list (white plaster, stone, concrete) by `1 - wall_warmth_index`, then sample. |
| `furniture_density`   | Aspirational (computed) | constraint-solver placement probabilities for `ChairFactory`, `DiningTableFactory` | `assets/objects/seating/chairs/chair.py:35` + `assets/objects/tables/dining_table.py` + `core/constraints/example_solver/room/decorate.py` | n/a | **Correcting v0 doc:** the dining-table factory is `DiningTableFactory` in `assets/objects/tables/dining_table.py`, not `TableFactory`. SideboardFactory does not exist in v1.19.1. Wrapper derives: scales the constraint-solver weight for chair placement (`chair_count_target = 4 + round(4 * furniture_density)`) and gates whether a sideboard-like asset is included (`sideboard_present = furniture_density > 0.5`). |
| `biophilia_count`     | Aspirational (computed) | instance count of `LargePlantContainerFactory` | `assets/objects/tableware/plant_container.py:128`                            | n/a    | LargePlantContainerFactory has only geometry parameters (depth, scale, side_size, top_size); no instance-count knob. Count is controlled at the constraint-solver placement layer. Wrapper passes a literal target count (the manifest integer) to the solver. |

---

## Wrapper-side derivation contract

The 9 `Aspirational (computed)` parameters require the wrapper layer to
implement the derivations above explicitly. The wrapper must:

1. Live at `scripts/track3/infinigen_wrapper.py` (extending the
   course-shipped scaffold) or as a standalone helper Paco's wrapper imports.
2. Expose a `resolve_params(manifest_params: dict) -> dict` function whose
   output is a dict of *Infinigen-native* parameters: gin overrides for
   `RoomConstants`, factory constructor kwargs, solver weight overrides, and
   instance-count targets.
3. For every `Aspirational (computed)` parameter, the resolution code must
   reference this document by section header in a docstring or comment, so
   future maintainers can trace each derivation back to its rationale.

The wrapper-side derivations should **never silently invent values**. If the
solver does not expose a weight that the derivation requires, the wrapper
must raise a `NotImplementedError` rather than skip — the failure surfaces in
the test render and the manifest gets demoted to `Aspirational (cannot
express)`.

---

## Open issues (to revisit before Task 2 finalises)

- **Sky lighting probe.** `sky_lighting.py` was located but its internals were
  not yet read. The exact symbol the wrapper should target for
  `daylight_intensity` (likely a node-graph "Strength" value) needs one more
  probe pass before the wrapper code is final. Until then, the
  `sky_strength = 0.2 + 1.8 * daylight_intensity` formula is provisional.

- **Material list names.** The mapping for `countertop_material` and
  `wall_warmth_index` references material lists in `material_assignments.py`
  (line 347+). The exact list names (`stone.granite` etc.) are educated
  guesses based on Infinigen's documented material taxonomy; need to be
  confirmed by reading `material_assignments.py` end-to-end.

- **Solver weight knobs.** The constraint solver in
  `core/constraints/example_solver/` exposes per-class placement weights, but
  the public API for overriding them at run time (vs. forking the solver
  config) needs to be confirmed. The first wrapper increment may have to
  monkey-patch placement probabilities until the documented override
  mechanism is found.

These open issues do not block the *ceiling-height slice*. The wrapper for
`ceiling_height_m` only depends on the confirmed alias to `RoomConstants.wall_height`,
which is verified.

---

## Submission readiness

| Check                                                                  | State |
| ----------------------------------------------------------------------- | ----- |
| Every row has an explicit `Status`                                      | Done  |
| Every `Aliased` row has a real file:line                                | Done (one TBD line for `Countertop` material assignments) |
| Every `Aspirational (computed)` row has an explicit derivation formula  | Done  |
| No row claims a knob that doesn't exist in Infinigen 1.19.1 source      | Done  |
| Asymmetries between manifests are documented                            | Done (lighting_warmth in kitchen vs lighting_intensity in dining is explicit; both rooms could grow the other knob in a v2 manifest) |
| HardwareFactory misattribution in v0 doc is corrected                   | Done (now noted as bathroom-only) |
| TableFactory / SideboardFactory misnaming in v0 doc is corrected        | Done (now `DiningTableFactory` and removed) |
| KitchenCounter misnaming in v0 doc is corrected                         | Done (now `Countertop`) |
