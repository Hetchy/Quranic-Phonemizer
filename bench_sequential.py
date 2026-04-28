"""Bench sequential phonemize calls in a single process (cached Phonemizer
instance). Measures whether successive calls slow down across patterns.

Patterns:
  - naive       : every prior result kept alive in a list (worst case)
  - drop_prev   : drop all prior results before each call (no gc.collect)
  - drop_and_gc : drop prior results + explicit gc.collect (best practice)

Each pattern runs phonemize("1-114") n times.
"""
from __future__ import annotations

import argparse
import gc
import json
import time


def rss_mb() -> float:
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024.0
    return -1.0


def run(pattern: str, n: int = 7) -> None:
    from quranic_phonemizer import Phonemizer
    p = Phonemizer()

    timings = []
    kept = []  # lives across iterations
    new_r = None  # local binding cleared between iterations

    for i in range(1, n + 1):
        # Pre-call cleanup. Order matters: clear local + kept refs so the
        # interpreter's `new_r` slot is None when the call begins.
        new_r = None
        if pattern == "drop_prev":
            kept.clear()
        elif pattern == "drop_and_gc":
            kept.clear()
            gc.collect()
        # naive: keep everything alive

        t0 = time.perf_counter()
        new_r = p.phonemize("1-114")
        elapsed = time.perf_counter() - t0

        timings.append(elapsed)
        print(json.dumps({
            "pattern": pattern, "run": i,
            "elapsed_s": round(elapsed, 4),
            "rss_mb": round(rss_mb(), 1),
            "objects": len(gc.get_objects()),
        }), flush=True)

        kept.append(new_r)

    # Don't reference `new_r`/`kept` after — they may pin a lot of memory
    print(json.dumps({
        "pattern": pattern, "summary": True,
        "runs_s": [round(t, 4) for t in timings],
        "min_s": round(min(timings), 4),
        "max_s": round(max(timings), 4),
        "mean_s": round(sum(timings) / len(timings), 4),
        "growth_pct_first_to_last": round((timings[-1] - timings[0]) / timings[0] * 100, 1),
    }), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pattern", choices=["naive", "drop_prev", "drop_and_gc"])
    ap.add_argument("--n", type=int, default=7)
    args = ap.parse_args()
    run(args.pattern, args.n)
