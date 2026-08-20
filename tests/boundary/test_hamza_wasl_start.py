from __future__ import annotations

import pytest

from quranic_phonemizer.model.canon import HAMZA_WASL_START

from tests.support import Site, for_each_riwayah, reading

ALLAHU = Site(hafs=("2:15", (1,)))
ILTAQA = Site(hafs=("3:155", (6,)))

AFTER_THE_ARTICLE = [
    ("1:2", 1, "ʔalħamdQ"),          # ٱلْحَمْدُ
    ("2:2", 2, "ʔalkita:bQ"),        # ٱلْكِتَـٰبُ
    ("114:1", 4, "ʔaña:s"),          # ٱلنَّاسِ
]

VERB_WITH_A_DAMMA = [
    ("2:58", 3, "ʔudQxulu:"),        # ٱدْخُلُوا۟
    ("6:11", 6, "ʔuŋðˤurˤu:"),      # ٱنظُرُوا۟
    ("4:66", 6, "ʔuqQtulu:"),        # ٱقْتُلُوٓا۟
]

VERB_WITHOUT_A_DAMMA = [
    ("20:24", 1, "ʔiðhabQ"),         # ٱذْهَبْ
    ("2:60", 6, "ʔidˤribQ"),         # ٱضْرِب
    ("89:28", 1, "ʔirˤʒiʕi:"),       # ٱرْجِعِىٓ
]

IRREGULAR_NOUN = [
    ("2:87", 11, "ʔibQn"),           # ٱبْنَ
    ("66:12", 2, "ʔibQnat"),         # ٱبْنَتَ
    ("4:176", 8, "ʔimrˤuʔ"),         # ٱمْرُؤٌا۟
    ("4:12", 56, "ʔimrˤaˤʔah"),      # ٱمْرَأَةٌ
    ("5:106", 12, "ʔiθna:n"),        # ٱثْنَانِ
    ("2:60", 11, "ʔiθnata:"),        # ٱثْنَتَا
    ("2:114", 10, "ʔismuh"),         # ٱسْمُهُۥ
]


def _started_on(ref, word):
    return reading(Site(hafs=(ref, (word,))), isolated=word)


#: The rule identifiers, so a test names the vowel it means.
STARTS = {rule.value for rule in HAMZA_WASL_START}


def _check(ref, word, expected, start):
    """The start names its own helping vowel, and only that one."""
    r = _started_on(ref, word)
    assert r.phonemes(word) == expected
    assert STARTS & r.rules_on_char(word, "ٱ") == {start}
    assert STARTS & r.rules_on_sound(word, "ʔ") == {start}


@pytest.mark.parametrize(("ref", "word", "expected"), AFTER_THE_ARTICLE)
def test_the_article_gives_the_prosthetic_hamza_a_fatha(ref, word, expected):
    _check(ref, word, expected, "hamza_wasl_fatha")


@pytest.mark.parametrize(("ref", "word", "expected"), VERB_WITH_A_DAMMA)
def test_a_verb_whose_third_letter_carries_a_damma_takes_a_damma(
    ref, word, expected
):
    _check(ref, word, expected, "hamza_wasl_damma")


@pytest.mark.parametrize(("ref", "word", "expected"), VERB_WITHOUT_A_DAMMA)
def test_a_verb_whose_third_letter_carries_no_damma_takes_a_kasra(
    ref, word, expected
):
    _check(ref, word, expected, "hamza_wasl_kasra")


@pytest.mark.parametrize(("ref", "word", "expected"), IRREGULAR_NOUN)
def test_the_seven_nouns_that_take_a_kasra_of_their_own(ref, word, expected):
    _check(ref, word, expected, "hamza_wasl_kasra")


@pytest.mark.parametrize(
    ("ref", "word", "start"),
    [
        ("1:2", 1, "hamza_wasl_fatha"),   # ٱلْحَمْدُ
        ("20:24", 1, "hamza_wasl_kasra"), # ٱذْهَبْ
        ("2:58", 3, "hamza_wasl_damma"),  # ٱدْخُلُوا۟
    ],
)
def test_each_helping_vowel_has_a_start_rule_of_its_own(ref, word, start):
    """One reference per vowel: the three starts are separate identities, and
    a consumer reading one never has to look at the vowel to tell them apart."""
    r = _started_on(ref, word)
    assert STARTS & r.rules_on_char(word, "ٱ") == {start}


@for_each_riwayah(ALLAHU, isolated=1)
def test_the_helping_vowel_is_a_fatha_before_the_divine_name(r):
    # ٱللَّهُ
    assert r.phonemes(1) == "ʔalˤlˤaˤ:h"
    assert "hamza_wasl_fatha" in r.rules_on_char(1, "ٱ")


@for_each_riwayah(ILTAQA, isolated=6)
def test_a_form_eight_verb_takes_a_kasra_and_not_the_article_fatha(r):
    # ٱلْتَقَى
    # the engine gives it the fatha the article takes, reading it as one
    assert r.phonemes(6) == "ʔiltaqaˤ:"
    assert "hamza_wasl_kasra" in r.rules_on_char(6, "ٱ")
