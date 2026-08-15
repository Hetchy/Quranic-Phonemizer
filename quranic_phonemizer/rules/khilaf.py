"""Reading a named point of legitimate disagreement off the Score."""
from __future__ import annotations

from dataclasses import dataclass, field

from ..model.address import KhilafId, VariantSelection
from ..model.canon import ABJAD, CanonLetter, Onset

#: Both readings of the two bilabial hidings are taught and both are correct.
#: A hidden meem before the baa is the phonetic description; the generic nasal
#: is what a reciter who does not close the lips produces. The reading rides
#: on the letter the rule mints: a real meem sounds where the lips close, a
#: noon-lettered hum where they do not.
NASAL_PLACES = {
    "bilabial": CanonLetter.MEEM,
    "assimilated": CanonLetter.NOON,
}
DEFAULT_NASAL_PLACE = CanonLetter.NOON

#: The two readings of a disputed raa, as a reader names them.
HEAVY = {"heavy": True, "light": False}

#: Whether a word-final yaa is still said once the stop has taken its vowel.
KEPT = {"ithbat": True, "hadhf": False}

class KhilafError(ValueError):
    """An option name no rule can act on."""


def nasal_place(selection: VariantSelection, khilaf: KhilafId) -> CanonLetter:
    name = selection.chosen(khilaf)
    if name is None:
        return DEFAULT_NASAL_PLACE
    letter = NASAL_PLACES.get(name)
    if letter is None:
        raise KhilafError(
            f"{khilaf.value}: {name!r} is not an option; expected one of "
            f"{sorted(NASAL_PLACES)}"
        )
    return letter


@dataclass(frozen=True, slots=True)
class Site:
    """One word of a khilaf that recurs word by word."""

    khilaf: KhilafId
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

    sites: dict[str, Site] = field(default_factory=dict)
    options: dict[KhilafId, dict[str, bool]] = field(default_factory=dict)

    def of(
        self, skeleton: str, stopped: bool, selection: VariantSelection
    ) -> bool | None:
        """`None` where this is no disputed site in this junction, which
        leaves the answer to the rule that decides every other word."""
        site = self.sites.get(skeleton)
        if site is None or site.at_stop is not stopped:
            return None
        name = selection.chosen(site.khilaf)
        if name is None:
            return site.default
        options = self.options[site.khilaf]
        if name not in options:
            raise KhilafError(
                f"{site.khilaf.value}: {name!r} is not an option; expected "
                f"one of {sorted(options)}"
            )
        return options[name]


def vocalised_word(word) -> str:
    """The word as a khilaf names its sites: letters and their vowels. Read
    from the Score, so a vowel a stop removes is still in the key."""
    out = []
    for slot in word.slots:
        quality = slot.nucleus.quality
        out.append(
            ABJAD[slot.letter.value]
            + ("~" if slot.onset is Onset.GEMINATE else "")
            + (quality.value if quality else "")
        )
    return "".join(out)
