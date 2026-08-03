"""The Performance layer: sounds, and the one relation that produces them.

No grapheme field and no script field anywhere below: a rule that wants
to inspect a glyph has nowhere to look.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

from .address import (
    BoundaryPlan,
    OccurrenceId,
    Riwayah,
    SlotId,
    SoundId,
    VariantSelection,
)
from .canon import CanonLetter, Quality, Rule


class Aspect(StrEnum):
    """Exactly two members, because a `Slot` is definitionally an onset plus a
    nucleus. A third would mean the slot gained a third field."""

    CONSONANT = "consonant"
    VOWEL = "vowel"


class Side(StrEnum):
    BEFORE = "before"
    AFTER = "after"


class NasalPlace(StrEnum):
    """A place of articulation, not a rule name. The realization khilaf is
    resolved in `rules/`, never in `render/`."""

    BILABIAL = "bilabial"
    ASSIMILATED = "assimilated"


class ReleaseKind(StrEnum):
    QALQALA = "qalqala"


@dataclass(frozen=True, slots=True)
class Consonant:
    letter: CanonLetter
    geminate: bool = False
    emphatic: bool = False
    nasal: bool = False


@dataclass(frozen=True, slots=True)
class Vowel:
    quality: Quality
    long: bool = False
    emphatic: bool = False


@dataclass(frozen=True, slots=True)
class Nasal:
    place: NasalPlace
    emphatic: bool = False


@dataclass(frozen=True, slots=True)
class Release:
    kind: ReleaseKind


Sound: TypeAlias = Consonant | Vowel | Nasal | Release


@dataclass(frozen=True, slots=True)
class Participants:
    """Family-specific canonical participants. Never a free-form dict."""

    slots: tuple[SlotId, ...] = ()


@dataclass(frozen=True, slots=True)
class Occurrence:
    id: OccurrenceId
    rule: Rule
    parts: Participants


@dataclass(frozen=True, slots=True)
class Hosts:
    """Ordinary realization. `len(slots) > 1` is joint ownership.

    `by` is `None` where the Score's own default fills the sound: no rule
    claimed it, so there is nothing to cite.
    """

    slots: tuple[SlotId, ...]
    aspect: Aspect
    sound: SoundId
    by: OccurrenceId | None


@dataclass(frozen=True, slots=True)
class Inserted:
    """No slot owns the sound; `anchor` places it. The 3:1 iltiqa fatha is
    the only genuinely slot-less sound in the design."""

    anchor: tuple[SlotId, Side]
    aspect: Aspect
    sound: SoundId
    by: OccurrenceId | None


@dataclass(frozen=True, slots=True)
class MergedInto:
    """The source half of a merger. The pair sharing a `SoundId` and an
    `OccurrenceId` *is* the merger; there is no `assimilated` flag."""

    slots: tuple[SlotId, ...]
    aspect: Aspect
    sound: SoundId
    by: OccurrenceId | None


@dataclass(frozen=True, slots=True)
class Silent:
    """Deletion with a reason. The reason is `by.rule`."""

    slots: tuple[SlotId, ...]
    aspect: Aspect
    by: OccurrenceId | None


Attribution: TypeAlias = Hosts | Inserted | MergedInto | Silent


@dataclass(frozen=True, slots=True)
class Performance:
    """One traversal. Carries the selection and plan that produced it, because
    a `SoundId` is meaningless without them."""

    riwayah: Riwayah
    sounds: tuple[tuple[SoundId, Sound], ...]
    attributions: tuple[Attribution, ...]
    occurrences: tuple[Occurrence, ...]
    selection: VariantSelection
    boundaries: BoundaryPlan
