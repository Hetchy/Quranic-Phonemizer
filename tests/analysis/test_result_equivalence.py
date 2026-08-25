"""The native result carries the same facts as the legacy assembler.

The native result reshapes the contract, so the legacy `Assembled` is mapped
into the reshaped form and compared exhaustively against it as the reference.
"""
from __future__ import annotations

import dataclasses

import pytest

from quranic_phonemizer.analysis import rule_definitions
from quranic_phonemizer.analysis.build import build_bundle
from quranic_phonemizer.analysis.dtos import BoundaryState
from quranic_phonemizer.analysis.ids import SoundId
from quranic_phonemizer.analysis.laws import ValidationError, validate
from quranic_phonemizer.analysis.result import build_result
from quranic_phonemizer.model.address import Script
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.phonemize import edges as ed
from quranic_phonemizer.phonemize.assemble import assemble
from quranic_phonemizer.phonemize.document import phonemes as legacy_phonemes
from quranic_phonemizer.phonemize.document import text as legacy_text
from quranic_phonemizer.phonemize.names import tajweed_rules as legacy_tajweed_rules
from quranic_phonemizer.session import phonemize_request

#: One reference per boundary state and hard case: a word isolated, a start,
#: joined words, cross-word idgham mergers, a spelled-out iltiqa fatha, an
#: authored sakt, and an internal stop taken two ways.
SITES = [
    ("1:1:1", {}),
    ("112:1", {}),
    ("1:1", {}),
    ("2:5", {}),
    ("3:1-3:2", {}),
    ("36:52-36:53", {}),
    ("2:255", {}),
    ("1:2", {"stop_refs": ["1:2:1"]}),
]


@pytest.fixture
def pen(hafs):
    return pen_for(hafs.inventory(Script.UTHMANI))


def _both(hafs, pen, alphabet, ref, kwargs):
    session = phonemize_request(hafs, ref, **kwargs)
    legacy = assemble(session, pen, alphabet)
    native = build_result(
        session, ref=ref, riwayah="hafs", script="uthmani", variant={}
    )
    return session, legacy, native


def _starts(boundary) -> bool:
    """A start boundary begins the word after it; so does an internal stop."""
    return boundary.state in (BoundaryState.START, BoundaryState.STOP)


def _legacy_sound_rules(legacy) -> list[set[int]]:
    out: list[set[int]] = [set() for _ in legacy.sounds]
    for edge in legacy.attributions:
        sound = getattr(edge, "sound", None)
        if sound is not None and edge.by is not None:
            out[sound].add(edge.by)
    for modifier in legacy.modifiers:
        out[modifier.sound].add(modifier.by)
    return out


def _legacy_mergers(legacy) -> list[tuple]:
    word_of = tuple(unit.word for unit in legacy.units)
    host_word: dict[int, int] = {}
    host_by: dict[int, int | None] = {}
    for edge in legacy.attributions:
        if isinstance(edge, ed.Hosts):
            host_word[edge.sound] = word_of[edge.unit]
            host_by[edge.sound] = edge.by
    out = []
    for edge in legacy.attributions:
        if isinstance(edge, ed.MergedInto):
            before, after = word_of[edge.unit], host_word[edge.sound]
            if before == after:
                continue
            occs = {edge.by}
            if host_by.get(edge.sound) is not None:
                occs.add(host_by[edge.sound])
            out.append((before, after, edge.sound, tuple(sorted(occs))))
    return sorted(out)


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_text_and_phonemes_are_byte_identical(hafs, pen, alphabet, ref, kwargs):
    _, legacy, native = _both(hafs, pen, alphabet, ref, kwargs)
    assert native.text() == legacy_text(legacy)
    assert native.phonemes() == legacy_phonemes(legacy)
    assert native.phonemes("word") == legacy_phonemes(legacy, "word")


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_words_agree_in_ref_text_and_sounds(hafs, pen, alphabet, ref, kwargs):
    _, legacy, native = _both(hafs, pen, alphabet, ref, kwargs)
    assert len(native.words) == len(legacy.words)
    for word, legacy_word in zip(native.words, legacy.words):
        assert word.ref == str(legacy_word.location)
        assert word.text == legacy_word.text
    grouped = native.phonemes("word")
    for word, tokens in zip(native.words, grouped):
        assert tuple(native.sounds[s.value].token for s in word.sound_ids) == tokens


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_boundary_states_match_word_flags(hafs, pen, alphabet, ref, kwargs):
    _, legacy, native = _both(hafs, pen, alphabet, ref, kwargs)
    assert len(native.boundaries) == len(native.words) + 1
    for i, legacy_word in enumerate(legacy.words):
        before, after = native.boundaries[i], native.boundaries[i + 1]
        assert _starts(before) == legacy_word.is_started_on
        assert (after.state is BoundaryState.STOP) == legacy_word.is_stopped_on
        assert (after.state is BoundaryState.SAKT) == legacy_word.sakt_after
        assert after.stop_advice == legacy_word.stop_sign


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_sounds_agree_in_order_token_word_and_rules(hafs, pen, alphabet, ref, kwargs):
    _, legacy, native = _both(hafs, pen, alphabet, ref, kwargs)
    assert len(native.sounds) == len(legacy.sounds)
    legacy_word = tuple(unit.word for unit in legacy.units)
    hosted = {
        edge.sound: legacy_word[edge.unit]
        for edge in legacy.attributions
        if isinstance(edge, ed.Hosts)
    }
    rules = _legacy_sound_rules(legacy)
    for i, sound in enumerate(native.sounds):
        assert sound.order == i
        assert sound.token == legacy.sounds[i].token
        assert sound.word_id.value == hosted[i]
        assert {o.value for o in sound.rule_occurrence_ids} == rules[i]


def test_rule_definition_inventory_equals_tajweed_rules():
    """Each riwayah publishes an ordered slice of the one inventory, and the
    two slices together cover the whole of it."""
    native = [
        (d.id.value, d.name, d.arabic_name, d.summary) for d in rule_definitions()
    ]
    published = set()
    for riwayah in ("hafs", "warsh"):
        rows = list(legacy_tajweed_rules(riwayah))
        assert [row for row in native if row in set(rows)] == rows
        published.update(rows)
    assert [row for row in native if row in published] == native


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_occurrences_agree_in_words_boundaries_and_sounds(
    hafs, pen, alphabet, ref, kwargs
):
    session, legacy, native = _both(hafs, pen, alphabet, ref, kwargs)
    word_of = tuple(unit.word for unit in legacy.units)
    per_sound = [set() for _ in legacy.sounds]
    for edge in legacy.attributions:
        sound = getattr(edge, "sound", None)
        if sound is not None and edge.by is not None:
            per_sound[sound].add(edge.by)
    for modifier in legacy.modifiers:
        per_sound[modifier.sound].add(modifier.by)
    assert len(native.rule_occurrences) == len(session.performance.occurrences)
    for i, occurrence in enumerate(session.performance.occurrences):
        instance, native_occ = legacy.rules[i], native.rule_occurrences[i]
        assert native_occ.rule_id.value == occurrence.rule.value
        host = () if instance.host is None else (instance.host,)
        legacy_words = sorted({word_of[instance.source], *(word_of[h] for h in host)})
        assert [w.value for w in native_occ.word_ids] == legacy_words
        legacy_boundary = () if occurrence.boundary is None else (occurrence.boundary + 1,)
        assert tuple(b.value for b in native_occ.boundary_ids) == legacy_boundary
        legacy_sounds = sorted(s for s, occs in enumerate(per_sound) if i in occs)
        assert [s.value for s in native_occ.sound_ids] == legacy_sounds


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_mergers_agree_over_boundary_words_and_sound(hafs, pen, alphabet, ref, kwargs):
    _, legacy, native = _both(hafs, pen, alphabet, ref, kwargs)
    native_mergers = sorted(
        (
            m.before_word_id.value,
            m.after_word_id.value,
            m.sound_id.value,
            tuple(o.value for o in m.rule_occurrence_ids),
        )
        for m in native.mergers if m.boundary_id is not None
    )
    assert native_mergers == _legacy_mergers(legacy)
    for merger in (m for m in native.mergers if m.boundary_id is not None):
        crossed = max(merger.before_word_id.value, merger.after_word_id.value)
        assert merger.boundary_id.value == crossed


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_closed_reference_validation_rejects_a_dangling_id(
    hafs, pen, alphabet, ref, kwargs
):
    session = phonemize_request(hafs, ref, **kwargs)
    bundle = build_bundle(
        session, ref=ref, riwayah="hafs", script="uthmani", variant={}
    )
    validate(bundle)  # the honest bundle passes
    first = bundle.words[0]
    dangling = dataclasses.replace(
        first, sound_ids=first.sound_ids + (SoundId(len(bundle.sounds)),)
    )
    broken = dataclasses.replace(bundle, words=(dangling, *bundle.words[1:]))
    with pytest.raises(ValidationError):
        validate(broken)


@pytest.mark.parametrize(("ref", "kwargs"), [("2:255", {})])
def test_validation_rejects_a_duplicate_occurrence(hafs, pen, alphabet, ref, kwargs):
    session = phonemize_request(hafs, ref, **kwargs)
    bundle = build_bundle(
        session, ref=ref, riwayah="hafs", script="uthmani", variant={}
    )
    validate(bundle)  # the honest bundle passes
    doubled = dataclasses.replace(
        bundle, rule_occurrences=bundle.rule_occurrences + (bundle.rule_occurrences[-1],)
    )
    with pytest.raises(ValidationError):
        validate(doubled)


def test_the_site_set_exercises_the_hard_cases(hafs, pen, alphabet):
    states: set[BoundaryState] = set()
    mergers = iltiqa = False
    for ref, kwargs in SITES:
        _, _, native = _both(hafs, pen, alphabet, ref, kwargs)
        states |= {boundary.state for boundary in native.boundaries}
        mergers |= bool(native.mergers)
        iltiqa |= any(
            occ.rule_id.value == "iltiqa_haraka"
            for occ in native.rule_occurrences
        )
    assert states == set(BoundaryState)
    assert mergers and iltiqa


def test_an_iltiqa_is_not_a_merger_and_names_its_boundary(hafs, pen, alphabet):
    _, _, native = _both(hafs, pen, alphabet, "3:1-3:2", {})
    iltiqa = [
        occ for occ in native.rule_occurrences
        if occ.rule_id.value == "iltiqa_haraka"
    ]
    assert iltiqa and all(occ.boundary_ids for occ in iltiqa)
    assert not any(m.boundary_id is not None for m in native.mergers)


def test_the_equivalence_bites(hafs, pen, alphabet):
    """A corrupted boundary state fails the flag comparison, so the passing
    comparisons above are not vacuous."""
    _, legacy, native = _both(hafs, pen, alphabet, "1:2", {"stop_refs": ["1:2:1"]})
    join = next(
        i for i, b in enumerate(native.boundaries)
        if b.state is BoundaryState.STOP and 0 < i < len(native.boundaries) - 1
    )
    corrupt = dataclasses.replace(
        native.boundaries[join], state=BoundaryState.JOIN
    )
    broken = dataclasses.replace(
        native,
        boundaries=native.boundaries[:join]
        + (corrupt,)
        + native.boundaries[join + 1:],
    )
    with pytest.raises(AssertionError):
        for i, legacy_word in enumerate(legacy.words):
            after = broken.boundaries[i + 1]
            assert (after.state is BoundaryState.STOP) == legacy_word.is_stopped_on


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_a_boundary_with_advice_carries_its_written_sign(hafs, pen, alphabet, ref, kwargs):
    _, _, native = _both(hafs, pen, alphabet, ref, kwargs)
    signed = [b for b in native.boundaries if b.stop_advice is not None]
    for boundary in signed:
        assert boundary.stop_sign, "an advised boundary writes no sign"


def test_the_written_signs_are_exercised(hafs, pen, alphabet):
    # non-vacuity: the sweep actually has advised, sign-carrying boundaries.
    total = 0
    for ref, kwargs in SITES:
        _, _, native = _both(hafs, pen, alphabet, ref, kwargs)
        total += sum(1 for b in native.boundaries if b.stop_sign)
    assert total > 0
