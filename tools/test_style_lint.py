"""Mechanical shape checks for hand-authored semantic test tables."""
from __future__ import annotations

import ast
import importlib.util
import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEMANTIC = ROOT / "tests" / "phonemize"
SOURCE_BUILDERS = frozenset({
    "Case", "StateCase", "VariantCase", "_case", "_pausal", "elision",
    "wasl_case", "_started", "_joined",
})

Problem = tuple[Path, int, str]


def _name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_name(node.value)}.{node.attr}"
    return ""


def _cases(tree: ast.Module) -> tuple[ast.expr, ...]:
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else (node.target,)
        if not any(isinstance(target, ast.Name) and target.id == "CASES" for target in targets):
            continue
        if isinstance(node.value, (ast.Tuple, ast.List)):
            return tuple(node.value.elts)
    return ()


def _call_id(node: ast.expr) -> str | None:
    if not isinstance(node, ast.Call):
        return None
    for keyword in node.keywords:
        if keyword.arg in {"id", "name"} and isinstance(keyword.value, ast.Constant):
            if isinstance(keyword.value.value, str):
                return keyword.value.value
    if node.args and isinstance(node.args[0], ast.Constant):
        if isinstance(node.args[0].value, str):
            return node.args[0].value
    return None


def _source_comment_block(lines: list[str], line: int) -> list[str]:
    index = line - 2
    block: list[str] = []
    while index >= 0 and lines[index].strip().startswith("#"):
        block.append(lines[index].strip()[1:].strip())
        index -= 1
    return list(reversed(block))


def _source_text(site, riwayah: str) -> str:
    from tests.support.reading import _through, _words, loaded
    from quranic_phonemizer.model.address import Riwayah, Script

    address = site.address(riwayah)
    record = loaded(riwayah)
    words = _words(record, Riwayah(riwayah), Script.UTHMANI, address.verse)
    count = record.corpus.surah_info[str(address.verse.surah)][address.verse.ayah - 1]
    if address.words and max(address.words) > count:
        words = _through(record, Riwayah(riwayah), Script.UTHMANI, address.verse)
    return " ".join(
        text for index, (_, text) in enumerate(words, 1)
        if not address.words or index in address.words
    )


def _source_comment_problems(
    path: Path, tree: ast.Module, lines: list[str]
) -> list[Problem]:
    rows = _cases(tree)
    targets = {
        _call_id(row): row.lineno
        for row in rows
        if isinstance(row, ast.Call)
        and _name(row.func).rsplit(".", 1)[-1] in SOURCE_BUILDERS
        and _call_id(row) is not None
    }
    if not targets:
        return []
    sys.path.insert(0, str(ROOT))
    try:
        spec = importlib.util.spec_from_file_location(
            f"source_comments_{abs(hash(path))}", path
        )
        if spec is None or spec.loader is None:
            return [(path, 1, "cannot load semantic module for source comments")]
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as error:
        return [(path, 1, f"source comment import failed: {error}")]
    finally:
        if sys.path and sys.path[0] == str(ROOT):
            sys.path.pop(0)
    cases = {case.id: case for case in getattr(module, "CASES", ())}
    out: list[Problem] = []
    for case_id, line in targets.items():
        case = cases.get(case_id)
        if case is None:
            out.append((path, line, f"source comment has unknown case {case_id!r}"))
            continue
        expected = [
            f"{riwayah.title()}: {_source_text(case.site, riwayah)}"
            for riwayah in ("hafs", "warsh")
            if riwayah in case.site.addresses
        ]
        actual = _source_comment_block(lines, line)
        if actual != expected:
            out.append((
                path,
                line,
                f"source comments for {case_id!r} must be {expected!r}",
            ))
    return out


def _semantic_paths(paths: tuple[str, ...]) -> tuple[Path, ...]:
    if not paths:
        return tuple(sorted(SEMANTIC.rglob("test_*.py")))
    selected = []
    for raw in paths:
        path = (ROOT / raw.split("::", 1)[0]).resolve()
        if path.is_file() and path.suffix == ".py" and SEMANTIC in path.parents:
            selected.append(path)
    return tuple(dict.fromkeys(selected))


def check(paths: tuple[str, ...] = ()) -> list[Problem]:
    out: list[Problem] = []
    for path in _semantic_paths(paths):
        source = path.read_text(encoding="utf-8")
        lines = source.splitlines()
        tree = ast.parse(source)
        out.extend(_source_comment_problems(path, tree, lines))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args()
    problems = check(tuple(args.paths))
    for path, line, message in problems:
        print(f"{path.relative_to(ROOT)}:{line}: test-style: {message}")
    print(f"\n{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
