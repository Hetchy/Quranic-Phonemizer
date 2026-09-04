"""Declarative semantic cases and their execution expansion."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Generic, TypeVar

import pytest

from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import (
    KhilafId,
    Option,
    Riwayah,
    Script,
    VariantSelection,
)

from .boundary_case import ReadSpec
from .site import Site

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Pick(Generic[T]):
    values: dict[str, T]

    def for_run(self, riwayah: str, script: Script | None = None) -> T:
        if script is not None:
            exact = f"{riwayah}_{script.value}"
            if exact in self.values:
                return self.values[exact]
        return self.values[riwayah]


def pick(**per_riwayah: T) -> Pick[T]:
    return Pick(dict(per_riwayah))


def resolve(value: T | Pick[T], riwayah: str, script: Script | None = None) -> T:
    return value.for_run(riwayah, script) if isinstance(value, Pick) else value


@dataclass(frozen=True, slots=True)
class RuleExpectation:
    rules: frozenset[str]


def R(*rules: str) -> RuleExpectation:
    if not rules:
        raise ValueError("R() needs at least one rule")
    return RuleExpectation(frozenset(rules))


Phonemes = str | tuple[str, ...]
RuleMap = dict[str, RuleExpectation]


@dataclass(frozen=True, slots=True)
class Expect:
    read: ReadSpec
    phonemes: Phonemes | Pick[Phonemes]
    char_rules: RuleMap | Pick[RuleMap] = field(default_factory=dict)
    sound_rules: RuleMap | Pick[RuleMap] = field(default_factory=dict)
    absent_char_rules: RuleMap | Pick[RuleMap] = field(default_factory=dict)
    absent_sound_rules: RuleMap | Pick[RuleMap] = field(default_factory=dict)
    silent: tuple[str, ...] | Pick[tuple[str, ...]] = ()
    said: tuple[str, ...] | Pick[tuple[str, ...]] = ()
    all_rules: RuleExpectation | Pick[RuleExpectation] | None = None
    extra_phonemes: tuple[str, ...] | None = None
    selection: VariantSelection = VariantSelection()


@dataclass(frozen=True, slots=True)
class Case(Expect):
    id: str = ""
    site: Site = field(default_factory=Site)


@dataclass(frozen=True, slots=True)
class StateCase:
    id: str
    site: Site
    states: dict[str, Expect]


@dataclass(frozen=True, slots=True)
class VariantCase:
    id: str
    site: Site
    selector: KhilafId
    faces: dict[str, Expect]
    default: str
    masked: Expect | None = None


SemanticCase = Case | StateCase | VariantCase


@dataclass(frozen=True, slots=True)
class CaseRun:
    case_id: str
    state: str
    site: Site
    expect: Expect
    riwayah: str
    script: Script

    @property
    def id(self) -> str:
        suffix = f"-{self.state}" if self.state else ""
        return f"{self.case_id}{suffix}-{self.riwayah}-{self.script.value}"


def _states(case: SemanticCase):
    if isinstance(case, StateCase):
        return case.id, case.site, tuple(case.states.items())
    if isinstance(case, VariantCase):
        if case.default not in case.faces:
            raise ValueError(f"{case.id}: default {case.default!r} has no face")
        states = [
            (
                f"value-{value}",
                replace(
                    expect,
                    selection=VariantSelection((Option(case.selector, value),)),
                ),
            )
            for value, expect in case.faces.items()
        ]
        states.append(("default", case.faces[case.default]))
        if case.masked is not None:
            states.extend(
                (
                    f"masked-{value}",
                    replace(
                        case.masked,
                        selection=VariantSelection((Option(case.selector, value),)),
                    ),
                )
                for value in case.faces
            )
        return case.id, case.site, tuple(states)
    return case.id, case.site, (("", case),)


def case_runs(cases: tuple[SemanticCase, ...] | list[SemanticCase]):
    """Expand review rows into narrow pytest executions."""
    runs: list[CaseRun] = []
    for case in cases:
        case_id, site, states = _states(case)
        if not case_id:
            raise ValueError("every semantic case needs a readable id")
        for name in site.shipped():
            package = recitation(Riwayah(name))
            for script in package.scripts:
                for state, expect in states:
                    runs.append(CaseRun(case_id, state, site, expect, name, script))
    if not runs:
        return (pytest.param(None, marks=pytest.mark.skip(reason="no packaged riwayah")),)
    return tuple(pytest.param(run, id=run.id) for run in runs)
