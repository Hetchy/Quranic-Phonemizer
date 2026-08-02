from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

BISMI_ALLAHI = Site(hafs=("1:1", (1, 2)))

BEFORE_THE_ARTICLE = [
    ("2:8", (1, 2), ("wamina", "ña:s")),            # وَمِنَ ٱلنَّاسِ
    ("2:2", (1, 2), ("ða:lika", "lkita:bQ")),       # ذَٰلِكَ ٱلْكِتَـٰبُ
    ("7:26", (10, 11),
     ("waliba:su", "ttaqQwa:")),                    # وَلِبَاسُ ٱلتَّقْوَىٰ
]

BEFORE_A_VERB = [
    ("6:11", (5, 6), ("θum̃a", "ŋðˤurˤu:")),        # ثُمَّ ٱنظُرُوا۟
    ("7:38", (1, 2), ("qaˤ:la", "dQxulu:")),        # قَالَ ٱدْخُلُوا۟
    ("17:63", (1, 2), ("qaˤ:la", "ðhabQ")),         # قَالَ ٱذْهَبْ
    ("12:50", (8, 9), ("qaˤ:la", "rˤʒiʕ")),         # قَالَ ٱرْجِعْ
]

BEFORE_AN_IRREGULAR_NOUN = [
    ("5:17", (8, 9), ("ʔalmasi:ħu", "bQn")),        # ٱلْمَسِيحُ ٱبْنُ
    ("66:12", (1, 2), ("wamarˤjama", "bQnat")),     # وَمَرْيَمَ ٱبْنَتَ
    ("12:30", (4, 5),
     ("ʔalmadi:nati", "mrˤaˤʔat")),                 # ٱلْمَدِينَةِ ٱمْرَأَتُ
    ("6:118", (3, 4), ("ðukirˤaˤ", "sm")),          # ذُكِرَ ٱسْمُ
    ("5:106", (11, 12),
     ("ʔalwasˤijjati", "θna:n")),                   # ٱلْوَصِيَّةِ ٱثْنَانِ
    ("2:60", (10, 11), ("minhu", "θnata:")),        # مِنْهُ ٱثْنَتَا
]


def _joined(ref, words):
    first, last = words
    r = reading(Site(hafs=(ref, words)), ibtidaa=first, waqf=last)
    return r.phonemes(first), r.phonemes(last)


@pytest.mark.parametrize(("ref", "words", "expected"), BEFORE_THE_ARTICLE)
def test_the_article_hamza_drops_when_the_word_before_it_joins(
    ref, words, expected
):
    assert _joined(ref, words) == expected


@pytest.mark.parametrize(("ref", "words", "expected"), BEFORE_A_VERB)
def test_a_verb_hamza_drops_when_the_word_before_it_joins(
    ref, words, expected
):
    assert _joined(ref, words) == expected


@pytest.mark.parametrize(
    ("ref", "words", "expected"), BEFORE_AN_IRREGULAR_NOUN
)
def test_an_irregular_noun_hamza_drops_when_the_word_before_it_joins(
    ref, words, expected
):
    assert _joined(ref, words) == expected


@for_each_riwayah(BISMI_ALLAHI, ibtidaa=1, waqf=2)
def test_the_divine_name_loses_its_hamza_when_the_word_before_it_joins(r):
    # بِسْمِ ٱللَّهِ
    assert r.phonemes(1) == "bismi"
    assert r.phonemes(2) == "lla:h"
    assert r.silent(2) == {"ِ", "ٱ"}
