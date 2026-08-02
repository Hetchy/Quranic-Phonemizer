from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

VOWELLED = [
    ("1:2", 3, "rˤaˤbbQ"),        # رَبِّ
    ("2:25", 22, "rˤuziqQna:"),   # رُزِقْنَا
    ("7:46", 5, "riʒa:l"),        # رِجَالٌ
]

SAKINAH = [
    ("2:87", 12, "marˤjam"),      # مَرْيَمَ
    ("2:11", 7, "ʔalʔarˤdˤ"),     # ٱلْأَرْضِ
    ("10:61", 9, "qurˤʔa:n"),     # قُرْءَانٍ
    ("2:49", 5, "firʕawn"),       # فِرْعَوْنَ
    ("11:17", 29, "mirjah"),      # مِرْيَةٍ
]

ISTILAA_AFTER = [
    ("6:7", 6, "qirˤtˤaˤ:s"),     # قِرْطَاسٍ
    ("78:21", 4, "mirˤsˤaˤ:da:"),  # مِرْصَادًا
    ("9:122", 10, "firˤqaˤh"),    # فِرْقَةٍ
]

RABBI = Site(hafs=("1:2", (3,)))
RUZIQNA = Site(hafs=("2:25", (22,)))
RIJALUN = Site(hafs=("7:46", (5,)))
MARYAMA = Site(hafs=("2:87", (12,)))
ALARD = Site(hafs=("2:11", (7,)))
QURAN = Site(hafs=("10:61", (9,)))
FIRAWNA = Site(hafs=("2:49", (5,)))
MIRYATIN = Site(hafs=("11:17", (29,)))
QIRTAS = Site(hafs=("6:7", (6,)))
MIRSADA = Site(hafs=("78:21", (4,)))
FIRQATIN = Site(hafs=("9:122", (10,)))
IRJII = Site(hafs=("89:28", (1,)))
IRJIUU = Site(hafs=("12:81", (1,)))
IRKAUU = Site(hafs=("22:77", (4,)))
AMI_IRTABU = Site(hafs=("24:50", (4, 5)))
KHAYRUN = Site(hafs=("2:54", (17,)))
GHAYRI = Site(hafs=("1:7", (5,)))
HIJRUN = Site(hafs=("6:138", (5,)))
SIHRUN = Site(hafs=("5:110", (62,)))
ANNAHAR = Site(hafs=("3:27", (4,)))
ANNARA = Site(hafs=("2:24", (7,)))
QADIRUN = Site(hafs=("2:20", (25,)))
ARRAHMAN = Site(hafs=("1:1", (3,)))
MUSTAMIRRUN = Site(hafs=("54:2", (7,)))


@pytest.mark.parametrize(("ref", "word", "expected"), VOWELLED)
def test_a_vowelled_raa_follows_its_own_vowel(ref, word, expected):
    site = Site(hafs=(ref, (word,)))
    assert reading(site, isolated=word).phonemes(word) == expected


@pytest.mark.parametrize(("ref", "word", "expected"), SAKINAH)
def test_a_quiescent_raa_follows_the_vowel_before_it(ref, word, expected):
    site = Site(hafs=(ref, (word,)))
    assert reading(site, isolated=word).phonemes(word) == expected


@pytest.mark.parametrize(("ref", "word", "expected"), ISTILAA_AFTER)
def test_an_istilaa_letter_behind_it_pulls_the_raa_heavy(
    ref, word, expected
):
    site = Site(hafs=(ref, (word,)))
    assert reading(site, isolated=word).phonemes(word) == expected


@for_each_riwayah(RABBI, isolated=3)
def test_a_raa_with_a_fatha_is_heavy(r):
    # رَبِّ
    assert r.phonemes(3) == "rˤaˤbbQ"


@for_each_riwayah(RUZIQNA, isolated=22)
def test_a_raa_with_a_damma_is_heavy(r):
    # رُزِقْنَا
    assert r.phonemes(22) == "rˤuziqQna:"


@for_each_riwayah(RIJALUN, isolated=5)
def test_a_raa_with_a_kasra_is_light(r):
    # رِجَالٌ
    assert r.phonemes(5) == "riʒa:l"


@for_each_riwayah(MARYAMA, isolated=12)
def test_a_quiescent_raa_after_a_fatha_is_heavy(r):
    # مَرْيَمَ
    assert r.phonemes(12) == "marˤjam"


@for_each_riwayah(ALARD, isolated=7)
def test_a_quiescent_raa_before_a_daad_is_heavy(r):
    # ٱلْأَرْضِ
    assert r.phonemes(7) == "ʔalʔarˤdˤ"


@for_each_riwayah(QURAN, isolated=9)
def test_a_quiescent_raa_after_a_damma_is_heavy(r):
    # قُرْءَانٍ
    assert r.phonemes(9) == "qurˤʔa:n"


@for_each_riwayah(FIRAWNA, isolated=5)
def test_a_quiescent_raa_after_a_kasra_is_light(r):
    # فِرْعَوْنَ
    assert r.phonemes(5) == "firʕawn"


@for_each_riwayah(MIRYATIN, isolated=29)
def test_another_quiescent_raa_after_a_kasra_is_light(r):
    # مِرْيَةٍ
    assert r.phonemes(29) == "mirjah"


@for_each_riwayah(QIRTAS, isolated=6)
def test_a_taa_after_the_raa_outweighs_the_kasra_before_it(r):
    # قِرْطَاسٍ
    assert r.phonemes(6) == "qirˤtˤaˤ:s"


@for_each_riwayah(MIRSADA, isolated=4)
def test_a_sad_after_the_raa_outweighs_the_kasra_before_it(r):
    # مِرْصَادًا
    assert r.phonemes(4) == "mirˤsˤaˤ:da:"


@for_each_riwayah(FIRQATIN, isolated=10)
def test_a_qaf_after_the_raa_outweighs_the_kasra_before_it(r):
    # فِرْقَةٍ
    assert r.phonemes(10) == "firˤqaˤh"


@for_each_riwayah(IRJII, isolated=1)
def test_a_raa_after_a_prosthetic_kasra_is_heavy(r):
    # ٱرْجِعِىٓ
    assert r.phonemes(1) == "ʔirˤʒiʕi:"


@for_each_riwayah(IRJIUU, isolated=1)
def test_another_raa_after_a_prosthetic_kasra_is_heavy(r):
    # ٱرْجِعُوٓا۟
    assert r.phonemes(1) == "ʔirˤʒiʕu:"


@for_each_riwayah(IRKAUU, isolated=4)
def test_a_third_raa_after_a_prosthetic_kasra_is_heavy(r):
    # ٱرْكَعُوا۟
    assert r.phonemes(4) == "ʔirˤkaʕu:"


@for_each_riwayah(AMI_IRTABU, isolated=5)
def test_the_same_word_started_on_keeps_its_heavy_raa(r):
    # ٱرْتَابُوٓا۟
    assert r.phonemes(5) == "ʔirˤta:bu:"


@for_each_riwayah(AMI_IRTABU, ibtidaa=4, waqf=5)
def test_joining_ami_onto_it_reports_the_raa_as_light(r):
    # أَمِ ٱرْتَابُوٓا۟
    assert r.phonemes(5) == "rta:bu:"


@for_each_riwayah(KHAYRUN, isolated=17)
def test_a_raa_after_a_quiescent_yaa_is_light(r):
    # خَيْرٌ
    assert r.phonemes(17) == "xaˤjr"


@for_each_riwayah(GHAYRI, isolated=5)
def test_another_raa_after_a_quiescent_yaa_is_light(r):
    # غَيْرِ
    assert r.phonemes(5) == "ɣaˤjr"


@for_each_riwayah(HIJRUN, isolated=5)
def test_a_raa_behind_a_quiescent_letter_after_a_kasra_is_light(r):
    # حِجْرٌ
    assert r.phonemes(5) == "ħiʒQr"


@for_each_riwayah(SIHRUN, isolated=62)
def test_another_raa_behind_such_a_quiescent_letter_is_light(r):
    # سِحْرٌ
    assert r.phonemes(62) == "siħr"


@for_each_riwayah(ANNAHAR, isolated=4)
def test_a_raa_stopped_on_after_an_alif_is_heavy(r):
    # ٱلنَّهَارِ
    assert r.phonemes(4) == "ʔañaha:rˤ"


@for_each_riwayah(ANNARA, isolated=7)
def test_another_raa_stopped_on_after_an_alif_is_heavy(r):
    # ٱلنَّارَ
    assert r.phonemes(7) == "ʔaña:rˤ"


@for_each_riwayah(QADIRUN, isolated=25)
def test_a_raa_stopped_on_after_a_long_yaa_is_light(r):
    # قَدِيرٌ
    assert r.phonemes(25) == "qaˤdi:r"


@for_each_riwayah(ARRAHMAN, isolated=3)
def test_a_doubled_raa_with_a_fatha_is_heavy(r):
    # ٱلرَّحْمَـٰنِ
    assert r.phonemes(3) == "ʔarˤrˤaˤħma:n"


@for_each_riwayah(MUSTAMIRRUN, isolated=7)
def test_a_doubled_raa_stopped_on_after_a_kasra_is_light(r):
    # مُّسْتَمِرٌّ
    assert r.phonemes(7) == "mustamirr"
