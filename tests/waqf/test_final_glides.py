from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

HUWA = Site(hafs=("2:29", (1,)))
WA_HUWA = Site(hafs=("2:29", (16,)))
HIYA = Site(hafs=("2:70", (8,)))
RABBIYA = Site(hafs=("2:258", (16,)))


@for_each_riwayah(HUWA, ibtidaa=1, wasl=1)
def test_a_final_waw_is_a_consonant_when_the_reading_carries_on(r):
    # هُوَ
    assert r.phonemes(1) == "huwa"
    assert r.silent(1) == frozenset()
    assert r.rules_on_char(1, "و") == frozenset()


@for_each_riwayah(HUWA, isolated=1)
def test_that_waw_becomes_pure_length_at_a_stop(r):
    # هُوَ
    assert r.phonemes(1) == "hu:"
    assert r.silent(1) == {"َ"}
    assert "waqf_diacritic_drop" in r.rules_on_char(1, "َ")
    assert "madd_tabii" in r.rules_on_char(1, "و")
    assert r.rules_on_sound(1, "u:") == {"madd_tabii"}


@for_each_riwayah(WA_HUWA, ibtidaa=16, wasl=16)
def test_a_prefixed_word_keeps_its_consonantal_waw_when_joined(r):
    # وَهُوَ
    assert r.phonemes(16) == "wahuwa"
    assert r.silent(16) == frozenset()


@for_each_riwayah(WA_HUWA, isolated=16)
def test_that_prefixed_waw_becomes_pure_length_at_a_stop(r):
    # وَهُوَ
    assert r.phonemes(16) == "wahu:"
    assert r.silent(16) == {"َ"}
    assert r.rules_on_sound(16, "u:") == {"madd_tabii"}


@for_each_riwayah(HIYA, ibtidaa=8, wasl=8)
def test_a_final_yaa_is_a_consonant_when_the_reading_carries_on(r):
    # هِىَ
    assert r.phonemes(8) == "hija"
    assert r.silent(8) == frozenset()
    assert r.rules_on_char(8, "ى") == frozenset()


@for_each_riwayah(HIYA, isolated=8)
def test_that_yaa_becomes_pure_length_at_a_stop(r):
    # هِىَ
    assert r.phonemes(8) == "hi:"
    assert r.silent(8) == {"َ"}
    assert "madd_tabii" in r.rules_on_char(8, "ى")
    assert r.rules_on_sound(8, "i:") == {"madd_tabii"}


@for_each_riwayah(RABBIYA, ibtidaa=16, wasl=16)
def test_a_pronoun_yaa_is_a_consonant_when_the_reading_carries_on(r):
    # رَبِّىَ
    assert r.phonemes(16) == "rˤaˤbbija"
    assert r.silent(16) == frozenset()


@for_each_riwayah(RABBIYA, isolated=16)
def test_that_pronoun_yaa_becomes_pure_length_at_a_stop(r):
    # رَبِّىَ
    assert r.phonemes(16) == "rˤaˤbbi:"
    assert r.silent(16) == {"َ"}
    assert r.rules_on_sound(16, "i:") == {"madd_tabii"}


#: A waw carrying a fatha, written with the otiose alif behind it. Joined, the
#: waw is a consonant; the stop drops the fatha and leaves it quiescent after
#: a damma, which is length.
FATHA_BEFORE_THE_OTIOSE_ALIF = [
    ("2:237", 18, 19, "jaʕfuwa", "jaʕfu:", "llaði:"),          # يَعْفُوَا۟ ٱلَّذِى
    ("13:30", 10, 11, "litatluwa", "litatlu:", "ʕalajhim"),    # لِّتَتْلُوَا۟ عَلَيْهِمُ
    ("18:14", 12, 13, "nadQʕuwa", "nadQʕu:", "min"),           # نَّدْعُوَا۟ مِن
    ("27:92", 2, 3, "ʔatluwa", "ʔatlu:", "lqurˤʔa:n"),         # أَتْلُوَا۟ ٱلْقُرْءَانَ
    ("30:39", 5, 6, "lijarˤbuwa", "lijarˤbu:", "fi:"),         # لِّيَرْبُوَا۟ فِىٓ
    ("47:4", 28, 29, "lijabQluwa", "lijabQlu:", "baʕdˤaˤkum"),  # لِّيَبْلُوَا۟ بَعْضَكُم
    ("47:31", 7, 8, "wanabQluwa", "wanabQlu:", "ʔaxba:rˤaˤkum"),  # وَنَبْلُوَا۟ أَخْبَارَكُمْ
]


@pytest.mark.parametrize(
    ("ref", "word", "after", "joined", "stopped", "next_word"),
    FATHA_BEFORE_THE_OTIOSE_ALIF,
)
def test_a_waw_holding_a_fatha_is_a_consonant_when_the_reading_carries_on(
    ref, word, after, joined, stopped, next_word
):
    r = reading(Site(hafs=(ref, (word, after))), ibtidaa=word, waqf=after)
    assert (r.phonemes(word), r.phonemes(after)) == (joined, next_word)


@pytest.mark.parametrize(
    ("ref", "word", "after", "joined", "stopped", "next_word"),
    FATHA_BEFORE_THE_OTIOSE_ALIF,
)
def test_the_stop_drops_that_fatha_and_leaves_the_waw_as_length(
    ref, word, after, joined, stopped, next_word
):
    r = reading(Site(hafs=(ref, (word,))), isolated=word)
    assert r.phonemes(word) == stopped
    assert r.silent(word) == {"ا", "َ", "۟"}
