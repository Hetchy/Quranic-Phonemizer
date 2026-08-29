from __future__ import annotations

import pytest

from quranic_phonemizer.riwayat.khilaf import KhilafError, load_khilaf


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
