#!/usr/bin/env python3
"""
infinigen_wrapper.py — Track 3 Task 2 wrapper (slice scope).

Author: Paco Yan (payan@ucsd.edu)
Track 3 · Task 2 · Phase 1

Contract per Task 2 PDF:

    python3 infinigen_wrapper.py \\
        --manifest manifests/kitchen.manifest.json \\
        --params   params/kitchen_default.json \\
        --out      renders/kitchen_default.gltf

Produces two files:
    <out>.gltf       — the rendered scene (real or stub).
    <out>.meta.json  — sidecar with resolved params, manifest version,
                       Infinigen commit, render time, and the wrapper mode.

Slice scope
-----------
Only `ceiling_height_m` is currently routed to a real Infinigen knob
(`RoomConstants.wall_height` via gin override). All other manifest
parameters validate fine but no-op with a warning recorded in the
sidecar's `unsupported_params` list. The wrapper grows mechanically:
add an entry to PARAM_TRANSLATORS for each parameter as its mapping is
verified.

Two execution modes
-------------------
--stub  (default)  Produces a placeholder glTF and sidecar without
                   invoking Blender. Used for fast plumbing tests and
                   for environments where Infinigen is not installed.
                   Render time is reported as 0.

--real             Invokes Blender + Infinigen for an actual render.
                   Requires:
                     * `blender` on PATH (or set --blender-bin)
                     * Infinigen cloned (default: /home/poca/infinigen,
                       override with --infinigen-root)
                   Calls the entry point at
                   `infinigen/infinigen_examples/generate_indoors.py`
                   with gin overrides translated from the manifest
                   parameters.

Validator integration
---------------------
Reuses validator.py (Track 3 / Task 3 / Phase 2 deliverable). The
flat params dict from Task 2 is internally converted to a series of
`set` operations and validated against the manifest with the same gate
the LLM front-end will use in Task 3.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Reuse our patch validator. It lives next to this file.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validator import validate as validate_patch  # noqa: E402


# ---------------------------------------------------------------------------
# Param translators — manifest name → Infinigen gin overrides
# ---------------------------------------------------------------------------
# Each entry maps a manifest parameter name to a callable that takes the
# resolved value and returns a list of gin override strings. Missing entries
# mean "validate but don't yet route" — handled as unsupported_params in
# the sidecar.
#
# See parameter_source_mapping.md for the verification trail of each row.
# ---------------------------------------------------------------------------

PARAM_TRANSLATORS: dict[str, Any] = {
    # ── Aliased parameters (one gin override each) ─────────────────────────
    # ceiling_height_m → RoomConstants.wall_height
    # Verified at core/constraints/constraint_language/constants.py:31
    "ceiling_height_m": lambda v: [f"RoomConstants.wall_height={v}"],

    # lighting_warmth → PointLampFactory.params['Temperature']  (Kelvin)
    # Verified at assets/lighting/indoor_lights.py:25.
    # Mapping: 0.0 (cool, ~6500 K) ↔ 1.0 (warm, ~2700 K).
    # Infinigen's clip_gaussian floor is 3500 K, so values below ~0.79
    # produce temperatures inside Infinigen's documented band; lower
    # warmth values (≥0.79) are clamped to 3500 K by Infinigen at runtime.
    # Note: gin-override propagation through PointLampFactory.params (a
    # dict built inside __init__ from random samples) is provisional
    # until --real mode confirms it; if propagation fails, the next
    # increment switches to wrapper-side scene post-processing.
    "lighting_warmth":    lambda v: [f"PointLampFactory.params['Temperature']={round(6500 - v * 3800, 1)}"],

    # lighting_intensity → PointLampFactory.params['Wattage']
    # Verified at assets/lighting/indoor_lights.py:25.
    # Mapping: 0.0 → 20 W (dim) ↔ 1.0 → 200 W (bright). Infinigen's
    # default U(40, 100) sits in the middle of this range. Same
    # propagation caveat as lighting_warmth.
    "lighting_intensity": lambda v: [f"PointLampFactory.params['Wattage']={round(20 + v * 180, 1)}"],

    # ── Aspirational (computed) — not yet routed ──────────────────────────
    # Per parameter_source_mapping.md, the remaining 7 parameters need
    # wrapper-side derivation logic (constraint-solver weights, instance
    # counts, material-list filtering). They land in subsequent increments.
}


# ---------------------------------------------------------------------------
# Param resolution: fill defaults, validate ranges
# ---------------------------------------------------------------------------

def resolve_params(params: dict, manifest: dict) -> dict:
    """Fill in any parameter the user omitted with its manifest default.
    Does not validate ranges — that is `validate_resolved_params`'s job."""
    resolved = dict(params)
    for name, spec in manifest.get("properties", {}).items():
        if name not in resolved and "default" in spec:
            resolved[name] = spec["default"]
    return resolved


def validate_resolved_params(params: dict, manifest: dict) -> dict:
    """Run params through the patch validator by encoding each entry as
    a `set` op. Returns the validator's standard {ok, violations} shape."""
    operations = [{"op": "set", "param": k, "value": v}
                  for k, v in params.items()]
    patch = {
        "room_id": "wrapper-internal",
        "manifest_version": str(manifest.get("$id", "1")),
        "operations": operations,
    }
    return validate_patch(patch, manifest)


# ---------------------------------------------------------------------------
# Translation: resolved params → gin overrides + warnings
# ---------------------------------------------------------------------------

def translate_params(resolved: dict) -> tuple[list[str], list[str]]:
    """Return (gin_overrides, unsupported_params).

    unsupported_params lists names that were valid against the manifest
    but have no PARAM_TRANSLATORS entry yet — accepted but not routed.
    """
    gin_overrides: list[str] = []
    unsupported: list[str] = []
    for name, value in resolved.items():
        translator = PARAM_TRANSLATORS.get(name)
        if translator is None:
            unsupported.append(name)
            continue
        gin_overrides.extend(translator(value))
    return gin_overrides, unsupported


# ---------------------------------------------------------------------------
# Output: stub glTF + sidecar JSON
# ---------------------------------------------------------------------------

# A minimal valid glTF 2.0 (single empty scene). model-viewer loads it without
# erroring — useful as a placeholder when running --stub for plumbing tests.
_STUB_GLTF = {
    "asset": {
        "version": "2.0",
        "generator": "Track 3 infinigen_wrapper.py stub mode",
    },
    "scene": 0,
    "scenes": [{"name": "stub", "nodes": []}],
    "nodes": [],
}


def write_stub_gltf(out_path: Path) -> None:
    """Write a placeholder glTF file."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(_STUB_GLTF, fh, indent=2)


def get_infinigen_commit(infinigen_root: Path | None) -> str:
    """Best-effort: ask git for the current commit hash of the Infinigen repo."""
    if infinigen_root is None or not infinigen_root.exists():
        return "unknown"
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(infinigen_root),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "unknown"


def write_sidecar(
    out_gltf: Path,
    manifest_filename: str,
    manifest_version: str,
    infinigen_commit: str,
    resolved_params: dict,
    gin_overrides: list[str],
    unsupported_params: list[str],
    render_time_seconds: float,
    mode: str,
) -> Path:
    """Write the .meta.json sidecar next to the glTF (per Task 2 spec)."""
    sidecar_path = out_gltf.with_suffix(out_gltf.suffix + ".meta.json")
    sidecar = {
        "manifest": manifest_filename,
        "manifest_version": manifest_version,
        "infinigen_commit": infinigen_commit,
        "params_resolved": resolved_params,
        "gin_overrides": gin_overrides,
        "unsupported_params": unsupported_params,
        "render_time_seconds": round(render_time_seconds, 3),
        "rendered_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "wrapper_mode": mode,
        "wrapper_version": "0.1.0-slice",
    }
    with sidecar_path.open("w", encoding="utf-8") as fh:
        json.dump(sidecar, fh, indent=2)
    return sidecar_path


# ---------------------------------------------------------------------------
# --real mode: invoke Blender + Infinigen
# ---------------------------------------------------------------------------

def invoke_infinigen(
    blender_bin: str,
    infinigen_root: Path,
    gin_overrides: list[str],
    out_gltf: Path,
    seed: int,
) -> float:
    """Run generate_indoors.py through Blender. Returns wall-clock seconds.
    Raises CalledProcessError if Infinigen exits non-zero."""
    entry_point = infinigen_root / "infinigen_examples" / "generate_indoors.py"
    if not entry_point.exists():
        raise FileNotFoundError(
            f"Infinigen entry point not found at {entry_point}. "
            f"Did you set --infinigen-root correctly?"
        )

    # Infinigen's gin override flag is `-g` / `--gin_param`; multiple overrides
    # are passed as separate -g arguments.
    gin_args: list[str] = []
    for override in gin_overrides:
        gin_args.extend(["-g", override])

    cmd = [
        blender_bin,
        "--background",
        "--python", str(entry_point),
        "--",
        "--seed", str(seed),
        "--output_folder", str(out_gltf.parent),
        "--task", "coarse",  # generate the room shell + coarse layout
        *gin_args,
    ]

    start = time.monotonic()
    subprocess.run(cmd, check=True, cwd=str(infinigen_root))
    elapsed = time.monotonic() - start

    # NOTE: the actual glTF export step from Infinigen → Blender → glTF still
    # needs to be wired (Task 2 Phase 1 says: bake the scene then call
    # bpy.ops.export_scene.gltf with GLTF_EMBEDDED). For the slice we treat
    # successful Infinigen invocation as the milestone and leave the glTF
    # export to the next wrapper increment. The stub glTF is written so
    # downstream tools (model-viewer, the gallery script) don't break.
    if not out_gltf.exists():
        write_stub_gltf(out_gltf)

    return elapsed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--params", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path,
                        help="Output glTF path. Sidecar is written next to it.")
    parser.add_argument("--real", action="store_true",
                        help="Invoke Blender + Infinigen. Default is --stub.")
    parser.add_argument("--blender-bin", default="blender",
                        help="Path to the Blender binary (default: 'blender' on PATH).")
    parser.add_argument("--infinigen-root", type=Path,
                        default=Path("/home/poca/infinigen"),
                        help="Path to the Infinigen clone root (default: /home/poca/infinigen).")
    parser.add_argument("--seed", type=int, default=42,
                        help="Infinigen seed for deterministic generation (default: 42).")
    args = parser.parse_args(argv)

    # Load inputs
    try:
        manifest = _load_json(args.manifest)
        params = _load_json(args.params)
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"infinigen_wrapper.py: failed to load input: {exc}\n")
        return 2

    if not isinstance(params, dict):
        sys.stderr.write("infinigen_wrapper.py: --params file must contain a JSON object.\n")
        return 2

    # Resolve + validate
    resolved = resolve_params(params, manifest)
    verdict = validate_resolved_params(resolved, manifest)
    if not verdict["ok"]:
        sys.stderr.write("infinigen_wrapper.py: parameter validation failed:\n")
        for v in verdict["violations"]:
            sys.stderr.write(f"  [{v['code']}] {v.get('param')}: {v['message']}\n")
        return 1

    # Translate to gin overrides
    gin_overrides, unsupported = translate_params(resolved)
    if unsupported:
        sys.stderr.write(
            "infinigen_wrapper.py: warning — these manifest parameters validated "
            "but are not yet routed to Infinigen:\n"
        )
        for name in unsupported:
            sys.stderr.write(f"  - {name} (recorded in sidecar.unsupported_params)\n")

    # Render
    mode = "real" if args.real else "stub"
    if mode == "real":
        try:
            render_time = invoke_infinigen(
                blender_bin=args.blender_bin,
                infinigen_root=args.infinigen_root,
                gin_overrides=gin_overrides,
                out_gltf=args.out,
                seed=args.seed,
            )
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            sys.stderr.write(f"infinigen_wrapper.py: real render failed: {exc}\n")
            return 3
    else:
        write_stub_gltf(args.out)
        render_time = 0.0

    # Sidecar
    infinigen_commit = get_infinigen_commit(
        args.infinigen_root if args.infinigen_root.exists() else None
    )
    manifest_version = str(manifest.get("$id", "1"))
    sidecar_path = write_sidecar(
        out_gltf=args.out,
        manifest_filename=args.manifest.name,
        manifest_version=manifest_version,
        infinigen_commit=infinigen_commit,
        resolved_params=resolved,
        gin_overrides=gin_overrides,
        unsupported_params=unsupported,
        render_time_seconds=render_time,
        mode=mode,
    )

    # Summary to stdout
    print(f"Wrote glTF:    {args.out}  ({mode} mode)")
    print(f"Wrote sidecar: {sidecar_path}")
    print(f"Render time:   {render_time:.3f} s")
    if gin_overrides:
        print(f"Gin overrides: {gin_overrides}")
    if unsupported:
        print(f"Unsupported (validated, not routed): {unsupported}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
