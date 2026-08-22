"""The normative tokenization: which scalars open a LetterUnit and which fold.

A base letter, a carrier, and each haraka, sukun and tanween is its own unit;
every other mark folds into the unit whose fact it states.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..model.address import SlotId
from ..model.inscription import SlotFact
from ..model.inscription import GlyphKind
from .inscription import (
    Decorated,
    InscriptionFacts,
    Supplied,
    Witnessed,
    sakt_seen_glyphs,
)

from .source_dtos import LetterUnitKind

#: Kinds a scalar writes at the vowel position or as a letter of its own.
_OPENING_KINDS = {
    GlyphKind.BASE: LetterUnitKind.LETTER,
    GlyphKind.VOWEL_LETTER: LetterUnitKind.LETTER,
    GlyphKind.SMALL_VOWEL: LetterUnitKind.LETTER,
    GlyphKind.HARAKA: LetterUnitKind.HARAKA,
    GlyphKind.SUKUN: LetterUnitKind.SUKUN,
    GlyphKind.TANWEEN: LetterUnitKind.TANWEEN,
}


@dataclass(slots=True)
class UnitDraft:
    anchor: int
    word: int
    slot: SlotId | None
    kind: LetterUnitKind
    glyphs: list[int] = field(default_factory=list)
    written_on_anchor: int | None = None


@dataclass(frozen=True, slots=True)
class Roles:
    letter: dict[SlotId, int]
    vowel: dict[SlotId, int]
    carrier: dict[SlotId, int]


@dataclass(frozen=True, slots=True)
class Tokenization:
    """The units in anchor order, with the maps ownership and placements read:
    every lexical glyph's unit, and each slot's letter, vowel and carrier."""

    units: tuple[UnitDraft, ...]
    unit_of_anchor: dict[int, int]
    unit_of_glyph: dict[int, int]
    roles: Roles
    sakt_seen_glyphs: frozenset[int]


def _facts_by_glyph(insc: InscriptionFacts) -> dict[int, set[SlotFact]]:
    out: dict[int, set[SlotFact]] = {}
    for edge in insc.spellings:
        if isinstance(edge, Supplied):
            out.setdefault(edge.glyph, set()).add(edge.fact)
    return out


def _seen_marks(insc: InscriptionFacts) -> frozenset[int]:
    """A decorated annotation glyph is a seen mark: the ishmam and tashil marks
    evidence a fact instead, and the maddah and silence signs are other kinds."""
    return frozenset(
        e.glyph for e in insc.spellings
        if isinstance(e, Decorated)
        and insc.glyphs[e.glyph].kind is GlyphKind.TAJWEED_MARK
    )


def _opens(glyph, seen_marks: frozenset[int], sakt_words: frozenset[int]) -> bool:
    if glyph.source_index in seen_marks:
        return glyph.word not in sakt_words
    return glyph.kind in _OPENING_KINDS


def _kind_of(glyph, seen_marks: frozenset[int]) -> LetterUnitKind:
    if glyph.source_index in seen_marks:
        return LetterUnitKind.LETTER
    return _OPENING_KINDS[glyph.kind]


def _draft_openers(insc, seen_marks, sakt_words):
    """One draft per opening glyph, in source order."""
    drafts: list[UnitDraft] = []
    unit_of_anchor: dict[int, int] = {}
    for glyph in insc.glyphs:
        if glyph.word is None or not _opens(glyph, seen_marks, sakt_words):
            continue
        unit_of_anchor[glyph.source_index] = len(drafts)
        drafts.append(UnitDraft(
            anchor=glyph.source_index,
            word=glyph.word,
            slot=insc.slot_of.get(glyph.source_index),
            kind=_kind_of(glyph, seen_marks),
            glyphs=[glyph.source_index],
        ))
    return drafts, unit_of_anchor


_VOWEL_POSITION_FACTS = (SlotFact.VOWEL_QUALITY, SlotFact.VOWEL_ABSENCE)


def _slot_roles(insc, drafts, unit_of_anchor) -> Roles:
    """Each slot's letter, vowel-position and length-carrier unit indices, read
    off the opener edges: a tanween supplies the vowel of the seat it rides and
    the letter of the noon it mints, so its unit answers for both slots."""
    letter: dict[SlotId, int] = {}
    vowel: dict[SlotId, int] = {}
    carrier: dict[SlotId, int] = {}
    for edge in insc.spellings:
        if not isinstance(edge, Supplied):
            continue
        unit = unit_of_anchor.get(edge.glyph)
        if unit is None:
            continue
        if edge.fact is SlotFact.LETTER:
            letter.setdefault(edge.slot, unit)
        elif edge.fact in _VOWEL_POSITION_FACTS:
            vowel.setdefault(edge.slot, unit)
    _carriers(insc, drafts, unit_of_anchor, carrier)
    return Roles(letter, vowel, carrier)


def _carriers(insc, drafts, unit_of_anchor, carrier):
    """The unit that carries a slot's length: the glyph that supplies it when
    that glyph opens a unit, else the base opener the mark decorates."""
    for edge in insc.spellings:
        if not (isinstance(edge, Supplied) and edge.fact is SlotFact.VOWEL_LENGTH):
            continue
        if edge.glyph in unit_of_anchor:
            carrier.setdefault(edge.slot, unit_of_anchor[edge.glyph])
            continue
        base = _nearest_opener(
            drafts, unit_of_anchor, edge.glyph, edge.slot, before=True
        )
        if base is not None:
            carrier.setdefault(edge.slot, base)


def _nearest_opener(drafts, unit_of_anchor, glyph_index, slot, *, before):
    """The opener nearest `glyph_index` in the same slot, on the named side."""
    best: int | None = None
    for anchor in unit_of_anchor:
        if drafts[unit_of_anchor[anchor]].slot != slot:
            continue
        if (anchor < glyph_index) != before:
            continue
        if best is None or abs(anchor - glyph_index) < abs(best - glyph_index):
            best = anchor
    return unit_of_anchor[best] if best is not None else None


def _fold_target(index, slot, facts, witnessed, drafts, unit_of_anchor, roles):
    """The unit a non-opening glyph joins. A gemination witness or an onset
    joins the base letter; every other mark joins the opener it sits on, or the
    unit answering its slot where a muqattaat name is one glyph."""
    consonant = index in witnessed or SlotFact.ONSET in facts.get(index, set())
    if consonant and slot in roles.letter:
        return roles.letter[slot]
    for before in (True, False):
        opener = _nearest_opener(drafts, unit_of_anchor, index, slot, before=before)
        if opener is not None:
            return opener
    for table in (roles.carrier, roles.vowel, roles.letter):
        if slot in table:
            return table[slot]
    return None


def tokenize(insc: InscriptionFacts, sakt_words: frozenset[int]) -> Tokenization:
    facts = _facts_by_glyph(insc)
    seen_marks = _seen_marks(insc)
    witnessed = frozenset(
        e.glyph for e in insc.spellings if isinstance(e, Witnessed)
    )
    sakt_seen = sakt_seen_glyphs(insc, sakt_words)
    drafts, unit_of_anchor = _draft_openers(insc, seen_marks, sakt_words)
    roles = _slot_roles(insc, drafts, unit_of_anchor)

    unit_of_glyph = dict(unit_of_anchor)
    for glyph in insc.glyphs:
        index = glyph.source_index
        if glyph.word is None or index in unit_of_anchor or index in sakt_seen:
            continue
        target = _fold_target(
            index, insc.slot_of.get(index), facts, witnessed,
            drafts, unit_of_anchor, roles,
        )
        if target is not None:
            drafts[target].glyphs.append(index)
            unit_of_glyph[index] = target

    _attach_seen(insc, seen_marks, sakt_seen, drafts, unit_of_anchor, roles.letter)
    for draft in drafts:
        draft.glyphs.sort()
    return Tokenization(
        tuple(drafts), unit_of_anchor, unit_of_glyph, roles, sakt_seen,
    )


def _attach_seen(insc, seen_marks, sakt_seen, drafts, unit_of_anchor, letter):
    """A written mini seen rides the base letter it pairs with."""
    for glyph in seen_marks:
        if glyph in sakt_seen:
            continue
        unit = unit_of_anchor.get(glyph)
        slot = insc.slot_of.get(glyph)
        if unit is not None and slot in letter and letter[slot] != unit:
            drafts[unit].written_on_anchor = drafts[letter[slot]].anchor


__all__ = ["Tokenization", "UnitDraft", "tokenize"]
