# Manifest Rationale

## Living Room

The living room manifest exposes six parameters: ceiling height, daylight intensity, wall warmth, furniture fullness, wall decoration density, and television presence. These were selected because they connect room-scale visual changes to environmental-psychology constructs such as perceived openness, restoration, clutter, attention, and comfort.

- `ceiling_height_m`: Included because ceiling height changes perceived spatial volume and openness. The 2.0–3.5 m range is broader than the ceiling-height values discussed in Vartanian et al. (2015), which references the U.S. standard ceiling height of 2.44 m and prior preference findings peaking around 3.04 m. The manifest range remains constrained to plausible residential interiors, while the default value of 2.7 m falls within this empirically discussed range.
- `daylight_intensity`: Included because daylight can influence restoration, alertness, and perceived environmental quality.
- `wall_warmth_index`: Included as a material and color warmth parameter linked to comfort and stress reduction.
- `furniture_fullness_pct`: Included because the Phase 2 survey found this source-controlled parameter in `home.py`, sampled from 0.6–0.9. It maps to furniture density and visual clutter.
- `painting_area_per_room_area`: Included because the Phase 2 survey found this source-controlled parameter in `home.py`, sampled from approximately 1.0–2.5. It maps to wall decoration density and visual complexity.
- `has_tv`: Included because the Phase 2 survey found this source-controlled boolean parameter in `home.py`. It changes whether the living room has a focal media object.

## Bedroom

The bedroom manifest exposes six parameters: ceiling height, daylight intensity, wall warmth, furniture fullness, bed size scale, and pillow count. These were selected because the bedroom survey showed that bedroom appearance is driven by bed-related factories, furniture density, lighting, rugs, and material assignments.

- `ceiling_height_m`: Included because ceiling height changes perceived openness and room volume.
- `daylight_intensity`: Included because daylight affects circadian regulation, alertness, and sleep-related comfort.
- `wall_warmth_index`: Included because warmer material palettes can support perceived softness, calmness, and comfort.
- `furniture_fullness_pct`: Included as a clutter and crowding proxy, using the same source-derived 0.6–0.9 range from the home constraints.
- `bed_size_scale`: Included because the bed is the dominant comfort object in the bedroom, and its scale changes both perceived spaciousness and restorative affordance.
- `pillow_count`: Included because the Phase 2 survey found pillow-related generation in the bedroom source, and pillow count provides a visible softness cue.

## References

Kaplan, R., & Kaplan, S. (1989). *The experience of nature: A psychological perspective*. Cambridge University Press.

Joye, Y. (2007). Architectural lessons from environmental psychology: The case of biophilic architecture. *Review of General Psychology, 11*(4), 305–328.

Meyers-Levy, J., & Zhu, R. J. (2007). The influence of ceiling height: The effect of priming on the type of processing that people use. *Journal of Consumer Research, 34*(2), 174–186.

Münch, M., Wirz-Justice, A., Brown, S. A., Kantermann, T., Martiny, K., Stefani, O., Vetter, C., Wright, K. P., Wulff, K., & Skene, D. J. (2020). The role of daylight for humans: Gaps in current knowledge. *Clocks & Sleep, 2*(1), 61–85.

Ulrich, R. S. (1991). Effects of interior design on wellness: Theory and recent scientific research. *Journal of Health Care Interior Design, 3*, 97–109.

Vartanian, O., Navarrete, G., Chatterjee, A., Fich, L. B., Leder, H., Modroño, C., Nadal, M., Rostrup, N., & Skov, M. (2015). Architectural design and the brain: Effects of ceiling height and perceived enclosure on beauty judgments and approach-avoidance decisions. *Journal of Environmental Psychology, 41*, 10–18.