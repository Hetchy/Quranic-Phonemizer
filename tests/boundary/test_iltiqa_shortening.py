from __future__ import annotations

import pytest

from tests.support import Site, reading

A_LONG_VOWEL_GIVING_WAY = [
    ("1:7", (8, 9), ("wala", "dˤdˤaˤ:lli:n")),      # وَلَا ٱلضَّآلِّينَ
    ("2:11", (6, 7), ("fi", "lʔarˤdˤ")),            # فِى ٱلْأَرْضِ
    ("2:68", (1, 2), ("qaˤ:lu", "dQʕ")),            # قَالُوا۟ ٱدْعُ
    ("2:87", (10, 11), ("ʕi:sa", "bQn")),           # عِيسَى ٱبْنَ
    ("1:6", (1, 2),
     ("ʔihdina", "sˤsˤirˤaˤ:tˤQ")),                 # ٱهْدِنَا ٱلصِّرَٰطَ
    ("2:53", (3, 4), ("mu:sa", "lkita:bQ")),        # مُوسَى ٱلْكِتَـٰبَ
]

A_VOWEL_PUT_IN_TO_REPAIR_THE_MEETING = [
    ("73:2", (1, 2), ("qumi", "llajl")),            # قُمِ ٱلَّيْلَ
    ("4:66", (5, 6), ("ʔani", "qQtulu:")),          # أَنِ ٱقْتُلُوٓا۟
    ("10:101", (1, 2), ("quli", "ŋðˤurˤu:")),       # قُلِ ٱنظُرُوا۟
    ("6:10", (1, 2),
     ("walaqaˤdi", "stuhziʔ")),                     # وَلَقَدِ ٱسْتُهْزِئَ
    ("3:35", (2, 3), ("qaˤ:lati", "mrˤaˤʔat")),     # قَالَتِ ٱمْرَأَتُ
    ("4:176", (7, 8), ("ʔini", "mrˤuʔ")),           # إِنِ ٱمْرُؤٌا۟
    ("2:16", (3, 4), ("ʔiʃtarˤaˤwu", "dˤdˤaˤla:lah")),
    # ٱشْتَرَوُا۟ ٱلضَّلَـٰلَةَ
]


def _joined(ref, words):
    first, last = words
    r = reading(Site(hafs=(ref, words)), ibtidaa=first, waqf=last)
    return r.phonemes(first), r.phonemes(last)


@pytest.mark.parametrize(("ref", "words", "expected"), A_LONG_VOWEL_GIVING_WAY)
def test_a_long_vowel_shortens_before_a_quiescent_letter(ref, words, expected):
    assert _joined(ref, words) == expected


@pytest.mark.parametrize(
    ("ref", "words", "expected"), A_VOWEL_PUT_IN_TO_REPAIR_THE_MEETING
)
def test_a_vowel_is_put_on_the_first_word_when_it_cannot_shorten(
    ref, words, expected
):
    assert _joined(ref, words) == expected
