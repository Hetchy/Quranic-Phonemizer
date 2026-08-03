from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

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

A_TANWEEN_MEETING_A_PROSTHETIC_HAMZA = [
    ("2:61", (30, 31), ("xaˤjrˤuni", "hbitˤu:")),        # خَيْرٌ ٱهْبِطُوا۟
    ("11:42", (8, 9), ("nu:ħuni", "bQnah")),             # نُوحٌ ٱبْنَهُۥ
    ("9:30", (3, 4), ("ʕuzajrˤuni", "bQn")),             # عُزَيْرٌ ٱبْنُ
    ("4:171", (31, 32), ("θala:θatuni", "ŋtahu:")),      # ثَلَـٰثَةٌ ٱنتَهُوا۟
    ("7:8", (2, 3), ("jawmaʔiðini", "lħaqqQ")),          # يَوْمَئِذٍ ٱلْحَقُّ
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


@pytest.mark.parametrize(
    ("ref", "words", "expected"), A_TANWEEN_MEETING_A_PROSTHETIC_HAMZA
)
def test_a_tanween_takes_a_linking_kasra_before_a_prosthetic_hamza(
    ref, words, expected
):
    # the engine leaves the tanween bare and joins on no vowel at all
    assert _joined(ref, words) == expected


AMILU_SSALIHAT = Site(hafs=("2:25", (4, 5)))
KAFARU_SAWAAUN = Site(hafs=("2:6", (3, 4)))


@for_each_riwayah(AMILU_SSALIHAT, ibtidaa=4, waqf=5)
def test_a_plural_waw_shortens_onto_a_word_whose_hamza_has_elided(r):
    # وَعَمِلُوا۟ ٱلصَّـٰلِحَـٰتِ
    assert r.phonemes(4) == "waʕamilu"
    assert r.phonemes(5) == "sˤsˤaˤ:liħa:t"


@for_each_riwayah(AMILU_SSALIHAT, isolated=4)
def test_that_same_plural_waw_is_long_when_it_is_stopped_on(r):
    # وَعَمِلُوا۟
    assert r.phonemes(4) == "waʕamilu:"


@for_each_riwayah(KAFARU_SAWAAUN, ibtidaa=3, waqf=4)
def test_it_keeps_its_length_onto_a_word_that_opens_on_a_vowel(r):
    # كَفَرُوا۟ سَوَآءٌ
    assert r.phonemes(3) == "kafarˤu:"
    assert r.phonemes(4) == "sawa:ʔ"
