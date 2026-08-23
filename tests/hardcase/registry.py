"""Map each published rule to the declarative cases that exercise it."""
from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass

import tests.phonemize
from tests.document.test_ishmam import (
    test_the_ishmam_classifies_the_consonant_and_owns_no_sound,
    test_the_ishmam_names_one_letter_and_reads_nothing_beside_it,
)
from tests.support.case import (
    Case,
    Expect,
    Pick,
    RuleExpectation,
    StateCase,
    VariantCase,
)


@dataclass(frozen=True, slots=True)
class FixtureRef:
    source: str


def _rules(value) -> frozenset[str]:
    if value is None:
        return frozenset()
    if isinstance(value, RuleExpectation):
        return value.rules
    if isinstance(value, Pick):
        return frozenset().union(*(_rules(item) for item in value.values.values()))
    if isinstance(value, dict):
        return frozenset().union(*(_rules(item) for item in value.values()))
    return frozenset()


def _expects(case) -> tuple[Expect, ...]:
    if isinstance(case, Case):
        return (case,)
    if isinstance(case, StateCase):
        return tuple(case.states.values())
    if isinstance(case, VariantCase):
        masked = () if case.masked is None else (case.masked,)
        return (*case.faces.values(), *masked)
    raise TypeError(f"unknown semantic case {type(case).__name__}")


def _case_rules(case) -> frozenset[str]:
    return frozenset().union(*(
        _rules(value)
        for expect in _expects(case)
        for value in (expect.char_rules, expect.sound_rules, expect.all_rules)
    ))


def _semantic_fixtures() -> dict[str, set[FixtureRef]]:
    found: dict[str, set[FixtureRef]] = {}
    prefix = f"{tests.phonemize.__name__}."
    modules = pkgutil.walk_packages(tests.phonemize.__path__, prefix)
    for info in modules:
        if not info.name.rsplit(".", 1)[-1].startswith("test_"):
            continue
        module = importlib.import_module(info.name)
        for case in getattr(module, "CASES", ()):
            fixture = FixtureRef(
                f"{info.name.replace('.', '/')}.py::{case.id}"
            )
            for rule in _case_rules(case):
                found.setdefault(rule, set()).add(fixture)
    return found


def _function_ref(function) -> FixtureRef:
    return FixtureRef(
        f"{function.__module__.replace('.', '/')}.py::{function.__name__}"
    )


_FIXTURES = _semantic_fixtures()
_FIXTURES["ishmam"] = {
    _function_ref(test_the_ishmam_classifies_the_consonant_and_owns_no_sound),
    _function_ref(test_the_ishmam_names_one_letter_and_reads_nothing_beside_it),
}

RULE_FIXTURES: dict[str, tuple[FixtureRef, ...]] = {
    rule: tuple(sorted(fixtures, key=lambda fixture: fixture.source))
    for rule, fixtures in sorted(_FIXTURES.items())
}


__all__ = ["FixtureRef", "RULE_FIXTURES"]
