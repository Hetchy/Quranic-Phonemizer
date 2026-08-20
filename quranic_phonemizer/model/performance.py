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


class Degree(StrEnum):
    """A qalqala's three degrees. The letter it names lives in the rule that
    minted it; this is how hard the echo bounces."""

    SUGHRA = "sughra"
    KUBRA = "kubra"
    AKBAR = "akbar"


class Length(StrEnum):
    """A relength's target, published so `SetsLength` can name one."""

    SHORT = "short"
    LONG = "long"


@dataclass(frozen=True, slots=True)
class Consonant:
    letter: CanonLetter
    geminate: bool = False
    emphatic: bool = False
    ghunnah: bool = False
    eased: bool = False


@dataclass(frozen=True, slots=True)
class Vowel:
    quality: Quality
    long: bool = False
    emphatic: bool = False


@dataclass(frozen=True, slots=True)
class Release:
    degree: Degree


Sound: TypeAlias = Consonant | Vowel | Release


@dataclass(frozen=True, slots=True)
class Occurrence:
    """`context` is what the rule read without touching it and `boundary` the
    junction it resolved, keyed as a `BoundaryPlan` keys one. What it did to
    a unit beside its subjects is on the edges, not here."""

    id: OccurrenceId
    rule: Rule
    subjects: tuple[SlotId, ...]
    context: tuple[SlotId, ...] = ()
    boundary: int | None = None


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
    `OccurrenceId` *is* the merger, so `by` is mandatory here and optional
    on the edges a rule need not have caused."""

    slots: tuple[SlotId, ...]
    aspect: Aspect
    sound: SoundId
    by: OccurrenceId


@dataclass(frozen=True, slots=True)
class Silent:
    """Deletion with a reason. The reason is `by.rule`."""

    slots: tuple[SlotId, ...]
    aspect: Aspect
    by: OccurrenceId | None


Attribution: TypeAlias = Hosts | Inserted | MergedInto | Silent


@dataclass(frozen=True, slots=True)
class Recolours:
    """The edge a `Recolour` effect leaves once its feature is baked into
    an already-hosted sound."""

    sound: SoundId
    by: OccurrenceId


@dataclass(frozen=True, slots=True)
class SetsLength:
    """The edge a `Relength` effect leaves once its length is baked into
    an already-hosted vowel."""

    sound: SoundId
    by: OccurrenceId
    length: Length


@dataclass(frozen=True, slots=True)
class Classifies:
    """A rule that names what a sound already is, producing and changing
    nothing of its own."""

    sound: SoundId
    by: OccurrenceId


Modifier: TypeAlias = Recolours | SetsLength | Classifies


@dataclass(frozen=True, slots=True)
class Performance:
    """One traversal. Carries the selection and plan that produced it, because
    a `SoundId` is meaningless without them."""

    riwayah: Riwayah
    sounds: tuple[tuple[SoundId, Sound], ...]
    attributions: tuple[Attribution, ...]
    modifiers: tuple[Modifier, ...]
    occurrences: tuple[Occurrence, ...]
    selection: VariantSelection
    boundaries: BoundaryPlan


def effect_targets(
    performance: Performance,
) -> dict[OccurrenceId, tuple[SlotId, ...]]:
    """Per occurrence, the slots its own edges name apart from its subjects:
    a merger's host, a letter it silenced, a vowel it relengthened. A
    modifier names a sound, so it reaches the slot hosting that sound."""
    hosting: dict[SoundId, set[SlotId]] = {}
    for attribution in performance.attributions:
        if isinstance(attribution, Hosts):
            hosting.setdefault(attribution.sound, set()).update(attribution.slots)

    named: dict[OccurrenceId, set[SlotId]] = {}
    for attribution in performance.attributions:
        if attribution.by is not None:
            named.setdefault(attribution.by, set()).update(_named(attribution))
    for modifier in performance.modifiers:
        named.setdefault(modifier.by, set()).update(
            hosting.get(modifier.sound, ())
        )

    subjects = {
        occurrence.id: frozenset(occurrence.subjects)
        for occurrence in performance.occurrences
    }
    return {
        occurrence: tuple(sorted(slots - subjects.get(occurrence, frozenset())))
        for occurrence, slots in named.items()
    }


def _named(attribution: Attribution) -> tuple[SlotId, ...]:
    if isinstance(attribution, Inserted):
        return (attribution.anchor[0],)
    return attribution.slots
