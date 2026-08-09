"""Run a gate harness and check its number against a ratchet floor/ceiling.

Floors live in `tools/gates.py`, which is what CI runs.

Run: python tools/floor.py cross|regression|l1 word|verse|- FLOOR
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

HARNESS = {
    "cross": ("cross_parity.py", "words agree across scripts"),
    "regression": ("parity.py", "words match"),
    "l1": ("l1_harness.py", "L1 residue"),
    "roundtrip": ("roundtrip.py", "verses round-trip"),
    "attest": ("attest.py", "unmet attestations"),
}


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    gate, mode, floor_text = argv
    if gate not in HARNESS:
        print(f"unknown gate {gate!r}; expected one of {sorted(HARNESS)}")
        return 2
    script, _ = HARNESS[gate]

    command = [sys.executable, str(ROOT / "tools" / script), "--show", "0"]
    if mode != "-":
        flag = "--script" if gate in ("roundtrip", "attest") else "--mode"
        command += [flag, mode]
    result = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)
    output = result.stdout + result.stderr
    print(output)
    if result.returncode not in (0, 1):
        print(f"{script} crashed (exit {result.returncode})")
        return result.returncode

    label = f"{gate} {mode}".strip(" -")
    if gate in ("l1", "attest"):
        return _ceiling(output, label, int(floor_text))
    return _floor(output, label, float(floor_text))


def _floor(output: str, label: str, floor: float) -> int:
    """A percentage that may only rise."""
    found = re.search(r"\(([0-9.]+)%\)", output)
    if not found:
        print(f"{label}: no percentage in the harness output")
        return 2
    value = float(found.group(1))
    if value + 1e-9 < floor:
        print(f"FAIL {label}: {value:.3f}% is below the floor of {floor:.3f}%")
        return 1
    print(f"ok {label}: {value:.3f}% (floor {floor:.3f}%)")
    if value > floor + 1e-9:
        print(f"     the floor can be raised to {value:.3f}%")
    return 0


def _ceiling(output: str, label: str, ceiling: int) -> int:
    """A residue count that may only fall."""
    found = re.search(r"(?:L1 residue|unmet attestations):\s*(\d+)", output)
    if not found:
        print(f"{label}: no residue count in the harness output")
        return 2
    value = int(found.group(1))
    if value > ceiling:
        print(f"FAIL {label}: residue {value} is above the ceiling of {ceiling}")
        return 1
    print(f"ok {label}: residue {value} (ceiling {ceiling})")
    if value < ceiling:
        print(f"     the ceiling can be lowered to {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
