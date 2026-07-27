"""Reading a named point of legitimate disagreement off the Score."""
from __future__ import annotations

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
