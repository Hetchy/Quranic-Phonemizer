"""Reading the tokenization the source view rests on.

A scalar opens its own unit when it supplies a letter or occupies the vowel
position; every other mark folds into the unit whose fact it states.
"""
from __future__ import annotations

from quranic_phonemizer.api import alphabet as _load_alphabet
from quranic_phonemizer.api import recitation as _recitation
from quranic_phonemizer.model.address import Riwayah, Script, VariantSelection
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.phonemize import edges as ed
from quranic_phonemizer.phonemize.assemble import Assembled, assemble
from quranic_phonemizer.phonemize.session import phonemize_request

#: The facts whose presence gives a scalar a unit of its own: a letter, or a
#: haraka, sukun or length carrier holding the vowel position. A shadda's
#: ONSET and a tashil or ishmam mark are absent, so those fold.
OPENING_FACTS = frozenset({
    ed.Fact.LETTER,
    ed.Fact.VOWEL_QUALITY,
    ed.Fact.VOWEL_LENGTH,
    ed.Fact.VOWEL_ABSENCE,
})

_HAFS = Riwayah("hafs")


def _recite():
    return _recitation(_HAFS)


def _pen(script: Script):
    return pen_for(_recite().inventory(script))


def built(
    ref: str,
    *,
    script: Script = Script.UTHMANI,
    selection: VariantSelection = VariantSelection(),
    **boundary,
) -> Assembled:
    """The assembled arrays for one reference, script and boundary plan."""
    session = phonemize_request(
        _recite(), ref, script=script, selection=selection, **boundary
    )
    return assemble(session, _pen(script), _load_alphabet())


def supplies(a: Assembled, glyph: int) -> frozenset[ed.Fact]:
    """The facts this glyph supplies."""
    return frozenset(
        s.fact for s in a.spellings
        if isinstance(s, ed.Supplies) and s.glyph == glyph
    )


def units_named(a: Assembled, glyph: int) -> frozenset[int]:
    """Every unit this glyph's spelling edges name."""
    return frozenset(
        s.unit for s in a.spellings
        if getattr(s, "glyph", None) == glyph
        and getattr(s, "unit", None) is not None
    )


def opens_unit(a: Assembled, glyph: int) -> bool:
    return bool(supplies(a, glyph) & OPENING_FACTS)


def find(a: Assembled, *, char=None, kind=None, word=None) -> list[int]:
    out = []
    for i, g in enumerate(a.glyphs):
        if char is not None and g.char != char:
            continue
        if kind is not None and g.kind is not kind:
            continue
        if word is not None and g.word != word:
            continue
        out.append(i)
    return out


def only(a: Assembled, **kw) -> int:
    """The single glyph matching, so a site drift surfaces as a failure."""
    hits = find(a, **kw)
    if len(hits) != 1:
        raise AssertionError(f"expected one glyph for {kw}, got {hits}")
    return hits[0]
