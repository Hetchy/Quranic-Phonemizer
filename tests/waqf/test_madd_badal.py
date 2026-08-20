from __future__ import annotations

from tests.support import Site, for_each_riwayah

YAUDUHU = Site(hafs=("2:255", (46, 47)))
AAMMEEN = Site(hafs=("5:2", (16, 17)))


@for_each_riwayah(YAUDUHU, ibtidaa=46, waqf=47)
def test_a_long_vowel_on_a_hamza_is_a_badal_and_not_a_plain_madd(r):
    """The two are one outcome under two names, so only the badal fires."""
    # يَـُٔودُهُۥ
    assert r.phonemes(46) == "jaʔu:duhu:"
    assert r.rules_on_sound(46, "u:") == {"madd_badal", "madd_silah",
                                          "madd_tabii"}
    assert "madd_badal" in r.rules_on_char(46, "ٔ")


@for_each_riwayah(AAMMEEN, ibtidaa=16, waqf=17)
def test_a_badal_before_a_permanent_sakin_keeps_the_madd_that_holds_it(r):
    """The badal names the length; the lazim names how long it is held."""
    # ءَآمِّينَ
    assert r.phonemes(16) == "ʔa:m̃i:na"
    assert r.rules_on_sound(16, "a:") == {"madd_badal", "madd_lazim"}
