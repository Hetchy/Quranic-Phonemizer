"""The public `stop_signs`/`stop_refs` pair, resolved against one reading.

`engine.boundary_plan.plan_from_request` already does the matching; this is
the one call site that hands it the assembled request's own words.
"""
from __future__ import annotations

from collections.abc import Collection, Sequence

from ..engine.boundary_plan import plan_from_request
from ..model.address import BoundaryPlan, Location
from ..model.canon import Score
from ..model.inscription import StopAdvice


def resolve_boundaries(
    advice: Sequence[StopAdvice | None],
    locations: Sequence[Location],
    score: Score,
    *,
    stop_signs: Sequence[str] = (),
    stop_refs: Sequence[str] = (),
    verse_ends: Collection[Location] = (),
) -> BoundaryPlan:
    return plan_from_request(
        advice, locations, stop_signs, stop_refs,
        score=score, verse_ends=verse_ends,
    )
