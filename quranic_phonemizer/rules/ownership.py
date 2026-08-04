"""Which family owns a slot, stated once instead of guarded per rule.

Ownership is a precondition on slot shape, not a partition of trigger
letters -- lam, meem and noon each trigger more than one family.
"""
from __future__ import annotations

from ..model.canon import Onset, Slot


def is_quiescent(slot: Slot | None) -> bool:
    """A quiescent slot has a silent nucleus; a geminate one belongs to
    the ghunnah rule instead."""
    return (
        slot is not None
        and slot.nucleus.is_silent
        and slot.onset is not Onset.GEMINATE
    )
