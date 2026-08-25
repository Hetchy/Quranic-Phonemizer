"""Reviewed naql spellings in the selected King Fahd Warsh script.

The source writes the transformed joined form; projection restores the
canonical sakin host and latent qata, and annotates the article family."""
from __future__ import annotations

from ...model.canon import Annotation, CanonLetter, Nucleus, Onset, Quality
from ...model.inscription import GraphemeClass, SlotFact
from ...orthography.inventory import LetterEntry, MarkEntry

_HARAKA_QUALITY = {"َ": Quality.A, "ُ": Quality.U, "ِ": Quality.I}
_HARAKA_ROLE = {"َ": "fatha", "ُ": "damma", "ِ": "kasra"}
_WASL_MARKS = frozenset("۪۬۟")

#: Scalars that carry no letter identity when reading a base skeleton.
_NON_SKELETON = frozenset('ًٌٍَُِّْٰٖ۪ٗٞٓ۬۟ـۥۦٕۧۢٔ')

#: The eased `جَآءَ ا۟لَ` tokens: their onset belongs to the hamza-meetings
#: chapter, not to naql, although they share the bare-alif spelling.
_EASED_AAL = "ا۟لَ"

#: A word may not end on these when locating the written moved vowel: stop
#: signs, the plural alif, and its silencing sukun.
_HOST_TRAIL = frozenset("اْۖ۩")

#: Proclitic letters (with their harakas) that may precede a bare-alif
#: article in this source.
_PROCLITICS = {"و": "َ", "ف": "َ", "ب": "ِ", "ك": "َ"}

#: Article bases whose deleted qata carried the long badal A, so the written
#: `لَا`/`لَٰ` reads long. Everything else in the family reads the short
#: transferred vowel. Reviewed against the full selected corpus.
_LONG_BASES = frozenset({
    "ثمين", "خر", "خرة", "خرين", "زفة", "صال", "فاق", "فلين",
    "كلين", "لهة", "مرون", "منين", "ن", "ية", "يت",
})

#: The one verse-final host written with its moved vowel: source `وَانْحَرِ`
#: before the latent `اِنَّ` opening the next verse.
_VERSE_FINAL_HOSTS = {"وَانْحَرِ": Quality.I}


def latent_qata_quality(text: str) -> Quality | None:
    """The transferred vowel a word-initial latent qata spells, or None."""
    if len(text) < 2 or text[0] != "ا":
        return None
    if latent_qata_badal_quality(text) is not None:
        return None
    if text[1] in _HARAKA_QUALITY and (len(text) < 3 or text[2] not in _WASL_MARKS):
        if len(text) >= 5 and text[2] == "ل" and text[4] == "ٓ":
            return None  # a vocalized compact opening spells letter names
        return _HARAKA_QUALITY[text[1]]
    if text[1] == "۟" and (len(text) < 3 or text[2] not in _HARAKA_QUALITY):
        return None if text.startswith(_EASED_AAL) else Quality.U
    return None


def latent_qata_badal_quality(text: str) -> Quality | None:
    """The initial long badal family deferred from ordinary naql."""
    if len(text) < 2 or text[0] != "ا":
        return None
    if text[1] == "ٰ":
        return Quality.A
    if len(text) < 3:
        return None
    if text[1] in "ُ۟" and text[2] == "و":
        return Quality.U
    if text[1] == "ِ" and text[2] in "يے" and (
        len(text) < 4 or text[3] != "ّ"
    ):
        return Quality.I
    return None


def project_latent_qata(text: str, entries: list) -> None:
    """A word-initial bare alif family is the latent qata hamza itself."""
    if latent_qata_quality(text) is None:
        return
    entries[0] = LetterEntry(CanonLetter.HAMZA)
    if text[1] == "۟":
        # The stroke spells the qata's damm here, not a wasl start quality.
        entries[1] = MarkEntry(
            role="damma",
            cls=GraphemeClass.HARAKA,
            fact=SlotFact.VOWEL_QUALITY,
            value=Nucleus.short(Quality.U),
        )


def demote_moved_haraka(text: str, entries: list, quality: Quality) -> None:
    """The host's written final haraka is the naql witness, not its own
    canonical vowel: the underlying host stays sakin."""
    index = len(text) - 1
    while index > 0 and text[index] in _HOST_TRAIL:
        index -= 1
    if index <= 0 or _HARAKA_QUALITY.get(text[index]) is not quality:
        return
    entries[index] = MarkEntry(
        role="naql_witness",
        cls=GraphemeClass.HARAKA,
        decorates="host",
        attests=True,
    )


def project_verse_final_host(text: str, entries: list) -> None:
    quality = _VERSE_FINAL_HOSTS.get(text)
    if quality is not None:
        demote_moved_haraka(text, entries, quality)


def _skeleton(text: str) -> str:
    return "".join(char for char in text if char not in _NON_SKELETON)


def _article_lam(text: str) -> tuple[int, int | None] | None:
    """The naql'd article lam index and the bare wasl alif to project."""
    if (
        len(text) >= 4
        and text[0] == "ا"
        and text[1] in _HARAKA_QUALITY
        and text[2] == "۬"
        and text[3] == "ل"
    ):
        return 3, None
    prefixed = _prefixed_lam(text)
    if prefixed is not None:
        return prefixed
    lil = _lil_lam(text)
    if lil is not None:
        return lil, None
    if text.startswith("ءَال") and _skeleton(text[6:]) == "ن":
        return 3, None  # the interrogative `ءَالَٰنَ`; the prefix stays qata
    return None


def _prefixed_lam(text: str) -> tuple[int, int] | None:
    index = 0
    while (
        index + 1 < len(text)
        and text[index] in _PROCLITICS
        and text[index + 1] == _PROCLITICS[text[index]]
    ):
        index += 2
    if index and index + 1 < len(text) and text[index] == "ا" and text[index + 1] == "ل":
        return index + 1, index
    return None


def _lil_lam(text: str) -> int | None:
    index = 2 if text.startswith("وَ") else 0
    if index >= len(text) or text[index] != "ل":
        return None
    index += 1
    voweled = False
    while index < len(text) and text[index] in "َِّ":
        voweled = voweled or text[index] in _HARAKA_QUALITY
        index += 1
    if voweled and index < len(text) and text[index] == "ل":
        return index
    return None


def project_article_naql(text: str, entries: list) -> None:
    """A voweled article lam followed by the deleted qata's rasm."""
    found = _article_lam(text)
    if found is None:
        return
    lam, wasl_alif = found
    haraka = lam + 1
    carrier = lam + 2
    if haraka >= len(text) or text[haraka] not in _HARAKA_QUALITY:
        return
    if carrier >= len(text) or text[carrier] not in "اٰ":
        return
    long_base = text[carrier] == "ٰ" or _skeleton(text[carrier + 1:]) in _LONG_BASES
    entries[carrier] = MarkEntry(
        role="naql_qata_rasm",
        cls=GraphemeClass.ANNOTATION,
        fact=SlotFact.TAJWEED_MARK,
        value=Annotation.NAQL,
    )
    if long_base:
        entries[haraka] = MarkEntry(
            role=_HARAKA_ROLE[text[haraka]],
            cls=GraphemeClass.HARAKA,
            fact=SlotFact.VOWEL_QUALITY,
            value=Nucleus.long(Quality.A),
        )
    if wasl_alif is not None:
        entries[wasl_alif] = LetterEntry(
            CanonLetter.HAMZA, onset=Onset.WASL, seat=True
        )


__all__ = [
    "demote_moved_haraka",
    "latent_qata_badal_quality",
    "latent_qata_quality",
    "project_article_naql",
    "project_latent_qata",
    "project_verse_final_host",
]
