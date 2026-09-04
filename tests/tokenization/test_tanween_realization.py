"""Iqlab and the open tanween are facts about a unit and an occurrence. The
result states neither a stacked-or-open glyph nor a written iqlab meem."""
from __future__ import annotations

from quranic_phonemizer.model.canon import Rule
from quranic_phonemizer.phonemize import edges as ed
from quranic_phonemizer.phonemize import nodes as nd

from .support import built, find, only, supplies

IQLAB = "2:10:9-2:10:10"        # أَلِيمٌ بِمَا
IZHAR = "2:7:11-2:7:12"         # عَذَابٌ عَظِيمٌ, tanween drawn stacked
IKHFAA = "2:20:24-2:20:25"      # شَىْءٍ قَدِيرٌ, tanween drawn open

# The scalar a mushaf may set beside the noon for iqlab; QPC Hafs writes none.
IQLAB_MEEM = "ۢ"

TANWEEN_FACTS = frozenset({
    ed.Fact.VOWEL_QUALITY, ed.Fact.LETTER, ed.Fact.VOWEL_ABSENCE
})


def _nunation_unit(a):
    """The unit the first word's tanween adds by supplying its own letter."""
    tanween = only(a, kind=nd.GlyphKind.TANWEEN, word=0)
    (unit,) = [
        s.unit for s in a.spellings
        if isinstance(s, ed.Supplies) and s.glyph == tanween
        and s.fact is ed.Fact.LETTER
    ]
    return tanween, unit


def _rule_on(a, unit):
    return {ri.rule for ri in a.rules if ri.source == unit or ri.host == unit}


def test_iqlab_is_an_occurrence_on_the_tanween_with_no_written_meem():
    a = built(IQLAB)
    _, unit = _nunation_unit(a)
    assert Rule.IQLAB in _rule_on(a, unit)
    assert not find(a, char=IQLAB_MEEM)


def test_the_tanween_scalar_is_unchanged_between_stacked_and_open_readings():
    """The only difference an open drawing would carry is the occurrence; the
    tanween glyph and its facts are the same under izhar and under ikhfaa."""
    stacked = built(IZHAR)
    opened = built(IKHFAA)
    st_glyph, st_unit = _nunation_unit(stacked)
    op_glyph, op_unit = _nunation_unit(opened)
    assert stacked.glyphs[st_glyph].kind is nd.GlyphKind.TANWEEN
    assert opened.glyphs[op_glyph].kind is nd.GlyphKind.TANWEEN
    assert supplies(stacked, st_glyph) == supplies(opened, op_glyph) == TANWEEN_FACTS
    # The reading differs only in the rule placed on the unit.
    assert Rule.IZHAR in _rule_on(stacked, st_unit)
    assert Rule.IKHFAA in _rule_on(opened, op_unit)
