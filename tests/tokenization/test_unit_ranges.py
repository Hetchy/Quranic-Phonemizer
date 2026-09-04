"""A main unit can span more than one scalar range, and a riding mark states
the carrier it sits on rather than borrowing the scalar beside it."""
from __future__ import annotations

from quranic_phonemizer.phonemize import edges as ed

from .support import built, only, opens_unit, supplies, units_named

TUURI = "52:1:1"        # a haraka written between a letter and its shadda
ILAAHA = "2:255:3"      # a dagger riding across a seat onto the lam


def _unit_of_letter(a, glyph):
    (unit,) = [
        s.unit for s in a.spellings
        if isinstance(s, ed.Supplies) and s.glyph == glyph
        and s.fact is ed.Fact.LETTER
    ]
    return unit


def test_a_letter_and_its_shadda_straddle_an_independent_haraka():
    """The taa's letter and its gemination name one unit, but the damma
    between them holds the vowel position, so its scalars are not contiguous."""
    # وَٱلطُّورِ
    a = built(TUURI)
    base = only(a, char="ط", word=0)
    haraka = only(a, char="ُ", word=0)
    shadda = only(a, char="ّ", word=0)
    assert base < haraka < shadda
    unit = _unit_of_letter(a, base)
    assert unit in units_named(a, shadda)
    assert not opens_unit(a, shadda)
    assert opens_unit(a, haraka)


def test_a_riding_dagger_names_its_carrier_not_the_seat_beside_it():
    """A tatweel sits between the lam's haraka and its dagger. The dagger
    names the lam's unit; the seat it rides opens no unit to attach to."""
    # إِلَـٰهَ
    a = built(ILAAHA)
    lam = only(a, char="ل", word=0)
    tatweel = only(a, char="ـ", word=0)
    dagger = only(a, char="ٰ", word=0)
    lam_unit = _unit_of_letter(a, lam)
    assert tatweel < dagger
    assert units_named(a, dagger) == {lam_unit}
    assert not opens_unit(a, tatweel)
    assert ed.Fact.LETTER not in supplies(a, tatweel)


def test_a_riding_haraka_names_the_unit_it_sits_on():
    # إِلَـٰهَ
    a = built(ILAAHA)
    lam_unit = _unit_of_letter(a, only(a, char="ل", word=0))
    riders = [
        s.glyph for s in a.spellings
        if isinstance(s, ed.Supplies) and s.unit == lam_unit
        and s.fact is ed.Fact.VOWEL_QUALITY
    ]
    assert len(riders) == 1
    assert a.glyphs[riders[0]].char == "َ"
