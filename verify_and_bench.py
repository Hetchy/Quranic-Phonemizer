"""Verify byte-equality vs /tmp/baseline_main and bench phonemize("1-114").

Per round of optimization:
  - re-runs capture_phonemes.py to regenerate the 5 output artefacts
  - diffs each against /tmp/baseline_main
  - runs phonemize("1-114") 5 times (drop-prev + gc.collect) and reports timings
  - prints cProfile top 12 by tottime for the second call (avoiding cold start)

Exits non-zero if any artefact diffs from baseline.
"""
from __future__ import annotations

import cProfile
import filecmp
import gc
import os
import pstats
import subprocess
import sys
import time
from io import StringIO
from pathlib import Path


BASELINE = Path("/tmp/baseline_main")
OUT = Path("/tmp/check_now")
ARTEFACTS = [
    "quran_full.txt",
    "quran_full_all_stops.txt",
    "quran_full_refs_10k.txt",
    "quran_full_letter_phoneme_mappings.json",
    "quran_full_tajweed_mappings.json",
]


def run_capture() -> None:
    if OUT.exists():
        for p in OUT.iterdir():
            p.unlink()
    OUT.mkdir(parents=True, exist_ok=True)
    res = subprocess.run(
        [sys.executable, "capture_phonemes.py", str(OUT)],
        capture_output=True, text=True, check=False,
    )
    if res.returncode != 0:
        print("capture failed:", res.stderr)
        sys.exit(1)


def verify() -> None:
    bad = []
    for name in ARTEFACTS:
        a = BASELINE / name
        b = OUT / name
        if not b.exists():
            bad.append((name, "missing"))
            continue
        if not filecmp.cmp(a, b, shallow=False):
            bad.append((name, "diff"))
    if bad:
        print("VERIFY FAILED:")
        for name, why in bad:
            print(f"  {why}: {name}")
        sys.exit(1)
    print("VERIFY OK: all 5 artefacts byte-identical to baseline_main")


def bench() -> None:
    from quranic_phonemizer import Phonemizer
    t0 = time.perf_counter()
    p = Phonemizer()
    init_s = time.perf_counter() - t0
    print(f"init_s={init_s*1000:.1f}ms")

    timings = []
    new_r = None
    kept = []
    for i in range(1, 6):
        new_r = None
        kept.clear()
        gc.collect()
        t0 = time.perf_counter()
        new_r = p.phonemize("1-114")
        elapsed = time.perf_counter() - t0
        timings.append(elapsed)
        print(f"call {i}: {elapsed:.3f}s")
        kept.append(new_r)
    new_r = None
    kept.clear()
    print(f"min={min(timings):.3f}s mean={sum(timings)/len(timings):.3f}s max={max(timings):.3f}s")


def profile() -> None:
    from quranic_phonemizer import Phonemizer
    p = Phonemizer()
    p.phonemize("1-114")  # warmup
    gc.collect()

    pr = cProfile.Profile()
    pr.enable()
    p.phonemize("1-114")
    pr.disable()
    s = StringIO()
    pstats.Stats(pr, stream=s).sort_stats("tottime").print_stats(15)
    print(s.getvalue())


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("capture", "all"):
        run_capture()
    if cmd in ("verify", "all"):
        verify()
    if cmd in ("bench", "all"):
        bench()
    if cmd in ("profile", "all"):
        profile()


if __name__ == "__main__":
    main()
