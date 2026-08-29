"""Run explicit targeted tests and the required lightweight checks."""
from __future__ import annotations

import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]


def _run(command: list[str]) -> int:
    return subprocess.run(command, cwd=ROOT).returncode


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: python tools/quick.py TEST_PATH [TEST_PATH ...]")
        return 2
    commands = (
        [sys.executable, "tools/structure_lint.py"],
        [sys.executable, "tools/test_style_lint.py", *argv],
        [sys.executable, "-m", "pytest", *argv, "-q"],
    )
    for command in commands:
        if result := _run(command):
            return result
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
