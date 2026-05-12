#!/usr/bin/env python3
"""llm_wrapper_starter.py — Task 3 Phase 1 starter.

Translates natural-language prompts into validated parameter patches by
function-calling an LLM with the room's manifest as context, then routing
the patch through validation_gate.py before applying it.

This is the SCAFFOLD students adapt. The system prompt, function-call
schema, validation routing, and error-recovery loop are complete; what
students customise is (a) which LLM provider to use (placeholder for
Anthropic / OpenAI / Google API), (b) the example-bank in the prompt,
and (c) any room-specific phrasing nuances.

Usage:

    python3 llm_wrapper_starter.py \\
        --manifest manifests/living_room.schema.json \\
        --prompt "warm up the lighting and raise the ceiling 30 cm"

    # Apply the patch through infinigen_wrapper.py end-to-end
    python3 llm_wrapper_starter.py \\
        --manifest manifests/living_room.schema.json \\
        --prompt "make this restorative" \\
        --apply \\
        --out renders/restorative.gltf
"""
from __future__ import annotations
import argparse, json, os, sys, subprocess, tempfile
from pathlib import Path
from typing import Any

try:
    from validation_gate import validate_patch
except ImportError:
    # Allow running from outside scripts/track3/
    sys.path.insert(0, str(Path(__file__).parent))
    from validation_gate import validate_patch


SYSTEM_PROMPT = """You are a parameter editor for a 3D room.

A user describes a desired change in plain language. Your job is to read the
room's parameter manifest (provided below as JSON Schema) and emit a JSON
patch consisting of one or more operations from the set {set, delta, preset}.

Constraints — VIOLATING THESE RETURNS A REJECTION:
  - Do NOT invent parameter names not in the manifest.
  - Do NOT exceed the manifest's documented [minimum, maximum] for any value.
  - For enum-typed parameters, the value MUST be one of the enum entries.
  - If the user's request cannot be expressed via the manifest, emit a
    structured error with shape {"error": "out_of_schema", "explanation": "..."}.

Output format — ALWAYS valid JSON, never prose. Either:

    {"op": "set",    "param": "<name>", "value": <value>}
    {"op": "delta",  "param": "<name>", "value": <signed_number>}
    {"op": "preset", "preset_name": "<canonical_preset_name>"}

Or, if multiple parameters change, an array of these objects.

Examples (for a living_room manifest with ceiling_height_m, daylight_intensity,
wall_warmth_index, biophilia_count):

  User: "raise the ceiling 30 cm"
  Output: {"op": "delta", "param": "ceiling_height_m", "value": 0.3}

  User: "make the lighting warmer"
  Output: {"op": "delta", "param": "wall_warmth_index", "value": 0.2}

  User: "make this restorative"
  Output: {"op": "preset", "preset_name": "kaplan_restorative_living_room"}

  User: "add a fireplace"
  Output: {"error": "out_of_schema", "explanation": "no fireplace parameter in manifest"}
"""


def call_llm(system: str, user_message: str, manifest: dict) -> str:
    """Stub LLM call — students replace with their preferred provider.

    Returns the raw text the LLM produced. The wrapper parses it into JSON
    afterwards so we can detect malformed output and re-prompt.
    """
    provider = os.environ.get("TRACK3_LLM_PROVIDER", "stub")
    if provider == "anthropic":
        try:
            import anthropic
            client = anthropic.Anthropic()
            msg = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=400,
                system=system + "\n\nManifest:\n" + json.dumps(manifest, indent=2),
                messages=[{"role": "user", "content": user_message}],
            )
            return msg.content[0].text
        except Exception as e:
            return json.dumps({"error": "llm_provider_failure", "explanation": str(e)})
    elif provider == "openai":
        # TODO: students implement
        return json.dumps({"error": "openai_not_implemented"})
    elif provider == "gemini":
        # TODO: students implement
        return json.dumps({"error": "gemini_not_implemented"})
    else:
        # Stub — useful for testing the rest of the pipeline without API costs
        return json.dumps({
            "op": "set", "param": "ceiling_height_m", "value": 2.7,
            "_note": "LLM stub (no provider configured); set TRACK3_LLM_PROVIDER env var"
        })


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--prompt", required=True)
    p.add_argument("--apply", action="store_true",
                   help="After validation, call infinigen_wrapper.py to render the result")
    p.add_argument("--out", help="Output GLB path (required if --apply)")
    p.add_argument("--max-retries", type=int, default=2,
                   help="Re-prompt the LLM if its output fails validation")
    args = p.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())
    user_msg = args.prompt
    last_violations: list = []

    for attempt in range(args.max_retries + 1):
        if last_violations:
            user_msg = (args.prompt + "\n\nPRIOR ATTEMPT FAILED VALIDATION:\n"
                       + json.dumps(last_violations, indent=2)
                       + "\nProduce a corrected patch.")
        raw = call_llm(SYSTEM_PROMPT, user_msg, manifest)
        try:
            patch = json.loads(raw)
        except json.JSONDecodeError:
            last_violations = [{"code": "malformed_json", "raw": raw[:200]}]
            continue
        if isinstance(patch, dict) and "error" in patch:
            print(json.dumps(patch, indent=2))
            return 1  # LLM declined; out_of_schema is a legitimate refusal
        if isinstance(patch, list):
            patches = patch
        else:
            patches = [patch]
        # Validate each operation
        all_ok = True
        all_violations = []
        for sub in patches:
            r = validate_patch(sub, manifest)
            if not r["ok"]:
                all_ok = False
                all_violations.extend(r["violations"])
        if all_ok:
            print(json.dumps({"ok": True, "patches": patches}, indent=2))
            if args.apply:
                if not args.out:
                    sys.stderr.write("--apply requires --out\n"); return 1
                _apply_patches(args.manifest, patches, args.out)
            return 0
        last_violations = all_violations

    sys.stderr.write(f"LLM failed validation after {args.max_retries + 1} attempts.\n")
    sys.stderr.write(json.dumps(last_violations, indent=2) + "\n")
    return 1


def _apply_patches(manifest_path: str, patches: list, out: str) -> None:
    """Resolve the patches into a parameter dict and call infinigen_wrapper."""
    manifest = json.loads(Path(manifest_path).read_text())
    properties = manifest.get("properties", {})
    # Start from defaults
    params = {name: spec.get("default") for name, spec in properties.items()
              if spec.get("default") is not None}
    for p in patches:
        if p["op"] == "set":
            params[p["param"]] = p["value"]
        elif p["op"] == "delta":
            params[p["param"]] = (params.get(p["param"], 0) + p["value"])
    # Write to temp file; call wrapper
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
        json.dump(params, f); pf = f.name
    room = manifest.get("_track3_room_type", "living_room")
    subprocess.run([sys.executable, str(Path(__file__).parent / "infinigen_wrapper.py"),
                    "--room", room, "--params", pf, "--out", out], check=True)
    Path(pf).unlink()


if __name__ == "__main__":
    sys.exit(main())
