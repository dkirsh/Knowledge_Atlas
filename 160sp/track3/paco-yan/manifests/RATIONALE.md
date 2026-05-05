# Manifest Rationale
**Student:** Paco Yan  
**Track 3 · Task 1 · Phase 3**  
**Room types:** Kitchen, Dining Room  

---

## Overview

Each manifest exposes six parameters — one more than the required minimum of five — selected on three criteria: (1) the parameter must correspond to a real generative knob in Infinigen's entity code, (2) it must be motivated by at least one published environmental-psychology study, and (3) its range must be defensible against the bands actually studied in that literature.

---

## Kitchen Manifest — `kitchen.manifest.json`

### Parameter Rationale

**`ceiling_height_m` (2.0–3.2 m, default 2.4 m)**  
Range set to 2.0–3.2 m rather than the living-room range of 2.0–3.5 m because kitchen ceilings are typically lower than living spaces due to overhead cabinet installation constraints. The upper bound of 3.2 m reflects the tallest residential kitchen ceiling in the Vartanian et al. (2015) study sample. Meyers-Levy & Zhu (2007) found the processing-mode shift at approximately 2.6 m; placing the default at 2.4 m reflects the functional, detail-oriented nature of kitchen tasks. *Corresponds to room shell geometry in Infinigen.*

**`cabinet_density` (0.0–1.0, default 0.5)**  
Range is a normalised scalar because Infinigen's placement system uses probability-weighted zone filling rather than absolute counts. The Joye (2007) crowding literature does not specify an absolute furniture count; instead it operates on perceived density, which this normalised scalar best approximates. Default of 0.5 produces a typical residential kitchen with counters on two walls. *Maps to SingleCabinetFactory placement probability in Infinigen kitchen entity hierarchy.*

**`daylight_intensity` (0.0–1.0, default 0.6)**  
Normalised scalar on sun/sky light contribution. Münch et al. (2020) identify 250–1000 lux at eye level as the relevant daylight band for circadian entrainment during daytime activities; 0.6 on this normalised scale approximates a well-windowed kitchen at midday. Kaplan & Kaplan (1989) Attention Restoration Theory further motivates daylight access as a restorative cue. *Maps to WindowFactory geometry and area parameters in Infinigen.*

**`countertop_material` (enum: granite, marble, oak, tile, metal, plastic)**  
Enum rather than continuous because Infinigen's material system resolves named tokens to PBR material packs — there is no continuous interpolation between material classes. The six values were selected to span the full warmth spectrum from cold-industrial (metal, plastic) to warm-natural (oak, granite, marble). Ulrich (1991) motivates material warmth as a wellness construct; the enum preserves the discrete material identity that the Infinigen wrapper requires. *Maps to material slots on KitchenCounterFactory surfaces.*

**`appliance_visibility` (0.0–1.0, default 0.5)**  
Controls countertop object density (BowlFactory, BottleFactory, HardwareFactory instance counts). Joye (2007) motivates this through the crowding-cognitive-load relationship; Kaplan & Kaplan (1989) provide the complementary framing through fascination and complexity. Default of 0.5 produces a "lived-in" kitchen without overwhelming clutter. *Maps directly to factory instance counts observed in Infinigen kitchen entity hierarchy.*

**`lighting_warmth` (0.0–1.0, default 0.5)**  
Colour temperature scalar from cool-white (0.0, ~5000 K) to warm-incandescent (1.0, ~2700 K). Ulrich (1991) links warm interior lighting to stress reduction; Münch et al. (2020) provide the complementary finding that cool daylight-spectrum lighting supports alertness during task activities. The parameter lets the LLM balance these competing effects depending on time-of-day context. *Maps to CeilingLightFactory and PointLampFactory colour parameters in Infinigen.*

---

## Dining Room Manifest — `dining_room.manifest.json`

### Parameter Rationale

**`ceiling_height_m` (2.0–3.5 m, default 2.7 m)**  
Full range of 2.0–3.5 m used because dining rooms lack the overhead-cabinet constraint that limits kitchen ceiling height. The Vartanian et al. (2015) study used ceilings in this exact range; Meyers-Levy & Zhu (2007) found relational/abstract processing shifts above approximately 2.6 m, motivating a default of 2.7 m for a socially oriented dining context. *Corresponds to room shell geometry in Infinigen.*

**`daylight_intensity` (0.0–1.0, default 0.5)**  
Default set lower than kitchen (0.5 vs 0.6) because dining rooms serve both daytime and evening contexts — a neutral default avoids over-committing to either. Münch et al. (2020) motivate daylight access for circadian health; Kaplan & Kaplan (1989) motivate it for restoration. *Maps to WindowFactory geometry in Infinigen.*

**`lighting_intensity` (0.0–1.0, default 0.6)**  
Distinct from `daylight_intensity` — controls artificial overhead and supplemental lighting. Ulrich (1991) links ambient lighting level to stress reduction; the social dining literature consistently associates dimmer lighting with longer meal duration and higher social engagement. Default of 0.6 represents a well-lit but not clinical dining room. *Maps to CeilingLightFactory and DeskLampFactory intensity in Infinigen.*

**`wall_warmth_index` (0.0–1.0, default 0.55)**  
Continuous scalar rather than enum because wall material warmth can be meaningfully interpolated (unlike countertop material identity). Ulrich (1991) is the primary citation; the 0.0–1.0 range spans from cool hard materials to warm soft materials. Default of 0.55 reflects a slightly warm residential dining room. *Maps to wall material slots in Infinigen room geometry.*

**`furniture_density` (0.0–1.0, default 0.4)**  
Joye (2007) is the primary citation for the crowding-cognitive-load relationship. Default of 0.4 reflects a moderately furnished dining room with table, chairs, and a sideboard — neither sparse nor crowded. *Maps to entity placement probability for seating and storage factories in Infinigen.*

**`biophilia_count` (0–4, default 1)**  
Integer rather than normalised scalar because plant entities are discrete objects (LargePlantContainerFactory instances). Upper bound of 4 reflects practical space constraints in a dining room — more than 4 plants would compete with furniture and circulation. Kaplan & Kaplan (1989) and Ulrich (1991) both support indoor greenery as a restorative cue. *Maps directly to LargePlantContainerFactory instance count in Infinigen.*

---

## References (APA)

Joye, Y. (2007). Architectural lessons from environmental psychology: The case of biophilic architecture. *Review of General Psychology, 11*(4), 305–328. https://doi.org/10.1037/1089-2680.11.4.305

Kaplan, R., & Kaplan, S. (1989). *The experience of nature: A psychological perspective.* Cambridge University Press.

Meyers-Levy, J., & Zhu, R. (2007). The influence of ceiling height: The effect of priming on the type of processing that people use. *Journal of Consumer Research, 34*(2), 174–186. https://doi.org/10.1086/519146

Münch, M., Wirz-Justice, A., Brown, S. A., Kantermann, T., Martiny, K., Stefani, O., Vetter, C., Wright, K. P., Wulff, K., & Skene, D. J. (2020). The role of daylight for humans: Gaps in current knowledge. *Clocks & Sleep, 2*(1), 61–85. https://doi.org/10.3390/clockssleep2010008

Raistrick, A., Mei, L., Kayan, K., Yan, D., Zuo, Y., Han, B., Wen, H., Parakh, M., Alexandropoulos, S., Lipson, L., Ma, Z., & Deng, J. (2024). Infinigen Indoors: Photorealistic indoor scenes using procedural generation. *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR).*

Ulrich, R. S. (1991). Effects of interior design on wellness: Theory and recent scientific research. *Journal of Health Care Interior Design, 3*, 97–109.

Vartanian, O., Navarrete, G., Chatterjee, A., Fich, L. B., Leder, H., Modroño, C., Rostrup, N., Skov, M., Corradi, G., & Nadal, M. (2015). Architectural design and the brain: Effects of ceiling height and perceived enclosure on beauty judgments and approach-avoidance decisions. *Journal of Environmental Psychology, 41*, 10–18. https://doi.org/10.1016/j.jenvp.2014.11.006
