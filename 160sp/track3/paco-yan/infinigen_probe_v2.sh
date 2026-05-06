#!/usr/bin/env bash
# infinigen_probe_v2.sh — second-pass probe.
#
# v1 confirmed which factory classes exist and that most knob names in
# Paco's manifests don't appear in source. v2 reads the actual class
# definitions to find the REAL knob names, and looks for how room
# dimensions (ceiling_height) are controlled.
#
# Usage (from WSL):
#     conda activate infinigen
#     bash "/mnt/c/Users/user/Documents/Claude/Projects/Cogs 160/infinigen_probe_v2.sh"

set -u

OUT="/mnt/c/Users/user/Documents/Claude/Projects/Cogs 160/infinigen_probe_v2.out.txt"
INF=/home/poca/infinigen/infinigen
KA=/home/poca/Knowledge_Atlas

# Helper: print the class body up to ~80 lines after the class definition
print_class() {
  local file="$1"
  local lineno="$2"
  echo "=== $file (line $lineno) ==="
  if [ -f "$file" ]; then
    sed -n "${lineno},$((lineno + 80))p" "$file"
  else
    echo "(file missing)"
  fi
  echo
}

{
  echo "================================================================"
  echo "INFINIGEN PROBE V2 — generated $(date -Iseconds)"
  echo "================================================================"
  echo

  # ---------- Factory class bodies ----------
  echo "================================================================"
  echo "## Factory class definitions (the actual knob signatures)"
  echo "================================================================"
  echo

  print_class "$INF/assets/objects/shelves/single_cabinet.py" 301
  print_class "$INF/assets/objects/tableware/bowl.py" 18
  print_class "$INF/assets/objects/tableware/bottle.py" 24
  print_class "$INF/assets/objects/bathroom/hardware.py" 18
  print_class "$INF/assets/objects/windows/window.py" 60
  print_class "$INF/assets/objects/lamp/ceiling_lights.py" 28
  print_class "$INF/assets/lighting/indoor_lights.py" 25
  print_class "$INF/assets/objects/lamp/lamp.py" 195
  print_class "$INF/assets/objects/tableware/plant_container.py" 128
  print_class "$INF/assets/objects/seating/chairs/chair.py" 35

  # ---------- Search for room/ceiling dimension control ----------
  echo "================================================================"
  echo "## How is ceiling height / room dimensions controlled?"
  echo "================================================================"
  echo
  echo "--- 'ceiling' (case-insensitive, broader than v1) in source:"
  grep -rni "ceiling" "$INF" --include="*.py" 2>/dev/null \
    | grep -v __pycache__ \
    | head -30

  echo
  echo "--- 'wall_height' / 'room_height' / 'shell_height':"
  grep -rn -E "wall_height|room_height|shell_height" "$INF" --include="*.py" 2>/dev/null \
    | grep -v __pycache__ \
    | head -20

  echo
  echo "--- gin config files (Infinigen uses gin for parameterisation):"
  find "$INF" -name "*.gin" 2>/dev/null | head -20
  echo "--- gin files in $INF/datagen/configs/:"
  ls -la "$INF/datagen/configs/" 2>/dev/null | head -30

  echo
  echo "--- searching gin files for ceiling / height / dimension keywords:"
  find "$INF" -name "*.gin" -exec grep -l -E "ceiling|height|dimension|room_size" {} \; 2>/dev/null

  echo
  echo "--- sample ceiling references in any .gin:"
  find "$INF" -name "*.gin" -exec grep -Hn -E "ceiling|height" {} \; 2>/dev/null | head -20

  # ---------- Indoor entry point ----------
  echo
  echo "================================================================"
  echo "## Indoor scene entry points"
  echo "================================================================"
  echo
  echo "--- generate_indoors and similar:"
  find "$INF" -name "*indoor*" -o -name "*generate*" 2>/dev/null \
    | grep -v __pycache__ | head -20
  echo
  ls /home/poca/infinigen/infinigen_examples/ 2>/dev/null \
    || echo "(no infinigen_examples/ dir at clone root — checking parent)"
  echo
  ls /home/poca/infinigen/ 2>/dev/null | head -40

  # ---------- Room generator / room shell ----------
  echo
  echo "================================================================"
  echo "## Room generator / room shell"
  echo "================================================================"
  echo
  echo "--- contents of core/constraints/example_solver/room/:"
  ls -la "$INF/core/constraints/example_solver/room/" 2>/dev/null
  echo
  echo "--- decorate.py top 80 lines (we know floor_material_gens lives here):"
  head -80 "$INF/core/constraints/example_solver/room/decorate.py" 2>/dev/null

  # ---------- Lighting setup ----------
  echo
  echo "================================================================"
  echo "## Lighting setup files"
  echo "================================================================"
  ls -la "$INF/assets/lighting/" 2>/dev/null

  # ---------- Bonus: how is the kitchen room itself defined? ----------
  echo
  echo "================================================================"
  echo "## Kitchen-specific code"
  echo "================================================================"
  echo "--- files mentioning 'kitchen':"
  grep -rln -i "kitchen" "$INF" --include="*.py" 2>/dev/null \
    | grep -v __pycache__ \
    | head -20
  echo
  echo "--- files mentioning 'dining':"
  grep -rln -i "dining" "$INF" --include="*.py" 2>/dev/null \
    | grep -v __pycache__ \
    | head -20

  echo
  echo "================================================================"
  echo "## Done"
  echo "================================================================"
  echo "Output written to: $OUT"
} > "$OUT" 2>&1

echo "Probe v2 complete. Output at:"
echo "  WSL side:     $OUT"
echo "  Windows side: C:\\Users\\user\\Documents\\Claude\\Projects\\Cogs 160\\infinigen_probe_v2.out.txt"
