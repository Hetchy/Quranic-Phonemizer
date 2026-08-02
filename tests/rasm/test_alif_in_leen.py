from __future__ import annotations

from tests.support import Site, for_each_riwayah

TAYASU = Site(hafs=("12:87", (8,)))
YAYASU = Site(hafs=("12:87", (13, 14)))
YAYASI = Site(hafs=("13:31", (20,)))


@for_each_riwayah(TAYASU, isolated=8)
def test_a_bare_alif_inside_a_leen_needs_neither_carrier_nor_hamza(r):
    # تَا۟يْـَٔسُوا۟
    assert r.phonemes(8) == "tajʔasu:"


@for_each_riwayah(YAYASU, ibtidaa=13, waqf=14)
def test_the_same_alif_in_the_third_person_of_that_verb(r):
    # لَا يَا۟يْـَٔسُ
    assert r.phonemes(13) == "la:"
    assert r.phonemes(14) == "jajʔas"


@for_each_riwayah(YAYASI, isolated=20)
def test_the_same_alif_where_the_verb_ends_in_a_kasra(r):
    # يَا۟يْـَٔسِ
    assert r.phonemes(20) == "jajʔas"
