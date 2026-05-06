#!/usr/bin/env python3
"""
test_validator.py — Test suite for validator.py.

Track 3 · Task 1 / Task 3 cross-cutting deliverable
Author: Paco Yan (payan@ucsd.edu)

Exercises the contract from Task 3 / Phase 2:
    >= 5 valid cases (single set, single delta, single preset,
                       multi-op patch, edge-of-range value)
    >= 3 invalid cases (unknown param, value above max, type mismatch)

Adds a few extra invalid cases (schema_invalid, enum out_of_schema,
delta on non-numeric) because these are realistic LLM failure modes
the gate must catch.

Run from the project folder:
    python test_validator.py
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from validator import validate


HERE = Path(__file__).parent
KITCHEN = json.loads((HERE / "kitchen.manifest.json").read_text(encoding="utf-8"))
DINING = json.loads((HERE / "dining_room.manifest.json").read_text(encoding="utf-8"))

# A pretend preset registry the LLM front-end might inject.
KITCHEN_PRESETS = {"meyers_levy_low_ceiling", "ulrich_warm_kitchen"}


def _patch(room: str, *ops: dict) -> dict:
    """Tiny constructor for compact test cases."""
    return {
        "room_id": room,
        "manifest_version": "1",
        "operations": list(ops),
    }


# ---------------------------------------------------------------------------
# Valid patches — should return ok=True with no violations.
# ---------------------------------------------------------------------------

class ValidPatches(unittest.TestCase):

    def test_single_set_in_range(self):
        """Plain set on a numeric param within bounds."""
        patch = _patch("kitchen_001",
                       {"op": "set", "param": "ceiling_height_m",
                        "value": 2.6, "unit": "m"})
        result = validate(patch, KITCHEN)
        self.assertTrue(result["ok"], result["violations"])

    def test_single_delta_within_full_span(self):
        """Delta whose magnitude is less than the full range."""
        patch = _patch("kitchen_001",
                       {"op": "delta", "param": "ceiling_height_m",
                        "delta": 0.3, "unit": "m"})
        result = validate(patch, KITCHEN)
        self.assertTrue(result["ok"], result["violations"])

    def test_single_preset_registered(self):
        """Preset op naming a registered preset."""
        patch = _patch("kitchen_001",
                       {"op": "preset", "preset": "meyers_levy_low_ceiling"})
        result = validate(patch, KITCHEN, presets=KITCHEN_PRESETS)
        self.assertTrue(result["ok"], result["violations"])

    def test_multi_op_patch(self):
        """Combination of set + delta + enum set in one patch."""
        patch = _patch(
            "kitchen_001",
            {"op": "set", "param": "ceiling_height_m", "value": 3.0, "unit": "m"},
            {"op": "delta", "param": "cabinet_density", "delta": -0.2},
            {"op": "set", "param": "countertop_material", "value": "oak"},
        )
        result = validate(patch, KITCHEN)
        self.assertTrue(result["ok"], result["violations"])

    def test_edge_of_range_value(self):
        """Set to the maximum legal value (inclusive bound check)."""
        patch = _patch("dining_001",
                       {"op": "set", "param": "ceiling_height_m",
                        "value": 3.5, "unit": "m"})
        result = validate(patch, DINING)
        self.assertTrue(result["ok"], result["violations"])

    def test_integer_at_max(self):
        """Integer-typed parameter at its declared maximum."""
        patch = _patch("dining_001",
                       {"op": "set", "param": "biophilia_count", "value": 4})
        result = validate(patch, DINING)
        self.assertTrue(result["ok"], result["violations"])


# ---------------------------------------------------------------------------
# Invalid patches — should return ok=False with the expected violation code.
# ---------------------------------------------------------------------------

class InvalidPatches(unittest.TestCase):

    def _assert_code(self, result: dict, code: str, op_index: int | None = 0) -> None:
        self.assertFalse(result["ok"], "expected violations, got ok=True")
        codes = [v["code"] for v in result["violations"]]
        self.assertIn(code, codes,
                      f"expected violation code '{code}', got {codes}")
        if op_index is not None:
            indices = [v["op_index"] for v in result["violations"]
                       if v["code"] == code]
            self.assertIn(op_index, indices,
                          f"expected op_index {op_index} for code '{code}', "
                          f"got {indices}")

    def test_unknown_param(self):
        """LLM hallucinates a parameter name (the spec's canonical example:
        ceiling_h_meters instead of ceiling_height_m)."""
        patch = _patch("kitchen_001",
                       {"op": "set", "param": "ceiling_h_meters", "value": 2.7})
        self._assert_code(validate(patch, KITCHEN), "unknown_param")

    def test_value_above_max(self):
        """LLM emits a numerically out-of-range value (spec example:
        ceiling_height_m: 47.0)."""
        patch = _patch("kitchen_001",
                       {"op": "set", "param": "ceiling_height_m", "value": 47.0})
        self._assert_code(validate(patch, KITCHEN), "out_of_range")

    def test_type_mismatch(self):
        """LLM puts a string where a number is required."""
        patch = _patch("kitchen_001",
                       {"op": "set", "param": "ceiling_height_m",
                        "value": "tall"})
        self._assert_code(validate(patch, KITCHEN), "type_mismatch")

    def test_schema_invalid_missing_required(self):
        """Patch is missing the required 'operations' key — fails the
        patch-grammar JSON Schema before any manifest checks run."""
        patch = {"room_id": "kitchen_001"}  # no 'operations'
        self._assert_code(validate(patch, KITCHEN), "schema_invalid", op_index=None)

    def test_enum_value_not_allowed(self):
        """Enum-valued parameter receives an unlisted token."""
        patch = _patch("kitchen_001",
                       {"op": "set", "param": "countertop_material",
                        "value": "concrete"})
        self._assert_code(validate(patch, KITCHEN), "out_of_schema")

    def test_delta_on_enum_param(self):
        """Delta op targeting a non-numeric parameter."""
        patch = _patch("kitchen_001",
                       {"op": "delta", "param": "countertop_material",
                        "delta": 0.5})
        self._assert_code(validate(patch, KITCHEN), "type_mismatch")

    def test_unit_mismatch(self):
        """Set op declares a unit that does not match the manifest's unit."""
        patch = _patch("kitchen_001",
                       {"op": "set", "param": "ceiling_height_m",
                        "value": 2.6, "unit": "K"})
        self._assert_code(validate(patch, KITCHEN), "out_of_schema")

    def test_unregistered_preset(self):
        """Preset op referring to a name not in the registry."""
        patch = _patch("kitchen_001",
                       {"op": "preset", "preset": "this_preset_does_not_exist"})
        self._assert_code(validate(patch, KITCHEN, presets=KITCHEN_PRESETS),
                          "out_of_schema")


if __name__ == "__main__":
    unittest.main(verbosity=2)
