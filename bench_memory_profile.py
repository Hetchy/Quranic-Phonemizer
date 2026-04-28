"""Measure RSS for realistic deployment scenarios.

1) Phonemizer alone (idle, no calls)
2) Verse-call workload: 100 verse-level phonemize calls, drop result + gc each
3) Surah-call workload: 10 surah calls
4) Full-Quran workload: 5 calls (worst case)

Reports steady-state RSS after each workload pattern.
"""
from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path


def rss_mb() -> float:
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024.0
    return -1.0


def main() -> None:
    print(f"baseline (just Python interpreter): {rss_mb():.1f} MB")

    # Stage 1: import + construct Phonemizer
    from quranic_phonemizer import Phonemizer
    print(f"after import quranic_phonemizer: {rss_mb():.1f} MB")

    p = Phonemizer()
    gc.collect()
    print(f"after Phonemizer() init (idle, no calls): {rss_mb():.1f} MB")

    # Stage 2: 100 verse-level calls (typical "few verses" web/mobile workload)
    new_r = None
    refs = ["1:1", "2:255", "112:1-112:4", "36:1-36:5", "55:13", "67:1-67:2",
            "1:1-1:7", "97:1-97:5", "113:1-113:5", "114:1-114:6"]
    rss_list = []
    t0 = time.perf_counter()
    for i in range(100):
        new_r = None
        gc.collect()
        new_r = p.phonemize(refs[i % len(refs)])
        if i in (0, 9, 49, 99):
            new_r = None
            gc.collect()
            rss_list.append((i + 1, rss_mb()))
    new_r = None
    gc.collect()
    dt = time.perf_counter() - t0
    print(f"\nverse-call workload (100 calls, varied verse refs):")
    for n, r in rss_list:
        print(f"  after call {n:3d}: {r:.1f} MB")
    print(f"  total wall time: {dt:.2f}s ({dt*10:.1f}ms per call avg)")
    print(f"  steady-state RSS: {rss_mb():.1f} MB")

    # Stage 3: 10 surah-level calls
    print(f"\nsurah-call workload (10 mid-size surahs):")
    surah_refs = ["1", "97", "112", "113", "114", "55", "36", "67", "78", "85"]
    t0 = time.perf_counter()
    for i, ref in enumerate(surah_refs):
        new_r = None
        gc.collect()
        new_r = p.phonemize(ref)
    new_r = None
    gc.collect()
    dt = time.perf_counter() - t0
    print(f"  total wall time: {dt:.2f}s")
    print(f"  steady-state RSS: {rss_mb():.1f} MB")

    # Stage 4: 5 full-Quran calls
    print(f"\nfull-Quran workload (5 calls):")
    t0 = time.perf_counter()
    for i in range(5):
        new_r = None
        gc.collect()
        new_r = p.phonemize("1-114")
    new_r = None
    gc.collect()
    dt = time.perf_counter() - t0
    print(f"  total wall time: {dt:.2f}s")
    print(f"  steady-state RSS: {rss_mb():.1f} MB")


if __name__ == "__main__":
    main()
