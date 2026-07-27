"""Orders performed sounds into recitation sequence.

Sorted by `(slot ordinal, aspect)`, with an inserted sound placed by its
anchor and side; a view over the attribution edges, not a computation.
"""
from __future__ import annotations

from collections.abc import Sequence

from ..model.canon import Score
from ..model.performance import (
    Aspect,
    Hosts,
    Inserted,
    Performance,
    Side,
    SoundId,
)
from .alphabet import Alphabet

_ASPECT_ORDER = {Aspect.ONSET: 0, Aspect.NUCLEUS: 1}


def sounds_in_order(performance: Performance) -> tuple[SoundId, ...]:
    placed: list[tuple[tuple[int, int, int], SoundId]] = []
    for attribution in performance.attributions:
        match attribution:
            case Hosts(slots=slots, aspect=aspect, sound=sound) if slots:
                placed.append(
                    ((slots[0].ordinal, _ASPECT_ORDER[aspect], 0), sound)
                )
            case Inserted(anchor=(slot, side), aspect=aspect, sound=sound):
                nudge = -1 if side is Side.BEFORE else 1
                placed.append(
                    ((slot.ordinal, _ASPECT_ORDER[aspect], nudge), sound)
                )
    placed.sort(key=lambda entry: entry[0])
    return tuple(sound for _, sound in placed)


def phonemes(
    performance: Performance, alphabet: Alphabet
) -> tuple[str, ...]:
    by_id = dict(performance.sounds)
    return tuple(
        alphabet.token(by_id[sound]) for sound in sounds_in_order(performance)
    )


def phonemes_by_word(
    performance: Performance, score: Score, alphabet: Alphabet
) -> tuple[tuple[str, ...], ...]:
    """The same sequence, split at word boundaries.

    A sound merged across a boundary belongs to the word that hosts it: in
    `مِّن رَّبِّهِمْ` the noon's sound lands on the second word.
    """
    by_id = dict(performance.sounds)
    owner: dict[int, int] = {}
    for index, word in enumerate(score.words):
        for slot in word.slots:
            owner[slot.id.ordinal] = index

    buckets: list[list[str]] = [[] for _ in score.words]
    for attribution in performance.attributions:
        match attribution:
            case Hosts(slots=slots, aspect=aspect, sound=sound) if slots:
                key = (slots[0].ordinal, _ASPECT_ORDER[aspect], 0)
            case Inserted(anchor=(slot, side), aspect=aspect, sound=sound):
                key = (slot.ordinal, _ASPECT_ORDER[aspect],
                       -1 if side is Side.BEFORE else 1)
            case _:
                continue
        buckets[owner[key[0]]].append((key, alphabet.token(by_id[sound])))

    return tuple(
        tuple(token for _, token in sorted(bucket, key=lambda e: e[0]))
        for bucket in buckets
    )


def joined(tokens: Sequence[str], separator: str = " ") -> str:
    return separator.join(tokens)
