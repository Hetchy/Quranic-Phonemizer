"""HighlightGroup: source units co-highlighted by the sounds they share.

Native ids in place of concatenated characters; a consumer maps a timed sound
to the group that holds it and lights the group's text ranges.
"""
from __future__ import annotations

from dataclasses import dataclass

from .ids import HighlightId, LetterUnitId, SoundId


@dataclass(frozen=True, slots=True)
class HighlightGroup:
    """One group: the units highlighted together, their ordered half-open
    scalar ranges in the source text, and the sounds that activate them."""

    id: HighlightId
    unit_ids: tuple[LetterUnitId, ...]
    ranges: tuple[tuple[int, int], ...]
    sound_ids: tuple[SoundId, ...]


__all__ = ["HighlightGroup"]
