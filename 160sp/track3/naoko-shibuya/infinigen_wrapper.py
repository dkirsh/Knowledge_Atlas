ROOM_BUILDERS = {

    "living_room": {
        "entity": "infinigen.entities.LivingRoom",
        "param_map": {
            # Manifest key                  : Actual key in home.py
            "ceiling_height_m":              "ceiling_height",        # TODO: verify key exists
            "daylight_intensity":            "sun_light_factor",      # TODO: verify key exists
            "wall_warmth_index":             "wall_warmth",           # TODO: verify key exists
            "furniture_fullness_pct":        "furniture_fullness_pct",   # home.py line 38
            "painting_area_per_room_area":   "painting_area_per_room_area", # home.py line 46
            "has_tv":                        "has_tv",                # home.py line 48
        }
    },

    "bedroom": {
        "entity": "infinigen.entities.Bedroom",
        "param_map": {
            # Manifest key                  : Factory / home.py key
            "ceiling_height_m":              "ceiling_height",        # TODO: verify key exists
            "daylight_intensity":            "sun_light_factor",      # TODO: verify key exists
            "wall_warmth_index":             "wall_warmth",           # TODO: verify key exists
            "furniture_fullness_pct":        "furniture_fullness_pct",   # home.py range 0.6–0.9
            "bed_size_scale":                "bed_size_scale",        # BedFactory scale TODO: verify
            "pillow_count":                  "pillow_count",          # BedFactory pillows TODO: verify
        }
    },
}