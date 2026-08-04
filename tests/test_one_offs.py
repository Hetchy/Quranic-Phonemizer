from __future__ import annotations

from tests.support import Site, for_each_riwayah, reading

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
    assert "imala" in r.rules_on_char(6, "۪")
    assert "imala" in r.rules_on_sound(6, "i:")


@for_each_riwayah(TAMANNA, isolated=6)
def test_the_one_ishmam_in_the_corpus(r):
    # تَأْمَ۫نَّا
    assert r.phonemes(6) == "taʔmaña:"
    assert "ishmam" in r.rules_on_char(6, "۫")


@for_each_riwayah(AAJAMIYY, isolated=9)
def test_the_one_tashil_in_the_corpus(r):
    # ءَا۬عْجَمِىٌّ
    assert r.phonemes(9) == "ʔaʔaʕʒamijj"
    assert "tashil" in r.rules_on_char(9, "ا")
    assert "tashil" in r.rules_on_sound(9, "ʔ")


def test_the_easing_toggle_defaults_off():
    off = reading(AAJAMIYY, extra_phonemes=(), isolated=9)
    on = reading(AAJAMIYY, extra_phonemes=("tashil",), isolated=9)
    assert off.phonemes(9) == "ʔaʔaʕʒamijj"
    assert on.phonemes(9) == "ʔaʔ̞aʕʒamijj"


@for_each_riwayah(MAN_RAQIN, ibtidaa=2, waqf=3)
def test_a_sakt_breaks_the_reading_without_stopping_it(r):
    # مَنْ ۜ رَاقٍ
    assert r.phonemes(2) == "man"
    assert r.phonemes(3) == "rˤaˤ:qQ"
    assert "idgham_bila_ghunnah" not in r.rules_on_char(2, "ن")


@for_each_riwayah(BAL_RANA, ibtidaa=2, waqf=3)
def test_a_sakt_keeps_a_lam_clear_of_the_raa_after_it(r):
    # بَلْ ۜ رَانَ
    assert r.phonemes(2) == "bal"
    assert r.phonemes(3) == "rˤaˤ:n"
    assert "idgham_mutaqaribayn" not in r.rules_on_char(2, "ل")


@for_each_riwayah(NUNJI, isolated=7)
def test_the_one_small_noon_in_the_corpus_is_a_noon_that_is_hidden(r):
    # نُـۨجِى
    assert r.phonemes(7) == "nuŋʒi:"
    assert "ikhfaa_haqiqi" in r.rules_on_char(7, "ۨ")
    assert r.rules_on_sound(7, "ŋ") == {"ikhfaa_haqiqi"}


@for_each_riwayah(MALIYAH, ibtidaa=4, wasl=4)
def test_a_sakt_keeps_the_haa_clear_of_the_haa_after_it(r):
    # مَالِيَهْ ۜ هَلَكَ
    assert r.phonemes(4) == "ma:lijah"
    assert r.phonemes(5) == "halaka"
    assert "idgham_mutamathilayn" not in r.rules_on_char(4, "ه")
