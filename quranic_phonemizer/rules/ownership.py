"""Which family owns a slot, stated once instead of guarded per rule.

Ownership is a precondition on slot shape, not a partition of trigger
letters -- lam, meem and noon each trigger more than one family.
"""
from __future__ import annotations

from ..model.canon import Onset, Slot
from ..model.performance import Aspect


def is_quiescent(slot: Slot | None) -> bool:
    """A quiescent slot has a silent nucleus; a geminate one belongs to
    the ghunnah rule instead."""
    return (
        slot is not None
        and slot.nucleus.is_silent
        and slot.onset is not Onset.GEMINATE
    )


def is_performed_quiescent(slot: Slot | None, plan, at) -> bool:
    """A sakin in the resolved reading, including a final vowel lost at waqf."""
    return (
        slot is not None
        and slot.onset is not Onset.GEMINATE
        and not plan.voweled(at)
        and not plan.merged_away(at, Aspect.CONSONANT)
        and (slot.nucleus.is_silent or plan.merged_away(at, Aspect.VOWEL))
    )
