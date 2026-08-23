"""A sakt is a silence the reading holds, not a stop the caller asked for.

It survives a request to join everything and brings no pausal treatment;
where a stop is asked for at the same word, the stop is what happens.
"""
from __future__ import annotations

import pytest

from quranic_phonemizer import Phonemizer
from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Riwayah
from quranic_phonemizer.model.canon import Rule
from quranic_phonemizer.session import phonemize_request

from tests.support import Site, reading

#: Every word the reading holds a sakt after, and the word it holds it before.
SAKT_SITES = [
    ("36:52", 6, 7),    # مَّرْقَدِنَاۜ هَـٰذَا
    ("75:27", 2, 3),    # مَنْ ۜ رَاقٍ
    ("83:14", 2, 3),    # بَلْ ۜ رَانَ
    ("69:28", 4, 5),    # مَالِيَهْۜ هَلَكَ
]

#: The one sakt word that also carries a stop sign.
MARQADINA = ("36:52", 6)


def _pair(ref, word, following):
    return reading(Site(hafs=(ref, (word, following))), ibtidaa=word, wasl=word)


@pytest.mark.parametrize(("ref", "word", "following"), SAKT_SITES)
def test_the_reading_holds_a_sakt_after_each_of_these_words(
    ref, word, following
):
    r = _pair(ref, word, following)
    assert r.score.words[word - 1].sakt_after


@pytest.mark.parametrize(("ref", "word", "following"), SAKT_SITES)
def test_no_rule_crosses_a_sakt_even_when_every_word_is_asked_to_join(
    ref, word, following
):
    """The plan here joins throughout, and the silence still separates the
    two words: nothing names a slot on both sides of it."""
    r = _pair(ref, word, following)
    left = {slot.id for slot in r.score.words[word - 1].slots}
    right = {slot.id for slot in r.score.words[following - 1].slots}
    crossing = [
        occurrence for occurrence in r.performance.occurrences
        if (set(occurrence.subjects) | set(occurrence.context)) & left
        and (set(occurrence.subjects) | set(occurrence.context)) & right
    ]
    assert crossing == []


@pytest.mark.parametrize(("ref", "word", "following"), SAKT_SITES)
def test_a_sakt_is_neither_a_stop_nor_a_start(ref, word, following):
    """A stop would put the word into its pausal form and let the next one be
    started on; a sakt does neither."""
    result = Phonemizer().phonemize(f"{ref}-{_next_verse(ref)}")
    held = result.words[word - 1]
    assert held.sakt_after
    assert not held.is_stopped_on
    assert not result.words[word].is_started_on


def _next_verse(ref: str) -> str:
    surah, ayah = (int(part) for part in ref.split(":"))
    return f"{surah}:{ayah + 1}"


def test_iwaja_carries_the_first_authored_sakt():
    # عِوَجَاۜ قَيِّمًا
    ref, word = "18:1", 11
    result = Phonemizer().phonemize(f"{ref}-{_next_verse(ref)}")
    held = result.words[word - 1]
    assert "ۜ" in held.text
    assert held.sakt_after
    assert not held.is_stopped_on
    assert "".join(result.phonemes("word")[word - 1]) == "ʕiwaʒa:"


@pytest.mark.parametrize(
    ("ref", "word", "rule"),
    [
        ("18:1", 11, Rule.MADD_TABII),
        ("36:52", 6, Rule.MADD_TABII),
        ("75:27", 2, Rule.IZHAR),
    ],
)
def test_sakt_keeps_the_local_rule_on_its_final_sound(ref, word, rule):
    session = phonemize_request(
        recitation(Riwayah.HAFS), f"{ref}-{_next_verse(ref)}", stop_refs=[]
    )
    slots = {slot.id for slot in session.score.words[word - 1].slots}
    assert rule in {
        occurrence.rule for occurrence in session.performance.occurrences
        if set(occurrence.subjects) & slots
    }


def test_a_stop_asked_for_at_a_sakt_word_is_a_stop():
    """Both marks sit on `مَّرْقَدِنَاۜ`. A caller who honours the stop sign
    stops there; the sakt is what happens when no one asks."""
    # مَّرْقَدِنَاۜ هَـٰذَا
    ref, word = MARQADINA
    phonemizer = Phonemizer()
    unasked = phonemizer.phonemize(ref).words[word - 1]
    assert unasked.sakt_after and not unasked.is_stopped_on

    for asked in (
        phonemizer.phonemize(ref, stop_signs=["preferred_stop"]),
        phonemizer.phonemize(ref, stop_refs=[f"{ref}:{word}"]),
    ):
        assert asked.words[word - 1].is_stopped_on
        assert asked.words[word].is_started_on
