"""The mutable slot under construction, and the one place a fact lands on it.

Both `canon/build.py` (per-cluster drafting) and `canon/passes.py` (verse-level
passes) write to a draft, so neither can own it. Extracted when the split made
the dependency explicit rather than because a third caller appeared.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..model.canon import CanonLetter, Nucleus, Onset, Silent, SlotOrigin
from ..model.inscription import SlotFact
from .derive import Target


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
    """A word-level fact carried on the slot that ends the word; `_assemble`
    lifts it onto the `ScoreWord`. Before this, `SlotFact.SAKT` reached `_set`
    and fell through a `match` with no case for it, so 18:1 -- one of Hafs'
    four canonical sakt sites -- never reached the Score."""


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
