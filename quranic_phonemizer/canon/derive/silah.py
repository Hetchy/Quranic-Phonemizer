"""Silah, and the polysemy of the small yaa mark.

Ambiguous in both scripts: the silah vowel belongs to the pronoun haa;
anywhere else the mark is an ordinary long vowel.
"""
from __future__ import annotations

from ...model.canon import CanonLetter, Long, Quality, Silah
from ...model.inscription import SlotFact
from . import Context, Outcome, Sets, Shows, Target, register


@register("silah_waw", requires=("shadda",))
def silah_waw(context: Context) -> Outcome:
    """The waw side is unambiguous, but resolved the same way as `silah_ya`
    so one rule covers both."""
    return _silah_or_long(context, Quality.U)


@register("silah_ya", requires=("shadda",))
def silah_ya(context: Context) -> Outcome:
    return _silah_or_long(context, Quality.I)


def _silah_or_long(context: Context, quality: Quality) -> Outcome:
    if context.cluster.has("shadda"):
        # A doubled yaa is a consonant with its own vowel; the small mark
        # shows the reading rather than supplying a nucleus, and folding it
        # to a long vowel would lose the gemination the script wrote.
        return Shows(Target.HERE)
    if _is_pronoun_haa(context):
        return Sets(SlotFact.NUCLEUS, Silah(quality))
    return Sets(SlotFact.NUCLEUS, Long(quality))


def _is_pronoun_haa(context: Context) -> bool:
    return context.cluster.letter is CanonLetter.HEH and context.word_final
