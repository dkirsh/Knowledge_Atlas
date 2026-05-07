# Knowledge Atlas Track 3 — Master Document

**Owner:** Diego Jimenez (`Diggss-sys`, `dij002@ucsd.edu`)
**Course:** COGS 160 (Spring 2026), Prof. David Kirsh
**Track:** Track 3 — VR Studio
**Rooms:** bedroom, bathroom
**Branch:** `track3/diggss` on fork of `dkirsh/Knowledge_Atlas`
**Repo path:** `~/Knowledge_Atlas/160sp/track3/diggss/`

---

## 1. Purpose

Canonical architecture record per KA Methodology Method 8. Records design decisions, alternatives rejected, and theoretical grounding. Not a progress log. The test: a researcher reading this in six months without chat history should reconstruct *why* the system is the way it is.

---

## 2. Project overview

The deliverable is the parametric backbone of Knowledge Atlas's VR pipeline on Infinigen Indoors (Raistrick et al. 2024). Task 1 ships JSON-Schema parameter manifests; Task 2 ships the render pipeline + sweep gallery; Task 3 wires an LLM frontend that emits valid manifest patches.

Each manifest parameter is a construct-validity claim per Cronbach & Meehl (1955) — the knob must correspond to a measurable construct in the environmental-psychology literature.

---

## 3. Design decisions

### 3.1 Bathroom 6th parameter — `room_volume_m3` (chosen)

**Decision (2026-05-06):** bathroom manifest extended from 5 to 6 parameters by adding `room_volume_m3`, range 5.0–25.0 m³, default 12.0.

**Citation:** Ulrich (1991).

**Construct:** spatial volume → wellness/control perception. Small bathrooms (5–10 m³) cue utilitarian function and constrained movement; larger volumes (20+ m³) signal premium/spa wellness contexts. Mirrors the bedroom's `room_volume_m3` parameter.

**Methodology self-correction (Method 1):** earlier this session I proposed `lighting_warmth` as the 6th param. Wrong — `lighting_warmth` was already the 2nd param in the shipped manifest. I had been reading from the briefing's `KNOWN_SIGNATURES` (which only listed 4 params) instead of the actual file. Caught after `cat`-ing the manifest. **Lesson logged:** always verify the shipped artifact against source before proposing amendments. Method 1's "DO NOT fabricate" applies to file contents, not just citations.

**Alternatives considered and rejected:**

- **`plant_count` (Kaplan & Kaplan 1989):** would have closed the only remaining required-citation gap (bathroom currently has no Kaplan citation). Rejected for implementation cost — required Infinigen plant placement plumbing into bathroom composition.
- **`enclosure` (Vartanian 2015):** parallels bedroom but Vartanian is already cited for bathroom's `glass_area_fraction`. Less differentiated.
- **`luminaire_count` (Ulrich 1991):** rejected during initial inspect — would require overriding Infinigen's deterministic constraint solver for lamp placement. Not parameterized natively.

**Implementation hook:** room dimensions in `infinigen_examples/generate_indoors.py`. Wrapper plumbs volume → width × depth × height with `ceiling_height_m` held constant.

**Open issue:** mild multicollinearity with `ceiling_height_m` (volume = floor_area × ceiling_height). Acceptable per the bedroom precedent (which has both knobs).

### 3.2 Phase 2.5 splat outputs — shipped as documented blocker

**Decision (2026-05-04):** HDRI, material packs, and regions.json not delivered for Task 1.

**Rationale:** Scaniverse free tier on iOS does not expose `.ply` or `.splat` export to the scaffold scripts. Verified empirically.

**Mitigation path documented:** future Polycam capture (free tier exports `.ply`) or upgraded Scaniverse.

**Task 2 consequence:** synthetic-only render path. The splat-augmentation addendum (render gallery twice with/without HDR + materials) does not apply. Note in divergence-note "implications" section.

### 3.3 Scaffold bug fix held local

**Decision (2026-05-04):** one-line bytes/str concat fix on `scripts/track3/splat_to_hdri.py:123` applied locally, not committed.

**Rationale:** project brief says "don't write infrastructure." Scaffold bug fix is borderline; held local to keep PR scoped to deliverables.

---

## 4. Methodology binding

| Method | Application here |
|---|---|
| 1 — DO NOT pattern | Every Infinigen-hook claim verified against source before commit. Self-correction logged in 3.1. |
| 2 — Five-component prompts | Applies to Task 3 LLM frontend. |
| 3 — Contracts | Each Task 2 phase gets a written, testable success condition before work begins. |
| 4 — Trust calibration | Wrapper = L1 spot-check. Renders = L2 sample. Divergence note = L3 cross-AI. |
| 5 — Ruthless prompts | On demand if AI repeats a constraint violation. |
| 6 — Expert panel | Consider for divergence note (architect / cognitive scientist / statistician). |
| 7 — Cross-AI verification | Gemini cross-check on divergence notes before commit; one-paragraph note in PR body. |
| 8 — Master document | This file. |

---

## 5. Cross-reference index

| Construct | Manifest field | Infinigen hook | Citation |
|---|---|---|---|
| Ceiling height | `ceiling_height_m` (both rooms) | room geometry | Vartanian 2015, Meyers-Levy & Zhu 2007 |
| Color temperature | `lighting_warmth` (both rooms) | `PointLampFactory.params["Temperature"]` (3500–6500 K) | Münch 2020 |
| Enclosure | `enclosure` (bedroom only) | room geometry | Kaplan & Kaplan 1989 |
| Spatial volume | `room_volume_m3` (both rooms) | room dimensions | Ulrich 1991 |
| Glass area | `glass_area_fraction` (bathroom) | wall-element placement | Vartanian 2015 |
| Tile organicism | `tile_organicism` (bathroom) | material assignment | Joye 2007 |
| Fixture count | `fixture_count` (bathroom) | composition | Ulrich 1991 |
| Wall texture | `wall_texture_organicism` (bedroom) | material assignment | Joye 2007 |
| Window view | `window_view_complexity` (bedroom) | scene background | Kaplan & Kaplan 1989 |

---

## 6. Citation coverage

| Required citation | Bedroom | Bathroom |
|---|---|---|
| Vartanian et al. 2015 | ✓ | ✓ |
| Meyers-Levy & Zhu 2007 | ✓ | ✓ |
| Münch et al. 2020 | ✓ | ✓ |
| Ulrich 1991 | ✓ | ✓ (×2) |
| Kaplan & Kaplan 1989 | ✓ | **gap** |
| Joye 2007 | ✓ | ✓ |
| Cronbach & Meehl 1955 | framing only | framing only |

Bathroom missing Kaplan & Kaplan — acceptable per spec (≥1 required citation per manifest), but flagged as future improvement target.

---

## 7. Open questions

- Task 2 Phase 1: confirm `infinigen_wrapper.py` plumbs `room_volume_m3` and `lighting_warmth` end-to-end.
- Task 2 Phase 4: HSSD-200 access path and file format for divergence-note screenshots.
- Task 3: testable success condition for LLM-frontend prompt validation against the manifest schema.

---

## 8. Submission state

- **PR #2** (`dkirsh/Knowledge_Atlas#2`) — Task 1 awaiting grading. Commit `9be836f`.
- **Bathroom manifest amendment** — pending commit on `track3/diggss`. Adds `room_volume_m3`.
- **Task 2 PR** — not yet opened.

---

*Last updated: 2026-05-06. ISO dates, terse Markdown.*
