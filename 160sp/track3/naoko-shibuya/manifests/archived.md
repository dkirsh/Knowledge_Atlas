
## living_room
"biophilia_count": {
            "type": "integer",
            "minimum": 0,
            "maximum": 8,
            "default": 2,
            "unit": "count",
            "description": "Number of indoor plant entities placed in the room.",
            "citation": "Kaplan & Kaplan (1989); Ulrich (1991)",
            "rationale": "Indoor plants are included as biophilic restoration cues."
        },

        "colour_palette_id": {
            "type": "string",
            "enum": [
                "neutral_warm",
                "neutral_cool",
                "high_contrast",
                "monochrome",
                "saturated"
            ],
            "default": "neutral_warm",
            "description": "Named color palette token resolved by the rendering wrapper.",
            "citation": "Meyers-Levy & Zhu (2007)",
            "rationale": "Color palette is included because color temperature and saturation can interact with spatial perception and mood."
        }