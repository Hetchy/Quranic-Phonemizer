from __future__ import annotations

from tests.support import Site, for_each_riwayah

HUDAN_MIN_RABBIHIM = Site(hafs=("2:5", (3, 4, 5)))
FAIN_LAM = Site(hafs=("2:24", (1, 2)))
HUDAN_LILMUTTAQIN = Site(hafs=("2:2", (6, 7)))
GHAFURUN_RAHEEM = Site(hafs=("2:173", (24, 25)))
ALEEMUN = Site(hafs=("2:224", (14,)))


@for_each_riwayah(HUDAN_MIN_RABBIHIM, ibtidaa=3, waqf=5)
def test_a_quiescent_noon_merges_into_a_raa_without_a_hum(r):
    # هُدًى مِّن رَّبِّهِمْ
    assert r.phonemes(3) == "huda"
    assert r.phonemes(4) == "m̃i"
    assert r.phonemes(5) == "rˤrˤaˤbbihim"
    assert r.source_of("idgham_bila_ghunnah") == "ن"
    assert r.host_of("idgham_bila_ghunnah") == "ر"
    assert "idgham_bila_ghunnah" in r.rules_on_char(4, "ن")
    assert "idgham_bila_ghunnah" in r.rules_on_sound(5, "rˤrˤ")


@for_each_riwayah(FAIN_LAM, ibtidaa=1, waqf=2)
def test_a_quiescent_noon_merges_into_a_lam_without_a_hum(r):
    # فَإِن لَّمْ
    assert r.phonemes(1) == "faʔi"
    assert r.phonemes(2) == "llam"
    assert "idgham_bila_ghunnah" in r.rules_on_char(1, "ن")
    assert r.rules_on_sound(2, "ll") == {"idgham_bila_ghunnah"}


@for_each_riwayah(HUDAN_LILMUTTAQIN, ibtidaa=6, waqf=7)
def test_a_tanween_merges_into_a_lam_without_a_hum(r):
    # هُدًى لِّلْمُتَّقِينَ
    assert r.phonemes(6) == "huda"
    assert r.phonemes(7) == "llilmuttaqi:n"
    assert "idgham_bila_ghunnah" in r.rules_on_char(6, "ً")
    assert r.rules_on_sound(7, "ll") == {"idgham_bila_ghunnah"}


@for_each_riwayah(GHAFURUN_RAHEEM, ibtidaa=24, waqf=25)
def test_a_tanween_merges_into_a_raa_without_a_hum(r):
    # غَفُورٌ رَّحِيمٌ
    assert r.phonemes(24) == "ɣaˤfu:rˤu"
    assert r.phonemes(25) == "rˤrˤaˤħi:m"
    assert "idgham_bila_ghunnah" in r.rules_on_char(24, "ٌ")
    assert "idgham_bila_ghunnah" in r.rules_on_sound(25, "rˤrˤ")


@for_each_riwayah(FAIN_LAM, isolated=1)
def test_a_stop_after_the_noon_undoes_the_merger_into_the_lam(r):
    # فَإِن
    assert r.phonemes(1) == "faʔin"
    assert "idgham_bila_ghunnah" not in r.rules_on_char(1, "ن")


@for_each_riwayah(ALEEMUN, ibtidaa=14, wasl=14)
def test_a_tanween_at_a_verse_end_merges_into_the_next_verse(r):
    # عَلِيمٌ لَّا
    assert r.phonemes(14) == "ʕali:mu"
    assert r.phonemes(15) == "lla:"
    assert "idgham_bila_ghunnah" in r.rules_on_char(14, "ٌ")
    assert r.rules_on_sound(15, "ll") == {"idgham_bila_ghunnah"}
