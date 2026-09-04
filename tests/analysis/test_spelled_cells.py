"""Native cell projection for the disjoint-letter names."""
from __future__ import annotations

import pytest

from quranic_phonemizer.analysis.build import build_bundle
from quranic_phonemizer.analysis.cells import build_cell_view
from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Riwayah, Script
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.session import phonemize_request

FORMS = {
    "2:1": ("أَلِفْ", "لَآم", "مِّيٓمْ"),
    "7:1": ("أَلِفْ", "لَآم", "مِّيٓمْ", "صَآدْ"),
    "10:1": ("أَلِفْ", "لَآمْ", "رَا"),
    "13:1": ("أَلِفْ", "لَآم", "مِّيٓمْ", "رَا"),
    "19:1": ("كَآفْ", "هَا", "يَا", "عَيْٓن", "صَآدْ"),
    "20:1": ("طَا", "هَا"),
    "26:1": ("طَا", "سِيٓن", "مِّيٓمْ"),
    "27:1": ("طَا", "سِيٓن"),
    "36:1": ("يَا", "سِيٓنْ"),
    "38:1": ("صَآدْ",),
    "40:1": ("حَا", "مِيٓمْ"),
    "42:1": ("حَا", "مِيٓمْ"),
    "42:2": ("عَيْٓن", "سِيٓن", "قَآفْ"),
    "50:1": ("قَآفْ",),
    "68:1": ("نُوٓنْ",),
}


def _build(reading, ref, *, stop_refs=()):
    session = phonemize_request(reading, ref, stop_refs=stop_refs)
    kw = dict(
        ref=ref, riwayah=reading.riwayah.value, script="uthmani", variant={}
    )
    view = build_cell_view(
        session, **kw, spelling="transformed",
        pen=pen_for(reading.inventory(Script.UTHMANI)),
    )
    return view, build_bundle(session, **kw)


def _rules(bundle):
    return {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }


@pytest.mark.parametrize(("ref", "expected"), FORMS.items())
def test_each_name_is_a_flat_run_of_native_cells(hafs, ref, expected):
    view, _ = _build(hafs, ref)
    word = view.words[0]
    columns = {column.id: column for column in word.columns}
    assert tuple(
        "".join(columns[column].text for column in run.column_ids)
        for run in word.runs
    ) == expected
    claimed = [column for run in word.runs for column in run.column_ids]
    assert claimed == [column.id for column in word.columns]


def test_cross_verse_muqattaat_keep_the_score_slot_ids(hafs):
    view, _ = _build(hafs, "42:1-42:2")
    word = view.words[1]
    columns = {column.id: column for column in word.columns}
    assert tuple(
        "".join(columns[column].text for column in run.column_ids)
        for run in word.runs
    ) == FORMS["42:2"]


def test_source_spelling_stays_compact(hafs):
    session = phonemize_request(hafs, "2:1")
    view = build_cell_view(
        session, ref="2:1", riwayah="hafs", script="uthmani", variant={}
    )
    assert not view.words[0].runs
    assert "".join(column.text for column in view.words[0].columns) == "الٓمٓ"


def test_the_lam_meem_idgham_is_an_internal_bridge(hafs):
    view, bundle = _build(hafs, "2:1")
    merger = next(m for m in bundle.mergers if m.boundary_id is None)
    bridge = view.words[0].bridges[0]
    assert bridge.merger_id == merger.id
    assert bridge.sound.sound_id == merger.sound_id
    assert bridge.before_column_ids and bridge.after_column_ids


@pytest.mark.parametrize("riwayah", (Riwayah.HAFS, Riwayah.WARSH))
def test_taa_seen_wasl_hides_the_final_noon_in_its_named_cell(riwayah):
    reading = recitation(riwayah)
    view, bundle = _build(reading, "27:1")
    ikhfaa = next(
        occurrence for occurrence in bundle.rule_occurrences
        if occurrence.rule_id.value == "ikhfaa"
    )
    noon = next(
        column for column in view.words[0].columns
        if column.text == "ن"
    )
    hum = next(
        sound for sound in view.words[0].sounds
        if sound.sound_id in ikhfaa.sound_ids
    )

    assert ikhfaa.id in noon.rule_occurrence_ids
    assert ikhfaa.id in hum.rule_occurrence_ids


def test_ain_has_only_madd_lazim_on_its_ya(hafs):
    view, bundle = _build(hafs, "42:2")
    names = _rules(bundle)
    columns = view.words[0].columns
    tagged = {
        column.text: {names[item] for item in column.rule_occurrence_ids}
        for column in columns
    }
    assert "madd_lazim" in tagged["يْٓ"]
    assert all("madd_leen" not in rules for rules in tagged.values())


def test_emphatic_fatha_is_unlabelled_while_its_carrier_keeps_tafkheem(hafs):
    view, bundle = _build(hafs, "50:1")
    names = _rules(bundle)
    tagged = {
        column.text: {names[item] for item in column.rule_occurrence_ids}
        for column in view.words[0].columns
    }
    for text in ("ق", "آ"):
        assert "tafkheem" in tagged[text]
    assert "tafkheem" not in tagged["َ"]


def test_sad_closes_with_the_boundary_specific_qalqala(hafs):
    joined, joined_bundle = _build(hafs, "38:1")
    stopped, stopped_bundle = _build(hafs, "38:1", stop_refs=("38:1:1",))
    joined_names = _rules(joined_bundle)
    stopped_names = _rules(stopped_bundle)
    joined_dal = next(c for c in joined.words[0].columns if c.text == "دْ")
    stopped_dal = next(c for c in stopped.words[0].columns if c.text == "دْ")
    assert {joined_names[x] for x in joined_dal.rule_occurrence_ids} == {
        "qalqala_sughra"
    }
    assert {stopped_names[x] for x in stopped_dal.rule_occurrence_ids} == {
        "qalqala_kubra"
    }
