"""Which unit owns each sound, which units present it, and why it is silent.

A consonant is owned by its letter, a long vowel by its carrier or haraka; a
silent letter names the rule that silenced or shortened it, or the orthographic.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from ..model.address import SlotId
from ..model.canon import ABJAD, CanonLetter, Rule, SlotOrigin
from ..model.performance import Aspect, Vowel
from .derivations import (
    decoration_targets,
    open_vowel_units,
    shortened_carriers,
    silent_groups,
)
from .facts import AnalysisFacts
from .inscription import InscriptionFacts, Witnessed
from .source_dtos import LetterUnitKind, LiteralSilence, Silence
from .source_units import Tokenization

#: The only riding letters whose active or silent state denotes a variant.
#: Other source-backed tajweed marks (notably Warsh's native iqlab meem) may
#: ride a host too, but that geometric relation is not a variant handoff.
_MINI_SEEN = frozenset({"ۜ", "ۣ"})

#: A base letter's canonical identity, read off its rasm glyph.
_LETTER_OF_BASE = {glyph: CanonLetter(name) for name, glyph in ABJAD.items()}


@dataclass(frozen=True, slots=True)
class Ownership:
    owner: dict[int, int]
    presenters: dict[int, frozenset[int]]
    silence: dict[int, Silence]
    shortened: dict[int, int]
    """Length-carrier unit -> occurrence that shortened it."""
    carrier_only: frozenset[int]
    """Shortening occurrences placed only on their written carrier."""


class OwnershipError(ValueError):
    """A written letter has no sound and no native silence derivation."""


def _is_long(facts: AnalysisFacts, sound: int) -> bool:
    value = facts.sounds[sound].value
    return isinstance(value, Vowel) and value.long


def _vowel_unit(facts, tok: Tokenization, carriers,
                slot: SlotId, sound: int) -> int | None:
    roles = tok.roles
    if _is_long(facts, sound) and slot in carriers:
        return carriers[slot]
    if slot in roles.vowel:
        return roles.vowel[slot]
    return roles.letter.get(slot)


def _slot_letter(facts: AnalysisFacts, slot: SlotId) -> CanonLetter:
    return facts.slots[facts.slot_index[slot]].letter


def _paired_owner(facts, tok, insc, slot: SlotId, base: int) -> int:
    """Resolve a riding pronunciation letter's owner.

    A seen/saad mini seen changes the base saad's realization but never becomes
    its sound host.  Other riding letters retain the native ownership rule.
    """
    marks = [
        i for i, unit in enumerate(tok.units)
        if unit.written_on_anchor is not None
        and tok.unit_of_anchor.get(unit.written_on_anchor) == base
    ]
    if not marks:
        return base
    if any(index in _mini_seen_units(tok, insc) for index in marks):
        return base
    base_letter = _LETTER_OF_BASE.get(insc.glyphs[tok.units[base].anchor].char)
    return base if base_letter is _slot_letter(facts, slot) else marks[0]


def _riding_pair_units(tok: Tokenization) -> frozenset[int]:
    pairs: set[int] = set()
    for index, unit in enumerate(tok.units):
        if unit.written_on_anchor is None:
            continue
        base = tok.unit_of_anchor.get(unit.written_on_anchor)
        if base is not None:
            pairs.update((base, index))
    return frozenset(pairs)


def _variant_pair_units(
    tok: Tokenization, insc: InscriptionFacts
) -> frozenset[int]:
    riding = _riding_pair_units(tok)
    seen = _mini_seen_units(tok, insc)
    return frozenset(
        index for index in riding
        if index in seen or any(
            tok.unit_of_anchor.get(tok.units[item].written_on_anchor) == index
            for item in seen
        )
    )


def _mini_seen_units(
    tok: Tokenization, insc: InscriptionFacts
) -> frozenset[int]:
    return frozenset(
        index for index, unit in enumerate(tok.units)
        if any(
            insc.glyphs[glyph].char in _MINI_SEEN for glyph in unit.glyphs
        )
    )


def _unit_at(facts, tok, insc, carriers,
             slot: SlotId, aspect: Aspect, sound: int) -> int | None:
    if aspect is Aspect.VOWEL:
        return _vowel_unit(facts, tok, carriers, slot, sound)
    # A tanween's own noon has no letter of its own; its unit is the tanween.
    base = tok.roles.letter.get(slot, tok.roles.vowel.get(slot))
    return None if base is None else _paired_owner(
        facts, tok, insc, slot, base
    )


def _present_carrier_vowel(
    facts, tok, carriers, slot, sound, owner, presenters
):
    """A carrier-owned long vowel lights its haraka with it. Where the carrier
    is the haraka itself -- a length on a seat, not a letter -- it owns alone."""
    if not _is_long(facts, sound) or slot not in carriers:
        return
    vowel = tok.roles.vowel.get(slot)
    if owner == carriers[slot] and vowel is not None and vowel != owner:
        presenters[sound].add(vowel)


def _present_active_seen_mark(facts, tok, insc, slot, sound, owner, presenters):
    """The mini seen announces /s/ while the base saad remains its host."""
    if _slot_letter(facts, slot) is not CanonLetter.SEEN:
        return
    for index in _mini_seen_units(tok, insc):
        unit = tok.units[index]
        if (
            unit.written_on_anchor is not None
            and tok.unit_of_anchor.get(unit.written_on_anchor) == owner
        ):
            presenters[sound].add(index)


def _naql_witness_unit(facts, tok, insc, edge) -> int | None:
    if (
        edge.by is None
        or edge.aspect is not Aspect.VOWEL
        or facts.occurrences[edge.by].rule is not Rule.NAQL
    ):
        return None
    candidates = [
        tok.unit_of_glyph[spelling.glyph]
        for spelling in insc.spellings
        if isinstance(spelling, Witnessed)
        and spelling.slot == edge.slots[0]
        and spelling.glyph in tok.unit_of_glyph
        and tok.units[tok.unit_of_glyph[spelling.glyph]].kind
            is LetterUnitKind.HARAKA
    ]
    return candidates[-1] if candidates else None


def _owners_and_presenters(facts, tok, insc, carriers):
    owner: dict[int, int] = {}
    presenters: dict[int, set[int]] = defaultdict(set)
    for edge in facts.hosts:
        unit = _naql_witness_unit(facts, tok, insc, edge)
        if unit is None:
            unit = _unit_at(
                facts, tok, insc, carriers,
                edge.slots[0], edge.aspect, edge.sound,
            )
        if unit is not None:
            owner[edge.sound] = unit
            if edge.aspect is Aspect.VOWEL:
                _present_carrier_vowel(
                    facts, tok, carriers, edge.slots[0], edge.sound,
                    unit, presenters,
                )
            else:
                _present_active_seen_mark(
                    facts, tok, insc, edge.slots[0], edge.sound,
                    unit, presenters,
                )
    for edge in facts.insertions:
        unit = _unit_at(
            facts, tok, insc, carriers,
            edge.anchor[0], edge.aspect, edge.sound,
        )
        if unit is not None:
            owner.setdefault(edge.sound, unit)
    for edge in facts.merges:
        presenter = facts.slots[facts.slot_index[edge.slots[0]]]
        tanween_naql = (
            edge.by is not None
            and edge.aspect is Aspect.VOWEL
            and presenter.origin is SlotOrigin.NUNATION
            and facts.occurrences[edge.by].rule is Rule.NAQL
        )
        unit = (
            _unit_at(
                facts, tok, insc, carriers,
                edge.slots[0], edge.aspect, edge.sound,
            )
            if tanween_naql else tok.roles.letter.get(edge.slots[0])
        )
        if unit is not None and unit != owner.get(edge.sound):
            presenters[edge.sound].add(unit)
    return owner, presenters


def _silenced_units(facts, tok) -> dict[int, int]:
    """Unit -> the occurrence that silenced it, from the performance edges."""
    out: dict[int, int] = {}
    for edge in facts.silences:
        if edge.by is None:
            continue
        rule = facts.occurrences[edge.by].rule
        unit = tok.roles.letter.get(edge.slots[0])
        if edge.aspect is Aspect.VOWEL:
            unit = tok.roles.vowel.get(edge.slots[0], unit)
            if rule is Rule.WAQF_SILAH_DROP:
                carrier = tok.roles.carrier.get(edge.slots[0])
                if carrier is not None:
                    out.setdefault(carrier, edge.by)
        if unit is not None:
            out.setdefault(unit, edge.by)
    # A source-backed pronunciation mark riding a silenced unit is cancelled
    # by that same explicit occurrence. It is not a variant or an eternally
    # orthographic letter merely because the stopped performance leaves it
    # without a sound (Warsh tanween iqlab mini-meem at waqf).
    for index, draft in enumerate(tok.units):
        if draft.written_on_anchor is None:
            continue
        host = tok.unit_of_anchor.get(draft.written_on_anchor)
        if host in out:
            out.setdefault(index, out[host])
    return out


def _shortened_units(facts, tok, insc) -> dict[int, int]:
    """Unit -> the occurrence whose rule shortened its length carrier."""
    return {
        tok.unit_of_glyph[glyph]: occ
        for glyph, occ in shortened_carriers(facts, insc).items()
        if glyph in tok.unit_of_glyph
    }


def _orthographic_units(facts, tok, insc) -> frozenset[int]:
    groups = silent_groups(
        insc, open_vowel_units(facts), decoration_targets(insc)
    )
    return frozenset(
        tok.unit_of_glyph[glyph]
        for group in groups for glyph in group
        if glyph in tok.unit_of_glyph
    )


def _orthographic_seats(tok: Tokenization) -> frozenset[int]:
    """A rasm seat stays silent when another unit writes the slot's letter."""
    letters = set(tok.roles.letter.values())
    vowels = set(tok.roles.vowel.values())
    carriers = set(tok.roles.carrier.values())
    return frozenset(
        index for index, unit in enumerate(tok.units)
        if unit.kind is LetterUnitKind.LETTER
        and unit.slot is not None
        and tok.roles.letter.get(unit.slot) is not None
        and index not in letters | vowels | carriers
    )


def _unclassified(index, unit, insc):
    text = "".join(insc.glyphs[glyph].char for glyph in unit.glyphs)
    raise OwnershipError(
        f"letter unit {index} {text!r} has no sound or silence derivation"
    )


def ownership(
    facts: AnalysisFacts, tok: Tokenization, insc: InscriptionFacts
) -> Ownership:
    carriers = tok.roles.carrier
    owner, presenters = _owners_and_presenters(facts, tok, insc, carriers)
    sounding = set(owner.values()) | {u for us in presenters.values() for u in us}
    silenced_by = _silenced_units(facts, tok)
    shortened = _shortened_units(facts, tok, insc)
    riding_pairs = _riding_pair_units(tok)
    variant_pairs = _variant_pair_units(tok, insc)
    mini_seen = _mini_seen_units(tok, insc)
    orthographic = _orthographic_units(facts, tok, insc)
    seats = _orthographic_seats(tok)
    silence: dict[int, Silence] = {}
    for index, unit in enumerate(tok.units):
        if index in sounding:
            silence[index] = None
        elif unit.kind is LetterUnitKind.LETTER:
            if index in silenced_by:
                silence[index] = silenced_by[index]
            elif index in shortened:
                silence[index] = shortened[index]
            elif index in variant_pairs:
                active_seen = (
                    index in mini_seen
                    and unit.slot is not None
                    and _slot_letter(facts, unit.slot) is CanonLetter.SEEN
                )
                silence[index] = (
                    None if active_seen else LiteralSilence.VARIANT
                )
            elif index in orthographic or index in seats or index in riding_pairs:
                silence[index] = LiteralSilence.ORTHOGRAPHIC
            else:
                _unclassified(index, unit, insc)
        else:
            silence[index] = None
    return Ownership(
        owner=owner,
        presenters={s: frozenset(u) for s, u in presenters.items()},
        silence=silence,
        shortened=shortened,
        carrier_only=frozenset(
            occurrence for occurrence in shortened.values()
            if facts.occurrences[occurrence].rule is Rule.ILTIQA_SHORTENING
        ),
    )


__all__ = ["Ownership", "OwnershipError", "ownership"]
