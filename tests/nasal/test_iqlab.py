from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

MIN_BADI = Site(hafs=("2:56", (3, 4)))

INSIDE_ONE_WORD = [
    ("19:92", 2, "jaŋbaɣi:"),      # يَنبَغِى
    ("26:6", 4, "ʔaŋba:ʔ"),        # أَنبَـٰٓؤُا۟
    ("37:146", 1, "waʔaŋbatna:"),  # وَأَنبَتْنَا
    ("80:27", 1, "faʔaŋbatna:"),   # فَأَنبَتْنَا
]

TANWEEN_ACROSS_A_BOUNDARY = [
    ("2:18", (1, 2), ("sˤum̃uŋ", "bukm")),            # صُمٌّ بُكْمٌ
    ("3:34", (1, 2), ("ðurrijjataŋ", "baʕdˤuha:")),   # ذُرِّيَّةً بَعْضُهَا
    ("19:14", (1, 2), ("wabarˤrˤaˤŋ", "biwa:lidajh")), # وَبَرًّا بِوَٰلِدَيْهِ
    ("2:241", (2, 3), ("mata:ʕuŋ", "bilmaʕrˤu:f")),   # مَتَـٰعٌ بِٱلْمَعْرُوفِ
    ("2:10", (9, 10), ("ʔali:muŋ", "bima:")),         # أَلِيمٌ بِمَا
]


@pytest.mark.parametrize(("ref", "word", "expected"), INSIDE_ONE_WORD)
def test_a_written_noon_before_a_baa_turns_inside_one_word(
    ref, word, expected
):
    site = Site(hafs=(ref, (word,)))
    assert reading(site, isolated=word).phonemes(word) == expected


@pytest.mark.parametrize(
    ("ref", "words", "expected"), TANWEEN_ACROSS_A_BOUNDARY
)
def test_a_tanween_turns_when_a_baa_starts_the_next_word(
    ref, words, expected
):
    first, last = words
    r = reading(Site(hafs=(ref, words)), ibtidaa=first, waqf=last)
    assert (r.phonemes(first), r.phonemes(last)) == expected


@for_each_riwayah(MIN_BADI, ibtidaa=3, waqf=4)
def test_a_quiescent_noon_turns_across_a_word_seam(r):
    # مِّن بَعْدِ
    assert r.phonemes(3) == "miŋ"
    assert r.phonemes(4) == "baʕdQ"
