from __future__ import annotations

from tests.support import Site, for_each_riwayah

KHALAQU = Site(hafs=("46:4", (10,)))
QALU = Site(hafs=("2:11", (8,)))
KHALAW = Site(hafs=("2:14", (8,)))
ISHTARAWU = Site(hafs=("2:16", (3,)))
MIATA = Site(hafs=("2:259", (19,)))
ARRIBA = Site(hafs=("2:275", (20,)))


@for_each_riwayah(KHALAQU, ibtidaa=10, waqf=10)
def test_the_alif_after_a_plural_waw_is_never_said(r):
    # خَلَقُوا۟
    assert r.phonemes(10) == "xaˤlaqu:"


@for_each_riwayah(QALU, ibtidaa=8, waqf=8)
def test_the_same_alif_behind_a_plural_waw_that_carries_a_madd(r):
    # قَالُوٓا۟
    assert r.phonemes(8) == "qaˤ:lu:"


@for_each_riwayah(KHALAW, ibtidaa=8, waqf=8)
def test_the_same_alif_behind_a_plural_waw_read_as_a_leen(r):
    # خَلَوْا۟
    assert r.phonemes(8) == "xaˤlaw"


@for_each_riwayah(ISHTARAWU, ibtidaa=3, waqf=3)
def test_the_same_alif_behind_a_plural_waw_given_a_damma(r):
    # ٱشْتَرَوُا۟
    assert r.phonemes(3) == "ʔiʃtarˤaˤw"
    assert r.silent(3) == {"ا", "ُ", "۟"}


@for_each_riwayah(MIATA, ibtidaa=19, waqf=19)
def test_an_alif_written_inside_a_word_and_never_said(r):
    # مِا۟ئَةَ
    assert r.phonemes(19) == "miʔah"


@for_each_riwayah(ARRIBA, ibtidaa=20, waqf=20)
def test_a_final_alif_that_adds_nothing_to_a_length_already_written(r):
    # ٱلرِّبَوٰا۟
    assert r.phonemes(20) == "ʔarriba:"
