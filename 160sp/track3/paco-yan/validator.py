#!/usr/bin/env python3
"""
validator.py — Patch validator for Knowledge Atlas room manifests.

Track 3 · Task 1 / Task 3 cross-cutting deliverable
Author: Paco Yan (payan@ucsd.edu)

Implements the validation contract specified in Track 3 / Task 3 / Phase 2:
loads a room manifest (JSON Schema) and a candidate JSON patch, then returns
either OK or a structured list of violations the LLM front-end must fix
before the patch reaches the renderer.

Patch grammar (per Task 3 / Phase 1):
    set:    {"op": "set",    "param": <name>, "value": <any>, "unit"?: <str>}
    delta:  {"op": "delta",  "param": <name>, "delta": <num>, "unit"?: <str>}
    preset: {"op": "preset", "preset": <name>}

Violation codes (per Task 3 / Phase 2):
    schema_invalid   — patch fails the patch-grammar JSON Schema
    unknown_param    — op targets a parameter not declared in the manifest
    type_mismatch    — value's JSON type disagrees with the manifest's type
    out_of_range     — numeric value falls outside [minimum, maximum]
    out_of_schema    — op cannot be expressed in this manifest at all
                       (e.g. preset name not registered, unit mismatch,
                        enum value not in declared enum)

CLI
---
    python validator.py --manifest kitchen.manifest.json \\
                        --patch   path/to/patch.json
        Exit 0 → OK
        Exit 1 → violations (printed as structured JSON to stdout)
        Exit 2 → CLI / IO error (printed to stderr)

Library
-------
    from validator import validate
    result = validate(patch_dict, manifest_dict, presets=set_of_names)
    # result is {"ok": bool, "violations": [...]}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "validator.py requires the 'jsonschema' package.\n"
        "Install with: pip install jsonschema\n"
    )
    sys.exit(2)


# ---------------------------------------------------------------------------
# Patch grammar — verbatim from Task 3 / Phase 1 spec.
# ---------------------------------------------------------------------------

PATCH_GRAMMAR: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Room Parameter Patch",
    "type": "object",
    "required": ["room_id", "operations"],
    "properties": {
        "room_id": {"type": "string"},
        "manifest_version": {"type": "string"},
        "operations": {
            "type": "array",
            "minItems": 1,
            "items": {
                "oneOf": [
                    {
                        "type": "object",
                        "required": ["op", "param", "value"],
                        "properties": {
                            "op": {"const": "set"},
                            "param": {"type": "string"},
                            "value": {},
                            "unit": {"type": "string"},
                        },
                    },
                    {
                        "type": "object",
                        "required": ["op", "param", "delta"],
                        "properties": {
                            "op": {"const": "delta"},
                            "param": {"type": "string"},
                            "delta": {"type": "number"},
                            "unit": {"type": "string"},
                        },
                    },
                    {
                        "type": "object",
                        "required": ["op", "preset"],
                        "properties": {
                            "op": {"const": "preset"},
                            "preset": {"type": "string"},
                        },
                    },
                ]
            },
        },
    },
}


# ---------------------------------------------------------------------------
# Violation construction helpers
# ---------------------------------------------------------------------------

def _v(op_index: int | None, code: str, param: str | None, message: str) -> dict:
    """Build a single violation record in the spec'd shape."""
    return {
        "op_index": op_index,
        "code": code,
        "param": param,
        "message": message,
    }


def _json_type(value: Any) -> str:
    """Map a Python value to its JSON-Schema type name."""
    if isinstance(value, bool):  # bool must be checked before int
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if value is None:
        return "null"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "unknown"


def _types_compatible(declared: str, actual: str) -> bool:
    """A manifest 'number' accepts both ints and floats; 'integer' rejects floats."""
    if declared == actual:
        return True
    if declared == "number" and actual == "integer":
        return True
    return False


# ---------------------------------------------------------------------------
# Per-operation checks
# ---------------------------------------------------------------------------

def _check_set(
    op: dict,
    op_index: int,
    manifest_props: dict[str, dict],
) -> list[dict]:
    """Validate a single 'set' op against the manifest's per-param schema."""
    violations: list[dict] = []
    param = op["param"]
    value = op["value"]

    if param not in manifest_props:
        return [_v(op_index, "unknown_param", param,
                   f"Parameter '{param}' is not declared in the manifest.")]

    pspec = manifest_props[param]
    declared_type = pspec.get("type")

    # Type check
    actual_type = _json_type(value)
    if declared_type and not _types_compatible(declared_type, actual_type):
        violations.append(_v(
            op_index, "type_mismatch", param,
            f"Parameter '{param}' expects type '{declared_type}'; got '{actual_type}'.",
        ))
        # If the type is wrong we cannot do range/enum checks meaningfully.
        return violations

    # Enum check (e.g. countertop_material)
    if "enum" in pspec and value not in pspec["enum"]:
        violations.append(_v(
            op_index, "out_of_schema", param,
            f"Value '{value}' is not in the declared enum for '{param}': "
            f"{pspec['enum']}.",
        ))

    # Range check (numeric)
    if declared_type in ("number", "integer"):
        lo = pspec.get("minimum")
        hi = pspec.get("maximum")
        if lo is not None and value < lo:
            violations.append(_v(
                op_index, "out_of_range", param,
                f"Value {value} is below minimum {lo} for '{param}'.",
            ))
        if hi is not None and value > hi:
            violations.append(_v(
                op_index, "out_of_range", param,
                f"Value {value} is above maximum {hi} for '{param}'.",
            ))

    # Unit check
    declared_unit = pspec.get("unit")
    op_unit = op.get("unit")
    if op_unit and declared_unit and op_unit != declared_unit:
        violations.append(_v(
            op_index, "out_of_schema", param,
            f"Unit '{op_unit}' does not match manifest unit '{declared_unit}' "
            f"for '{param}'.",
        ))

    return violations


def _check_delta(
    op: dict,
    op_index: int,
    manifest_props: dict[str, dict],
) -> list[dict]:
    """Validate a single 'delta' op. Cannot range-check absolute value
    (no current state available) but checks that the parameter exists,
    is numeric, and that the delta itself isn't larger than the full
    declared range (which would always overflow)."""
    violations: list[dict] = []
    param = op["param"]
    delta = op["delta"]

    if param not in manifest_props:
        return [_v(op_index, "unknown_param", param,
                   f"Parameter '{param}' is not declared in the manifest.")]

    pspec = manifest_props[param]
    declared_type = pspec.get("type")

    if declared_type not in ("number", "integer"):
        violations.append(_v(
            op_index, "type_mismatch", param,
            f"Parameter '{param}' is non-numeric (type '{declared_type}'); "
            f"delta operations are not applicable.",
        ))
        return violations

    if declared_type == "integer" and not isinstance(delta, int):
        violations.append(_v(
            op_index, "type_mismatch", param,
            f"Parameter '{param}' is integer-typed; delta must be an integer.",
        ))

    lo = pspec.get("minimum")
    hi = pspec.get("maximum")
    if lo is not None and hi is not None:
        full_range = hi - lo
        if abs(delta) > full_range:
            violations.append(_v(
                op_index, "out_of_range", param,
                f"Delta {delta} exceeds the full range "
                f"[{lo}, {hi}] of '{param}' (span {full_range}); "
                f"the operation cannot stay in bounds from any starting value.",
            ))

    declared_unit = pspec.get("unit")
    op_unit = op.get("unit")
    if op_unit and declared_unit and op_unit != declared_unit:
        violations.append(_v(
            op_index, "out_of_schema", param,
            f"Unit '{op_unit}' does not match manifest unit '{declared_unit}' "
            f"for '{param}'.",
        ))

    return violations


def _check_preset(
    op: dict,
    op_index: int,
    presets: set[str] | None,
) -> list[dict]:
    """Validate a single 'preset' op against the registered preset names."""
    name = op["preset"]
    if presets is None:
        # Caller did not supply a preset registry — accept by default,
        # downstream renderer is responsible for resolving the name.
        return []
    if name not in presets:
        return [_v(op_index, "out_of_schema", None,
                   f"Preset '{name}' is not registered for this room type. "
                   f"Available: {sorted(presets) if presets else '(none)'}.")]
    return []


# ---------------------------------------------------------------------------
# Top-level entrypoint
# ---------------------------------------------------------------------------

def validate(
    patch: dict,
    manifest: dict,
    presets: set[str] | None = None,
) -> dict:
    """Validate a patch against a manifest. Returns
    {"ok": bool, "violations": [...]}.

    presets: optional set of registered preset names for this room.
             If None, preset operations are accepted without name-checking.
    """
    # 1. Patch must conform to the patch grammar.
    grammar_validator = Draft202012Validator(PATCH_GRAMMAR)
    grammar_errors = sorted(
        grammar_validator.iter_errors(patch),
        key=lambda e: list(e.absolute_path),
    )
    if grammar_errors:
        violations = [
            _v(None, "schema_invalid", None,
               f"Patch fails patch-grammar schema at "
               f"{list(e.absolute_path) or '<root>'}: {e.message}")
            for e in grammar_errors
        ]
        return {"ok": False, "violations": violations}

    # 2. Each operation must be valid against the manifest.
    manifest_props = manifest.get("properties", {})
    all_violations: list[dict] = []
    for i, op in enumerate(patch["operations"]):
        kind = op["op"]
        if kind == "set":
            all_violations.extend(_check_set(op, i, manifest_props))
        elif kind == "delta":
            all_violations.extend(_check_delta(op, i, manifest_props))
        elif kind == "preset":
            all_violations.extend(_check_preset(op, i, presets))
        else:
            # Unreachable: the grammar's oneOf already enforces op ∈ {set,delta,preset}.
            all_violations.append(_v(
                i, "schema_invalid", None,
                f"Unknown op type '{kind}' (grammar should have caught this).",
            ))

    return {"ok": not all_violations, "violations": all_violations}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a JSON patch against a room manifest.",
    )
    parser.add_argument("--manifest", required=True, type=Path,
                        help="Path to the room manifest (JSON Schema).")
    parser.add_argument("--patch", required=True, type=Path,
                        help="Path to the candidate JSON patch.")
    parser.add_argument("--presets", type=Path, default=None,
                        help="Optional path to a JSON file mapping preset "
                             "names to patches; only the keys are used.")
    args = parser.parse_args(argv)

    try:
        manifest = _load_json(args.manifest)
        patch = _load_json(args.patch)
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"validator.py: failed to load input: {exc}\n")
        return 2

    presets: set[str] | None = None
    if args.presets is not None:
        try:
            preset_data = _load_json(args.presets)
            presets = set(preset_data.keys()) if isinstance(preset_data, dict) else set(preset_data)
        except (OSError, json.JSONDecodeError) as exc:
            sys.stderr.write(f"validator.py: failed to load presets: {exc}\n")
            return 2

    result = validate(patch, manifest, presets=presets)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
