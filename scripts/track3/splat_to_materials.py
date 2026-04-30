#!/usr/bin/env python3
"""splat_to_materials.py — Track 3 Phase 2.5 splat-augmentation scaffold.

Takes a 3D Gaussian Splatting capture plus a list of region selections and
produces a library of PBR (Physically-Based Rendering) material packs the
parametric Infinigen renderer applies to surfaces. Each pack is:

    <library>/<target_class>/<region_name>/
        albedo.png      — base colour, sRGB
        normal.png      — tangent-space normals, RG = XY, B = Z
        roughness.png   — surface microfacet roughness, 8-bit grayscale
        metallic.png    — metallic-vs-dielectric, 8-bit grayscale
        manifest.json   — splat source, region bbox, target_class, etc.

Per the Sprint-3 panel addendum: splats supply *realism layers* over the
parametric Track 3 pipeline. The parametric models stay editable; the
splat-derived materials accumulate into a class-keyed library that any
parametric room can draw from at render time.

Algorithm (Sprint 5 fills in the real implementation):
    1. Load splat file -> per-Gaussian {position, opacity, SH colour}
    2. For each region in regions.json:
        a. Project the Gaussians inside the region's 3D bbox onto the
           bbox's largest face (the "material plane")
        b. Sample SH coefficients per output texel -> resolve albedo
        c. Estimate normals from local Gaussian orientation gradients
        d. Estimate roughness from per-Gaussian opacity variance
        e. Estimate metallic from albedo + roughness coupling (heuristic)
    3. Save 4 PBR maps + manifest.json into the output directory

Regions JSON schema (regions.json):
    [
      {
        "name": "kitchen_counter_north",
        "bbox": [[xmin, ymin, zmin], [xmax, ymax, zmax]],
        "target_class": "granite"
      },
      ...
    ]

Usage:

    # Single-room mode (flat output)
    python3 splat_to_materials.py --splat scans/kitchen.splat \\
        --regions regions.json \\
        --out-dir 3d_rooms/kitchen/materials/

    # Library mode (organized by target_class for cohort-wide accumulation)
    python3 splat_to_materials.py --splat scans/kitchen.splat \\
        --regions regions.json \\
        --out-dir 3d_rooms/_materials_library/ \\
        --library-mode

If splat libraries (splatviz, nerfstudio, gsplat) are unavailable, writes
stub PBR packs (4x4 placeholder PNGs) with manifest.json explaining the
scaffold state, so students can verify the wrapper signal-path before the
Sprint 5 implementation lands.

Sprint 4 deliverable: this SCAFFOLD (CLI + file I/O + library
organization + stub mode + documentation). Sprint 5 implementer fills in
real SH-coefficient sampling and PBR-channel separation.
"""
from __future__ import annotations
import argparse, json, struct, sys, time, zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


VALID_EXTENSIONS = {".ply", ".splat"}
PBR_CHANNELS = ("albedo", "normal", "roughness", "metallic")


# ──────────────────────────────────────────────────────────────────
# Splat + regions validation
# ──────────────────────────────────────────────────────────────────

def validate_splat_file(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, f"File not found: {path}"
    if path.suffix.lower() not in VALID_EXTENSIONS:
        return False, f"Unexpected extension {path.suffix!r}; expected one of {sorted(VALID_EXTENSIONS)}"
    if path.stat().st_size < 64:
        return False, f"File too small ({path.stat().st_size} bytes); likely truncated"
    return True, "ok"


def load_regions(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Regions file not found: {path}")
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise ValueError(f"Regions JSON must be a list, got {type(data).__name__}")
    for i, r in enumerate(data):
        for required in ("name", "bbox", "target_class"):
            if required not in r:
                raise ValueError(f"Region {i} missing required field {required!r}")
        bbox = r["bbox"]
        if (not isinstance(bbox, list) or len(bbox) != 2
                or not all(isinstance(corner, list) and len(corner) == 3 for corner in bbox)):
            raise ValueError(
                f"Region {i!r} bbox must be [[xmin,ymin,zmin],[xmax,ymax,zmax]], got {bbox!r}"
            )
    return data


# ──────────────────────────────────────────────────────────────────
# Real extraction (Sprint 5 fills in)
# ──────────────────────────────────────────────────────────────────

def extract_pbr_pack(splat_path: Path, region: dict) -> Optional[dict]:
    """Extract per-region PBR maps from the splat.

    Returns a dict {channel: (H, W) numpy array} or None if splat
    libraries are unavailable.
    """
    try:
        import numpy as np  # noqa: F401
        import nerfstudio  # noqa: F401  # type: ignore
    except ImportError:
        return None

    # ── Sprint 5 implementer fills in below ──────────────────────
    # 1. gaussians = load_splat(splat_path)
    # 2. region_gaussians = filter_by_bbox(gaussians, region["bbox"])
    # 3. plane = largest_face(region["bbox"])
    # 4. albedo  = project_and_resolve_sh(region_gaussians, plane, channels=3)
    # 5. normal  = estimate_normals_from_orientation(region_gaussians, plane)
    # 6. roughness = estimate_roughness_from_opacity_variance(region_gaussians, plane)
    # 7. metallic = heuristic_metallic_from_albedo_roughness(albedo, roughness)
    # 8. return {"albedo": albedo, "normal": normal,
    #            "roughness": roughness, "metallic": metallic}
    raise NotImplementedError(
        "Sprint 5 deliverable: SH-coefficient projection + PBR channel separation."
    )


# ──────────────────────────────────────────────────────────────────
# Stub PNG writer (no PIL dependency — minimal PNG encoder)
# ──────────────────────────────────────────────────────────────────

def _png_chunk(tag: bytes, data: bytes) -> bytes:
    chunk = tag + data
    return (struct.pack(">I", len(data)) + chunk
            + struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF))


def write_stub_png(path: Path, channel: str, size: int = 4) -> None:
    """Write a minimal 4x4 8-bit PNG. Greyscale fill chosen per channel."""
    fills = {
        "albedo":    0x80,  # mid-gray
        "normal":    0x80,  # 0x8080FF in RGB; here we go grayscale 0x80 to keep it 1-channel
        "roughness": 0xC0,  # high roughness placeholder
        "metallic":  0x10,  # low metallic placeholder (dielectric)
    }
    fill = fills.get(channel, 0x80)
    # PNG signature
    sig = b"\x89PNG\r\n\x1a\n"
    # IHDR: width, height, bitdepth=8, colortype=0 (grayscale), compression=0, filter=0, interlace=0
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 0, 0, 0, 0)
    # IDAT: filter byte 0 + size pixels per row
    raw = b""
    for _ in range(size):
        raw += b"\x00" + bytes([fill]) * size
    idat = zlib.compress(raw)
    iend = b""
    path.write_bytes(
        sig + _png_chunk(b"IHDR", ihdr) + _png_chunk(b"IDAT", idat) + _png_chunk(b"IEND", iend)
    )


def write_real_png(path: Path, array) -> None:
    """Sprint 5: replace with PIL.Image.fromarray(array).save(path)."""
    raise NotImplementedError(
        "Sprint 5 deliverable: real PNG writer with PIL or imageio."
    )


# ──────────────────────────────────────────────────────────────────
# Pack writer
# ──────────────────────────────────────────────────────────────────

def resolve_pack_dir(out_dir: Path, region: dict, library_mode: bool) -> Path:
    """Compute the destination directory for a region's pack."""
    if library_mode:
        return out_dir / region["target_class"] / region["name"]
    return out_dir / region["name"]


def write_pack(
    pack_dir: Path,
    splat_path: Path,
    region: dict,
    pbr_arrays: Optional[dict],
    stub: bool,
) -> None:
    pack_dir.mkdir(parents=True, exist_ok=True)
    for channel in PBR_CHANNELS:
        target = pack_dir / f"{channel}.png"
        if stub or pbr_arrays is None:
            write_stub_png(target, channel)
        else:
            write_real_png(target, pbr_arrays[channel])
    # Manifest
    manifest = {
        "tool": "splat_to_materials.py",
        "tool_version": "0.1.0-sprint4-scaffold",
        "splat_source": str(splat_path),
        "region_name": region["name"],
        "region_bbox": region["bbox"],
        "target_class": region["target_class"],
        "extraction_date_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rendering_convention": "PBR Metallic-Roughness (glTF 2.0)",
        "channels": {
            "albedo":    "sRGB base colour",
            "normal":    "tangent-space normal map (R=X, G=Y, B=Z)",
            "roughness": "linear, 0=mirror smooth, 1=fully rough",
            "metallic":  "linear, 0=dielectric, 1=conductor",
        },
        "stub": stub,
        "stub_note": (
            "Stub 4x4 placeholder PNGs written; install splat libraries and re-run "
            "for real PBR extraction." if stub else None
        ),
    }
    (pack_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))


# ──────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(
        description="Extract PBR material packs from a 3D Gaussian Splatting capture.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--splat", required=True, type=Path,
                   help="Input splat file (.ply or .splat)")
    p.add_argument("--regions", required=True, type=Path,
                   help="JSON file: list of {name, bbox, target_class}")
    p.add_argument("--out-dir", required=True, type=Path,
                   help="Output directory for material packs")
    p.add_argument("--library-mode", action="store_true",
                   help="Organize outputs by target_class (granite/, marble/, oak/...) "
                        "for cohort-wide library accumulation")
    args = p.parse_args()

    splat_path: Path = args.splat.resolve()
    regions_path: Path = args.regions.resolve()
    out_dir: Path = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    ok, reason = validate_splat_file(splat_path)
    if not ok:
        sys.stderr.write(f"\033[91mSplat validation failed: {reason}\033[0m\n")
        return 1

    try:
        regions = load_regions(regions_path)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        sys.stderr.write(f"\033[91mRegions file invalid: {e}\033[0m\n")
        return 1

    print(f"\033[96mProcessing {len(regions)} region(s) from {splat_path.name}...\033[0m")
    t0 = time.time()
    stub_mode = False
    written = []

    for region in regions:
        pack_dir = resolve_pack_dir(out_dir, region, args.library_mode)
        try:
            pbr = extract_pbr_pack(splat_path, region)
        except NotImplementedError:
            pbr = None
        if pbr is None:
            stub_mode = True
            write_pack(pack_dir, splat_path, region, None, stub=True)
        else:
            write_pack(pack_dir, splat_path, region, pbr, stub=False)
        written.append(str(pack_dir))

    elapsed = time.time() - t0

    if stub_mode:
        sys.stderr.write(
            "\033[93mSplat libraries not installed (need numpy + nerfstudio / "
            "splatviz / gsplat). Wrote stub PBR packs for smoke-test only.\033[0m\n"
            "\033[96mTo install: pip3 install --break-system-packages numpy nerfstudio\033[0m\n"
        )
        print(f"\033[93mOK (STUB): wrote {len(written)} pack(s) into {out_dir} "
              f"({elapsed:.1f}s)\033[0m")
    else:
        print(f"\033[92mOK: wrote {len(written)} pack(s) into {out_dir} "
              f"({elapsed:.1f}s)\033[0m")
    for path in written:
        print(f"  - {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
