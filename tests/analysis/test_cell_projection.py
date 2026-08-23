"""The transformed CellView is a complete renderer-ready projection."""
from __future__ import annotations

import pytest

from quranic_phonemizer.analysis.build import build_bundle
from quranic_phonemizer.analysis.cells import CellRole, CellStatus, build_cell_view
from quranic_phonemizer.analysis.facts import analyse
from quranic_phonemizer.model.address import Script
from quranic_phonemizer.model.canon import Quality
from quranic_phonemizer.model.performance import Consonant, Vowel
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.render.alphabet import packaged_alphabet
from quranic_phonemizer.session import phonemize_request


@pytest.fixture(scope="module")
def pen(hafs):
    return pen_for(hafs.inventory(Script.UTHMANI))


def _build(hafs, pen, ref: str):
    session = phonemize_request(hafs, ref)
    kw = dict(ref=ref, riwayah="hafs", script="uthmani", variant={})
    bundle = build_bundle(session, **kw)
    view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
    return session, bundle, view


def test_sukun_is_folded_into_its_main_letter(hafs, pen):
    _, _, view = _build(hafs, pen, "1:1")
    assert all(c.role is not CellRole.SUKUN for w in view.words for c in w.columns)
    assert any(c.tier.value == "main" and "ْ" in c.text for w in view.words for c in w.columns)


@pytest.mark.parametrize("ref", ["1:1:1", "2:10:3"])
def test_a_pausal_sukun_changes_the_final_consonant_cell(hafs, pen, ref):
    session, _, view = _build(hafs, pen, ref)
    facts = analyse(session, packaged_alphabet())
    column = next(
        col for col in view.words[0].columns
        if col.text.endswith(pen.role("sukun"))
        and col.status is CellStatus.REPLACED
    )
    assert any(
        isinstance(facts.sounds[sound.value].value, Consonant)
        for sound in column.owned_sound_ids
    )
    assert all(col.role is not CellRole.SUKUN for col in view.words[0].columns)


@pytest.mark.parametrize("ref", ["2:29:1", "2:70:8", "2:29:2"])
def test_a_final_vowel_carrier_does_not_gain_a_pausal_sukun(hafs, pen, ref):
    _, _, view = _build(hafs, pen, ref)
    assert all(
        not col.text.endswith(pen.role("sukun"))
        for col in view.words[0].columns if col.role is CellRole.MADD
    )


@pytest.mark.parametrize(("ref", "base", "mark"), [
    ("1:2", "أ", "َ"),
    ("20:24:1", "إ", "ِ"),
    ("2:58:3", "أ", "ُ"),
])
def test_started_wasl_is_a_seated_hamza_plus_its_vowel(hafs, pen, ref, base, mark):
    session, _, view = _build(hafs, pen, ref)
    facts = analyse(session, packaged_alphabet())
    first = view.words[0]
    assert first.columns[0].text == base
    assert first.columns[0].status is CellStatus.REPLACED
    assert first.columns[1].text == mark
    assert first.columns[1].status is CellStatus.INSERTED
    assert all(isinstance(facts.sounds[s.value].value, Consonant)
               for s in first.columns[0].owned_sound_ids)
    assert all(isinstance(facts.sounds[s.value].value, Vowel)
               for s in first.columns[1].owned_sound_ids)


def test_every_drawn_long_vowel_has_an_explicit_vowel_group(hafs, pen):
    session, bundle, view = _build(hafs, pen, "3:103")
    facts = analyse(session, packaged_alphabet())
    words = {w.word_id.value: w for w in view.words}
    for sound in bundle.sounds:
        value = facts.sounds[sound.id.value].value
        if not isinstance(value, Vowel) or not value.long:
            continue
        word = words[sound.word_id.value]
        group = next(g for g in word.groups if sound.id in g.sound_ids)
        columns = {c.id: c for c in word.columns}
        assert group.kind.value == "vowel"
        assert any(columns[c].role is CellRole.MADD for c in group.column_ids)


def test_madd_iwad_reuses_the_written_alif_and_replaces_tanween(hafs, pen):
    session = phonemize_request(hafs, "3:103", stop_refs=["3:103:4"])
    kw = dict(ref="3:103", riwayah="hafs", script="uthmani", variant={})
    bundle = build_bundle(session, **kw)
    view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
    word_id = next(w.id for w in bundle.words if w.ref == "3:103:4")
    word = next(w for w in view.words if w.word_id == word_id)
    iwad = next(
        o for o in bundle.rule_occurrences if o.rule_id.value == "madd_iwad"
    )
    group = next(g for g in word.groups if set(g.sound_ids) & set(iwad.sound_ids))
    columns = {c.id: c for c in word.columns}
    quality, carrier = (columns[c] for c in group.column_ids)
    assert quality.role is CellRole.HARAKA
    assert quality.status is CellStatus.REPLACED
    assert quality.text == pen.short_vowel(
        analyse(session, packaged_alphabet()).sounds[iwad.sound_ids[0].value].value.quality
    )
    assert carrier.role is CellRole.MADD
    assert carrier.status is CellStatus.PRESENT
    assert carrier.source_character_ids
    assert not any(
        c.status is CellStatus.INSERTED and c.role is CellRole.MADD
        for c in word.columns
    )


def test_a_written_small_vowel_is_the_carrier_not_a_stray_cell(hafs, pen):
    session, bundle, view = _build(hafs, pen, "3:103:19")
    facts = analyse(session, packaged_alphabet())
    word = view.words[0]
    long_sound = next(
        s for s in bundle.sounds
        if isinstance(facts.sounds[s.id.value].value, Vowel)
        and facts.sounds[s.id.value].value.long
    )
    group = next(g for g in word.groups if long_sound.id in g.sound_ids)
    columns = {c.id: c for c in word.columns}
    carrier = next(c for c in group.column_ids if columns[c].role is CellRole.MADD)
    assert columns[carrier].source_character_ids
    assert columns[carrier].status is CellStatus.PRESENT
    assert not any(
        c.status is CellStatus.INSERTED and c.role is CellRole.MADD
        for c in word.columns
    )


def test_imala_uses_its_written_ya_carrier(hafs, pen):
    session, bundle, view = _build(hafs, pen, "11:41:6")
    facts = analyse(session, packaged_alphabet())
    sound = next(
        s for s in bundle.sounds
        if isinstance(facts.sounds[s.id.value].value, Vowel)
        and facts.sounds[s.id.value].value.quality.value == "e"
    )
    group = next(g for g in view.words[0].groups if sound.id in g.sound_ids)
    columns = {c.id: c for c in view.words[0].columns}
    carrier = next(columns[c] for c in group.column_ids if columns[c].role is CellRole.MADD)
    assert group.kind.value == "vowel"
    assert carrier.text == pen.performed_carrier(Quality.E)[1] + "ٰ"
    assert carrier.source_character_ids


@pytest.mark.parametrize("ref", ["2:5:2", "11:41:6"])
def test_a_maqsura_and_its_dagger_are_one_native_carrier_cell(hafs, pen, ref):
    _, _, view = _build(hafs, pen, ref)
    word = view.words[0]
    carriers = [c for c in word.columns if "ىٰ" in c.text]
    assert len(carriers) == 1
    assert carriers[0].role is CellRole.MADD
    assert all(c.text != "ٰ" for c in word.columns)


def test_a_bare_maqsura_revived_at_a_stop_gains_a_transformed_dagger(hafs, pen):
    session = phonemize_request(hafs, "2:11:6-2:11:7", stop_refs=["2:11:6"])
    kw = dict(ref="2:11:6-2:11:7", riwayah="hafs", script="uthmani", variant={})
    view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
    carrier = next(c for c in view.words[0].columns if c.role is CellRole.MADD)
    assert carrier.text == "ىٰ"
    assert carrier.status is CellStatus.REPLACED


def test_stopping_a_munfasil_removes_its_maddah_as_a_transformation(hafs, pen):
    session = phonemize_request(hafs, "2:4:3-2:4:4", stop_refs=["2:4:3"])
    kw = dict(ref="2:4:3-2:4:4", riwayah="hafs", script="uthmani", variant={})
    view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
    carrier = next(c for c in view.words[0].columns if c.role is CellRole.MADD)
    assert carrier.text == "ا"
    assert carrier.status is CellStatus.REPLACED


@pytest.mark.parametrize(("ref", "carrier_text"), [
    ("2:29:1", "و"),
    ("2:70:8", "ى"),
])
def test_a_stopped_glide_reuses_its_written_carrier(hafs, pen, ref, carrier_text):
    _, _, view = _build(hafs, pen, ref)
    carriers = [c for c in view.words[0].columns if c.role is CellRole.MADD]
    assert [(c.text, c.status) for c in carriers] == [
        (carrier_text, CellStatus.PRESENT)
    ]
    assert carriers[0].source_character_ids


@pytest.mark.parametrize(("ref", "before", "after", "rule"), [
    ("3:74:3-3:74:4", "ن", "ي", "idgham_bi_ghunnah"),
    ("2:10:2-2:10:3", "م", "م", "idgham_shafawi"),
    ("2:16:7-2:16:8", "ت", "ت", "idgham_mutamathilayn"),
    ("23:118:1-23:118:2", "ل", "ر", "idgham_mutaqaribayn"),
    ("2:256:5-2:256:6", "د", "ت", "idgham_mutajanisayn_kamil"),
])
def test_a_cross_word_merger_marks_both_active_letters(
    hafs, pen, ref, before, after, rule
):
    session = phonemize_request(hafs, ref, stop_refs=[])
    kw = dict(ref=ref, riwayah="hafs", script="uthmani", variant={})
    bundle = build_bundle(session, **kw)
    view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
    occurrence = next(o for o in bundle.rule_occurrences if o.rule_id.value == rule)
    first = next(c for c in view.words[0].columns if before in c.text)
    second = next(c for c in view.words[1].columns if after in c.text)
    assert first.status is CellStatus.PRESENT and first.silence is None
    assert occurrence.id in first.rule_occurrence_ids
    assert occurrence.id in second.rule_occurrence_ids


@pytest.mark.parametrize(("ref", "stop", "letter", "rule"), [
    ("3:74:3-3:74:4", "3:74:3", "ن", "izhar"),
    ("2:56:3-2:56:4", "2:56:3", "ن", "izhar"),
    ("2:10:2-2:10:3", "2:10:2", "م", "izhar_shafawi"),
    ("2:8:10-2:8:11", "2:8:10", "م", "izhar_shafawi"),
])
def test_a_cancelled_cross_word_nasal_rule_recovers_sukun_on_its_letter(
    hafs, pen, ref, stop, letter, rule
):
    session = phonemize_request(hafs, ref, stop_refs=[stop])
    kw = dict(ref=ref, riwayah="hafs", script="uthmani", variant={})
    bundle = build_bundle(session, **kw)
    view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
    occurrence = next(o for o in bundle.rule_occurrences if o.rule_id.value == rule)
    column = next(c for c in view.words[0].columns if letter in c.text)
    assert column.text.endswith(pen.role("sukun"))
    assert column.status is CellStatus.REPLACED
    assert occurrence.id in column.rule_occurrence_ids


def test_lam_shamsiyyah_is_only_on_the_silent_lam(hafs, pen):
    _, bundle, view = _build(hafs, pen, "1:1")
    occurrence = next(o for o in bundle.rule_occurrences if o.rule_id.value == "lam_shamsiyyah")
    columns = [c for w in view.words for c in w.columns]
    named = [c for c in columns if occurrence.id in c.rule_occurrence_ids]
    assert len(named) == 1
    assert named[0].text.startswith("ل")
    assert not named[0].owned_sound_ids and named[0].presented_sound_ids


def test_muqattaat_letters_remain_base_cells_with_folded_maddah(hafs, pen):
    _, _, view = _build(hafs, pen, "3:1")
    columns = view.words[0].columns
    assert all(c.role is CellRole.LETTER for c in columns)
    assert any("ٓ" in c.text for c in columns)


def test_iltiqa_sound_and_column_live_on_the_boundary(hafs, pen):
    _, bundle, view = _build(hafs, pen, "3:1-3:2")
    occurrence = next(o for o in bundle.rule_occurrences if o.rule_id.value == "iltiqa_haraka")
    boundary = next(b for b in view.boundaries if b.boundary_id in occurrence.boundary_ids)
    assert [s.sound_id for s in boundary.sounds] == list(occurrence.sound_ids)
    assert any(c.status is CellStatus.INSERTED for c in boundary.columns)
    assert all(
        s.sound_id not in occurrence.sound_ids
        for word in view.words for s in word.sounds
    )
