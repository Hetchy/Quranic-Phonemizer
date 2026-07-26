"""Turning a stop request into a `BoundaryPlan`.

Advice lives in the Inscription layer, so this takes an `Inscription` and not a
`Score` (ADR-003 §5). Two scripts yield two plans from one request; that is
correct and stated, and it is why phoneme identity across scripts holds per
*boundary plan* rather than per call.
"""
from __future__ import annotations

from collections.abc import Sequence

from ..model.address import BoundaryPlan, Junction
from ..model.canon import Score
from ..model.inscription import StopAdvice


class UnknownStopError(ValueError):
    """An unknown stop reference raises rather than silently doing nothing."""


ALL_JOIN = "all_join"
"""The traversal the attestation law is evaluated under: a mushaf writes the
connected reading, so a witness is checked against it (ADR-003 §4.1)."""


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
            # `ScoreWord.sakt_after` forces SAKT unless the plan selects STOP.
            # It may never be JOIN — which makes 75:27 a domain fact rather
            # than a glyph shortcut.
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
