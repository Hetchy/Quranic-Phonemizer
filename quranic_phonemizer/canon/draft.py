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
    Silent,
    SlotOrigin,
)
from ..model.inscription import SlotFact
from .derive import Target

#: Never serialised and never compared across builds -- only a key while one
#: verse is being drafted, so a process-wide counter is enough.
_uid = count()


@dataclass(slots=True)
class _Draft:
    """One slot under construction, plus who decided each of its facts."""

    letter: CanonLetter
    onset: Onset = Onset.PLAIN
    nucleus: Nucleus = field(default_factory=Silent)
    origin: SlotOrigin = SlotOrigin.WRITTEN
    cluster: int = -1
    onset_declared: bool = False
    nucleus_declared: bool = False
    sakt_after: bool = False
    """A word-level fact carried on the word's final slot; `_assemble` lifts
    it onto the `ScoreWord`."""

    annotations: frozenset[Annotation] = frozenset()

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
        case SlotFact.NUCLEUS:
            return draft.nucleus
        case SlotFact.SAKT:
            return draft.sakt_after
        case SlotFact.ANNOTATION:
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
        case SlotFact.NUCLEUS:
            subject.nucleus, subject.nucleus_declared = value, True
        case SlotFact.SAKT:
            subject.sakt_after = bool(value)
        case SlotFact.ANNOTATION:
            subject.annotations = subject.annotations | {value}
