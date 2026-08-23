"""Which unit owns each sound, which units present it, and why it is silent.

A consonant is owned by its letter, a long vowel by its carrier or haraka; a
silent letter names the rule that silenced or shortened it, or the orthographic.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from ..model.address import SlotId
from ..model.canon import ABJAD, CanonLetter
from ..model.performance import Aspect, Vowel
from .derivations import shortened_carriers
from .facts import AnalysisFacts
from .inscription import InscriptionFacts
from .source_dtos import LetterUnitKind, LiteralSilence, Silence
from .source_units import Tokenization

#: A base letter's canonical identity, read off its rasm glyph.
_LETTER_OF_BASE = {glyph: CanonLetter(name) for name, glyph in ABJAD.items()}


@dataclass(frozen=True, slots=True)
class Ownership:
    owner: dict[int, int]
    presenters: dict[int, frozenset[int]]
    silence: dict[int, Silence]


def _is_long(facts: AnalysisFacts, sound: int) -> bool:
    value = facts.sounds[sound].value
    return isinstance(value, Vowel) and value.long


def _vowel_unit(facts, tok: Tokenization, slot: SlotId, sound: int) -> int | None:
    roles = tok.roles
    if _is_long(facts, sound) and slot in roles.carrier:
        return roles.carrier[slot]
    if slot in roles.vowel:
        return roles.vowel[slot]
    return roles.letter.get(slot)


def _slot_letter(facts: AnalysisFacts, slot: SlotId) -> CanonLetter:
    return facts.slots[facts.slot_index[slot]].letter


def _paired_owner(facts, tok, insc, slot: SlotId, base: int) -> int:
    """A base letter and the mini seen written on it are a seen/saad pair; the
    read half is the one whose letter is the slot's, the other stays silent."""
    marks = [
        i for i, unit in enumerate(tok.units)
        if unit.written_on_anchor is not None
        and tok.unit_of_anchor.get(unit.written_on_anchor) == base
    ]
    if not marks:
        return base
    base_letter = _LETTER_OF_BASE.get(insc.glyphs[tok.units[base].anchor].char)
    return base if base_letter is _slot_letter(facts, slot) else marks[0]


def _variant_pair_units(tok: Tokenization) -> frozenset[int]:
    pairs: set[int] = set()
    for index, unit in enumerate(tok.units):
        if unit.written_on_anchor is None:
            continue
        base = tok.unit_of_anchor.get(unit.written_on_anchor)
        if base is not None:
            pairs.update((base, index))
    return frozenset(pairs)


def _unit_at(facts, tok, insc, slot: SlotId, aspect: Aspect, sound: int) -> int | None:
    if aspect is Aspect.VOWEL:
        return _vowel_unit(facts, tok, slot, sound)
    # A tanween's own noon has no letter of its own; its unit is the tanween.
    base = tok.roles.letter.get(slot, tok.roles.vowel.get(slot))
    return None if base is None else _paired_owner(facts, tok, insc, slot, base)


def _present_carrier_vowel(facts, tok, slot, sound, owner, presenters):
    """A carrier-owned long vowel lights its haraka with it. Where the carrier
    is the haraka itself -- a length on a seat, not a letter -- it owns alone."""
    if not _is_long(facts, sound) or slot not in tok.roles.carrier:
        return
    vowel = tok.roles.vowel.get(slot)
    if owner == tok.roles.carrier[slot] and vowel is not None and vowel != owner:
        presenters[sound].add(vowel)


def _owners_and_presenters(facts, tok, insc):
    owner: dict[int, int] = {}
    presenters: dict[int, set[int]] = defaultdict(set)
    for edge in facts.hosts:
        unit = _unit_at(facts, tok, insc, edge.slots[0], edge.aspect, edge.sound)
        if unit is not None:
            owner[edge.sound] = unit
            if edge.aspect is Aspect.VOWEL:
                _present_carrier_vowel(
                    facts, tok, edge.slots[0], edge.sound, unit, presenters
                )
    for edge in facts.insertions:
        unit = _unit_at(facts, tok, insc, edge.anchor[0], edge.aspect, edge.sound)
        if unit is not None:
            owner.setdefault(edge.sound, unit)
    for edge in facts.merges:
        unit = tok.roles.letter.get(edge.slots[0])
        if unit is not None:
            presenters[edge.sound].add(unit)
    return owner, presenters


def _silenced_units(facts, tok) -> dict[int, int]:
    """Unit -> the occurrence that silenced it, from the performance edges."""
    out: dict[int, int] = {}
    for edge in facts.silences:
        if edge.by is None:
            continue
        unit = tok.roles.letter.get(edge.slots[0])
        if edge.aspect is Aspect.VOWEL:
            unit = tok.roles.vowel.get(edge.slots[0], unit)
        if unit is not None:
            out.setdefault(unit, edge.by)
    return out


def _shortened_units(facts, tok, insc) -> dict[int, int]:
    """Unit -> the occurrence whose rule shortened its length carrier."""
    return {
        tok.unit_of_glyph[glyph]: occ
        for glyph, occ in shortened_carriers(facts, insc).items()
        if glyph in tok.unit_of_glyph
    }


def ownership(
    facts: AnalysisFacts, tok: Tokenization, insc: InscriptionFacts
) -> Ownership:
    owner, presenters = _owners_and_presenters(facts, tok, insc)
    sounding = set(owner.values()) | {u for us in presenters.values() for u in us}
    silenced_by = _silenced_units(facts, tok)
    shortened = _shortened_units(facts, tok, insc)
    variant_pairs = _variant_pair_units(tok)
    silence: dict[int, Silence] = {}
    for index, unit in enumerate(tok.units):
        if index in sounding:
            silence[index] = None
        elif unit.kind is LetterUnitKind.LETTER:
            silence[index] = (
                silenced_by[index] if index in silenced_by
                else shortened.get(
                    index,
                    LiteralSilence.VARIANT
                    if index in variant_pairs
                    else LiteralSilence.ORTHOGRAPHIC,
                )
            )
        else:
            silence[index] = None
    return Ownership(
        owner=owner,
        presenters={s: frozenset(u) for s, u in presenters.items()},
        silence=silence,
    )


__all__ = ["Ownership", "ownership"]
