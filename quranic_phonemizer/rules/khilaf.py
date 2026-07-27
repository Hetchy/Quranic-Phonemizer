"""Reading a named point of legitimate disagreement off the Score."""
from __future__ import annotations

from dataclasses import dataclass, field

from ..model.address import KhilafId, VariantSelection
from ..model.performance import NasalPlace

#: Both readings of the two bilabial hidings are taught and both are correct.
#: A hidden meem before the baa is the phonetic description; the generic nasal
#: is what a reciter who does not close the lips produces.
NASAL_PLACES = {
    "bilabial": NasalPlace.BILABIAL,
    "assimilated": NasalPlace.ASSIMILATED,
}
DEFAULT_NASAL_PLACE = NasalPlace.ASSIMILATED

#: The two readings of a disputed raa, as a reader names them.
HEAVY = {"heavy": True, "light": False}


class KhilafError(ValueError):
    """An option name no rule can act on."""


def nasal_place(selection: VariantSelection, khilaf: KhilafId) -> NasalPlace:
    name = selection.chosen(khilaf)
    if name is None:
        return DEFAULT_NASAL_PLACE
    place = NASAL_PLACES.get(name)
    if place is None:
        raise KhilafError(
            f"{khilaf.value}: {name!r} is not an option; expected one of "
            f"{sorted(NASAL_PLACES)}"
        )
    return place


@dataclass(frozen=True, slots=True)
class Site:
    """One word of a khilaf that recurs word by word."""

    at_stop: bool
    """The junction the dispute lives in; in the other one the reading is
    settled and the ordinary rule gives it."""

    default_heavy: bool


@dataclass(frozen=True, slots=True)
class RaaKhilaf:
    """The words whose quiescent raa is read both ways, and which way."""

    sites: dict[str, Site] = field(default_factory=dict)

    def weight(
        self, skeleton: str, stopped: bool, selection: VariantSelection
    ) -> bool | None:
        """`None` where this is no disputed site in this junction, which
        leaves the answer to the rule that decides every other raa."""
        site = self.sites.get(skeleton)
        if site is None or site.at_stop is not stopped:
            return None
        name = selection.chosen(KhilafId.RAA_TAFKHEEM, site=skeleton)
        if name is None:
            return site.default_heavy
        weight = HEAVY.get(name)
        if weight is None:
            raise KhilafError(
                f"{KhilafId.RAA_TAFKHEEM.value}: {name!r} is not an option; "
                f"expected one of {sorted(HEAVY)}"
            )
        return weight

    def points(self) -> dict[str, dict[str, object]]:
        """What a caller may choose, without reading the data file."""
        return {
            skeleton: {
                "options": sorted(HEAVY),
                "default": "heavy" if site.default_heavy else "light",
                "disputed_at": "stop" if site.at_stop else "join",
            }
            for skeleton, site in self.sites.items()
        }
