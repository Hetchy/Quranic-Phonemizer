"""`(ref, boundaries, variant)` resolved, built and performed: one call.

Arbitrary stops, sakt and cross-verse joins all take this one path -- there
is no second, request-shaped entry into `canon.build` or `engine.run`.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from ..model.address import (
    BoundaryPlan,
    KhilafId,
    Location,
    Script,
    VariantSelection,
)
from ..model.canon import Score
from ..model.inscription import Inscription
from ..model.performance import Performance
from .boundaries import resolve_boundaries
from .request import resolve_words
from .span import assemble as assemble_span


@dataclass(frozen=True, slots=True)
class Session:
    """One request, resolved: every word it addresses, its Score and
    Inscription, the boundary plan that read it, and what performing it
    produced."""

    locations: tuple[Location, ...]
    score: Score
    inscription: Inscription
    boundaries: BoundaryPlan
    performance: Performance
    letter_khilaf_sites: dict[Location, KhilafId] = field(default_factory=dict)
    """Where the reading's authored data sites a per-location letter khilaf,
    for a projection to tag; empty when a caller resolves without one."""
    verse_ends: frozenset[str] | None = None
    """Actual corpus verse-final words touched by this request."""
    public_refs: tuple[str, ...] = ()
    """The selected script's address for each internal score word."""


def phonemize_request(
    recitation,
    ref: str,
    *,
    script: Script = Script.UTHMANI,
    stop_signs: Sequence[str] = (),
    stop_refs: Sequence[str] = (),
    selection: VariantSelection = VariantSelection(),
) -> Session:
    """A started-on word is simply the first one `locations` names: there is
    no separate `starts` input for `resolve_boundaries` to read."""
    locations = resolve_words(recitation.corpus, recitation.ledger, ref)
    built = assemble_span(
        recitation, locations, script=script, selection=selection
    )
    resolved_stop_refs = tuple(
        str(location)
        for stop_ref in stop_refs
        for location in recitation.corpus.locations(stop_ref)
    )
    boundaries = resolve_boundaries(
        built.inscription.advice,
        locations,
        built.score,
        stop_signs=stop_signs,
        stop_refs=resolved_stop_refs,
    )
    performance = recitation.perform(
        built.score, boundaries, selection=selection
    )
    return Session(
        locations, built.score, built.inscription, boundaries, performance,
        letter_khilaf_sites={
            site.location: site.khilaf
            for site in recitation.khilaf.canonical.letters
        },
        verse_ends=frozenset(
            recitation.corpus.public_ref(location)
            for location in recitation.corpus.verse_ends(locations)
        ),
        public_refs=tuple(
            recitation.corpus.public_ref(location) for location in locations
        ),
    )
