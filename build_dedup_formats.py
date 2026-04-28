"""Build dedup'd Quran-DB variants from canonical Quran.json.

Outputs into /tmp/quran_formats/ (so they don't bloat the package install
unless we adopt one as a runtime format):

  - dedup_naive.json        : ["unique_text", ...] + per-word index uint32 array
                              encoded as separate JSON arrays.
  - dedup_naive_blob.bin    : binary version of the above; uses uint16
                              indices since 20.7k fits.
  - dedup_smart.json        : (core_table, decoration_table, per_word
                              [core_idx, deco_idx] pairs).
  - dedup_smart_blob.bin    : packed-binary version of dedup_smart.

These let the loader allocate ~20k unique str objects instead of 77k.
"""
from __future__ import annotations

import array
import json
import struct
from collections import Counter
from pathlib import Path

import yaml


SOURCE = Path("quranic_phonemizer/resources/Quran.json")
SYMBOLS = Path("quranic_phonemizer/resources/base_phonemes.yaml")
OUT = Path("/tmp/quran_formats")
OUT.mkdir(parents=True, exist_ok=True)


def lt(k):
    s, a, w = k.split(":")
    return int(s), int(a), int(w)


def load_decoration_set():
    """Stop signs + non-essential 'other' symbols + the inter-letter space."""
    with SYMBOLS.open(encoding="utf-8") as f:
        sym = yaml.safe_load(f)
    keep_other = {"SHADDA", "PARTIAL_ALEF_MAKSURA", "TATWEEL"}
    decoration = set()
    for info in sym.get("stop_signs", {}).values():
        decoration.add(info["char"])
    for name, info in sym.get("other", {}).items():
        if name not in keep_other:
            decoration.add(info["char"])
    decoration.add(" ")
    return decoration


def main():
    with SOURCE.open(encoding="utf-8") as f:
        raw = json.load(f)
    keys = sorted(raw.keys(), key=lt)
    texts = [raw[k]["text"] for k in keys]
    n = len(texts)
    decoration = load_decoration_set()

    # === Naive dedup ===
    # Unique texts in canonical first-seen order.
    uniq = {}
    for t in texts:
        if t not in uniq:
            uniq[t] = len(uniq)
    unique_texts = list(uniq.keys())
    indices = [uniq[t] for t in texts]
    print(f"naive unique: {len(unique_texts):,} ({len(unique_texts)/n*100:.1f}%)")

    # JSON: [unique_texts, indices]  (compact, human-readable)
    p = OUT / "dedup_naive.json"
    with p.open("w", encoding="utf-8") as f:
        json.dump([unique_texts, indices], f, ensure_ascii=False, separators=(",", ":"))
    print(f"  {p.name}: {p.stat().st_size / 1024:.1f} KB")

    # Binary blob: header + offsets array + utf-8 unique-text blob + uint16 indices
    if len(unique_texts) > 65535:
        raise RuntimeError("naive unique count > uint16 limit; need wider index")
    text_bytes_list = [t.encode("utf-8") for t in unique_texts]
    text_blob = b"".join(text_bytes_list)
    text_offsets = array.array("I")
    off = 0
    for tb in text_bytes_list:
        text_offsets.append(off)
        off += len(tb)
    text_offsets.append(off)
    word_indices = array.array("H", indices)  # uint16
    p = OUT / "dedup_naive_blob.bin"
    with p.open("wb") as f:
        f.write(struct.pack("<II", n, len(unique_texts)))
        f.write(text_offsets.tobytes())
        f.write(struct.pack("<I", len(text_blob)))
        f.write(text_blob)
        f.write(word_indices.tobytes())
    print(f"  {p.name}: {p.stat().st_size / 1024:.1f} KB")

    # === Smart dedup ===
    def core_and_deco(t):
        core_chars = []
        deco_positions = []  # (offset_in_full_text, char)
        for i, c in enumerate(t):
            if c in decoration:
                deco_positions.append((i, c))
            else:
                core_chars.append(c)
        return "".join(core_chars), tuple(deco_positions)

    cores = []
    decos = []
    for t in texts:
        c, d = core_and_deco(t)
        cores.append(c)
        decos.append(d)

    core_uniq = {}
    for c in cores:
        if c not in core_uniq:
            core_uniq[c] = len(core_uniq)
    deco_uniq = {}
    for d in decos:
        if d not in deco_uniq:
            deco_uniq[d] = len(deco_uniq)
    print(f"smart unique cores: {len(core_uniq):,}, unique decoration sigs: {len(deco_uniq):,}")

    core_idxs = [core_uniq[c] for c in cores]
    deco_idxs = [deco_uniq[d] for d in decos]
    unique_cores_list = list(core_uniq.keys())
    # Decoration signatures encoded as compact strings: "pos1:char1;pos2:char2;..."
    # (positions are stable in the *full* text, which is what we'll reconstruct)
    deco_serialised = [
        ";".join(f"{i}:{c}" for i, c in d) if d else ""
        for d in deco_uniq.keys()
    ]

    p = OUT / "dedup_smart.json"
    with p.open("w", encoding="utf-8") as f:
        json.dump([unique_cores_list, deco_serialised, core_idxs, deco_idxs],
                  f, ensure_ascii=False, separators=(",", ":"))
    print(f"  {p.name}: {p.stat().st_size / 1024:.1f} KB")

    # Smart blob: cores blob + offsets + decoration table + per-word (core_idx, deco_idx)
    if len(unique_cores_list) > 65535 or len(deco_uniq) > 65535:
        raise RuntimeError("smart unique count > uint16 limit")
    core_bytes_list = [c.encode("utf-8") for c in unique_cores_list]
    core_blob = b"".join(core_bytes_list)
    core_offsets = array.array("I")
    off = 0
    for cb in core_bytes_list:
        core_offsets.append(off)
        off += len(cb)
    core_offsets.append(off)
    # Decoration table: count, then variable-length entries with offsets
    deco_bytes_list = [d.encode("utf-8") for d in deco_serialised]
    deco_blob = b"".join(deco_bytes_list)
    deco_offsets = array.array("I")
    off = 0
    for db in deco_bytes_list:
        deco_offsets.append(off)
        off += len(db)
    deco_offsets.append(off)

    word_core_idxs = array.array("H", core_idxs)
    word_deco_idxs = array.array("H", deco_idxs)

    p = OUT / "dedup_smart_blob.bin"
    with p.open("wb") as f:
        f.write(struct.pack("<III", n, len(unique_cores_list), len(deco_uniq)))
        f.write(core_offsets.tobytes())
        f.write(struct.pack("<I", len(core_blob)))
        f.write(core_blob)
        f.write(deco_offsets.tobytes())
        f.write(struct.pack("<I", len(deco_blob)))
        f.write(deco_blob)
        f.write(word_core_idxs.tobytes())
        f.write(word_deco_idxs.tobytes())
    print(f"  {p.name}: {p.stat().st_size / 1024:.1f} KB")

    # For comparison: existing slim formats
    print("\nExisting formats for reference:")
    for name in ("quran_db_texts.json", "quran_db_flat.json", "quran_db_blob.bin"):
        path = Path("quranic_phonemizer/resources") / name
        if path.exists():
            print(f"  {name}: {path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
