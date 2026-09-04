"""The versioned wire schema: frozen golden, round-trip, and closed references.

The reflected schema is compared to committed fixtures, every document round-trips
through JSON and validates, and every id reference resolves across the documents.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from quranic_phonemizer.analysis import schema as wire
from quranic_phonemizer.analysis.build import build_bundle
from quranic_phonemizer.analysis.cells.view import build_cell_view
from quranic_phonemizer.analysis.highlights import highlight_groups
from quranic_phonemizer.analysis.ids import SCHEMA_VERSION
from quranic_phonemizer.analysis.result import build_result
from quranic_phonemizer.analysis.source import build_source_view
from quranic_phonemizer.model.address import Location, Script
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.session import phonemize_request
from quranic_phonemizer.session.boundaries import resolve_boundaries
from quranic_phonemizer.session.core import Session
from quranic_phonemizer.session.request import resolve_words

FIXTURES = Path(__file__).resolve().parent / "schema"

#: One reference per boundary state and hard case: a lone word, a start, joined
#: words, a cross-word idgham with a sakt, an iltiqa, a tanween idgham, a long
#: ayah, and internal stops.
SITES = [
    ("1:1:1", {}),
    ("112:1", {}),
    ("1:1", {}),
    ("36:52-36:53", {}),
    ("3:1-3:2", {}),
    ("2:5", {}),
    ("2:255", {}),
    ("52:1:1", {}),
    ("18:38", {"stop_refs": ["18:38:1"]}),
    ("1:2", {"stop_refs": ["1:2:1"]}),
]


def _canon(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def _indopak_text(sources, location: Location) -> str:
    for candidate, text in sources[Script.INDOPAK][(location.surah, location.ayah)]:
        if candidate.word == location.word:
            return text
    raise KeyError(location)


def _indopak_session(hafs, sources, locations, stop_refs=()):
    """One indopak span over exactly `locations`, so a ref that spans verses,
    words, or stops reads the same words its uthmani counterpart does."""
    words = tuple((loc, _indopak_text(sources, loc)) for loc in locations)
    built = hafs.build(hafs.read(Script.INDOPAK, locations[0].verse, words))
    boundaries = resolve_boundaries(
        built.inscription.advice, locations, built.score, stop_refs=stop_refs
    )
    performance = hafs.perform(built.score, boundaries)
    return Session(locations, built.score, built.inscription, boundaries, performance)


def _documents(hafs, session, ref, script):
    """The four documents plus the source-spelled cell view, each as one
    (kind, serialized, schema) triple ready to validate."""
    kw = dict(ref=ref, riwayah="hafs", script=script.value, variant={})
    bundle = build_bundle(session, **kw)
    source = build_source_view(session, bundle=bundle)
    pen = pen_for(hafs.inventory(script))
    built = {
        "analysis_result": wire.analysis_document(build_result(session, **kw)),
        "source_view": wire.source_document(source),
        "highlight_groups": wire.highlight_document(
            highlight_groups(source, bundle)
        ),
        "cell_view": wire.cell_document(
            build_cell_view(session, **kw, spelling="transformed", pen=pen)
        ),
    }
    triples = [
        (kind, wire.serialize_document(doc), wire.document_schema(kind))
        for kind, doc in built.items()
    ]
    source_cells = wire.cell_document(build_cell_view(session, **kw))
    triples.append(
        ("cell_view", wire.serialize_document(source_cells),
         wire.document_schema("cell_view"))
    )
    return triples


# ---- the frozen golden schema and its version ----

def test_the_reflected_schema_matches_the_frozen_fixture():
    """A field added to a record changes the reflected schema; when it does,
    regenerate the fixtures and bump SCHEMA_VERSION."""
    for kind in wire.KINDS:
        assert _canon(wire.document_schema(kind)) == _fixture(f"{kind}.schema.json")


def test_each_frozen_schema_pins_the_current_version():
    for kind in wire.KINDS:
        frozen = json.loads(_fixture(f"{kind}.schema.json"))
        root = frozen["$defs"][frozen["$ref"].split("/")[-1]]
        assert root["properties"]["schema_version"]["const"] == SCHEMA_VERSION


def test_the_version_record_tracks_the_fixtures_and_the_code():
    """Regenerating a fixture without updating version.json, or bumping the
    version alone, breaks this: the digest and the version move together."""
    record = json.loads(_fixture("version.json"))
    assert record["schema_version"] == SCHEMA_VERSION
    blob = b"".join(
        _fixture(f"{kind}.schema.json").encode("utf-8") for kind in wire.KINDS
    )
    assert record["digest"] == hashlib.sha256(blob).hexdigest()


# ---- round-trip and closed references over every boundary state ----

@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_documents_round_trip_and_validate_uthmani(hafs, ref, kwargs):
    session = phonemize_request(hafs, ref, **kwargs)
    _check(_documents(hafs, session, ref, Script.UTHMANI))


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_documents_round_trip_and_validate_indopak(hafs, sources, ref, kwargs):
    locations = resolve_words(hafs.corpus, hafs.ledger, ref)
    session = _indopak_session(
        hafs, sources, locations, stop_refs=kwargs.get("stop_refs", ())
    )
    _check(_documents(hafs, session, ref, Script.INDOPAK))


def _check(triples):
    pairs = []
    for kind, serialized, schema in triples:
        reloaded = json.loads(json.dumps(serialized, ensure_ascii=False))
        assert reloaded == serialized, kind
        assert not wire.validation_errors(schema, serialized), kind
        assert not wire.closed_reference_errors(schema, serialized), kind
        pairs.append((schema, serialized))
    assert not wire.combined_reference_errors(pairs)


def test_the_sites_reference_every_target_record(hafs):
    """The combined check would flag an absent target; over these refs each of
    the referenced records is present, so no reference is left open."""
    session = phonemize_request(hafs, "2:255")
    triples = _documents(hafs, session, "2:255", Script.UTHMANI)
    pairs = [(schema, ser) for _, ser, schema in triples]
    assert wire.combined_reference_errors(pairs) == []
