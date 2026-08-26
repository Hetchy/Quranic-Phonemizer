"""The transformed CellView is a complete renderer-ready projection."""
from __future__ import annotations

import pytest

from quranic_phonemizer.api import recitation
from quranic_phonemizer.analysis.build import build_bundle
from quranic_phonemizer.analysis.cells import (
    CellRole,
    CellSide,
    CellStatus,
    build_cell_view,
)
from quranic_phonemizer.analysis.facts import analyse
from quranic_phonemizer.analysis.inscription import inscribe
from quranic_phonemizer.analysis.source import build_source_view
from quranic_phonemizer.model.address import Riwayah, Script
from quranic_phonemizer.model.canon import Quality, VowelForm
from quranic_phonemizer.model.performance import Aspect, Consonant, Vowel
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


def test_tanween_keeps_the_vowel_slot_it_is_written_on(hafs, pen):
    _, _, view = _build(hafs, pen, "2:29")
    tanween = next(
        column for word in view.words for column in word.columns
        if column.role is CellRole.TANWEEN and column.text == "ٍ"
    )

    assert tanween.attached_to_column_id is not None


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


def test_madd_iwad_inserts_an_alif_when_the_rasm_has_no_carrier(hafs, pen):
    _, bundle, view = _build(hafs, pen, "2:22:11")
    names = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }
    carrier = next(
        column for column in view.words[0].columns
        if column.status is CellStatus.INSERTED
        and column.role is CellRole.MADD
    )
    assert carrier.text == "ا"
    assert not carrier.source_character_ids
    assert {names[item] for item in carrier.rule_occurrence_ids} == {
        "madd_iwad", "madd_tabii"
    }


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


def test_the_small_waw_with_maddah_is_the_muttasil_carrier(hafs, pen):
    _, bundle, view = _build(hafs, pen, "17:7")
    word_id = next(word.id for word in bundle.words if word.ref == "17:7:12")
    word = next(word for word in view.words if word.word_id == word_id)
    carrier = next(column for column in word.columns if column.text == "ۥٓ")
    names = {
        bundle.rule_occurrences[item.value].rule_id.value
        for item in carrier.rule_occurrence_ids
    }

    assert carrier.role is CellRole.MADD
    assert carrier.status is CellStatus.PRESENT
    assert carrier.source_character_ids
    assert names == {"madd_muttasil"}
    assert not any(
        column.status is CellStatus.INSERTED
        and column.role is CellRole.MADD
        for column in word.columns
    )


@pytest.mark.parametrize(("stop_refs", "rule"), [
    ((), "madd_tabii"),
    (("2:124:3",), "madd_arid_lissukun"),
])
def test_ibrahim_small_yaa_remains_the_i_carrier(
    hafs, pen, stop_refs, rule
):
    session = phonemize_request(hafs, "2:124", stop_refs=stop_refs)
    kw = dict(ref="2:124", riwayah="hafs", script="uthmani", variant={})
    bundle = build_bundle(session, **kw)
    view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
    word_id = next(word.id for word in bundle.words if word.ref == "2:124:3")
    word = next(word for word in view.words if word.word_id == word_id)
    carrier = next(column for column in word.columns if column.text == "ۧ")
    names = {
        bundle.rule_occurrences[item.value].rule_id.value
        for item in carrier.rule_occurrence_ids
    }

    assert carrier.role is CellRole.MADD
    assert carrier.status is CellStatus.PRESENT
    assert carrier.source_character_ids
    assert names == {rule}
    assert not any(
        column.status is CellStatus.INSERTED
        and column.role is CellRole.MADD
        for column in word.columns
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
    assert carrier.text == pen.performed_carrier(Quality.KUBRA)[1] + "ٰ"
    assert carrier.source_character_ids


@pytest.mark.parametrize("ref", ["2:5:2", "11:41:6"])
def test_a_maqsura_and_its_dagger_are_one_native_carrier_cell(hafs, pen, ref):
    _, _, view = _build(hafs, pen, ref)
    word = view.words[0]
    carriers = [c for c in word.columns if "ىٰ" in c.text]
    assert len(carriers) == 1
    assert carriers[0].role is CellRole.MADD
    assert all(c.text != "ٰ" for c in word.columns)


def test_a_long_i_maqsura_never_gains_a_dagger_alif(hafs, pen):
    _, _, view = _build(hafs, pen, "2:11:6")  # فِى
    carrier = next(c for c in view.words[0].columns if c.role is CellRole.MADD)
    assert carrier.text == "ى"
    assert carrier.status is CellStatus.PRESENT


def test_madd_iwad_reuses_a_maqsura_as_a_transformed_dagger_carrier(hafs, pen):
    _, _, view = _build(hafs, pen, "2:2:6")  # هُدًى
    word = view.words[0]
    carrier = next(c for c in word.columns if c.role is CellRole.MADD)
    assert carrier.text == "ىٰ"
    assert carrier.status is CellStatus.REPLACED
    assert carrier.source_character_ids
    assert not any(
        c.status is CellStatus.INSERTED and c.role is CellRole.MADD
        for c in word.columns
    )


def test_ibdal_hamza_reuses_the_source_hamza_as_a_replacement(hafs, pen):
    _, _, view = _build(hafs, pen, "46:4:18")
    word = view.words[0]
    carrier = next(c for c in word.columns if c.role is CellRole.MADD)
    assert carrier.text == pen.performed_carrier(Quality.I)[1]
    assert carrier.status is CellStatus.REPLACED
    assert carrier.source_character_ids
    assert not any(
        c.status is CellStatus.INSERTED and c.role is CellRole.MADD
        for c in word.columns
    )


def test_divine_name_inserts_a_dagger_not_a_full_alif(hafs, pen):
    _, _, view = _build(hafs, pen, "2:15:1")
    inserted = [
        c for c in view.words[0].columns
        if c.status is CellStatus.INSERTED and c.role is CellRole.MADD
    ]
    assert [c.text for c in inserted] == ["ٰ"]


def test_starting_on_a_shaddad_letter_removes_the_shadda(hafs, pen):
    _, _, view = _build(hafs, pen, "57:28:11")
    first = view.words[0].columns[0]
    assert first.text == "ر"
    assert first.status is CellStatus.REPLACED


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


@pytest.mark.parametrize("ref", ["2:29:1", "2:70:8"])
def test_a_stopped_glides_madd_rule_is_only_on_its_carrier(hafs, pen, ref):
    _, bundle, view = _build(hafs, pen, ref)
    occurrence = next(
        o for o in bundle.rule_occurrences if o.rule_id.value == "madd_tabii"
    )
    named = [
        c for c in view.words[0].columns
        if occurrence.id in c.rule_occurrence_ids
    ]
    assert len(named) == 1
    assert named[0].role is CellRole.MADD


def test_a_performed_madd_rule_is_only_on_its_carrier(hafs, pen):
    _, bundle, view = _build(hafs, pen, "1:1")
    occurrences = {
        occurrence.id for occurrence in bundle.rule_occurrences
        if occurrence.rule_id.value == "madd_tabii"
    }
    named = [
        column for word in view.words for column in word.columns
        if occurrences.intersection(column.rule_occurrence_ids)
    ]

    assert named
    assert all(column.role is CellRole.MADD for column in named)


@pytest.mark.parametrize(("ref", "stopped", "carrier_text"), [
    ("11:64:1-11:64:3", "11:64:2", "ۦ"),
    ("2:17:8-2:17:10", "2:17:9", "ۥ"),
])
def test_stopped_silah_keeps_its_dropped_haraka_with_the_carrier(
    hafs, pen, ref, stopped, carrier_text
):
    session = phonemize_request(
        hafs, ref, stop_refs=[stopped]
    )
    kw = dict(
        ref=ref, riwayah="hafs", script="uthmani", variant={}
    )
    bundle = build_bundle(session, **kw)
    view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
    occurrence = next(
        o for o in bundle.rule_occurrences
        if o.rule_id.value == "waqf_silah_drop"
    )
    word_id = next(w.id for w in bundle.words if w.ref == stopped)
    word = next(w for w in view.words if w.word_id == word_id)
    columns = {column.id: column for column in word.columns}
    haraka = next(
        column for column in word.columns
        if occurrence.id in column.rule_occurrence_ids
        and column.role is CellRole.HARAKA
    )
    carrier = next(
        column for column in word.columns
        if column.text == carrier_text
    )
    group = next(g for g in word.groups if carrier.id in g.column_ids)

    assert group.kind.value == "vowel"
    assert group.column_ids == (haraka.id, carrier.id)
    assert haraka.attached_to_column_id == carrier.id
    assert columns[carrier.id].role is CellRole.MADD
    assert occurrence.id in carrier.rule_occurrence_ids
    assert all(columns[column].status is CellStatus.DROPPED
               for column in group.column_ids)
    assert all(
        columns[column].silence == occurrence.id
        for column in group.column_ids
    )
    assert occurrence.id in columns[carrier.id].rule_occurrence_ids


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


@pytest.mark.parametrize(("ref", "stop", "letter"), [
    ("3:74:3-3:74:4", "3:74:3", "ن"),
    ("2:10:2-2:10:3", "2:10:2", "م"),
    ("2:61:57-2:61:58", "2:61:57", "و"),
    ("2:16:7-2:16:8", "2:16:7", "ت"),
    ("23:118:1-23:118:2", "23:118:1", "ل"),
    ("2:256:5-2:256:6", "2:256:5", "د"),
    ("2:19:14", "2:19:14", "ق"),
    ("2:19:7", "2:19:7", "د"),
])
def test_a_stopped_consonant_recovers_sukun_on_its_letter(
    hafs, pen, ref, stop, letter
):
    session = phonemize_request(hafs, ref, stop_refs=[stop])
    kw = dict(ref=ref, riwayah="hafs", script="uthmani", variant={})
    view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
    column = next(c for c in view.words[0].columns if letter in c.text)
    assert column.text.endswith(pen.role("sukun"))
    assert column.status is CellStatus.REPLACED


def test_an_internal_mini_noon_does_not_gain_pausal_sukun(hafs, pen):
    ref = "21:88"
    session = phonemize_request(hafs, ref, stop_refs=["21:88:7"])
    kw = dict(ref=ref, riwayah="hafs", script="uthmani", variant={})
    bundle = build_bundle(session, **kw)
    view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
    word_id = next(w.id for w in bundle.words if w.ref == "21:88:7")
    word = next(w for w in view.words if w.word_id == word_id)
    mini_noon = next(c for c in word.columns if "ۨ" in c.text)

    assert mini_noon.text == "ـۨ"
    assert mini_noon.status is CellStatus.PRESENT
    assert all(not c.text.endswith(pen.role("sukun")) for c in word.columns)


def test_lam_shamsiyyah_is_only_on_the_silent_lam(hafs, pen):
    _, bundle, view = _build(hafs, pen, "1:1")
    occurrences = [
        item for item in bundle.rule_occurrences
        if item.rule_id.value == "lam_shamsiyyah"
    ]
    rules = {item.id: item.rule_id.value for item in bundle.rule_occurrences}
    columns = [c for w in view.words for c in w.columns]
    for occurrence in occurrences:
        named = [c for c in columns if occurrence.id in c.rule_occurrence_ids]
        assert len(named) == 1
        assert named[0].text.startswith("ل")
        assert not named[0].owned_sound_ids and named[0].presented_sound_ids
        assert named[0].silence == occurrence.id
        assert [rules[item] for item in named[0].rule_occurrence_ids] == ["lam_shamsiyyah"]


def test_muqattaat_expand_to_flat_named_letter_runs(hafs, pen):
    _, _, view = _build(hafs, pen, "3:1")
    word = view.words[0]
    columns = {column.id: column for column in word.columns}
    assert tuple(
        "".join(columns[item].text for item in run.column_ids)
        for run in word.runs
    ) == ("أَلِفْ", "لَآم", "مِّيٓمْ")


@pytest.mark.parametrize("riwayah", (Riwayah.HAFS, Riwayah.WARSH))
def test_ishmam_keeps_the_fatha_visible_and_names_the_noon(riwayah):
    reading = recitation(riwayah)
    pen = pen_for(reading.inventory(Script.UTHMANI))
    session = phonemize_request(reading, "12:11")
    kw = dict(
        ref="12:11", riwayah=riwayah.value, script="uthmani", variant={}
    )
    bundle = build_bundle(session, **kw)
    view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
    occurrence = next(o for o in bundle.rule_occurrences if o.rule_id.value == "ishmam")
    word_id = next(w.id for w in bundle.words if w.ref == "12:11:6")
    word = next(w for w in view.words if w.word_id == word_id)
    meem = next(c for c in word.columns if c.text == "م")
    fatha = next(c for c in word.columns if c.attached_to_column_id == meem.id)
    noon = next(c for c in word.columns if c.text.startswith("ن"))

    assert fatha.text == "َ"
    assert occurrence.id not in fatha.rule_occurrence_ids
    assert occurrence.id in noon.rule_occurrence_ids
    assert all("۫" not in c.text for c in word.columns)


def test_tanween_keeps_vowel_colour_on_its_sound_not_its_glyph(hafs, pen):
    _, bundle, view = _build(hafs, pen, "4:1")
    word_id = next(word.id for word in bundle.words if word.ref == "4:1:16")
    word = next(word for word in view.words if word.word_id == word_id)
    tafkheem = next(
        occurrence for occurrence in bundle.rule_occurrences
        if occurrence.rule_id.value == "tafkheem"
        and word_id in occurrence.word_ids
        and len(occurrence.sound_ids) == 2
    )
    idgham = next(
        occurrence for occurrence in bundle.rule_occurrences
        if occurrence.rule_id.value == "idgham_bi_ghunnah"
        and word_id in occurrence.word_ids
    )
    tanween = next(column for column in word.columns if column.role is CellRole.TANWEEN)
    vowel = next(
        sound
        for sound in word.sounds
        if tanween.id in sound.column_ids and sound.sound_id in tafkheem.sound_ids
    )

    assert tafkheem.id not in tanween.rule_occurrence_ids
    assert tafkheem.id in vowel.rule_occurrence_ids
    assert idgham.id in tanween.rule_occurrence_ids


@pytest.mark.parametrize(("ref", "mark"), [
    ("3:1-3:2", "َ"),
    ("2:61:30-2:61:31", "ِ"),
])
def test_iltiqa_sound_and_column_live_on_the_boundary(hafs, pen, ref, mark):
    _, bundle, view = _build(hafs, pen, ref)
    occurrence = next(o for o in bundle.rule_occurrences if o.rule_id.value == "iltiqa_haraka")
    boundary = next(b for b in view.boundaries if b.boundary_id in occurrence.boundary_ids)
    inserted = [
        column for column in boundary.columns
        if column.status is CellStatus.INSERTED
    ]

    assert [s.sound_id for s in boundary.sounds] == list(occurrence.sound_ids)
    assert len(inserted) == 1
    assert inserted[0].text == mark
    assert inserted[0].role is CellRole.HARAKA
    assert not inserted[0].source_character_ids
    assert not inserted[0].source_unit_ids
    assert inserted[0].anchor_unit_id is not None
    assert inserted[0].side is CellSide.AFTER
    assert inserted[0].owned_sound_ids == occurrence.sound_ids
    assert inserted[0].rule_occurrence_ids == (occurrence.id,)
    assert all(
        s.sound_id not in occurrence.sound_ids
        for word in view.words for s in word.sounds
    )


def test_warsh_naql_stays_on_the_written_host_haraka():
    warsh = recitation(Riwayah.WARSH)
    pen = pen_for(warsh.inventory(Script.UTHMANI))
    session = phonemize_request(warsh, "23:1")
    kw = dict(ref="23:1", riwayah="warsh", script="uthmani", variant={})
    bundle = build_bundle(session, **kw)
    view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
    occurrence = next(o for o in bundle.rule_occurrences if o.rule_id.value == "naql")
    host, qata = view.words[:2]

    host_haraka = host.columns[-1]
    qata_alif, qata_haraka = qata.columns[:2]
    boundary = next(b for b in view.boundaries if b.boundary_id in occurrence.boundary_ids)

    assert host_haraka.text == "َ"
    assert host_haraka.role is CellRole.HARAKA
    assert host_haraka.status is CellStatus.PRESENT
    assert host_haraka.owned_sound_ids == occurrence.sound_ids
    assert occurrence.id in host_haraka.rule_occurrence_ids

    assert qata_alif.text == "ا"
    assert qata_alif.status is CellStatus.DROPPED
    assert qata_alif.silence == occurrence.id
    assert qata_haraka.text == "َ"
    assert qata_haraka.status is CellStatus.DROPPED
    assert qata_haraka.silence == occurrence.id
    assert qata_haraka.attached_to_column_id == qata_alif.id
    assert occurrence.id in qata_haraka.rule_occurrence_ids

    assert not any(occurrence.id in column.rule_occurrence_ids for column in boundary.columns)
    assert not any(sound.sound_id in occurrence.sound_ids for sound in boundary.sounds)


def test_warsh_native_iqlab_meem_is_its_own_source_backed_cell():
    warsh = recitation(Riwayah.WARSH)
    pen = pen_for(warsh.inventory(Script.UTHMANI))
    ref = "2:10-2:11"
    session = phonemize_request(warsh, ref)
    kw = dict(ref=ref, riwayah="warsh", script="uthmani", variant={})
    bundle = build_bundle(session, **kw)
    view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
    occurrence = next(o for o in bundle.rule_occurrences if o.rule_id.value == "iqlab")
    word = next(
        word for word in view.words
        if any(column.text == "ۢ" for column in word.columns)
    )
    meem = next(column for column in word.columns if column.text == "ۢ")
    tanween = next(column for column in word.columns if column.role is CellRole.TANWEEN)

    assert meem.source_character_ids
    assert meem.source_unit_ids
    assert meem.status is CellStatus.PRESENT
    assert meem.owned_sound_ids == occurrence.sound_ids
    assert meem.rule_occurrence_ids == (occurrence.id,)
    assert meem.attached_to_column_id == tanween.attached_to_column_id
    assert tanween.owned_sound_ids
    assert occurrence.id not in tanween.rule_occurrence_ids


@pytest.mark.slow
def test_every_stopped_consonant_in_the_corpus_projects_its_sukun(hafs, pen):
    """Audit every word, including every cancelled cross-word rule and qalqala."""
    for surah in range(1, 115):
        for ayah in range(1, len(hafs.corpus.surah_info[str(surah)]) + 1):
            ref = f"{surah}:{ayah}"
            draft = phonemize_request(hafs, ref)
            stops = [str(word.location) for word in draft.score.words[:-1]]
            session = phonemize_request(hafs, ref, stop_refs=stops)
            kw = dict(ref=ref, riwayah="hafs", script="uthmani", variant={})
            view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
            facts = analyse(session, packaged_alphabet())
            source = build_source_view(session)
            written = inscribe(session)
            slot_of = {
                unit.id.value: written.slot_of[min(c.value for c in unit.character_ids)]
                for unit in source.units if unit.character_ids
            }
            pausal = {
                slot for edge in facts.silences
                if edge.aspect is Aspect.VOWEL and edge.by is not None
                and facts.occurrences[edge.by].boundary is not None
                for slot in edge.slots
            }
            for word in view.words:
                consonants = [
                    col for col in word.columns
                    if col.role is CellRole.LETTER and any(
                        isinstance(facts.sounds[s.value].value, Consonant)
                        for s in col.owned_sound_ids
                    )
                ]
                if not consonants:
                    continue
                final = consonants[-1]
                needs_sukun = any(
                    slot_of[u.value] in pausal or facts.slots[
                        facts.slot_index[slot_of[u.value]]
                    ].nucleus.stopped.form is VowelForm.ABSENT
                    for u in final.source_unit_ids if u.value in slot_of
                )
                if needs_sukun:
                    assert final.text.endswith(pen.role("sukun")), (
                        ref, word.word_id, final
                    )
