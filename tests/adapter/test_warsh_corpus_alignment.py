"""Selected-source words aligned to canonical/public Quran addresses."""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

import pytest

from quranic_phonemizer.model.address import Location, SourceLocation, VerseRef
from quranic_phonemizer.riwayat.warsh.resources import ARTIFACT, corpus

ROOT = Path(__file__).resolve().parents[2]
ALIGNMENT = (
    ROOT / "quranic_phonemizer" / "data" / "riwayat" / "warsh"
    / "corpus" / "alignment.jsonl.gz"
)
CANONICAL = ROOT / "corpus_sources" / "hafs" / "scripts" / "uthmani" / "quran.json"
SOURCE = ROOT / "corpus_sources" / "warsh" / "scripts" / "king-fahd" / "quran.json"


def _key(ref: str) -> tuple[int, int, int]:
    return tuple(int(part) for part in ref.split(":"))  # type: ignore[return-value]


@pytest.fixture(scope="module")
def artifact():
    with gzip.open(ALIGNMENT, "rt", encoding="utf-8") as source:
        header = json.loads(source.readline())
        rows = tuple(json.loads(line) for line in source)
    return header, rows


def test_the_pinned_alignment_is_deterministic(artifact):
    header, rows = artifact
    assert header == {"schema_version": 1, "artifact": ARTIFACT}
    assert len(rows) == 77_426
    assert hashlib.sha256(ALIGNMENT.read_bytes()).hexdigest() == (
        "7ccdb7664ec0f625f2808207f614983cc21c6462bf1463d1813d448000f70aad"
    )


def test_every_source_and_canonical_word_occurs_once_in_order(artifact):
    _, rows = artifact
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    canonical = json.loads(CANONICAL.read_text(encoding="utf-8"))
    source_refs = [item["ref"] for row in rows for item in row["source"]]
    canonical_refs = [ref for row in rows for ref in row["canonical"]]

    assert source_refs == sorted(source, key=_key)
    assert canonical_refs == sorted(canonical, key=_key)
    assert [item["ordinal"] for row in rows for item in row["source"]] == list(
        range(1, 77_426)
    )
    assert all(item["text"] == source[item["ref"]]["text"]
               for row in rows for item in row["source"])


def test_only_the_reviewed_cardinality_spans_differ(artifact):
    _, rows = artifact
    edits = {
        tuple(row["canonical"]): tuple(item["ref"] for item in row["source"])
        for row in rows
        if len(row["canonical"]) != 1 or len(row["source"]) != 1
    }
    assert edits == {
        ("1:1:1", "1:1:2", "1:1:3", "1:1:4"): (),
        ("15:7:1", "15:7:2"): ("15:7:1",),
        ("27:20:4", "27:20:5"): ("27:20:4",),
        ("36:22:1", "36:22:2"): ("36:21:1",),
        ("40:26:13", "40:26:14"): ("40:26:13",),
        ("57:24:10",): (),
        ("72:16:1",): ("72:16:1", "72:16:2"),
    }


def test_runtime_lookup_is_public_and_provenance_is_source_typed():
    aligned = corpus()
    entry = aligned.entries[Location(2, 3, 1)]
    assert entry.sources[0].location == SourceLocation(ARTIFACT, 2, 2, 1)
    assert aligned.words(VerseRef(2, 3))[0] == (entry.location, entry.text)
    with pytest.raises(ValueError, match="absent"):
        aligned.word(Location(1, 1, 1))


def test_a_two_source_word_preserves_both_source_runs_and_the_separator():
    aligned = corpus()
    entry = aligned.entries[Location(72, 16, 1)]
    refs = aligned.sources_for(entry.location, entry.text)
    split = len(entry.sources[0].text)

    assert [source.location.word for source in entry.sources] == [1, 2]
    assert refs[split] is None
    assert refs[0].location == entry.sources[0].location
    assert refs[-1].location == entry.sources[1].location
    assert refs[-1].offset == len(entry.sources[1].text) - 1


def test_each_coordinate_of_a_canonical_span_resolves_the_same_runtime_word():
    aligned = corpus()
    first = Location(15, 7, 1)
    second = Location(15, 7, 2)

    assert aligned.entries[first].canonical == (first, second)
    assert aligned.locations("15:7:1") == (first,)
    assert aligned.locations("15:7:2") == (first,)
    assert aligned.word(second) == aligned.word(first) == "لَّوْمَا"
    assert aligned.contains_full_verse(
        first.verse, aligned.locations("15:7")
    )
