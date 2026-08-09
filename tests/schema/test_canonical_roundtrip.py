"""A version bump must be a clear rejection, never a misread."""
from __future__ import annotations

import json

import pytest

from quranic_phonemizer import Phonemizer
from quranic_phonemizer.phonemize.document import SCHEMA_VERSION
from quranic_phonemizer.phonemize.schema import canonical_bytes, to_canonical
from quranic_phonemizer.phonemize.schema_checks import SchemaError, validate


def test_the_same_request_serializes_byte_stable():
    a = Phonemizer().phonemize("1:1")
    b = Phonemizer().phonemize("1:1")
    assert canonical_bytes(a) == canonical_bytes(b)


def test_a_different_request_serializes_differently():
    a = Phonemizer().phonemize("1:1")
    b = Phonemizer().phonemize("1:2")
    assert canonical_bytes(a) != canonical_bytes(b)


def test_json_round_trip_is_lossless_and_still_valid():
    r = Phonemizer().phonemize("2:255")
    once = to_canonical(r)
    loaded = json.loads(json.dumps(once, sort_keys=True, ensure_ascii=False))
    validate(loaded)
    assert json.dumps(loaded, sort_keys=True) == json.dumps(once, sort_keys=True)


def test_canonical_bytes_is_valid_utf8_json():
    r = Phonemizer().phonemize("2:255")
    reparsed = json.loads(canonical_bytes(r).decode("utf-8"))
    assert reparsed["ref"] == "2:255"
    assert reparsed["schema_version"] == SCHEMA_VERSION


def test_an_older_reader_rejects_a_newer_version_clearly():
    """A reader pinned to today's `SCHEMA_VERSION` must refuse a document
    stamped with a version it does not know, rather than misinterpret it."""
    r = Phonemizer().phonemize("1:1")
    data = to_canonical(r)
    data["schema_version"] = str(int(SCHEMA_VERSION) + 1)
    with pytest.raises(SchemaError, match="unknown schema version"):
        validate(data)
