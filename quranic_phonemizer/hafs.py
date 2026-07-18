from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .dataio import load_yaml, require_keys
from .model import (
    Consonant,
    Letter,
    Location,
    OrthographicHint,
    SourceMark,
    Vowel,
    VowelQuality,
)
from .rules.context import RuleContext, WordState


@dataclass(frozen=True, slots=True)
class HafsExceptions:
    second_hamza: frozenset[Location]
    stopped_small_ya: frozenset[Location]
    shortened_raa: frozenset[Location]
    started_ituuni: frozenset[Location]


def load_exceptions(path: Path) -> HafsExceptions:
    data = load_yaml(path)
    require_keys(
        data,
        {
            "schema_version",
            "riwayah",
            "second_hamza",
            "stopped_small_ya",
            "shortened_raa",
            "started_ituuni",
        },
        name="Hafs exceptions",
    )
    if data.get("schema_version") != 1 or data.get("riwayah") != "hafs":
        raise ValueError(f"Unsupported Hafs exceptions schema: {path}")
    return HafsExceptions(
        second_hamza=_locations(data["second_hamza"]),
        stopped_small_ya=_locations(data["stopped_small_ya"]),
        shortened_raa=_locations(data["shortened_raa"]),
        started_ituuni=_locations(data["started_ituuni"]),
    )


def apply_exceptions(context: RuleContext, config: HafsExceptions) -> None:
    for word in context.words:
        if word.expanded:
            continue
        location = word.source.location
        if location in config.second_hamza:
            _replace(
                word, Letter.HAMZA, [Consonant(Letter.HAMZA), Vowel(VowelQuality.A)]
            )
            _replace_marked(
                word,
                SourceMark.SECOND_HAMZA,
                [Consonant(Letter.HAMZA), Vowel(VowelQuality.A)],
            )
        if location in config.stopped_small_ya and word.stopping:
            _replace(word, Letter.NOON, [Consonant(Letter.NOON)])
            _replace_hinted(word, OrthographicHint.SMALL_YA_LETTER, [])
        if location in config.shortened_raa:
            _replace(
                word,
                Letter.RA,
                [
                    Consonant(Letter.RA, emphatic=True),
                    Vowel(VowelQuality.A, emphatic=True),
                ],
            )
        if location in config.started_ituuni and word.starting:
            _replace(word, Letter.HAMZA_WASL, [Consonant(Letter.HAMZA_WASL)])
            _replace(word, Letter.HAMZA, [Vowel(VowelQuality.I_VOWEL, long=True)])


def _replace(word: WordState, source: Letter, segments: list) -> None:
    for letter in word.letters:
        if letter.form.letter is source:
            letter.segments = list(segments)
            letter.resolved = True
            return


def _replace_marked(word: WordState, mark: SourceMark, segments: list) -> None:
    for letter in word.letters:
        if letter.form.has_mark(mark):
            letter.segments = list(segments)
            letter.resolved = True
            return


def _replace_hinted(word: WordState, hint: OrthographicHint, segments: list) -> None:
    for letter in word.letters:
        if hint in letter.form.hints:
            letter.segments = list(segments)
            letter.resolved = True
            return


def _locations(values: list[list[int]]) -> frozenset[Location]:
    return frozenset(Location(*value) for value in values)
