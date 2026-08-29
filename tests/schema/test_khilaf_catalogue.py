from __future__ import annotations

import pytest

from quranic_phonemizer.model.address import Location
from quranic_phonemizer.riwayat.khilaf import (
    KhilafError,
    VariantSpan,
    load_khilaf,
)


def _catalogue(tmp_path, identifier: str):
    path = tmp_path / "khilaf.yaml"
    path.write_text(
        "\n".join((
            "schema_version: 3",
            "variants:",
            f"  {identifier}:",
            "    kind: rule",
            "    options: [first, second]",
            "    default: first",
            "    source: docs/variants.md",
            "catalogue:",
            f"  {identifier}:",
            "    group: test",
            "    display_name: Future selector",
            "    website_visible: false",
            "    dynamic_scope: test",
        )),
        encoding="utf-8",
    )
    return path


def test_a_catalogue_declares_its_own_selector_ids(tmp_path):
    khilaf = load_khilaf(_catalogue(tmp_path, "future_selector"))
    assert khilaf.points() == {
        "future_selector": {
            "options": ["first", "second"],
            "default": "first",
        }
    }


def test_selector_ids_use_the_public_ascii_spelling(tmp_path):
    with pytest.raises(KhilafError, match="invalid variant ID"):
        load_khilaf(_catalogue(tmp_path, "Future-Selector"))


def _entry(tmp_path, catalogue_lines: tuple[str, ...]):
    path = tmp_path / "khilaf.yaml"
    path.write_text(
        "\n".join((
            "schema_version: 3",
            "variants:",
            "  future_selector:",
            "    kind: rule",
            "    options: [first, second]",
            "    default: first",
            "    source: docs/variants.md",
            "catalogue:",
            "  future_selector:",
            "    group: test",
            "    display_name: Future selector",
            "    website_visible: false",
            *catalogue_lines,
        )),
        encoding="utf-8",
    )
    return path


def test_a_catalogue_entry_may_declare_a_subgroup(tmp_path):
    path = _entry(tmp_path, (
        "    subgroup: lexical",
        "    occurrences:",
        "      - {words: ['1:1:1'], anchor: word, requires: all}",
    ))
    entry = next(iter(load_khilaf(path).catalogue.values()))
    assert entry.subgroup == "lexical"


def test_a_catalogue_entry_may_source_spans_from_an_authored_register(tmp_path):
    path = _entry(tmp_path, ("    register: meetings",))
    spans = (VariantSpan((Location(1, 1, 1),), "word", "all"),)
    khilaf = load_khilaf(path, registers={"meetings": spans})
    entry = next(iter(khilaf.catalogue.values()))
    assert entry.spans == spans
    with pytest.raises(KhilafError, match="unknown register"):
        load_khilaf(path)


def test_occurrence_sources_are_mutually_exclusive(tmp_path):
    path = _entry(tmp_path, (
        "    register: meetings",
        "    dynamic_scope: test",
    ))
    with pytest.raises(KhilafError, match="mutually exclusive"):
        load_khilaf(path, registers={"meetings": ()})
