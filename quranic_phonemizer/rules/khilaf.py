"""Reading a named point of legitimate disagreement off the Score."""
from __future__ import annotations

from dataclasses import dataclass, field

from ..model.address import KhilafId, VariantSelection
from ..model.canon import ABJAD, NucleusKind, Onset
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

#: Whether a word-final yaa is still said once the stop has taken its vowel.
KEPT = {"ithbat": True, "hadhf": False}

#: The option set each sited point is read with.
OPTIONS = {
    KhilafId.RAA_TAFKHEEM: HEAVY,
    KhilafId.YAA_ITHBAT: KEPT,
}


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

    default: bool


@dataclass(frozen=True, slots=True)
class SitedKhilaf:
    """A point disputed word by word, in one junction, two ways.

    The raa's weight and the pronoun yaa's survival are the same question
    asked of different things, so they are one structure and not two.
    """

    khilaf: KhilafId = KhilafId.RAA_TAFKHEEM
    sites: dict[str, Site] = field(default_factory=dict)

    def of(
        self, skeleton: str, stopped: bool, selection: VariantSelection
    ) -> bool | None:
        """`None` where this is no disputed site in this junction, which
        leaves the answer to the rule that decides every other word."""
        site = self.sites.get(skeleton)
        if site is None or site.at_stop is not stopped:
            return None
        name = selection.chosen(self.khilaf, site=skeleton)
        if name is None:
            return site.default
        options = OPTIONS[self.khilaf]
        if name not in options:
            raise KhilafError(
                f"{self.khilaf.value}: {name!r} is not an option; expected "
                f"one of {sorted(options)}"
            )
        return options[name]

    def points(self) -> dict[str, dict[str, object]]:
        """What a caller may choose, without reading the data file."""
        options = OPTIONS[self.khilaf]
        named = {value: name for name, value in options.items()}
        return {
            skeleton: {
                "options": sorted(options),
                "default": named[site.default],
                "disputed_at": "stop" if site.at_stop else "join",
            }
            for skeleton, site in self.sites.items()
        }


def vocalised_word(word) -> str:
    """The word as a khilaf names its sites: letters and their vowels. Read
    from the Score, so a vowel a stop removes is still in the key."""
    out = []
    for slot in word.slots:
        quality = getattr(slot.nucleus, "quality", None)
        if slot.nucleus.kind is NucleusKind.SILENT:
            quality = None
        out.append(
            ABJAD[slot.letter.value]
            + ("~" if slot.onset is Onset.GEMINATE else "")
            + (quality.value if quality else "")
        )
    return "".join(out)
