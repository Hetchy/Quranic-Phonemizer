"""The mutable slot under construction, and where a decided fact is written.

Shared by `build.py`'s per-cluster drafting and `passes.py`'s verse-level passes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count

from ..model.canon import (
    Annotation,
    CanonLetter,
    Nucleus,
    Onset,
    SlotOrigin,
)
from ..model.inscription import VOWEL_FACTS, SlotFact
from . import derive
from .derive import Absent, Shows, Target

#: Never serialised and never compared across builds -- only a key while one
#: verse is being drafted, so a process-wide counter is enough.
_uid = count()


@dataclass(slots=True)
class _Draft:
    """One slot under construction, plus who decided each of its facts."""

    letter: CanonLetter
    onset: Onset = Onset.PLAIN
    nucleus: Nucleus = field(default_factory=Nucleus.silent)
    origin: SlotOrigin = SlotOrigin.WRITTEN
    cluster: int = -1
    onset_declared: bool = False
    nucleus_declared: bool = False
    sakt_after: bool = False
    """A word-level fact carried on the word's final slot; `_assemble` lifts
    it onto the `ScoreWord`."""

    annotations: frozenset[Annotation] = frozenset()
    spelling_run: int | None = None
    spelled_letter: CanonLetter | None = None

    uid: int = field(default_factory=lambda: next(_uid))
    """Identity that survives being moved, split or dropped, which `id()` did
    not. Also what makes `list.remove` and `list.index` mean this draft."""


def fact_of(draft, fact: SlotFact):
    """What a draft currently says about one fact. The mirror of `set_fact`."""
    match fact:
        case SlotFact.LETTER:
            return draft.letter
        case SlotFact.ONSET:
            return draft.onset
        case _ if fact in VOWEL_FACTS:
            return draft.nucleus
        case SlotFact.SAKT:
            return draft.sakt_after
        case SlotFact.TAJWEED_MARK:
            return draft.annotations
    return None


def set_fact(draft, drafts, fact: SlotFact, value, target: Target,
         scribe: Scribe | None = None, offset: int = -1) -> None:
    subject = draft if target is Target.HERE else (drafts[-1] if drafts else None)
    if subject is None:
        return
    if scribe is not None:
        scribe.evidence(offset, subject, fact)
    match fact:
        case SlotFact.LETTER:
            subject.letter = value
        case SlotFact.ONSET:
            subject.onset, subject.onset_declared = value, True
        case _ if fact in VOWEL_FACTS:
            subject.nucleus, subject.nucleus_declared = value, True
        case SlotFact.SAKT:
            subject.sakt_after = bool(value)
        case SlotFact.TAJWEED_MARK:
            subject.annotations = subject.annotations | {value}


def letter_of(rows, cluster) -> CanonLetter | None:
    for row in rows:
        if row.fact is SlotFact.LETTER and row.value is not None:
            return row.value
    return cluster.letter


def stray_letter_offsets(rows, used_offset: int) -> frozenset[int]:
    """Letter-fact rows on this cluster whose offset went unused: a second
    mark riding the same letter, like the sakt sites' small seen."""
    return frozenset(
        row.offset for row in rows
        if row.fact is SlotFact.LETTER and row.value is not None
        and row.offset != used_offset
    )


def decorated_offsets(rows, context, own: int, evidenced) -> list[int]:
    """Every offset a cluster written but not a slot decorates: its own, a
    stray letter mark, and a nucleus row supplying no fact -- the dagger of
    `مَجْر۪ىٰهَا`, whose length the imala mark had already given."""
    shown = {
        row.offset if row.offset >= 0 else context.cluster.offset
        for row in rows
        if row.fact in VOWEL_FACTS and row.value is None
        and isinstance(derive.resolve(row.derivation, context), (Shows, Absent))
    }
    return sorted(
        {own, *stray_letter_offsets(rows, own)} | (shown - set(evidenced))
    )


def letter_offsets_of(rows, cluster) -> tuple[int, frozenset[int]]:
    """The offset that carries the cluster's letter, and every other offset
    also written as part of it -- a seat's own bare position, or a stray
    mark -- neither reached by any other pass."""
    letter_rows = [
        row for row in rows
        if row.fact is SlotFact.LETTER and row.value is not None
    ]
    winner = letter_rows[0].offset if letter_rows else cluster.offset
    extra = stray_letter_offsets(rows, winner) | ({cluster.offset} - {winner})
    return winner, extra


def nucleus_fact(nucleus: Nucleus) -> SlotFact:
    """Which vowel fact a glyph asserting a whole nucleus supplies.

    Absent when silent; otherwise quality, since stating shape and quality
    together is not a length-only claim."""
    return SlotFact.VOWEL_ABSENCE if nucleus.is_silent else SlotFact.VOWEL_QUALITY
