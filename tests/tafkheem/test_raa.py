from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah

RABBI = Site(hafs=("1:2", (3,)))
RUZIQNA = Site(hafs=("2:25", (22,)))
RIJALUN = Site(hafs=("7:46", (5,)))
MARYAMA = Site(hafs=("2:87", (12,)))
ALARD = Site(hafs=("2:11", (7,)))
QURAN = Site(hafs=("10:61", (9,)))
FIRAWNA = Site(hafs=("2:49", (5,)))
QIRTAS = Site(hafs=("6:7", (6,)))
MIRSADA = Site(hafs=("78:21", (4,)))
FIRQATIN = Site(hafs=("9:122", (10,)))
IRJII = Site(hafs=("89:28", (1,)))
AMI_IRTABU = Site(hafs=("24:50", (4, 5)))
KHAYRUN = Site(hafs=("2:54", (17,)))
HIJRUN = Site(hafs=("6:138", (5,)))
ANNAHAR = Site(hafs=("3:27", (4,)))
QADIRUN = Site(hafs=("2:20", (25,)))
ARRAHMAN = Site(hafs=("1:1", (3,)))
MUSTAMIRRUN = Site(hafs=("54:2", (7,)))


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


@for_each_riwayah(AMI_IRTABU, isolated=5)
def test_the_same_word_started_on_keeps_its_heavy_raa(r):
    # ٱرْتَابُوٓا۟
    assert r.phonemes(5) == "ʔirˤta:bu:"


@pytest.mark.engine_bug
@for_each_riwayah(AMI_IRTABU, ibtidaa=4, waqf=5)
def test_an_incidental_kasra_before_it_leaves_the_raa_heavy(r):
    # أَمِ ٱرْتَابُوٓا۟
    # the engine reads the kasra of ami as a real one and gives rta:bu:
    assert r.phonemes(4) == "ʔami"
    assert r.phonemes(5) == "rˤta:bu:"


@for_each_riwayah(KHAYRUN, isolated=17)
def test_a_raa_after_a_quiescent_yaa_is_light(r):
    # خَيْرٌ
    assert r.phonemes(17) == "xaˤjr"


@for_each_riwayah(HIJRUN, isolated=5)
def test_a_raa_behind_a_quiescent_letter_after_a_kasra_is_light(r):
    # حِجْرٌ
    assert r.phonemes(5) == "ħiʒQr"


@for_each_riwayah(ANNAHAR, isolated=4)
def test_a_raa_stopped_on_after_an_alif_is_heavy(r):
    # ٱلنَّهَارِ
    assert r.phonemes(4) == "ʔañaha:rˤ"


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
