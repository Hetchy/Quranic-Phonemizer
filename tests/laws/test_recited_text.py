"""The recited-text writer, over real sites."""
from __future__ import annotations

import unicodedata

import pytest

from quranic_phonemizer.model.address import Script
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.phonemize.nodes import GlyphKind
from quranic_phonemizer.phonemize.recited import text, write_recited
from quranic_phonemizer.phonemize.session import phonemize_request


@pytest.fixture
def pen(hafs):
    return pen_for(hafs.inventory(Script.UTHMANI))


def _write(hafs, pen, ref, **boundary):
    session = phonemize_request(hafs, ref, **boundary)
    return write_recited(
        session.score, session.inscription, session.performance, pen
    )


def _text(hafs, pen, ref, **boundary):
    # The writer spells a long a as a bare alif plus a combining maddah, not
    # the precomposed scalar this file's own comments use to quote one.
    return unicodedata.normalize("NFC", text(_write(hafs, pen, ref, **boundary)))


def test_row_30_a_stop_sign_is_kept_and_takes_no_pairing(hafs, pen):
    # 83:14 كَلَّا ۖ -- the sign after the first word survives an all-join plan.
    glyphs = _write(hafs, pen, "83:14")
    signs = [g for g in glyphs if g.kind is GlyphKind.STOP_SIGN]
    assert signs and signs[0].char == "ۖ"


def test_text_serializes_exactly_what_rendered_holds(hafs, pen):
    glyphs = _write(hafs, pen, "1:1")
    assert text(glyphs) == "".join(g.char for g in glyphs)


def test_row_6_a_joined_hamza_wasl_seat_goes(hafs, pen):
    # بِسْمِ ٱللَّهِ, joined -- no wasl seat, no helping vowel.
    got = _text(hafs, pen, "1:1-1:2")
    assert "لَّآهِ" in got
    assert "ٱ" not in got


def test_row_24_a_started_wasl_hamza_takes_its_vowel_s_own_shape(hafs, pen):
    # ٱقْرَأْ, started on -- the definite kasra shape, not the bare letter.
    assert _text(hafs, pen, "96:1").startswith("إِقْرَ")


def test_row_19_a_short_vowel_at_a_stop_becomes_a_sukun(hafs, pen):
    # ذَٰلِكَ, isolated -- the final fatha silences to a sukun.
    assert _text(hafs, pen, "2:2:1") == "ذَآلِكْ"


def test_row_22_a_taa_marbuta_at_a_stop_becomes_a_haa(hafs, pen):
    # بَعُوضَةً, isolated -- taa marbuta reads as haa, and its fathatan drops.
    assert _text(hafs, pen, "2:26:9") == "بَعُوٓضَهْ"


def test_4_1a_izhar_keeps_a_tanween_noon_with_a_sukun(hafs, pen):
    # عَذَابٌ عَظِيمٌ -- izhar before ain: a bare noon plus its sukun mark.
    assert "بُنْ" in _text(hafs, pen, "2:7:11-2:7:12")


def test_4_1a_ikhfaa_leaves_a_tanween_noon_bare(hafs, pen):
    # حَيَّةٌ تَسْعَىٰ -- ikhfaa before ta: no sukun mark on the noon.
    assert "ةُن " in _text(hafs, pen, "20:20:4-20:20:5")


def test_4_1a_idgham_writes_no_noon_and_a_shadda_on_the_host(hafs, pen):
    # عَظِيمٌ وَمِنَ -- the noon disappears and the waw doubles; this range's
    # own last word is stopped on, so its own vowel silences too.
    assert _text(hafs, pen, "2:7:12-2:8:1") == "عَظِىٓمُ وَّمِنْ"


def test_a_merged_or_silenced_unit_writes_no_glyph_at_all(hafs, pen):
    glyphs = _write(hafs, pen, "2:7:12-2:8:1")
    assert all(glyph.char for glyph in glyphs), "no rendered glyph is empty"


def test_a_kept_letter_names_its_source_glyph(hafs, pen):
    glyphs = _write(hafs, pen, "1:1:1")
    kept = [g for g in glyphs if g.kind is GlyphKind.BASE]
    assert kept and all(g.from_glyphs for g in kept)
