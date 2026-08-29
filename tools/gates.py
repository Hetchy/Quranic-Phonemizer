"""Run the checks required by pull requests.

Run: python tools/gates.py [--serial] [-jN] [gate ...]
"""
from __future__ import annotations

import argparse
import concurrent.futures
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

GATES: dict[str, tuple[tuple[str, ...], ...]] = {
    "suite": ((
        sys.executable, "-m", "pytest", "tests/", "-q", "-n", "2",
    ),),
    "lint": ((sys.executable, "-m", "ruff", "check", "."),),
    "structure": ((sys.executable, "tools/structure_lint.py"),),
    "test-style": ((sys.executable, "tools/test_style_lint.py"),),
}

def _run(name: str) -> tuple[str, bool, str]:
    """Output is captured, because the gates do not finish in the order given."""
    output = []
    for step in GATES[name]:
        done = subprocess.run(
            list(step), cwd=ROOT, capture_output=True, text=True
        )
        output.append(done.stdout + done.stderr)
        if done.returncode != 0:
            return name, False, "".join(output)
    return name, True, "".join(output)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("gates", nargs="*")
    parser.add_argument("--serial", action="store_true")
    parser.add_argument("-j", type=int, default=0, help="how many at once")
    args = parser.parse_args(argv)

    names = args.gates or list(GATES)
    unknown = [n for n in names if n not in GATES]
    if unknown:
        print(f"unknown gate {unknown[0]!r}; expected one of {sorted(GATES)}")
        return 2

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
