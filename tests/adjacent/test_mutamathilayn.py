from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

YUDRIKKUM = Site(hafs=("4:78", (3,)))
AQUL_LAKUM = Site(hafs=("2:33", (10, 11)))

THE_SAME_LETTER_TWICE = [
    ("2:16", (7, 8), "ت",
     ("rˤaˤbiħa", "ttiʒa:rˤaˤtuhum")),                # رَبِحَت تِّجَـٰرَتُهُمْ
    ("2:33", (10, 11), "ل", ("ʔaqu", "llakum")),      # أَقُل لَّكُمْ
    ("2:60", (6, 7), "ب", ("ʔidˤri", "bbiʕasˤaˤ:k")),  # ٱضْرِب بِّعَصَاكَ
    ("2:61", (57, 58), "و", ("ʕasˤaˤ", "wwaka:nu:")),  # عَصَوا۟ وَّكَانُوا۟
    ("3:41", (15, 16), "ر", ("waðku", "rˤrˤaˤbbak")),  # وَٱذْكُر رَّبَّكَ
    ("5:61", (5, 6), "د", ("waqaˤ", "ddaxaˤlu:")),    # وَقَد دَّخَلُوا۟
    ("21:87", (3, 4), "ذ", ("ʔi", "ððahabQ")),        # إِذ ذَّهَبَ
    ("18:78", (10, 11), "ع", ("tastatˤi", "ʕʕalajh")),  # تَسْتَطِع عَّلَيْهِ
    ("17:33", (17, 18), "ف", ("jusri", "ffi:")),      # يُسْرِف فِّى
]


@pytest.mark.parametrize(
    ("ref", "words", "letter", "expected"), THE_SAME_LETTER_TWICE
)
def test_a_letter_merges_into_the_same_letter_across_a_boundary(
    ref, words, letter, expected
):
    first, last = words
    r = reading(Site(hafs=(ref, words)), ibtidaa=first, waqf=last)
    assert (r.phonemes(first), r.phonemes(last)) == expected
    assert "idgham_mutamathilayn" in r.rules_on_char(first, letter)
    merged = r.sounds(last)[0]
    assert "idgham_mutamathilayn" in r.rules_on_sound(last, merged)


@for_each_riwayah(YUDRIKKUM, isolated=3)
def test_the_same_merger_inside_one_word(r):
    # يُدْرِككُّمُ
    assert r.phonemes(3) == "judQrikkum"
    assert "idgham_mutamathilayn" in r.rules_on_char(3, "ك")
    assert "idgham_mutamathilayn" in r.rules_on_sound(3, "kk")


@for_each_riwayah(AQUL_LAKUM, isolated=10)
def test_a_stop_after_the_first_lam_undoes_the_merger(r):
    # أَقُل
    assert r.phonemes(10) == "ʔaqul"
    assert "idgham_mutamathilayn" not in r.rules_on_char(10, "ل")


WAQAD_DAKHALU = Site(hafs=("5:61", (5, 6)))


@for_each_riwayah(WAQAD_DAKHALU, ibtidaa=5, waqf=6)
def test_a_qalqala_letter_that_merges_away_is_not_echoed(r):
    # وَقَد دَّخَلُوا۟ -- the sakin dal is a qalqala letter, but it never
    # sounds its own place: only the merger reaches it.
    assert r.phonemes(5) == "waqaˤ"
    assert r.rules_on_char(5, "د") == frozenset({"idgham_mutamathilayn"})
