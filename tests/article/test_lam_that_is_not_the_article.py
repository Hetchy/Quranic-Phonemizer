from __future__ import annotations

from tests.support import Site, for_each_riwayah

ILTAQA = Site(hafs=("3:155", (6,)))
ATTAQWA = Site(hafs=("7:26", (11,)))
ADHDHAKARAYN = Site(hafs=("6:143", (10,)))


@for_each_riwayah(ILTAQA, waqf=6)
def test_a_form_eight_lam_is_said_and_does_not_merge(r):
    # ٱلْتَقَى
    assert r.phonemes(6) == "ltaqaˤ:"


@for_each_riwayah(ATTAQWA, waqf=11)
def test_the_article_lam_in_the_same_shape_does_merge(r):
    # ٱلتَّقْوَىٰ
    assert r.phonemes(11) == "ttaqQwa:"


@for_each_riwayah(ADHDHAKARAYN, waqf=10)
def test_the_article_after_an_interrogative_hamza(r):
    # ءَآلذَّكَرَيْنِ
    assert r.phonemes(10) == "ʔa:ððakarˤaˤjn"
