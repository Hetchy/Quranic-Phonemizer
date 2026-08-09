from __future__ import annotations

from tests.support import Site, for_each_riwayah

QULUBIHIM_MARADUN = Site(hafs=("2:10", (2, 3)))
AHWAAHUM = Site(hafs=("47:14", (13,)))


@for_each_riwayah(QULUBIHIM_MARADUN, ibtidaa=2, waqf=3)
def test_a_quiescent_meem_merges_into_the_meem_of_the_next_word(r):
    # قُلُوبِهِم مَّرَضٌ
    assert r.phonemes(2) == "qulu:bihi"
    assert r.phonemes(3) == "m̃arˤaˤdˤ"
    assert "idgham_shafawi" in r.rules_on_char(2, "م")
    assert r.rules_on_sound(3, "m̃") == {"idgham_shafawi"}


@for_each_riwayah(QULUBIHIM_MARADUN, isolated=2)
def test_a_stop_after_the_meem_undoes_the_merger(r):
    # قُلُوبِهِم
    assert r.phonemes(2) == "qulu:bihim"
    assert "idgham_shafawi" not in r.rules_on_char(2, "م")


@for_each_riwayah(AHWAAHUM, ibtidaa=13, wasl=13)
def test_a_meem_at_a_verse_end_merges_into_the_next_verse(r):
    # أَهْوَآءَهُم مَّثَلُ
    assert r.phonemes(13) == "ʔahwa:ʔahu"
    assert r.phonemes(14) == "m̃aθalu"
    assert "idgham_shafawi" in r.rules_on_char(13, "م")
    assert r.rules_on_sound(14, "m̃") == {"idgham_shafawi"}
