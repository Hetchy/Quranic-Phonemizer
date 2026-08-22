"""Mechanical shape checks for hand-authored semantic test tables."""
from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEMANTIC = ROOT / "tests" / "phonemize"
ARABIC = re.compile(r"[\u0600-\u06ff]")
LEGACY_DIRS = frozenset({"adjacent", "boundary", "laws", "nasal", "tafkheem", "waqf"})
CASE_BUILDERS = frozenset({"Case", "StateCase", "VariantCase"})
ID_FIRST_BUILDERS = frozenset({"_case", "_pausal", "elision", "wasl_case"})
FORBIDDEN_SOURCE_ALIASES = frozenset({
    "@long_a", "@long_i", "@long_u", "@wasl_alif",
})
MERGER_RULES = frozenset({
    "idgham_bi_ghunnah",
    "idgham_bila_ghunnah",
    "idgham_mutajanisayn_kamil",
    "idgham_mutajanisayn_naqis",
    "idgham_mutamathilayn",
    "idgham_mutaqaribayn",
    "idgham_shafawi",
    "lam_shamsiyyah",
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


def _has_arabic_comment(lines: list[str], line: int) -> bool:
    if line < 2:
        return False
    previous = lines[line - 2].strip()
    return previous.startswith("#") and ARABIC.search(previous) is not None


def _fingerprint(node: ast.expr) -> str | None:
    if not isinstance(node, ast.Call):
        return None
    name = _name(node.func)
    short = name.rsplit(".", 1)[-1]
    if short not in CASE_BUILDERS | ID_FIRST_BUILDERS:
        return None
    args = list(node.args)
    if short in ID_FIRST_BUILDERS and args:
        args = args[1:]
    keywords = [keyword for keyword in node.keywords if keyword.arg not in {"id", "name"}]
    normalized = ast.Call(func=ast.Name(id=short), args=args, keywords=keywords)
    return ast.dump(normalized, include_attributes=False)


def _rules(node: ast.AST) -> frozenset[str]:
    if not isinstance(node, ast.Call) or _name(node.func) != "R":
        return frozenset()
    return frozenset(
        arg.value for arg in node.args
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
    )


def _check_merger_sources(path: Path, node: ast.AST, out: list[Problem]) -> None:
    for mapping in (item for item in ast.walk(node) if isinstance(item, ast.Dict)):
        counts = {rule: 0 for rule in MERGER_RULES}
        for value in mapping.values:
            if value is None:
                continue
            for rule in _rules(value) & MERGER_RULES:
                counts[rule] += 1
        for rule, count in counts.items():
            hidden_muqattaat_source = "muqattaat" in path.name
            if count == 1 and not hidden_muqattaat_source:
                out.append((
                    path,
                    mapping.lineno,
                    f"{rule} needs both written source and host in char_rules",
                ))


def check() -> list[Problem]:
    out: list[Problem] = []
    seen: dict[str, tuple[Path, int]] = {}
    for legacy in sorted(LEGACY_DIRS):
        path = ROOT / "tests" / legacy
        if any(path.glob("*.py")):
            out.append((path, 1, "legacy semantic directory remains"))
    for path in sorted(SEMANTIC.rglob("test_*.py")):
        source = path.read_text(encoding="utf-8")
        lines = source.splitlines()
        tree = ast.parse(source)
        for alias in sorted(FORBIDDEN_SOURCE_ALIASES):
            if alias in source:
                out.append((path, 1, f"use the literal carrier instead of {alias}"))
        for keyword in (
            item for item in ast.walk(tree)
            if isinstance(item, ast.keyword) and item.arg == "char_rules"
        ):
            _check_merger_sources(path, keyword.value, out)
        cases = _cases(tree)
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        has_typed_cases = False
        for case in cases:
            if not _has_arabic_comment(lines, case.lineno):
                out.append((path, case.lineno, "CASES row needs an adjacent Arabic comment"))
            if not isinstance(case, ast.Call):
                out.append((path, case.lineno, "CASES row needs Case, StateCase, or pytest.param"))
                continue
            if isinstance(case, ast.Call) and _name(case.func) == "pytest.param":
                if not any(keyword.arg == "id" for keyword in case.keywords):
                    out.append((path, case.lineno, "pytest.param row needs a readable id"))
            short = _name(case.func).rsplit(".", 1)[-1] if isinstance(case, ast.Call) else ""
            has_typed_cases |= short in CASE_BUILDERS | ID_FIRST_BUILDERS
            fingerprint = _fingerprint(case)
            if fingerprint is None:
                continue
            previous = seen.get(fingerprint)
            if previous is not None:
                first, line = previous
                out.append((path, case.lineno, f"duplicate semantic case from {first.relative_to(ROOT)}:{line}"))
            else:
                seen[fingerprint] = (path, case.lineno)
        if has_typed_cases and not {"case_runs", "assert_case"} <= names:
            out.append((path, 1, "typed CASES must use case_runs and assert_case"))
    return out


def main() -> int:
    problems = check()
    for path, line, message in problems:
        print(f"{path.relative_to(ROOT)}:{line}: test-style: {message}")
    print(f"\n{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
