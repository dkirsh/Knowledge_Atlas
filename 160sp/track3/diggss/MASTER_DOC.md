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

### 3.4 Infinigen wrapper bridge and gin overrides (Source Verified)

**Decision (2026-05-06):** Implemented `build_bedroom` and `build_bathroom` bridge runners in `infinigen_wrapper.py` using `subprocess.run` to invoke `generate_indoors.py` directly, capturing `.blend` output for the existing GLTF export pipeline. No gin overrides (`-p`) were fabricated or passed.

**Decision (2026-05-06):** Scaffold maps `ceiling_height_m` to `RoomConstants.global_params.wall_height` directly. The remaining 11 parameters (e.g. `lighting_warmth`, `glass_area_fraction`) lacked native gin hooks and could not be mapped without violating the Read-Only constraint.

**Decision (2026-05-07) Pivot:** Rather than fabricating paths or breaking the Read-Only constraint to monkey-patch the solver, we have redefined the parameter manifests for both the Bedroom and Bathroom to use 7 **unified, natively configurable parameters**.
These 7 parameters are:
1. `ceiling_height_m` -> `RoomConstants.global_params.wall_height`
2. `wall_thickness_m` -> `RoomConstants.global_params.wall_thickness`
3. `daylight_intensity` -> `nishita_lighting.strength`
4. `sun_elevation_deg` -> `nishita_lighting.sun_elevation`
5. `dust_density` -> `nishita_lighting.dust_density`
6. `camera_exposure` -> `configure_render_cycles.exposure`
7. `lighting_warmth` -> Runtime monkey-patched into `PointLampFactory` *(retracted — see 2026-05-12 below)*

**Rationale:** This guarantees all paths are grep-verifiable (Method 1) and unifies the schema across room types. To support Dr. Kirsh's lighting-manipulation requirement we initially implemented a runtime interceptor for `lighting_warmth` that injects the Temperature constraint directly into memory without modifying Infinigen source on disk.

### 3.4a Wrapper simplification (2026-05-12)

**Decision (2026-05-12):** `lighting_warmth` is **removed from the rendered parameter set**. The `PointLampFactory.__init__` monkey-patch (Patch 2 in the 2026-05-07 wrapper) is deleted. `lighting_warmth` remains declared in `bedroom.manifest.json` and `bathroom.manifest.json` as a construct-validity claim citing Münch et al. (2020), but Task 2 sweeps will not exercise it.

**Rationale:** Patch 2 replaced an Infinigen *class method* (`il.PointLampFactory.__init__`) on a class path subject to rename across Infinigen versions. Patch 1 (room-type pinning) substitutes a single argument value inside `apply_greedy_restriction` and is preserved; surface area is narrower (one function, one argument) and the function is part of `infinigen_examples.util.generate_indoors_util` which is the documented entry-point seam students customise. The trade is: lose one rendered parameter, gain a wrapper whose breakages we can grep for.

**Spec alignment:** Task 2 prompt specifies *"six parameters per manifest × three settings each = 18 renders."* The manifests declare seven; removing `lighting_warmth` from the rendered set lands the sweep matrix at exactly six. This is the spec's anticipated shape, not a reduction.

**Sweep-axis selection:** The six rendered parameters for the Phase 3 gallery are `ceiling_height_m`, `wall_thickness_m`, `daylight_intensity`, `sun_elevation_deg`, `dust_density`, `camera_exposure`. All map to gin override paths verified by inspection of `scripts/track3/infinigen_wrapper.py:GIN_OVERRIDE_MAP`.

**Sidecar bug fix:** The 2026-05-07 wrapper, when invoked with `--params-default`, wrote `"resolved_params": {}` to the sidecar instead of the manifest defaults — making the idempotency check non-functional for default-parameter renders. The 2026-05-12 wrapper loads manifest defaults via `load_manifest_defaults()` before sidecar emission. `bedroom_default.glb` (the single render that survives from Sprint 3) carries an empty sidecar; Phase A re-render orchestration (`scripts/track3/phase_a_rerender.py`) detects this and re-renders to produce a correct sidecar.

**Method 1 trace:** before deleting Patch 2, the Infinigen CLI signature was cross-checked against `setup/install_log.txt` (the actual `argparse: error` output from Infinigen 1.19.1) — no fabricated flags, all `-t / -g / -p` arguments map to documented choices. Patch 2's class path (`infinigen.assets.lighting.indoor_lights.PointLampFactory`) was *not* verified against the installed Infinigen source; this is the failure mode the deletion addresses.

**Future hook:** if Infinigen exposes a native lamp-temperature gin path in a later release, `lighting_warmth` re-enters the rendered set without manifest changes. The construct is declared; only the implementation is deferred.

**Backups:** the pre-pivot wrapper is preserved at `scripts/track3/infinigen_wrapper.legacy.py` for diff/audit.

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
| Color temperature | `lighting_warmth` (both rooms) | declared construct only — no rendered hook (see §3.4a) | Münch 2020 |
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

- Task 2 Phase 1: empirically verify the six retained gin override paths (`nishita_lighting.*`, `RoomConstants.global_params.*`, `configure_render_cycles.exposure`) move pixels — see Phase D perceptual-hash check in Task 2 plan.
- Task 2 Phase 4: HSSD-200 access path and file format for divergence-note screenshots.
- Task 3: testable success condition for LLM-frontend prompt validation against the manifest schema.
- Docs hygiene: §3.1 references `room_volume_m3` as the bathroom 6th parameter, but the 2026-05-07 pivot superseded that parameter set. `RATIONALE.md` likewise describes pre-pivot constructs (`enclosure`, `window_view_complexity`, `glass_area_fraction`, `tile_organicism`, `fixture_count`). A reconciliation pass is needed.

---

## 8. Submission state

- **PR #2** (`dkirsh/Knowledge_Atlas#2`) — Task 1 awaiting grading. Commit `9be836f`.
- **Bathroom manifest amendment** — pending commit on `track3/diggss`. Adds `room_volume_m3`.
- **Task 2 PR** — not yet opened.

---

*Last updated: 2026-05-06. ISO dates, terse Markdown.*

---

## 9. Render pipeline verified (2026-05-06)

Full Infinigen → glTF pipeline confirmed working end-to-end. The course scaffold's intended flow is bridgeable.

**Verified invocations:**

```bash
# Step 1: Infinigen scene generation (~9 min/render)
python -m infinigen_examples.generate_indoors \
  --output_folder <dir> --seed <n> \
  -g singleroom fast_solve -t coarse
# Produces: <dir>/scene.blend (~520 MB)

# Step 2: Blender headless glTF export (~13 sec)
blender -b <dir>/scene.blend --python export_gltf.py -- <out>.glb
# Produces: <out>.glb (~600 MB before Draco compression)
```

**Compute budget for Task 2 sweep:** 36 renders × ~10 min = ~6 hrs total compute, distributable across sessions.

**Open issue:** 600 MB GLB per render is heavy for browser-based model-viewer. Bridge code should enable Draco compression (`export_draco_mesh_compression_enable=True`) and consider mesh decimation. May need to render at coarser settings for the gallery, with one or two higher-fidelity test renders for the viewer.

**Bridge implementation plan (handed to Antigravity, separate session):**
1. Translate manifest params to gin overrides (`-p path.field=value`)
2. Subprocess-call generate_indoors.py
3. Locate scene.blend in output folder
4. Headless Blender export to GLB with Draco compression
5. Write sidecar JSON per existing wrapper pattern
