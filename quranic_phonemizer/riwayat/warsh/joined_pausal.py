"""Selected-script projection for joined-only and pausal source shapes."""
from __future__ import annotations

import unicodedata

from ...canon.passes import word_spans
from ...model.canon import CanonLetter, Nucleus, Onset, Quality
from ...model.inscription import SlotFact


_STOP = frozenset("ۖۗۘۙۚۛۜ۩")
_YAA_TAIL = _STOP | {"ٓ", "َ"}
_PLURAL_HOSTS = frozenset({CanonLetter.KAF, CanonLetter.HEH, CanonLetter.TA})
_ANA_FORMS = frozenset({"أَنَا", "اَنَا", "وَأَنَا"})


def _word_text(reading, word: int) -> str:
    offsets = {
        cluster.offset for cluster in reading.clusters if cluster.word == word
    }
    offsets.update(
        mark.offset
        for cluster in reading.clusters if cluster.word == word
        for mark in cluster.marks
    )
    by_offset = {glyph.id.offset: glyph.char for glyph in reading.graphemes}
    return "".join(by_offset[offset] for offset in sorted(offsets))


def _prior_letter(text: str, offset: int) -> str | None:
    return next(
        (
            char for char in reversed(text[:offset])
            if unicodedata.category(char).startswith("L") and char != "ـ"
        ),
        None,
    )


def yaa_zawaid_shape(text: str) -> str | None:
    """The reviewed terminal small-yaa family and its canonical shape."""
    try:
        offset = text.index("ۦ")
    except ValueError:
        return None
    if _prior_letter(text, offset) in {"ه", "ي"}:
        return None
    tail = text[offset + 1:]
    if not all(char in _YAA_TAIL for char in tail):
        return None
    return "glide" if "َ" in tail else "long"


def _plural_meem(span) -> bool:
    return (
        len(span) >= 2
        and span[-1].letter is CanonLetter.MEEM
        and span[-2].letter in _PLURAL_HOSTS
    )


def _before_wasl(spans, index: int) -> bool:
    return (
        index + 1 < len(spans)
        and bool(spans[index + 1])
        and spans[index + 1][0].onset is Onset.WASL
    )


def _demote_boundary_damma(span, scribe) -> None:
    mim = span[-1]
    offsets = scribe.evidence_offsets(mim, SlotFact.VOWEL_QUALITY)
    for offset in offsets:
        scribe.withdraw_evidence(offset, mim, SlotFact.VOWEL_QUALITY)
        scribe.attestation(offset, mim)


def _pausal_alif(text: str) -> bool:
    plain = text.rstrip("".join(_STOP))
    return plain == "لَّٰكِنَّا" or plain in _ANA_FORMS


def supply_joined_pausal(reading, drafts, lexicon, scribe, selection) -> None:
    """Project only reviewed King Fahd sequences into neutral model shapes."""
    del lexicon, selection
    if scribe is None:
        return
    spans = word_spans(reading, drafts)
    for word, span in enumerate(spans):
        if not span:
            continue
        text = _word_text(reading, word)
        if "مُۥٓ" in text and _plural_meem(span):
            span[-1].nucleus = Nucleus.joined_only_long(Quality.U)
        elif _plural_meem(span) and _before_wasl(spans, word):
            _demote_boundary_damma(span, scribe)

        shape = yaa_zawaid_shape(text)
        if shape == "long":
            span[-1].nucleus = Nucleus.joined_only_long(Quality.I)
        elif shape == "glide":
            span[-1].onset = Onset.GLIDE

        if _pausal_alif(text):
            span[-1].nucleus = Nucleus.pausal_long(Quality.A)


__all__ = ["supply_joined_pausal", "yaa_zawaid_shape"]
