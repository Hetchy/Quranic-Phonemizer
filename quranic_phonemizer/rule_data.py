from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from .dataio import load_yaml, require_keys
from .model import Letter


@dataclass(frozen=True, slots=True)
class RuleConfig:
    inherent_emphasis: frozenset[Letter]
    qalqala: frozenset[Letter]
    noon_ikhfaa: frozenset[Letter]
    noon_iqlab: frozenset[Letter]
    noon_idgham_ghunnah: frozenset[Letter]
    noon_idgham_plain: frozenset[Letter]
    meem_ikhfaa: frozenset[Letter]
    meem_idgham: frozenset[Letter]
    partial_assimilation: Mapping[Letter, frozenset[Letter]]
    hamza_wasl_kasra_nouns: tuple[tuple[Letter, ...], ...]
    hamza_wasl_kasra_verbs: tuple[tuple[Letter, ...], ...]
    allah_words: frozenset[tuple[Letter, ...]]


def _letters(value: list[str]) -> frozenset[Letter]:
    letters = frozenset(Letter(char) for char in value)
    if len(letters) != len(value):
        raise ValueError(f"Duplicate letter in list: {value}")
    return letters


def _pairs(values: dict[str, list[str]]) -> Mapping[Letter, frozenset[Letter]]:
    return MappingProxyType(
        {Letter(source): _letters(targets) for source, targets in values.items()}
    )


def _patterns(values: list[str]) -> tuple[tuple[Letter, ...], ...]:
    return tuple(tuple(Letter(char) for char in value) for value in values)


def _require_disjoint(name: str, groups: tuple[frozenset[Letter], ...]) -> None:
    combined = set()
    for group in groups:
        overlap = combined.intersection(group)
        if overlap:
            glyphs = "".join(sorted(letter.value for letter in overlap))
            raise ValueError(f"{name} groups overlap at {glyphs}")
        combined.update(group)


def load_rule_config(path: Path) -> RuleConfig:
    data = load_yaml(path)
    require_keys(
        data,
        {
            "schema_version",
            "inherent_emphasis",
            "qalqala",
            "noon_tanween",
            "meem_sakinah",
            "idgham",
            "hamza_wasl",
            "allah_words",
        },
        name="Tajweed data",
    )
    if data.get("schema_version") != 1:
        raise ValueError(f"Unsupported Tajweed schema: {path}")

    noon = data["noon_tanween"]
    require_keys(
        noon,
        {
            "izhar_halqi",
            "ikhfaa_haqiqi",
            "iqlab",
            "idgham_bi_ghunnah",
            "idgham_bila_ghunnah",
        },
        name="noon_tanween",
    )
    noon_groups = (
        _letters(noon["izhar_halqi"]),
        _letters(noon["ikhfaa_haqiqi"]),
        _letters(noon["iqlab"]),
        _letters(noon["idgham_bi_ghunnah"]),
        _letters(noon["idgham_bila_ghunnah"]),
    )
    _require_disjoint("noon_tanween", noon_groups)

    meem = data["meem_sakinah"]
    require_keys(
        meem,
        {"ikhfaa_shafawi", "idgham_shafawi"},
        name="meem_sakinah",
    )
    meem_groups = (
        _letters(meem["ikhfaa_shafawi"]),
        _letters(meem["idgham_shafawi"]),
    )
    _require_disjoint("meem_sakinah", meem_groups)

    idgham = data["idgham"]
    hamza_wasl = data["hamza_wasl"]
    require_keys(
        idgham,
        {"partial_assimilation"},
        name="idgham",
    )
    require_keys(
        hamza_wasl,
        {"kasra_nouns", "kasra_verbs"},
        name="hamza_wasl",
    )
    return RuleConfig(
        inherent_emphasis=_letters(data["inherent_emphasis"]),
        qalqala=_letters(data["qalqala"]),
        noon_ikhfaa=noon_groups[1],
        noon_iqlab=noon_groups[2],
        noon_idgham_ghunnah=noon_groups[3],
        noon_idgham_plain=noon_groups[4],
        meem_ikhfaa=meem_groups[0],
        meem_idgham=meem_groups[1],
        partial_assimilation=_pairs(idgham["partial_assimilation"]),
        hamza_wasl_kasra_nouns=_patterns(hamza_wasl["kasra_nouns"]),
        hamza_wasl_kasra_verbs=_patterns(hamza_wasl["kasra_verbs"]),
        allah_words=frozenset(_patterns(data["allah_words"])),
    )
