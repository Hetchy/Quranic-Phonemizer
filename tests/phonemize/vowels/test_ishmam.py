"""The two kinds of authored ishmam in Hafs and Warsh.

Hafs writes the mark after the meem; Warsh supplies the same canonical fact
without that mark. The rounding belongs to the noon in both readings.
"""
from __future__ import annotations

import pytest

from quranic_phonemizer.model import performance as pf
from quranic_phonemizer.model.address import KhilafId
from quranic_phonemizer.model.canon import CanonLetter, Rule
from tests.support import (
    Expect,
    Site,
    VariantCase,
    assert_case,
    case_runs,
    for_each_riwayah,
    isolated,
)

TAMANNA = Site.shared("12:11", (6,), riwayat=("hafs", "warsh"))
SIA = Site.shared("11:77", (5,), riwayat=("warsh",))

CASES = (
    # Hafs: تَأْمَ۫نَّا
    VariantCase(
        id="tamanna-noon",
        site=Site(hafs=("12:11", (6,))),
        selector=KhilafId.TAMANNA_NOON,
        faces={
            "ishmam": Expect(read=isolated(), phonemes="t a ʔ m a ñ a:"),
            "ikhtilas": Expect(
                read=isolated(), phonemes="t a ʔ m a n u n a:"
            ),
        },
        default="ishmam",
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_tamanna_variant(run):
    assert_case(run)


def _the_ishmam(r) -> pf.Occurrence:
    found = [
        occurrence for occurrence in r.performance.occurrences
        if occurrence.rule is Rule.ISHMAM
    ]
    assert len(found) == 1
    return found[0]


@for_each_riwayah(TAMANNA, isolated=6)
def test_the_ishmam_names_one_letter_and_reads_nothing_beside_it(r):
    # Hafs: تَأْمَ۫نَّا
    # Warsh: تَامَ۬نَّا
    assert r.phonemes(6) == r.pick(hafs="taʔmaña:", warsh="ta:maña:")
    occurrence = _the_ishmam(r)
    noon = next(
        slot for slot in r.score.words[5].slots
        if slot.letter is CanonLetter.NOON
    )
    assert occurrence.subjects == (noon.id,)
    assert occurrence.context == ()
    assert occurrence.boundary is None
    assert r.source_of("ishmam") == "ن"
    assert r.host_of("ishmam") is None


@for_each_riwayah(TAMANNA, isolated=6)
def test_the_ishmam_classifies_the_consonant_and_owns_no_sound(r):
    """Its only edge is a classification, so a consumer drawing the noon can
    name the rule without the reading crediting it with the sound."""
    # Hafs: تَأْمَ۫نَّا
    # Warsh: تَامَ۬نَّا
    occurrence = _the_ishmam(r)
    assert [
        edge for edge in r.performance.attributions
        if edge.by == occurrence.id
    ] == []
    modifiers = [
        modifier for modifier in r.performance.modifiers
        if modifier.by == occurrence.id
    ]
    assert len(modifiers) == 1
    assert isinstance(modifiers[0], pf.Classifies)
    assert "ishmam" in r.rules_on_sound(6, "ñ")


@for_each_riwayah(TAMANNA, ibtidaa=6, wasl=6)
def test_the_rounding_holds_whichever_way_the_word_is_read(r):
    """It is a fact of the word, not of the junction after it."""
    # Hafs: تَأْمَ۫نَّا
    # Warsh: تَامَ۬نَّا
    assert r.phonemes(6) == r.pick(hafs="taʔmaña:", warsh="ta:maña:")
    assert "ishmam" in r.rules_on_char(6, "ن")
    assert "ishmam" not in r.rules_on_char(6, "۫")


@for_each_riwayah(SIA, ibtidaa=5, wasl=5)
def test_vowel_ishmam_preserves_the_long_i_and_real_hamza(r):
    # Warsh: س۬ےٓءَ — the initial mixed movement is mostly kasra, the yaa is
    # still long, and the following hamza remains fully pronounced.
    assert r.phonemes(5) == "si:ʔa"
    assert "ishmam" in r.rules_on_char(5, "س")
    assert "madd_muttasil" in r.rules_on_sound(5, "i:")
