"""Attribution and modifier edges, resolved to sound and occurrence positions.

Each edge keeps the model's slots and aspect; an inserted sound stays distinct
from a hosted one, so insertions, mergers, and silences read off by type.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from ..model.address import OccurrenceId, SlotId, SoundId
from ..model.performance import (
    Aspect,
    Classifies,
    Hosts,
    Inserted,
    Length,
    MergedInto,
    Performance,
    Recolours,
    SetsLength,
    Side,
    Silent,
)


@dataclass(frozen=True, slots=True)
class Hosted:
    slots: tuple[SlotId, ...]
    aspect: Aspect
    sound: int
    by: int | None


@dataclass(frozen=True, slots=True)
class Insertion:
    anchor: tuple[SlotId, Side]
    aspect: Aspect
    sound: int
    by: int | None


@dataclass(frozen=True, slots=True)
class Merged:
    slots: tuple[SlotId, ...]
    aspect: Aspect
    sound: int
    by: int


@dataclass(frozen=True, slots=True)
class Silenced:
    slots: tuple[SlotId, ...]
    aspect: Aspect
    by: int | None


Attribution: TypeAlias = Hosted | Insertion | Merged | Silenced


@dataclass(frozen=True, slots=True)
class Recoloured:
    sound: int
    by: int


@dataclass(frozen=True, slots=True)
class Relengthened:
    sound: int
    by: int
    length: Length


@dataclass(frozen=True, slots=True)
class Classified:
    sound: int
    by: int


Modifier: TypeAlias = Recoloured | Relengthened | Classified


def attributions(
    performance: Performance,
    sound_index: dict[SoundId, int],
    occurrence_index: dict[OccurrenceId, int],
) -> tuple[Attribution, ...]:
    out: list[Attribution] = []
    for edge in performance.attributions:
        by = occurrence_index.get(edge.by) if edge.by is not None else None
        match edge:
            case Hosts(slots=slots, aspect=aspect, sound=sound):
                out.append(Hosted(slots, aspect, sound_index[sound], by))
            case Inserted(anchor=anchor, aspect=aspect, sound=sound):
                out.append(Insertion(anchor, aspect, sound_index[sound], by))
            case MergedInto(slots=slots, aspect=aspect, sound=sound):
                out.append(Merged(slots, aspect, sound_index[sound], by))
            case Silent(slots=slots, aspect=aspect):
                out.append(Silenced(slots, aspect, by))
            case _:
                raise TypeError(f"unmapped attribution edge {type(edge).__name__}")
    return tuple(out)


def modifiers(
    performance: Performance,
    sound_index: dict[SoundId, int],
    occurrence_index: dict[OccurrenceId, int],
) -> tuple[Modifier, ...]:
    out: list[Modifier] = []
    for edge in performance.modifiers:
        by = occurrence_index[edge.by]
        match edge:
            case Recolours(sound=sound):
                out.append(Recoloured(sound_index[sound], by))
            case SetsLength(sound=sound, length=length):
                out.append(Relengthened(sound_index[sound], by, length))
            case Classifies(sound=sound):
                out.append(Classified(sound_index[sound], by))
            case _:
                raise TypeError(f"unmapped modifier edge {type(edge).__name__}")
    return tuple(out)


__all__ = [
    "Attribution",
    "Classified",
    "Hosted",
    "Insertion",
    "Merged",
    "Modifier",
    "Recoloured",
    "Relengthened",
    "Silenced",
    "attributions",
    "modifiers",
]
