# Track 3 Task 1 — Phase 2 Coverage Survey

## Method

I inspected Infinigen's built-in indoor room generation pipeline and ran the generator from the command line. The course handout referenced `indoor_scene_trial` and `scene.json`, but the installed Infinigen 1.19.1 CLI exposes task stages such as `coarse`, `populate`, `fine_terrain`, `render`, `mesh_save`, and `export`. For the smoke test, I therefore used the current CLI form with `-t coarse populate`, and verified output through generated files such as `scene.blend`, `solve_state.json`, `MaskTag.json`, and pipeline logs.

For Phase 2, I inspected source files and generated outputs to identify the top-level entities and visually meaningful parameters for the seven built-in indoor room types.

## Coverage Table

| Room type | Infinigen entity | Top-3 most-exposed parameters | Units | Range | What they affect visually |
|---|---|---|---|---|---|
| living_room | TBD | TBD | TBD | TBD | TBD |
| kitchen | TBD | TBD | TBD | TBD | TBD |
| bedroom | TBD | TBD | TBD | TBD | TBD |
| bathroom | TBD | TBD | TBD | TBD | TBD |
| dining_room | TBD | TBD | TBD | TBD | TBD |
| hallway / corridor | TBD | TBD | TBD | TBD | TBD |
| office | TBD | TBD | TBD | TBD | TBD |

## Entity / Parameter Notes

### living_room

Top-level entities observed or source-indicated: TBD.

Useful environmental-psychology parameters: TBD.

Internal scaffolding parameters the LLM should not touch: TBD.

### kitchen

Top-level entities observed or source-indicated: TBD.

Useful environmental-psychology parameters: TBD.

Internal scaffolding parameters the LLM should not touch: TBD.

### bedroom

Top-level entities observed or source-indicated: TBD.

Useful environmental-psychology parameters: TBD.

Internal scaffolding parameters the LLM should not touch: TBD.

### bathroom

Top-level entities observed or source-indicated: TBD.

Useful environmental-psychology parameters: TBD.

Internal scaffolding parameters the LLM should not touch: TBD.

### dining_room

Top-level entities observed or source-indicated: TBD.

Useful environmental-psychology parameters: TBD.

Internal scaffolding parameters the LLM should not touch: TBD.

### hallway / corridor

Top-level entities observed or source-indicated: TBD.

Useful environmental-psychology parameters: TBD.

Internal scaffolding parameters the LLM should not touch: TBD.

### office

Top-level entities observed or source-indicated: TBD.

Useful environmental-psychology parameters: TBD.

Internal scaffolding parameters the LLM should not touch: TBD.
