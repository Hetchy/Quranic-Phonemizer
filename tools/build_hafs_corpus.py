"""Regenerate the packaged Hafs corpus from its editable JSON source.

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

The packaged runtime corpus is always built from the Uthmani script. Other
scripts under ``corpus_sources/riwayat/hafs/scripts/`` are alignment fixtures,
not shipped data, so building one requires an explicit ``--output-dir``.

Run after editing ``corpus_sources/riwayat/hafs/scripts/uthmani/quran.json``:
    $ python tools/build_hafs_corpus.py
"""

from __future__ import annotations

import argparse
import array
import json
import struct
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "corpus_sources" / "riwayat" / "hafs" / "scripts"
CORPUS_DIR = REPO_ROOT / "quranic_phonemizer" / "data" / "riwayat" / "hafs" / "corpus"
SHIPPED_SCRIPT = "uthmani"
SURAH_INFO = CORPUS_DIR / "surah_info.json"


def _location_tuple(key: str):
    s, a, w = key.split(":")
    return int(s), int(a), int(w)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", default=SHIPPED_SCRIPT)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    if args.script != SHIPPED_SCRIPT and args.output_dir is None:
        raise SystemExit(
            f"Only the {SHIPPED_SCRIPT!r} script may overwrite the packaged "
            f"corpus. Pass --output-dir to build {args.script!r} elsewhere."
        )
    src = SCRIPTS_DIR / args.script / "quran.json"
    if not src.exists():
        raise SystemExit(f"No such script source: {src}")
    output_dir = (args.output_dir or CORPUS_DIR).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    dst = output_dir / "quran_db.bin"

    with src.open(encoding="utf-8") as fh:
        raw = json.load(fh)
    keys = sorted(raw.keys(), key=_location_tuple)
    texts = [raw[k]["text"] for k in keys]
    n = len(texts)

    # Cross-check against surah_info: the binary's word count must equal
    # the sum of num_words across all verses.
    with SURAH_INFO.open(encoding="utf-8") as fh:
        info = json.load(fh)
    expected = sum(w for s in info.values() for w in s)
    if expected != n:
        raise SystemExit(
            f"Mismatch: {src.name} has {n} words but surah_info.json implies "
            f"{expected}. Update surah_info.json or fix the source."
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
            "the per-word index width in corpus.py and here."
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

    with dst.open("wb") as fh:
        fh.write(struct.pack("<II", n, len(unique_texts)))
        fh.write(offsets.tobytes())
        fh.write(struct.pack("<I", len(text_blob)))
        fh.write(text_blob)
        fh.write(indices.tobytes())

    print(
        f"wrote {dst}: {dst.stat().st_size / 1024:.1f} KB "
        f"({len(unique_texts):,} unique / {n:,} word slots)"
    )


if __name__ == "__main__":
    main()
