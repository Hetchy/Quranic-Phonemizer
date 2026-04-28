"""Capture phoneme output for correctness regression testing.

Writes a deterministic newline-delimited string of phonemes for the 3 reference
cases. Files are diffed before/after optimization to ensure phonemes are
preserved exactly.

Cases:
  - quran_full           : phonemize("1-114")
  - quran_full_all_stops : phonemize("1-114", stop_signs=<all 6>)
  - quran_full_refs_10k  : phonemize("1-114", stop_refs=<10000 random valid keys>)

Usage: python capture_phonemes.py <output_dir>
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path


SURAH_INFO_PATH = Path(__file__).parent / "quranic_phonemizer" / "resources" / "surah_info.json"

ALL_STOPS = [
    "verse", "preferred_continue", "preferred_stop",
    "optional_stop", "compulsory_stop", "prohibited_stop",
]


def all_word_keys() -> list[str]:
    info = json.loads(SURAH_INFO_PATH.read_text(encoding="utf-8"))
    keys: list[str] = []
    for s_key in sorted(info.keys(), key=int):
        s = info[s_key]
        for v in s["verses"]:
            verse_num = int(v["verse"])
            nw = int(v["num_words"])
            for w in range(1, nw + 1):
                keys.append(f"{s_key}:{verse_num}:{w}")
    return keys


def serialize(result) -> str:
    """Word-by-word phonemes, one word per line, separated by '|'."""
    lines = []
    for w_phonemes in result._nested:
        lines.append("|".join(w_phonemes))
    return "\n".join(lines) + "\n"


def main() -> None:
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)

    from quranic_phonemizer import Phonemizer
    p = Phonemizer()

    cases = {
        "quran_full": {"ref": "1-114"},
        "quran_full_all_stops": {"ref": "1-114", "stop_signs": ALL_STOPS},
        "quran_full_refs_10k": {
            "ref": "1-114",
            "stop_refs": random.Random(0xC0FFEE).sample(all_word_keys(), k=10000),
        },
    }

    for name, kwargs in cases.items():
        ref = kwargs.pop("ref")
        result = p.phonemize(ref, **kwargs)
        out_path = out_dir / f"{name}.txt"
        out_path.write_text(serialize(result), encoding="utf-8")
        print(f"wrote {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
