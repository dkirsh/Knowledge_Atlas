# Phase 2.5: Splat Capture Notes

## Capture Metadata
- **Capture Device:** iPhone [model, e.g., 15 Pro] with LiDAR
- **Capture Service:** Scaniverse (free tier)
- **Room Captured:** Bedroom
- **Capture Date / Time:** [YYYY-MM-DD, HH:MM]
- **Lighting Conditions:** [e.g., afternoon daylight through one west-facing window plus warm overhead LED]
- **Retries:** [e.g., 2 attempts; first lost tracking near the mirror]
- **Surface Assessment:** [e.g., matte walls and rug tracked cleanly; glossy monitor and mirror produced reconstruction artifacts]

## Export Blocker (why Phase 2.5 artifacts are not delivered)
- Scaniverse free tier on iOS does not expose a `.splat` or `.ply` export path for the splat capture used here. The scan is viewable in-app but cannot be moved off-device in a format the scaffold scripts (`splat_to_hdri.py`, `splat_to_materials.py`) accept (`.ply` or `.splat`).
- Verified: no Share/Export menu entry produces `.ply` or `.splat` in the free tier; cloud-sync routes (Files app, iCloud Drive) do not surface a splat-format file.
- Consequence: `lighting.hdr` + meta sidecar, `regions.json`, and the PBR material pack at `3d_rooms/_materials_library/bedroom/` are **not produced** for this submission.
- Mitigation path for a future pass: recapture in Polycam (free tier exports `.ply` for splats) or upgrade Scaniverse, then run the existing scaffold pipeline unchanged.

## What is delivered
- This notes file, documenting the capture attempt and the export blocker.
- The scaffold scripts remain untouched and ready to consume a valid `.ply` / `.splat` if one becomes available.
