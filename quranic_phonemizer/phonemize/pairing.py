"""`alignment(text, grouping)` aligns glyphs and sounds with optional grouping.

Two texts and two groupings meet in one function; `reach.py` owns both the
reaching and the grouping, and everything here reads a reach.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import edges as ed
from . import nodes as nd
from . import reach as rh
from .assemble import Assembled

#: Lower sorts first (length before quality). A `Decorates` reach (no fact)
#: ranks with length: the iwad and the seven alifs carry a vowel's length
#: with no canonical length fact to name it.
_OWNER_RANK = {ed.Fact.VOWEL_QUALITY: 1}



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
    reach = rh.reach_recited(assembled) if text == "recited" else rh.reach_source(assembled)
    included = (
        _non_structural_source(assembled) if text == "source"
        # `rendered` carries no spelling edges; its own `word` is exactly
        # this, by construction of `assemble.py`'s `_rendered_words`.
        else [i for i, g in enumerate(glyphs) if g.word is not None]
    )

    groups = (
        rh.cells_source(assembled, included, reach) if text == "source"
        else rh.cells_recited(assembled, included, reach)
    ) if grouping == "cell" else [(i,) for i in included]

    return _pairings(assembled, text, groups, reach)


def _non_structural_source(assembled: Assembled) -> list[int]:
    """A glyph takes no pairing only where it carries the `Structural` edge.
    `word` is not this law, even where it agrees."""
    structural = {s.glyph for s in assembled.spellings if isinstance(s, ed.Structural)}
    return [i for i in range(len(assembled.glyphs)) if i not in structural]


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


def _presenting_glyphs(reach, mute: frozenset[int]) -> dict[tuple[int, ed.Part], list]:
    """`(unit, part) -> [(glyph, fact)]`, in this text's own reading order.

    A muted glyph keeps its reach, which is what seats it in a cell, and is
    left out here, which is what stops it presenting.
    """
    out: dict[tuple[int, ed.Part], list] = {}
    for glyph in sorted(reach):
        if glyph in mute:
            continue
        for unit, part, fact in reach[glyph]:
            out.setdefault((unit, part), []).append((glyph, fact))
    return out


def _mute(assembled: Assembled, text: str) -> frozenset[int]:
    """Glyphs a rule silenced. They keep their reach, which is what seats
    them in their letter's cell, and present nothing."""
    if text != "source":
        return frozenset()
    return frozenset(assembled.orthographic_silence)


def _seats(assembled: Assembled, text: str) -> frozenset[int]:
    """Recitation writes no seat, so the recited text has none."""
    if text != "source":
        return frozenset()
    return frozenset(
        i for i, glyph in enumerate(assembled.glyphs)
        if glyph.kind is nd.GlyphKind.TATWEEL
    )


def _owning_glyph(part: ed.Part, candidates: list, seats: frozenset[int]) -> int | None:
    """Pick owning glyph: length before quality, then reading order. A seat
    supplies nothing, so it sorts after every glyph that does."""
    if not candidates:
        return None
    if part is ed.Part.VOWEL:
        return min(
            candidates,
            key=lambda c: (c[0] in seats, _OWNER_RANK.get(c[1], 0), c[0]),
        )[0]
    return min(candidates, key=lambda c: (c[0] in seats, c[0]))[0]


def _owners(assembled: Assembled, reach, seats: frozenset[int],
            mute: frozenset[int]) -> list[int | None]:
    """The owning glyph of every sound, `None` where no glyph of this text
    presents it -- a gap."""
    primary = {
        a.sound: (a.unit, a.part) for a in assembled.attributions
        if isinstance(a, ed.Hosts)
    }
    by_part = _presenting_glyphs(reach, mute)
    out = []
    for index in range(len(assembled.sounds)):
        part_key = primary.get(index)
        candidates = by_part.get(part_key, []) if part_key else []
        out.append(
            _owning_glyph(part_key[1], candidates, seats) if part_key else None
        )
    return out


def _presented_sounds(assembled, reach, glyph, sound_of_part, release_of_unit,
                      supplied: frozenset[int]) -> set[int]:
    out: set[int] = set()
    for entry in reach.get(glyph, ()):
        unit, part, _ = entry
        if not rh.presents(assembled, glyph, entry, supplied):
            continue
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


def _group_rules(assembled: Assembled, text, group, reach, rule_of_part,
                 supplied: frozenset[int]) -> tuple[int, ...]:
    rules: set[int] = set()
    for glyph in group:
        for entry in reach.get(glyph, ()):
            if not rh.presents(assembled, glyph, entry, supplied):
                continue
            rules |= rule_of_part.get((entry[0], entry[1]), frozenset())
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

    mute = _mute(assembled, text)
    supplied = rh.supplied_lengths(assembled) if text == "source" else frozenset()
    owners = _owners(assembled, reach, _seats(assembled, text), mute)
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
                release_of_unit, rule_of_part, silent, mute, supplied,
            ))
        else:
            rules = rule_of_part.get(primary.get(ref), frozenset())
            out.append(Pairing((), (ref,), (), (), tuple(sorted(rules)),
                               after=position - 1 if position else None))
    return tuple(out)


def _real_pairing(assembled, text, group, owned, reach, sound_of_part,
                  release_of_unit, rule_of_part, silent, mute, supplied) -> Pairing:
    presented: set[int] = set()
    for glyph in group:
        if glyph in mute:
            continue
        presented |= _presented_sounds(
            assembled, reach, glyph, sound_of_part, release_of_unit, supplied
        )
    return Pairing(
        glyphs=group, sounds=tuple(sorted(owned)),
        shares=tuple(sorted(presented - set(owned))),
        silent=tuple(g for g in group if g in silent),
        rules=_group_rules(assembled, text, group, reach, rule_of_part, supplied),
    )


__all__ = ["Pairing", "alignment"]
