"""The packed corpus: one binary per riwayah, addressed by location."""
from __future__ import annotations

import array
import bisect
import gzip
import json
import struct
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import TypeAlias

from .model.address import (
    Location,
    SourceGraphemeRef,
    SourceLocation,
    VerseRef,
)


@dataclass(frozen=True, slots=True)
class SourceWord:
    location: SourceLocation
    text: str


@dataclass(frozen=True, slots=True)
class AlignedWord:
    location: Location
    canonical: tuple[Location, ...]
    sources: tuple[SourceWord, ...]

    @property
    def text(self) -> str:
        return " ".join(source.text for source in self.sources)


@dataclass(frozen=True, slots=True)
class PackedCorpus:
    texts: tuple[str, ...]
    word_indices: tuple[int, ...]
    verse_starts: Mapping[tuple[int, int], int]
    surah_info: Mapping[str, tuple[int, ...]]

    def word(self, location: Location) -> str:
        index = self.verse_starts[(location.surah, location.ayah)] + location.word - 1
        return self.texts[self.word_indices[index]]

    def words(self, verse: VerseRef) -> tuple[tuple[Location, str], ...]:
        count = self.surah_info[str(verse.surah)][verse.ayah - 1]
        return tuple(
            (location, self.word(location))
            for location in (
                Location(verse.surah, verse.ayah, index)
                for index in range(1, count + 1)
            )
        )

    def contains_full_verse(
        self, verse: VerseRef, locations: tuple[Location, ...]
    ) -> bool:
        return len(locations) == self.surah_info[str(verse.surah)][verse.ayah - 1]

    def locations(self, reference: str) -> tuple[Location, ...]:
        if "-" in reference:
            left, right = reference.split("-", 1)
            start = _parse_endpoint(left.strip())
            end = _parse_endpoint(right.strip())
        else:
            start = end = _parse_endpoint(reference)

        if _depth(start) != _depth(end):
            raise ValueError(
                f"Reference endpoints are at different depths: {reference}"
            )

        low = _canonical_endpoint(start, end=False)
        high = _canonical_endpoint(end, end=True)
        if low > high:
            raise ValueError(f"Reference starts after it ends: {reference}")

        result: list[Location] = []
        for surah in range(max(low[0], 1), high[0] + 1):
            verses = self.surah_info.get(str(surah))
            if verses is None:
                continue
            first_ayah = max(low[1] if surah == low[0] else 1, 1)
            last_ayah = min(high[1] if surah == high[0] else len(verses), len(verses))
            for ayah in range(first_ayah, last_ayah + 1):
                count = verses[ayah - 1]
                first_word = max(
                    low[2] if (surah, ayah) == low[:2] else 1,
                    1,
                )
                last_word = min(
                    high[2] if (surah, ayah) == high[:2] else count,
                    count,
                )
                result.extend(
                    Location(surah, ayah, word)
                    for word in range(first_word, last_word + 1)
                )
        if not result:
            raise ValueError(f"Reference selects no words: {reference}")
        return tuple(result)

    @staticmethod
    def public_ref(location: Location) -> str:
        return str(location)

    def verse_ends(self, locations: tuple[Location, ...]) -> frozenset[Location]:
        return frozenset(
            location
            for location in locations
            if location.word
            == self.surah_info[str(location.surah)][location.ayah - 1]
        )


@dataclass(frozen=True, slots=True)
class AlignedCorpus:
    """A selected-source corpus aligned to internal canonical locations."""

    entries: Mapping[Location, AlignedWord]
    canonical_to_runtime: Mapping[Location, Location]
    by_verse: Mapping[VerseRef, tuple[Location, ...]]
    surah_info: Mapping[str, tuple[int, ...]]
    source_to_runtime: Mapping[Location, Location]
    source_locations: tuple[Location, ...]
    source_by_verse: Mapping[VerseRef, tuple[Location, ...]]
    source_verse_ends: frozenset[Location]

    def word(self, location: Location) -> str:
        try:
            return self.entries[self.canonical_to_runtime[location]].text
        except KeyError:
            raise ValueError(f"{location} is absent in this riwayah") from None

    def words(self, verse: VerseRef) -> tuple[tuple[Location, str], ...]:
        return tuple(
            (location, self.entries[location].text)
            for location in self.by_verse.get(verse, ())
        )

    def contains_full_verse(
        self, verse: VerseRef, locations: tuple[Location, ...]
    ) -> bool:
        return locations == self.by_verse.get(verse, ())

    def locations(self, reference: str) -> tuple[Location, ...]:
        if "-" in reference:
            left, right = reference.split("-", 1)
            start = _parse_endpoint(left.strip())
            end = _parse_endpoint(right.strip())
        else:
            start = end = _parse_endpoint(reference)
        if _depth(start) != _depth(end):
            raise ValueError(
                f"Reference endpoints are at different depths: {reference}"
            )
        low = _canonical_endpoint(start, end=False)
        high = _canonical_endpoint(end, end=True)
        if low > high:
            raise ValueError(f"Reference starts after it ends: {reference}")
        first = bisect.bisect_left(self.source_locations, Location(*low))
        last = bisect.bisect_right(self.source_locations, Location(*high))
        result: list[Location] = []
        for source in self.source_locations[first:last]:
            runtime = self.source_to_runtime[source]
            if not result or result[-1] != runtime:
                result.append(runtime)
        if not result:
            raise ValueError(f"Reference selects no words: {reference}")
        return tuple(result)

    def public_ref(self, location: Location) -> str:
        entry = self.entries[self.canonical_to_runtime[location]]
        refs = tuple(
            Location(source.location.surah, source.location.ayah,
                     source.location.word)
            for source in entry.sources
        )
        if len(refs) == 1:
            return str(refs[0])
        return f"{refs[0]}-{refs[-1]}"

    def verse_ends(self, locations: tuple[Location, ...]) -> frozenset[Location]:
        return frozenset(
            location for location in locations
            if location in self.source_verse_ends
        )

    def sources_for(
        self, location: Location, text: str
    ) -> tuple[SourceGraphemeRef | None, ...]:
        entry = self.entries[self.canonical_to_runtime[location]]
        sources: list[SourceGraphemeRef | None] = []
        for index, source in enumerate(entry.sources):
            if index:
                sources.append(None)
            sources.extend(
                SourceGraphemeRef(source.location, offset)
                for offset in range(len(source.text))
            )
        if entry.text != text or len(sources) != len(text):
            raise ValueError(f"{location}: aligned source text drifted")
        return tuple(sources)


Corpus: TypeAlias = PackedCorpus | AlignedCorpus


def _parse_endpoint(value: str) -> tuple[int, int | None, int | None]:
    parts = value.split(":")
    if not 1 <= len(parts) <= 3:
        raise ValueError(f"Invalid reference endpoint: {value}")
    try:
        numbers = tuple(int(part) for part in parts)
    except ValueError as error:
        raise ValueError(f"Invalid reference endpoint: {value}") from error
    return (
        numbers[0],
        numbers[1] if len(numbers) > 1 else None,
        numbers[2] if len(numbers) > 2 else None,
    )


def _depth(endpoint: tuple[int, int | None, int | None]) -> int:
    """`surah` alone is depth 1; `surah:ayah:word` is depth 3."""
    return 1 + (endpoint[1] is not None) + (endpoint[2] is not None)


def _canonical_endpoint(
    endpoint: tuple[int, int | None, int | None],
    *,
    end: bool,
) -> tuple[int, int, int]:
    surah, ayah, word = endpoint
    upper = 10_000 if end else 0
    return (
        surah,
        ayah if ayah is not None else upper,
        word if word is not None else upper,
    )


def load_corpus(db_path: Path, info_path: Path) -> PackedCorpus:
    raw_info = json.loads(info_path.read_text(encoding="utf-8"))
    surah_info = {key: tuple(value) for key, value in raw_info.items()}
    surahs = sorted(int(key) for key in surah_info)
    verse_starts: dict[tuple[int, int], int] = {}
    total_words = 0
    for surah in surahs:
        for ayah, count in enumerate(surah_info[str(surah)], start=1):
            verse_starts[(surah, ayah)] = total_words
            total_words += count

    data = db_path.read_bytes()
    word_count, text_count = struct.unpack_from("<II", data)
    position = 8

    offsets = array.array("I")
    offsets.frombytes(data[position : position + (text_count + 1) * 4])
    position += (text_count + 1) * 4

    text_bytes = struct.unpack_from("<I", data, position)[0]
    position += 4
    blob = data[position : position + text_bytes]
    position += text_bytes

    indices = array.array("H")
    indices.frombytes(data[position : position + word_count * 2])
    if word_count != total_words:
        raise ValueError(
            f"Corpus has {word_count} words but its address file has {total_words}"
        )

    texts = tuple(
        blob[offsets[index] : offsets[index + 1]].decode("utf-8")
        for index in range(text_count)
    )
    return PackedCorpus(
        texts,
        tuple(indices),
        MappingProxyType(verse_starts),
        MappingProxyType(surah_info),
    )


def load_aligned_corpus(path: Path, *, artifact: str) -> AlignedCorpus:
    """Load the complete selected-source/internal alignment artifact."""
    entries: dict[Location, AlignedWord] = {}
    canonical_to_runtime: dict[Location, Location] = {}
    by_verse: dict[VerseRef, list[Location]] = {}
    source_to_runtime: dict[Location, Location] = {}
    source_by_verse: dict[VerseRef, list[Location]] = {}
    canonical_verses: dict[int, int] = {}
    canonical_counts: dict[VerseRef, int] = {}
    with gzip.open(path, "rt", encoding="utf-8") as source:
        header = json.loads(source.readline())
        if header != {"schema_version": 1, "artifact": artifact}:
            raise ValueError(f"{path}: unexpected alignment header {header!r}")
        for line_number, line in enumerate(source, start=2):
            row = json.loads(line)
            canonical = tuple(_location(value) for value in row["canonical"])
            sources = tuple(
                SourceWord(
                    SourceLocation(artifact, *_parts(item["ref"])),
                    item["text"],
                )
                for item in row["source"]
            )
            for location in canonical:
                canonical_verses[location.surah] = max(
                    canonical_verses.get(location.surah, 0), location.ayah
                )
                canonical_counts[location.verse] = max(
                    canonical_counts.get(location.verse, 0), location.word
                )
            if not sources:
                continue
            _bind_aligned_word(
                path, line_number, canonical, sources,
                entries, canonical_to_runtime, by_verse,
                source_to_runtime, source_by_verse,
            )

    ordered = dict(sorted(entries.items()))
    frozen_by_verse = {
        verse: tuple(sorted(locations)) for verse, locations in by_verse.items()
    }
    frozen_source_by_verse = {
        verse: tuple(locations) for verse, locations in source_by_verse.items()
    }
    return AlignedCorpus(
        MappingProxyType(ordered),
        MappingProxyType(dict(sorted(canonical_to_runtime.items()))),
        MappingProxyType(frozen_by_verse),
        MappingProxyType(_surah_info(canonical_verses, canonical_counts)),
        MappingProxyType(dict(sorted(source_to_runtime.items()))),
        tuple(sorted(source_to_runtime)),
        MappingProxyType(frozen_source_by_verse),
        frozenset(words[-1] for words in frozen_source_by_verse.values()),
    )


def _bind_aligned_word(
    path, line_number, canonical, sources,
    entries, canonical_to_runtime, by_verse,
    source_to_runtime, source_by_verse,
) -> None:
    if not canonical:
        raise ValueError(f"{path}:{line_number}: source-only row")
    runtime = canonical[0]
    if runtime in entries:
        raise ValueError(f"{path}:{line_number}: duplicate {runtime}")
    for alias in canonical:
        if alias in canonical_to_runtime:
            raise ValueError(
                f"{path}:{line_number}: duplicate canonical {alias}"
            )
        canonical_to_runtime[alias] = runtime
    entries[runtime] = AlignedWord(runtime, canonical, sources)
    by_verse.setdefault(runtime.verse, []).append(runtime)
    for source in sources:
        location = Location(
            source.location.surah, source.location.ayah, source.location.word
        )
        if location in source_to_runtime:
            raise ValueError(f"{path}:{line_number}: duplicate source {location}")
        source_to_runtime[location] = runtime
        verse_words = source_by_verse.setdefault(location.verse, [])
        if not verse_words or verse_words[-1] != runtime:
            verse_words.append(runtime)


def _surah_info(canonical_verses, canonical_counts):
    return {
        str(surah): tuple(
            canonical_counts.get(VerseRef(surah, ayah), 0)
            for ayah in range(1, canonical_verses[surah] + 1)
        )
        for surah in sorted(canonical_verses)
    }


def _parts(value: str) -> tuple[int, int, int]:
    parts = tuple(int(part) for part in value.split(":"))
    if len(parts) != 3:
        raise ValueError(f"expected a word ref, got {value!r}")
    return parts


def _location(value: str) -> Location:
    return Location(*_parts(value))
