"""The performance-tier facts a projection reads, cached off a `Session`.

Derived from the Score and the Performance alone: the slots and their words,
the sounds in order, the occurrences, and the edges resolved to positions.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..model.address import Junction, OccurrenceId, SlotId, SoundId
from ..model.canon import Slot
from ..model.inscription import SilenceReason
from ..model.performance import (
    Aspect,
    Occurrence,
    effect_targets,
)
from ..model.performance import (
    Silent as PerformanceSilent,
)
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
    hosts: tuple[Hosted, ...]
    insertions: tuple[Insertion, ...]
    silences: tuple[Silenced, ...]
    merges: tuple[Merged, ...]
    variant_omissions: frozenset[tuple[SlotId, Aspect]]


def analyse(
    session: Session,
    alphabet: Alphabet,
    *,
    extra_phonemes: frozenset[str] = frozenset(),
    quality_fallbacks: dict | None = None,
) -> AnalysisFacts:
    score = session.score
    slots = score.slots()
    performance = session.performance

    order = sounds_in_order(performance)
    sound_index = {sound: i for i, sound in enumerate(order)}
    hidden = frozenset(
        occurrence.id for occurrence in performance.occurrences
        if occurrence.rule is SilenceReason.VARIANT
    )
    occurrences = tuple(
        occurrence for occurrence in performance.occurrences
        if occurrence.id not in hidden
    )
    occurrence_index = {
        occurrence.id: i for i, occurrence in enumerate(occurrences)
    }
    edges = attributions(performance, sound_index, occurrence_index)
    by_type: dict[type, list] = {Hosted: [], Insertion: [], Silenced: [], Merged: []}
    for edge in edges:
        by_type[type(edge)].append(edge)
    return AnalysisFacts(
        slots=slots,
        slot_index={slot.id: i for i, slot in enumerate(slots)},
        word_of_slot=tuple(
            word for word, score_word in enumerate(score.words)
            for _ in score_word.slots
        ),
        sounds=sound_facts(
            performance, order, alphabet, extra_phonemes, quality_fallbacks
        ),
        sound_index=sound_index,
        occurrences=occurrences,
        occurrence_index=occurrence_index,
        effect_targets={
            occurrence: targets
            for occurrence, targets in effect_targets(performance).items()
            if occurrence not in hidden
        },
        attributions=edges,
        modifiers=modifiers(performance, sound_index, occurrence_index),
        junctions=session.boundaries.junctions,
        alphabet=alphabet,
        hosts=tuple(by_type[Hosted]),
        insertions=tuple(by_type[Insertion]),
        silences=tuple(by_type[Silenced]),
        merges=tuple(by_type[Merged]),
        variant_omissions=frozenset(
            (edge.slots[0], edge.aspect)
            for edge in performance.attributions
            if isinstance(edge, PerformanceSilent)
            and edge.by in hidden
        ),
    )


__all__ = ["AnalysisFacts", "analyse"]
