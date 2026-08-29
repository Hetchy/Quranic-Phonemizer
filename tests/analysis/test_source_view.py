"""The native source view holds the exact characters and the units over them.

Correctness is held three ways: the tokenization, the characters covering the
text exactly, and ownership, silence and placements agreeing with the result.
"""
from __future__ import annotations

import dataclasses

import pytest

from quranic_phonemizer.analysis.build import build_bundle
from quranic_phonemizer.analysis.dtos import BoundaryState
from quranic_phonemizer.analysis.source import build_source_view
from quranic_phonemizer.analysis.source_dtos import (
    CharacterKind,
    LetterUnitKind,
    LiteralSilence,
)
from quranic_phonemizer.analysis.source_laws import (
    SourceValidationError,
    validate_source_view,
)
from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Riwayah, Script, VerseRef
from quranic_phonemizer.model.inscription import StopAdvice
from quranic_phonemizer.session import phonemize_request
from quranic_phonemizer.session.boundaries import resolve_boundaries
from quranic_phonemizer.session.core import Session

#: One reference per boundary state and hard case: a word isolated, a start,
#: joined words, a cross-word idgham merger, a spelled-out iltiqa, muqattaat,
#: an authored sakt, the seen/saad khilaf, a silent alif, an imala, a pausal
#: zero at a stop, and an internal stop.
SITES = [
    ("1:1:1", {}),
    ("112:1", {}),
    ("1:1", {}),
    ("2:5", {}),
    ("36:52-36:53", {}),
    ("3:1-3:2", {}),
    ("2:255", {}),
    ("75:27", {}),
    ("2:245:14", {}),
    ("2:6:3", {}),
    ("11:41", {}),
    ("18:38", {"stop_refs": ["18:38:1"]}),
    ("1:2", {"stop_refs": ["1:2:1"]}),
]


def _both(hafs, ref, kwargs):
    session = phonemize_request(hafs, ref, **kwargs)
    bundle = build_bundle(
        session, ref=ref, riwayah="hafs", script="uthmani", variant={}
    )
    view = build_source_view(session, bundle=bundle)
    return session, bundle, view


def _indopak_word(hafs, sources, surah, ayah, ordinal):
    """One word read and performed in IndoPak, isolated, as its own session.

    The packaged IndoPak inventory is partial, so a word is read alone rather
    than through a whole verse."""
    verse = VerseRef(surah, ayah)
    location, text = sources[Script.INDOPAK][(surah, ayah)][ordinal - 1]
    reading = hafs.read(Script.INDOPAK, verse, ((location, text),))
    built = hafs.build(reading)
    boundaries = resolve_boundaries(built.inscription.advice, (location,), built.score)
    performance = hafs.perform(built.score, boundaries)
    session = Session(
        (location,), built.score, built.inscription, boundaries, performance
    )
    ref = str(location)
    bundle = build_bundle(
        session, ref=ref, riwayah="hafs", script="indopak", variant={}
    )
    view = build_source_view(session, bundle=bundle)
    return session, bundle, view


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_characters_reproduce_the_text_exactly(hafs, ref, kwargs):
    _, bundle, view = _both(hafs, ref, kwargs)
    assert "".join(c.text for c in view.characters) == view.text == bundle.source_text
    for i, char in enumerate(view.characters):
        assert char.index == i and char.id.value == i


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_every_character_is_exactly_one_kind(hafs, ref, kwargs):
    _, _, view = _both(hafs, ref, kwargs)
    for char in view.characters:
        if char.kind is CharacterKind.LEXICAL:
            assert char.word_id is not None and char.letter_unit_id is not None
            assert char.boundary_id is None
            unit = view.units[char.letter_unit_id.value]
            assert char.id in unit.character_ids and unit.word_id == char.word_id
        else:
            assert char.boundary_id is not None
            assert char.word_id is None and char.letter_unit_id is None


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_unit_ranges_reproduce_their_characters(hafs, ref, kwargs):
    _, _, view = _both(hafs, ref, kwargs)
    for unit in view.units:
        spanned = [i for lo, hi in unit.ranges for i in range(lo, hi)]
        assert sorted(c.value for c in unit.character_ids) == sorted(spanned)
        assert unit.text == "".join(view.characters[i].text for i in sorted(spanned))


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_ownership_is_disjoint_and_total(hafs, ref, kwargs):
    _, bundle, view = _both(hafs, ref, kwargs)
    owned: set[int] = set()
    for unit in view.units:
        own = {s.value for s in unit.owned_sound_ids}
        present = {s.value for s in unit.presented_sound_ids}
        assert not (own & present)
        assert not (own & owned), "a sound is owned twice"
        owned |= own
    assert owned == set(range(len(bundle.sounds)))


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_silence_is_a_real_occurrence_or_the_orthographic(hafs, ref, kwargs):
    _, bundle, view = _both(hafs, ref, kwargs)
    occ_ids = {occ.id for occ in bundle.rule_occurrences}
    for unit in view.units:
        if unit.silence is None:
            continue
        assert not unit.owned_sound_ids and not unit.presented_sound_ids
        if isinstance(unit.silence, LiteralSilence):
            continue
        assert unit.silence in occ_ids
        assert unit.silence in unit.rule_occurrence_ids


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_placements_agree_with_the_unit_rule_queries(hafs, ref, kwargs):
    _, bundle, view = _both(hafs, ref, kwargs)
    assert len(view.rule_placements) == len(bundle.rule_occurrences)
    by_unit: dict[int, set[int]] = {u.id.value: set() for u in view.units}
    for placement in view.rule_placements:
        for unit in placement.unit_ids:
            by_unit[unit.value].add(placement.rule_occurrence_id.value)
    for unit in view.units:
        assert {o.value for o in unit.rule_occurrence_ids} == by_unit[unit.id.value]


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_mergers_place_a_host_and_agree_with_the_core(hafs, ref, kwargs):
    _, bundle, view = _both(hafs, ref, kwargs)
    assert len(view.merger_placements) == len(bundle.mergers)
    for placement in view.merger_placements:
        assert placement.after_unit_ids, "a merger hosts on no unit"
        host = view.units[placement.after_unit_ids[0].value]
        merger = bundle.mergers[placement.merger_id.value]
        assert merger.sound_id.value in {s.value for s in host.owned_sound_ids}


def test_the_site_set_exercises_every_boundary_state(hafs):
    states: set[BoundaryState] = set()
    for ref, kwargs in SITES:
        session, _, _ = _both(hafs, ref, kwargs)
        session = phonemize_request(hafs, ref, **kwargs)
        bundle = build_bundle(
            session, ref=ref, riwayah="hafs", script="uthmani", variant={}
        )
        states |= {b.state for b in bundle.boundaries}
    assert states == set(BoundaryState)


def test_warsh_optional_stop_is_a_typed_boundary_sign():
    warsh = recitation(Riwayah.WARSH)
    ref = "1:3-1:4"

    session = phonemize_request(warsh, ref)
    bundle = build_bundle(
        session, ref=ref, riwayah="warsh", script="uthmani", variant={}
    )
    view = build_source_view(session, bundle=bundle)
    sign = next(character for character in view.characters if character.text == "ۖ")
    boundary = bundle.boundaries[sign.boundary_id.value]

    assert sign.kind is CharacterKind.STOP_SIGN
    assert boundary.stop_sign == "ۖ"
    assert boundary.stop_advice is StopAdvice.OPTIONAL_STOP
    assert boundary.state is BoundaryState.JOIN

    stopped = phonemize_request(warsh, ref, stop_signs=("optional_stop",))
    stopped_bundle = build_bundle(
        stopped, ref=ref, riwayah="warsh", script="uthmani", variant={}
    )
    assert stopped_bundle.boundaries[sign.boundary_id.value].state is BoundaryState.STOP


def test_every_warsh_optional_stop_uses_the_typed_inventory_entry():
    warsh = recitation(Riwayah.WARSH)
    occurrences = sum(
        word.text.count("ۖ") for word in warsh.corpus.entries.values()
    )
    entry = warsh.inventory(Script.UTHMANI).classify("ۖ")

    assert occurrences == 9_948
    assert entry.advice is StopAdvice.OPTIONAL_STOP
    assert not entry.structural


def test_a_cross_word_merger_places_a_contributor(hafs):
    _, bundle, view = _both(hafs, "36:52-36:53", {})
    assert view.merger_placements
    assert any(p.before_unit_ids for p in view.merger_placements)


def test_iltiqa_shortening_is_placed_only_on_its_length_carrier(hafs):
    _, bundle, view = _both(hafs, "2:11", {})
    occurrence = next(
        item for item in bundle.rule_occurrences
        if item.rule_id.value == "iltiqa_shortening"
    )
    placement = view.rule_placements[occurrence.id.value]

    texts = tuple(view.units[unit.value].text for unit in placement.unit_ids)
    assert texts == ("ى",)


def test_validation_rejects_a_double_owned_sound(hafs):
    _, bundle, view = _both(hafs, "2:255", {})
    validate_source_view(view, bundle)  # the honest view passes
    sounding = next(u for u in view.units if u.owned_sound_ids)
    other = next(
        u for u in view.units
        if u.id != sounding.id and not u.owned_sound_ids and u.silence is None
    )
    doubled = dataclasses.replace(other, owned_sound_ids=sounding.owned_sound_ids)
    broken = dataclasses.replace(
        view,
        units=view.units[:other.id.value]
        + (doubled,) + view.units[other.id.value + 1:],
    )
    with pytest.raises(SourceValidationError):
        validate_source_view(broken, bundle)


def test_validation_rejects_a_silence_that_still_sounds(hafs):
    _, bundle, view = _both(hafs, "1:1", {})
    sounding = next(u for u in view.units if u.owned_sound_ids)
    lying = dataclasses.replace(sounding, silence=LiteralSilence.ORTHOGRAPHIC)
    broken = dataclasses.replace(
        view, units=view.units[:sounding.id.value]
        + (lying,) + view.units[sounding.id.value + 1:],
    )
    with pytest.raises(SourceValidationError):
        validate_source_view(broken, bundle)


def test_validation_rejects_characters_that_drop_a_scalar(hafs):
    _, bundle, view = _both(hafs, "1:1", {})
    broken = dataclasses.replace(view, characters=view.characters[:-1])
    with pytest.raises(SourceValidationError):
        validate_source_view(broken, bundle)


def test_the_divine_name_long_vowel_is_haraka_owned_without_a_carrier(hafs):
    """Uthmani spells no alif for the divine name, so the lam's fatha owns the
    long vowel and no carrier letter unit stands beside it."""
    _, bundle, view = _both(hafs, "1:1:2", {})
    owners = {s.value: u for u in view.units for s in u.owned_sound_ids}
    aa = next(s.id.value for s in bundle.sounds if s.token in ("aˤ:", "aː", "aˤː"))
    assert owners[aa].kind is LetterUnitKind.HARAKA


#: The hamzat al-wasl, elided by a rule when read in continuation.
_WASL_HAMZA = "ٱ"
#: The small high rounded zero, marking a written letter no reading pronounces.
_SILENT_ZERO = "۟"


def test_a_silenced_wasl_hamza_carries_its_rule_not_the_orthographic(hafs):
    """A hamzat al-wasl read in continuation is elided by a rule, so a silent
    one names that occurrence. Pins that a rule silence is never downgraded to
    the orthographic, which the shape checks alone accept."""
    seen = 0
    for ref, kwargs in SITES:
        _, bundle, view = _both(hafs, ref, kwargs)
        occ_ids = {occ.id for occ in bundle.rule_occurrences}
        for unit in view.units:
            if _WASL_HAMZA not in unit.text or unit.silence is None:
                continue
            seen += 1
            assert not isinstance(unit.silence, LiteralSilence), (
                f"{ref} unit {unit.id.value}: an elided wasl hamza went orthographic"
            )
            assert unit.silence in occ_ids
    assert seen, "the sites exercise no silenced wasl hamza"


def test_a_letter_no_rule_reads_takes_the_orthographic(hafs):
    """The small high rounded zero marks a letter the rasm writes but no reading
    pronounces -- silent by orthography, never by a named occurrence."""
    seen = 0
    for ref, kwargs in SITES:
        _, _, view = _both(hafs, ref, kwargs)
        for unit in view.units:
            if _SILENT_ZERO not in unit.text or unit.silence is None:
                continue
            seen += 1
            assert unit.silence is LiteralSilence.ORTHOGRAPHIC, (
                f"{ref} unit {unit.id.value}: an orthographic silence named a rule"
            )
    assert seen, "the sites exercise no orthographic silence"


def test_a_written_carrier_owns_its_long_vowel_and_the_haraka_presents_it(hafs):
    """The waw of الطور carries the long vowel; the damma before it presents it."""
    _, bundle, view = _both(hafs, "52:1:1", {})
    carrier = next(
        u for u in view.units
        if u.kind is LetterUnitKind.LETTER and u.owned_sound_ids
        and any(
            bundle.sounds[s.value].token in ("uː", "uˤ:", "u:") for s in u.owned_sound_ids
        )
    )
    owned = carrier.owned_sound_ids[0]
    presenters = [u for u in view.units if owned in u.presented_sound_ids]
    assert presenters and all(u.kind is LetterUnitKind.HARAKA for u in presenters)


@pytest.mark.parametrize(("ref", "word_ref", "carrier_text"), [
    ("17:7", "17:7:12", "ۥٓ"),
    ("2:3", "2:3:5", "وٰ"),
    ("2:124", "2:124:3", "ۧ"),
])
def test_a_written_display_carrier_owns_its_vowel(
    hafs, ref, word_ref, carrier_text
):
    _, bundle, view = _both(hafs, ref, {})
    word = next(word for word in bundle.words if word.ref == word_ref)
    carrier = next(
        unit for unit in view.units
        if unit.word_id == word.id and unit.text == carrier_text
    )

    assert carrier.owned_sound_ids
    assert carrier.silence is None


def test_a_decoration_only_dagger_is_explicitly_silent(hafs):
    _, bundle, view = _both(hafs, "2:72", {})
    word = next(word for word in bundle.words if word.ref == "2:72:4")
    units = [unit for unit in view.units if unit.word_id == word.id]
    dagger = next(
        unit for unit in units
        if unit.text == "ٰ" and not unit.owned_sound_ids
    )
    hamza = next(unit for unit in units if unit.text == "ٔ")

    assert dagger.silence is LiteralSilence.ORTHOGRAPHIC
    assert hamza.owned_sound_ids
    assert hamza.silence is None
