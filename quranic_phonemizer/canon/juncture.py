"""Repairs a word owes its neighbour, made while the drafts are still open.

One script may draw a fact on the word after the one it belongs to, so a
verse-scoped pass is not enough and these take a word of right context.
"""
from __future__ import annotations

from ..model.canon import (
    CanonLetter,
    Nucleus,
    Onset,
    Quality,
    SlotOrigin,
)
from ..model.inscription import SlotFact
from ..orthography.adapter import Reading
from .derive import tanween
from .draft import _Draft, nucleus_fact
from .passes import word_of


def apply_cross_word_noon(reading, drafts, right_context, scribe) -> None:
    """Give word n the noon slot that word n+1 is carrying for it."""
    marked = _split_tanween_words(reading)
    if right_context is not None and 0 in _split_tanween_words(right_context):
        marked.add(len(reading.words))
    for word_index in sorted(marked):
        span = [d for d in drafts if word_of(reading, d) == word_index - 1]
        if word_index and span:
            _restore_noon(reading, drafts, span[-1], word_index, scribe)


def _restore_noon(reading, drafts, last, word_index: int, scribe) -> None:
    if last.letter is CanonLetter.NOON and last.nucleus.is_silent:
        return   # already a tanween noon; nothing was split
    last.nucleus = Nucleus.short(last.nucleus.quality or Quality.A)
    noon = _Draft(
        letter=CanonLetter.NOON,
        onset=Onset.PLAIN,
        nucleus=Nucleus.silent(),
        cluster=last.cluster,
        origin=SlotOrigin.NUNATION,
    )
    drafts.insert(drafts.index(last) + 1, noon)
    # The noon is written on the next word, so the grapheme that reaches it
    # is that word's mark, not the donor's.
    offset = _split_tanween_offset(reading, word_index)
    if offset >= 0:
        scribe.evidence(offset, noon, SlotFact.LETTER)
        scribe.evidence(offset, noon, nucleus_fact(noon.nucleus))


def _split_tanween_words(reading: Reading) -> set[int]:
    """Words whose predecessor carries a tanween this script drew here.

    IndoPak splits it across the boundary: the vowel stays on word n, and
    the noon-plus-kasra is drawn as a mark on word n+1.
    """
    return {
        cluster.word
        for cluster in reading.clusters
        if cluster.has(tanween.CROSS_WORD_ROLE)
    }


def _split_tanween_offset(reading: Reading, word: int) -> int:
    """Where the mark that supplies the noon is actually written."""
    for cluster in reading.clusters:
        if cluster.word != word:
            continue
        mark = cluster.mark(tanween.CROSS_WORD_ROLE)
        if mark is not None:
            return mark.offset
    return -1
