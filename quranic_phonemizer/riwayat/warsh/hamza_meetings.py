"""Reviewed source projection and register for Warsh adjacent qata hamzas."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path

from ...canon.draft import _Draft
from ...canon.passes import word_spans
from ...canon.draft import nucleus_fact
from ...dataio import require_keys
from ...model.address import Location
from ...model.canon import Annotation, CanonLetter, Nucleus, Onset, Quality, SlotOrigin
from ...model.inscription import SlotFact


_REGISTER = Path(__file__).resolve().parents[2] / "data/riwayat/warsh/hamza_meetings.json"


@dataclass(frozen=True, slots=True)
class MeetingRow:
    source: str
    canonical: Location
    first: Quality
    second: Quality
    scope: str
    owner: str
    exception: str | None
    previous: Location | None = None


def _location(ref: str) -> Location:
    try:
        return Location(*(int(part) for part in ref.split(":")))
    except (AttributeError, TypeError, ValueError):
        raise ValueError(f"{_REGISTER}: invalid location {ref!r}") from None


@lru_cache(maxsize=1)
def meeting_rows() -> tuple[MeetingRow, ...]:
    raw = json.loads(_REGISTER.read_text(encoding="utf-8"))
    require_keys(raw, {"schema_version", "rows"}, name=str(_REGISTER))
    if raw["schema_version"] != 1:
        raise ValueError(f"{_REGISTER}: unsupported schema {raw['schema_version']!r}")
    rows = []
    for item in raw["rows"]:
        require_keys(
            item,
            {"source", "canonical", "first", "second", "scope", "owner", "exception"},
            name=str(_REGISTER), optional={"previous"},
        )
        rows.append(MeetingRow(
            source=str(item["source"]),
            canonical=_location(item["canonical"]),
            previous=_location(item["previous"]) if item.get("previous") else None,
            first=Quality[item["first"]], second=Quality[item["second"]],
            scope=str(item["scope"]), owner=str(item["owner"]),
            exception=item["exception"],
        ))
    return tuple(rows)


@lru_cache(maxsize=1)
def rows_by_target() -> dict[Location, MeetingRow]:
    return {row.canonical: row for row in meeting_rows()}


def _source_offset(reading, draft) -> int:
    return reading.clusters[draft.cluster].offset


def _split_collapsed(reading, drafts, scribe, first, quality: Quality):
    length_offsets = scribe.evidence_offsets(first, SlotFact.VOWEL_LENGTH)
    first.nucleus = Nucleus.short(Quality.A)
    for offset in length_offsets:
        scribe.withdraw_evidence(offset, first, SlotFact.VOWEL_LENGTH)
    second = _Draft(
        letter=CanonLetter.HAMZA,
        onset=Onset.PLAIN,
        nucleus=Nucleus.short(quality),
        origin=SlotOrigin.WRITTEN,
        cluster=first.cluster,
        onset_declared=True,
        nucleus_declared=True,
    )
    drafts.insert(drafts.index(first) + 1, second)
    cluster = reading.clusters[first.cluster]
    collapsed = next(
        (mark.offset for mark in cluster.marks if mark.role == "collapsed_hamza"),
        None,
    )
    offset = (
        collapsed
        if collapsed is not None
        else length_offsets[0] if length_offsets else _source_offset(reading, first)
    )
    scribe.evidence(offset, second, SlotFact.LETTER)
    scribe.evidence(offset, second, nucleus_fact(second.nucleus))
    return second


def _one_word(reading, drafts, scribe, span, row: MeetingRow) -> None:
    hamzas = [draft for draft in span if draft.letter is CanonLetter.HAMZA]
    first = hamzas[0] if hamzas else span[0]
    first_index = span.index(first)
    following = span[first_index + 1] if first_index + 1 < len(span) else None
    first.letter = CanonLetter.HAMZA
    first.onset = Onset.PLAIN
    first.nucleus = Nucleus.short(row.first)
    if following is not None and following.letter is CanonLetter.HAMZA:
        second = following
    elif row.exception == "aimma" and len(span) > 1:
        second = span[1]
        second.letter = CanonLetter.HAMZA
    else:
        second = _split_collapsed(reading, drafts, scribe, first, row.second)
    second.nucleus = Nucleus.short(row.second) if row.exception != "triple" else second.nucleus.with_quality(row.second)
    if row.owner == "fixed_tashil":
        second.onset = Onset.TASHIL


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


def _cluster_offsets(reading, cluster_index: int) -> frozenset[int]:
    cluster = reading.clusters[cluster_index]
    return frozenset((cluster.offset, *(mark.offset for mark in cluster.marks)))


def _restore_right_qata(reading, drafts, scribe, right, row: MeetingRow):
    right_word = reading.words.index(row.canonical)
    if not _word_text(reading, right_word).startswith(("ا", "أ", "إ", "ء")):
        return None
    first_cluster = next(
        index for index, cluster in enumerate(reading.clusters)
        if cluster.word == right_word
    )
    second = right[0]
    if second.cluster != first_cluster:
        second = _Draft(
            letter=CanonLetter.HAMZA, onset=Onset.PLAIN,
            nucleus=Nucleus.short(row.second), origin=SlotOrigin.WRITTEN,
            cluster=first_cluster, onset_declared=True, nucleus_declared=True,
        )
        drafts.insert(drafts.index(right[0]), second)
        scribe.retarget(_cluster_offsets(reading, first_cluster), right, second)
        cluster = reading.clusters[first_cluster]
        scribe.evidence(cluster.offset, second, SlotFact.LETTER)
        for mark in cluster.marks:
            scribe.decoration(mark.offset, second)
    second.letter = CanonLetter.HAMZA
    second.onset = Onset.PLAIN
    second.nucleus = Nucleus.short(row.second)
    return second


def supply_hamza_meetings(reading, drafts, lexicon, scribe, selection) -> None:
    """Project only rows attested by the checked-in selected-source register."""
    del lexicon, selection
    if scribe is None:
        return
    spans = dict(zip(reading.words, word_spans(reading, drafts)))
    for row in meeting_rows():
        if row.canonical not in spans:
            continue
        right = spans[row.canonical]
        if not right:
            continue
        if row.scope == "one_word":
            _one_word(reading, drafts, scribe, right, row)
            continue
        second = _restore_right_qata(reading, drafts, scribe, right, row)
        if second is None:
            continue
        if row.previous not in spans:
            continue
        left = spans[row.previous]
        if not left or left[-1].letter is not CanonLetter.HAMZA:
            continue
        first = left[-1]
        first.letter = CanonLetter.HAMZA
        first.onset = Onset.PLAIN
        first.nucleus = Nucleus.short(row.first)
        if row.exception == "fused_badal":
            second.annotations |= {Annotation.BADAL}


__all__ = ["MeetingRow", "meeting_rows", "rows_by_target", "supply_hamza_meetings"]
