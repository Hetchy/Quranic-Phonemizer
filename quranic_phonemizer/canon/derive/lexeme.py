"""Lexical facts: the name of God, and the wāw that is written but never said.

Both are places where one script writes what the other leaves to knowledge, so
both are derivations rather than script conventions. Neither may consult a
`Script` — a canonical field that silently encodes which script you happened to
read is the failure this design keeps catching (R9's seven alifs, `SlotOrigin`,
`ScoreWord.advice`).
"""
from __future__ import annotations

from ...model.canon import CanonLetter, Long, NucleusKind, Quality
from . import Context, register  # noqa: F401  (registry import kept explicit)

ALLAH_TAIL = (CanonLetter.LAM, CanonLetter.HEH)


def allah_long_a(letters: list[CanonLetter], nuclei: list) -> list[int]:
    """Indices whose nucleus must become `Long(A)`.

    Uthmani writes `ٱللَّهِ` with no ālif at all; IndoPak writes the dagger.
    The lexeme is the shared fact both are spelling. 2,704 words, 12 skeletons.
    """
    out: list[int] = []
    for i, letter in enumerate(letters):
        if letter is not CanonLetter.LAM or i == 0 or i + 1 >= len(letters):
            continue
        if letters[i + 1] is not CanonLetter.HEH:
            continue
        if letters[i - 1] not in (CanonLetter.LAM, CanonLetter.HAMZA):
            continue
        nucleus = nuclei[i]
        if nucleus.kind is NucleusKind.SHORT and nucleus.quality is Quality.A:
            out.append(i)
    return out


def relengthened(nucleus) -> Long:
    del nucleus
    return Long(Quality.A)


def otiose_waw(context: Context) -> bool:
    """`أُو۟لَـٰٓئِكَ`, `أُو۟لِى` — a wāw in the rasm that never sounds.

    Uthmani marks it with `۟`; IndoPak writes nothing, so without this the two
    disagree at ~240 words. One shape covers them all: a prosthetic-looking
    hamza with damma, a bare wāw, then a lām or rāʾ.
    """
    start = context.word_bounds[0]
    for i in range(start, min(start + 3, context.index)):
        head = context.clusters[i]
        if head.letter not in (CanonLetter.ALIF, CanonLetter.HAMZA):
            break
        if not head.has("damma"):
            break
        if i + 1 != context.index:
            continue
        following = context.ahead()
        return (
            context.cluster.letter is CanonLetter.WAW
            and not context.cluster.marks
            and following is not None
            and following.letter in (CanonLetter.LAM, CanonLetter.RA)
        )
    return False


def otiose_alif(context: Context) -> bool:
    """The ālif of the plural wāw — `قَالُوا۟` — and the ālif no vowel can carry.

    Uthmani marks 3,722 of them with `۟`; IndoPak marks 26. Word-finally after
    a wāw or a short *u*, or anywhere after a short vowel that is not *a*, a
    bare ālif is rasm.
    """
    cluster = context.cluster
    if cluster.letter is not CanonLetter.ALIF or cluster.marks:
        return False
    if context.word_initial:
        return False   # the previous nucleus belongs to another word
    previous = context.previous_nucleus
    if previous is None:
        return False
    if context.word_final and (
        context.previous_letter is CanonLetter.WAW
        or (previous.kind is NucleusKind.SHORT and previous.quality is Quality.U)
    ):
        return True
    return (
        previous.kind is NucleusKind.SHORT and previous.quality is not Quality.A
    )
