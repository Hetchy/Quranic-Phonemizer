import json
import re
import sys

if len(sys.argv) < 2:
    print("Usage: python compare_coverage.py <cmap_dump.ttx> [unicode_inventory.json]")
    sys.exit(1)

ttx_path = sys.argv[1]
inventory_path = sys.argv[2] if len(sys.argv) > 2 else "unicode_inventory.json"

# Load the required codepoints from your inventory
with open(inventory_path, encoding="utf-8") as f:
    inventory = json.load(f)

required_codepoints = []
for entry in inventory["allowed_codepoints"]:
    cp_str = entry["codepoint"].replace("U+", "")
    cp_int = int(cp_str, 16)
    required_codepoints.append((cp_int, entry["codepoint"], entry["unicode_name"]))

# Parse the cmap ttx file to get codepoints the font actually supports
with open(ttx_path, encoding="utf-8") as f:
    ttx_content = f.read()

# Extract all code="0x...." entries from the ttx XML
font_codepoints = set(int(m, 16) for m in re.findall(r'code="0x([0-9A-Fa-f]+)"', ttx_content))

# Compare
missing = []
present = []

for cp_int, cp_str, name in required_codepoints:
    if cp_int in font_codepoints:
        present.append((cp_str, name))
    else:
        missing.append((cp_str, name))

print(f"Total required: {len(required_codepoints)}")
print(f"Present in font: {len(present)}")
print(f"MISSING from font: {len(missing)}\n")

if missing:
    print("--- Missing codepoints ---")
    for cp_str, name in missing:
        print(f"{cp_str}  {name}")