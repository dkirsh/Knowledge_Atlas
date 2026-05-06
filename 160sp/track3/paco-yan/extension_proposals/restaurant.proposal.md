# Extension Proposal: Restaurant Room Type
**Student:** Paco Yan  
**Track 3 · Task 1 · Phase 4**  
**Target room type:** Restaurant  
**Closest existing Infinigen entity:** `infinigen.entities.DiningRoom`  

---

## 1. Target Room Type and Closest Existing Entity

**Target:** Restaurant (commercial dining establishment)  
**Closest existing entity:** `DiningRoom`

The DiningRoom entity is the closest match because a restaurant is architecturally an extension of a dining room into a commercial context: both are organized around table-and-seating clusters, overhead lighting rigs, window placements, and a connection to a kitchen zone. The DiningRoom constraint graph already handles `CeilingLightFactory`, `DeskLampFactory`, `WindowFactory`, `PanelDoorFactory`, and `GlassPanelDoorFactory` — all of which are semantically appropriate in a restaurant context.

The Kitchen entity was considered as a secondary reference because restaurants contain a back-of-house kitchen zone, but the customer-facing dining floor is structurally closer to DiningRoom than Kitchen.

---

## 2. Gap Analysis

The following constructs are present in a typical restaurant that the DiningRoom entity **cannot express**:

| Gap | Why DiningRoom Cannot Express It |
|-----|----------------------------------|
| **Commercial table clusters** | DiningRoom has no concept of repeated table-and-chair groupings at defined spacing intervals |
| **Bar / service counter** | No bar counter factory or service station entity in DiningRoom constraint graph |
| **Booth seating** | DiningRoom has no booth or banquette seating entity |
| **Host stand / reception point** | No entry reception furniture in DiningRoom |
| **Acoustic zoning** | DiningRoom has no concept of noise-separated dining zones |
| **Menu/signage displays** | No wall-mounted display or signage entity |
| **Table density control** | DiningRoom cannot control seating capacity as a parameter — tables are not placed as repeating units |
| **Kitchen pass-through opening** | No service window or pass-through wall opening between kitchen and dining floor |

---

## 3. Proposed New Parameters (JSON-Schema)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ka://manifests/restaurant.v1.proposed",
  "title": "Restaurant Room Extension Proposal",
  "description": "Proposed parameters for a restaurant room type extending Infinigen DiningRoom.",
  "infinigen_entity": "infinigen.entities.DiningRoom",
  "status": "proposed",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "ceiling_height_m": {
      "type": "number",
      "minimum": 2.4,
      "maximum": 5.0,
      "default": 3.0,
      "unit": "m",
      "status": "proposed",
      "description": "Floor-to-ceiling clear height of the restaurant dining floor.",
      "citation": "Meyers-Levy & Zhu (2007); Vartanian et al. (2015)",
      "rationale": "Ceiling height in restaurants modulates the social character and perceived prestige of the space. Meyers-Levy & Zhu (2007) found that higher ceilings promote abstract, relational thinking suited to social dining and conversation. Vartanian et al. (2015) link enclosure to approach-avoidance judgments — a higher ceiling signals a more formal, upscale establishment. Range extended to 5.0 m compared to residential DiningRoom (3.5 m) to accommodate commercial restaurant typologies including warehouse-style and high-ceiling fine dining spaces."
    },
    "table_density": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.5,
      "unit": "normalised",
      "status": "proposed",
      "description": "Scalar controlling how densely table-and-chair clusters are packed onto the dining floor (0 = spacious fine dining; 1 = packed casual dining).",
      "citation": "Joye (2007); Kaplan & Kaplan (1989)",
      "rationale": "Table density is the primary driver of perceived crowding and social comfort in restaurant environments. Joye (2007) establishes that high density increases cognitive load and reduces comfort; low density signals exclusivity and calm. Kaplan & Kaplan (1989) link complexity and crowding to attentional fatigue during social interactions. Maps to a proposed repeating TableClusterFactory placement system, extending DiningRoom's zone-filling constraint graph.",
      "implementation_hook": "infinigen/infinigen_examples/constraints/home.py — add TableClusterFactory zone rules"
    },
    "lighting_intensity": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.45,
      "unit": "normalised",
      "status": "proposed",
      "description": "Scalar on overhead and accent lighting output (0 = very dim/intimate; 1 = bright/cafeteria-style). Controls CeilingLightFactory and pendant light intensity.",
      "citation": "Ulrich (1991); Münch et al. (2020)",
      "rationale": "Lighting intensity in restaurants is one of the most studied environmental variables in commercial dining research. Ulrich (1991) links dimmer ambient lighting to reduced physiological stress and longer social engagement — consistent with fine dining contexts. Münch et al. (2020) provide the circadian basis for light-level effects on arousal. Default of 0.45 approximates a mid-range restaurant with warm ambient lighting. Maps to existing CeilingLightFactory parameters in Infinigen DiningRoom entity."
    },
    "seating_style": {
      "type": "string",
      "enum": ["chairs", "booths", "mixed", "bar_stools"],
      "default": "mixed",
      "unit": "token",
      "status": "proposed",
      "description": "Named seating arrangement token controlling which seating factory types are placed on the dining floor.",
      "citation": "Joye (2007); Ulrich (1991)",
      "rationale": "Seating style fundamentally changes the social geometry of a restaurant. Booth seating creates semi-private enclosures that Joye (2007) associates with reduced arousal and increased comfort through defined personal space. Chair seating produces more open, flexible arrangements. Mixed seating accommodates both intimate and group dining. This parameter requires new booth/banquette factory implementations not present in the current DiningRoom entity.",
      "implementation_hook": "infinigen/infinigen/entities/ — add BoothSeatingFactory.py"
    },
    "daylight_intensity": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.5,
      "unit": "normalised",
      "status": "proposed",
      "description": "Scalar on sun/sky light contribution through restaurant windows (0 = windowless/basement; 1 = full floor-to-ceiling glazing).",
      "citation": "Münch et al. (2020); Kaplan & Kaplan (1989)",
      "rationale": "Daylight access in restaurants affects both diner wellbeing and perceived atmosphere. Münch et al. (2020) identify daylight as the primary driver of circadian entrainment for daytime diners; Kaplan & Kaplan (1989) link window views and natural light to restorative experience. Range includes 0.0 to accommodate windowless restaurant typologies (basement restaurants, food courts). Maps to WindowFactory geometry parameters already present in Infinigen DiningRoom entity."
    },
    "wall_warmth_index": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.6,
      "unit": "normalised",
      "status": "proposed",
      "description": "0 = cool/industrial palette (exposed concrete, steel, white tile); 1 = warm/organic palette (wood panelling, brick, warm plaster).",
      "citation": "Ulrich (1991)",
      "rationale": "Wall material warmth is a robust predictor of perceived comfort and stress reduction in interior environments. Ulrich (1991) demonstrates that warm material palettes reduce physiological stress indicators — particularly relevant in commercial dining where atmosphere drives customer dwell time and return visits. A restaurant with cool industrial materials reads as modern and casual; warm materials signal comfort and tradition. Maps to wall material slots in Infinigen room geometry."
    },
    "biophilia_count": {
      "type": "integer",
      "minimum": 0,
      "maximum": 8,
      "default": 2,
      "unit": "count",
      "status": "proposed",
      "description": "Number of plant entities placed on the restaurant dining floor (LargePlantContainerFactory instances), used as zone dividers and decorative elements.",
      "citation": "Kaplan & Kaplan (1989); Ulrich (1991)",
      "rationale": "Indoor plants in restaurants serve dual purposes: restorative cues (Kaplan & Kaplan, 1989) and soft zone dividers that create semi-private dining areas without hard partitions. Ulrich (1991) links indoor greenery to reduced physiological stress. Upper bound of 8 is higher than residential dining room (4) to reflect the larger floor area of commercial restaurants and the common use of large planters as spatial dividers. Maps to existing LargePlantContainerFactory in Infinigen DiningRoom entity."
    }
  },
  "required": ["ceiling_height_m", "table_density", "lighting_intensity", "seating_style"]
}
```

---

## 4. Implementation Hooks

The following Infinigen source files would need editing to implement the restaurant entity:

| File | Change Required |
|------|----------------|
| `infinigen/infinigen_examples/generate_indoors.py` | Add `t.Semantics.Restaurant` to the supported roomtype list (line 175); add restaurant to `restrict_single_supported_roomtype` |
| `infinigen/infinigen_examples/constraints/home.py` | Add restaurant-specific furniture constraint graph: repeating TableClusterFactory zone rules, bar counter placement, booth seating zones |
| `infinigen/infinigen_examples/constraints/semantics.py` | Add `used_as[Semantics.BoothSeating]`, `used_as[Semantics.BarCounter]`, `used_as[Semantics.RestaurantTable]` semantic categories |
| `infinigen/infinigen/entities/tables/` | Add `TableClusterFactory.py` — procedural repeating table-and-chair cluster generator for commercial spacing |
| `infinigen/infinigen/entities/seating/` | Add `BoothSeatingFactory.py` — procedural booth/banquette geometry with upholstered back panels |
| `infinigen/infinigen_examples/configs_indoor/floor_plans/predefined.json` | Add restaurant floor plan geometry — rectangular dining floor with kitchen pass-through wall opening |

The minimal viable implementation requires only the first two files — `generate_indoors.py` and `home.py` — to produce a restaurant room populated with existing DiningRoom factories at higher density. The remaining files add restaurant-specific assets that would significantly improve typological fidelity.

---

## 5. Literature Backing

**Ceiling height** — Meyers-Levy, J., & Zhu, R. (2007). The influence of ceiling height: The effect of priming on the type of processing that people use. *Journal of Consumer Research, 34*(2), 174–186. https://doi.org/10.1086/519146; Vartanian, O., et al. (2015). Architectural design and the brain. *Journal of Environmental Psychology, 41*, 10–18. https://doi.org/10.1016/j.jenvp.2014.11.006

**Table density / biophilia** — Joye, Y. (2007). Architectural lessons from environmental psychology. *Review of General Psychology, 11*(4), 305–328. https://doi.org/10.1037/1089-2680.11.4.305; Kaplan, R., & Kaplan, S. (1989). *The experience of nature.* Cambridge University Press.

**Lighting intensity** — Ulrich, R. S. (1991). Effects of interior design on wellness. *Journal of Health Care Interior Design, 3*, 97–109; Münch, M., et al. (2020). The role of daylight for humans. *Clocks & Sleep, 2*(1), 61–85. https://doi.org/10.3390/clockssleep2010008

**Seating style / wall warmth** — Joye, Y. (2007). *ibid.*; Ulrich, R. S. (1991). *ibid.*

**Daylight intensity** — Münch, M., et al. (2020). *ibid.*; Kaplan, R., & Kaplan, S. (1989). *ibid.*
