"""Regenerate the slim runtime DB formats from the canonical Quran.json.

Outputs alongside Quran.json in quranic_phonemizer/resources/:
  - quran_db_dedup.bin  : deduplicated binary, 20.7k unique texts +
                           uint16 word indices  (default at runtime)
  - quran_db_texts.json : [text, ...] in canonical order
  - quran_db_flat.json  : [keys, texts] parallel arrays
  - quran_db_blob.bin   : packed binary, no dedup

Run after editing Quran.json.
"""
from __future__ import annotations

import array
import json
import struct
from pathlib import Path


def main() -> None:
    here = Path(__file__).resolve().parent
    src = here / "quranic_phonemizer" / "resources" / "Quran.json"
    dst = src.parent

    with src.open(encoding="utf-8") as f:
        raw = json.load(f)

    def lt(k: str):
        s, a, w = k.split(":")
        return int(s), int(a), int(w)

    keys = sorted(raw.keys(), key=lt)
    texts = [raw[k]["text"] for k in keys]

    # quran_db_texts.json: just texts in canonical order; keys reconstructed
    # at load time from surah_info.json.
    texts_path = dst / "quran_db_texts.json"
    with texts_path.open("w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {texts_path}: {texts_path.stat().st_size / 1024:.1f} KB")

    # quran_db_flat.json: parallel arrays
    flat_path = dst / "quran_db_flat.json"
    with flat_path.open("w", encoding="utf-8") as f:
        json.dump([keys, texts], f, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {flat_path}: {flat_path.stat().st_size / 1024:.1f} KB")

    # quran_db_blob.bin: packed binary
    blob_path = dst / "quran_db_blob.bin"
    n = len(keys)
    text_bytes_list = [t.encode("utf-8") for t in texts]
    text_blob = b"".join(text_bytes_list)
    text_offsets = array.array("I")
    off = 0
    for tb in text_bytes_list:
        text_offsets.append(off)
        off += len(tb)
    text_offsets.append(off)
    key_blob = ("\n".join(keys) + "\n").encode("ascii")
    with blob_path.open("wb") as f:
        f.write(struct.pack("<I", n))
        f.write(text_offsets.tobytes())
        f.write(struct.pack("<I", len(text_blob)))
        f.write(text_blob)
        f.write(struct.pack("<I", len(key_blob)))
        f.write(key_blob)
    print(f"wrote {blob_path}: {blob_path.stat().st_size / 1024:.1f} KB")

    # quran_db_dedup.bin: deduplicated binary. Only ~20.7k of the 77.4k
    # word strings are unique; we store one copy of each and a uint16
    # index per word slot. Layout matches loader._read_dedup_blob_header.
    dedup_path = dst / "quran_db_dedup.bin"
    uniq_index: dict[str, int] = {}
    word_indices: list[int] = []
    for t in texts:
        u = uniq_index.get(t)
        if u is None:
            u = len(uniq_index)
            uniq_index[t] = u
        word_indices.append(u)
    unique_texts = list(uniq_index.keys())
    if len(unique_texts) > 65535:
        raise RuntimeError(
            f"dedup unique count {len(unique_texts)} > uint16 limit; "
            "widen the per-word index width in loader and writer"
        )
    u_bytes_list = [t.encode("utf-8") for t in unique_texts]
    u_blob = b"".join(u_bytes_list)
    u_offsets = array.array("I")
    off = 0
    for ub in u_bytes_list:
        u_offsets.append(off)
        off += len(ub)
    u_offsets.append(off)
    word_idx_arr = array.array("H", word_indices)
    with dedup_path.open("wb") as f:
        f.write(struct.pack("<II", n, len(unique_texts)))
        f.write(u_offsets.tobytes())
        f.write(struct.pack("<I", len(u_blob)))
        f.write(u_blob)
        f.write(word_idx_arr.tobytes())
    print(f"wrote {dedup_path}: {dedup_path.stat().st_size / 1024:.1f} KB "
          f"({len(unique_texts):,} unique texts, {n:,} word slots)")


if __name__ == "__main__":
    main()
