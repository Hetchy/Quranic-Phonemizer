"""Every gate, and the one place the ratchet numbers live.

Run: python tools/gates.py [gate ...]     no argument runs all of them
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

#: A floor may only rise, a ceiling may only fall. Moving one is a claim about
#: which refs changed, so the commit that moves it says which and why. Every
#: row behind a floor short of total is in docs/conformance/gate-residues.md.
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


def _command(step: tuple[str, ...]) -> list[str]:
    """A step is either an argv, or a harness and mode to look the floor up by."""
    if step in FLOORS:
        return [sys.executable, "tools/floor.py", *step, FLOORS[step]]
    return list(step)


def _run(name: str) -> bool:
    print(f"\n=== {name} " + "=" * (60 - len(name)), flush=True)
    for step in GATES[name]:
        result = subprocess.run(_command(step), cwd=ROOT)
        if result.returncode != 0:
            return False
    return True


def main(argv: list[str]) -> int:
    names = argv or list(GATES)
    unknown = [n for n in names if n not in GATES]
    if unknown:
        print(f"unknown gate {unknown[0]!r}; expected one of {sorted(GATES)}")
        return 2

    results = {name: _run(name) for name in names}
    print("\n=== summary " + "=" * 53, flush=True)
    for name, ok in results.items():
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}", flush=True)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
