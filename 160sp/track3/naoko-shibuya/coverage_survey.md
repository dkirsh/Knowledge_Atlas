# Track 3 Task 1 — Phase 2 Coverage Survey

## Method

I inspected Infinigen's built-in indoor room generation pipeline and ran the generator from the command line. The course handout referenced `indoor_scene_trial` and `scene.json`, but the installed Infinigen 1.19.1 CLI exposes task stages such as `coarse`, `populate`, `fine_terrain`, `render`, `mesh_save`, and `export`. For the smoke test, I therefore used the current CLI form with `-t coarse populate`, and verified output through generated files such as `scene.blend`, `solve_state.json`, `MaskTag.json`, and pipeline logs.

For Phase 2, I inspected source files and generated outputs to identify the top-level entities and visually meaningful parameters for the seven built-in indoor room types.

## Coverage Table

| Room type | Infinigen entity | Top-3 most-exposed parameters | Units | Range | What they affect visually |
|---|---|---|---|---|---|
| living_room | `Semantics.LivingRoom` / home constraints | `furniture_fullness_pct`, `painting_area_per_room_area`, `has_tv` | 0–1 float, area ratio, boolean | 0.6–0.9; 1.0–2.5; true/false | Furniture density/clutter; wall decoration coverage; media/focal object presence |
| kitchen | `Semantics.Kitchen`; `KitchenSpaceFactory`; `KitchenCabinetFactory` | `dimensions`, `has_kitchen_barstools`, `kitchen_wall` | Blender units, boolean, material category | source-derived; true/false; categorical | Cabinet/counter size; seating affordances; wall material |
| bedroom | `Semantics.Bedroom`; `BedFactory`; `BedFrameFactory` | bed/mattress scale, pillow count, bed/furniture density | Blender units, count, 0–1 float | source-derived; 2–3 pillows observed in source; 0.6–0.9 | Bed size/volume; softness/comfort cues; furniture density/clutter |
| bathroom | `Semantics.Bathroom`; `BathroomSinkFactory`; `StandingSinkFactory`; `BathtubFactory`; `ToiletFactory` | `bathroom_wall`, `bathroom_floor`, fixture count | material category, material category, count | categorical; categorical; source-derived | Wall finish; floor finish; fixture density |
| dining_room | `Semantics.DiningRoom`; `TableDiningFactory` | `dimensions`, `dining_chairs`, `dining_table_objects` | Blender units, count, object density | table height 0.65–0.85; source-derived; source-derived | Table size; seating density; table clutter |
| hallway / corridor | `Semantics.Hallway` | hallway count/connectivity, `portal_accessibility`, lighting/material | count, score, material/light category | 0–3; source-derived; source-derived | Circulation; openness/accessibility; wayfinding and brightness |
| office | `Semantics.Office`; `Semantics.OpenOffice`; `OfficeChairFactory` | `office_floor`, office chair dimensions, office type | material category, Blender units, categorical | categorical; source-derived; office/open-office/factory-office | Floor material; chair/work density; open vs enclosed office layout |

## Entity / Parameter Notes

### living_room

Semantic tag: Semantics.LivingRoom = "living-room"
Main files:
- infinigen/core/tags.py
- infinigen/core/constraints/example_solver/room/decorate.py
- infinigen_examples/constraints/home.py

Parameter candidates:
- furniture_fullness_pct
- painting_area_per_room_area
- has_tv / has_aquarium_tank / has_cocktail_tables

Likely visual effects:
- furniture density / clutter
- wall decoration amount
- media or focal object presence

Source evidence: In `infinigen_examples/constraints/home.py`, `furniture_fullness_pct` is sampled as `uniform(0.6, 0.9)` on line 38, `painting_area_per_room_area` is sampled as `uniform(40, 100) / 40` on line 46, and `has_tv` is sampled as `uniform() < 0.5` on line 48. These parameters are useful because they directly affect clutter/furniture density, wall decoration coverage, and the presence of a focal media object.

Useful environmental-psychology parameters: `furniture_fullness_pct`, `painting_area_per_room_area`, and focal-object flags such as `has_tv` are useful because they affect perceived clutter, decoration intensity, and attentional focus in the room.

Internal scaffolding parameters the LLM should not touch: random seeds, solver stages, relation-plane indices, placeholder IDs, object IDs, collision constraints, and annealing/optimization parameters should not be exposed because they control generation mechanics rather than psychologically interpretable room qualities.

### kitchen

Semantic tag: Semantics.Kitchen = "kitchen"
Main files:
- infinigen/core/tags.py
- infinigen/core/constraints/example_solver/room/decorate.py
- infinigen_examples/constraints/home.py
- infinigen/assets/objects/shelves/kitchen_space.py
- infinigen/assets/objects/shelves/kitchen_cabinet.py
- infinigen/assets/composition/material_assignments.py

Entity candidates:
- KitchenSpaceFactory
- KitchenIslandFactory
- KitchenCabinetFactory
- KitchenCounter
- KitchenAppliance
- wall/floor/ceiling surfaces

Parameter candidates:
- dimensions
- has_kitchen_barstools
- kitchen_wall
- kitchen_appliance_hard

Likely visual effects:
- cabinet/counter size
- seating affordances
- kitchen wall material
- appliance surface material

Source evidence: In `infinigen_examples/constraints/home.py`, `has_kitchen_barstools` is sampled as `uniform() < 0.15` on line 52 and checked on line 897. In `infinigen/assets/objects/shelves/kitchen_space.py`, `KitchenSpaceFactory` accepts `dimensions=None` on line 196, samples default dimensions around lines 200–213, and stores them as `self.dimensions` on line 213. In `infinigen/assets/objects/shelves/kitchen_cabinet.py`, `KitchenCabinetFactory` accepts `dimensions=None` on line 360 and samples default cabinet dimensions as `(uniform(0.25, 0.35), uniform(1.0, 4.0), uniform(0.5, 1.3))` on line 369. These parameters affect cabinet/counter size, kitchen layout, and seating affordances.

Useful environmental-psychology parameters: kitchen dimensions, cabinet/counter size, barstool presence, and wall/appliance material are useful because they affect perceived spaciousness, seating/social affordances, material warmth, and visual complexity.

Internal scaffolding parameters the LLM should not touch: factory seeds, object IDs, placeholder IDs, low-level mesh construction variables, relation-plane indices, collision constraints, and solver/annealing parameters should not be exposed because they control procedural generation mechanics rather than interpretable room qualities.

### bedroom

Semantic tag: Semantics.Bedroom = "bedroom"
Main files:
- infinigen/core/tags.py
- infinigen_examples/constraints/home.py
- infinigen/core/constraints/example_solver/room/decorate.py

Entity candidates:
- bed-related furniture
- lamps
- rugs
- floor/wall/ceiling surfaces

Parameter candidates:
- bedroom constraints
- lamps
- rugs
- furniture density

Source evidence: `BedFactory` is defined in `infinigen/assets/objects/seating/bed.py` line 22, and `BedFrameFactory` is defined in `infinigen/assets/objects/seating/bedframe.py` line 31. Although the grep output did not expose a simple bedroom-specific scalar parameter, the bedroom is strongly controlled by bed-related object factories, furniture density, lamps, rugs, and room material assignments. For the survey, bed presence, lighting, floor softness, and furniture density are the most interpretable manipulation candidates.

Useful environmental-psychology parameters: bed presence, bed frame/material variation, lamp presence, rug/floor material, and furniture density are useful because they affect perceived comfort, softness, lighting atmosphere, privacy, and visual clutter.

Internal scaffolding parameters the LLM should not touch: random seeds, factory seeds, object IDs, placeholder IDs, relation-plane choices, solver temperature, collision constraints, and low-level mesh-generation parameters should not be exposed because they may break generation or produce changes that are not psychologically interpretable.

Additional source evidence: In `infinigen/assets/objects/seating/bed.py`, `BedFactory` defines mattress type choices on line 23, creates a mattress through `mattress_factory` on lines 39–41, scales bed-related widths and sizes on lines 51–79, and creates pillows through `pillow_factory` on lines 89–105. This suggests that bedroom appearance is not controlled by one single scalar parameter, but by bed, mattress, pillow, and furniture object factories. These exposed object-level parameters affect bed size, bedding volume, softness, and visual comfort.

### bathroom

Semantic tag: Semantics.Bathroom = "bathroom"
Main files:
- infinigen/core/tags.py
- infinigen/assets/objects/bathroom/bathroom_sink.py
- infinigen/assets/objects/bathroom/bathtub.py
- infinigen/assets/objects/bathroom/toilet.py
- infinigen/assets/objects/bathroom/hardware.py
- infinigen/assets/composition/material_assignments.py

Entity candidates:
- BathroomSinkFactory
- StandingSinkFactory
- BathtubFactory
- ToiletFactory
- MirrorFactory
- HardwareFactory
- CeilingLightFactory

Parameter candidates:
- bathroom_wall
- bathroom_floor
- bathroom_touchsurface
- fixture count / fixture density

Source evidence: In `infinigen/assets/composition/material_assignments.py`, `bathroom_wall` is defined on line 318 and `bathroom_floor` is defined on line 340. The previous source search also located `BathroomSinkFactory` and `StandingSinkFactory` in `infinigen/assets/objects/bathroom/bathroom_sink.py`, and the smoke-test output showed `StandingSinkFactory`, `ToiletFactory`, `BathtubFactory`, `MirrorFactory`, `HardwareFactory`, and `CeilingLightFactory`. These parameters and entities affect material finish, fixture density, brightness, and perceived cleanliness/crowding.

Useful environmental-psychology parameters: `bathroom_wall`, `bathroom_floor`, `bathroom_touchsurface`, fixture count, and ceiling light count are useful because they affect perceived cleanliness, brightness, surface texture, and crowding.

Internal scaffolding parameters the LLM should not touch: random seeds, factory seeds, object IDs, placeholder IDs, relation-plane indices, collision constraints, and annealing/optimization parameters should not be exposed because they are internal solver controls rather than room-level design variables.

### dining_room

Semantic tag: Semantics.DiningRoom = "dining-room"
Main files:
- infinigen/core/tags.py
- infinigen_examples/constraints/home.py
- infinigen/assets/objects/tables/dining_table.py

Entity candidates:
- TableDiningFactory
- ChairFactory
- dining table objects

Parameter candidates:
- dining_chairs
- dining_table_objects
- table count

Source evidence: `TableDiningFactory` is defined in `infinigen/assets/objects/tables/dining_table.py` line 193. Its constructor accepts `dimensions=None` on line 194, and table dimensions are sampled in `sample_parameters` around lines 226–237, including a table height range of `uniform(0.65, 0.85)` on line 237. `SideTableFactory` and `CoffeeTableFactory` also define dimensions around lines 345–357. Dining-room constraints in `home.py` include dining chairs and dining table objects, which affect seating density and table clutter.

Useful environmental-psychology parameters: table dimensions, dining chair count, and dining-table object density are useful because they affect social spacing, seating density, perceived formality, and table clutter.

Internal scaffolding parameters the LLM should not touch: random seeds, factory seeds, object IDs, placeholder IDs, relation-plane indices, collision constraints, and low-level mesh-generation parameters should not be exposed because they control procedural placement rather than interpretable dining-room qualities.

### hallway / corridor

Semantic tag: Semantics.Hallway = "hallway"
Main files:
- infinigen/core/tags.py
- infinigen/core/constraints/example_solver/room/solidifier.py
- infinigen_examples/constraints/home.py

Entity candidates:
- hallway room node
- walls
- floor
- ceiling
- portals / openings
- lighting

Parameter candidates:
- hallway count
- portal_accessibility
- room connectivity

Source evidence: The search found `Semantics.Hallway` in `infinigen/core/tags.py` and hallway constraints in `infinigen_examples/constraints/home.py`. The hallway appears to be controlled more through room graph/connectivity constraints than through a single object factory. The most interpretable parameters are hallway count/connectivity, portal accessibility, corridor width/shape if exposed, and lighting/material choices.

Useful environmental-psychology parameters: hallway count/connectivity, `portal_accessibility`, corridor width/shape if exposed, lighting, and wall/floor material are useful because they affect wayfinding, openness, accessibility, perceived safety, and brightness.

Internal scaffolding parameters the LLM should not touch: graph-generation internals, adjacency solver controls, portal IDs, object IDs, random seeds, relation-plane indices, and collision/constraint solver settings should not be exposed because they define the procedural room graph rather than controllable environmental-psychology variables.

Additional source evidence: In `infinigen_examples/constraints/home.py`, hallway constraints appear repeatedly around lines 76, 123–153, and 209. The hallway count is constrained with `rooms[Semantics.Hallway].count().in_range(0, 3)` on line 312. The file also defines `portal_accessibility` as a score term around line 613. This supports treating hallway count/connectivity and portal accessibility as the most interpretable exposed controls for circulation, openness, and wayfinding.

### office

Semantic tags:
- Semantics.Office = "office"
- Semantics.OpenOffice = "open-office"
- Semantics.FactoryOffice = "factory-office"

Main files:
- infinigen/core/tags.py
- infinigen/core/constraints/example_solver/room/decorate.py
- infinigen/assets/objects/seating/chairs/office_chair.py
- infinigen/assets/composition/material_assignments.py

Entity candidates:
- OfficeChairFactory
- office floor
- shelves / office shelf items
- desk-like furniture

Parameter candidates:
- office_floor
- office chair count
- office type

Source evidence: `OfficeChairFactory` is defined in `infinigen/assets/objects/seating/chairs/office_chair.py` line 70. Its constructor accepts `dimensions=None` on line 71 and samples default dimensions in `sample_parameters` around lines 98–104. In `infinigen/assets/composition/material_assignments.py`, `office_floor` is defined on line 344. These parameters affect chair/workstation scale, office density, and floor material appearance.

Useful environmental-psychology parameters: `office_floor`, office chair dimensions/count, desk or workstation density, and office type are useful because they affect work density, openness, task focus, acoustic/social exposure, and material feel.

Internal scaffolding parameters the LLM should not touch: factory seeds, object IDs, placeholder IDs, relation-plane indices, solver stages, annealing parameters, mesh-generation internals, and collision constraints should not be exposed because they control generation mechanics rather than interpretable workspace qualities.

Additional source evidence: In `infinigen/assets/objects/seating/chairs/office_chair.py`, `OfficeChairFactory` is defined on line 70, accepts `dimensions=None` on line 71, stores dimensions on line 74, and samples default dimensions through `sample_parameters` on lines 98–104. In `infinigen/assets/composition/material_assignments.py`, `office_floor` is defined on line 344 as `wood_tiles + [(fabric.Rug, 1.0)]`. These source locations support using office chair dimensions/count and floor material as interpretable workspace parameters.