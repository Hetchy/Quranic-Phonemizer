"""Silah, and the polysemy of the small madd letters.

Ambiguous in both scripts: the vowel is a silah when it belongs to the
pronoun haa; anywhere else the mark is an ordinary long vowel.
"""
from __future__ import annotations

from ...model.canon import CanonLetter, Long, Quality, Silah
from ...model.inscription import SlotFact
from . import Context, Outcome, Sets, register


@register("silah_waw")
def silah_waw(context: Context) -> Outcome:
    return _silah_or_long(context, Quality.U)


@register("silah_ya")
def silah_ya(context: Context) -> Outcome:
    return _silah_or_long(context, Quality.I)


def _silah_or_long(context: Context, quality: Quality) -> Outcome:
    if _is_pronoun_haa(context):
        return Sets(SlotFact.NUCLEUS, Silah(quality))
    return Sets(SlotFact.NUCLEUS, Long(quality))


def _is_pronoun_haa(context: Context) -> bool:
    return context.cluster.letter is CanonLetter.HEH and context.word_final
