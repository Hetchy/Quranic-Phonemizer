from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

YUDRIKKUM = Site(hafs=("4:78", (3,)))
AQUL_LAKUM = Site(hafs=("2:33", (10, 11)))

THE_SAME_LETTER_TWICE = [
    ("2:16", (7, 8),
     ("rˤaˤbiħa", "ttiʒa:rˤaˤtuhum")),           # رَبِحَت تِّجَـٰرَتُهُمْ
    ("2:33", (10, 11), ("ʔaqu", "llakum")),      # أَقُل لَّكُمْ
    ("2:60", (6, 7), ("ʔidˤri", "bbiʕasˤaˤ:k")),  # ٱضْرِب بِّعَصَاكَ
    ("2:61", (57, 58), ("ʕasˤaˤ", "wwaka:nu:")),  # عَصَوا۟ وَّكَانُوا۟
    ("3:41", (15, 16), ("waðku", "rˤrˤaˤbbak")),  # وَٱذْكُر رَّبَّكَ
    ("5:61", (5, 6), ("waqaˤ", "ddaxaˤlu:")),    # وَقَد دَّخَلُوا۟
    ("21:87", (3, 4), ("ʔi", "ððahabQ")),        # إِذ ذَّهَبَ
    ("18:78", (10, 11), ("tastatˤi", "ʕʕalajh")),  # تَسْتَطِع عَّلَيْهِ
    ("17:33", (17, 18), ("jusri", "ffi:")),      # يُسْرِف فِّى
]


@pytest.mark.parametrize(("ref", "words", "expected"), THE_SAME_LETTER_TWICE)
def test_a_letter_merges_into_the_same_letter_across_a_boundary(
    ref, words, expected
):
    first, last = words
    r = reading(Site(hafs=(ref, words)), ibtidaa=first, waqf=last)
    assert (r.phonemes(first), r.phonemes(last)) == expected


@for_each_riwayah(YUDRIKKUM, isolated=3)
def test_the_same_merger_inside_one_word(r):
    # يُدْرِككُّمُ
    assert r.phonemes(3) == "judQrikkum"


@for_each_riwayah(AQUL_LAKUM, isolated=10)
def test_a_stop_after_the_first_lam_undoes_the_merger(r):
    # أَقُل
    assert r.phonemes(10) == "ʔaqul"
