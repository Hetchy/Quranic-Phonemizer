"""Effects, the Plan, and conflict.

A rule affects a neighbour by **declaring an effect naming it**, never by
writing to it. That is the whole of ADR-004 §2, and it is what makes the
`owner.segments.pop(index)` class of bug unwriteable: there is nothing to pop.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TypeAlias

from ..model.address import OccurrenceId, SlotId
from ..model.canon import Phase, Rule
from ..model.performance import Aspect, Occurrence, Side, SoundSpec


class Length(StrEnum):
    SHORT = "short"
    LONG = "long"


class SoundFeature(StrEnum):
    EMPHATIC = "emphatic"
    NASAL = "nasal"


@dataclass(frozen=True, slots=True)
class Realize:
    slot: SlotId
    aspect: Aspect
    sounds: tuple[SoundSpec, ...]


@dataclass(frozen=True, slots=True)
class MergeInto:
    slot: SlotId
    aspect: Aspect
    host: SlotId
    host_aspect: Aspect


@dataclass(frozen=True, slots=True)
class Silence:
    """The reason is the verdict's own `Occurrence.rule` (ADR-002 §4.1)."""

    slot: SlotId
    aspect: Aspect


@dataclass(frozen=True, slots=True)
class Insert:
    anchor: tuple[SlotId, Side]
    aspect: Aspect
    sounds: tuple[SoundSpec, ...]


@dataclass(frozen=True, slots=True)
class Recolour:
    """Carries a feature, not a bare boolean: a boolean covered one of the two
    things the `COLOUR` phase decides, and ghunnah quality had no member."""

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
    """Per ADR-004 §4. `Relength` keys on the nucleus because that is the only
    aspect it can touch; `Insert` keys on the anchor and side, because two
    rules inserting on the same side of the same slot is the conflict."""
    match effect:
        case Relength(slot=slot):
            return (slot, Aspect.NUCLEUS)
        case Insert(anchor=(slot, side)):
            return (slot, side)
        case _:
            return (effect.slot, effect.aspect)


#: Occurrence ids are minted from the rule and the site that caused it, so two
#: rules firing on one slot stay distinguishable. `SoundId` and `OccurrenceId`
#: are request-local, so any injection is fine as long as it is a function.
_RULE_SLOT_STRIDE = 1_000_000


def mint(rule: Rule, at: SlotId) -> OccurrenceId:
    ordinal = list(Rule).index(rule) * _RULE_SLOT_STRIDE + at.ordinal
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

    def verdict_for(self, slot: SlotId, aspect: Aspect) -> Verdict | None:
        for _, verdict in self.entries:
            for effect in verdict.effects:
                if getattr(effect, "slot", None) == slot and (
                    getattr(effect, "aspect", None) is aspect
                ):
                    return verdict
        return None

    def merged_away(self, slot: SlotId, aspect: Aspect) -> bool:
        return any(
            isinstance(effect, (MergeInto, Silence))
            and effect.slot == slot
            and effect.aspect is aspect
            for effect in self.effects()
        )
