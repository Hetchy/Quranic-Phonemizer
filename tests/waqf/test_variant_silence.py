from __future__ import annotations

from tests.support import Site, for_each_riwayah

AATANI = Site(hafs=("27:36", (8,)))


@for_each_riwayah(AATANI, isolated=8)
def test_the_pronoun_yaa_the_stop_omits_names_a_variant_silence(r):
    # ءَاتَىٰنِۧ -- the default hadhf leaves the written yaa unsaid at a stop
    assert r.phonemes(8) == "ʔa:ta:n"
    assert "variant_silence" in r.rules_on_char(8, "ۧ")


@for_each_riwayah(AATANI, wasl=8)
def test_the_joined_pronoun_yaa_is_said_and_names_no_silence(r):
    # ءَاتَىٰنِۧ
    assert r.phonemes(8) == "ʔa:ta:nija"
    assert "variant_silence" not in r.rules_on_char(8, "ۧ")
