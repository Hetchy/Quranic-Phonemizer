"""Lexical facts: the name of God, and the waw that is written but never said.

Both are places where one script writes what the other leaves to knowledge,
so both are derivations, never a `Script` consulted directly.
"""
from __future__ import annotations

from ...model.canon import CanonLetter, Long, NucleusKind, Onset, Quality
from . import Context, register  # noqa: F401  (registry import kept explicit)

#: The name is a lam before a haa, and the lam before it or the wasl hamza.
ALLAH_TAIL = (CanonLetter.LAM, CanonLetter.HEH)
ALLAH_HEAD = (CanonLetter.LAM, CanonLetter.HAMZA)


def divine_name(letters: list[CanonLetter], nuclei: list, onsets: list) -> list[int]:
    """Indices of the lam of the divine name, from the letters alone.

    Script-independent by construction: one script writes the alif and the
    other does not, so keying on the nucleus would tag only one of them.
    """
    out: list[int] = []
    for i, letter in enumerate(letters):
        if letter is not ALLAH_TAIL[0] or i == 0 or i + 1 >= len(letters):
            continue
        if letters[i + 1] is not ALLAH_TAIL[1]:
            continue
        if letters[i - 1] not in ALLAH_HEAD:
            continue
        if getattr(nuclei[i], "quality", None) is not Quality.A:
            continue
        doubled = onsets[i] is Onset.GEMINATE or (
            letters[i - 1] is CanonLetter.LAM
            and nuclei[i - 1].kind is NucleusKind.SILENT
        )
        if not doubled:
            continue
        out.append(i)
    return out


def allah_long_a(letters: list[CanonLetter], nuclei: list, onsets: list) -> list[int]:
    """Of those, the ones whose nucleus must still become `Long(A)`.

    Uthmani writes `ٱللَّهِ` with no alif at all; IndoPak writes the dagger.
    """
    return [
        i
        for i in divine_name(letters, nuclei, onsets)
        if nuclei[i].kind is NucleusKind.SHORT
        and nuclei[i].quality is Quality.A
    ]


def relengthened(nucleus) -> Long:
    del nucleus
    return Long(Quality.A)


def otiose_waw(context: Context) -> bool:
    """`أُو۟لَـٰٓئِكَ`, `أُو۟لِى` - a waw in the rasm that never sounds.

    Uthmani marks it with `۟`; IndoPak writes nothing. One shape covers
    both: a hamza with damma, a bare waw, then a lam or raa.
    """
    if context.index == context.word_bounds[0]:
        return False
    head = context.clusters[context.index - 1]
    if head.letter not in (CanonLetter.ALIF, CanonLetter.HAMZA):
        return False
    if not head.has("damma"):
        return False
    following = context.ahead()
    return (
        context.cluster.letter is CanonLetter.WAW
        and not context.cluster.has("fatha", "damma", "kasra", "shadda")
        and following is not None
        and following.letter in (CanonLetter.LAM, CanonLetter.RA)
    )


#: The two letters that carry a leen with a preceding fatha.
LEEN_CARRIERS = (CanonLetter.YA, CanonLetter.WAW)


def alif_in_leen(context: Context) -> bool:
    """`تَا۟يْـَٔسُوا۟` - a bare alif inside a leen, which needs neither a
    carrier nor a prosthetic hamza. Uthmani marks it, IndoPak does not."""
    cluster = context.cluster
    following = context.ahead()
    return (
        cluster.letter is CanonLetter.ALIF
        and not cluster.has("fatha", "damma", "kasra", "shadda")
        and not context.word_initial
        and context.clusters[context.index - 1].has("fatha")
        and following is not None
        and following.letter in LEEN_CARRIERS
        and following.has("sukun")
    )


def otiose_alif(context: Context) -> bool:
    """The alif of the plural waw (`قَالُوا۟`), and the alif no vowel can carry.

    Word-finally after a waw or a short u, or anywhere after a short vowel
    that is not a, a bare alif is rasm.
    """
    cluster = context.cluster
    if cluster.letter is not CanonLetter.ALIF or cluster.marks:
        return False
    if context.word_initial:
        return False   # the previous nucleus belongs to another word
    if alif_in_leen(context):
        return True
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
