"""Performed sounds in recitation order, each with its notation token.

Ordered by slot ordinal then aspect, with a release nudged past the consonant
it echoes and an inserted sound placed by its anchor side.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..model.address import SoundId
from ..model.performance import Performance, Sound, sounds_in_order
from ..render.alphabet import Alphabet


@dataclass(frozen=True, slots=True)
class SoundFact:
    """A performed sound: its typed model value and the token that writes it."""

    value: Sound
    token: str


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
