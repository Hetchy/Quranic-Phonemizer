"""Performed sounds in recitation order, each with its notation token.

Ordered by slot ordinal then aspect, with a release nudged past the consonant
it echoes and an inserted sound placed by its anchor side.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..model.address import SoundId
from ..model.performance import (
    Aspect,
    Hosts,
    Inserted,
    Performance,
    Release,
    Side,
    Sound,
)
from ..render.alphabet import Alphabet

_ASPECT_ORDER = {Aspect.CONSONANT: 0, Aspect.VOWEL: 1}


@dataclass(frozen=True, slots=True)
class SoundFact:
    """A performed sound: its typed model value and the token that writes it."""

    value: Sound
    token: str


def _hosts_key(slots, aspect: Aspect, sound: SoundId, by_id) -> tuple[int, int, int]:
    nudge = 1 if isinstance(by_id[sound], Release) else 0
    return (slots[0].ordinal, _ASPECT_ORDER[aspect], nudge)


def sounds_in_order(performance: Performance) -> tuple[SoundId, ...]:
    """Recitation sequence of the sound ids a slot or an anchor realizes."""
    by_id = dict(performance.sounds)
    placed: list[tuple[tuple[int, int, int], SoundId]] = []
    for attribution in performance.attributions:
        match attribution:
            case Hosts(slots=slots, aspect=aspect, sound=sound) if slots:
                placed.append((_hosts_key(slots, aspect, sound, by_id), sound))
            case Inserted(anchor=(slot, side), aspect=aspect, sound=sound):
                nudge = -1 if side is Side.BEFORE else 1
                placed.append(
                    ((slot.ordinal, _ASPECT_ORDER[aspect], nudge), sound)
                )
    placed.sort(key=lambda entry: entry[0])
    return tuple(sound for _, sound in placed)


def sound_facts(
    performance: Performance,
    order: tuple[SoundId, ...],
    alphabet: Alphabet,
    extra_phonemes: frozenset[str],
) -> tuple[SoundFact, ...]:
    """The ordered sound ids resolved to their typed values and tokens."""
    by_id = dict(performance.sounds)
    return tuple(
        SoundFact(
            by_id[sound],
            alphabet.token(by_id[sound], extra_phonemes=extra_phonemes),
        )
        for sound in order
    )


__all__ = ["SoundFact", "sound_facts", "sounds_in_order"]
