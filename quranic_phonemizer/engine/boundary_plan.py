"""Build a `BoundaryPlan` from a stop request.

Operates on per-word advice already extracted from the writing, not on a
`Score` -- phoneme identity across scripts is compared per boundary plan.
"""
from __future__ import annotations

from collections.abc import Collection, Sequence

from ..model.address import BoundaryPlan, Junction, Location
from ..model.canon import Score
from ..model.inscription import StopAdvice


class UnknownStopError(ValueError):
    """An unknown stop reference raises rather than silently doing nothing."""


def plan_from_request(
    advice: Sequence[StopAdvice | None],
    locations: Sequence[Location],
    stop_signs: Sequence[str] = (),
    stop_refs: Sequence[str] = (),
    *,
    score: Score | None = None,
    verse_ends: Collection[Location] = (),
) -> BoundaryPlan:
    """`locations` is `advice` and `score.words` in the same order, so a
    caller's stop-sign class and a caller's word ref both index it."""
    requested, stop_at_verse = _parse_stop_signs(stop_signs)
    at_refs = frozenset(stop_refs)

    sakt = _sakt_flags(score, len(advice))
    junctions = []
    for index, word_advice in enumerate(advice):
        last = index == len(advice) - 1
        asked = (
            (stop_at_verse and locations[index] in verse_ends)
            or (word_advice is not None and word_advice in requested)
            or str(locations[index]) in at_refs
        )
        if last:
            junctions.append(Junction.EDGE)
        elif asked:
            junctions.append(Junction.STOP)
        elif sakt[index]:
            # `sakt_after` forces SAKT even with no stop requested; never JOIN.
            junctions.append(Junction.SAKT)
        else:
            junctions.append(Junction.JOIN)
    return BoundaryPlan(tuple(junctions))


def _parse_stop_signs(
    stop_signs: Sequence[str],
) -> tuple[set[StopAdvice], bool]:
    requested: set[StopAdvice] = set()
    unknown: list[str] = []
    stop_at_verse = False
    for sign in stop_signs:
        if sign == "verse":
            stop_at_verse = True
            continue
        try:
            requested.add(StopAdvice(sign))
        except ValueError:
            unknown.append(sign)
    if unknown:
        raise UnknownStopError(
            f"unknown stop sign {sorted(unknown)}; expected some of "
            f"{['verse', *(m.value for m in StopAdvice)]}"
        )
    return requested, stop_at_verse


def all_join(word_count: int) -> BoundaryPlan:
    if word_count <= 0:
        return BoundaryPlan(())
    return BoundaryPlan((Junction.JOIN,) * (word_count - 1) + (Junction.EDGE,))


def _sakt_flags(score: Score | None, count: int) -> list[bool]:
    if score is None:
        return [False] * count
    flags = [word.sakt_after for word in score.words]
    return flags + [False] * (count - len(flags))
