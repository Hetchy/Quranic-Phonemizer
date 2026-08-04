"""Check source comments against the project's comment rules.

Run:  python tools/comment_lint.py [--summary] [paths...]
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_TARGETS = ("quranic_phonemizer", "tools", "tests")

#: Arabic script and its supplement, allowed when quoting a word or a mark.
ARABIC = ((0x600, 0x6FF), (0x750, 0x77F), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF))

#: Non-ASCII that is not Arabic and not a phoneme symbol inside a string.
SYMBOLS = "§×²·–—‘’“”…"

BANNED = [
    (re.compile(r"\bADR-\d"), "design-document reference"),
    (re.compile(r"\b\d\d-[a-z][a-z-]*\b"), "design-document reference"),
    (re.compile(r"\b[\w-]+\.md\b"), "design-document reference"),
    (re.compile(r"\bdocs/"), "design-document reference"),
    (re.compile(r"§"), "section reference"),
    (re.compile(
        r"\b(sections?|secs?|clauses?|items?|rows?|questions?|steps?|parts?"
        r"|tables?|figures?|appendices|appendix)\s+\d", re.I),
     "numbered cross-reference"),
    (re.compile(r"(?<![\w.:])\d{1,2}\.\d{1,2}(?![\d\w])"),
     "numbered cross-reference"),
    (re.compile(r"\bopen question\b", re.I), "numbered cross-reference"),
    (re.compile(r"\b[A-Z]\d{1,2}\b(?!\w)"), "codename"),
    (re.compile(r"\bphase[- ]\d|\bphase [A-E]\b", re.I), "phase reference"),
    (re.compile(r"\brefactor|\brebuild\b|\bthe old implementation\b"
                r"|\bused to\b|\bpreviously\b|\bformerly\b"
                r"|\bhas been (moved|renamed|removed|replaced)\b", re.I),
     "history"),
    (re.compile(r"which is why|the whole argument|did its job|reads as done",
                re.I), "narration"),
    (re.compile(r"\b\d[\d,]{2,}\b"), "corpus measurement"),
]

#: Budgets. A docstring longer than this is a signal to simplify the code.
MODULE_DOC, DEF_DOC = 3, 3


def check(path: pathlib.Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    prose = _docstring_lines(source)
    return [*_prose_problems(path, source, prose),
            *_budget_problems(path, source)]


def _is_arabic(char: str) -> bool:
    point = ord(char)
    return any(low <= point <= high for low, high in ARABIC)


def _prose_problems(
    path: pathlib.Path, source: str, prose: frozenset[int]
) -> list[str]:
    out = []
    for number, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if not (stripped.startswith("#") or number in prose):
            continue
        for pattern, label in BANNED:
            if pattern.search(line):
                out.append(f"{path}:{number}: {label}: {stripped[:70]}")
        for char in line:
            if ord(char) > 127 and not _is_arabic(char):
                out.append(
                    f"{path}:{number}: non-ascii {char!r}: {stripped[:70]}"
                )
                break
    return out


def _docstring_lines(source: str) -> frozenset[int]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return frozenset()
    holders = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    lines: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, holders):
            continue
        for child in node.body:
            if (
                isinstance(child, ast.Expr)
                and isinstance(child.value, ast.Constant)
                and isinstance(child.value.value, str)
            ):
                lines.update(range(child.lineno, (child.end_lineno or 0) + 1))
    return frozenset(lines)


def _budget_problems(path: pathlib.Path, source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [f"{path}: does not parse"]
    out = []
    for node in ast.walk(tree):
        if not isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                   ast.AsyncFunctionDef)
        ):
            continue
        text = ast.get_docstring(node, clean=True)
        if not text:
            continue
        length = len([line for line in text.splitlines() if line.strip()])
        budget = MODULE_DOC if isinstance(node, ast.Module) else DEF_DOC
        if length > budget:
            where = getattr(node, "lineno", 1)
            name = getattr(node, "name", path.name)
            out.append(
                f"{path}:{where}: docstring of {name!r} is {length} lines, "
                f"budget {budget}"
            )
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", default=[])
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    targets = [pathlib.Path(p) for p in args.paths] or [
        ROOT / name for name in DEFAULT_TARGETS
    ]
    files = sorted(
        f for target in targets
        for f in ([target] if target.is_file() else target.rglob("*.py"))
        if "__pycache__" not in f.parts
    )
    problems = [problem for f in files for problem in check(f)]
    if args.summary:
        counts: dict[str, int] = {}
        for problem in problems:
            key = problem.split(": ", 2)[1] if ": " in problem else "other"
            counts[key] = counts.get(key, 0) + 1
        for key, count in sorted(counts.items(), key=lambda kv: -kv[1]):
            print(f"{count:5d}  {key}")
    else:
        for problem in problems:
            print(problem)
    print(f"\n{len(problems)} problems in {len(files)} files")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
