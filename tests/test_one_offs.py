from __future__ import annotations

from tests.support import Site, for_each_riwayah

MAJRAHA = Site(hafs=("11:41", (6,)))
TAMANNA = Site(hafs=("12:11", (6,)))
AAJAMIYY = Site(hafs=("41:44", (9,)))
MAN_RAQIN = Site(hafs=("75:27", (2, 3)))
BAL_RANA = Site(hafs=("83:14", (2, 3)))
NUNJI = Site(hafs=("21:88", (7,)))
MALIYAH = Site(hafs=("69:28", (4,)))


@for_each_riwayah(MAJRAHA, isolated=6)
def test_the_one_imala_in_the_corpus(r):
    # مَجْر۪ىٰهَا
    assert r.phonemes(6) == "maʒQri:ha:"


@for_each_riwayah(TAMANNA, isolated=6)
def test_the_one_ishmam_in_the_corpus(r):
    # تَأْمَ۫نَّا
    assert r.phonemes(6) == "taʔmaña:"


@for_each_riwayah(AAJAMIYY, isolated=9)
def test_the_one_tashil_in_the_corpus(r):
    # ءَا۬عْجَمِىٌّ
    assert r.phonemes(9) == "ʔaʔaʕʒamijj"


@for_each_riwayah(MAN_RAQIN, ibtidaa=2, waqf=3)
def test_a_sakt_breaks_the_reading_without_stopping_it(r):
    # مَنْ ۜ رَاقٍ
    # the engine ignores the sakt and merges the noon into the raa
    assert r.phonemes(2) == "man"
    assert r.phonemes(3) == "rˤaˤ:qQ"


@for_each_riwayah(BAL_RANA, ibtidaa=2, waqf=3)
def test_a_sakt_keeps_a_lam_clear_of_the_raa_after_it(r):
    # بَلْ ۜ رَانَ
    # the engine ignores the sakt and merges the lam into the raa
    assert r.phonemes(2) == "bal"
    assert r.phonemes(3) == "rˤaˤ:n"


@for_each_riwayah(NUNJI, isolated=7)
def test_the_one_small_noon_in_the_corpus_is_a_noon_that_is_hidden(r):
    # نُـۨجِى
    assert r.phonemes(7) == "nuŋʒi:"


@for_each_riwayah(MALIYAH, ibtidaa=4, wasl=4)
def test_a_sakt_keeps_the_haa_clear_of_the_haa_after_it(r):
    # مَالِيَهْ ۜ هَلَكَ
    # the engine merges the two haa as though nothing stood between them
    assert r.phonemes(4) == "ma:lijah"
    assert r.phonemes(5) == "halaka"
