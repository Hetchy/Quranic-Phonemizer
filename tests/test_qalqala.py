from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading


def _alone(ref: str, word: int):
    site = Site(hafs=(ref, (word,)))
    return reading(site, isolated=word)


def _check(ref, word, letter, expected, degree):
    r = _alone(ref, word)
    assert r.phonemes(word) == expected
    assert degree in r.rules_on_char(word, letter)
    assert r.rules_on_sound(word, "Q") == {degree}


SUGHRA = [
    ("2:3", 7, "ق", "rˤaˤzaqQna:hum"),      # رَزَقْنَـٰهُمْ
    ("106:4", 2, "ط", "ʔatˤQʕamahum"),      # أَطْعَمَهُم
    ("2:17", 17, "ب", "jubQsˤirˤu:n"),      # يُبْصِرُونَ
    ("2:19", 9, "ج", "jaʒQʕalu:n"),         # يَجْعَلُونَ
    ("46:4", 4, "د", "tadQʕu:n"),           # تَدْعُونَ
]

KUBRA = [
    ("2:19", 14, "ق", "ʔasˤsˤaˤwa:ʕiqQ"),   # ٱلصَّوَٰعِقِ
    ("1:6", 2, "ط", "ʔasˤsˤirˤaˤ:tˤQ"),     # ٱلصِّرَٰطَ
    ("1:7", 6, "ب", "ʔalmaɣdˤu:bQ"),        # ٱلْمَغْضُوبِ
    ("2:22", 12, "ج", "faʔaxrˤaˤʒQ"),       # فَأَخْرَجَ
    ("2:20", 1, "د", "jaka:dQ"),            # يَكَادُ
]

#: A qalqala letter the stop silences under its own tanween. The stop makes it
#: final and quiescent, so the echo is the heavier degree.
TANWEEN_AT_A_STOP = [
    ("2:19", 18, "ط", "muħi:tˤQ"),          # مُحِيطٌ
    ("2:19", 7, "د", "warˤaˤʕdQ"),          # وَرَعْدٌ
]

AKBAR = [
    ("2:26", 17, "ق", "ʔalħaqqQ"),          # ٱلْحَقُّ
    ("1:2", 3, "ب", "rˤaˤbbQ"),             # رَبِّ
    ("2:158", 8, "ج", "ħaʒʒQ"),             # حَجَّ
    ("2:74", 10, "د", "ʔaʃaddQ"),           # أَشَدُّ
]


@pytest.mark.parametrize(("ref", "word", "letter", "expected"), SUGHRA)
def test_every_qalqala_letter_echoes_quiescent_inside_a_word(
    ref, word, letter, expected
):
    _check(ref, word, letter, expected, "qalqala_sughra")


@pytest.mark.parametrize(("ref", "word", "letter", "expected"), KUBRA)
def test_every_qalqala_letter_echoes_when_the_stop_silences_it(
    ref, word, letter, expected
):
    _check(ref, word, letter, expected, "qalqala_kubra")


@pytest.mark.engine_bug
@pytest.mark.parametrize(
    ("ref", "word", "letter", "expected"), TANWEEN_AT_A_STOP
)
def test_a_qalqala_letter_under_a_tanween_echoes_when_stopped_on(
    ref, word, letter, expected
):
    # the engine files these as the lighter degree
    _check(ref, word, letter, expected, "qalqala_kubra")


@pytest.mark.parametrize(("ref", "word", "letter", "expected"), AKBAR)
def test_a_doubled_qalqala_letter_echoes_at_a_stop(
    ref, word, letter, expected
):
    _check(ref, word, letter, expected, "qalqala_akbar")


BIMA = Site(hafs=("2:10", (10,)))
QABLIKA = Site(hafs=("2:4", (9,)))


@for_each_riwayah(BIMA, isolated=10)
def test_a_qalqala_letter_carrying_a_vowel_is_not_echoed(r):
    # بِمَا
    assert r.phonemes(10) == "bima:"
    assert not any(
        rule.startswith("qalqala") for rule in r.rules_on_char(10, "ب")
    )


@for_each_riwayah(QABLIKA, ibtidaa=9, wasl=9)
def test_the_echo_inside_a_word_does_not_depend_on_the_junction(r):
    # قَبْلِكَ
    assert r.phonemes(9) == "qaˤbQlika"
    assert "qalqala_sughra" in r.rules_on_char(9, "ب")
    assert r.rules_on_sound(9, "Q") == {"qalqala_sughra"}


IQRA_KHALAQA = Site(hafs=("96:1", (1, 2, 3, 4, 5)))


def test_the_degree_toggle_defaults_to_one_token():
    # ٱقْرَأْ .. خَلَقَ -- the toggle doubles only the kubra echo; sughra and
    # its extended form already share a token.
    off = reading(IQRA_KHALAQA, extra_phonemes=(), waqf=5)
    on = reading(IQRA_KHALAQA, extra_phonemes=("qalqala_degree",), waqf=5)
    assert (off.phonemes(1), on.phonemes(1)) == ("ʔiqQrˤaʔ", "ʔiqQrˤaʔ")
    assert (off.phonemes(5), on.phonemes(5)) == ("xalaqQ", "xalaqQQ")
