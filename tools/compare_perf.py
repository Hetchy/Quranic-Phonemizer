"""Time two revisions against each other.

    $ python tools/compare_perf.py <base> [<candidate>]

Both sides answer in turn inside one run, so the ratio survives host load.
"""
from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: One request per scale. Surah 2 is here because a cost that grows with the
#: square of the passage is invisible at an ayah and plain at six thousand
#: words. A single word is not here: at half a millisecond it reads as noise.
REFS = ("2:255", "55", "2")

#: How much slower a side may be before it is a regression rather than noise.
TOLERANCE = 0.10

PROBE = """
import gc, json, sys, time
from quranic_phonemizer import Phonemizer

pm = Phonemizer()
out = {}
for ref in sys.argv[1:]:
    warm = pm.analyse(ref)
    out.setdefault("counts", {})[ref] = [len(warm.words), len(warm.sounds)]
    out.setdefault("digests", {})[ref] = warm.analysis.canon_digest
    del warm
    best = None
    for _ in range(3):
        gc.collect()
        started = time.perf_counter()
        pm.analyse(ref)
        spent = (time.perf_counter() - started) * 1000
        best = spent if best is None else min(best, spent)
    out.setdefault("ms", {})[ref] = best
print(json.dumps(out))
"""


def export(revision: str, into: Path) -> Path:
    """A worktree of its own, so neither side can import the other."""
    into.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(
        ["git", "archive", revision], cwd=ROOT, capture_output=True, check=True
    )
    subprocess.run(["tar", "-x", "-C", str(into)], input=archive.stdout, check=True)
    return into


def ask(tree: Path) -> dict:
    done = subprocess.run(
        [sys.executable, "-c", PROBE, *REFS],
        cwd=tree, capture_output=True, text=True, check=True,
    )
    return json.loads(done.stdout)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("base")
    parser.add_argument("candidate", nargs="?", default="HEAD")
    parser.add_argument("--rounds", type=int, default=3)
    args = parser.parse_args(argv)

    work = Path(tempfile.mkdtemp(prefix="compare-perf-"))
    try:
        trees = {
            side: export(rev, work / side)
            for side, rev in (("base", args.base), ("candidate", args.candidate))
        }
        ratios: dict[str, list[float]] = {ref: [] for ref in REFS}
        answers: dict[str, dict] = {}
        for round_number in range(args.rounds):
            # Alternate which side goes first, so a drifting host cannot
            # favour whichever one is always warm.
            order = ("base", "candidate")
            if round_number % 2:
                order = tuple(reversed(order))
            said = {side: ask(trees[side]) for side in order}
            answers = said
            for ref in REFS:
                ratios[ref].append(said["candidate"]["ms"][ref]
                                   / said["base"]["ms"][ref])

        failed = []
        print(f"{'ref':<8} {'ratio':>7}  verdict")
        for ref in REFS:
            ratio = statistics.median(ratios[ref])
            same = (answers["base"]["digests"][ref]
                    == answers["candidate"]["digests"][ref])
            if not same:
                verdict = "DIFFERENT OUTPUT -- not comparable"
                failed.append(ref)
            elif ratio > 1 + TOLERANCE:
                verdict = "slower"
                failed.append(ref)
            elif ratio < 1 - TOLERANCE:
                verdict = "faster"
            else:
                verdict = "same"
            print(f"{ref:<8} {ratio:>6.3f}x  {verdict}")

        return 1 if failed else 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
