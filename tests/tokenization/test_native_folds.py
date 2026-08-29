"""The four folds the native LetterUnit builder decides.

Each keys on the grapheme kind and the fact it supplies, never on the scalar.
"""
from __future__ import annotations

from quranic_phonemizer.analysis.build import build_bundle
from quranic_phonemizer.analysis.ids import RuleId
from quranic_phonemizer.analysis.result import build_result
from quranic_phonemizer.analysis.source import build_source_view
from quranic_phonemizer.analysis.source_dtos import (
    CharacterKind,
    LetterUnitKind,
    LiteralSilence,
)
from quranic_phonemizer.model.address import (
    KhilafId,
    Option,
    Script,
    VariantSelection,
    VerseRef,
)
from quranic_phonemizer.session import phonemize_request
from quranic_phonemizer.session.boundaries import resolve_boundaries
from quranic_phonemizer.session.core import Session

PAUSAL_ZERO = "۠"      # the rectangular zero of the seven alifs
ROUND_ZERO = "۟"       # the round zero over a purely orthographic alif
IMALA_MARK = "۪"       # the empty-centre low stop over the imala raa
SEEN_ABOVE = "ۜ"       # the small high seen
SEEN_BELOW = "ۣ"       # the small low seen
PAUSAL_ALIF = "ا"
RAA = "ر"
SAD = "ص"


def _view(hafs, ref, script="uthmani", **kwargs):
    session = phonemize_request(hafs, ref, script=Script(script), **kwargs)
    bundle = build_bundle(
        session, ref=ref, riwayah="hafs", script=script, variant={}
    )
    return build_source_view(session, bundle=bundle)


def _indopak_word_view(hafs, sources, surah, ayah, ordinal):
    verse = VerseRef(surah, ayah)
    location, text = sources[Script.INDOPAK][(surah, ayah)][ordinal - 1]
    reading = hafs.read(Script.INDOPAK, verse, ((location, text),))
    built = hafs.build(reading)
    boundaries = resolve_boundaries(built.inscription.advice, (location,), built.score)
    performance = hafs.perform(built.score, boundaries)
    session = Session(
        (location,), built.score, built.inscription, boundaries, performance
    )
    bundle = build_bundle(
        session, ref=str(location), riwayah="hafs", script="indopak", variant={}
    )
    return build_source_view(session, bundle=bundle)


def _char(view, scalar):
    hits = [c for c in view.characters if c.text == scalar]
    assert len(hits) == 1, f"expected one {scalar!r}, got {len(hits)}"
    return hits[0]


def _unit_of(view, scalar):
    char = _char(view, scalar)
    assert char.kind is CharacterKind.LEXICAL
    return view.units[char.letter_unit_id.value]


def test_the_pausal_zero_folds_into_the_silent_alif_it_marks(hafs):
    """The zero supplies a length yet mints no unit; the alif beside it is the
    carrier unit, and the zero is a character inside it."""
    view = _view(hafs, "18:38", stop_refs=["18:38:1"])
    unit = _unit_of(view, PAUSAL_ZERO)
    assert unit.kind is LetterUnitKind.LETTER
    assert PAUSAL_ALIF in unit.text
    assert not any(u.text == PAUSAL_ZERO for u in view.units)


def test_a_shortened_pausal_alif_carrier_names_the_rule_that_shortened_it(hafs):
    """Joined, wasl takes the pausal alif's length back: the carrier sounds
    nothing and its silence is the pausal_alif occurrence, not the literal."""
    session = phonemize_request(hafs, "18:38", script=Script("uthmani"))
    bundle = build_bundle(
        session, ref="18:38", riwayah="hafs", script="uthmani", variant={}
    )
    view = build_source_view(session, bundle=bundle)
    carrier = _unit_of(view, PAUSAL_ZERO)
    assert carrier.silence not in (None, LiteralSilence.ORTHOGRAPHIC)
    assert carrier.silence in carrier.rule_occurrence_ids
    result = build_result(
        session, ref="18:38", riwayah="hafs", script="uthmani", variant={}
    )
    occurrence = next(o for o in result.rule_occurrences if o.id == carrier.silence)
    assert occurrence.rule_id == RuleId("pausal_alif")


def test_a_purely_orthographic_alif_keeps_the_literal_silence(hafs):
    """The dropped alif of qaaluu is written and never said with no rule
    taking a length back, so its silence stays the literal orthographic."""
    view = _view(hafs, "2:32:1")
    carrier = _unit_of(view, ROUND_ZERO)
    assert carrier.silence is LiteralSilence.ORTHOGRAPHIC


def test_a_round_zero_after_tanween_stays_with_its_alif(hafs):
    view = _view(hafs, "4:176:8")
    carrier = _unit_of(view, ROUND_ZERO)

    assert carrier.text == PAUSAL_ALIF + ROUND_ZERO
    assert carrier.silence is LiteralSilence.ORTHOGRAPHIC


def test_the_imala_mark_folds_into_the_letter_it_qualifies(hafs):
    """The mark supplies a vowel quality yet mints no unit; the raa carries it."""
    view = _view(hafs, "11:41")
    unit = _unit_of(view, IMALA_MARK)
    assert unit.kind is LetterUnitKind.LETTER
    assert RAA in unit.text
    assert not any(u.text == IMALA_MARK for u in view.units)


def test_the_seen_reading_keeps_the_sound_on_the_base_saad(hafs):
    """The mini seen is a visible reading sign; the base cell remains the
    sound-alignment host when that sign selects the seen realization."""
    view = _view(hafs, "2:245:14")
    seen = _unit_of(view, SEEN_ABOVE)
    saad = _unit_of(view, SAD)
    assert seen.kind is LetterUnitKind.LETTER
    assert seen.id != saad.id
    assert seen.written_on_unit_id == saad.id
    assert seen.text == SEEN_ABOVE
    assert saad.owned_sound_ids
    assert not seen.owned_sound_ids
    assert seen.presented_sound_ids == saad.owned_sound_ids
    assert seen.silence is None
    assert saad.silence is None


def test_the_saad_reading_only_silences_the_mini_seen(hafs):
    """Selecting saad keeps the same sound host and applies variant silence
    only to the mini seen."""
    view = _view(
        hafs, "2:245:14",
        selection=VariantSelection((Option(KhilafId.YABSUT, "saad"),)),
    )
    seen = _unit_of(view, SEEN_ABOVE)
    saad = _unit_of(view, SAD)
    assert saad.owned_sound_ids and not seen.owned_sound_ids
    assert saad.silence is None
    assert seen.silence is LiteralSilence.VARIANT


def test_the_mini_seen_pairs_in_both_scripts(hafs, sources):
    """IndoPak writes the mark below at yabsut too, so the pair is two units in
    both scripts even where the position differs."""
    view = _indopak_word_view(hafs, sources, 2, 245, 14)
    seen = next(
        (u for u in view.units if u.text in (SEEN_ABOVE, SEEN_BELOW)), None
    )
    assert seen is not None and seen.kind is LetterUnitKind.LETTER
    assert seen.written_on_unit_id is not None


def test_the_unwritten_site_has_no_seen_unit_and_the_base_carries(hafs):
    """Uthmani writes no mark at bimusaytir, so there is no second unit and the
    base saad alone owns the site's sound."""
    view = _view(hafs, "88:22:3")
    assert not any(c.text in (SEEN_ABOVE, SEEN_BELOW) for c in view.characters)
    saad = _unit_of(view, SAD)
    assert saad.owned_sound_ids


def test_indopak_writes_the_seen_where_uthmani_does_not(hafs, sources):
    """The same bimusaytir site writes the mark in IndoPak, so there the pair
    exists as two units."""
    view = _indopak_word_view(hafs, sources, 88, 22, 3)
    seen = next(
        (u for u in view.units if u.text in (SEEN_ABOVE, SEEN_BELOW)), None
    )
    assert seen is not None
    assert seen.written_on_unit_id is not None


def test_the_sakt_seen_belongs_to_the_boundary_not_a_letter_unit(hafs):
    """The sakt seen is a boundary character like a stop sign, owning no letter
    unit, where the same scalar written as a khilaf mark opens one."""
    view = _view(hafs, "75:27")
    seen = _char(view, SEEN_ABOVE)
    assert seen.kind is CharacterKind.STOP_SIGN
    assert seen.letter_unit_id is None and seen.boundary_id is not None
    assert not any(seen.id in u.character_ids for u in view.units)
