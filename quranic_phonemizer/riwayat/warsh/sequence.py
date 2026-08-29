"""Reviewed sequence overrides for the selected King Fahd Warsh script."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from ...model.canon import CanonLetter, Nucleus, Onset, Quality
from ...model.inscription import GraphemeClass, SlotFact
from ...orthography.inventory import Inventory, LetterEntry, MarkEntry
from . import naql_script
from .inclination import is_inclination_witness


_HARAKA_TO_TANWIN = {
    "َ": "fathatan",
    "ُ": "dammatan",
    "ِ": "kasratan",
}
_FATHATAN = frozenset({"ً", "ٗ"})

#: The reviewed wasl small marks. This source writes the linking vowel as an
#: ordinary haraka on the alif, and the start quality as the small mark.
_WASL_MARK_QUALITY = {"۬": Quality.A, "۟": Quality.U, "۪": Quality.I}


def _release_combining_hamza_seats(inventory, text, entries) -> None:
    for index, entry in enumerate(entries[:-2]):
        if (
            isinstance(entry, LetterEntry)
            and entry.letter in {CanonLetter.WAW, CanonLetter.YA}
            and text[index + 1] == "ْ"
            and text[index + 2] in inventory.combining_hamza
        ):
            entries[index] = replace(entry, seat=False)


def _wasl_sequence(text, entries) -> bool:
    matched = (
        len(text) >= 3
        and text[0] == "ا"
        and text[1] in _HARAKA_TO_TANWIN
        and text[2] in _WASL_MARK_QUALITY
    )
    if matched:
        entries[0] = LetterEntry(CanonLetter.HAMZA, onset=Onset.WASL, seat=True)
        entries[1] = MarkEntry(
            role="wasl_link_haraka",
            cls=GraphemeClass.ANNOTATION,
            fact=SlotFact.ONSET,
            value=Onset.WASL,
        )
        entries[2] = MarkEntry(
            role="wasl_start_quality",
            cls=GraphemeClass.ANNOTATION,
            fact=SlotFact.VOWEL_QUALITY,
            value=Nucleus.short(_WASL_MARK_QUALITY[text[2]]),
        )
        _silent_qata_hamza(text, entries)
    return matched


def _silent_qata_hamza(text, entries) -> None:
    """A bare waw or yaa right after the wasl sequence writes the silenced
    qata hamza it replaces when the word is started on: the `ائتوني` family."""
    if (
        len(text) >= 5
        and text[3] in "يو"
        and isinstance(entries[4], LetterEntry)
    ):
        entries[3] = LetterEntry(CanonLetter.HAMZA)


def _project_marked_fatha(text, entries, *, wasl: bool) -> None:
    for index, char in enumerate(text):
        if char == "۪" and not (wasl and index == 2):
            inclined = is_inclination_witness(text, index)
            if inclined:
                entries[index] = MarkEntry(
                    role="inclination_witness", cls=GraphemeClass.ANNOTATION,
                    fact=SlotFact.VOWEL_QUALITY,
                    value=Nucleus.short(Quality.A),
                )
            else:
                entries[index] = MarkEntry(
                    role="fatha", cls=GraphemeClass.ANNOTATION,
                    fact=SlotFact.VOWEL_QUALITY,
                    value=Nucleus.short(Quality.A),
                )
            if (
                inclined and text[index + 1:index + 3] == "يٰ"
            ):
                entries[index + 1] = LetterEntry(
                    CanonLetter.ALIF,
                    dagger_host=True,
                    bare_rasm=True,
                )


def _attach_reversed_fathatan(text, entries) -> None:
    for index, char in enumerate(text[1:], start=1):
        if char in _FATHATAN and text[index - 1] == "ا" and index > 1:
            entries[index] = MarkEntry(
                role="fathatan",
                cls=GraphemeClass.TANWEEN,
                fact=SlotFact.VOWEL_QUALITY,
                derivation="tanween",
                attach_to_previous=True,
            )
        elif char in _FATHATAN and text[index - 1] == "ى":
            entries[index - 1] = LetterEntry(
                CanonLetter.ALIF,
                dagger_host=True,
                bare_rasm=True,
            )
            entries[index] = MarkEntry(
                role="fathatan",
                cls=GraphemeClass.TANWEEN,
                fact=SlotFact.VOWEL_QUALITY,
                derivation="tanween",
                attach_to_previous=True,
            )


def _project_alif_sukun_silence(text, entries) -> None:
    """An ordinary sukun on alif marks rasm, never a consonantal alif."""
    for alif_index in range(len(text) - 1):
        if text[alif_index:alif_index + 2] != "اْ":
            continue
        entry = entries[alif_index]
        if isinstance(entry, LetterEntry) and entry.letter is CanonLetter.ALIF:
            entries[alif_index + 1] = MarkEntry(
                role="silence_sign",
                cls=GraphemeClass.HARAKA,
                decorates="host",
                silences=True,
            )


def _silence_mark(entries, index: int) -> None:
    entries[index] = MarkEntry(
        role="silence_sign",
        cls=GraphemeClass.HARAKA,
        decorates="host",
        silences=True,
    )


def _consonantal_sukun(entries, index: int) -> None:
    entries[index] = MarkEntry(
        role="consonantal_sukun",
        cls=GraphemeClass.HARAKA,
        fact=SlotFact.VOWEL_ABSENCE,
        value=Nucleus.silent(),
    )


def _project_collapsed_hamza(text, entries) -> None:
    """Keep the explicit interrogative hamza in the `أَ۟...` family.

    The following rounded mark attests the unwritten second qata; it is not a
    silence sign on the first hamza.
    """
    if text.startswith("أَ۟"):
        entries[2] = MarkEntry(
            role="collapsed_hamza",
            cls=GraphemeClass.ANNOTATION,
            decorates="host",
        )


def _project_orthographic_silence(text, entries) -> None:
    """Project selected-script sukuns or harakas that mark rasm-only letters."""
    for pattern, relative in (
        ("أُوْ", 3),
        ("إِيْن", 3),
        ("إِيْه", 3),
        ("إِےْ", 3),
    ):
        start = text.find(pattern)
        if start >= 0:
            _silence_mark(entries, start + relative)

    # `بِأَيَيْدٖ`: the stroke after the first yaa is the Maghribi jarrah
    # sukun, while the second written yaa is the rasm-only addition.
    start = text.find("أَيَيْ")
    if start >= 0:
        _consonantal_sukun(entries, start + 3)
        _silence_mark(entries, start + 5)

    for pattern, relative in (
        ("ليْل", 2),
        ("اْيْـٔ", 3),
        ("اْےْء", 3),
    ):
        start = text.find(pattern)
        if start >= 0:
            _consonantal_sukun(entries, start + relative)


def _release_dagger_hamza_seats(text, entries) -> None:
    for index, char in enumerate(text[:-2]):
        if char == "ٰ" and text[index + 1] == "ء" and text[index + 2] == "ْ":
            entries[index] = MarkEntry(
                role="hamza_seat",
                cls=GraphemeClass.SMALL_VOWEL,
                decorates="host",
            )


def _project_hamza_madd(text, entries) -> None:
    """A maddah after hamza supplies the written long A nucleus."""
    for index, char in enumerate(text[1:], start=1):
        if char != "ٓ" or text[index - 1] not in "ءأإؤئ":
            continue
        entries[index] = MarkEntry(
            role="madd",
            cls=GraphemeClass.MADD_SIGN,
            fact=SlotFact.VOWEL_QUALITY,
            value=Nucleus.long(Quality.A),
        )


def _project_composite_tanwin(text, entries) -> None:
    for index, char in enumerate(text):
        if char != "ۢ" or index == 0:
            continue
        previous = text[index - 1]
        role = _HARAKA_TO_TANWIN.get(previous)
        if role is not None:
            behind_alif = index >= 2 and text[index - 2] == "ا"
            entries[index - 1] = MarkEntry(
                role=role,
                cls=GraphemeClass.TANWEEN,
                fact=SlotFact.VOWEL_QUALITY,
                derivation="tanween",
                attach_to_previous=behind_alif,
            )
            if behind_alif:
                entries[index] = MarkEntry(
                    role="mini_meem",
                    cls=GraphemeClass.ANNOTATION,
                    decorates="host",
                    attests=True,
                    attach_to_previous=True,
                )


def _entries(inventory: Inventory, text: str) -> list:
    entries = [inventory.classify(char) for char in text]
    _release_combining_hamza_seats(inventory, text, entries)
    wasl = _wasl_sequence(text, entries)
    naql_script.project_initial_badal(text, entries)
    naql_script.project_latent_qata(text, entries)
    naql_script.project_article_naql(text, entries)
    naql_script.project_verse_final_host(text, entries)
    _project_marked_fatha(text, entries, wasl=wasl)
    _attach_reversed_fathatan(text, entries)
    _project_alif_sukun_silence(text, entries)
    _project_orthographic_silence(text, entries)
    _project_collapsed_hamza(text, entries)
    _release_dagger_hamza_seats(text, entries)
    _project_hamza_madd(text, entries)
    _project_composite_tanwin(text, entries)
    return entries


def entries_for(inventory: Inventory, text: str):
    """Return one classification per scalar without changing source text."""
    return tuple(_entries(inventory, text))


def entries_for_words(inventory: Inventory, texts: Sequence[str]):
    """Per-word classifications for one verse, with cross-word context: a
    host's written moved haraka before a latent qata or initial badal is a
    naql witness."""
    prepared = [_entries(inventory, text) for text in texts]
    for index in range(len(texts) - 1):
        quality = naql_script.latent_qata_quality(texts[index + 1])
        if quality is None:
            quality = naql_script.latent_qata_badal_quality(texts[index + 1])
        if quality is not None:
            naql_script.demote_moved_haraka(
                texts[index], prepared[index], quality
            )
    return tuple(tuple(entries) for entries in prepared)


__all__ = ["entries_for", "entries_for_words"]
