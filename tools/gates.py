"""Every gate, and the one place the ratchet numbers live.

Run: python tools/gates.py [--fast] [--serial] [-jN] [gate ...]
"""
from __future__ import annotations

import argparse
import concurrent.futures
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

#: A floor may only rise, a ceiling may only fall. Moving one is a claim about
#: which refs changed, so the commit that moves it says which and why.
FLOORS = {
    ("cross", "word"): "99.997",
    ("cross", "verse"): "100.0",
    ("regression", "word"): "99.921",
    ("regression", "verse"): "97.852",
    ("roundtrip", "uthmani"): "100.0",
    ("attest", "uthmani"): "176",
    ("attest", "indopak"): "237",
    ("l1", "-"): "18",
}

GATES: dict[str, tuple[tuple[str, ...], ...]] = {
    "suite": ((sys.executable, "-m", "pytest", "tests/", "-q"),),
    "comments": ((sys.executable, "tools/comment_lint.py"),),
    "structure": ((sys.executable, "tools/structure_lint.py"),),
    "cross-script": (("cross", "word"), ("cross", "verse")),
    "regression": (("regression", "word"), ("regression", "verse")),
    "roundtrip": (("roundtrip", "uthmani"),),
    "attestation": (("attest", "uthmani"), ("attest", "indopak")),
    "l1": (("l1", "-"),),
}

#: The three that read no corpus. Seconds rather than minutes, so these are the
#: ones worth running after every change.
FAST = ("suite", "comments", "structure")


def _command(step: tuple[str, ...]) -> list[str]:
    """A step is either an argv, or a harness and mode to look the floor up by."""
    if step in FLOORS:
        return [sys.executable, "tools/floor.py", *step, FLOORS[step]]
    return list(step)


def _run(name: str) -> tuple[str, bool, str]:
    """Output is captured, because the gates do not finish in the order given."""
    output = []
    for step in GATES[name]:
        done = subprocess.run(
            _command(step), cwd=ROOT, capture_output=True, text=True
        )
        output.append(done.stdout + done.stderr)
        if done.returncode != 0:
            return name, False, "".join(output)
    return name, True, "".join(output)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("gates", nargs="*")
    parser.add_argument("--fast", action="store_true",
                        help="only the gates that read no corpus")
    parser.add_argument("--serial", action="store_true")
    parser.add_argument("-j", type=int, default=0, help="how many at once")
    args = parser.parse_args(argv)

    names = args.gates or (list(FAST) if args.fast else list(GATES))
    unknown = [n for n in names if n not in GATES]
    if unknown:
        print(f"unknown gate {unknown[0]!r}; expected one of {sorted(GATES)}")
        return 2

    # Every corpus gate is one CPU-bound process holding its own copy of the
    # corpus, so this is bounded by cores and by memory, not by the work.
    workers = args.j or min(len(names), max(1, (os.cpu_count() or 4) - 2))
    if args.serial or workers == 1:
        results = [_run(name) for name in names]
    else:
        with concurrent.futures.ThreadPoolExecutor(workers) as pool:
            results = list(pool.map(_run, names))

    for name, _, output in results:
        print(f"\n=== {name} " + "=" * (60 - len(name)), flush=True)
        print(output.rstrip(), flush=True)
    print("\n=== summary " + "=" * 53, flush=True)
    for name, ok, _ in results:
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}", flush=True)
    return 0 if all(ok for _, ok, _ in results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
