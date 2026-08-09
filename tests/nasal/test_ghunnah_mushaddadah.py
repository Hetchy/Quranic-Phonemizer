from __future__ import annotations

from tests.support import Site, for_each_riwayah

WAMIMMA = Site(hafs=("2:3", (6,)))
ANNAAS = Site(hafs=("2:8", (2,)))
ALMAGHDUB = Site(hafs=("1:7", (6,)))


@for_each_riwayah(WAMIMMA, isolated=6)
def test_a_doubled_meem_is_held_through_the_nose(r):
    # وَمِمَّا
    assert r.phonemes(6) == "wamim̃a:"
    assert "ghunnah_mushaddadah" in r.rules_on_char(6, "م")
    assert r.rules_on_sound(6, "m̃") == {"ghunnah_mushaddadah"}


@for_each_riwayah(ANNAAS, isolated=2)
def test_a_noon_the_article_doubles_is_held_the_same_way(r):
    """ٱلنَّاسِ. The doubling is the article's merger and not canonical, so
    `lam_shamsiyyah` produces the sound and the ghunnah only names it."""
    assert r.phonemes(2) == "ʔaña:s"
    assert "ghunnah_mushaddadah" in r.rules_on_char(2, "ن")
    assert "lam_shamsiyyah" in r.rules_on_char(2, "ل")


@for_each_riwayah(ALMAGHDUB, isolated=6)
def test_a_meem_behind_a_pronounced_article_lam_is_not_doubled_at_all(r):
    # ٱلْمَغْضُوبِ -- a moon letter, so the lam stands and nothing merges.
    assert "ghunnah_mushaddadah" not in r.rules_on_char(6, "م")
    assert "lam_qamariyyah" in r.rules_on_char(6, "ل")
