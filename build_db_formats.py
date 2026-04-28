"""Build candidate Quran-DB formats from the canonical Quran.json.

For each format, writes a file under /tmp/quran_formats/. Some formats also
need a sidecar key-index file (so the loader can reconstruct sorted keys
without re-reading text payloads).

Run once before benchmarking.
"""
from __future__ import annotations

import array
import csv
import json
import marshal
import pickle
import sqlite3
import struct
from pathlib import Path

SOURCE = Path("/home/user/Quranic-Phonemizer/quranic_phonemizer/resources/Quran.json")
OUT = Path("/tmp/quran_formats")
OUT.mkdir(parents=True, exist_ok=True)


def loc_tuple(k: str):
    s, a, w = k.split(":")
    return int(s), int(a), int(w)


def load_canonical():
    with SOURCE.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    keys_sorted = sorted(raw.keys(), key=loc_tuple)
    texts = [raw[k]["text"] for k in keys_sorted]
    return keys_sorted, texts


def main() -> None:
    keys, texts = load_canonical()
    n = len(keys)
    print(f"loaded {n} entries from canonical JSON")

    # 1. json_full (current shape, slim source) — kept for reference
    p = OUT / "json_full.json"
    with p.open("w", encoding="utf-8") as f:
        json.dump({k: {"text": t} for k, t in zip(keys, texts)}, f, ensure_ascii=False)
    print(f"  json_full           : {p.stat().st_size / 1024:.1f} KB")

    # 2. json_slim: {key: text}
    p = OUT / "json_slim.json"
    with p.open("w", encoding="utf-8") as f:
        json.dump(dict(zip(keys, texts)), f, ensure_ascii=False)
    print(f"  json_slim           : {p.stat().st_size / 1024:.1f} KB")

    # 3. json_flat: [keys, texts] parallel arrays
    p = OUT / "json_flat.json"
    with p.open("w", encoding="utf-8") as f:
        json.dump([keys, texts], f, ensure_ascii=False)
    print(f"  json_flat           : {p.stat().st_size / 1024:.1f} KB")

    # 4. tsv
    p = OUT / "tsv.tsv"
    with p.open("w", encoding="utf-8") as f:
        for k, t in zip(keys, texts):
            f.write(f"{k}\t{t}\n")
    print(f"  tsv                 : {p.stat().st_size / 1024:.1f} KB")

    # 5. msgpack {key: text}
    import msgpack
    p = OUT / "msgpack_dict.mp"
    with p.open("wb") as f:
        f.write(msgpack.packb(dict(zip(keys, texts)), use_bin_type=True))
    print(f"  msgpack_dict        : {p.stat().st_size / 1024:.1f} KB")

    # 6. msgpack flat (keys, texts)
    p = OUT / "msgpack_flat.mp"
    with p.open("wb") as f:
        f.write(msgpack.packb([keys, texts], use_bin_type=True))
    print(f"  msgpack_flat        : {p.stat().st_size / 1024:.1f} KB")

    # 7. pickle dict
    p = OUT / "pickle_dict.pkl"
    with p.open("wb") as f:
        pickle.dump(dict(zip(keys, texts)), f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"  pickle_dict         : {p.stat().st_size / 1024:.1f} KB")

    # 8. pickle flat (keys list + texts list)
    p = OUT / "pickle_flat.pkl"
    with p.open("wb") as f:
        pickle.dump((keys, texts), f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"  pickle_flat         : {p.stat().st_size / 1024:.1f} KB")

    # 9. marshal flat
    p = OUT / "marshal_flat.bin"
    with p.open("wb") as f:
        marshal.dump((keys, texts), f)
    print(f"  marshal_flat        : {p.stat().st_size / 1024:.1f} KB")

    # 10. binary_blob: header + count + (offset_u32, len_u16) per entry + key blob + text blob
    #     keys are ASCII (location strings), texts are UTF-8 Arabic
    p = OUT / "binary_blob.bin"
    key_bytes = b"\n".join(k.encode("ascii") for k in keys) + b"\n"
    # text blob: concatenated UTF-8 with offset/length table
    text_bytes_list = [t.encode("utf-8") for t in texts]
    text_blob = b"".join(text_bytes_list)
    text_offsets = array.array("I")  # unsigned 4-byte
    off = 0
    for tb in text_bytes_list:
        text_offsets.append(off)
        off += len(tb)
    text_offsets.append(off)  # sentinel for last entry's length
    with p.open("wb") as f:
        f.write(struct.pack("<I", n))
        f.write(text_offsets.tobytes())
        f.write(struct.pack("<I", len(text_blob)))
        f.write(text_blob)
        f.write(struct.pack("<I", len(key_bytes)))
        f.write(key_bytes)
    print(f"  binary_blob         : {p.stat().st_size / 1024:.1f} KB")

    # 11. SQLite on-disk
    p = OUT / "quran.sqlite"
    if p.exists():
        p.unlink()
    conn = sqlite3.connect(p)
    cur = conn.cursor()
    cur.execute("CREATE TABLE quran (location TEXT PRIMARY KEY, text TEXT) WITHOUT ROWID")
    cur.executemany("INSERT INTO quran VALUES (?, ?)", zip(keys, texts))
    conn.commit()
    conn.execute("VACUUM")
    conn.close()
    print(f"  sqlite              : {p.stat().st_size / 1024:.1f} KB")

    print(f"\nfor reference, source Quran.json: {SOURCE.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
