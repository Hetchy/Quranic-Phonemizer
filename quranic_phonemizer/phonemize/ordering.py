"""Orders performed sounds into recitation sequence.

Sorted by `(slot ordinal, aspect)`, with an inserted sound placed by its
anchor and side; a view over the attribution edges, not a computation.
"""
from __future__ import annotations

from ..model.performance import Aspect, Hosts, Inserted, Performance, Release, Side, SoundId

_ASPECT_ORDER = {Aspect.CONSONANT: 0, Aspect.VOWEL: 1}


def _hosts_key(slots, aspect, sound: SoundId, by_id) -> tuple[int, int, int]:
    """A release shares its slot and aspect with the consonant it echoes, so
    it needs its own nudge to sort after it rather than colliding on the
    same key and falling back to attribution order."""
    nudge = 1 if isinstance(by_id[sound], Release) else 0
    return (slots[0].ordinal, _ASPECT_ORDER[aspect], nudge)


def sounds_in_order(performance: Performance) -> tuple[SoundId, ...]:
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


__all__ = ["sounds_in_order"]
