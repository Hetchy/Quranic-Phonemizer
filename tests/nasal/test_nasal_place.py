from __future__ import annotations

import pytest

from tests.support import KhilafId, Option, Site, VariantSelection, reading

IQLAB = KhilafId.IQLAB_NASAL
SHAFAWI = KhilafId.IKHFAA_SHAFAWI_NASAL

#: Both readings of the two bilabial hidings are taught. The hum with no place
#: is what a reciter who does not close the lips produces; the bilabial one is
#: the phonetic description of closing them. Neither point names a site, so a
#: selection carries the point alone.
SITES = [
    (IQLAB, "2:56", (3, 4), 3, "miŋ", "mim̃"),          # مِّن بَعْدِ
    (IQLAB, "2:18", (1, 2), 1, "sˤum̃uŋ", "sˤum̃um̃"),    # صُمٌّ بُكْمٌ
    (SHAFAWI, "2:8", (10, 11), 10, "huŋ", "hum̃"),      # هُم بِمُؤْمِنِينَ
]

COLUMNS = ("khilaf", "ref", "words", "word", "assimilated", "bilabial")


def _read(ref, words, word, selection):
    first, last = words
    site = Site(hafs=(ref, words))
    r = reading(site, selection=selection, ibtidaa=first, waqf=last)
    return r.phonemes(word)


@pytest.mark.parametrize(COLUMNS, SITES)
def test_the_hum_takes_no_place_unless_one_is_asked_for(
    khilaf, ref, words, word, assimilated, bilabial
):
    assert _read(ref, words, word, VariantSelection()) == assimilated


@pytest.mark.parametrize(COLUMNS, SITES)
def test_both_wajh_are_reachable(
    khilaf, ref, words, word, assimilated, bilabial
):
    picked = VariantSelection((Option(khilaf, "assimilated"),))
    assert _read(ref, words, word, picked) == assimilated
    picked = VariantSelection((Option(khilaf, "bilabial"),))
    assert _read(ref, words, word, picked) == bilabial


def test_choosing_one_point_leaves_the_other_alone():
    picked = VariantSelection((Option(IQLAB, "bilabial"),))
    assert _read("2:8", (10, 11), 10, picked) == "huŋ"
    picked = VariantSelection((Option(SHAFAWI, "bilabial"),))
    assert _read("2:56", (3, 4), 3, picked) == "miŋ"
