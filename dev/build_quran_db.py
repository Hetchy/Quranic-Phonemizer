"""Regenerates `quranic_phonemizer/resources/{hafs-warsh}/quran_db.bin` from `Quran_{warsh}.json`.

Reads the canonical, human-editable Quran source and emits the runtime
deduplicated binary blob the package ships. Word texts repeat heavily
(~73% of the 77,433 word slots are duplicates), so the binary stores
each unique text once and a ``uint16`` index per word slot. Keys are
not persisted — they are reconstructed at load time from
``surah_info.json``.

File layout (little-endian):
    <u32 n_words>                          number of word slots
    <u32 n_unique>                         number of unique texts
    <(n_unique + 1) * u32> text_offsets    cumulative byte offsets
    <u32 text_blob_len>                    length of the text blob
    <text_blob_len bytes> text_blob        UTF-8 concatenated unique texts
    <n_words * u16> word_indices           per-word slot -> unique-text index

Run after editing ``dev/Quran_warsh.json``:
    $ python dev/build_quran_db.py <quran_json> <output_bin> <surah_info_json>

"""

from __future__ import annotations

import argparse
import array
import json
import struct
from pathlib import Path


def _location_tuple(key: str):
    s, a, w = key.split(":")
    return int(s), int(a), int(w)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build quran_db.bin from a Quran.json source file."
    )
    parser.add_argument(
        "quran_json",
        type=Path,
        help="Path to the input Quran.json file (canonical, human-editable source)",
    )
    parser.add_argument(
        "output_bin",
        type=Path,
        help="Path to write the output quran_db.bin binary file",
    )
    parser.add_argument(
        "surah_info_json",
        type=Path,
        help="Path to surah_info.json, used to cross-check the total word count",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    src = args.quran_json
    dst = args.output_bin
    surah_info_path = args.surah_info_json

    if not src.is_file():
        raise SystemExit(f"Input file not found: {src}")
    if not surah_info_path.is_file():
        raise SystemExit(f"surah_info.json not found: {surah_info_path}")

    with src.open(encoding="utf-8") as fh:
        raw = json.load(fh)
    keys = sorted(raw.keys(), key=_location_tuple)
    texts = [raw[k]["text"] for k in keys]
    n = len(texts)

    # Cross-check against surah_info: the binary's word count must equal
    # the sum of num_words across all verses.
    with surah_info_path.open(encoding="utf-8") as fh:
        info = json.load(fh)
    expected = sum(w for s in info.values() for w in s)
    if expected != n:
        raise SystemExit(
            f"Mismatch: {src.name} has {n} words but {surah_info_path.name} implies "
            f"{expected}. Update surah_info.json or fix Quran.json."
        )

    # Deduplicate (preserve canonical first-seen order)
    uniq: dict[str, int] = {}
    word_idx: list[int] = []
    for t in texts:
        idx = uniq.get(t)
        if idx is None:
            idx = len(uniq)
            uniq[t] = idx
        word_idx.append(idx)
    if len(uniq) > 65535:
        raise SystemExit(
            f"Unique-text count {len(uniq)} exceeds uint16 range; widen "
            "the per-word index width in loader.py and here."
        )

    unique_texts = list(uniq.keys())
    encoded = [t.encode("utf-8") for t in unique_texts]
    text_blob = b"".join(encoded)

    offsets = array.array("I")
    cursor = 0
    for chunk in encoded:
        offsets.append(cursor)
        cursor += len(chunk)
    offsets.append(cursor)

    indices = array.array("H", word_idx)

    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("wb") as fh:
        fh.write(struct.pack("<II", n, len(unique_texts)))
        fh.write(offsets.tobytes())
        fh.write(struct.pack("<I", len(text_blob)))
        fh.write(text_blob)
        fh.write(indices.tobytes())

    print(f"wrote {dst}: {dst.stat().st_size / 1024:.1f} KB "
          f"({len(unique_texts):,} unique / {n:,} word slots)")


if __name__ == "__main__":
    main()