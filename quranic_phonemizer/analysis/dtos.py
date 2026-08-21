"""The core public records: the six DTOs and the bundle that carries them.

Plain frozen records over the result-local id spaces. Nothing here reaches the
result object; laws and the builder read these, not the other way round.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..model.inscription import StopAdvice
from .ids import BoundaryId, MergerId, OccurrenceId, RuleId, SoundId, WordId


class BoundaryState(StrEnum):
    """What a junction resolves to. `stop` before an internal boundary already
    implies a start after it, so no separate start flag is needed."""

    START = "start"
    JOIN = "join"
    SAKT = "sakt"
    STOP = "stop"


@dataclass(frozen=True, slots=True)
class Word:
    id: WordId
    ref: str
    text: str
    before_boundary_id: BoundaryId
    after_boundary_id: BoundaryId
    sound_ids: tuple[SoundId, ...]


@dataclass(frozen=True, slots=True)
class Boundary:
    id: BoundaryId
    before: WordId | None
    after: WordId | None
    state: BoundaryState
    stop_sign: str | None
    stop_advice: StopAdvice | None


@dataclass(frozen=True, slots=True)
class Sound:
    id: SoundId
    order: int
    token: str
    word_id: WordId
    rule_occurrence_ids: tuple[OccurrenceId, ...]


@dataclass(frozen=True, slots=True)
class RuleDefinition:
    id: RuleId
    name: str
    arabic_name: str
    summary: str


@dataclass(frozen=True, slots=True)
class RuleOccurrence:
    id: OccurrenceId
    rule_id: RuleId
    word_ids: tuple[WordId, ...]
    boundary_ids: tuple[BoundaryId, ...]
    sound_ids: tuple[SoundId, ...]


@dataclass(frozen=True, slots=True)
class Merger:
    id: MergerId
    boundary_id: BoundaryId
    before_word_id: WordId
    after_word_id: WordId
    sound_id: SoundId
    rule_occurrence_ids: tuple[OccurrenceId, ...]


@dataclass(frozen=True, slots=True)
class AnalysisBundle:
    """Everything a result is, before it exposes any of it. The builder fills
    it and the laws validate it; the result only reads it."""

    ref: str
    riwayah: str
    script: str
    variant: dict
    extra_phonemes: frozenset[str]
    schema_version: int
    canon_digest: str

    source_text: str
    tokens: tuple[str, ...]

    words: tuple[Word, ...]
    boundaries: tuple[Boundary, ...]
    sounds: tuple[Sound, ...]
    rule_occurrences: tuple[RuleOccurrence, ...]
    mergers: tuple[Merger, ...]


__all__ = [
    "AnalysisBundle",
    "Boundary",
    "BoundaryState",
    "Merger",
    "RuleDefinition",
    "RuleOccurrence",
    "Sound",
    "Word",
]
