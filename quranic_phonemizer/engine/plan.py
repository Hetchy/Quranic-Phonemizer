"""Effects, the Plan that accumulates them, and conflict detection.

A rule affects a neighbour only by declaring an effect naming it, never by
writing to it directly -- there is no shared mutable structure to corrupt.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TypeAlias

from ..model.address import OccurrenceId, SlotId
from ..model.canon import Rule
from ..model.performance import Aspect, Occurrence, Side, Sound


class Phase(StrEnum):
    """Closed and ordered. Within a phase, rules are unordered and
    conflicts are errors."""

    BOUNDARY = "boundary"
    MERGE = "merge"
    LENGTH = "length"
    COLOUR = "colour"
    RELEASE = "release"


class Length(StrEnum):
    SHORT = "short"
    LONG = "long"


class SoundFeature(StrEnum):
    EMPHATIC = "emphatic"


@dataclass(frozen=True, slots=True)
class Realize:
    slot: SlotId
    aspect: Aspect
    sound: Sound


@dataclass(frozen=True, slots=True)
class MergeInto:
    slot: SlotId
    aspect: Aspect
    host: SlotId
    host_aspect: Aspect


@dataclass(frozen=True, slots=True)
class Silence:
    """Removes a slot's sound. The occurrence's own rule is the reason;
    there is no separate reason field."""

    slot: SlotId
    aspect: Aspect


@dataclass(frozen=True, slots=True)
class Insert:
    anchor: tuple[SlotId, Side]
    aspect: Aspect
    sound: Sound


@dataclass(frozen=True, slots=True)
class Recolour:
    """Sets one named feature rather than a single boolean, since the
    COLOUR phase decides more than one feature per sound."""

    slot: SlotId
    aspect: Aspect
    feature: SoundFeature
    value: bool


@dataclass(frozen=True, slots=True)
class Relength:
    """Nucleus-only by definition, and keyed on `(SlotId, NUCLEUS)`."""

    slot: SlotId
    length: Length


Effect: TypeAlias = Realize | MergeInto | Silence | Insert | Recolour | Relength


@dataclass(frozen=True, slots=True)
class Verdict:
    occurrence: Occurrence
    effects: tuple[Effect, ...]


def conflict_key(effect: Effect) -> tuple:
    """The (target, aspect) an effect claims, for conflict detection.

    `Relength` always keys on NUCLEUS, its only aspect; `Insert` keys on its
    anchor and side instead of a slot and aspect.
    """
    match effect:
        case Relength(slot=slot):
            return (slot, Aspect.VOWEL)
        case Insert(anchor=(slot, side)):
            return (slot, side)
        case _:
            return (effect.slot, effect.aspect)


#: Spaces ordinals by rule, so two rules firing on the same slot mint
#: distinct occurrence ids.
_RULE_SLOT_STRIDE = 1_000_000

#: Separates two classifiers that legitimately declare the same `Rule` on
#: the same slot (different aspects) -- rule plus slot alone is not unique.
_VARIANT_STRIDE = 100_000_000


def mint(rule: Rule, at: SlotId, variant: int = 0) -> OccurrenceId:
    """Mint a stable occurrence id from rule, slot, and variant.

    `variant` is a small integer, not the classifier's identity -- ids must
    stay stable across runs.
    """
    ordinal = (
        variant * _VARIANT_STRIDE
        + list(Rule).index(rule) * _RULE_SLOT_STRIDE
        + at.ordinal
    )
    return OccurrenceId(at.verse, ordinal)


class ConflictError(ValueError):
    """Names both occurrence tags and both rules. Never last-writer-wins."""


@dataclass(slots=True)
class Plan:
    """Append-only journal: keyed for conflict detection, ordered for replay."""

    entries: list[tuple[Phase, Verdict]] = field(default_factory=list)
    _keys: dict[tuple[Phase, tuple], tuple[OccurrenceId, Rule]] = field(
        default_factory=dict
    )

    def record(self, phase: Phase, verdict: Verdict) -> None:
        for effect in verdict.effects:
            key = (phase, conflict_key(effect))
            existing = self._keys.get(key)
            if existing is not None:
                raise ConflictError(
                    f"{phase.value}: two effects on {key[1]} — "
                    f"{existing[1].value} ({existing[0]}) and "
                    f"{verdict.occurrence.rule.value} ({verdict.occurrence.id}). "
                    f"Exactly one rule of a family fires per trigger; this is a "
                    f"found bug, not a precedence question."
                )
            self._keys[key] = (verdict.occurrence.id, verdict.occurrence.rule)
        self.entries.append((phase, verdict))

    def effects(self, phase: Phase | None = None):
        for recorded_phase, verdict in self.entries:
            if phase is None or recorded_phase is phase:
                yield from verdict.effects

    def merged_away(self, slot: SlotId, aspect: Aspect) -> bool:
        return any(
            isinstance(effect, (MergeInto, Silence))
            and effect.slot == slot
            and effect.aspect is aspect
            for effect in self.effects()
        )
