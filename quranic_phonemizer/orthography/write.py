"""Score -> text: the inverse of reading.

Correctness is round-trip closure, not byte identity -- spelling a Score
and reading it back must reproduce it.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..model.canon import CanonLetter, NucleusKind, Onset, Quality, Score
from ..model.inscription import SlotFact
from .inventory import Inventory, InventoryError

#: Which role writes each nucleus quality, and which carrier lengthens it.
_SHORT_ROLE = {Quality.A: "fatha", Quality.U: "damma", Quality.I: "kasra"}

#: Imala and ishmam are colourings a reciter applies to an ordinary vowel,
#: not vowels of their own, so they spell as their base quality.
_BASE = {Quality.IMALA: Quality.A}

#: The mark that says a carrier lengthens the vowel before it.
MADD = "madd"
_CARRIER = {
    Quality.A: CanonLetter.ALIF,
    Quality.U: CanonLetter.WAW,
    Quality.I: CanonLetter.YA,
}


class WriteError(ValueError):
    """A canonical fact this script has no scalar for. Never a silent gap."""


@dataclass(frozen=True, slots=True)
class Pen:
    """The inventory, inverted once. Built per script, not per verse."""

    letters: dict[CanonLetter, str]
    roles: dict[str, str]
    onsets: dict[Onset, str]
    carriers: dict[CanonLetter, str]
    """The scalar that lengthens a vowel, as opposed to the one that spells
    the same letter as a consonant -- `dagger_host` scalars can do either.
    """

    def letter(self, letter: CanonLetter) -> str:
        scalar = self.letters.get(letter)
        if scalar is None:
            raise WriteError(
                f"no scalar writes {letter.value} in this script. `write` is "
                f"total over `CanonLetter` or the round-trip cannot close."
            )
        return scalar

    def role(self, role: str) -> str:
        scalar = self.roles.get(role)
        if scalar is None:
            raise WriteError(f"no scalar has role {role!r} in this script")
        return scalar


def pen_for(inventory: Inventory) -> Pen:
    """Invert an inventory. Ambiguity resolves to the first scalar declared
    for a given letter or role."""
    letters: dict[CanonLetter, str] = {}
    onsets: dict[Onset, str] = {}
    # Two passes: plain letters first, then dagger_host/bare_rasm scalars as
    # a fallback -- they are still valid letters, just not the first choice.
    carriers: dict[CanonLetter, str] = {}
    for plain in (True, False):
        for scalar, entry in inventory.letters.items():
            rasm = entry.dagger_host or entry.bare_rasm
            if (not rasm) is not plain:
                continue
            if entry.onset is not None:
                onsets.setdefault(entry.onset, scalar)
                continue
            letters.setdefault(entry.letter, scalar)
            if rasm:
                carriers.setdefault(entry.letter, scalar)
    roles: dict[str, str] = {}
    for scalar, mark in inventory.marks.items():
        if mark.role and (mark.fact is not None or mark.decorates is not None):
            roles.setdefault(mark.role, scalar)
    return Pen(letters=letters, roles=roles, onsets=onsets,
               carriers=carriers)


def write_verse(score: Score, pen: Pen) -> tuple[str, ...]:
    """One string per `ScoreWord`, in order."""
    return tuple(_word(word, pen) for word in score.words)


def _word(word, pen: Pen) -> str:
    return "".join(_slot(slot, pen) for slot in word.slots)


def _slot(slot, pen: Pen) -> str:
    if slot.onset is Onset.WASL:
        out = pen.onsets.get(Onset.WASL) or pen.letter(CanonLetter.ALIF)
    else:
        out = pen.letter(slot.letter)
    if slot.onset is Onset.GEMINATE:
        out += pen.role("shadda")
    out += _nucleus(slot, pen)
    for annotation in sorted(slot.annotations):
        # An annotation a script writes has a role; one the builder derives
        # has none and is re-derived on the way back in.
        if annotation.value in pen.roles:
            out += pen.role(annotation.value)
    return out


def _nucleus(slot, pen: Pen) -> str:
    nucleus = slot.nucleus
    quality = _BASE.get(getattr(nucleus, "quality", None), None) or getattr(
        nucleus, "quality", None
    )
    match nucleus.kind:
        case NucleusKind.SILENT:
            return pen.role("sukun")
        case NucleusKind.SHORT:
            return pen.role(_short_role(quality))
        case NucleusKind.LONG | NucleusKind.PAUSAL_LONG:
            # Always write the full haraka plus carrier rather than the
            # dagger abbreviation; both read back to the same slot. The madd
            # sign says the carrier lengthens rather than standing for a
            # letter, which is what keeps a bare alif from reading back as a
            # prosthetic hamza.
            carrier = _CARRIER[quality]
            return (
                pen.role(_short_role(quality))
                + (pen.carriers.get(carrier) or pen.letter(carrier))
                + pen.roles.get(MADD, "")
            )
        case NucleusKind.SILAH:
            return pen.role("silah_waw" if quality is Quality.U else "silah_ya")
    raise WriteError(f"no spelling for nucleus kind {nucleus.kind.value}")


def _short_role(quality) -> str:
    role = _SHORT_ROLE.get(quality)
    if role is None:
        raise WriteError(f"no haraka writes quality {quality}")
    return role


__all__ = ["Pen", "WriteError", "pen_for", "write_verse", "InventoryError",
           "SlotFact"]
