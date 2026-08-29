"""The transformed CellView is a complete renderer-ready projection."""

from __future__ import annotations

import pytest

from quranic_phonemizer.api import recitation
from quranic_phonemizer.analysis.build import build_bundle
from quranic_phonemizer.analysis.cells import (
    CellRole,
    CellSide,
    CellStatus,
    CellTier,
    build_cell_view,
)
from quranic_phonemizer.analysis.facts import analyse
from quranic_phonemizer.analysis.inscription import inscribe
from quranic_phonemizer.analysis.source import build_source_view
from quranic_phonemizer.analysis.source_dtos import LiteralSilence
from quranic_phonemizer.model.address import Riwayah, Script
from quranic_phonemizer.model.canon import CanonLetter, Onset, Quality, VowelForm
from quranic_phonemizer.model.performance import Aspect, Consonant, Vowel
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.render.alphabet import packaged_alphabet
from quranic_phonemizer.riwayat.warsh.resources import corpus as warsh_corpus
from quranic_phonemizer.session import phonemize_request


@pytest.fixture(scope="module")
def pen(hafs):
    return pen_for(hafs.inventory(Script.UTHMANI))


def _build(hafs, pen, ref: str, *, extra_phonemes=frozenset()):
    session = phonemize_request(hafs, ref)
    kw = dict(ref=ref, riwayah="hafs", script="uthmani", variant={})
    bundle = build_bundle(session, extra_phonemes=extra_phonemes, **kw)
    view = build_cell_view(
        session,
        spelling="transformed",
        pen=pen,
        extra_phonemes=extra_phonemes,
        **kw,
    )
    return session, bundle, view


def _build_warsh(ref: str, *, stop_refs=(), extra_phonemes=frozenset()):
    warsh = recitation(Riwayah.WARSH)
    warsh_pen = pen_for(warsh.inventory(Script.UTHMANI))
    session = phonemize_request(warsh, ref, stop_refs=stop_refs)
    kw = dict(ref=ref, riwayah="warsh", script="uthmani", variant={})
    bundle = build_bundle(session, extra_phonemes=extra_phonemes, **kw)
    view = build_cell_view(
        session,
        spelling="transformed",
        pen=warsh_pen,
        extra_phonemes=extra_phonemes,
        **kw,
    )
    return session, bundle, view


def test_sukun_is_folded_into_its_main_letter(hafs, pen):
    _, _, view = _build(hafs, pen, "1:1")
    assert all(c.role is not CellRole.SUKUN for w in view.words for c in w.columns)
    assert any(
        c.tier.value == "main" and "ْ" in c.text for w in view.words for c in w.columns
    )


def test_a_replaced_warsh_sukun_separates_its_realized_vowel_mark():
    _, bundle, view = _build_warsh("35:28")
    word_id = next(word.id for word in bundle.words if word.ref == "35:28:13")
    word = next(item for item in view.words if item.word_id == word_id)
    carrier = next(column for column in word.columns if column.text == "ؤ")
    mark = next(
        column for column in word.columns
        if column.role is CellRole.HARAKA
        and column.attached_to_column_id == carrier.id
    )

    assert {bundle.sounds[sound.value].token for sound in carrier.owned_sound_ids} == {"ʔ"}
    assert {bundle.sounds[sound.value].token for sound in mark.owned_sound_ids} == {"u"}
    assert all(
        mark.id in sound.column_ids
        for sound in word.sounds
        if sound.sound_id in mark.owned_sound_ids
    )


def test_joined_wasl_ibdal_transforms_its_root_carrier_across_the_boundary():
    # Warsh: يَّقُولُ اُ۪يذَن
    _, bundle, view = _build_warsh("9:49")
    before = next(word for word in bundle.words if word.ref == "9:49:3")
    after = next(word for word in bundle.words if word.ref == "9:49:4")
    merger = next(
        item for item in bundle.mergers
        if item.before_word_id == before.id and item.after_word_id == after.id
    )
    bridge = next(
        item for boundary in view.boundaries for item in boundary.bridges
        if item.merger_id == merger.id
    )
    before_word = view.words[before.id.value]
    after_word = view.words[after.id.value]
    presenter = next(
        column for column in before_word.columns
        if merger.sound_id in column.presented_sound_ids
    )
    carrier = next(
        column for column in after_word.columns
        if merger.sound_id in column.owned_sound_ids
    )
    ibdal = next(
        occurrence.id for occurrence in bundle.rule_occurrences
        if occurrence.rule_id.value == "ibdal_hamza"
        and merger.sound_id in occurrence.sound_ids
    )

    assert presenter.text == "ُ"
    assert presenter.role is CellRole.HARAKA
    assert carrier.text == "و"
    assert carrier.role is CellRole.MADD
    assert carrier.status is CellStatus.REPLACED
    assert carrier.source_unit_ids
    assert bridge.before_column_ids == (presenter.id,)
    assert bridge.after_column_ids == (carrier.id,)
    assert bridge.sound.column_ids == (presenter.id, carrier.id)
    assert [
        column.id for word in (before_word, after_word) for column in word.columns
        if ibdal in column.rule_occurrence_ids
    ] == [carrier.id]
    assert all(
        not (column.status is CellStatus.INSERTED and column.text == "و")
        for column in before_word.columns
    )


def test_joined_wasl_ibdal_long_a_has_tarqeeq_on_its_carrier():
    _, bundle, view = _build_warsh("10:15")
    target = next(word for word in bundle.words if word.ref == "10:15:11")
    word = next(item for item in view.words if item.word_id == target.id)
    rules = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }
    carrier = next(
        column
        for column in word.columns
        if column.role is CellRole.MADD
        and any(
            bundle.sounds[sound.value].token == "a:"
            for sound in column.owned_sound_ids
        )
    )

    assert {
        rules[occurrence]
        for occurrence in carrier.rule_occurrence_ids
        if rules[occurrence] in {"tafkheem", "tarqeeq"}
    } == {"tarqeeq"}


def test_a_compact_hamza_seat_keeps_its_written_haraka_attached():
    _, _, view = _build_warsh("37:52")
    word = view.words[1]
    haraka = next(column for column in word.columns if column.role is CellRole.HARAKA)

    assert haraka.attached_to_column_id == word.columns[0].id


def test_tanween_keeps_the_vowel_slot_it_is_written_on(hafs, pen):
    _, _, view = _build(hafs, pen, "2:29")
    tanween = next(
        column
        for word in view.words
        for column in word.columns
        if column.role is CellRole.TANWEEN and column.text == "ٍ"
    )

    assert tanween.attached_to_column_id is not None


@pytest.mark.parametrize("ref", ["1:1:1", "2:10:3"])
def test_a_pausal_sukun_changes_the_final_consonant_cell(hafs, pen, ref):
    session, _, view = _build(hafs, pen, ref)
    facts = analyse(session, packaged_alphabet())
    column = next(
        col
        for col in view.words[0].columns
        if col.text.endswith(pen.role("sukun")) and col.status is CellStatus.REPLACED
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
        for col in view.words[0].columns
        if col.role is CellRole.MADD
    )


@pytest.mark.parametrize(
    ("ref", "base", "mark"),
    [
        ("1:2", "أ", "َ"),
        ("20:24:1", "إ", "ِ"),
        ("2:58:3", "أ", "ُ"),
    ],
)
def test_started_wasl_is_a_seated_hamza_plus_its_vowel(hafs, pen, ref, base, mark):
    session, _, view = _build(hafs, pen, ref)
    facts = analyse(session, packaged_alphabet())
    first = view.words[0]
    assert first.columns[0].text == base
    assert first.columns[0].status is CellStatus.REPLACED
    assert first.columns[1].text == mark
    assert first.columns[1].status is CellStatus.INSERTED
    assert all(
        isinstance(facts.sounds[s.value].value, Consonant)
        for s in first.columns[0].owned_sound_ids
    )
    assert all(
        isinstance(facts.sounds[s.value].value, Vowel)
        for s in first.columns[1].owned_sound_ids
    )


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
    iwad = next(o for o in bundle.rule_occurrences if o.rule_id.value == "madd_iwad")
    group = next(g for g in word.groups if set(g.sound_ids) & set(iwad.sound_ids))
    columns = {c.id: c for c in word.columns}
    quality, carrier = (columns[c] for c in group.column_ids)
    assert quality.role is CellRole.HARAKA
    assert quality.status is CellStatus.REPLACED
    assert quality.text == pen.short_vowel(
        analyse(session, packaged_alphabet())
        .sounds[iwad.sound_ids[0].value]
        .value.quality
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
        column
        for column in view.words[0].columns
        if column.status is CellStatus.INSERTED and column.role is CellRole.MADD
    )
    assert carrier.text == "ا"
    assert not carrier.source_character_ids
    assert {names[item] for item in carrier.rule_occurrence_ids} == {
        "madd_iwad",
        "madd_tabii",
        "tarqeeq",
    }


def test_a_written_small_vowel_is_the_carrier_not_a_stray_cell(hafs, pen):
    session, bundle, view = _build(hafs, pen, "3:103:19")
    facts = analyse(session, packaged_alphabet())
    word = view.words[0]
    long_sound = next(
        s
        for s in bundle.sounds
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
        column.status is CellStatus.INSERTED and column.role is CellRole.MADD
        for column in word.columns
    )


@pytest.mark.parametrize(
    ("stop_refs", "rule"),
    [
        ((), "madd_tabii"),
        (("2:124:3",), "madd_arid_lissukun"),
    ],
)
def test_ibrahim_small_yaa_remains_the_i_carrier(hafs, pen, stop_refs, rule):
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
        column.status is CellStatus.INSERTED and column.role is CellRole.MADD
        for column in word.columns
    )


def test_imala_uses_its_written_ya_carrier(hafs, pen):
    session, bundle, view = _build(hafs, pen, "11:41:6")
    facts = analyse(session, packaged_alphabet())
    sound = next(
        s
        for s in bundle.sounds
        if isinstance(facts.sounds[s.id.value].value, Vowel)
        and facts.sounds[s.id.value].value.quality.value == "e"
    )
    group = next(g for g in view.words[0].groups if sound.id in g.sound_ids)
    columns = {c.id: c for c in view.words[0].columns}
    carrier = next(
        columns[c] for c in group.column_ids if columns[c].role is CellRole.MADD
    )
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
        c
        for c in view.words[0].columns
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


@pytest.mark.parametrize(
    ("ref", "carrier_text"),
    [
        ("2:29:1", "و"),
        ("2:70:8", "ى"),
    ],
)
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
    named = [c for c in view.words[0].columns if occurrence.id in c.rule_occurrence_ids]
    assert len(named) == 1
    assert named[0].role is CellRole.MADD


@pytest.mark.parametrize(
    ("riwayah", "ref"),
    [
        ("hafs", "2:29:1"),
        ("hafs", "2:70:8"),
        ("warsh", "2:28:1"),
        ("warsh", "2:69:8"),
    ],
)
def test_a_stopped_glides_diacritic_drop_stays_on_its_haraka(
    hafs, pen, riwayah, ref
):
    if riwayah == "hafs":
        _, bundle, view = _build(hafs, pen, ref)
    else:
        _, bundle, view = _build_warsh(ref)
    occurrence = next(
        item
        for item in bundle.rule_occurrences
        if item.rule_id.value == "waqf_diacritic_drop"
    )
    carrier = next(
        column for column in view.words[0].columns if column.role is CellRole.MADD
    )
    dropped = next(
        column
        for column in view.words[0].columns
        if column.role is CellRole.HARAKA and column.status is CellStatus.DROPPED
    )

    assert occurrence.id not in carrier.rule_occurrence_ids
    assert dropped.silence == occurrence.id
    assert occurrence.id in dropped.rule_occurrence_ids


def test_a_performed_madd_rule_is_only_on_its_carrier(hafs, pen):
    _, bundle, view = _build(hafs, pen, "1:1")
    occurrences = {
        occurrence.id
        for occurrence in bundle.rule_occurrences
        if occurrence.rule_id.value == "madd_tabii"
    }
    named = [
        column
        for word in view.words
        for column in word.columns
        if occurrences.intersection(column.rule_occurrence_ids)
    ]

    assert named
    assert all(column.role is CellRole.MADD for column in named)


@pytest.mark.parametrize(
    ("ref", "stopped", "carrier_text"),
    [
        ("11:64:1-11:64:3", "11:64:2", "ۦ"),
        ("2:17:8-2:17:10", "2:17:9", "ۥ"),
    ],
)
def test_stopped_silah_keeps_its_dropped_haraka_with_the_carrier(
    hafs, pen, ref, stopped, carrier_text
):
    session = phonemize_request(hafs, ref, stop_refs=[stopped])
    kw = dict(ref=ref, riwayah="hafs", script="uthmani", variant={})
    bundle = build_bundle(session, **kw)
    view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
    occurrence = next(
        o for o in bundle.rule_occurrences if o.rule_id.value == "waqf_silah_drop"
    )
    word_id = next(w.id for w in bundle.words if w.ref == stopped)
    word = next(w for w in view.words if w.word_id == word_id)
    columns = {column.id: column for column in word.columns}
    haraka = next(
        column
        for column in word.columns
        if occurrence.id in column.rule_occurrence_ids
        and column.role is CellRole.HARAKA
    )
    carrier = next(column for column in word.columns if column.text == carrier_text)
    group = next(g for g in word.groups if carrier.id in g.column_ids)

    assert group.kind.value == "vowel"
    assert group.column_ids == (haraka.id, carrier.id)
    assert haraka.attached_to_column_id == carrier.id
    assert columns[carrier.id].role is CellRole.MADD
    assert occurrence.id in carrier.rule_occurrence_ids
    assert all(
        columns[column].status is CellStatus.DROPPED for column in group.column_ids
    )
    assert all(columns[column].silence == occurrence.id for column in group.column_ids)
    assert occurrence.id in columns[carrier.id].rule_occurrence_ids


@pytest.mark.parametrize(
    ("ref", "before", "after", "rule"),
    [
        ("3:74:3-3:74:4", "ن", "ي", "idgham_bi_ghunnah"),
        ("2:10:2-2:10:3", "م", "م", "idgham_shafawi"),
        ("2:16:7-2:16:8", "ت", "ت", "idgham_mutamathilayn"),
        ("23:118:1-23:118:2", "ل", "ر", "idgham_mutaqaribayn"),
        ("2:256:5-2:256:6", "د", "ت", "idgham_mutajanisayn_kamil"),
    ],
)
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


@pytest.mark.parametrize(
    ("ref", "stop", "letter"),
    [
        ("3:74:3-3:74:4", "3:74:3", "ن"),
        ("2:10:2-2:10:3", "2:10:2", "م"),
        ("2:61:57-2:61:58", "2:61:57", "و"),
        ("2:16:7-2:16:8", "2:16:7", "ت"),
        ("23:118:1-23:118:2", "23:118:1", "ل"),
        ("2:256:5-2:256:6", "2:256:5", "د"),
        ("2:19:14", "2:19:14", "ق"),
        ("2:19:7", "2:19:7", "د"),
    ],
)
def test_a_stopped_consonant_recovers_sukun_on_its_letter(hafs, pen, ref, stop, letter):
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
        item
        for item in bundle.rule_occurrences
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
        assert [rules[item] for item in named[0].rule_occurrence_ids] == [
            "lam_shamsiyyah"
        ]


def test_muqattaat_expand_to_flat_named_letter_runs(hafs, pen):
    _, _, view = _build(hafs, pen, "3:1")
    word = view.words[0]
    columns = {column.id: column for column in word.columns}
    assert tuple(
        "".join(columns[item].text for item in run.column_ids) for run in word.runs
    ) == ("أَلِفْ", "لَآم", "مِّيٓمْ")


@pytest.mark.parametrize("riwayah", (Riwayah.HAFS, Riwayah.WARSH))
def test_ishmam_keeps_the_fatha_visible_and_names_the_noon(riwayah):
    reading = recitation(riwayah)
    pen = pen_for(reading.inventory(Script.UTHMANI))
    session = phonemize_request(reading, "12:11")
    kw = dict(ref="12:11", riwayah=riwayah.value, script="uthmani", variant={})
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


def test_tanween_vowel_renders_emphatic_without_a_weight_label(hafs, pen):
    _, bundle, view = _build(
        hafs, pen, "4:1", extra_phonemes=frozenset({"emphatic_fatha"})
    )
    word_id = next(word.id for word in bundle.words if word.ref == "4:1:16")
    word = next(word for word in view.words if word.word_id == word_id)
    tafkheem = next(
        occurrence
        for occurrence in bundle.rule_occurrences
        if occurrence.rule_id.value == "tafkheem"
        and word_id in occurrence.word_ids
        and len(occurrence.sound_ids) == 2
    )
    idgham = next(
        occurrence
        for occurrence in bundle.rule_occurrences
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
    assert tafkheem.id not in vowel.rule_occurrence_ids
    assert bundle.sounds[vowel.sound_id.value].token.startswith("aˤ")
    assert idgham.id in tanween.rule_occurrence_ids


def test_warsh_pronounced_raa_lam_and_a_carriers_have_one_weight_identity():
    _, bundle, view = _build_warsh("32:4")
    rules = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }
    weights = {"tafkheem", "tarqeeq"}

    for word in view.words:
        for column in word.columns:
            named = {
                rules[item]
                for item in column.rule_occurrence_ids
                if rules[item] in weights
            }
            sounds = tuple(
                dict.fromkeys(
                    (
                        *column.owned_sound_ids,
                        *column.presented_sound_ids,
                    )
                )
            )
            pronounced_weight_letter = (
                column.role is CellRole.LETTER
                and any(letter in column.text for letter in "رل")
                and sounds
                and column.silence is None
            )
            pronounced_a_carrier = column.role is CellRole.MADD and any(
                bundle.sounds[sound.value].token.startswith(("a", "aˤ"))
                for sound in sounds
            )
            if pronounced_weight_letter or pronounced_a_carrier:
                assert len(named) == 1, (word.word_id, column.text, named)
            if column.role is CellRole.HARAKA and "َ" in column.text:
                assert not named, (word.word_id, column.text, named)


def test_joined_shortened_long_a_has_no_weight_identity_on_its_base():
    """A carrier dropped before wasl leaves short /a/, not a light alif."""
    _, bundle, view = _build_warsh("2:35")
    rules = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }
    word_id = next(word.id for word in bundle.words if word.ref == "2:35:1")
    word = next(word for word in view.words if word.word_id == word_id)
    meem = next(column for column in word.columns if column.text == "م")
    fatha = next(
        column
        for column in word.columns
        if column.role is CellRole.HARAKA and column.attached_to_column_id == meem.id
    )

    assert not {
        rules[item]
        for item in meem.rule_occurrence_ids
        if rules[item] in {"tafkheem", "tarqeeq"}
    }
    assert not {
        rules[item]
        for item in fatha.rule_occurrence_ids
        if rules[item] in {"tafkheem", "tarqeeq"}
    }


def test_long_a_tarqeeq_labels_its_alif_carrier_not_the_hamza_presenter():
    _, bundle, view = _build_warsh("2:5")
    rules = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }
    word_id = next(word.id for word in bundle.words if word.ref == "2:5:6")
    word = next(word for word in view.words if word.word_id == word_id)
    hamza = next(column for column in word.columns if column.text == "ء")
    carrier = next(
        column
        for column in word.columns
        if column.role is CellRole.MADD and column.text == "ا"
    )
    on = lambda column: tuple(
        rules[item]
        for item in column.rule_occurrence_ids
        if rules[item] in {"tafkheem", "tarqeeq"}
    )

    assert on(hamza) == ()
    assert on(carrier) == ("tarqeeq",)


def test_compact_two_hamza_dagger_stays_in_the_source_alif_cell():
    """The small vowel in Warsh `aantum` is not a standalone letter unit."""
    _, _, view = _build_warsh("2:139:14")
    columns = view.words[0].columns

    assert any(column.text == "أٰ" for column in columns)
    assert all(column.text != "ٰ" for column in columns)


@pytest.mark.parametrize(("ref", "word_number"), (
    ("7:122", 3),
    ("20:70", 2),
    ("26:48", 2),
    ("43:58", 2),
))
def test_triple_hamza_uses_source_backed_hamza_and_alif_cells(
    ref, word_number,
):
    _, bundle, view = _build_warsh(ref)
    word_ref = f"{ref}:{word_number}"
    word_id = next(word.id for word in bundle.words if word.ref == word_ref)
    word = next(item for item in view.words if item.word_id == word_id)
    rules = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }

    eased = next(
        sound for sound in bundle.sounds
        if sound.word_id == word_id and sound.token == "ʔ̞"
    )
    badal = next(
        sound for sound in bundle.sounds
        if sound.word_id == word_id
        and sound.token == "a:"
        and "madd_badal" in {rules[item] for item in sound.rule_occurrence_ids}
    )
    hamza = next(
        column for column in word.columns if eased.id in column.owned_sound_ids
    )
    carrier = next(
        column for column in word.columns if badal.id in column.owned_sound_ids
    )

    assert hamza.status is CellStatus.REPLACED
    assert any(glyph in hamza.text for glyph in "ءأإؤئ")
    assert carrier.role is CellRole.MADD
    assert carrier.status is CellStatus.REPLACED
    assert carrier.text == "ا"
    assert all(column.text not in {"۬", "ٰ"} for column in word.columns)
    assert not any(
        column.status is CellStatus.INSERTED and column.text == "ا"
        for column in word.columns
    )
    assert not any(
        column.status is CellStatus.DROPPED and column.text == "ا"
        for column in word.columns
    )


def test_joined_naql_badal_folds_the_silent_hamza_alif_into_its_carrier():
    _, bundle, view = _build_warsh("3:83")
    word_id = next(word.id for word in bundle.words if word.ref == "3:83:2")
    word = next(item for item in view.words if item.word_id == word_id)
    rules = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }
    carrier = next(column for column in word.columns if column.text == "اٰ")

    assert carrier.role is CellRole.MADD
    assert carrier.status is CellStatus.PRESENT
    assert {rules[item] for item in carrier.rule_occurrence_ids} >= {
        "naql",
        "madd_badal",
    }
    assert {bundle.sounds[item.value].token for item in carrier.owned_sound_ids} == {
        "a:",
    }
    assert all(column.text != "ٰ" for column in word.columns)
    assert not any(
        column.text == "ا"
        and "naql" in {rules[item] for item in column.rule_occurrence_ids}
        for column in word.columns
    )


def test_a_lam_shaped_tashil_seat_is_not_classified_as_a_spoken_lam():
    _, bundle, view = _build_warsh("27:62")
    word_id = next(word.id for word in bundle.words if word.ref == "27:62:21")
    word = next(item for item in view.words if item.word_id == word_id)
    eased = next(
        sound for sound in word.sounds
        if bundle.sounds[sound.sound_id.value].token == "ʔ̞"
    )
    seat = next(
        column for column in word.columns
        if eased.sound_id in column.owned_sound_ids
    )
    rules = {
        bundle.rule_occurrences[item.value].rule_id.value
        for item in seat.rule_occurrence_ids
    }

    assert "tashil" in rules
    assert rules.isdisjoint({"tafkheem", "tarqeeq"})


@pytest.mark.parametrize(
    ("ref", "mark"),
    [
        ("3:1-3:2", "َ"),
        ("2:61:30-2:61:31", "ِ"),
    ],
)
def test_iltiqa_sound_and_column_live_on_the_boundary(hafs, pen, ref, mark):
    _, bundle, view = _build(hafs, pen, ref)
    occurrence = next(
        o for o in bundle.rule_occurrences if o.rule_id.value == "iltiqa_haraka"
    )
    boundary = next(
        b for b in view.boundaries if b.boundary_id in occurrence.boundary_ids
    )
    inserted = [
        column for column in boundary.columns if column.status is CellStatus.INSERTED
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
        for word in view.words
        for s in word.sounds
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
    qata_alif = qata.columns[0]
    boundary = next(
        b for b in view.boundaries if b.boundary_id in occurrence.boundary_ids
    )

    assert host_haraka.text == "َ"
    assert host_haraka.role is CellRole.HARAKA
    assert host_haraka.status is CellStatus.PRESENT
    assert host_haraka.owned_sound_ids == occurrence.sound_ids
    assert occurrence.id in host_haraka.rule_occurrence_ids

    assert qata_alif.text == "اَ"
    assert qata_alif.status is CellStatus.DROPPED
    assert qata_alif.silence == occurrence.id
    assert len(qata_alif.source_unit_ids) == 2
    assert all(
        not (
            column.status is CellStatus.DROPPED
            and column.attached_to_column_id == qata_alif.id
        )
        for column in qata.columns
    )

    assert not any(
        occurrence.id in column.rule_occurrence_ids for column in boundary.columns
    )
    assert not any(sound.sound_id in occurrence.sound_ids for sound in boundary.sounds)


def test_warsh_naql_folds_a_dropped_small_haraka_into_its_qata_alif():
    _, bundle, view = _build_warsh("41:46")
    word_id = next(word.id for word in bundle.words if word.ref == "41:46:14")
    word = next(item for item in view.words if item.word_id == word_id)
    qata = word.columns[0]

    assert qata.text == "ا۟"
    assert qata.status is CellStatus.DROPPED
    assert len(qata.source_character_ids) == 2
    assert len(qata.source_unit_ids) == 1
    assert all(column.text != "۟" for column in word.columns)


def test_a_started_damm_stroke_becomes_an_inserted_ordinary_damma():
    _, bundle, view = _build_warsh("41:46:14")
    qata, damma = view.words[0].columns[:2]

    assert qata.text == "أ"
    assert qata.status is CellStatus.REPLACED
    assert [bundle.sounds[sound.value].token for sound in qata.owned_sound_ids] == ["ʔ"]
    assert damma.text == "ُ"
    assert damma.status is CellStatus.INSERTED
    assert not damma.source_character_ids and not damma.source_unit_ids
    assert [bundle.sounds[sound.value].token for sound in damma.owned_sound_ids] == [
        "u"
    ]
    assert all(column.text != "۟" for column in view.words[0].columns)


@pytest.mark.parametrize(
    ("ref", "mark", "carrier_text", "token"),
    [
        ("69:18:3", "ُ", "و", "u:"),
        ("46:21:5", "َ", "ٰ", "a:"),
        ("2:139:14", "َ", "ا", "a:"),
    ],
)
def test_a_started_hamza_long_vowel_groups_an_inserted_haraka_with_its_carrier(
    ref, mark, carrier_text, token
):
    _, bundle, view = _build_warsh(ref)
    word = view.words[0]
    sound = next(item for item in bundle.sounds if item.token == token)
    cell = next(item for item in word.sounds if item.sound_id == sound.id)
    carrier = next(
        column
        for column in word.columns
        if column.id in cell.column_ids and column.role is CellRole.MADD
    )
    haraka = next(
        column
        for column in word.columns
        if column.id in cell.column_ids and column.role is CellRole.HARAKA
    )
    group = next(item for item in word.groups if item.key == carrier.id)

    assert carrier.text == carrier_text
    assert haraka.text == mark
    assert haraka.status is CellStatus.INSERTED
    assert not haraka.source_character_ids and not haraka.source_unit_ids
    assert haraka.attached_to_column_id == carrier.id
    assert haraka.presented_sound_ids == (sound.id,)
    assert carrier.owned_sound_ids == (sound.id,)
    assert cell.column_ids == (haraka.id, carrier.id)
    assert group.column_ids == cell.column_ids
    assert all(column.text != "۟" for column in word.columns)


def test_warsh_native_iqlab_meem_is_its_own_source_backed_cell():
    warsh = recitation(Riwayah.WARSH)
    pen = pen_for(warsh.inventory(Script.UTHMANI))
    ref = "2:9-2:10"
    session = phonemize_request(warsh, ref)
    kw = dict(ref=ref, riwayah="warsh", script="uthmani", variant={})
    bundle = build_bundle(session, **kw)
    view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
    occurrence = next(o for o in bundle.rule_occurrences if o.rule_id.value == "iqlab")
    word = next(
        word for word in view.words if any(column.text == "ۢ" for column in word.columns)
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


def test_stopped_warsh_native_iqlab_meem_is_not_variant_silence():
    """A written iqlab mark is not an implicit recitation variant handoff."""
    session, bundle, view = _build_warsh("2:9-2:10", stop_refs=("2:9:9",))
    source = build_source_view(session, bundle=bundle)
    meem = next(unit for unit in source.units if unit.text == "ۢ")
    word_id = next(word.id for word in bundle.words if word.ref == "2:9:9")
    word = next(item for item in view.words if item.word_id == word_id)
    cell = next(column for column in word.columns if column.text == "ۢ")
    rules = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }

    assert meem.silence not in {
        LiteralSilence.ORTHOGRAPHIC,
        LiteralSilence.VARIANT,
    }
    assert rules[meem.silence] == "waqf_diacritic_drop"
    assert cell.silence is not LiteralSilence.VARIANT
    assert rules[cell.silence] == "waqf_diacritic_drop"


def test_stopped_warsh_native_noon_iqlab_meem_uses_waqf_drop():
    session, bundle, view = _build_warsh("2:158", stop_refs=("2:158:9",))
    source = build_source_view(session, bundle=bundle)
    word_id = next(word.id for word in bundle.words if word.ref == "2:158:9")
    unit = next(
        item for item in source.units
        if item.word_id == word_id and item.text == "ۢ"
    )
    word = next(item for item in view.words if item.word_id == word_id)
    cell = next(column for column in word.columns if column.text == "ۢ")
    rules = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }

    assert unit.silence not in {
        LiteralSilence.ORTHOGRAPHIC,
        LiteralSilence.VARIANT,
    }
    assert rules[unit.silence] == "waqf_diacritic_drop"
    assert cell.silence == unit.silence


def test_warsh_native_iqlab_meem_follows_kasratan_below_the_host():
    _, _, view = _build_warsh("7:53")
    word = next(
        item for item in view.words if any(column.text == "ۢ" for column in item.columns)
    )
    meem = next(column for column in word.columns if column.text == "ۢ")
    tanween = next(column for column in word.columns if column.role is CellRole.TANWEEN)

    assert tanween.tier is CellTier.BELOW
    assert meem.tier is CellTier.BELOW
    assert meem.attached_to_column_id == tanween.attached_to_column_id


def test_warsh_native_noon_iqlab_meem_owns_the_rule_and_sound():
    _, bundle, view = _build_warsh("19:93")
    occurrence = next(
        item for item in bundle.rule_occurrences if item.rule_id.value == "iqlab"
    )
    word = next(
        item for item in view.words if any(column.text == "ۢ" for column in item.columns)
    )
    meem = next(column for column in word.columns if column.text == "ۢ")
    noon = next(
        column for column in word.columns if column.id == meem.attached_to_column_id
    )

    assert meem.source_character_ids
    assert meem.status is CellStatus.PRESENT
    assert meem.silence is None
    assert meem.owned_sound_ids == occurrence.sound_ids
    assert meem.rule_occurrence_ids == (occurrence.id,)
    assert not noon.owned_sound_ids
    assert noon.silence == occurrence.id


def test_warsh_final_alif_sukun_stays_with_its_written_alif():
    _, _, view = _build_warsh("6:70")
    word = next(
        item
        for item in view.words
        if "اَ۪تَّخَذُوا" in "".join(column.text for column in item.columns)
    )
    final = word.columns[-1]

    assert final.role is CellRole.LETTER
    assert final.text == "اْ"
    assert not any(column.role is CellRole.SUKUN for column in word.columns)


def test_warsh_naql_badal_long_vowel_is_a_cross_word_bridge():
    _, bundle, view = _build_warsh("84:6-84:7")
    rules = {
        sound.id: {
            bundle.rule_occurrences[item.value].rule_id.value
            for item in sound.rule_occurrence_ids
        }
        for sound in bundle.sounds
    }
    merger = next(
        item
        for item in bundle.mergers
        if item.boundary_id is not None
        and rules[item.sound_id] >= {"naql", "madd_badal"}
    )
    bridge = next(
        item
        for boundary in view.boundaries
        for item in boundary.bridges
        if item.merger_id == merger.id
    )
    before = next(word for word in view.words if word.word_id == merger.before_word_id)
    after = next(word for word in view.words if word.word_id == merger.after_word_id)
    presenter = next(
        column
        for column in before.columns
        if merger.sound_id in column.presented_sound_ids
    )
    carrier = next(
        column for column in after.columns if merger.sound_id in column.owned_sound_ids
    )
    qata = next(
        column
        for column in after.columns
        if column.text == "ا۟" and column.status is CellStatus.DROPPED
    )

    assert bridge.sound.sound_id == merger.sound_id
    assert bridge.before_column_ids == (presenter.id,)
    assert bridge.after_column_ids == (carrier.id,)
    assert set(bridge.sound.column_ids) == {presenter.id, carrier.id}
    assert presenter.role is CellRole.HARAKA and presenter.text == "ُ"
    assert carrier.role is CellRole.MADD and carrier.text == "و"
    assert qata.id != carrier.id and qata.silence is not None
    assert all(
        item.sound_id != merger.sound_id for word in view.words for item in word.sounds
    )


def test_warsh_tanween_naql_does_not_put_madd_badal_on_tanween():
    _, bundle, view = _build_warsh("20:21")
    rules = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }
    merger = next(
        item for item in bundle.mergers
        if item.boundary_id is not None
        and bundle.words[item.before_word_id.value].ref == "20:21:9"
        and bundle.words[item.after_word_id.value].ref == "20:21:10"
        and {
            rules[occurrence]
            for occurrence in bundle.sounds[item.sound_id.value].rule_occurrence_ids
        } >= {"naql", "madd_badal"}
    )
    before = next(word for word in view.words if word.word_id == merger.before_word_id)
    after = next(word for word in view.words if word.word_id == merger.after_word_id)
    tanween = next(
        column for column in before.columns
        if merger.sound_id in column.presented_sound_ids
    )
    carrier = next(
        column for column in after.columns
        if merger.sound_id in column.owned_sound_ids
    )

    assert tanween.role is CellRole.TANWEEN
    assert {rules[item] for item in tanween.rule_occurrence_ids} == {"naql"}
    assert {rules[item] for item in carrier.rule_occurrence_ids} >= {
        "naql", "madd_badal",
    }


def test_warsh_tanween_naql_vowel_is_a_cross_word_bridge():
    _, bundle, view = _build_warsh("7:58")
    occurrence = next(
        item
        for item in bundle.rule_occurrences
        if item.rule_id.value == "naql"
        and {bundle.words[word.value].ref for word in item.word_ids}
        == {"7:58:3", "7:58:4"}
    )
    merger = next(
        item for item in bundle.mergers if occurrence.id in item.rule_occurrence_ids
    )
    bridge = next(
        item
        for boundary in view.boundaries
        for item in boundary.bridges
        if item.merger_id == merger.id
    )
    before = view.words[2]
    boundary = next(
        boundary for boundary in view.boundaries if bridge in boundary.bridges
    )
    tanween = next(
        column
        for column in before.columns
        if column.role is CellRole.TANWEEN
        and merger.sound_id in column.presented_sound_ids
    )
    source_haraka = next(
        column
        for column in boundary.columns
        if column.role is CellRole.HARAKA and merger.sound_id in column.owned_sound_ids
    )

    assert bundle.sounds[merger.sound_id.value].token == "i"
    assert source_haraka.text == "ِ"
    assert source_haraka.status is CellStatus.PRESENT
    assert occurrence.id not in tanween.rule_occurrence_ids
    assert occurrence.id in source_haraka.rule_occurrence_ids
    assert occurrence.id in bridge.sound.rule_occurrence_ids
    assert bridge.before_column_ids == (tanween.id,)
    assert bridge.after_column_ids == (source_haraka.id,)
    assert bridge.sound.column_ids == (tanween.id, source_haraka.id)
    assert all(
        sound.sound_id != merger.sound_id
        for word in view.words
        for sound in word.sounds
    )
    assert all(
        source_haraka.id not in group.column_ids
        for word in view.words
        for group in word.groups
    )


def test_warsh_tanween_naql_extracts_a_compact_tashil_haraka_to_the_bridge():
    _, bundle, view = _build_warsh("27:63")
    merger = next(
        item
        for item in bundle.mergers
        if item.before_word_id == bundle.words[13].id
        and item.after_word_id == bundle.words[14].id
    )
    boundary = next(
        item for item in view.boundaries if item.boundary_id == merger.boundary_id
    )
    bridge = next(item for item in boundary.bridges if item.merger_id == merger.id)
    haraka = next(
        column for column in boundary.columns if column.role is CellRole.HARAKA
    )
    after = view.words[14]

    assert haraka.text == "َ"
    assert haraka.owned_sound_ids == (merger.sound_id,)
    assert bridge.after_column_ids == (haraka.id,)
    assert any(column.text == "ا۟" for column in after.columns)
    assert all(column.text != "اَ۟" for column in after.columns)


def test_warsh_naql_badal_compound_keeps_intervening_source_marks():
    _, joined_bundle, joined_view = _build_warsh("84:6-84:7")
    _, fresh_bundle, fresh_view = _build_warsh(
        "84:6-84:7",
        stop_refs=("84:7:2",),
    )
    joined_id = next(word.id for word in joined_bundle.words if word.ref == "84:7:3")
    fresh_id = next(word.id for word in fresh_bundle.words if word.ref == "84:7:3")
    joined = next(word for word in joined_view.words if word.word_id == joined_id)
    fresh = next(word for word in fresh_view.words if word.word_id == fresh_id)

    joined_units = tuple(
        unit for column in joined.columns for unit in column.source_unit_ids
    )
    fresh_units = tuple(
        unit for column in fresh.columns for unit in column.source_unit_ids
    )
    assert joined_units == fresh_units
    assert any(
        column.text == "ا۟" and column.status is CellStatus.DROPPED
        for column in joined.columns
    )
    assert all(column.text != "۟" for column in joined.columns)
    assert any(
        column.text == "و" and column.role is CellRole.MADD and column.owned_sound_ids
        for column in joined.columns
    )
    assert all(column.text != "ا۟و" for column in joined.columns)


def test_warsh_matching_hamza_ibdal_long_is_a_cross_word_bridge():
    session, bundle, view = _build_warsh("32:4")
    underlying = session.score.words[4].slots[0]
    merger = next(
        item
        for item in bundle.mergers
        if item.before_word_id == bundle.words[3].id
        and item.after_word_id == bundle.words[4].id
    )
    bridge = next(
        item
        for boundary in view.boundaries
        for item in boundary.bridges
        if item.merger_id == merger.id
    )
    before = view.words[3]
    after = view.words[4]
    kasra = next(
        column
        for column in before.columns
        if merger.sound_id in column.presented_sound_ids
    )
    carrier = next(
        column for column in after.columns if merger.sound_id in column.owned_sound_ids
    )

    assert underlying.onset is Onset.PLAIN
    assert underlying.nucleus.joined.quality is Quality.I
    assert bundle.sounds[merger.sound_id.value].token == "i:"
    assert kasra.role is CellRole.HARAKA and kasra.text == "ِ"
    assert carrier.role is CellRole.MADD and carrier.text == "ى"
    assert carrier.status is CellStatus.REPLACED
    assert carrier.source_character_ids
    assert bridge.before_column_ids == (kasra.id,)
    assert bridge.after_column_ids == (carrier.id,)
    assert bridge.sound.column_ids == (kasra.id, carrier.id)
    assert {
        bundle.rule_occurrences[item.value].rule_id.value
        for item in bridge.sound.rule_occurrence_ids
    } == {"ibdal_hamza", "madd_tabii"}


@pytest.mark.parametrize(
    ("riwayah", "ref", "word_ref", "stop_refs"),
    [
        ("hafs", "18:38", "18:38:1", ()),
        ("hafs", "18:38", "18:38:1", ("18:38:1",)),
        ("warsh", "18:37", "18:37:1", ()),
        ("warsh", "18:37", "18:37:1", ("18:37:1",)),
    ],
)
def test_pausal_alif_identity_stays_on_its_carrier_in_wasl_and_waqf(
    hafs, riwayah, ref, word_ref, stop_refs
):
    reading = hafs if riwayah == "hafs" else recitation(Riwayah.WARSH)
    session = phonemize_request(reading, ref, stop_refs=stop_refs)
    kw = dict(ref=ref, riwayah=riwayah, variant={})
    bundle = build_bundle(session, script="uthmani", **kw)
    occurrence = next(
        item for item in bundle.rule_occurrences if item.rule_id.value == "pausal_alif"
    )
    scripts = reading.scripts if riwayah == "hafs" else (Script.UTHMANI,)

    for script in scripts:
        script_pen = pen_for(reading.inventory(script))
        view = build_cell_view(
            session,
            spelling="transformed",
            pen=script_pen,
            bundle=bundle,
            script=script.value,
            **kw,
        )
        word_id = next(word.id for word in bundle.words if word.ref == word_ref)
        word = next(item for item in view.words if item.word_id == word_id)
        labelled = [
            column
            for column in word.columns
            if occurrence.id in column.rule_occurrence_ids
        ]

        assert len(labelled) == 1
        assert labelled[0].role is CellRole.MADD
        assert labelled[0].text.startswith("ا")
        assert all(
            occurrence.id not in column.rule_occurrence_ids
            for column in word.columns
            if column.role is CellRole.HARAKA
        )


def test_iltiqa_shortening_labels_only_the_carrier_in_both_riwayat(hafs, pen):
    cases = (
        (*_build(hafs, pen, "2:11"), "ى"),
        (*_build_warsh("42:25"), "ے"),
    )
    for _, bundle, view, carrier_text in cases:
        occurrence = next(
            item
            for item in bundle.rule_occurrences
            if item.rule_id.value == "iltiqa_shortening"
        )
        labelled = [
            column
            for word in view.words
            for column in word.columns
            if occurrence.id in column.rule_occurrence_ids
        ]

        assert len(labelled) == 1
        assert labelled[0].text == carrier_text
        assert labelled[0].status is CellStatus.DROPPED
        assert all(
            occurrence.id not in column.rule_occurrence_ids
            for word in view.words
            for column in word.columns
            if column.role is CellRole.HARAKA
        )


@pytest.mark.parametrize("ref", ["18:37", "2:15", "3:145"])
def test_warsh_carrier_identity_rules_never_label_harakas(ref):
    _, bundle, view = _build_warsh(ref)
    rules = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }
    forbidden = {"pausal_alif", "taqlil", "ibdal_hamza"}

    assert all(
        not any(
            rules[occurrence] in forbidden or rules[occurrence].startswith("madd_")
            for occurrence in column.rule_occurrence_ids
        )
        for word in view.words
        for column in word.columns
        if column.role is CellRole.HARAKA
    )


def test_warsh_long_article_naql_is_one_source_backed_madd_cell():
    _, bundle, view = _build_warsh("31:3")
    rules = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }
    target = next(
        column
        for word in view.words
        for column in word.columns
        if {rules[item] for item in column.rule_occurrence_ids}
        >= {"naql", "madd_badal"}
        and column.text == "َا"
    )

    assert target.role is CellRole.MADD
    assert target.status is CellStatus.PRESENT
    assert target.source_character_ids
    assert target.owned_sound_ids
    assert not any(
        column.text == "ا"
        and column.status is CellStatus.DROPPED
        and any(rules[item] == "naql" for item in column.rule_occurrence_ids)
        for word in view.words
        for column in word.columns
    )


def test_warsh_combining_hamza_seat_is_one_live_cell():
    _, _, view = _build_warsh("11:53")
    target = next(
        column for word in view.words for column in word.columns if column.text == "ئْ"
    )

    assert target.role is CellRole.LETTER
    assert target.status is CellStatus.PRESENT
    assert target.owned_sound_ids
    assert not any(
        column.text == "ي" and column.status is CellStatus.DROPPED
        for word in view.words
        for column in word.columns
    )


def test_warsh_hamza_maddah_projects_separate_onset_and_carrier_cells():
    session, bundle, view = _build_warsh("6:135")
    facts = analyse(session, packaged_alphabet())
    word = view.words[3]
    hamza = next(column for column in word.columns if column.text == "أ")
    carrier = next(column for column in word.columns if column.text == "َا")
    hamza_sounds = [facts.sounds[sound.value].value for sound in hamza.owned_sound_ids]
    carrier_sounds = [
        facts.sounds[sound.value].value for sound in carrier.owned_sound_ids
    ]
    rules = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }

    assert hamza.source_character_ids and carrier.source_character_ids
    assert set(hamza.source_character_ids).isdisjoint(carrier.source_character_ids)
    assert all(isinstance(sound, Consonant) for sound in hamza_sounds)
    assert all(isinstance(sound, Vowel) and sound.long for sound in carrier_sounds)
    assert "madd_badal" not in {
        rules[occurrence] for occurrence in hamza.rule_occurrence_ids
    }
    assert "madd_badal" in {
        rules[occurrence] for occurrence in carrier.rule_occurrence_ids
    }
    assert all(
        cell.column_ids == (carrier.id,)
        for cell in word.sounds
        if cell.sound_id in carrier.owned_sound_ids
    )


def test_warsh_suwaa_keeps_its_final_vowel_before_the_following_qata():
    _, bundle, view = _build_warsh("30:9")
    words = {word.ref: word.id for word in bundle.words}
    suwaa = next(word for word in view.words if word.word_id == words["30:9:6"])
    an = next(word for word in view.words if word.word_id == words["30:9:7"])
    suwaa_hamza = next(column for column in suwaa.columns if column.text == "أ۪")
    suwaa_carrier = next(column for column in suwaa.columns if column.text == "ىٰٓ")
    an_hamza = next(column for column in an.columns if column.text == "أ")
    an_fatha = next(column for column in an.columns if column.text == "َ")
    rules = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }

    def tokens(column):
        return {bundle.sounds[sound.value].token for sound in column.owned_sound_ids}

    assert suwaa_hamza.status is CellStatus.PRESENT
    assert suwaa_carrier.status is CellStatus.PRESENT
    assert an_hamza.status is CellStatus.PRESENT
    assert tokens(suwaa_hamza) == {"ʔ"}
    assert tokens(suwaa_carrier) == {"ɛ:"}
    assert tokens(an_hamza) == {"ʔ"}
    assert tokens(an_fatha) == {"a"}
    assert {rules[item] for item in suwaa_carrier.rule_occurrence_ids} == {
        "madd_munfasil",
        "madd_badal",
        "taqlil",
    }
    assert not {
        rules[item]
        for column in (*suwaa.columns, *an.columns)
        for item in column.rule_occurrence_ids
    } & {"naql", "ibdal_hamza", "tashil"}


def test_all_warsh_hamza_maddah_spellings_project_separate_carriers():
    corpus = warsh_corpus()
    entries = [
        (corpus.public_ref(location), entry.text)
        for location, entry in corpus.entries.items()
        if any(pair in entry.text for pair in ("أٓ", "إٓ", "ءٓ", "ؤٓ", "ئٓ"))
    ]

    assert len(entries) == 69
    for ref, text in entries:
        _, bundle, view = _build_warsh(ref)
        word_id = next(word.id for word in bundle.words if word.ref == ref)
        word = next(item for item in view.words if item.word_id == word_id)
        assert any(
            column.text in {"أ", "إ", "ء", "ؤ", "ئ"} for column in word.columns
        ), (
            ref,
            text,
        )
        assert any(column.text == "َا" for column in word.columns), (ref, text)


def test_warsh_unwritten_divine_name_gemination_is_visible_when_transformed():
    _, _, view = _build_warsh("27:25")
    word = view.words[2]
    lam = next(column for column in word.columns if column.text == "لّ")
    carrier = next(
        column
        for column in word.columns
        if column.role is CellRole.MADD and column.anchor_unit_id in lam.source_unit_ids
    )
    long_vowel = next(
        sound for sound in word.sounds if sound.sound_id in carrier.owned_sound_ids
    )

    assert lam.status is CellStatus.REPLACED
    assert long_vowel.column_ids == (carrier.id,)
    assert long_vowel.sound_id not in lam.presented_sound_ids


@pytest.mark.parametrize(
    ("ref", "word_ref"),
    [
        ("1:1", "1:1:2"),
        ("1:6", "1:6:2"),
        ("2:163", "2:163:7"),
    ],
)
def test_warsh_unwritten_gemination_is_visible_for_every_source_convention(
    ref, word_ref
):
    session, bundle, view = _build_warsh(ref)
    facts = analyse(session, packaged_alphabet())
    word_id = next(word.id for word in bundle.words if word.ref == word_ref)
    source_word = next(word for word in bundle.words if word.id == word_id)
    cell_word = next(word for word in view.words if word.word_id == word_id)
    geminates = [
        column
        for column in cell_word.columns
        if any(
            isinstance(facts.sounds[sound.value].value, Consonant)
            and facts.sounds[sound.value].value.geminate
            for sound in column.owned_sound_ids
        )
    ]

    assert "ّ" not in source_word.text
    assert geminates
    assert all("ّ" in column.text for column in geminates)


def test_warsh_feminine_relative_pronoun_inserts_its_unwritten_fatha_cell():
    session, bundle, view = _build_warsh("41:33")
    facts = analyse(session, packaged_alphabet())
    word_id = next(word.id for word in bundle.words if word.ref == "41:33:7")
    word = next(item for item in view.words if item.word_id == word_id)
    lam = next(column for column in word.columns if column.text == "لّ")
    fatha = next(
        column
        for column in word.columns
        if column.status is CellStatus.INSERTED
        and column.role is CellRole.HARAKA
        and column.text == "َ"
        and column.anchor_unit_id in lam.source_unit_ids
    )
    ta = next(column for column in word.columns if column.text == "ت")

    lam_sounds = [facts.sounds[sound.value].value for sound in lam.owned_sound_ids]
    fatha_sounds = [facts.sounds[sound.value].value for sound in fatha.owned_sound_ids]
    ta_sounds = [facts.sounds[sound.value].value for sound in ta.owned_sound_ids]

    assert fatha.source_character_ids == ()
    assert fatha.source_unit_ids == ()
    assert len(lam_sounds) == 1
    assert isinstance(lam_sounds[0], Consonant)
    assert lam_sounds[0].letter is CanonLetter.LAM and lam_sounds[0].geminate
    assert fatha_sounds == [Vowel(Quality.A)]
    assert ta_sounds == [Consonant(CanonLetter.TA)]
    assert not any(
        occurrence.rule_id.value == "lam_shamsiyyah" and word_id in occurrence.word_ids
        for occurrence in bundle.rule_occurrences
    )


def test_warsh_taqlil_is_only_on_its_carrier_cell():
    _, bundle, view = _build_warsh("2:15")
    taqlil = {
        occurrence.id
        for occurrence in bundle.rule_occurrences
        if occurrence.rule_id.value == "taqlil"
    }
    labelled = [
        column
        for word in view.words
        for column in word.columns
        if taqlil.intersection(column.rule_occurrence_ids)
    ]

    assert labelled
    assert all(column.role is CellRole.MADD for column in labelled)


def test_warsh_article_naql_keeps_a_separate_silent_qata_alif_cell():
    _, bundle, view = _build_warsh("31:18")
    occurrence = next(
        item
        for item in bundle.rule_occurrences
        if item.rule_id.value == "naql"
        and any(bundle.words[word.value].ref == "31:18:9" for word in item.word_ids)
    )
    word_id = next(word.id for word in bundle.words if word.ref == "31:18:9")
    word = next(item for item in view.words if item.word_id == word_id)
    named = [
        column for column in word.columns if occurrence.id in column.rule_occurrence_ids
    ]

    assert any(
        column.role is CellRole.HARAKA
        and column.text == "َ"
        and column.status is CellStatus.PRESENT
        for column in named
    )
    assert any(
        column.role is CellRole.LETTER
        and column.text == "ا"
        and column.status is CellStatus.DROPPED
        and column.source_character_ids
        for column in named
    )
    assert all(column.text != "َا" for column in word.columns)


@pytest.mark.parametrize(
    ("ref", "word_ref", "haraka"),
    [
        ("84:6", "84:6:2", "ِ"),
        ("81:23", "81:23:3", "ُ"),
        ("53:20", "53:20:3", "ُ"),
    ],
)
def test_warsh_article_naql_splits_non_fatha_haraka_from_qata_alif(
    ref, word_ref, haraka
):
    _, bundle, view = _build_warsh(ref)
    word_id = next(word.id for word in bundle.words if word.ref == word_ref)
    word = next(item for item in view.words if item.word_id == word_id)
    named = [
        column
        for column in word.columns
        if any(
            bundle.rule_occurrences[item.value].rule_id.value == "naql"
            for item in column.rule_occurrence_ids
        )
    ]

    assert any(
        column.role is CellRole.HARAKA
        and column.text == haraka
        and column.status is CellStatus.PRESENT
        for column in named
    )
    assert any(
        column.role is CellRole.LETTER
        and column.text == "ا"
        and column.status is CellStatus.DROPPED
        for column in named
    )
    assert all(column.text != haraka + "ا" for column in word.columns)


def test_warsh_ibdal_hamza_labels_the_carrier_not_its_haraka():
    _, bundle, view = _build_warsh("3:145")
    ibdal = {
        occurrence.id
        for occurrence in bundle.rule_occurrences
        if occurrence.rule_id.value == "ibdal_hamza"
    }
    labelled = [
        column
        for word in view.words
        for column in word.columns
        if ibdal.intersection(column.rule_occurrence_ids)
    ]

    assert labelled
    assert any(column.role is CellRole.MADD for column in labelled)
    assert all(column.role is not CellRole.HARAKA for column in labelled)


@pytest.mark.parametrize(
    ("ref", "word_ref", "text", "token"),
    [
        ("16:61", "16:61:2", "و", "w"),
        ("57:28", "57:28:1", "ي", "j"),
    ],
)
def test_warsh_moving_ibdal_absorbs_its_source_mark_without_rendering_it(
    ref,
    word_ref,
    text,
    token,
):
    _, bundle, view = _build_warsh(ref)
    word_id = next(word.id for word in bundle.words if word.ref == word_ref)
    word = next(item for item in view.words if item.word_id == word_id)
    carrier = next(column for column in word.columns if column.text == text)
    rules = {
        bundle.rule_occurrences[item.value].rule_id.value
        for item in carrier.rule_occurrence_ids
    }

    assert carrier.status is CellStatus.PRESENT
    assert len(carrier.source_character_ids) == 2
    assert "ibdal_hamza" in rules
    assert {bundle.sounds[sound.value].token for sound in carrier.owned_sound_ids} == {
        token
    }
    assert all("۬" not in column.text for column in word.columns)


@pytest.mark.parametrize(
    ("ref", "expected"),
    [
        ("23:1:2", "أ"),
        ("49:9:10", "إ"),
        ("77:12:3", "أ"),
        ("15:87:2", "أ"),
    ],
)
def test_every_started_latent_qata_uses_a_visible_hamza_seat(ref, expected):
    _, bundle, view = _build_warsh(ref)
    hamza = next(
        column
        for column in view.words[0].columns
        if any(
            bundle.sounds[sound.value].token == "ʔ" for sound in column.owned_sound_ids
        )
    )

    assert hamza.text == expected
    assert hamza.status is CellStatus.REPLACED


def test_a_stopped_naql_witness_uses_the_shared_waqf_diacritic_drop():
    _, bundle, view = _build_warsh("23:1", stop_refs=("23:1:1",))
    rules = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }
    host = view.words[0]
    witness = next(
        column
        for column in reversed(host.columns)
        if column.role is CellRole.HARAKA
        and not column.owned_sound_ids
        and not column.presented_sound_ids
    )

    assert witness.status is CellStatus.DROPPED
    assert witness.silence is not None
    assert rules[witness.silence] == "waqf_diacritic_drop"
    assert witness.silence in witness.rule_occurrence_ids


def test_warsh_native_iqlab_fatha_renders_weight_without_a_label():
    _, bundle, view = _build_warsh("61:6", extra_phonemes=frozenset({"emphatic_fatha"}))
    word_id = next(word.id for word in bundle.words if word.ref == "61:6:18")
    word = next(item for item in view.words if item.word_id == word_id)
    rules = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }
    fatha = next(column for column in word.columns if column.role is CellRole.TANWEEN)

    assert "tafkheem" not in {
        rules[occurrence] for occurrence in fatha.rule_occurrence_ids
    }
    vowel = next(
        sound
        for sound in word.sounds
        if fatha.id in sound.column_ids
        and bundle.sounds[sound.sound_id.value].token.startswith("aˤ")
    )
    assert "tafkheem" not in {
        rules[occurrence] for occurrence in vowel.rule_occurrence_ids
    }


def test_stopped_warsh_native_iqlab_keeps_iwad_cells_contiguous():
    _, bundle, view = _build_warsh("61:6", stop_refs=("61:6:18",))
    word_id = next(word.id for word in bundle.words if word.ref == "61:6:18")
    word = next(item for item in view.words if item.word_id == word_id)
    by_id = {column.id: column for column in word.columns}
    carrier_group = next(
        group
        for group in word.groups
        if any(by_id[column].role is CellRole.MADD for column in group.column_ids)
    )

    assert [by_id[column].text for column in carrier_group.column_ids] == [
        "َ",
        "ۢ",
        "ا",
    ]


def test_lam_shamsiyyah_cell_keeps_only_its_own_rule_in_warsh():
    _, bundle, view = _build_warsh("2:263")
    rules = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }
    lams = [
        column
        for word in view.words
        for column in word.columns
        if "lam_shamsiyyah"
        in {rules[occurrence] for occurrence in column.rule_occurrence_ids}
    ]

    assert lams
    assert all(
        [rules[occurrence] for occurrence in column.rule_occurrence_ids]
        == ["lam_shamsiyyah"]
        for column in lams
    )


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
                for unit in source.units
                if unit.character_ids
            }
            pausal = {
                slot
                for edge in facts.silences
                if edge.aspect is Aspect.VOWEL
                and edge.by is not None
                and facts.occurrences[edge.by].boundary is not None
                for slot in edge.slots
            }
            for word in view.words:
                consonants = [
                    col
                    for col in word.columns
                    if col.role is CellRole.LETTER
                    and any(
                        isinstance(facts.sounds[s.value].value, Consonant)
                        for s in col.owned_sound_ids
                    )
                ]
                if not consonants:
                    continue
                final = consonants[-1]
                needs_sukun = any(
                    slot_of[u.value] in pausal
                    or facts.slots[
                        facts.slot_index[slot_of[u.value]]
                    ].nucleus.stopped.form
                    is VowelForm.ABSENT
                    for u in final.source_unit_ids
                    if u.value in slot_of
                )
                if needs_sukun:
                    assert final.text.endswith(pen.role("sukun")), (
                        ref,
                        word.word_id,
                        final,
                    )
