#!/usr/bin/env python3
"""
strip_flagged_chars.py

Removes characters from a JSON data file's field, using the list of
codepoints to remove from a FLAGGED report (the output of
generate_codepoint_inventory.py's flagged_output file).

This does not decide what's "flagged" itself -- it trusts whatever is
in the flagged file you give it. That means you can review/edit the
flagged file first (e.g. delete an entry from it if you decide that
character should actually be kept) before running this script.

Workflow:
    1. python3 generate_codepoint_inventory.py data.json aya_text_plain allowed.json flagged.json
    2. (optional) review/edit flagged.json -- remove any entries you want to KEEP
    3. python3 strip_flagged_chars.py data.json aya_text_plain flagged.json data.stripped.json

Usage:
    python strip_flagged_chars.py \
        warshData.json \
        aya_text \
        flagged.json \
        warshData.clean.json
"""

import json
import argparse


def load_flagged_codepoints(flagged_path):
    """Reads a flagged.json file (as produced by generate_codepoint_inventory.py)
    and returns the set of characters to remove."""
    with open(flagged_path, encoding="utf-8") as f:
        doc = json.load(f)
    chars_to_remove = set()
    for entry in doc["flagged_codepoints"]:
        # Prefer the literal char if present; fall back to decoding the codepoint string
        if "char" in entry:
            chars_to_remove.add(entry["char"])
        else:
            cp = int(entry["codepoint"].replace("U+", ""), 16)
            chars_to_remove.add(chr(cp))
    return chars_to_remove


def guess_record_label(record, index):
    if not isinstance(record, dict):
        return f"index {index}"
    if "surah" in record and "ayah" in record:
        return f"{record['surah']}:{record['ayah']}"
    if "sura_no" in record and "aya_no" in record:
        return f"{record['sura_no']}:{record['aya_no']}"
    if "id" in record:
        return f"id={record['id']}"
    return f"index {index}"


def _looks_like_record(d):
    id_like = {"surah", "ayah", "sura_no", "aya_no", "id"}
    return bool(id_like & set(d.keys()))


def strip_chars(text: str, chars_to_remove: set):
    removed_count = sum(1 for ch in text if ch in chars_to_remove)
    if removed_count == 0:
        return text, 0
    cleaned = "".join(ch for ch in text if ch not in chars_to_remove)
    return cleaned, removed_count


def process(obj, field_name, chars_to_remove, index_hint=0, current_label=None, affected=None):
    if isinstance(obj, dict):
        label = guess_record_label(obj, index_hint) if _looks_like_record(obj) else current_label
        for key, value in list(obj.items()):
            if key == field_name and isinstance(value, str):
                cleaned, removed_count = strip_chars(value, chars_to_remove)
                if removed_count:
                    obj[key] = cleaned
                    affected.append((label if label else f"index {index_hint}", removed_count))
            elif isinstance(value, (dict, list)):
                process(value, field_name, chars_to_remove, index_hint, label, affected)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            process(item, field_name, chars_to_remove, i, current_label, affected)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", help="Path to the source JSON data file")
    parser.add_argument("field", help="Field name to clean, e.g. aya_text_plain")
    parser.add_argument("flagged", help="Path to the flagged.json file listing which characters to remove")
    parser.add_argument("output", help="Path to write the cleaned JSON file")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    chars_to_remove = load_flagged_codepoints(args.flagged)

    affected = []
    process(data, args.field, chars_to_remove, affected=affected)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total_chars_removed = sum(c for _, c in affected)

    print(f"Field cleaned:              {args.field}")
    print(f"Characters targeted:        {sorted(f'U+{ord(c):04X}' for c in chars_to_remove)}")
    print(f"Records with removals:      {len(affected)}")
    print(f"Total characters removed:   {total_chars_removed}")
    print(f"Cleaned file written to:    {args.output}")


if __name__ == "__main__":
    main()
