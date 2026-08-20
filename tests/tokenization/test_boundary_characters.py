"""Stop signs, separators and the sakt belong to the boundary, not to a word
letter unit."""
from __future__ import annotations

from quranic_phonemizer.phonemize import edges as ed
from quranic_phonemizer.phonemize import nodes as nd

from .support import built, find, only, opens_unit, units_named

KURSI = "2:255"
SAKT = "75:27"           # an authored sakt after the second word


def _structural(a, glyph):
    return any(
        isinstance(s, ed.Structural) and s.glyph == glyph for s in a.spellings
    )


def test_a_stop_sign_is_boundary_owned_not_a_letter_unit():
    a = built(KURSI)
    stop = find(a, kind=nd.GlyphKind.STOP_SIGN)[0]
    assert a.glyphs[stop].word is None
    assert _structural(a, stop)
    assert not units_named(a, stop)
    # The contrast: a real letter carries a word and a unit.
    letter = only(a, char="ٱ", word=0)
    assert a.glyphs[letter].word == 0 and units_named(a, letter)


def test_a_separator_is_boundary_owned():
    a = built(KURSI)
    space = find(a, char=" ")[0]
    assert a.glyphs[space].word is None
    assert _structural(a, space)
    assert not units_named(a, space)


def test_the_sakt_is_a_boundary_state_and_its_seen_opens_no_unit():
    """The sakt is stated on the word it follows, never read off array
    position; the small seen that shows it opens no unit of its own."""
    # مَنْۜ رَاقٍ
    a = built(SAKT)
    assert a.words[1].sakt_after
    seen = only(a, char="ۜ")
    assert not opens_unit(a, seen)
