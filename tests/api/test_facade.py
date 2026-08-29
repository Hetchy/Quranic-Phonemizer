"""The root facade and its configuration-scoped consumer contract."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

import quranic_phonemizer as package
from quranic_phonemizer import (
    Phonemizer,
    Result,
    UnknownRule,
    UnknownStopSign,
    available_stop_signs,
    available_variants,
    tajweed_rules,
)
from quranic_phonemizer.analysis import (
    AnalysisResult,
    BoundaryState,
    CharacterKind,
    SourceView,
    analysis_document,
    cell_document,
    serialize_document,
)
from quranic_phonemizer.analysis.cells import CellView
from quranic_phonemizer.model.inscription import StopAdvice


def test_the_root_exports_the_facade_without_the_legacy_graph():
    assert isinstance(Phonemizer().analyse("1:1"), Result)
    assert not hasattr(package, "PhonemizeResult")
    assert not hasattr(package, "edges")
    assert not hasattr(package, "nodes")


def test_the_eager_core_exposes_the_native_records():
    result = Phonemizer().analyse("2:5")
    assert isinstance(result.analysis, AnalysisResult)
    assert result.words is result.analysis.words
    assert result.boundaries is result.analysis.boundaries
    assert result.sounds is result.analysis.sounds
    assert result.rule_occurrences is result.analysis.rule_occurrences
    assert result.mergers is result.analysis.mergers
    assert result.text() == result.analysis.text()
    assert result.phonemes() == tuple(sound.token for sound in result.sounds)
    assert result.phonemes(by="word") == result.analysis.phonemes("word")


def test_selective_projections_are_native_and_cached():
    result = Phonemizer().analyse("2:5")
    source = result.source()
    highlights = result.highlights()
    source_cells = result.cells(spelling="source")
    transformed_cells = result.cells(spelling="transformed")

    assert isinstance(source, SourceView)
    assert isinstance(source_cells, CellView)
    assert isinstance(transformed_cells, CellView)
    assert result.source() is source
    assert result.highlights() is highlights
    assert result.cells(spelling="source") is source_cells
    assert result.cells(spelling="transformed") is transformed_cells


def test_source_projection_does_not_build_cells(monkeypatch):
    result = Phonemizer().analyse("1:1")

    def fail(*args, **kwargs):
        raise AssertionError("cell construction was requested")

    monkeypatch.setattr(
        "quranic_phonemizer.analysis.facade.build_cell_view", fail
    )
    assert result.source().text == result.text()


def test_cells_reuse_the_eager_facts_and_bundle(monkeypatch):
    result = Phonemizer().analyse("2:5")

    def fail(*args, **kwargs):
        raise AssertionError("shared analysis state was rebuilt")

    for name in ("analyse", "inscribe", "build_bundle"):
        monkeypatch.setattr(
            f"quranic_phonemizer.analysis.cells.view.{name}", fail
        )
    assert result.cells(spelling="source").words
    assert result.cells(spelling="transformed").words


def test_concurrent_source_calls_build_once(monkeypatch):
    result = Phonemizer().analyse("2:255")
    original = __import__(
        "quranic_phonemizer.analysis.facade", fromlist=["build_source_view"]
    ).build_source_view
    calls = []

    def counted(*args, **kwargs):
        calls.append(None)
        return original(*args, **kwargs)

    monkeypatch.setattr(
        "quranic_phonemizer.analysis.facade.build_source_view", counted
    )
    gate = Barrier(8)

    def source():
        gate.wait()
        return result.source()

    with ThreadPoolExecutor(max_workers=8) as pool:
        views = tuple(pool.map(lambda _: source(), range(8)))
    assert len(calls) == 1
    assert all(view is views[0] for view in views)


def test_projection_ids_close_over_one_native_space():
    result = Phonemizer().analyse("2:5")
    source = result.source()
    cells = result.cells(spelling="transformed")
    columns = tuple(column for word in cells.words for column in word.columns)
    cell_sounds = {
        sound.sound_id
        for word in cells.words for sound in word.sounds
    } | {
        bridge.sound.sound_id
        for boundary in cells.boundaries for bridge in boundary.bridges
    }
    cell_units = {
        unit for column in columns for unit in column.source_unit_ids
    }
    cell_occurrences = {
        occurrence for column in columns
        for occurrence in column.rule_occurrence_ids
    }
    bridges = {
        bridge.merger_id
        for boundary in cells.boundaries for bridge in boundary.bridges
    }

    assert cell_sounds == {sound.id for sound in result.sounds}
    assert cell_units <= {unit.id for unit in source.units}
    assert cell_occurrences <= {
        occurrence.id for occurrence in result.rule_occurrences
    }
    assert bridges == {
        merger.id for merger in result.mergers if merger.boundary_id is not None
    }


def test_every_document_is_the_native_serialization():
    result = Phonemizer().analyse("2:5")
    transformed = result.cells(spelling="transformed")

    assert result.document("analysis_result") == serialize_document(
        analysis_document(result.analysis)
    )
    assert result.document(
        "cell_view", spelling="transformed"
    ) == serialize_document(cell_document(transformed))
    assert result.document("source_view")["schema_version"] == 3
    assert result.document("highlight_groups")["schema_version"] == 3


@pytest.mark.parametrize(
    ("riwayah", "script", "expected"),
    [
        (
            "hafs",
            "uthmani",
            (
                "verse",
                "preferred_continue",
                "preferred_stop",
                "optional_stop",
                "compulsory_stop",
                "prohibited_stop",
                "either_stop",
            ),
        ),
        (
            "hafs",
            "indopak",
            (
                "verse",
                "preferred_continue",
                "preferred_stop",
                "optional_stop",
                "compulsory_stop",
                "prohibited_stop",
                "either_stop",
                "permitted_stop",
            ),
        ),
        ("warsh", "uthmani", ("verse", "optional_stop")),
    ],
)
def test_stop_catalogues_are_configuration_scoped(riwayah, script, expected):
    reader = Phonemizer(riwayah=riwayah, script=script)
    assert reader.available_stop_signs == expected
    assert available_stop_signs(riwayah, script=script) == expected


@pytest.mark.parametrize("riwayah", ["hafs", "warsh"])
def test_reader_and_root_catalogues_agree(riwayah):
    reader = Phonemizer(riwayah=riwayah)
    assert reader.available_variants == available_variants(riwayah)
    assert reader.tajweed_rules == tajweed_rules(riwayah)
    result = reader.analyse("1:2")
    assert result.rule_catalogue == reader.tajweed_rules
    for definition in result.rule_catalogue:
        assert result.rule_definition(definition.id.value) is definition


def test_rule_lookup_is_scoped_to_the_selected_riwayah():
    result = Phonemizer(riwayah="warsh").analyse("1:2")
    unavailable = "not_a_rule"
    with pytest.raises(UnknownRule, match=unavailable):
        result.rule_definition(unavailable)


def test_warsh_requests_and_word_refs_use_its_source_coordinates():
    reader = Phonemizer(riwayah="warsh")

    result = reader.analyse("1:3")

    assert result.text() == "مَلِكِ يَوْمِ اِ۬لدِّينِۖ"
    assert tuple(word.ref for word in result.words) == (
        "1:3:1",
        "1:3:2",
        "1:3:3",
    )


@pytest.mark.parametrize(
    ("reader", "ref", "verse_final_ref"),
    [
        (Phonemizer(), "1:4-1:5", "1:4:3"),
        (Phonemizer(riwayah="warsh"), "1:3-1:4", "1:3:3"),
    ],
)
def test_verse_stop_is_published_and_stops_at_each_source_ayah(
    reader, ref, verse_final_ref
):
    assert "verse" in reader.available_stop_signs
    joined = reader.analyse(ref)
    stopped = reader.analyse(ref, stop_signs=("verse",))
    word = next(word for word in joined.words if word.ref == verse_final_ref)

    assert joined.boundaries[word.after_boundary_id.value].state is BoundaryState.JOIN
    assert stopped.boundaries[word.after_boundary_id.value].state is BoundaryState.STOP


def test_warsh_stop_sign_is_typed_and_requested_by_its_catalogue_name():
    reader = Phonemizer(riwayah="warsh")
    ref = "1:4-1:5"
    joined = reader.analyse(ref)
    selected = reader.analyse(ref, stop_signs=("optional_stop",))
    explicit = reader.analyse(ref, stop_refs=("1:4:4",))

    boundary = next(item for item in joined.boundaries if item.stop_sign == "ۖ")
    assert boundary.stop_advice is StopAdvice.OPTIONAL_STOP
    assert boundary.state is BoundaryState.JOIN
    assert selected.boundaries[boundary.id.value].state is BoundaryState.STOP
    assert explicit.boundaries[boundary.id.value].state is BoundaryState.STOP

    character = next(item for item in joined.source().characters if item.text == "ۖ")
    assert character.kind is CharacterKind.STOP_SIGN
    assert character.boundary_id == boundary.id
    assert character.word_id is None
    assert character.letter_unit_id is None


def test_unavailable_stop_names_fail_before_boundary_resolution(monkeypatch):
    reader = Phonemizer(riwayah="warsh")

    def fail(*args, **kwargs):
        raise AssertionError("boundary resolution was reached")

    monkeypatch.setattr(
        "quranic_phonemizer.analysis.facade.phonemize_request", fail
    )
    with pytest.raises(UnknownStopSign) as caught:
        reader.analyse("1:1", stop_signs=("preferred_stop", "unknown"))
    assert str(caught.value) == (
        "['preferred_stop', 'unknown'] is not available for warsh/uthmani; "
        "available stop signs: ['verse', 'optional_stop']"
    )


@pytest.mark.parametrize("spelling", ["recited", "all", ""])
def test_invalid_cell_spelling_is_user_facing(spelling):
    with pytest.raises(ValueError, match="spelling must be"):
        Phonemizer().analyse("1:1").cells(spelling=spelling)


def test_unknown_document_kind_is_user_facing():
    with pytest.raises(ValueError, match="unknown document kind"):
        Phonemizer().analyse("1:1").document("all")
