"""`Session` -> the public node and edge arrays.

One index space per array; every edge below names an index into it, never a
model-layer id. `pairing.py` and `respell.py` are the readers.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..model.canon import Rule, Score
from ..model.inscription import (
    Attests,
    Decorates as InscDecorates,
    Evidences,
    Inscription,
    SlotFact,
    Structural as InscStructural,
)
from ..model.performance import (
    Aspect,
    Classifies,
    Consonant,
    Hosts as PerfHosts,
    Inserted,
    MergedInto as PerfMergedInto,
    Performance,
    Recolours,
    Release,
    SetsLength,
    Silent as PerfSilent,
    Vowel,
)
from ..orthography.write import Pen
from ..render.alphabet import Alphabet
from . import edges as ed
from . import nodes as nd
from .ordering import sounds_in_order
from .recited import write_recited
from .session import Session

#: SlotFact.SAKT is not mapped; nothing evidences it.
_FACT_OF = {
    SlotFact.LETTER: ed.Fact.LETTER,
    SlotFact.ONSET: ed.Fact.CONSONANT,
    SlotFact.VOWEL_QUALITY: ed.Fact.VOWEL_QUALITY,
    SlotFact.VOWEL_LENGTH: ed.Fact.VOWEL_LENGTH,
    SlotFact.VOWEL_ABSENCE: ed.Fact.VOWEL_ABSENCE,
    SlotFact.TAJWEED_MARK: ed.Fact.TAJWEED_MARK,
}
_PART_OF = {Aspect.CONSONANT: ed.Part.CONSONANT, Aspect.VOWEL: ed.Part.VOWEL}


@dataclass(frozen=True, slots=True)
class RenderedLink:
    """Which unit and sounds a `RenderGlyph` presents. Not part of the
    public contract: `pairing.py`'s own machinery."""

    unit: int | None
    sound: int | None
    release: int | None


@dataclass(frozen=True, slots=True)
class Assembled:
    words: tuple[nd.Word, ...]
    glyphs: tuple[nd.Glyph, ...]
    rendered: tuple[nd.RenderGlyph, ...]
    units: tuple[nd.Unit, ...]
    sounds: tuple[nd.Sound, ...]
    rules: tuple[nd.RuleInstance, ...]
    spellings: tuple[ed.SpellingEdge, ...]
    attributions: tuple[ed.AttributionEdge, ...]
    modifiers: tuple[ed.ModifierEdge, ...]
    rendered_link: tuple[RenderedLink, ...]
    orthographic_silence: dict[int, int]
    """Source glyph index -> the `rules` index of the instance it shows."""
    open_vowel_units: frozenset[int]
    """Units whose vowel performs long, read off the `Performance`."""
    decoration_target: dict[int, int]
    """A `Decorates`-only glyph's unit: its own named unit, or the last unit
    a preceding glyph presented a vowel for
    when the mark's own attachment (`canon/build.py`'s bookkeeping) names a
    unit -- such as a tanween's noon -- that never itself carries a vowel."""


def _unit_indices(score: Score):
    """`unit_of_slot`, `word_of_slot` and the `Unit` array, all keyed the
    same way: position in `score.slots()` is a unit's index everywhere."""
    unit_of_slot = {slot.id: i for i, slot in enumerate(score.slots())}
    word_of_slot = {
        slot.id: w for w, word in enumerate(score.words) for slot in word.slots
    }
    units = tuple(
        nd.unit_of(word_of_slot[slot.id], slot) for slot in score.slots()
    )
    return unit_of_slot, word_of_slot, units


def assemble(
    session: Session,
    pen: Pen,
    alphabet: Alphabet,
    *,
    extra_phonemes: frozenset[str] = frozenset(),
) -> Assembled:
    score = session.score
    unit_of_slot, word_of_slot, units = _unit_indices(score)

    glyphs, glyph_of = _glyphs(session.inscription, word_of_slot, unit_of_slot)
    spellings = _spellings(session.inscription, glyph_of, unit_of_slot)

    performance = session.performance
    sound_ids = sounds_in_order(performance)
    sound_of = {sound_id: i for i, sound_id in enumerate(sound_ids)}
    by_id = dict(performance.sounds)
    sounds = tuple(
        _sound(by_id[sound_id], alphabet, extra_phonemes) for sound_id in sound_ids
    )

    occurrence_of = {o.id: i for i, o in enumerate(performance.occurrences)}
    mergers = _merger_occurrences(performance)
    rules = [
        _rule_instance(o, unit_of_slot, mergers) for o in performance.occurrences
    ]
    attributions = _attributions(performance, sound_of, unit_of_slot, occurrence_of)
    modifiers = _modifiers(performance, sound_of, occurrence_of)

    open_vowel = _open_vowel_units(attributions, sounds)
    decoration_target = _decoration_targets(glyphs, spellings)
    silence_rules, orthographic_silence = _orthographic_silence(
        glyphs, spellings, open_vowel, decoration_target, len(rules)
    )
    rules.extend(silence_rules)

    rendered, links = _rendered(
        session.score, session.inscription, performance, pen, glyph_of,
        unit_of_slot, sound_of,
    )
    words = _words(session, glyphs)

    return Assembled(
        words=words, glyphs=glyphs, rendered=rendered, units=units,
        sounds=sounds, rules=tuple(rules), spellings=spellings,
        attributions=attributions, modifiers=modifiers,
        rendered_link=links, orthographic_silence=orthographic_silence,
        open_vowel_units=open_vowel, decoration_target=decoration_target,
    )


def _glyphs(inscription: Inscription, word_of_slot, unit_of_slot):
    """Sorted by offset; the position in this array is `source_index`."""
    structural, vowel_absent = set(), set()
    unit_of_grapheme = {}
    for spelling in inscription.spellings:
        grapheme = getattr(spelling, "grapheme", None)
        if isinstance(spelling, InscStructural):
            structural.add(grapheme)
        elif isinstance(spelling, Evidences) and spelling.fact is SlotFact.VOWEL_ABSENCE:
            vowel_absent.add(grapheme)
        slot = getattr(spelling, "slot", None) or getattr(spelling, "anchor", None)
        if grapheme is not None and slot is not None:
            unit_of_grapheme.setdefault(grapheme, slot)

    ordered = sorted(inscription.graphemes, key=lambda g: g.id.offset)
    glyphs = []
    glyph_of = {}
    for index, grapheme in enumerate(ordered):
        slot = unit_of_grapheme.get(grapheme.id)
        word = (
            word_of_slot.get(slot)
            if slot is not None and grapheme.id not in structural
            else None
        )
        glyphs.append(nd.Glyph(
            word=word, char=grapheme.char,
            kind=nd.glyph_kind_of(grapheme.cls, vowel_absent=grapheme.id in vowel_absent),
            word_index=grapheme.index if word is not None else None,
            source_index=index,
        ))
        glyph_of[grapheme.id] = index
    return tuple(glyphs), glyph_of


def _spellings(inscription: Inscription, glyph_of, unit_of_slot):
    out = []
    for spelling in inscription.spellings:
        match spelling:
            case Evidences(grapheme=g, slot=s, fact=f):
                fact = _FACT_OF.get(f)
                if fact is None:
                    raise ValueError(f"{s}: unmapped spelling fact {f!r}")
                out.append(ed.Supplies(glyph_of[g], unit_of_slot[s], fact))
            case Attests(grapheme=g, anchor=s):
                out.append(ed.Witnesses(glyph_of[g], unit_of_slot[s]))
            case InscDecorates(grapheme=g, slot=s):
                out.append(ed.Decorates(glyph_of[g], unit_of_slot[s]))
            case InscStructural(grapheme=g):
                out.append(ed.Structural(glyph_of[g]))
    return tuple(out)


def _sound(sound, alphabet: Alphabet, extra_phonemes: frozenset[str]) -> nd.Sound:
    token = alphabet.token(sound, extra_phonemes=extra_phonemes)
    match sound:
        case Consonant(letter=l, geminate=g, emphatic=e, ghunnah=gh, eased=ea):
            return nd.Sound(token, nd.SoundKind.CONSONANT, letter=l,
                             geminate=g, emphatic=e, ghunnah=gh, eased=ea)
        case Vowel(quality=q, long=lg, emphatic=e):
            return nd.Sound(token, nd.SoundKind.VOWEL, quality=q, long=lg,
                             emphatic=e)
        case Release(degree=d):
            return nd.Sound(token, nd.SoundKind.QALQALA, degree=d)
    raise TypeError(f"{sound!r} is not a Sound")


def _merger_occurrences(performance: Performance) -> frozenset:
    """Occurrence ids that genuinely merge two units into one sound."""
    return frozenset(
        a.by for a in performance.attributions
        if isinstance(a, PerfMergedInto) and a.by is not None
    )


def _rule_instance(occurrence, unit_of_slot, mergers) -> nd.RuleInstance:
    """`host` is published only for a merger."""
    parts = occurrence.parts
    host = None
    if parts.host is not None and occurrence.id in mergers:
        host = unit_of_slot[parts.host]
    return nd.RuleInstance(occurrence.rule, unit_of_slot[parts.source], host)


def _attributions(performance: Performance, sound_of, unit_of_slot, occurrence_of):
    out = []
    for attribution in performance.attributions:
        by = occurrence_of.get(attribution.by) if attribution.by else None
        match attribution:
            case PerfHosts(slots=slots, aspect=a, sound=s):
                out.append(ed.Hosts(unit_of_slot[slots[0]], _PART_OF[a],
                                     sound_of[s], by))
            case Inserted(anchor=(slot, _), aspect=a, sound=s):
                out.append(ed.Hosts(unit_of_slot[slot], _PART_OF[a],
                                     sound_of[s], by))
            case PerfMergedInto(slots=slots, aspect=a, sound=s):
                out.append(ed.MergedInto(unit_of_slot[slots[0]], _PART_OF[a],
                                          sound_of[s], by))
            case PerfSilent(slots=slots, aspect=a):
                out.append(ed.Silent(unit_of_slot[slots[0]], _PART_OF[a], by))
    return tuple(out)


def _modifiers(performance: Performance, sound_of, occurrence_of):
    out = []
    for modifier in performance.modifiers:
        by = occurrence_of[modifier.by]
        match modifier:
            case Recolours(sound=s):
                out.append(ed.Recolours(sound_of[s], by))
            case SetsLength(sound=s, length=length):
                out.append(ed.SetsLength(sound_of[s], by, length))
            case Classifies(sound=s):
                out.append(ed.Classifies(sound_of[s], by))
    return tuple(out)


def _open_vowel_units(attributions, sounds) -> frozenset[int]:
    """A unit whose vowel is long in this reading.

    Read off the performed sound, never a canonical fact: the iwad and the
    seven alifs lengthen with no `Evidences(VOWEL_LENGTH)` edge at all.
    """
    return frozenset(
        a.unit for a in attributions
        if isinstance(a, ed.Hosts) and a.part is ed.Part.VOWEL
        and sounds[a.sound].kind is nd.SoundKind.VOWEL and sounds[a.sound].long
    )


_VOWEL_FACTS = (ed.Fact.VOWEL_QUALITY, ed.Fact.VOWEL_LENGTH)


def _decoration_targets(glyphs, spellings) -> dict[int, int]:
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


def _orthographic_silence(glyphs, spellings, open_vowel_units, targets,
                          rule_offset):
    """A `Decorates` glyph whose target has no open vowel to seat answers to
    no unit. `Witnesses` always sounds and is never a candidate; consecutive
    silent glyphs are one instance."""
    evidenced = {s.glyph for s in spellings if isinstance(s, ed.Supplies)}

    groups: list[list[int]] = []
    for index, glyph in enumerate(glyphs):
        silent = (
            glyph.word is not None
            and index not in evidenced
            and index in targets
            and targets[index] not in open_vowel_units
        )
        if not silent:
            continue
        if groups and groups[-1][-1] == index - 1:
            groups[-1].append(index)
        else:
            groups.append([index])

    rules = [nd.RuleInstance(Rule.ORTHOGRAPHIC_SILENCE, None, None) for _ in groups]
    lookup = {
        glyph: rule_offset + rule
        for rule, group in enumerate(groups) for glyph in group
    }
    return rules, lookup


def _words(session: Session, glyphs):
    score, boundaries, inscription = (
        session.score, session.boundaries, session.inscription
    )
    texts: list[list[str]] = [[] for _ in score.words]
    for glyph in glyphs:
        if glyph.word is not None:
            texts[glyph.word].append(glyph.char)
    return tuple(
        nd.Word(
            location=word.location, text="".join(texts[i]),
            is_started_on=boundaries.started_on(i),
            is_stopped_on=boundaries.stopped_on(i),
            sakt_after=word.sakt_after, stop_sign=inscription.advice[i],
        )
        for i, word in enumerate(score.words)
    )


def _rendered(score: Score, inscription, performance, pen: Pen, glyph_of,
             unit_of_slot, sound_of):
    written = write_recited(score, inscription, performance, pen)
    word_of = _rendered_words(written)
    counters: dict[int, int] = {}
    glyphs = []
    links = []
    for index, glyph in enumerate(written):
        word = word_of[index]
        word_index = None
        if word is not None:
            word_index = counters.get(word, 0)
            counters[word] = word_index + 1
        glyphs.append(nd.RenderGlyph(
            word=word, char=glyph.char, kind=glyph.kind, word_index=word_index,
            source_index=index,
            from_glyphs=tuple(glyph_of[g] for g in glyph.from_glyphs)))
        links.append(RenderedLink(
            unit=unit_of_slot.get(glyph.slot),
            sound=sound_of.get(glyph.sound),
            release=sound_of.get(glyph.release),
        ))
    return tuple(glyphs), tuple(links)


def _rendered_words(written):
    out = []
    current = 0
    for glyph in written:
        if glyph.kind is nd.GlyphKind.STRUCTURAL:
            out.append(None)
            current += 1
        elif glyph.kind is nd.GlyphKind.STOP_SIGN:
            out.append(None)
        else:
            out.append(current)
    return out


__all__ = ["Assembled", "RenderedLink", "assemble"]
