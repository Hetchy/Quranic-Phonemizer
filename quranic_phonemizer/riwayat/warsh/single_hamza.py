"""Selected-script supplies for Warsh single-hamza replacement sites."""

from __future__ import annotations

import unicodedata
from functools import lru_cache
from pathlib import Path

from ...canon.passes import word_spans
from ...dataio import load_yaml, require_keys
from ...model.address import Location
from ...model.canon import (
    Annotation,
    CanonLetter,
    Quality,
)


_REGISTER = (
    Path(__file__).resolve().parents[2]
    / "data" / "riwayat" / "warsh" / "single_hamza.yaml"
)

_IGNORED = frozenset("ـۥۦۧۨ")


def _location(ref) -> Location:
    try:
        surah, ayah, word = (int(part) for part in ref.split(":"))
    except (AttributeError, TypeError, ValueError):
        raise ValueError(f"{_REGISTER}: invalid canonical ref {ref!r}") from None
    return Location(surah, ayah, word)


@lru_cache(maxsize=1)
def _raw_register() -> dict:
    raw = load_yaml(_REGISTER)
    require_keys(
        raw,
        {
            "schema_version",
            "fixed_counts",
            "tahqiq_exclusions",
            "canonical_absence",
            "supplied",
        },
        name=str(_REGISTER),
    )
    if raw["schema_version"] != 1:
        raise ValueError(
            f"{_REGISTER}: schema_version {raw['schema_version']!r}, expected 1"
        )
    return raw


@lru_cache(maxsize=1)
def supplied_ibdal() -> dict[Location, int]:
    """The reviewed regular sites and their selected-script host slots."""
    return {
        _location(ref): int(index)
        for ref, index in _raw_register()["supplied"].items()
    }


@lru_cache(maxsize=None)
def authored_locations(name: str) -> frozenset[Location]:
    """One closed fixed lexical register consumed by this owner."""
    raw = _raw_register()
    values = raw.get(name)
    if not isinstance(values, list):
        raise ValueError(f"{_REGISTER}: unknown location register {name!r}")
    return frozenset(_location(ref) for ref in values)


@lru_cache(maxsize=1)
def canonical_absence() -> dict[Location, str]:
    return {
        _location(ref): text
        for ref, text in _raw_register()["canonical_absence"].items()
    }


@lru_cache(maxsize=1)
def fixed_ibdal_counts() -> dict[str, int]:
    return {
        name: int(count)
        for name, count in _raw_register()["fixed_counts"].items()
    }


def _skeleton(text: str) -> str:
    return "".join(
        char for char in text
        if not unicodedata.combining(char) and char not in _IGNORED
    )


def fixed_ibdal_family(text: str) -> str | None:
    """The reviewed fixed family written by one selected-source token."""
    skeleton = _skeleton(text)
    if skeleton == "وبير":
        return "bir"
    if "بيس" in skeleton:
        return "bis"
    if skeleton == "الذيب":
        return "dhib"
    if skeleton == "سال":
        return "saal"
    if skeleton == "النسي":
        return "nasi"
    if skeleton == "ليلا" and "۬" in text:
        return "liila"
    if skeleton == "لاهب":
        return "lahab"
    if skeleton == "منساته":
        return "minsa"
    if skeleton in {"ياجوج", "وماجوج"}:
        return "yajuj"
    return None


def _word_text(reading, word: int) -> str:
    offsets = {
        cluster.offset for cluster in reading.clusters if cluster.word == word
    }
    offsets.update(
        mark.offset
        for cluster in reading.clusters if cluster.word == word
        for mark in cluster.marks
    )
    by_offset = {glyph.id.offset: glyph.char for glyph in reading.graphemes}
    return "".join(by_offset[offset] for offset in sorted(offsets))


def _fixed_target(family: str, span):
    if family == "nasi":
        return next(
            draft for draft in reversed(span)
            if draft.letter is CanonLetter.YA
        )
    if family in {"liila", "lahab"}:
        target = next(
            draft for draft in span
            if draft.nucleus.quality is Quality.A
            and draft.letter in {CanonLetter.YA, CanonLetter.HAMZA}
        )
        target.letter = CanonLetter.YA
        return target
    return next(draft for draft in span if draft.nucleus.is_long)


def supply_single_hamza(reading, drafts, lexicon, scribe, selection) -> None:
    """Annotate the reviewed replacement slot written by the selected text."""
    del lexicon, scribe, selection
    for word, (location, span) in enumerate(
        zip(reading.words, word_spans(reading, drafts))
    ):
        text = _word_text(reading, word)
        family = fixed_ibdal_family(text)
        if family is not None:
            _fixed_target(family, span).annotations |= {Annotation.IBDAL}
            continue
        index = supplied_ibdal().get(location)
        if index is not None:
            span[index].annotations |= {Annotation.IBDAL}
            if "وَ۬ا" in text:
                span[index].annotations |= {Annotation.BADAL}


__all__ = [
    "authored_locations",
    "canonical_absence",
    "fixed_ibdal_family",
    "fixed_ibdal_counts",
    "supplied_ibdal",
    "supply_single_hamza",
]
