# Track 3 · Task 1 — Coverage Survey
**Student:** Paco Yan  
**Date:** 2026-04-30  
**Infinigen version:** 1.19.1  
**Blender version:** 4.0.2  

## Method

For each room type, the indoor generator was run twice (seed 0 and seed 1) using:

```bash
python3 -m infinigen_examples.generate_indoors \
  --output_folder ~/infinigen_out/survey/<room> \
  --seed <seed> \
  -t coarse populate \
  -g singleroom fast_solve \
  -p restrict_single_supported_roomtype=True
```

Entity hierarchies were extracted via Blender CLI.

## Coverage Table

| Room Type | Infinigen Entity | Top-3 Most-Exposed Parameters | Units | Range | What They Affect Visually |
|-----------|-----------------|-------------------------------|-------|-------|--------------------------|
| living_room | `living-room_0/0` | `ceiling_height`, `furniture_density`, `window_area_ratio` | m, norm, norm | 2.0–3.5, 0–1, 0–0.6 | Volume; clutter; daylight admission |
| kitchen | `kitchen_0/0` | `cabinet_density`, `appliance_count`, `countertop_material` | norm, count, token | 0–1, 0–6, enum | Storage density; appliance presence; surface appearance |
| bedroom | `bedroom_0/0` | `ceiling_height`, `furniture_density`, `lighting_warmth` | m, norm, norm | 2.0–3.5, 0–1, 0–1 | Volume; clutter; ambient warmth |
| bathroom | `bathroom_0/0` | `fixture_density`, `tile_material`, `lighting_intensity` | norm, token, norm | 0–1, enum, 0–1 | Fixture count; surface material; brightness |
| dining_room | `dining-room_0/0` | `table_size`, `seating_count`, `lighting_intensity` | norm, count, norm | 0–1, 2–12, 0–1 | Table footprint; capacity; ambiance |
| hallway | not implemented in v1.19.1 | `width`, `length`, `lighting_density` | m, m, norm | 0.9–2.4, 2–20, 0–1 | Passage width; corridor length; lighting |
| office | not implemented in v1.19.1 | `desk_count`, `lighting_intensity`, `storage_density` | count, norm, norm | 1–8, 0–1, 0–1 | Workstation count; task lighting; shelf density |
