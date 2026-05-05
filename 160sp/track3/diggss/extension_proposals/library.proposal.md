# Phase 4: Library Extension Proposal

## 1. Target Room & Closest Existing Entity
* **Target Room:** Library
* **Closest Existing Infinigen Entity:** `infinigen.entities.Office`
* **Rationale:** The Office class already contains the primitive generator logic for bookshelves, desks, and reading chairs. Extending it to a Library requires shifting from a single-user private layout to a multi-user public spatial arrangement.

## 2. Gap Analysis
The current `Office` class generates a "perimeter-focused" room where desks face windows or walls, and bookshelves are treated as isolated accent pieces. A Library requires "core-focused" macro-structures: parallel arrays of tall shelving (stacks) and clustered, central reading zones. The Office class lacks the procedural logic to generate navigable, equidistant aisles or to calculate acoustic dampening based on mass paper volume.

## 3. Proposed Parameters (JSON-Schema)
```json
{
  "$schema": "[https://json-schema.org/draft/2020-12/schema](https://json-schema.org/draft/2020-12/schema)",
  "$id": "ka://manifests/library.v1",
  "title": "Library Parameter Manifest",
  "type": "object",
  "properties": {
    "stack_spacing_m": {
      "type": "number",
      "minimum": 0.9,
      "maximum": 2.5,
      "unit": "meters",
      "description": "Navigable width between parallel bookshelves.",
      "status": "proposed"
    },
    "shelf_height_m": {
      "type": "number",
      "minimum": 1.2,
      "maximum": 3.0,
      "unit": "meters",
      "description": "Vertical height of the main library stacks.",
      "status": "proposed"
    },
    "public_seating_density": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "unit": "fraction",
      "description": "Ratio of floor space dedicated to reading tables vs stacks.",
      "status": "proposed"
    },
    "acoustic_dampening_index": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "unit": "fraction",
      "description": "Proxy for soft materials (carpet, acoustic tiles) to lower reverb.",
      "status": "proposed"
    },
    "wayfinding_visibility": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "unit": "fraction",
      "description": "Clearance of visual sightlines across the room from the entrance.",
      "status": "proposed"
    }
  },
  "required": ["stack_spacing_m", "shelf_height_m", "public_seating_density"]
}
