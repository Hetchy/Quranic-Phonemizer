"""The public `stop_signs`/`stop_refs` pair, resolved against one reading.

`engine.boundary_plan.plan_from_request` already does the matching; this is
the one call site that hands it the assembled request's own words.
"""
from __future__ import annotations

from collections.abc import Collection, Sequence

from ..engine.boundary_plan import plan_from_request
from ..model.address import BoundaryPlan, Junction, Location, VariantSelection
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


def mask_stopped_sakt_variants(
    khilaf,
    locations: Sequence[Location],
    boundaries: BoundaryPlan,
    selection: VariantSelection,
) -> VariantSelection:
    """A sakt dispute exists only at a continuing junction.

    A caller may select an idraj/idgham face and subsequently stop at that
    boundary.  In that state the dispute is inapplicable, so the canonical
    build must revert to the ordinary, unselected reading as well as the
    performance rules being blocked by the stop.
    """
    sakt_ids = {site.khilaf for site in khilaf.canonical.sakt}
    index = {location: at for at, location in enumerate(locations)}
    masked = set()
    for option in selection.options:
        sites = (
            site for site in khilaf.canonical.sakt
            if site.khilaf == option.khilaf and site.location in index
        )
        states = tuple(boundaries.after(index[site.location]) for site in sites)
        if (
            option.khilaf in sakt_ids
            and states
            and not any(state in {Junction.JOIN, Junction.SAKT} for state in states)
        ):
            masked.add(option.khilaf)
    return VariantSelection(tuple(
        option for option in selection.options if option.khilaf not in masked
    ))


__all__ = ["mask_stopped_sakt_variants", "resolve_boundaries"]
