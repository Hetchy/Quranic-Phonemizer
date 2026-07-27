"""Score → Arabic. The other direction across the script boundary.

`read` extracts evidence from a script; `write` spells a Score back into one.
ADR-005 §4 makes the second a gate rather than a convenience: **if some Score
cannot be spelled, the canonical layer is holding something no orthography can
express**, and that is the shape of a missing layer.

The gate is not byte-identity with the source, which would be false by design —
`read` deliberately discards what the Score does not need, so `write` cannot
put it back and should not pretend to. The invariant that is both true and
worth having is **Score → text → Score**: spelling a Score and reading the
result must give the same Score. That proves `write` covers the whole canonical
vocabulary, which is what §4 actually asks.

Nothing here is a table of its own. The spelling is the script's own inventory
read backwards: the inventory already says "this scalar evidences `Short(A)`",
so `write` asks it which scalar evidences `Short(A)`. A second table would be
the same facts written twice, and the two would drift.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..model.canon import CanonLetter, NucleusKind, Onset, Quality, Score
from ..model.inscription import SlotFact
from .inventory import Inventory, InventoryError

#: Which role writes each nucleus quality, and which carrier lengthens it.
_SHORT_ROLE = {Quality.A: "fatha", Quality.U: "damma", Quality.I: "kasra"}

#: Imāla and ishmām are *colourings a reciter applies* to an ordinary vowel,
#: not vowels in their own right, and the scripts that mark them write an
#: annotation on top of the ordinary haraka. So they spell as their base and
#: the annotation belongs to recited writing rather than to this. Without the
#: mapping a long imāla vowel raised `KeyError` instead of a `WriteError`,
#: which is the difference between a bug and a stated gap.
_BASE = {Quality.IMALA: Quality.A, Quality.ISHMAM: Quality.I}
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
    """The scalar that lengthens rather than the one that consonants.

    `dagger_host` is exactly the inventory's word for "this glyph may stand
    for length rather than for itself", so the carrier map is the entries the
    letter map takes second. Spelling a long ī with the consonantal `ي`
    instead of the bare `ى` made 71 verses read back with a short vowel --
    the carrier was no longer recognised as one.
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
    """Invert an inventory. Ambiguity is resolved by *first declared wins*,
    which is why the YAML lists the ordinary scalar before its variants."""
    letters: dict[CanonLetter, str] = {}
    onsets: dict[Onset, str] = {}
    # Two passes. `dagger_host` and `bare_rasm` describe scalars that *may*
    # stand for something else as well -- Uthmani's `و` can carry a dagger for
    # the slot before it -- but they are still the letter, so they are a
    # fallback rather than an exclusion. Skipping them outright left wāw and
    # yāʾ with no spelling at all.
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
        if mark.role and mark.fact is not None:
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
    return out + _nucleus(slot, pen)


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
            # A long vowel is its haraka plus the carrier that lengthens it.
            # Written out rather than as a dagger, because the dagger is a
            # script's *abbreviation* of exactly this and reading it back
            # gives the same slot either way.
            carrier = _CARRIER[quality]
            return pen.role(_short_role(quality)) + (
                pen.carriers.get(carrier) or pen.letter(carrier)
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
