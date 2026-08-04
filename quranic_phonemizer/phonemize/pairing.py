"""`alignment(text, grouping)` aligns glyphs and sounds with optional grouping.

Two texts and two groupings meet in one function; the `_cells_*` functions
are the only place grouping matters, and `_reach_*` the only place text does.
"""
from __future__ import annotations

from dataclasses import dataclass

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
#: Lower sorts first (length before quality). A `Decorates` reach (no fact)
#: ranks with length: the iwad and the seven alifs carry a vowel's length
#: with no canonical length fact to name it.
_OWNER_RANK = {ed.Fact.VOWEL_QUALITY: 1}

Reach = tuple[tuple[int, ed.Part, ed.Fact | None], ...]


@dataclass(frozen=True, slots=True)
class Pairing:
    glyphs: tuple[int, ...]
    sounds: tuple[int, ...]
    shares: tuple[int, ...]
    silent: tuple[int, ...]
    rules: tuple[int, ...]
    after: int | None = None


def alignment(
    assembled: Assembled, *, text: str, grouping: str
) -> tuple[Pairing, ...]:
    if text not in ("source", "recited"):
        raise ValueError(f"text must be 'source' or 'recited', got {text!r}")
    if grouping not in ("glyph", "cell"):
        raise ValueError(f"grouping must be 'glyph' or 'cell', got {grouping!r}")

    glyphs = assembled.glyphs if text == "source" else assembled.rendered
    reach = _reach_recited(assembled) if text == "recited" else _reach_source(assembled)
    included = (
        _non_structural_source(assembled) if text == "source"
        # `rendered` carries no spelling edges; its own `word` is exactly
        # this, by construction of `assemble.py`'s `_rendered_words`.
        else [i for i, g in enumerate(glyphs) if g.word is not None]
    )

    groups = (
        _cells_source(assembled, included, reach) if text == "source"
        else _cells_recited(assembled, included, reach)
    ) if grouping == "cell" else [(i,) for i in included]

    return _pairings(assembled, text, groups, reach)


def _non_structural_source(assembled: Assembled) -> list[int]:
    """A glyph takes no pairing only where it carries the `Structural` edge.
    `word` is not this law, even where it agrees."""
    structural = {s.glyph for s in assembled.spellings if isinstance(s, ed.Structural)}
    return [i for i in range(len(assembled.glyphs)) if i not in structural]


# --------------------------------------------------------------------- reach

def _reach_recited(assembled: Assembled) -> dict[int, Reach]:
    out: dict[int, Reach] = {}
    for i, glyph in enumerate(assembled.rendered):
        unit = assembled.rendered_link[i].unit
        if unit is None:
            continue
        if glyph.kind in _CONSONANT_KINDS:
            out[i] = ((unit, ed.Part.CONSONANT, None),)
        elif glyph.kind in _VOWEL_KINDS:
            out[i] = ((unit, ed.Part.VOWEL, None),)
    return out


def _reach_source(assembled: Assembled) -> dict[int, Reach]:
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

def _cells_recited(assembled: Assembled, included, reach) -> list[tuple[int, ...]]:
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


def _cells_source(assembled: Assembled, included, reach) -> list[tuple[int, ...]]:
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


# ----------------------------------------------------------------- pairings

def _sound_of_part(assembled: Assembled) -> dict[tuple[int, ed.Part], int]:
    """A part's own sound: `Hosts` or `MergedInto` share one `SoundId`, so
    either edge answers. A `Silent` part has none."""
    return {
        (a.unit, a.part): a.sound
        for a in assembled.attributions
        if isinstance(a, (ed.Hosts, ed.MergedInto))
    }


def _release_of_unit(assembled: Assembled) -> dict[int, int]:
    return {
        a.unit: a.sound for a in assembled.attributions
        if isinstance(a, ed.Hosts)
        and assembled.sounds[a.sound].kind is nd.SoundKind.QALQALA
    }


def _rule_of_part(assembled: Assembled) -> dict[tuple[int, ed.Part], frozenset]:
    out: dict[tuple[int, ed.Part], set] = {}
    for a in assembled.attributions:
        if a.by is not None:
            out.setdefault((a.unit, a.part), set()).add(a.by)
    sound_parts: dict[int, list] = {}
    for a in assembled.attributions:
        if isinstance(a, (ed.Hosts, ed.MergedInto)):
            sound_parts.setdefault(a.sound, []).append((a.unit, a.part))
    for m in assembled.modifiers:
        for key in sound_parts.get(m.sound, ()):
            out.setdefault(key, set()).add(m.by)
    return {key: frozenset(rules) for key, rules in out.items()}


def _presenting_glyphs(reach) -> dict[tuple[int, ed.Part], list]:
    """`(unit, part) -> [(glyph, fact)]`, in this text's own reading order."""
    out: dict[tuple[int, ed.Part], list] = {}
    for glyph in sorted(reach):
        for unit, part, fact in reach[glyph]:
            out.setdefault((unit, part), []).append((glyph, fact))
    return out


def _owning_glyph(part: ed.Part, candidates: list) -> int | None:
    """Pick owning glyph: length before quality, then reading order."""
    if not candidates:
        return None
    if part is ed.Part.VOWEL:
        return min(candidates, key=lambda c: (_OWNER_RANK.get(c[1], 0), c[0]))[0]
    return candidates[0][0]


def _owners(assembled: Assembled, reach) -> list[int | None]:
    """The owning glyph of every sound, `None` where no glyph of this text
    presents it -- a gap."""
    primary = {
        a.sound: (a.unit, a.part) for a in assembled.attributions
        if isinstance(a, ed.Hosts)
    }
    by_part = _presenting_glyphs(reach)
    out = []
    for index in range(len(assembled.sounds)):
        part_key = primary.get(index)
        candidates = by_part.get(part_key, []) if part_key else []
        out.append(_owning_glyph(part_key[1], candidates) if part_key else None)
    return out


def _presented_sounds(reach, glyph, sound_of_part, release_of_unit) -> set[int]:
    out: set[int] = set()
    for unit, part, _ in reach.get(glyph, ()):
        sound = sound_of_part.get((unit, part))
        if sound is not None:
            out.add(sound)
        if part is ed.Part.CONSONANT and unit in release_of_unit:
            out.add(release_of_unit[unit])
    return out


def _silent_glyphs(assembled: Assembled, text: str, reach) -> set[int]:
    if text == "recited":
        return set()
    silent_parts = {
        (a.unit, a.part) for a in assembled.attributions
        if isinstance(a, ed.Silent)
    }
    out = set(assembled.orthographic_silence)
    for glyph, pairs in reach.items():
        if any(
            (u, p) in silent_parts for u, p, fact in pairs
            if fact is not ed.Fact.CONSONANT
        ):
            out.add(glyph)
    return out


def _group_rules(assembled: Assembled, text, group, reach, rule_of_part) -> tuple[int, ...]:
    rules: set[int] = set()
    for glyph in group:
        for unit, part, _ in reach.get(glyph, ()):
            rules |= rule_of_part.get((unit, part), frozenset())
        if text == "source" and glyph in assembled.orthographic_silence:
            rules.add(assembled.orthographic_silence[glyph])
    return tuple(sorted(rules))


def _gap_anchor(sound_index: int, owner_group: list) -> int | None:
    """The nearest preceding sound some group of this text owns."""
    for index in range(sound_index - 1, -1, -1):
        if owner_group[index] is not None:
            return owner_group[index]
    return None


def _ordered_items(groups, owner_group) -> list[tuple[str, int]]:
    """Reading order over real pairings and the gaps interleaved among them,
    keyed on the owning glyph's position and, for a chain of gaps, the
    sound's own reading index."""
    min_glyph = [min(group) for group in groups]
    items = [(0, min_glyph[i], -1, "real", i) for i in range(len(groups))]
    for sound_index, group_index in enumerate(owner_group):
        if group_index is None:
            anchor = _gap_anchor(sound_index, owner_group)
            anchor_glyph = min_glyph[anchor] if anchor is not None else -1
            items.append((1, anchor_glyph, sound_index, "gap", sound_index))
    items.sort(key=lambda item: (item[1], item[0], item[2]))
    return [(kind, ref) for _, _, _, kind, ref in items]


def _pairings(assembled: Assembled, text, groups, reach) -> tuple[Pairing, ...]:
    sound_of_part = _sound_of_part(assembled)
    release_of_unit = _release_of_unit(assembled)
    rule_of_part = _rule_of_part(assembled)
    silent = _silent_glyphs(assembled, text, reach)
    primary = {
        a.sound: (a.unit, a.part) for a in assembled.attributions
        if isinstance(a, ed.Hosts)
    }

    owners = _owners(assembled, reach)
    group_of_glyph = {g: i for i, group in enumerate(groups) for g in group}
    owner_group = [group_of_glyph.get(g) if g is not None else None for g in owners]
    owned: list[list[int]] = [[] for _ in groups]
    for sound_index, group_index in enumerate(owner_group):
        if group_index is not None:
            owned[group_index].append(sound_index)

    out = []
    for position, (kind, ref) in enumerate(_ordered_items(groups, owner_group)):
        if kind == "real":
            out.append(_real_pairing(
                assembled, text, groups[ref], owned[ref], reach, sound_of_part,
                release_of_unit, rule_of_part, silent,
            ))
        else:
            rules = rule_of_part.get(primary.get(ref), frozenset())
            out.append(Pairing((), (ref,), (), (), tuple(sorted(rules)),
                               after=position - 1 if position else None))
    return tuple(out)


def _real_pairing(assembled, text, group, owned, reach, sound_of_part,
                  release_of_unit, rule_of_part, silent) -> Pairing:
    presented: set[int] = set()
    for glyph in group:
        presented |= _presented_sounds(reach, glyph, sound_of_part, release_of_unit)
    return Pairing(
        glyphs=group, sounds=tuple(sorted(owned)),
        shares=tuple(sorted(presented - set(owned))),
        silent=tuple(g for g in group if g in silent),
        rules=_group_rules(assembled, text, group, reach, rule_of_part),
    )


__all__ = ["Pairing", "alignment"]
