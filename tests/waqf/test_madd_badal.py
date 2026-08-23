from __future__ import annotations

from tests.support import Site, for_each_riwayah

YAUDUHU = Site(hafs=("2:255", (46, 47)))
AAMMEEN = Site(hafs=("5:2", (16, 17)))
AADAMA = Site(hafs=("2:31", (2, 3)))


@for_each_riwayah(YAUDUHU, ibtidaa=46, waqf=47)
def test_a_long_vowel_on_a_hamza_is_both_badal_and_tabii(r):
    # يَـُٔودُهُۥ
    assert r.phonemes(46) == "jaʔu:duhu:"
    assert r.rules_on_char(46, "ٔ") == {"madd_badal", "madd_tabii"}


@for_each_riwayah(AADAMA, ibtidaa=2, waqf=3)
def test_the_plainest_badal_keeps_the_plain_madd_beside_it(r):
    # ءَادَمَ
    assert r.phonemes(2) == "ʔa:dama"
    assert r.rules_on_char(2, "ء") == {"madd_badal", "madd_tabii"}
    assert r.rules_on_sound(2, "a:") == {"madd_badal", "madd_tabii"}


@for_each_riwayah(AAMMEEN, ibtidaa=16, waqf=17)
def test_a_badal_before_a_permanent_sakin_keeps_the_madd_that_holds_it(r):
    """The badal names the length; the lazim names how long it is held."""
    # ءَآمِّينَ
    assert r.phonemes(16) == "ʔa:m̃i:na"
    assert r.rules_on_sound(16, "a:") == {"madd_badal", "madd_lazim"}
