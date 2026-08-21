"""The performance-tier facts a projection reads, cached off a `Session`.

Derived from the Score and the Performance alone: the slots and their words,
the sounds in order, the occurrences, and the edges resolved to positions.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..model.address import Junction, OccurrenceId, SlotId, SoundId
from ..model.canon import Slot
from ..model.performance import Occurrence, effect_targets
from ..render.alphabet import Alphabet
from ..session import Session
from .attributions import (
    Attribution,
    Hosted,
    Insertion,
    Merged,
    Modifier,
    Silenced,
    attributions,
    modifiers,
)
from .sounds import SoundFact, sound_facts, sounds_in_order


@dataclass(frozen=True, slots=True)
class AnalysisFacts:
    """One resolved request's performance tier, keyed for position lookups."""

    slots: tuple[Slot, ...]
    slot_index: dict[SlotId, int]
    word_of_slot: tuple[int, ...]
    sounds: tuple[SoundFact, ...]
    sound_index: dict[SoundId, int]
    occurrences: tuple[Occurrence, ...]
    occurrence_index: dict[OccurrenceId, int]
    effect_targets: dict[OccurrenceId, tuple[SlotId, ...]]
    attributions: tuple[Attribution, ...]
    modifiers: tuple[Modifier, ...]
    junctions: tuple[Junction, ...]
    alphabet: Alphabet

    @property
    def hosts(self) -> tuple[Hosted, ...]:
        return tuple(a for a in self.attributions if isinstance(a, Hosted))

    @property
    def insertions(self) -> tuple[Insertion, ...]:
        return tuple(a for a in self.attributions if isinstance(a, Insertion))

    @property
    def silences(self) -> tuple[Silenced, ...]:
        return tuple(a for a in self.attributions if isinstance(a, Silenced))

    @property
    def merges(self) -> tuple[Merged, ...]:
        return tuple(a for a in self.attributions if isinstance(a, Merged))


def analyse(
    session: Session,
    alphabet: Alphabet,
    *,
    extra_phonemes: frozenset[str] = frozenset(),
) -> AnalysisFacts:
    score = session.score
    slots = score.slots()
    performance = session.performance

    order = sounds_in_order(performance)
    sound_index = {sound: i for i, sound in enumerate(order)}
    occurrence_index = {
        occurrence.id: i for i, occurrence in enumerate(performance.occurrences)
    }
    return AnalysisFacts(
        slots=slots,
        slot_index={slot.id: i for i, slot in enumerate(slots)},
        word_of_slot=tuple(
            word for word, score_word in enumerate(score.words)
            for _ in score_word.slots
        ),
        sounds=sound_facts(performance, order, alphabet, extra_phonemes),
        sound_index=sound_index,
        occurrences=performance.occurrences,
        occurrence_index=occurrence_index,
        effect_targets=effect_targets(performance),
        attributions=attributions(performance, sound_index, occurrence_index),
        modifiers=modifiers(performance, sound_index, occurrence_index),
        junctions=session.boundaries.junctions,
        alphabet=alphabet,
    )


__all__ = ["AnalysisFacts", "analyse"]
