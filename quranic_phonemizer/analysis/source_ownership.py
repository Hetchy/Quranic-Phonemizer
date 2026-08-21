"""Which unit owns each sound, which units present it, and why it is silent.

A consonant is owned by its letter, a long vowel by its written carrier or else
its haraka; a silent letter names the rule that silenced it or the orthographic.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from ..model.address import SlotId
from ..model.performance import Aspect, Vowel
from .facts import AnalysisFacts
from .source_dtos import LetterUnitKind, LiteralSilence, Silence
from .source_units import Tokenization


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


def _unit_at(facts, tok, slot: SlotId, aspect: Aspect, sound: int) -> int | None:
    if aspect is Aspect.VOWEL:
        return _vowel_unit(facts, tok, slot, sound)
    # A tanween's own noon has no letter of its own; its unit is the tanween.
    return tok.roles.letter.get(slot, tok.roles.vowel.get(slot))


def _present_carrier_vowel(facts, tok, slot, sound, owner, presenters):
    """A carrier-owned long vowel lights its haraka with it. Where the carrier
    is the haraka itself -- a length on a seat, not a letter -- it owns alone."""
    if not _is_long(facts, sound) or slot not in tok.roles.carrier:
        return
    vowel = tok.roles.vowel.get(slot)
    if owner == tok.roles.carrier[slot] and vowel is not None and vowel != owner:
        presenters[sound].add(vowel)


def _owners_and_presenters(facts, tok):
    owner: dict[int, int] = {}
    presenters: dict[int, set[int]] = defaultdict(set)
    for edge in facts.hosts:
        unit = _unit_at(facts, tok, edge.slots[0], edge.aspect, edge.sound)
        if unit is not None:
            owner[edge.sound] = unit
            if edge.aspect is Aspect.VOWEL:
                _present_carrier_vowel(
                    facts, tok, edge.slots[0], edge.sound, unit, presenters
                )
    for edge in facts.insertions:
        unit = _unit_at(facts, tok, edge.anchor[0], edge.aspect, edge.sound)
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


def ownership(facts: AnalysisFacts, tok: Tokenization) -> Ownership:
    owner, presenters = _owners_and_presenters(facts, tok)
    sounding = set(owner.values()) | {u for us in presenters.values() for u in us}
    silenced_by = _silenced_units(facts, tok)
    silence: dict[int, Silence] = {}
    for index, unit in enumerate(tok.units):
        if index in sounding:
            silence[index] = None
        elif unit.kind is LetterUnitKind.LETTER:
            silence[index] = (
                silenced_by[index] if index in silenced_by
                else LiteralSilence.ORTHOGRAPHIC
            )
        else:
            silence[index] = None
    return Ownership(
        owner=owner,
        presenters={s: frozenset(u) for s, u in presenters.items()},
        silence=silence,
    )


__all__ = ["Ownership", "ownership"]
