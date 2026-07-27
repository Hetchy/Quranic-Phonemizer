"""Tanween is two slots: one grapheme evidences facts on both.

A `Short(q)` nucleus lands on the base slot; `NOON` plus a silent nucleus
lands on a new slot, so tanween and noon-sakinah share one rule.
"""
from __future__ import annotations

from ...model.canon import CanonLetter, Onset, Quality, Short, Silent
from ...model.inscription import SlotFact
from . import Absent, AddsSlot, Context, Outcome, Sets, Target, register

_QUALITY = {"fathatan": Quality.A, "dammatan": Quality.U, "kasratan": Quality.I}


def _nunate(quality: Quality) -> AddsSlot:
    return AddsSlot(
        fact=SlotFact.NUCLEUS,
        value=Short(quality),
        letter=CanonLetter.NOON,
        onset=Onset.PLAIN,
        nucleus=Silent(),
    )


@register("tanween", requires=("fathatan", "dammatan", "kasratan"))
def tanween(context: Context) -> Outcome:
    for role, quality in _QUALITY.items():
        if context.cluster.has(role):
            return _nunate(quality)
    raise ValueError(
        f"cluster {context.index} was routed to the tanwīn derivation but "
        f"carries no tanwīn mark: {[m.role for m in context.cluster.marks]}"
    )


@register("iwad_carrier")
def iwad_carrier(context: Context) -> Outcome:
    """The alif written after a fathatan.

    Not a fourth slot and not a length carrier in wasl; at waqf it is the
    iwad, lengthening the base while silencing the noon slot.
    """
    return Absent(shows=Target.PREVIOUS)


#: The role an inventory gives IndoPak's cross-word noon-kasra mark.
#: `canon.build` looks for it by name to know whether the previous word
#: ends in a tanween the script drew on this one.
CROSS_WORD_ROLE = "cross_word_noon"


# Deliberately declares no required role. `cross_word_noon` is a convention
# exactly one script has, so requiring it would reject Uthmani for not writing
# something Uthmani does not write. That it is readable from shared code at all
# is the deeper problem: `build._split_tanween_words` greps the role name, so a
# script fact decides a canonical question. The fix is for this derivation to
# return the slot itself rather than for the builder to look for the mark.
@register("cross_word_noon")
def cross_word_noon(context: Context) -> Outcome:
    """IndoPak's noon-kasra mark drawn on the following word.

    IndoPak splits the tanween across the boundary: the vowel stays on
    word n with the mark dropped, and the noon is depicted on word n+1.
    """
    return Absent(shows=Target.PREVIOUS)
