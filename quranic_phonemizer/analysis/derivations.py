"""What the inscription tier derives beyond the raw source facts.

Each reads only native facts: the performance tier's sounds and edges, and
the inscription tier's glyphs and spellings.
"""
from __future__ import annotations

from ..model.address import SlotId
from ..model.inscription import GlyphKind, SlotFact
from ..model.performance import Aspect, Length, Vowel
from .attributions import Insertion, Relengthened
from .facts import AnalysisFacts
from .inscription import Decorated, InscriptionFacts, Supplied

_VOWEL_FACTS = (SlotFact.VOWEL_QUALITY, SlotFact.VOWEL_LENGTH)

#: Kinds that write a letter or a silence rather than seating a vowel mark.
#: One decorating a length an earlier glyph already wrote is rasm the reading
#: spells without -- the alif of `كَفَرُوا۟` beside its waw. A tatweel or a madd
#: sign is not: it is part of how the vowel is written.
_RASM_KINDS = frozenset({GlyphKind.BASE, GlyphKind.SILENCE_SIGN})


def _slot_of(attribution) -> SlotId:
    if isinstance(attribution, Insertion):
        return attribution.anchor[0]
    return attribution.slots[0]


def _vowel_hosts(facts: AnalysisFacts):
    for attribution in (*facts.hosts, *facts.insertions):
        if attribution.aspect is Aspect.VOWEL:
            yield attribution


def open_vowel_units(facts: AnalysisFacts) -> frozenset[SlotId]:
    """A unit whose vowel is long in this reading, read off the performed
    sound: the iwad and the seven alifs lengthen with no length edge."""
    return frozenset(
        _slot_of(a) for a in _vowel_hosts(facts)
        if isinstance(facts.sounds[a.sound].value, Vowel)
        and facts.sounds[a.sound].value.long
    )


def decoration_targets(inscription: InscriptionFacts) -> dict[int, SlotId]:
    """A decorating glyph's own unit, or -- when that unit never itself hosts
    a vowel, as a tanween's noon does not -- the last unit some glyph
    presented a vowel for."""
    vowel_fact_slot = {
        s.glyph: s.slot for s in inscription.spellings
        if isinstance(s, Supplied) and s.fact in _VOWEL_FACTS
    }
    vowel_bearing = frozenset(vowel_fact_slot.values())
    decorated = {
        s.glyph: s.slot for s in inscription.spellings if isinstance(s, Decorated)
    }

    out: dict[int, SlotId] = {}
    last_vowel_slot: SlotId | None = None
    for index in range(len(inscription.glyphs)):
        if index in vowel_fact_slot:
            last_vowel_slot = vowel_fact_slot[index]
        if index not in decorated:
            continue
        nominal = decorated[index]
        if nominal in vowel_bearing or last_vowel_slot is None:
            out[index] = nominal
        else:
            out[index] = last_vowel_slot
    return out


def _spelt_lengths(inscription: InscriptionFacts) -> dict[SlotId, int]:
    """Unit -> the earliest letter that writes its vowel length outright. A
    seat draws no letter, so the yaa of `إِبْرَٰهِـۧمَ` is not rasm behind it."""
    out: dict[SlotId, int] = {}
    for s in inscription.spellings:
        if not isinstance(s, Supplied) or s.fact is not SlotFact.VOWEL_LENGTH:
            continue
        if inscription.glyphs[s.glyph].kind is GlyphKind.TATWEEL:
            continue
        out[s.slot] = min(out.get(s.slot, s.glyph), s.glyph)
    return out


def _writes_nothing(glyph, index, target, open_vowels, spelt) -> bool:
    if glyph.kind is GlyphKind.SILENCE_SIGN:
        return True
    if target not in open_vowels:
        return True
    written = spelt.get(target)
    return written is not None and written < index and glyph.kind in _RASM_KINDS


def silent_groups(
    inscription: InscriptionFacts,
    open_vowels: frozenset[SlotId],
    targets: dict[int, SlotId],
) -> list[list[int]]:
    """A decorating glyph that writes nothing answers to no unit; consecutive
    silent glyphs are one instance."""
    evidenced = {s.glyph for s in inscription.spellings if isinstance(s, Supplied)}
    spelt = _spelt_lengths(inscription)

    groups: list[list[int]] = []
    for index, glyph in enumerate(inscription.glyphs):
        if glyph.word is None or index in evidenced or index not in targets:
            continue
        if not _writes_nothing(glyph, index, targets[index], open_vowels, spelt):
            continue
        if groups and groups[-1][-1] == index - 1:
            groups[-1].append(index)
        else:
            groups.append([index])
    return groups


def shortened_carriers(
    facts: AnalysisFacts, inscription: InscriptionFacts
) -> dict[int, int]:
    """A length carrier whose length a rule took back sounds nothing: the
    vowel it was written for performs short without it."""
    shortened = {
        m.sound: m.by for m in facts.modifiers
        if isinstance(m, Relengthened) and m.length is Length.SHORT
    }
    vowel_of_slot = {_slot_of(a): a.sound for a in _vowel_hosts(facts)}
    return {
        s.glyph: shortened[vowel_of_slot[s.slot]]
        for s in inscription.spellings
        if isinstance(s, Supplied)
        and s.fact is SlotFact.VOWEL_LENGTH
        and vowel_of_slot.get(s.slot) in shortened
    }


__all__ = [
    "decoration_targets",
    "open_vowel_units",
    "shortened_carriers",
    "silent_groups",
]
