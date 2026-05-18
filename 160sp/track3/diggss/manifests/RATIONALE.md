# Phase 3 Parameter Rationale

## Bedroom Manifest

* **`ceiling_height_m` (2.0m - 4.0m)**
  * **Citation:** Meyers-Levy, J., & Zhu, R. (2007). The influence of ceiling height: The effect of priming on the type of processing that people use. *Journal of Consumer Research, 34*(2), 174–186.
  * **Justification:** The range spans from cramped residential (2.0m) to expansive architectural (4.0m). Meyers-Levy & Zhu demonstrate that lower ceilings prime item-specific, confined processing, while higher ceilings promote relational processing and feelings of freedom.
* **`lighting_warmth` (0.0 - 1.0)**
  * **Citation:** Münch, M., et al. (2020). The role of daylight for humans: Gaps in current knowledge. *Clocks & Sleep, 2*(1), 61–85.
  * **Justification:** Regulates circadian rhythm. The 0.0 to 1.0 fraction allows the LLM to transition the room from high-alertness cool daylight to pre-sleep warm/amber light, critical for melatonin onset in a bedroom environment.
* **`enclosure` (0.0 - 1.0)**
  * **Citation:** Vartanian, O., et al. (2015). Architectural design and the brain: Effects of ceiling height and perceived enclosure on beauty judgments and approach-avoidance decisions. *Journal of Environmental Psychology, 41*, 10–18.
  * **Justification:** Measures physical containment. Higher enclosure correlates with increased beauty judgments in private spaces (like bedrooms) but can trigger avoidance if pushed to the extreme, justifying the full 0.0-1.0 band.
* **`window_view_complexity` (0.0 - 1.0)**
  * **Citation:** Kaplan, R., & Kaplan, S. (1989). The experience of nature: A psychological perspective. *Cambridge University Press*.
  * **Justification:** Rooted in Attention Restoration Theory. A bedroom requires a restorative environment; the parameter allows tuning the view to provide "soft fascination" to recover from cognitive fatigue.
* **`wall_texture_organicism` (0.0 - 1.0)**
  * **Citation:** Joye, Y. (2007). Architectural lessons from environmental psychology: The case of biophilic architecture. *Review of General Psychology, 11*(4), 305–328.
  * **Justification:** Biophilic design dictates that organic, fractal-like textures (wood) reduce stress compared to synthetic, flat surfaces (paint/drywall). 
* **`room_volume_m3` (20.0 - 100.0)**
  * **Citation:** Ulrich, R. S. (1991). Effects of interior design on wellness: Theory and recent scientific research. *Journal of Health Care Interior Design, 3*, 97–109.
  * **Justification:** Total spatial volume impacts the baseline sense of control and "wellness" within a private recovery space.

---

## Bathroom Manifest

* **`ceiling_height_m` (2.0m - 3.0m)**
  * **Citation:** Meyers-Levy, J., & Zhu, R. (2007). The influence of ceiling height: The effect of priming on the type of processing that people use. *Journal of Consumer Research, 34*(2), 174–186.
  * **Justification:** Constrained to a tighter range than the bedroom, as bathrooms rarely exceed 3m. Modifies perceived freedom in a high-enclosure space.
* **`lighting_warmth` (0.0 - 1.0)**
  * **Citation:** Münch, M., et al. (2020). The role of daylight for humans: Gaps in current knowledge. *Clocks & Sleep, 2*(1), 61–85.
  * **Justification:** Crucial for task lighting (vanity mirrors). Allows switching between high-acuity morning routines (cool) and relaxing evening routines (warm).
* **`glass_area_fraction` (0.0 - 0.6)**
  * **Citation:** Vartanian, O., et al. (2015). Architectural design and the brain: Effects of ceiling height and perceived enclosure on beauty judgments and approach-avoidance decisions. *Journal of Environmental Psychology, 41*, 10–18.
  * **Justification:** Mirrors and shower glass alter the psychological perception of enclosure and boundary definition without changing physical dimensions.
* **`tile_organicism` (0.0 - 1.0)**
  * **Citation:** Joye, Y. (2007). Architectural lessons from environmental psychology: The case of biophilic architecture. *Review of General Psychology, 11*(4), 305–328.
  * **Justification:** Controls the transition from stark, sterile ceramic to natural, high-variance stone to leverage biophilic stress-reduction.
* **`fixture_count` (1 - 6)**
  * **Citation:** Ulrich, R. S. (1991). Effects of interior design on wellness: Theory and recent scientific research. *Journal of Health Care Interior Design, 3*, 97–109.
  * **Justification:** Functional complexity. A higher count increases utility but can trigger crowding/clutter responses, impacting baseline wellness perceptions.
* **`room_volume_m3` (5.0 m³ - 25.0 m³)**
  * **Citation:** Ulrich, R. S. (1991). Effects of interior design on wellness: Theory and recent scientific research. *Journal of Health Care Interior Design, 3*, 97–109.
  * **Justification:** Spatial volume modulates the baseline sense of control and wellness in a small private space. Smaller bathrooms (5-10 m³) cue utilitarian function and constrained movement; larger volumes (20+ m³) signal premium / spa-like wellness contexts. Ulrich's interior-design-wellness framework supports volume as a modulator of restorative interior experience.
