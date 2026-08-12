"""How a glyph reaches a unit, and how glyphs group into cells.

`reach_*` is the only place the text matters; `cells_*` the only place the
grouping does. Everything downstream reads a reach and never a spelling edge.
"""
from __future__ import annotations

from . import edges as ed
from . import nodes as nd
from .assemble import Assembled

#: A recited glyph's reach: the (part, fact) pairing the consonant side and
#: the vowel side of a unit render as. `GlyphKind`s absent here (`tanween`,
#: `small_vowel`, `structural`, `stop_sign`) never occur in `rendered`.
_CONSONANT_KINDS = frozenset({nd.GlyphKind.BASE, nd.GlyphKind.SHADDA})
_VOWEL_KINDS = frozenset({
    nd.GlyphKind.HARAKA, nd.GlyphKind.SUKUN, nd.GlyphKind.VOWEL_LETTER,
    nd.GlyphKind.MADD_SIGN,
})

_VOWEL_FACT = {ed.Fact.VOWEL_QUALITY, ed.Fact.VOWEL_LENGTH, ed.Fact.VOWEL_ABSENCE}


Reach = tuple[tuple[int, ed.Part, ed.Fact | None], ...]
# --------------------------------------------------------------------- reach

def reach_recited(assembled: Assembled) -> dict[int, Reach]:
    out: dict[int, Reach] = {}
    for i, glyph in enumerate(assembled.rendered):
        unit = glyph.unit
        if unit is None:
            continue
        if glyph.kind in _CONSONANT_KINDS:
            out[i] = ((unit, ed.Part.CONSONANT, None),)
        elif glyph.kind in _VOWEL_KINDS:
            out[i] = ((unit, ed.Part.VOWEL, None),)
    return out


def reach_source(assembled: Assembled) -> dict[int, Reach]:
    out: dict[int, list] = {}
    for s in assembled.spellings:
        match s:
            case ed.Supplies(glyph=g, unit=u, fact=f) if f in _VOWEL_FACT:
                out.setdefault(g, []).append((u, ed.Part.VOWEL, f))
            case ed.Supplies(glyph=g, unit=u, fact=f):
                out.setdefault(g, []).append((u, ed.Part.CONSONANT, f))
            case ed.Witnesses(glyph=g, unit=u):
                out.setdefault(g, []).append((u, ed.Part.CONSONANT, None))
            case ed.Decorates(glyph=g):
                target = assembled.decoration_target.get(g)
                if target is not None and target in assembled.open_vowel_units:
                    out.setdefault(g, []).append((target, ed.Part.VOWEL, None))
    return {g: tuple(pairs) for g, pairs in out.items()}


# -------------------------------------------------------------------- cells

def cells_recited(assembled: Assembled, included, reach) -> list[tuple[int, ...]]:
    """A recited haraka is always its unit's whole carrier when the vowel
    is long, so an open unit's own vowel glyph never joins the consonant."""
    groups: list[list[int]] = []
    vowel_cell: dict[int, int] = {}
    consonant_cell: dict[int, int] = {}
    for i in included:
        unit, part, _ = reach[i][0]
        cells = (
            vowel_cell if part is ed.Part.VOWEL and unit in assembled.open_vowel_units
            else consonant_cell
        )
        group = cells.get(unit)
        if group is None:
            group = len(groups)
            groups.append([])
            cells[unit] = group
        groups[group].append(i)
        if part is ed.Part.CONSONANT:
            consonant_cell.setdefault(unit, group)
    return [tuple(g) for g in groups]


def _carrier_units(reach) -> frozenset[int]:
    """Units some glyph presents a vowel for otherwise than by quality: a
    dedicated length mark, or a `Decorates` glyph. A bare quality fact never
    qualifies alone -- there is no carrier to part it from."""
    return frozenset(
        unit for pairs in reach.values() for unit, part, fact in pairs
        if part is ed.Part.VOWEL and fact is not ed.Fact.VOWEL_QUALITY
    )


def cells_source(assembled: Assembled, included, reach) -> list[tuple[int, ...]]:
    """Group glyphs by unit and vowel/consonant; chain decorations together."""
    carriers = _carrier_units(reach)
    groups: list[list[int]] = []
    vowel_cell: dict[int, int] = {}
    consonant_cell: dict[int, int] = {}
    chain_target = None
    for i in included:
        pairs = reach.get(i, ())
        if not pairs:
            target = assembled.decoration_target.get(i)
            if groups and chain_target is not None and chain_target == target:
                groups[-1].append(i)
            else:
                groups.append([i])
            chain_target = target
            continue
        chain_target = None
        unit, part, _ = pairs[0]
        open_vowel = (
            part is ed.Part.VOWEL and unit in assembled.open_vowel_units
            and unit in carriers
        )
        cells = vowel_cell if open_vowel else consonant_cell
        group = cells.get(unit)
        if group is None:
            group = len(groups)
            groups.append([])
            cells[unit] = group
        groups[group].append(i)
        for u, p, _ in pairs:
            if p is ed.Part.CONSONANT:
                consonant_cell.setdefault(u, group)
    return [tuple(g) for g in groups]



def supplied_lengths(assembled: Assembled) -> frozenset[int]:
    """Units whose vowel length a glyph writes outright. A `Decorates` glyph
    onto one of these is rasm the reading already spells: the alif of
    `كَفَرُوا۟` beside the waw that carries the `u:`."""
    return frozenset(
        s.unit for s in assembled.spellings
        if isinstance(s, ed.Supplies) and s.fact is ed.Fact.VOWEL_LENGTH
    )


#: Glyphs that write a letter or a silence rather than seating a vowel mark.
#: One of these decorating a unit whose length is already supplied is rasm --
#: the alif of `كَفَرُوا۟` beside its waw. A tatweel or a madd sign is not:
#: it is part of how the vowel is written, and presents it.
_RASM_KINDS = frozenset({nd.GlyphKind.BASE, nd.GlyphKind.SILENCE_SIGN})


def presents(assembled: Assembled, glyph: int, entry,
              supplied: frozenset[int]) -> bool:
    """Does this reach entry present its part's sound, or only decorate it?"""
    unit, part, fact = entry
    if fact is not None or part is not ed.Part.VOWEL or unit not in supplied:
        return True
    return assembled.glyphs[glyph].kind not in _RASM_KINDS


__all__ = [
    "Reach",
    "cells_recited",
    "cells_source",
    "presents",
    "reach_recited",
    "reach_source",
    "supplied_lengths",
]
