#!/usr/bin/env python3
r"""
unicode_validator.py

Scans a single field of a JSON data file and sorts every distinct
codepoint found into one of two separate output files:

  - unicode_inventory file  -- codepoints inside the Arabic block (U+0600-06FF),
                      EXCLUDING the Arabic-Indic digit sub-range (U+0660-0669),
                      or the explicitly allowed space/NBSP characters
  - flagged file    -- everything else, with the exact location
                      (record, character index, context) of every
                      occurrence, so each one can be found and fixed

Usage:
    python .\Scripts\unicode_validator.py \
      '.\Raw Data\warshData.json' \
      aya_text  \
      unicode_inventory.json \
      flagged.json

Optional:
    --max-locations N       Max locations recorded per flagged codepoint (default 10)
"""

import json
import argparse
import unicodedata
from collections import defaultdict

ALLOWED_BLOCKS = [
    (0x0600, 0x06FF, "Arabic"),
]

# Sub-ranges that fall INSIDE an allowed block above, but should still
# be treated as not allowed. Arabic-Indic digits (U+0660-0669) sit
# inside the Arabic block by Unicode's own block definition, but a
# digit appearing in Quranic recitation text is a data bug (e.g. a
# leaked verse-number marker), not valid script content -- so they're
# carved back OUT here even though the block check alone would let
# them through.
EXCLUDED_SUBRANGES = [
    (0x0660, 0x0669, "Arabic-Indic digits"),
]

# The only characters allowed outside the Arabic block. Not a "block"
# exception -- explicit single-codepoint carve-outs, since they're
# needed structurally (word separator / typographic glue). Nothing
# else is exempted this way; add to this set only if you mean to allow
# one more specific character everywhere, not a whole block.
ALLOWED_CHARS = {0x0020, 0x00A0}


def is_excluded(codepoint: int) -> bool:
    return any(start <= codepoint <= end for start, end, _ in EXCLUDED_SUBRANGES)


def excluded_subrange_name(codepoint: int):
    for start, end, name in EXCLUDED_SUBRANGES:
        if start <= codepoint <= end:
            return name
    return None


def block_name(codepoint: int) -> str:
    """Returns the block name ONLY if it's allowed. Anything excluded
    (even if technically inside an allowed block) or otherwise not
    allowed is labeled 'Other', with the exclusion reason noted
    separately where relevant."""
    if codepoint in ALLOWED_CHARS:
        return "Basic Latin (explicitly allowed: space/NBSP)"
    if is_excluded(codepoint):
        return f"Other (excluded from Arabic block: {excluded_subrange_name(codepoint)})"
    for start, end, name in ALLOWED_BLOCKS:
        if start <= codepoint <= end:
            return name
    return "Other"


def is_allowed(codepoint: int) -> bool:
    if codepoint in ALLOWED_CHARS:
        return True
    if is_excluded(codepoint):
        return False
    return any(start <= codepoint <= end for start, end, _ in ALLOWED_BLOCKS)


def guess_record_label(record, index):
    """Best-effort human-readable identifier for a record."""
    if not isinstance(record, dict):
        return f"index {index}"
    if "surah" in record and "ayah" in record:
        return f"{record['surah']}:{record['ayah']}"
    if "sura_no" in record and "aya_no" in record:
        return f"{record['sura_no']}:{record['aya_no']}"
    if "id" in record:
        return f"id={record['id']}"
    return f"index {index}"


def walk_field(obj, field_name, index_hint=0, current_label=None):
    """Recursively yield (record_label, text) for every string found
    under field_name, anywhere in the JSON structure."""
    if isinstance(obj, dict):
        label = guess_record_label(obj, index_hint) if _looks_like_record(obj) else current_label
        for key, value in obj.items():
            if key == field_name and isinstance(value, str):
                yield (label if label else f"index {index_hint}", value)
            elif isinstance(value, (dict, list)):
                yield from walk_field(value, field_name, index_hint, label)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            yield from walk_field(item, field_name, i, current_label)


def _looks_like_record(d):
    id_like = {"surah", "ayah", "sura_no", "aya_no", "id"}
    return bool(id_like & set(d.keys()))


def scan(data, field_name, max_locations=10):
    """Returns (allowed_codepoints, flagged_codepoints) where:
      - allowed_codepoints: set of distinct chars found that are allowed
      - flagged_codepoints: dict of char -> list of location dicts
        (capped at max_locations; a codepoint can still have more
        occurrences than are listed, that's just not counted or noted)
    """
    allowed_chars_found = set()
    flagged_locations = defaultdict(list)

    for label, text in walk_field(data, field_name):
        for pos, ch in enumerate(text):
            if is_allowed(ord(ch)):
                allowed_chars_found.add(ch)
            else:
                if len(flagged_locations[ch]) < max_locations:
                    start = max(0, pos - 8)
                    end = min(len(text), pos + 9)
                    context = text[start:pos] + "⟦" + ch + "⟧" + text[pos + 1:end]
                    flagged_locations[ch].append({
                        "record": label,
                        "char_index": pos,
                        "context": context,
                    })

    return allowed_chars_found, flagged_locations


def build_allowed_report(allowed_chars_found):
    entries = []
    for ch in sorted(allowed_chars_found, key=ord):
        cp_int = ord(ch)
        try:
            name = unicodedata.name(ch)
        except ValueError:
            name = "UNNAMED / CONTROL CHARACTER"
        entries.append({
            "char": ch,
            "codepoint": f"U+{cp_int:04X}",
            "unicode_name": name,
            "unicode_block": block_name(cp_int),
        })
    return entries


def build_flagged_report(flagged_locations):
    entries = []
    for ch, locations in sorted(flagged_locations.items(), key=lambda x: ord(x[0])):
        cp_int = ord(ch)
        try:
            name = unicodedata.name(ch)
        except ValueError:
            name = "UNNAMED / CONTROL CHARACTER"
        entries.append({
            "char": ch,
            "codepoint": f"U+{cp_int:04X}",
            "unicode_name": name,
            "unicode_block": block_name(cp_int),
            "locations": locations,
        })
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", help="Path to the source JSON data file")
    parser.add_argument("field", help="Field name to scan, e.g. aya_text_plain")
    parser.add_argument("allowed_output", help="Path to write the ALLOWED codepoints report")
    parser.add_argument("flagged_output", help="Path to write the FLAGGED codepoints report")
    parser.add_argument(
        "--max-locations", type=int, default=10,
        help="Max locations to record per flagged codepoint (default 10)"
    )
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    allowed_chars_found, flagged_locations = scan(data, args.field, args.max_locations)

    allowed_entries = build_allowed_report(allowed_chars_found)
    flagged_entries = build_flagged_report(flagged_locations)

    with open(args.allowed_output, "w", encoding="utf-8") as f:
        json.dump({"allowed_codepoints": allowed_entries}, f, ensure_ascii=False, indent=2)

    with open(args.flagged_output, "w", encoding="utf-8") as f:
        json.dump({"flagged_codepoints": flagged_entries}, f, ensure_ascii=False, indent=2)

    print(f"Field scanned:            {args.field}")
    print(f"Allowed:                  {[name for _, _, name in ALLOWED_BLOCKS]} "
          f"(excluding {[name for _, _, name in EXCLUDED_SUBRANGES]}) + U+0020 SPACE + U+00A0 NBSP")
    print(f"Allowed codepoints found: {len(allowed_entries)}  -> {args.allowed_output}")
    print(f"Flagged codepoints found: {len(flagged_entries)}  -> {args.flagged_output}")
    print()
    if not flagged_entries:
        print("Verdict: PASS -- every codepoint is Arabic (excluding digits) or the allowed space/NBSP")
    else:
        print(f"Verdict: FAIL -- {len(flagged_entries)} flagged codepoint(s)\n")
        for entry in flagged_entries:
            print(f"  {entry['codepoint']}  {entry['unicode_name']}  ({entry['unicode_block']})")
            for loc in entry["locations"]:
                print(f"      at {loc['record']} / char {loc['char_index']}: ...{loc['context']}...")
            print()


if __name__ == "__main__":
    main()