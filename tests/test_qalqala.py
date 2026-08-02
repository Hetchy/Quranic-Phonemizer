from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading


def _alone(ref: str, word: int) -> str:
    site = Site(hafs=(ref, (word,)))
    return reading(site, isolated=word).phonemes(word)


SUGHRA = [
    ("2:3", 7, "rˤaˤzaqQna:hum"),      # رَزَقْنَـٰهُمْ
    ("2:19", 18, "muħi:tˤQ"),          # مُحِيطٌ
    ("2:4", 9, "qaˤbQlik"),            # قَبْلِكَ
    ("2:19", 9, "jaʒQʕalu:n"),         # يَجْعَلُونَ
    ("2:19", 7, "warˤaˤʕdQ"),          # وَرَعْدٌ
]

KUBRA = [
    ("2:19", 14, "ʔasˤsˤaˤwa:ʕiqQ"),   # ٱلصَّوَٰعِقِ
    ("1:6", 2, "ʔasˤsˤirˤaˤ:tˤQ"),     # ٱلصِّرَٰطَ
    ("1:7", 6, "ʔalmaɣdˤu:bQ"),        # ٱلْمَغْضُوبِ
    ("2:22", 12, "faʔaxrˤaˤʒQ"),       # فَأَخْرَجَ
    ("1:2", 1, "ʔalħamdQ"),            # ٱلْحَمْدُ
]

AKBAR = [
    ("2:26", 17, "ʔalħaqqQ"),          # ٱلْحَقُّ
    ("1:2", 3, "rˤaˤbbQ"),             # رَبِّ
    ("2:158", 8, "ħaʒʒQ"),             # حَجَّ
    ("2:74", 10, "ʔaʃaddQ"),           # أَشَدُّ
]


@pytest.mark.parametrize(("ref", "word", "expected"), SUGHRA)
def test_every_qalqala_letter_echoes_quiescent_inside_a_word(
    ref, word, expected
):
    assert _alone(ref, word) == expected


@pytest.mark.parametrize(("ref", "word", "expected"), KUBRA)
def test_every_qalqala_letter_echoes_when_the_stop_silences_it(
    ref, word, expected
):
    assert _alone(ref, word) == expected


@pytest.mark.parametrize(("ref", "word", "expected"), AKBAR)
def test_a_doubled_qalqala_letter_echoes_at_a_stop(ref, word, expected):
    assert _alone(ref, word) == expected


BIMA = Site(hafs=("2:10", (10,)))
QABLIKA = Site(hafs=("2:4", (9,)))


@for_each_riwayah(BIMA, isolated=10)
def test_a_qalqala_letter_carrying_a_vowel_is_not_echoed(r):
    # بِمَا
    assert r.phonemes(10) == "bima:"
    assert "Q" not in r.phonemes(10)


@for_each_riwayah(QABLIKA, ibtidaa=9, wasl=9)
def test_the_echo_inside_a_word_does_not_depend_on_the_junction(r):
    # قَبْلِكَ
    assert r.phonemes(9) == "qaˤbQlika"
