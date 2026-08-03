"""Silah, and the polysemy of the small madd letters.

Ambiguous in both scripts: the vowel is a silah when it belongs to the
pronoun haa; anywhere else the mark is an ordinary long vowel.
"""
from __future__ import annotations

from ...model.canon import CanonLetter, Nucleus, Quality
from ...model.inscription import SlotFact
from .vocabulary import Context, Outcome, Sets, register


@register("silah_waw")
def silah_waw(context: Context) -> Outcome:
    return _silah_or_long(context, Quality.U)


@register("silah_ya")
def silah_ya(context: Context) -> Outcome:
    return _silah_or_long(context, Quality.I)


def _silah_or_long(context: Context, quality: Quality) -> Outcome:
    if _is_pronoun_haa(context):
        return Sets(SlotFact.NUCLEUS, Nucleus.silah(quality))
    return Sets(SlotFact.NUCLEUS, Nucleus.long(quality))


def _is_pronoun_haa(context: Context) -> bool:
    return context.cluster.letter is CanonLetter.HEH and context.word_final


def carries_silah(context: Context) -> bool:
    """The same question asked of the letter that carries the vowel rather
    than of the haa: a script that writes the waw out reaches here instead."""
    return (
        context.cluster.omitted
        and context.previous_letter is CanonLetter.HEH
        and context.word_final
    )
