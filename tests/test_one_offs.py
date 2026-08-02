from __future__ import annotations

from tests.support import Site, for_each_riwayah

MAJRAHA = Site(hafs=("11:41", (6,)))
TAMANNA = Site(hafs=("12:11", (6,)))
AAJAMIYY = Site(hafs=("41:44", (9,)))
MAN = Site(hafs=("75:27", (2,)))


@for_each_riwayah(MAJRAHA, waqf=6)
def test_the_one_imala_in_the_corpus(r):
    # مَجْر۪ىٰهَا
    assert r.phonemes(6) == "maʒQri:ha:"


@for_each_riwayah(TAMANNA, waqf=6)
def test_the_one_ishmam_in_the_corpus(r):
    # تَأْمَ۫نَّا
    assert r.phonemes(6) == "taʔmaña:"


@for_each_riwayah(AAJAMIYY, waqf=9)
def test_the_one_tashil_in_the_corpus(r):
    # ءَا۬عْجَمِىٌّ
    assert r.phonemes(9) == "ʔaʔaʕʒamijj"


@for_each_riwayah(MAN, waqf=2)
def test_a_sakt_breaks_the_reading_without_stopping_it(r):
    # مَنْ ۜ
    assert r.phonemes(2) == "man"
