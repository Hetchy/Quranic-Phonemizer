"""End-to-end benchmark covering: cold start, per-test timings, cached/repeated
calls with memory and gc tracking.

Each invocation runs in its own Python process for isolation and consistent
cold-start measurement.

Usage:
    python bench_full.py <test_name>

Test names:
    cold_start            -- time to import + construct Phonemizer (3 runs)
    verse_2_255           -- phonemize("2:255") x 3
    surah_2               -- phonemize("2") x 3
    surah_2_verse_stops   -- phonemize("2", stop_signs=["verse"]) x 3
    quran_full            -- phonemize("1-114") x 3
    quran_full_all_stops  -- phonemize("1-114", stop_signs=<all>) x 3
    cached_repeated       -- phonemize("1-114") x 5 dropping prev result + gc.collect
"""
from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path


ALL_STOPS = [
    "verse", "preferred_continue", "preferred_stop",
    "optional_stop", "compulsory_stop", "prohibited_stop",
]


def rss_mb() -> float:
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024.0
    return -1.0


SIMPLE = {
    "verse_2_255": {"ref": "2:255"},
    "surah_2": {"ref": "2"},
    "surah_2_verse_stops": {"ref": "2", "stop_signs": ["verse"]},
    "quran_full": {"ref": "1-114"},
    "quran_full_all_stops": {"ref": "1-114", "stop_signs": ALL_STOPS},
}


def run_simple(name: str) -> None:
    spec = SIMPLE[name]
    ref = spec["ref"]
    kwargs = {k: v for k, v in spec.items() if k != "ref"}

    t0 = time.perf_counter()
    from quranic_phonemizer import Phonemizer
    phonemizer = Phonemizer()
    init_s = time.perf_counter() - t0

    timings = []
    for i in range(1, 4):
        t0 = time.perf_counter()
        result = phonemizer.phonemize(ref, **kwargs)
        elapsed = time.perf_counter() - t0
        timings.append(elapsed)
        n_words = len(result._nested)
        print(json.dumps({
            "test": name, "run": i,
            "elapsed_s": elapsed,
            "init_s": init_s if i == 1 else None,
            "n_words": n_words,
            "rss_mb": rss_mb(),
        }), flush=True)
    print(json.dumps({
        "test": name, "summary": True,
        "init_s": init_s,
        "min_s": min(timings), "mean_s": sum(timings) / len(timings), "max_s": max(timings),
        "runs_s": timings,
    }), flush=True)


def run_cold_start() -> None:
    """Measure import + construct in 3 separate freshly-spawned subprocesses."""
    import subprocess
    timings = []
    rss = []
    snippet = (
        "import time, sys; t0=time.perf_counter();"
        "from quranic_phonemizer import Phonemizer;"
        "p = Phonemizer();"
        "dt = time.perf_counter() - t0;"
        "import json;"
        "rss_kb = 0\n"
        "with open('/proc/self/status') as f:\n"
        " for line in f:\n"
        "  if line.startswith('VmRSS:'): rss_kb = int(line.split()[1])\n"
        "print(json.dumps({'cold_start_s': dt, 'rss_mb': rss_kb/1024.0}))"
    )
    for i in range(1, 4):
        out = subprocess.check_output([sys.executable, "-c", snippet], text=True)
        rec = json.loads(out.strip())
        timings.append(rec["cold_start_s"])
        rss.append(rec["rss_mb"])
        print(json.dumps({"test": "cold_start", "run": i, **rec}), flush=True)
    print(json.dumps({
        "test": "cold_start", "summary": True,
        "min_s": min(timings), "mean_s": sum(timings) / len(timings), "max_s": max(timings),
        "runs_s": timings, "rss_mb": rss,
    }), flush=True)


def run_cached_repeated() -> None:
    """5 phonemize("1-114") calls, dropping prev result + gc.collect between."""
    t0 = time.perf_counter()
    from quranic_phonemizer import Phonemizer
    phonemizer = Phonemizer()
    init_s = time.perf_counter() - t0

    timings = []
    for i in range(1, 6):
        gc.collect()
        rss_before = rss_mb()
        t0 = time.perf_counter()
        result = phonemizer.phonemize("1-114")
        elapsed = time.perf_counter() - t0
        rss_after = rss_mb()
        timings.append(elapsed)
        print(json.dumps({
            "test": "cached_repeated", "run": i,
            "elapsed_s": elapsed,
            "rss_before_mb": rss_before,
            "rss_after_mb": rss_after,
            "n_words": len(result._nested),
        }), flush=True)
        result = None
        gc.collect()

    print(json.dumps({
        "test": "cached_repeated", "summary": True,
        "init_s": init_s,
        "min_s": min(timings), "mean_s": sum(timings) / len(timings), "max_s": max(timings),
        "runs_s": timings,
    }), flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("test")
    args = p.parse_args()
    if args.test == "cold_start":
        run_cold_start()
    elif args.test == "cached_repeated":
        run_cached_repeated()
    elif args.test in SIMPLE:
        run_simple(args.test)
    else:
        print(f"unknown test {args.test}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
