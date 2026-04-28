"""Benchmark harness for the Phonemizer.

Usage:
    python bench_phonemizer.py <test_name> [--repeat N]

Test names:
    verse_2_255         phonemize("2:255")
    surah_2             phonemize("2")
    surah_2_verse_stops phonemize("2", stop_signs=["verse"])
    surah_2_refs_100    phonemize("2", stop_refs=<100 random valid keys>)
    surah_2_refs_500    phonemize("2", stop_refs=<500 random valid keys>)
    surah_2_refs_1000   phonemize("2", stop_refs=<1000 random valid keys>)
    quran_full          phonemize("1-114")
    quran_full_all_stops phonemize("1-114", stop_signs=<all valid stop signs>)

Each run prints a JSON line with name, run index, init_seconds, elapsed_seconds.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path


SURAH_INFO_PATH = Path(__file__).parent / "quranic_phonemizer" / "resources" / "surah_info.json"


def all_word_keys_for_surah(surah_num: int) -> list[str]:
    info = json.loads(SURAH_INFO_PATH.read_text(encoding="utf-8"))
    s = info[str(surah_num)]
    keys: list[str] = []
    for v in s["verses"]:
        verse_num = int(v["verse"])
        nw = int(v["num_words"])
        for w in range(1, nw + 1):
            keys.append(f"{surah_num}:{verse_num}:{w}")
    return keys


def build_random_stop_refs(surah_num: int, n: int, seed: int) -> list[str]:
    rng = random.Random(seed)
    pool = all_word_keys_for_surah(surah_num)
    return rng.sample(pool, k=n)


TESTS = {
    "verse_2_255": {"ref": "2:255"},
    "surah_2": {"ref": "2"},
    "surah_2_verse_stops": {"ref": "2", "stop_signs": ["verse"]},
    "surah_2_refs_100": {"ref": "2", "stop_refs_random": (2, 100, 0xC0FFEE)},
    "surah_2_refs_500": {"ref": "2", "stop_refs_random": (2, 500, 0xC0FFEE)},
    "surah_2_refs_1000": {"ref": "2", "stop_refs_random": (2, 1000, 0xC0FFEE)},
    "quran_full": {"ref": "1-114"},
    "quran_full_all_stops": {
        "ref": "1-114",
        "stop_signs": [
            "verse", "preferred_continue", "preferred_stop",
            "optional_stop", "compulsory_stop", "prohibited_stop",
        ],
    },
}


def run_test(name: str, repeat: int) -> None:
    if name not in TESTS:
        print(f"Unknown test: {name}", file=sys.stderr)
        sys.exit(2)

    spec = TESTS[name]
    kwargs: dict = {}
    if "stop_signs" in spec:
        kwargs["stop_signs"] = list(spec["stop_signs"])
    if "stop_refs_random" in spec:
        surah_num, n, seed = spec["stop_refs_random"]
        kwargs["stop_refs"] = build_random_stop_refs(surah_num, n, seed)
    elif "stop_refs" in spec:
        kwargs["stop_refs"] = list(spec["stop_refs"])

    t0 = time.perf_counter()
    from quranic_phonemizer import Phonemizer
    phonemizer = Phonemizer()
    init_elapsed = time.perf_counter() - t0

    timings: list[float] = []
    for i in range(1, repeat + 1):
        t0 = time.perf_counter()
        result = phonemizer.phonemize(spec["ref"], **kwargs)
        elapsed = time.perf_counter() - t0
        timings.append(elapsed)
        # touch result lightly to ensure no laziness skews timing
        n_words = len(result._nested)
        out = {
            "test": name,
            "run": i,
            "elapsed_s": elapsed,
            "init_s": init_elapsed if i == 1 else None,
            "n_words": n_words,
        }
        print(json.dumps(out), flush=True)

    summary = {
        "test": name,
        "summary": True,
        "init_s": init_elapsed,
        "runs_s": timings,
        "min_s": min(timings),
        "max_s": max(timings),
        "mean_s": sum(timings) / len(timings),
    }
    print(json.dumps(summary), flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("test", help="Test name; one of: " + ", ".join(TESTS))
    p.add_argument("--repeat", type=int, default=3)
    args = p.parse_args()
    run_test(args.test, args.repeat)


if __name__ == "__main__":
    main()
