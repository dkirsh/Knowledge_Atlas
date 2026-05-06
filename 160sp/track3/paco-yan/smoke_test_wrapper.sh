#!/usr/bin/env bash
# smoke_test_wrapper.sh — exercise the wrapper end-to-end in stub mode.
#
# Runs 5 cases (3 valid, 2 invalid) and dumps everything Claude needs to
# verify into smoke_test.out.txt in this folder.
#
# Usage (from WSL):
#     bash "/mnt/c/Users/user/Documents/Claude/Projects/Cogs 160/smoke_test_wrapper.sh"

set -u

CWD="/mnt/c/Users/user/Documents/Claude/Projects/Cogs 160"
OUT="$CWD/smoke_test.out.txt"
cd "$CWD" || exit 1

# Ensure jsonschema (validator.py dependency) is installed in the active env.
# Idempotent: no-op if already installed.
python3 -c "import jsonschema" 2>/dev/null || {
  echo "Installing jsonschema into $(python3 -c 'import sys; print(sys.executable)')..."
  pip install jsonschema --quiet 2>&1 | tail -3
}

# Make sure we have a fresh renders/ dir
rm -rf renders/
mkdir -p renders/

run_case() {
  local label="$1"
  local manifest="$2"
  local params_file="$3"
  local out_gltf="$4"
  echo
  echo "================================================================"
  echo "## $label"
  echo "## manifest: $manifest"
  echo "## params:   $params_file"
  echo "================================================================"
  python3 infinigen_wrapper.py \
    --manifest "$manifest" \
    --params   "$params_file" \
    --out      "$out_gltf" 2>&1
  echo "exit=$?"
}

{
  echo "================================================================"
  echo "WRAPPER SMOKE TEST — generated $(date -Iseconds)"
  echo "Python: $(python3 --version 2>&1)"
  echo "================================================================"

  run_case "TEST 1: kitchen default"          "kitchen.manifest.json"     "params/kitchen_default.json"        "renders/kitchen_default.gltf"
  run_case "TEST 2: kitchen low ceiling 2.0m" "kitchen.manifest.json"     "params/kitchen_low_ceiling.json"    "renders/kitchen_low.gltf"
  run_case "TEST 3: kitchen high ceiling 3.2m" "kitchen.manifest.json"    "params/kitchen_high_ceiling.json"   "renders/kitchen_high.gltf"
  run_case "TEST 4: kitchen above-max (should reject, exit=1)" "kitchen.manifest.json" "params/kitchen_BAD_above_max.json"  "renders/kitchen_bad1.gltf"
  run_case "TEST 5: kitchen unknown param (should reject, exit=1)" "kitchen.manifest.json" "params/kitchen_BAD_unknown_param.json" "renders/kitchen_bad2.gltf"
  run_case "TEST 6: dining default (exercises lighting_intensity)" "dining_room.manifest.json" "params/dining_default.json" "renders/dining_default.gltf"

  echo
  echo "================================================================"
  echo "## Files produced in renders/:"
  echo "================================================================"
  ls -la renders/ 2>&1

  echo
  echo "================================================================"
  echo "## Sidecar contents (TEST 1: default):"
  echo "================================================================"
  cat renders/kitchen_default.gltf.meta.json 2>&1 || echo "(missing)"

  echo
  echo "================================================================"
  echo "## Sidecar contents (TEST 3: high ceiling):"
  echo "================================================================"
  cat renders/kitchen_high.gltf.meta.json 2>&1 || echo "(missing)"

  echo
  echo "================================================================"
  echo "## Sidecar contents (TEST 6: dining default):"
  echo "================================================================"
  cat renders/dining_default.gltf.meta.json 2>&1 || echo "(missing)"

  echo
  echo "================================================================"
  echo "## Stub glTF contents (TEST 1):"
  echo "================================================================"
  cat renders/kitchen_default.gltf 2>&1 || echo "(missing)"

  echo
  echo "================================================================"
  echo "## Done"
  echo "================================================================"
  echo "Output written to: $OUT"
} > "$OUT" 2>&1

echo "Smoke test complete. Output at:"
echo "  $OUT"
