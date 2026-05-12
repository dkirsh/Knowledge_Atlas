#!/usr/bin/env python3
"""validation_gate.py — Task 3 Phase 2 reference implementation.

Validates an LLM-emitted parameter patch against a manifest. Three checks:

    1. Structural: patch is a JSON object with valid op (set | delta | preset).
    2. Range: every value falls within the manifest's [min, max].
    3. Type: every value matches the manifest's declared type.
    4. Name: every targeted parameter exists in the manifest.

Returns either OK or a list of structured violations the LLM can read back.

Usage as a library:

    from validation_gate import validate_patch
    result = validate_patch(patch, manifest)
    if not result["ok"]: print(result["violations"])

Usage as a CLI (for testing):

    python3 validation_gate.py --manifest manifests/living_room.schema.json \\
        --patch params/test_patch.json
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any


VALID_OPS = {"set", "delta", "preset"}


def validate_patch(patch: dict, manifest: dict) -> dict:
    """Return {"ok": bool, "violations": list[dict]}."""
    violations: list[dict] = []

    # Structural
    if not isinstance(patch, dict):
        return {"ok": False, "violations": [{
            "code": "structural", "message": "patch must be a JSON object"
        }]}
    op = patch.get("op")
    if op not in VALID_OPS:
        violations.append({
            "code": "invalid_op", "field": "op", "value": op,
            "message": f"op must be one of {sorted(VALID_OPS)}"
        })
        return {"ok": False, "violations": violations}

    # If preset op, defer to preset registry (out of scope here)
    if op == "preset":
        if not patch.get("preset_name"):
            violations.append({"code": "missing_preset", "message": "preset op requires preset_name"})
        return {"ok": len(violations) == 0, "violations": violations}

    # Set / delta operations
    properties = manifest.get("properties", {})
    if not properties:
        return {"ok": False, "violations": [{
            "code": "manifest_empty", "message": "manifest has no properties block"
        }]}

    target = patch.get("param")
    value = patch.get("value")

    # Name check
    if target not in properties:
        violations.append({
            "code": "unknown_param", "field": "param", "value": target,
            "message": f"param {target!r} not in manifest. Known: {sorted(properties)}"
        })
        return {"ok": False, "violations": violations}

    spec = properties[target]
    expected_type = spec.get("type")

    # Type check
    py_type_map = {
        "number": (int, float),
        "integer": (int,),
        "string": (str,),
        "boolean": (bool,),
    }
    if expected_type in py_type_map:
        if not isinstance(value, py_type_map[expected_type]):
            violations.append({
                "code": "type_mismatch", "field": "value",
                "expected_type": expected_type, "got_type": type(value).__name__,
                "message": f"value for {target} must be {expected_type}, got {type(value).__name__}"
            })
            # type-mismatched values can still range-check incorrectly, so skip range
            return {"ok": False, "violations": violations}

    # Range check (numeric only)
    if expected_type in {"number", "integer"} and isinstance(value, (int, float)):
        lo = spec.get("minimum")
        hi = spec.get("maximum")
        if lo is not None and value < lo:
            violations.append({
                "code": "out_of_range_low", "field": "value", "value": value,
                "minimum": lo,
                "message": f"value {value} below minimum {lo} for {target}"
            })
        if hi is not None and value > hi:
            violations.append({
                "code": "out_of_range_high", "field": "value", "value": value,
                "maximum": hi,
                "message": f"value {value} above maximum {hi} for {target}"
            })

    # Enum check
    if "enum" in spec:
        if value not in spec["enum"]:
            violations.append({
                "code": "enum_violation", "field": "value", "value": value,
                "allowed": spec["enum"],
                "message": f"value {value!r} not in enum {spec['enum']} for {target}"
            })

    # Delta-specific: ensure the resulting value (if applied) is in range
    # (Caller must perform the actual application; we just compute a safe-on-apply hint.)
    if op == "delta" and isinstance(value, (int, float)):
        # Without the current value, we can only check that the delta itself is bounded
        if lo is not None and hi is not None:
            range_size = hi - lo
            if abs(value) > range_size:
                violations.append({
                    "code": "delta_too_large", "field": "value", "value": value,
                    "max_delta": range_size,
                    "message": f"delta {value} exceeds parameter range {range_size}; will fail any base value"
                })

    return {"ok": len(violations) == 0, "violations": violations}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--patch", required=True)
    args = p.parse_args()
    manifest = json.loads(Path(args.manifest).read_text())
    patch = json.loads(Path(args.patch).read_text())
    result = validate_patch(patch, manifest)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
