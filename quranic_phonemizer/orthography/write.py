"""Score -> text: the inverse of reading.

Correctness is round-trip closure, not byte identity -- spelling a Score
and reading it back must reproduce it.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..model.canon import (
    CARRIER_OF,
    Annotation,
    CanonLetter,
    NucleusKind,
    Onset,
    Quality,
    Score,
    SlotOrigin,
)
from .inventory import Inventory

#: Which role writes each nucleus quality, and which carrier lengthens it.
_SHORT_ROLE = {Quality.A: "fatha", Quality.U: "damma", Quality.I: "kasra"}

#: The same three vowels doubled, which is how a script writes the noon that
#: follows them rather than drawing the letter.
_TANWEEN_ROLE = {
    Quality.A: "fathatan", Quality.U: "dammatan", Quality.I: "kasratan",
}

#: Imala and ishmam are colourings a reciter applies to an ordinary vowel,
#: not vowels of their own, so they spell as their base quality wherever the
#: script has no mark that says otherwise.
_BASE = {Quality.E: Quality.A}

#: Onsets and qualities a script may name outright.
TASHIL = "tashil"
IMALA = "imala"

#: The mark that says a carrier lengthens the vowel before it.
MADD = "madd"

#: Annotations the nucleus spells on their behalf, so writing them again
#: would put the same mark down twice.
_SPELT_AS_A_NUCLEUS = frozenset({Annotation.IMALA})

#: How each script spells the pronoun haa's conditional vowel.
_SILAH_ROLES = {
    Quality.U: ("silah_waw", "small_waw"),
    Quality.I: ("silah_ya", "small_ya"),
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
    names: dict[tuple, CanonLetter] = field(default_factory=dict)
    """What each letter's spoken name spells, reversed. Injected, because the
    table it comes from belongs to the reading and not to the script."""

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


def pen_for(inventory: Inventory, names: dict | None = None) -> Pen:
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
               carriers=carriers, names=names or {})


def write_verse(score: Score, pen: Pen) -> tuple[str, ...]:
    """One string per `ScoreWord`, in order."""
    return tuple(_word(word, pen) for word in score.words)


def _word(word, pen: Pen) -> str:
    slots = list(word.slots)
    out = []
    index = 0
    while index < len(slots):
        step = _spelled_name(slots, index, pen)
        if step is not None:
            text, index = step
            out.append(text)
            continue
        if _nunated(slots, index):
            doubled = pen.role(_TANWEEN_ROLE[slots[index].nucleus.quality])
            out.append(_slot(slots[index], pen, nucleus=doubled))
            index += 2
            continue
        out.append(_slot(slots[index], pen))
        index += 1
    return "".join(out)


def _nunated(slots, index: int) -> bool:
    """A slot whose noon the script writes by doubling its vowel.

    Spelling the noon as a letter would read back as an ordinary one, and
    the rules that own the pause tell the two apart.
    """
    if index + 1 >= len(slots) or slots[index + 1].origin is not SlotOrigin.NUNATION:
        return False
    return (
        slots[index].nucleus.kind is NucleusKind.SHORT
        and slots[index].origin is not SlotOrigin.NUNATION
        and getattr(slots[index].nucleus, "quality", None) in _TANWEEN_ROLE
    )


def _spelled_name(slots, index: int, pen: Pen):
    """A letter said by its name is written as the letter, not as its name."""
    if slots[index].origin is not SlotOrigin.SPELLED or not pen.names:
        return None
    for length in range(len(slots) - index, 0, -1):
        run = tuple(slots[index:index + length])
        if any(slot.origin is not SlotOrigin.SPELLED for slot in run):
            continue
        letter = pen.names.get(tuple(_spelt(slot) for slot in run))
        if letter is not None:
            return pen.letter(letter), index + length
    return None


def _spelt(slot) -> tuple:
    return (slot.letter, slot.nucleus.kind, getattr(slot.nucleus, "quality", None))


def _slot(slot, pen: Pen, nucleus: str | None = None) -> str:
    """`nucleus` overrides the vowel text when the script writes the slot
    after this one into the same mark."""
    if slot.onset is Onset.WASL:
        out = pen.onsets.get(Onset.WASL) or pen.letter(CanonLetter.ALIF)
    else:
        out = pen.letter(slot.letter)
    if slot.onset is Onset.GEMINATE:
        out += pen.role("shadda")
    elif slot.onset is Onset.TASHIL and TASHIL in pen.roles:
        out += pen.role(TASHIL)
    out += _nucleus(slot, pen) if nucleus is None else nucleus
    for annotation in sorted(slot.annotations):
        # An annotation a script writes has a role; one the builder derives
        # has none and is re-derived on the way back in.
        if annotation in _SPELT_AS_A_NUCLEUS:
            continue
        if annotation.value in pen.roles:
            out += pen.role(annotation.value)
    return out


def _nucleus(slot, pen: Pen) -> str:
    nucleus = slot.nucleus
    if Annotation.IMALA in slot.annotations and IMALA in pen.roles:
        # The mark stands for the whole vowel, carrier and all, whichever
        # of the two the khilaf selected.
        return pen.role(IMALA)
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
            carrier = CARRIER_OF[quality]
            return (
                pen.role(_short_role(quality))
                + (pen.carriers.get(carrier) or pen.letter(carrier))
                + pen.roles.get(MADD, "")
            )
        case NucleusKind.SILAH:
            # One script spells the pronoun's vowel and its carrier in a
            # single mark; the other writes the vowel and then the carrier.
            composite, carrier = _SILAH_ROLES[quality]
            if composite in pen.roles:
                return pen.role(composite)
            return pen.role(_short_role(quality)) + pen.role(carrier)
    raise WriteError(f"no spelling for nucleus kind {nucleus.kind.value}")


def _short_role(quality) -> str:
    role = _SHORT_ROLE.get(quality)
    if role is None:
        raise WriteError(f"no haraka writes quality {quality}")
    return role


__all__ = ["Pen", "WriteError", "pen_for", "write_verse"]
