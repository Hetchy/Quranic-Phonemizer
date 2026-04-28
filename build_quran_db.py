"""Regenerate the slim runtime DB formats from the canonical Quran.json.

Outputs alongside Quran.json in quranic_phonemizer/resources/:
  - quran_db_texts.json : [text, ...] in canonical order (smallest, default)
  - quran_db_flat.json  : [keys, texts] parallel arrays
  - quran_db_blob.bin   : packed binary  (opt-in via QURAN_DB_FORMAT=blob)

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


if __name__ == "__main__":
    main()
