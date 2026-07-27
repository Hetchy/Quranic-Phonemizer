"""Derivations: the facts no script writes, resolved in one shared place.

A scalar either carries a canonical value outright or names a derivation
here; no derivation may consult a `Script`.
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
    """One grapheme evidencing facts on two slots.

    Routine rather than exotic: the tanween mark does this, as does a
    compact muqattaat grapheme fanning to several slots.
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
    """Supplies nothing; decorates the named slot so a projection can point
    at it, unlike `Absent`, which names a cluster with no slot at all."""

    target: Target = Target.HERE


@dataclass(frozen=True, slots=True)
class Absent:
    """The cluster produces no slot at all - a length carrier, an otiose seat.
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
_REQUIRED_ROLES: dict[str, frozenset[str]] = {}


def register(
    name: str, *, requires: tuple[str, ...] = ()
) -> Callable[[Derivation], Derivation]:
    """`requires` names the inventory roles this derivation reads.

    `Cluster.has` returns `False`, never raises, for an undeclared role, so
    a typo would silently change output instead of failing at load time.
    """

    def decorate(fn: Derivation) -> Derivation:
        if name in _REGISTRY:
            raise ValueError(f"derivation {name!r} is already registered")
        _REGISTRY[name] = fn
        _REQUIRED_ROLES[name] = frozenset(requires)
        return fn

    return decorate


def required_roles() -> dict[str, frozenset[str]]:
    """Which roles each registered derivation reads.

    Per derivation, not a union: a mark one script writes and another does
    not carries a role only the first can declare.
    """
    return dict(_REQUIRED_ROLES)


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


def _load_all() -> None:
    """Import every derivation module so the registry is complete.

    At the bottom because these modules import the vocabulary defined above.
    An empty registry would make a validator pass everything silently.
    """
    from . import (  # noqa: F401
        gemination,
        length,
        lexeme,
        silah,
        tanween,
        wasl,
    )


_load_all()
