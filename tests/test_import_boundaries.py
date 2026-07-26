"""ADR-007 §2: the dependency direction, checked over the AST.

This is the only defence that survives a careless refactor. Two of the rules
carry design weight rather than tidiness:

  * `rules` must not import `orthography` — the packaging expression of
    ADR-001 §1's one-way reference, and a second independent guard on the
    absent grapheme field.
  * `render` must not import `rules`, `canon` or `engine` — a projection
    cannot re-detect a rule if it cannot import a classifier.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

PACKAGE = pathlib.Path(__file__).resolve().parent.parent / "quranic_phonemizer"

#: package -> what it may import from this package. `riwayat` is the assembly
#: point and may import anything; nothing imports *it*, which is what keeps a
#: second riwayah additive.
ALLOWED: dict[str, frozenset[str]] = {
    "model": frozenset(),
    "orthography": frozenset({"model"}),
    "canon": frozenset({"model", "orthography"}),
    "engine": frozenset({"model"}),
    "rules": frozenset({"model", "engine"}),
    "render": frozenset({"model"}),
    "riwayat": frozenset(
        {"model", "orthography", "canon", "engine", "rules", "render", "corpus"}
    ),
    "corpus": frozenset({"model"}),
    #: Root modules. `api.py` is the composition root and `__init__.py` its
    #: re-export, so both sit with `riwayat`; `dataio.py` imports nothing.
    "": frozenset(
        {"model", "orthography", "canon", "engine", "rules", "render",
         "riwayat", "corpus"}
    ),
}

#: `canon` may import the adapter protocol only, not the whole package.
MODULE_ALLOWED: dict[tuple[str, str], frozenset[str]] = {
    ("canon", "orthography"): frozenset({"adapter"}),
}

#: Modules from the superseded implementation, pending deletion (ADR-007 §7).
#: The set only shrinks. A new module must never be added here.
LEGACY: frozenset[str] = frozenset()


def _modules() -> list[pathlib.Path]:
    return sorted(p for p in PACKAGE.rglob("*.py") if "__pycache__" not in p.parts)


def _key(path: pathlib.Path) -> str:
    return path.relative_to(PACKAGE).with_suffix("").as_posix()


def _imported_packages(tree: ast.AST, own_package: str) -> set[tuple[str, str]]:
    """Intra-package imports, as (package, first module segment) pairs."""
    found: set[tuple[str, str]] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not node.level:
            continue
        parts = (node.module or "").split(".")
        if node.level == 1 and own_package:
            # `from .x import y` inside a subpackage stays in that subpackage
            parts = [own_package, *parts]
        parts = [p for p in parts if p]
        if not parts:
            continue
        head, tail = parts[0], parts[1] if len(parts) > 1 else ""
        found.add((head, tail))
    return found


@pytest.mark.parametrize("path", _modules(), ids=_key)
def test_module_imports_only_what_it_may(path: pathlib.Path) -> None:
    key = _key(path)
    if key in LEGACY:
        pytest.skip("superseded implementation, pending deletion")

    parts = key.split("/")
    own = parts[0] if len(parts) > 1 else ""
    if own and own not in ALLOWED:
        pytest.fail(f"{key}: package {own!r} is not in the ADR-007 §2 table")

    permitted = ALLOWED.get(own, frozenset())
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for package, module in _imported_packages(tree, own):
        if package == own or package not in ALLOWED:
            continue
        assert package in permitted, (
            f"{key} imports {package!r}, which ADR-007 §2 forbids "
            f"(allowed: {sorted(permitted)})"
        )
        narrow = MODULE_ALLOWED.get((own, package))
        if narrow is not None:
            assert module in narrow, (
                f"{key} imports {package}.{module or '<package>'}; only "
                f"{sorted(narrow)} is reachable from {own!r}"
            )


def test_no_phoneme_strings_outside_render() -> None:
    """ADR-007 §4.9. The output alphabet is data, and it lives in one place."""
    offenders = []
    for path in _modules():
        key = _key(path)
        if key in LEGACY or key.startswith("render/"):
            continue
        text = path.read_text(encoding="utf-8")
        for marker in ("ˤ", "ː", "m̃", "ñ"):
            if marker in text:
                offenders.append(f"{key}: {marker!r}")
    assert not offenders, "phoneme notation outside render/: " + ", ".join(offenders)


def test_legacy_set_only_names_modules_that_exist() -> None:
    """Keeps the skip list honest: a deleted module must leave the set."""
    present = {_key(p) for p in _modules()}
    stale = sorted(LEGACY - present)
    assert not stale, f"LEGACY names modules that no longer exist: {stale}"
