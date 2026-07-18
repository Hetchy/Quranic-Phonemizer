from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from .dataio import load_yaml, require_keys
from .model import (
    Consonant,
    Letter,
    Nasal,
    Release,
    Segment,
    Vowel,
    VowelQuality,
)


@dataclass(frozen=True, slots=True)
class RenderConfig:
    consonants: Mapping[Letter, str]
    emphatic: Mapping[Letter, str]
    nasalized: Mapping[Letter, str]
    vowels: Mapping[VowelQuality, str]
    nasal: str
    nasal_emphatic: str
    qalqala: str


def _letter_map(values: dict[str, str]) -> Mapping[Letter, str]:
    return MappingProxyType(
        {Letter(letter): symbol for letter, symbol in values.items()}
    )


def _vowel_map(values: dict[str, str]) -> Mapping[VowelQuality, str]:
    return MappingProxyType(
        {VowelQuality(quality): symbol for quality, symbol in values.items()}
    )


def load_render_config(path: Path) -> RenderConfig:
    data = load_yaml(path)
    require_keys(
        data,
        {
            "schema_version",
            "consonants",
            "emphatic",
            "nasalized",
            "vowels",
            "nasal",
            "nasal_emphatic",
            "qalqala",
        },
        name="render data",
    )
    if data.get("schema_version") != 1:
        raise ValueError(f"Unsupported render schema: {path}")
    return RenderConfig(
        consonants=_letter_map(data["consonants"]),
        emphatic=_letter_map(data["emphatic"]),
        nasalized=_letter_map(data["nasalized"]),
        vowels=_vowel_map(data["vowels"]),
        nasal=data["nasal"],
        nasal_emphatic=data["nasal_emphatic"],
        qalqala=data["qalqala"],
    )


def render_segment(segment: Segment, config: RenderConfig) -> str:
    if isinstance(segment, Consonant):
        if segment.nasalized:
            return config.nasalized[segment.letter]
        symbol = (
            config.emphatic.get(segment.letter, config.consonants[segment.letter])
            if segment.emphatic
            else config.consonants[segment.letter]
        )
        return symbol + symbol if segment.geminated else symbol
    if isinstance(segment, Vowel):
        symbol = config.vowels[segment.quality]
        if segment.emphatic:
            symbol += "ˤ"
        if segment.long:
            symbol += ":"
        return symbol
    if isinstance(segment, Nasal):
        return config.nasal_emphatic if segment.emphatic else config.nasal
    if segment is Release.QALQALA:
        return config.qalqala
    raise TypeError(f"Unsupported segment: {segment!r}")


def render_segments(
    segments: Iterable[Segment], config: RenderConfig
) -> tuple[str, ...]:
    return tuple(render_segment(segment, config) for segment in segments)
