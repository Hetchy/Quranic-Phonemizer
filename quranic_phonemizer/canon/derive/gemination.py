"""The shadda: canonical gemination, or a witness to an assimilation.

A shadda whose preceding sound is silent attests an assimilation; otherwise
it is `Onset.GEMINATE`. Decided by the sound, never by glyph position.
"""
from __future__ import annotations

from ...model.canon import NucleusKind, Onset
from ...model.inscription import SlotFact
from .vocabulary import Attests, Context, Outcome, Sets, register


@register("gemination")
def gemination(context: Context) -> Outcome:
    if _preceded_by_silence(context):
        return Attests()
    return Sets(SlotFact.ONSET, Onset.GEMINATE)


def _preceded_by_silence(context: Context) -> bool:
    if context.word_initial:
        # A word-initial shadda's helping vowel is elided in wasl, so the
        # preceding sound is silent even though it is not canonically absent.
        return True
    previous = context.previous_nucleus
    return previous is not None and previous.kind is NucleusKind.SILENT
