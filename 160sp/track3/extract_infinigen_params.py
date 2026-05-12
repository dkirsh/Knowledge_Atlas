#!/usr/bin/env python3
"""extract_infinigen_params.py — Task 1 Phase 2 helper.

Introspects a given Infinigen room class and emits a draft parameter manifest
(JSON-Schema shape) listing every constructor argument with type, range, and
default. The student then fills in the literature citations and any panel-
required fields the introspector cannot infer.

Usage:

    # All seven Infinigen-covered room types
    python3 extract_infinigen_params.py --all

    # One specific room type, write to file
    python3 extract_infinigen_params.py --room living_room \\
        --out drafts/living_room_draft.schema.json

    # List parameters without producing a manifest
    python3 extract_infinigen_params.py --room kitchen --inspect

If Infinigen is not installed, falls back to the documented constructor
signatures shipped in `KNOWN_SIGNATURES` so students can author manifests
even before completing the smoke test. The fallback is approximate; verify
against the live Infinigen source once installed.
"""
from __future__ import annotations
import argparse, inspect, json, sys
from pathlib import Path

# ──────────────────────────────────────────────────────────────────
# Documented signatures (v0.5 reference, used as fallback when Infinigen
# is not installed). Update these as Infinigen versions move.
# ──────────────────────────────────────────────────────────────────

KNOWN_SIGNATURES = {
    "living_room": {
        "ceiling_height_m":  {"type": "number", "min": 2.0, "max": 3.5, "default": 2.7, "unit": "metres"},
        "daylight_intensity":{"type": "number", "min": 0.0, "max": 1.0, "default": 0.7, "unit": "fraction"},
        "wall_warmth_index": {"type": "number", "min": 0.0, "max": 1.0, "default": 0.5, "unit": "fraction"},
        "furniture_density": {"type": "number", "min": 0.0, "max": 1.0, "default": 0.6, "unit": "fraction"},
        "biophilia_count":   {"type": "integer","min": 0,   "max": 8,   "default": 2,   "unit": "count"},
    },
    "kitchen": {
        "ceiling_height_m":  {"type": "number", "min": 2.0, "max": 3.5, "default": 2.5, "unit": "metres"},
        "counter_material":  {"type": "string", "enum": ["stone","wood","laminate","metal"], "default": "stone"},
        "cabinet_color_hue": {"type": "number", "min": 0.0, "max": 1.0, "default": 0.1, "unit": "hue"},
        "lighting_brightness":{"type":"number", "min": 0.0, "max": 1.0, "default": 0.8, "unit": "fraction"},
        "layout":            {"type": "string", "enum": ["galley","l_shape","u_shape","island"], "default": "l_shape"},
    },
    "bedroom": {
        "ceiling_height_m":  {"type": "number", "min": 2.0, "max": 3.2, "default": 2.5, "unit": "metres"},
        "lighting_warmth":   {"type": "number", "min": 0.0, "max": 1.0, "default": 0.7, "unit": "fraction"},
        "enclosure":         {"type": "number", "min": 0.0, "max": 1.0, "default": 0.6, "unit": "fraction"},
        "wall_material":     {"type": "string", "enum": ["paint","wood","fabric"], "default": "paint"},
        "color_saturation":  {"type": "number", "min": 0.0, "max": 1.0, "default": 0.3, "unit": "fraction"},
    },
    "bathroom": {
        "ceiling_height_m":  {"type": "number", "min": 2.0, "max": 3.0, "default": 2.4, "unit": "metres"},
        "tile_material":     {"type": "string", "enum": ["ceramic","stone","mosaic"], "default": "ceramic"},
        "glass_area_fraction":{"type":"number", "min": 0.0, "max": 0.6, "default": 0.2, "unit": "fraction"},
        "fixture_count":     {"type": "integer","min": 1,   "max": 6,   "default": 3,   "unit": "count"},
    },
    "dining_room": {
        "ceiling_height_m":  {"type": "number", "min": 2.2, "max": 3.5, "default": 2.7, "unit": "metres"},
        "table_size":        {"type": "number", "min": 2,   "max": 12,  "default": 6,   "unit": "seats"},
        "lighting_intimacy": {"type": "number", "min": 0.0, "max": 1.0, "default": 0.5, "unit": "fraction"},
        "material_warmth":   {"type": "number", "min": 0.0, "max": 1.0, "default": 0.6, "unit": "fraction"},
    },
    "hallway": {
        "width_m":           {"type": "number", "min": 1.0, "max": 4.0, "default": 1.5, "unit": "metres"},
        "ceiling_height_m":  {"type": "number", "min": 2.0, "max": 3.5, "default": 2.5, "unit": "metres"},
        "lighting_frequency":{"type": "number", "min": 0.0, "max": 1.0, "default": 0.5, "unit": "fraction"},
    },
    "office": {
        "ceiling_height_m":  {"type": "number", "min": 2.4, "max": 3.5, "default": 2.7, "unit": "metres"},
        "task_lighting":     {"type": "number", "min": 0.0, "max": 1.0, "default": 0.7, "unit": "fraction"},
        "openness":          {"type": "number", "min": 0.0, "max": 1.0, "default": 0.5, "unit": "fraction"},
        "wall_color_hue":    {"type": "number", "min": 0.0, "max": 1.0, "default": 0.4, "unit": "hue"},
        "visual_complexity": {"type": "number", "min": 0.0, "max": 1.0, "default": 0.3, "unit": "fraction"},
    },
}


def introspect_live(room: str) -> dict | None:
    """Return parameter dict by introspecting the live Infinigen class. None on failure."""
    try:
        import infinigen
    except ImportError:
        return None
    cls_name = "".join(w.capitalize() for w in room.split("_"))
    cls = getattr(getattr(infinigen, "entities", None), cls_name, None)
    if cls is None: return None
    sig = inspect.signature(cls.__init__)
    out = {}
    for name, p in sig.parameters.items():
        if name == "self": continue
        anno = p.annotation
        default = p.default if p.default is not inspect.Parameter.empty else None
        out[name] = {
            "type": _type_str(anno),
            "default": default,
            "min": None,  # student fills in
            "max": None,
            "unit": "TODO",
            "_introspected": True,
        }
    return out


def _type_str(anno) -> str:
    if anno is inspect.Parameter.empty: return "TODO"
    if anno is float: return "number"
    if anno is int: return "integer"
    if anno is str: return "string"
    if anno is bool: return "boolean"
    return str(anno)


def make_manifest(room: str, params: dict) -> dict:
    """Wrap a parameter dict into a JSON-Schema-shaped draft manifest."""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": f"{room} parameter manifest (DRAFT — fill in citations)",
        "_track3_room_type": room,
        "_authored_by": "TODO student name",
        "_authored_date": "TODO YYYY-MM-DD",
        "_panel_required_fields": {
            "interaction_mode": "TODO  # focused | unfocused | mixed",
            "valence_polarity": "TODO  # positive | negative | neutral | mixed",
            "temporal_window":  "TODO  # snapshot | short_period | sustained | longitudinal",
            "cross_cultural_variance": "TODO  # low | medium | high",
        },
        "type": "object",
        "properties": {
            name: {
                "type": p["type"],
                "minimum": p.get("min"),
                "maximum": p.get("max"),
                "default": p.get("default"),
                "x-unit": p.get("unit", "TODO"),
                "x-citation": "TODO  # APA citation supporting this parameter",
                "x-rationale": "TODO  # one sentence on why this parameter matters",
            } for name, p in params.items()
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--all", action="store_true")
    p.add_argument("--room")
    p.add_argument("--out")
    p.add_argument("--inspect", action="store_true",
                   help="Print parameter list without writing a manifest")
    args = p.parse_args()

    rooms = list(KNOWN_SIGNATURES) if args.all else [args.room] if args.room else None
    if not rooms:
        p.print_help(); return 2

    for room in rooms:
        live = introspect_live(room)
        params = live or KNOWN_SIGNATURES.get(room)
        if params is None:
            sys.stderr.write(f"No known signature and no live Infinigen for room={room!r}\n")
            continue
        source = "introspected from live Infinigen" if live else "fallback (KNOWN_SIGNATURES; install Infinigen for live)"
        if args.inspect:
            print(f"\n=== {room} ({source}) ===")
            for name, info in params.items():
                print(f"  {name}: {info}")
            continue
        manifest = make_manifest(room, params)
        out = Path(args.out) if args.out else Path(f"drafts/{room}_draft.schema.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f: json.dump(manifest, f, indent=2)
        print(f"  Wrote {out} ({source})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
