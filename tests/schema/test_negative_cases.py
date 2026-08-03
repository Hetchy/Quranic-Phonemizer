"""02-gate section 5's fourteen negative cases, over a real canonical
document. Every mutation is minimal; a schema that accepts it is too loose.
"""
from __future__ import annotations

import copy
import json

import pytest

from quranic_phonemizer import Phonemizer
from quranic_phonemizer.phonemize.schema import to_canonical, to_pairing
from quranic_phonemizer.phonemize.schema_checks import (
    SchemaError,
    check_rendered_glyph,
    validate,
    validate_pairings,
)


@pytest.fixture(scope="module")
def base() -> dict:
    r = Phonemizer().phonemize("1:1")
    return json.loads(json.dumps(to_canonical(r)))


@pytest.fixture
def data(base) -> dict:
    return copy.deepcopy(base)


def test_valid_document_passes(data):
    validate(data)


@pytest.mark.parametrize("ref", ["1:1", "2:255", "2:1-2:8", "18:1-18:6", "4:1-4:6"])
def test_real_pairings_validate_under_both_texts_and_groupings(ref):
    """A real document's own `alignment()`, which the synthetic rows below
    never exercise, must validate as readily as they are rejected."""
    r = Phonemizer().phonemize(ref)
    canon = json.loads(json.dumps(to_canonical(r)))
    structural = {
        e["glyph"] for e in canon["spellings"] if e["kind"] == "structural"
    }
    for text, glyphs in (("source", canon["glyphs"]), ("recited", canon["rendered"])):
        excluded = structural if text == "source" else {
            i for i, g in enumerate(glyphs) if g["word"] is None
        }
        for grouping in ("glyph", "cell"):
            pairings = [to_pairing(p) for p in r.alignment(text=text, grouping=grouping)]
            validate_pairings(
                pairings, glyphs, excluded,
                n_sounds=len(canon["sounds"]), n_rules=len(canon["rules"]),
            )


def test_a_nullable_quality_on_an_incompatible_vowel_kind(data):
    data["units"][0]["vowel"]["joined"] = {"kind": "absent", "quality": "a"}
    with pytest.raises(SchemaError):
        validate(data)


def test_a_short_vowel_with_no_quality(data):
    data["units"][0]["vowel"]["joined"] = {"kind": "short"}
    with pytest.raises(SchemaError):
        validate(data)


def test_a_sound_carrying_fields_from_two_kinds(data):
    data["sounds"][0]["quality"] = "a"
    with pytest.raises(SchemaError):
        validate(data)


def test_structural_with_a_word(data):
    structural = next(e for e in data["spellings"] if e["kind"] == "structural")
    data["glyphs"][structural["glyph"]]["word"] = 0
    with pytest.raises(SchemaError):
        validate(data)


def test_supplies_without_a_fact(data):
    supplies = next(e for e in data["spellings"] if e["kind"] == "supplies")
    del supplies["fact"]
    with pytest.raises(SchemaError):
        validate(data)


def test_an_attribution_naming_two_units(data):
    hosts = next(e for e in data["attributions"] if e["kind"] == "hosts")
    hosts["second_unit"] = hosts["unit"]
    with pytest.raises(SchemaError):
        validate(data)


def test_silent_carrying_a_sound(data):
    silent = next((e for e in data["attributions"] if e["kind"] == "silent"), None)
    if silent is None:
        silent = dict(data["attributions"][0])
        silent.update(kind="silent", part="consonant")
        data["attributions"].append(silent)
    silent["sound"] = 0
    with pytest.raises(SchemaError):
        validate(data)


def test_an_attribution_without_a_part(data):
    hosts = next(e for e in data["attributions"] if e["kind"] == "hosts")
    del hosts["part"]
    with pytest.raises(SchemaError):
        validate(data)


def test_a_merger_without_its_host(data):
    merger = next((e for e in data["attributions"] if e["kind"] == "mergedinto"), None)
    if merger is None:
        pytest.skip("1:1 has no cross-word merger to model this on")
    data["rules"][merger["by"]]["host"] = None
    with pytest.raises(SchemaError):
        validate(data)


def test_a_pairing_target_out_of_range(data):
    pairing = {"glyphs": [10_000], "sounds": [], "shares": [], "silent": [],
               "rules": [], "after": None}
    with pytest.raises(SchemaError):
        validate_pairings([pairing], data["glyphs"], set(), n_sounds=0, n_rules=0)


def test_a_non_structural_glyph_in_no_pairing(data):
    assert data["glyphs"], "1:1 writes at least one glyph"
    with pytest.raises(SchemaError):
        validate_pairings([], data["glyphs"], set(), n_sounds=0, n_rules=0)


def test_a_rendered_glyph_with_an_empty_character(data):
    data["rendered"][0]["char"] = ""
    with pytest.raises(SchemaError):
        check_rendered_glyph(data["rendered"][0])


def test_a_gap_row_with_glyphs(data):
    pairing = {"glyphs": [0], "sounds": [], "shares": [], "silent": [],
               "rules": [], "after": 0}
    with pytest.raises(SchemaError):
        validate_pairings(
            [pairing, pairing], data["glyphs"], set(),
            n_sounds=len(data["sounds"]), n_rules=len(data["rules"]),
        )


def test_duplicate_canonical_relations(data):
    data["spellings"].append(dict(data["spellings"][0]))
    with pytest.raises(SchemaError):
        validate(data)


def test_an_unknown_schema_version(data):
    data["schema_version"] = "99"
    with pytest.raises(SchemaError):
        validate(data)
