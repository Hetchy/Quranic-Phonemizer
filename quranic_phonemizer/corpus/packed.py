from __future__ import annotations

import array
import json
import struct
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from ..model.address import Location


@dataclass(frozen=True, slots=True)
class PackedCorpus:
    texts: tuple[str, ...]
    word_indices: tuple[int, ...]
    verse_starts: Mapping[tuple[int, int], int]
    surah_info: Mapping[str, tuple[int, ...]]

    def word(self, location: Location) -> str:
        index = self.verse_starts[(location.surah, location.ayah)] + location.word - 1
        return self.texts[self.word_indices[index]]

    def locations(self, reference: str) -> tuple[Location, ...]:
        if "-" in reference:
            left, right = reference.split("-", 1)
            start = _parse_endpoint(left.strip())
            end = _parse_endpoint(right.strip())
        else:
            start = end = _parse_endpoint(reference)

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
