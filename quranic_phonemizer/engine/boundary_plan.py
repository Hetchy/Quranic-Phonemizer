"""Build a `BoundaryPlan` from a stop request.

Operates on per-word advice already extracted from the writing, not on a
`Score` -- phoneme identity across scripts is compared per boundary plan.
"""
from __future__ import annotations

from collections.abc import Sequence

from ..model.address import BoundaryPlan, Junction
from ..model.canon import Score
from ..model.inscription import StopAdvice


class UnknownStopError(ValueError):
    """An unknown stop reference raises rather than silently doing nothing."""


def plan_from_request(
    advice: Sequence[StopAdvice | None],
    stop_at: Sequence[StopAdvice] = (),
    *,
    score: Score | None = None,
) -> BoundaryPlan:
    requested = set(stop_at)
    unknown = requested - set(StopAdvice)
    if unknown:
        raise UnknownStopError(
            f"unknown stop advice {sorted(unknown)}; expected some of "
            f"{[m.value for m in StopAdvice]}"
        )

    sakt = _sakt_flags(score, len(advice))
    junctions = []
    for index, word_advice in enumerate(advice):
        last = index == len(advice) - 1
        if last:
            junctions.append(Junction.EDGE)
        elif word_advice is not None and word_advice in requested:
            junctions.append(Junction.STOP)
        elif sakt[index]:
            # `sakt_after` forces SAKT even with no stop requested; never JOIN.
            junctions.append(Junction.SAKT)
        else:
            junctions.append(Junction.JOIN)
    return BoundaryPlan(tuple(junctions))


def all_join(word_count: int) -> BoundaryPlan:
    if word_count <= 0:
        return BoundaryPlan(())
    return BoundaryPlan((Junction.JOIN,) * (word_count - 1) + (Junction.EDGE,))


def _sakt_flags(score: Score | None, count: int) -> list[bool]:
    if score is None:
        return [False] * count
    flags = [word.sakt_after for word in score.words]
    return flags + [False] * (count - len(flags))
