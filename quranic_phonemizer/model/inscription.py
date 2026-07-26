"""The Inscription layer: what a script wrote, and what each mark is doing.

`Spelling` points *up* from a grapheme into the Score. Nothing points down at
a grapheme (ADR-001 §1) — which is why deleting this layer breaks only
source-text projections.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

from .address import GraphemeId, Location, Script, SlotId, VerseRef
from .canon import RuleFamily


class GraphemeClass(StrEnum):
    """What the grapheme *is*. `Spelling` says what it *does*; the two axes
    are independent and a projection's `role` reads the second (ADR-007 §6.1)."""

    BASE = "base"
    HARAKA = "haraka"
    TANWEEN = "tanween"
    SHADDA = "shadda"
    LENGTH_CARRIER = "length_carrier"
    SMALL_VOWEL = "small_vowel"
    MADD_SIGN = "madd_sign"
    SILENCE_SIGN = "silence_sign"
    ANNOTATION = "annotation"
    ADVICE = "advice"
    STRUCTURAL = "structural"


@dataclass(frozen=True, slots=True)
class Grapheme:
    id: GraphemeId
    char: str
    cls: GraphemeClass
    index: int
    """Ordinal within its word. The frozen baseline's `source_letter_index`."""


class SlotFact(StrEnum):
    LETTER = "letter"
    ONSET = "onset"
    NUCLEUS = "nucleus"
    SAKT = "sakt"


@dataclass(frozen=True, slots=True)
class Evidences:
    """This grapheme supplies or asserts a canonical fact of a named slot."""

    grapheme: GraphemeId
    slot: SlotId
    fact: SlotFact


@dataclass(frozen=True, slots=True)
class Attests:
    """This grapheme witnesses a *performance* outcome at an anchor slot.

    Names a `RuleFamily`, never a `Rule`: deciding which of seven idghām
    members a shadda attests is tajweed classification and does not belong in
    a script adapter (ADR-003 §4.1).
    """

    grapheme: GraphemeId
    family: RuleFamily
    anchor: SlotId


@dataclass(frozen=True, slots=True)
class Decorates:
    """Supplies no canonical fact, but is bound to the slot it shows.

    The slot is mandatory. Its predecessor `Inert` asserted two things at
    once — *supplies no fact* and *shows nothing* — and the maddah is the
    first without being the second: 5,044 cells in the frozen baseline give it
    a long vowel and a madd tag (ADR-003 §4.0).
    """

    grapheme: GraphemeId
    slot: SlotId


@dataclass(frozen=True, slots=True)
class Structural:
    """Not part of any word: space, sajdah, hizb, verse marker, tatweel, and
    the stop-sign scalars, which reach `StopAdvice` through the inventory."""

    grapheme: GraphemeId


Spelling: TypeAlias = Evidences | Attests | Decorates | Structural


class StopAdvice(StrEnum):
    """A mushaf convention, legitimately script-scoped. The *class* vocabulary
    is shared; the mapping from scalars into it is per (riwayah, script)."""

    PREFERRED_CONTINUE = "preferred_continue"
    PREFERRED_STOP = "preferred_stop"
    OPTIONAL_STOP = "optional_stop"
    COMPULSORY_STOP = "compulsory_stop"
    PROHIBITED_STOP = "prohibited_stop"
    EITHER_STOP = "either_stop"
    PERMITTED_STOP = "permitted_stop"
    """A stop is allowed, class unspecified. IndoPak's `ؕ` absorbs three
    Uthmani classes; mapping it to any one would invent a distinction the
    source does not make (ADR-003 §5)."""


@dataclass(frozen=True, slots=True)
class Inscription:
    """One verse as one script wrote it."""

    verse: VerseRef
    script: Script
    words: tuple[Location, ...]
    graphemes: tuple[Grapheme, ...]
    spellings: tuple[Spelling, ...]
    advice: tuple[StopAdvice | None, ...]
    """One per word, in `words` order."""
