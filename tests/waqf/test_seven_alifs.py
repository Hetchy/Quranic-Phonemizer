from __future__ import annotations

from tests.support import Site, for_each_riwayah

QAWARIRA = Site(hafs=("76:15", (8,)))
QAWARIRA_SECOND = Site(hafs=("76:16", (1,)))
SALASILA = Site(hafs=("76:4", (4,)))
DHUNUNA = Site(hafs=("33:10", (16,)))
RASULA = Site(hafs=("33:66", (11,)))
SABILA = Site(hafs=("33:67", (8,)))
ANA = Site(hafs=("2:258", (21,)))
ANA_AGAIN = Site(hafs=("18:39", (15,)))
LAKINNA = Site(hafs=("18:38", (1,)))


@for_each_riwayah(QAWARIRA, isolated=8)
def test_the_pausal_alif_of_qawarira_is_long_when_stopped_on(r):
    # قَوَارِيرَا۠
    assert r.phonemes(8) == "qaˤwa:ri:rˤaˤ:"
    assert r.silent(8) == frozenset()


@for_each_riwayah(QAWARIRA_SECOND, ibtidaa=1, wasl=1)
def test_the_second_qawarira_keeps_its_fatha_when_joined_forward(r):
    # قَوَارِيرَا۟
    assert r.phonemes(1) == "qaˤwa:ri:rˤaˤ"
    assert r.silent(1) == frozenset()


@for_each_riwayah(QAWARIRA_SECOND, isolated=1)
def test_the_second_qawarira_drops_that_alif_at_a_stop(r):
    # قَوَارِيرَا۟
    assert r.phonemes(1) == "qaˤwa:ri:r"
    assert r.silent(1) == {"َ", "ا", "۟"}


@for_each_riwayah(SALASILA, ibtidaa=4, wasl=4)
def test_salasila_keeps_a_short_fatha_when_the_reading_carries_on(r):
    # سَلَـٰسِلَا۟
    assert r.phonemes(4) == "sala:sila"
    assert r.silent(4) == frozenset()


@for_each_riwayah(SALASILA, isolated=4)
def test_salasila_is_stopped_on_without_sounding_its_alif(r):
    # سَلَـٰسِلَا۟
    assert r.phonemes(4) == "sala:sil"
    assert r.silent(4) == {"َ", "ا", "۟"}


@for_each_riwayah(DHUNUNA, isolated=16)
def test_the_pausal_alif_of_adh_dhununa_is_long_when_stopped_on(r):
    # ٱلظُّنُونَا۠
    assert r.phonemes(16) == "ʔaðˤðˤunu:na:"
    assert r.silent(16) == frozenset()


@for_each_riwayah(RASULA, isolated=11)
def test_the_pausal_alif_of_ar_rasula_is_long_when_stopped_on(r):
    # ٱلرَّسُولَا۠
    assert r.phonemes(11) == "ʔarˤrˤaˤsu:la:"
    assert r.silent(11) == frozenset()


@for_each_riwayah(SABILA, isolated=8)
def test_the_pausal_alif_of_as_sabila_is_long_when_stopped_on(r):
    # ٱلسَّبِيلَا۠
    assert r.phonemes(8) == "ʔassabi:la:"
    assert r.silent(8) == frozenset()


@for_each_riwayah(ANA, isolated=21)
def test_ana_is_long_when_stopped_on(r):
    # أَنَا۠
    assert r.phonemes(21) == "ʔana:"
    assert r.silent(21) == frozenset()


@for_each_riwayah(ANA, ibtidaa=21, wasl=21)
def test_ana_is_read_long_when_joined_forward_as_well(r):
    # أَنَا۠
    assert r.phonemes(21) == "ʔana:"
    assert r.silent(21) == frozenset()


@for_each_riwayah(ANA_AGAIN, isolated=15)
def test_a_second_ana_is_long_when_stopped_on(r):
    # أَنَا۠
    assert r.phonemes(15) == "ʔana:"


@for_each_riwayah(ANA_AGAIN, ibtidaa=15, wasl=15)
def test_a_second_ana_is_read_long_when_joined_forward_as_well(r):
    # أَنَا۠
    assert r.phonemes(15) == "ʔana:"


@for_each_riwayah(LAKINNA, isolated=1)
def test_lakinna_is_long_when_stopped_on(r):
    # لَّـٰكِنَّا۠
    assert r.phonemes(1) == "la:kiña:"
    assert r.silent(1) == frozenset()


@for_each_riwayah(LAKINNA, ibtidaa=1, wasl=1)
def test_lakinna_is_read_long_when_joined_forward_as_well(r):
    # لَّـٰكِنَّا۠
    assert r.phonemes(1) == "la:kiña:"
    assert r.silent(1) == frozenset()
