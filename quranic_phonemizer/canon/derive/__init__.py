"""Derivations: the facts no script writes, resolved in one shared place.

A scalar either carries a canonical value outright — declared in the
inventory — or names a derivation here. There is no third way, and no
derivation may consult a `Script`: doing so would make the canonical layer
script-relative, which is the failure R9 clause 2 fires on.

Each derivation is one module, so each is one testable unit and each appears
**by name** in the L1 residue report (ADR-007 §5). A residue row whose class is
`UNCLASSIFIED` is a failed equality proof, not a rounding error.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Callable, TypeAlias

from ...model.canon import CanonLetter, Nucleus, Onset, RuleFamily
from ...model.inscription import SlotFact
from ...orthography.adapter import Cluster


class Target(StrEnum):
    """Which draft slot a resolution lands on."""

    HERE = "here"
    PREVIOUS = "previous"


@dataclass(frozen=True, slots=True)
class Sets:
    """A canonical fact, on this cluster's slot or on the previous one."""

    fact: SlotFact
    value: object
    target: Target = Target.HERE


@dataclass(frozen=True, slots=True)
class AddsSlot:
    """One grapheme evidencing facts on **two** slots.

    Routine rather than exotic: the tanwīn mark does it at 8,893 words and
    three compact muqaṭṭaʿāt graphemes fan to seven slots (ADR-001 §3.5b).
    """

    fact: SlotFact
    value: object
    letter: CanonLetter
    onset: Onset
    nucleus: Nucleus


@dataclass(frozen=True, slots=True)
class Attests:
    """A performance outcome, not a canonical fact. Names a family."""

    family: RuleFamily
    target: Target = Target.HERE


@dataclass(frozen=True, slots=True)
class Shows:
    """Supplies nothing; decorates the named slot so a projection can point at
    it. The maddah is the case that forced this to exist separately from
    'contributes nothing' (ADR-003 §4.0)."""

    target: Target = Target.HERE


@dataclass(frozen=True, slots=True)
class Absent:
    """The cluster produces no slot at all — a length carrier, an otiose seat.
    `shows` names the slot a projection should attribute it to."""

    shows: Target = Target.PREVIOUS


Outcome: TypeAlias = Sets | AddsSlot | Attests | Shows | Absent


@dataclass(frozen=True, slots=True)
class Context:
    """Everything a derivation may see. Deliberately no `Script`."""

    clusters: tuple[Cluster, ...]
    index: int
    word_bounds: tuple[int, int]
    """[start, end) cluster indices of the word this cluster belongs to."""
    previous_nucleus: Nucleus | None
    previous_letter: CanonLetter | None
    lexicon: object
    """The canonical-skeleton lexicon. Keyed by canonical letters, never by a
    glyph, which is what makes it script-independent."""

    @property
    def cluster(self) -> Cluster:
        return self.clusters[self.index]

    @property
    def word_initial(self) -> bool:
        return self.index == self.word_bounds[0]

    @property
    def word_final(self) -> bool:
        return self.index == self.word_bounds[1] - 1

    def ahead(self, step: int = 1) -> Cluster | None:
        nxt = self.index + step
        return self.clusters[nxt] if nxt < self.word_bounds[1] else None


Derivation: TypeAlias = Callable[[Context], Outcome]

_REGISTRY: dict[str, Derivation] = {}


def register(name: str) -> Callable[[Derivation], Derivation]:
    def decorate(fn: Derivation) -> Derivation:
        if name in _REGISTRY:
            raise ValueError(f"derivation {name!r} is already registered")
        _REGISTRY[name] = fn
        return fn

    return decorate


def resolve(name: str, context: Context) -> Outcome:
    derivation = _REGISTRY.get(name)
    if derivation is None:
        raise KeyError(
            f"no derivation named {name!r}; an inventory referenced it but "
            f"canon/derive/ has no module for it. Registered: {sorted(_REGISTRY)}"
        )
    return derivation(context)


def registered() -> tuple[str, ...]:
    return tuple(sorted(_REGISTRY))
