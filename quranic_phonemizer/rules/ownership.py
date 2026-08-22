"""Which family owns a slot, stated once instead of guarded per rule.

Ownership is a precondition on slot shape, not a partition of trigger
letters -- lam, meem and noon each trigger more than one family.
"""
from __future__ import annotations

from ..model.canon import Onset, Slot, SlotOrigin
from ..model.performance import Aspect


def is_quiescent(slot: Slot | None) -> bool:
    """A quiescent slot has a silent nucleus; a geminate one belongs to
    the ghunnah rule instead."""
    return (
        slot is not None
        and slot.nucleus.is_silent
        and slot.onset is not Onset.GEMINATE
    )


def is_effectively_quiescent(near, plan, at, boundaries) -> bool:
    """Canonical sukun or a word-final vowel removed by complete waqf."""
    slot, word = near.slot(at), near.word_of(at)
    if is_quiescent(slot):
        return True
    if slot is None or word is None or slot.onset is Onset.GEMINATE:
        return False
    if not boundaries.stopped_on(word):
        return False
    lexical = tuple(
        candidate for candidate in near.score.words[word].slots
        if candidate.origin is not SlotOrigin.NUNATION
    )
    return (
        bool(lexical)
        and lexical[-1].id == at
        and plan.merged_away(at, Aspect.VOWEL)
    )
