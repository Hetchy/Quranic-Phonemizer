from __future__ import annotations

from tests.support import Site, for_each_riwayah

ALLAHU = Site(hafs=("2:15", (1,)))
QALA_ALLAHU = Site(hafs=("5:119", (1, 2)))
NASRU_ALLAHI = Site(hafs=("110:1", (3, 4)))
WALLAHU = Site(hafs=("2:19", (17,)))
TALLAHI = Site(hafs=("12:73", (2,)))
BISMI_ALLAHI = Site(hafs=("1:1", (1, 2)))
LILLAHI = Site(hafs=("1:2", (2,)))
BILLAHI = Site(hafs=("2:8", (6,)))
WALILLAHI = Site(hafs=("2:115", (1,)))
LAALLAKUM = Site(hafs=("2:21", (10,)))
ALALAMIN = Site(hafs=("1:2", (4,)))


@for_each_riwayah(ALLAHU, isolated=1)
def test_the_divine_name_started_on_is_heavy(r):
    # ٱللَّهُ
    assert r.phonemes(1) == "ʔalˤlˤaˤ:h"


@for_each_riwayah(QALA_ALLAHU, ibtidaa=1, waqf=2)
def test_the_divine_name_after_a_fatha_is_heavy(r):
    # قَالَ ٱللَّهُ
    assert r.phonemes(2) == "lˤlˤaˤ:h"


@for_each_riwayah(NASRU_ALLAHI, ibtidaa=3, waqf=4)
def test_the_divine_name_after_a_damma_is_heavy(r):
    # نَصْرُ ٱللَّهِ
    assert r.phonemes(4) == "lˤlˤaˤ:h"


@for_each_riwayah(WALLAHU, isolated=17)
def test_the_divine_name_behind_a_waw_of_fatha_is_heavy(r):
    # وَٱللَّهُ
    assert r.phonemes(17) == "walˤlˤaˤ:h"


@for_each_riwayah(TALLAHI, isolated=2)
def test_the_divine_name_behind_an_oath_taa_is_heavy(r):
    # تَٱللَّهِ
    assert r.phonemes(2) == "talˤlˤaˤ:h"


@for_each_riwayah(BISMI_ALLAHI, ibtidaa=1, waqf=2)
def test_the_divine_name_joined_after_a_kasra_is_light(r):
    # بِسْمِ ٱللَّهِ
    assert r.phonemes(2) == "lla:h"


@for_each_riwayah(BISMI_ALLAHI, isolated=2)
def test_the_very_same_word_started_on_is_heavy_instead(r):
    # ٱللَّهِ
    assert r.phonemes(2) == "ʔalˤlˤaˤ:h"


@for_each_riwayah(LILLAHI, isolated=2)
def test_the_divine_name_behind_a_lam_of_kasra_is_light(r):
    # لِلَّهِ
    assert r.phonemes(2) == "lilla:h"


@for_each_riwayah(BILLAHI, isolated=6)
def test_the_divine_name_behind_a_baa_of_kasra_is_light(r):
    # بِٱللَّهِ
    assert r.phonemes(6) == "billa:h"


@for_each_riwayah(WALILLAHI, isolated=1)
def test_a_waw_before_the_kasra_does_not_make_it_heavy(r):
    # وَلِلَّهِ
    assert r.phonemes(1) == "walilla:h"


@for_each_riwayah(LAALLAKUM, isolated=10)
def test_an_ordinary_doubled_lam_after_a_fatha_stays_light(r):
    # لَعَلَّكُمْ
    assert r.phonemes(10) == "laʕallakum"


@for_each_riwayah(ALALAMIN, isolated=4)
def test_an_ordinary_lam_of_the_article_stays_light(r):
    # ٱلْعَـٰلَمِينَ
    assert r.phonemes(4) == "ʔalʕa:lami:n"
