"""What the projections need beyond the nine published arrays.

Every function here reads only those arrays, which is what lets a document
copied member by member project the same as the one assembly built.
"""
from __future__ import annotations

from ..model.performance import Length
from . import edges as ed
from . import nodes as nd

_VOWEL_FACTS = (ed.Fact.VOWEL_QUALITY, ed.Fact.VOWEL_LENGTH)


def open_vowel_units(attributions, sounds) -> frozenset[int]:
    """A unit whose vowel is long in this reading.

    Read off the performed sound, never a canonical fact: the iwad and the
    seven alifs lengthen with no `Evidences(VOWEL_LENGTH)` edge at all.
    """
    return frozenset(
        a.unit for a in attributions
        if isinstance(a, ed.Hosts) and a.part is ed.Part.VOWEL
        and sounds[a.sound].kind is nd.SoundKind.VOWEL and sounds[a.sound].long
    )


def decoration_targets(glyphs, spellings) -> dict[int, int]:
    """A `Decorates` glyph's own unit, or -- when that unit never itself
    hosts a vowel, as a tanween's noon does not -- the last unit some fact
    glyph presented a vowel for."""
    vowel_fact_unit = {
        s.glyph: s.unit for s in spellings
        if isinstance(s, ed.Supplies) and s.fact in _VOWEL_FACTS
    }
    vowel_bearing_units = frozenset(vowel_fact_unit.values())
    decorated_unit = {
        s.glyph: s.unit for s in spellings if isinstance(s, ed.Decorates)
    }

    out: dict[int, int] = {}
    last_vowel_unit: int | None = None
    for index in range(len(glyphs)):
        if index in vowel_fact_unit:
            last_vowel_unit = vowel_fact_unit[index]
        if index not in decorated_unit:
            continue
        nominal = decorated_unit[index]
        if nominal in vowel_bearing_units or last_vowel_unit is None:
            out[index] = nominal
        else:
            out[index] = last_vowel_unit
    return out


#: Glyphs that write a letter or a silence rather than seating a vowel mark.
#: One of these decorating a length some earlier glyph already wrote is rasm
#: the reading spells without it -- the alif of `كَفَرُوا۟` beside its waw. A
#: tatweel or a madd sign is not: it is part of how the vowel is written.
_RASM_KINDS = frozenset({nd.GlyphKind.BASE, nd.GlyphKind.SILENCE_SIGN})


def _spelt_lengths(glyphs, spellings) -> dict[int, int]:
    """Unit -> the earliest letter that writes its vowel length outright. A
    seat draws no letter, so the yaa of `إِبْرَٰهِـۧمَ` is not rasm behind it."""
    out: dict[int, int] = {}
    for s in spellings:
        if not isinstance(s, ed.Supplies) or s.fact is not ed.Fact.VOWEL_LENGTH:
            continue
        if glyphs[s.glyph].kind is nd.GlyphKind.TATWEEL:
            continue
        out[s.unit] = min(out.get(s.unit, s.glyph), s.glyph)
    return out


def _writes_nothing(glyph, index, target, open_vowels, spelt) -> bool:
    """Either the target seats no long vowel, or a glyph before this one
    already wrote that length and this is the rasm beside it."""
    if target not in open_vowels:
        return True
    written = spelt.get(target)
    return written is not None and written < index and glyph.kind in _RASM_KINDS


def silent_groups(glyphs, spellings, open_vowels, targets) -> list[list[int]]:
    """A `Decorates` glyph that writes nothing answers to no unit.
    `Witnesses` always sounds and is never a candidate; consecutive silent
    glyphs are one instance."""
    evidenced = {s.glyph for s in spellings if isinstance(s, ed.Supplies)}
    spelt = _spelt_lengths(glyphs, spellings)

    groups: list[list[int]] = []
    for index, glyph in enumerate(glyphs):
        if glyph.word is None or index in evidenced or index not in targets:
            continue
        if not _writes_nothing(
            glyph, index, targets[index], open_vowels, spelt
        ):
            continue
        if groups and groups[-1][-1] == index - 1:
            groups[-1].append(index)
        else:
            groups.append([index])
    return groups


def shortened_carriers(spellings, attributions, modifiers) -> dict[int, int]:
    """A length carrier whose length a rule took back shows that rule and
    sounds nothing: the vowel it was written for performs short without it."""
    shortened = {
        m.sound: m.by for m in modifiers
        if isinstance(m, ed.SetsLength) and m.length is Length.SHORT
    }
    vowel_of_unit = {
        a.unit: a.sound for a in attributions
        if isinstance(a, ed.Hosts) and a.part is ed.Part.VOWEL
    }
    return {
        s.glyph: shortened[vowel_of_unit[s.unit]]
        for s in spellings
        if isinstance(s, ed.Supplies)
        and s.fact is ed.Fact.VOWEL_LENGTH
        and vowel_of_unit.get(s.unit) in shortened
    }


__all__ = [
    "decoration_targets",
    "open_vowel_units",
    "shortened_carriers",
    "silent_groups",
]
