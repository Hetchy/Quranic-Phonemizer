"""Stop signs and separators belong to the boundary, not to a word letter
unit. The sakt sign is the same: the native builder makes its small seen a
boundary character, while the pause itself is a separate boundary state."""
from __future__ import annotations

from quranic_phonemizer.analysis.source import build_source_view
from quranic_phonemizer.analysis.source_dtos import CharacterKind
from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Riwayah
from quranic_phonemizer.phonemize import edges as ed
from quranic_phonemizer.phonemize import nodes as nd
from quranic_phonemizer.session import phonemize_request

from .support import built, find, only, units_named

KURSI = "2:255"
SAKT = "75:27"           # an authored sakt after the second word
SAKT_SEEN = "ۜ"


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


def test_the_sakt_is_a_boundary_state_and_its_seen_is_a_boundary_character():
    """The pause is stated on the word it follows, and the small seen that shows
    it is a boundary character like a stop sign: the native builder gives it no
    letter unit, where the same scalar written as a khilaf mark opens one."""
    # مَنْۜ رَاقٍ
    a = built(SAKT)
    assert a.words[1].sakt_after
    session = phonemize_request(recitation(Riwayah("hafs")), SAKT)
    view = build_source_view(
        session, ref=SAKT, riwayah="hafs", script="uthmani", variant={}
    )
    seen = only_char(view, SAKT_SEEN)
    assert seen.kind is CharacterKind.STOP_SIGN
    assert seen.letter_unit_id is None and seen.boundary_id is not None
    assert not any(seen.id in unit.character_ids for unit in view.units)


def only_char(view, scalar):
    hits = [c for c in view.characters if c.text == scalar]
    assert len(hits) == 1, f"expected one {scalar!r}, got {len(hits)}"
    return hits[0]
