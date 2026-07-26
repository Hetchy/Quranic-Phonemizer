"""Ṣilah, and the polysemy of the small yāʾ.

`Nucleus.Silah` is long in waṣl and absent at pause; `Onset.SILAH` is its
mirror on the other axis. Both are canonical, so neither needs a boundary rule
to exist — conditionality lives in the vocabulary (ADR-001 §3.6).

The mark is polysemous in **both** scripts, which the first draft missed. Equal
counts are not evidence of a 1:1 mapping: Uthmani `ۦ` ×956 against IndoPak `ٖ`
×993, the 956 shared plus 37 IndoPak-only, and at least three of those write an
ordinary long ī (11:41:6 `مَجْرٖىهَا`, 17:55:10 and 19:58:7 `النَّبِيّٖنَ`).
Uthmani's `ۧ` is the same story at ~38 of its 39 sites.

So the discriminator is canonical, not glyphic: the ṣilah vowel belongs to the
**pronoun hāʾ**. Anywhere else the mark writes a long vowel nobody spelled.
"""
from __future__ import annotations

from ...model.canon import CanonLetter, Long, Quality, Silah
from ...model.inscription import SlotFact
from . import Context, Outcome, Sets, register


@register("silah_waw")
def silah_waw(context: Context) -> Outcome:
    """The wāw side is a clean 1:1 — U+06E5 ×1,257 and U+0657 ×1,257 at the
    same 1,257 words — but it is resolved the same way, because a rule that
    holds for one side and not the other is the asymmetry this design exists
    to remove."""
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
