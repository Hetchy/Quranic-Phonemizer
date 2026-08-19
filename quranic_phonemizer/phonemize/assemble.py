"""`Session` -> the public node and edge arrays.

One index space per array; every edge below names an index into it, never a
model-layer id. `pairing.py` and `respell.py` are the readers.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

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
from .derived import (
    decoration_targets,
    open_vowel_units,
    shortened_carriers,
    silent_groups,
)
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


@dataclass(frozen=True)
class Assembled:
    """The nine published arrays and nothing else. What the projections need
    beyond them is derived here, so a document copied field by field
    projects the same as the one assembly built."""

    words: tuple[nd.Word, ...]
    glyphs: tuple[nd.Glyph, ...]
    rendered: tuple[nd.RenderGlyph, ...]
    units: tuple[nd.Unit, ...]
    sounds: tuple[nd.Sound, ...]
    rules: tuple[nd.RuleInstance, ...]
    spellings: tuple[ed.SpellingEdge, ...]
    attributions: tuple[ed.AttributionEdge, ...]
    modifiers: tuple[ed.ModifierEdge, ...]

    @cached_property
    def open_vowel_units(self) -> frozenset[int]:
        """Units whose vowel performs long."""
        return open_vowel_units(self.attributions, self.sounds)

    @cached_property
    def decoration_target(self) -> dict[int, int]:
        """A `Decorates`-only glyph's unit: its own named unit, or the last
        unit a preceding glyph presented a vowel for when the mark's own
        attachment names one that never itself carries a vowel."""
        return decoration_targets(self.glyphs, self.spellings)

    @cached_property
    def orthographic_silence(self) -> dict[int, int]:
        """Source glyph index -> the `rules` index of the instance it shows."""
        groups = silent_groups(
            self.glyphs, self.spellings, self.open_vowel_units,
            self.decoration_target,
        )
        offset = next(
            (i for i, r in enumerate(self.rules)
             if r.rule is Rule.ORTHOGRAPHIC_SILENCE),
            len(self.rules),
        )
        out = {
            glyph: offset + rule
            for rule, group in enumerate(groups) for glyph in group
        }
        out.update(
            shortened_carriers(self.spellings, self.attributions, self.modifiers)
        )
        return out


def _unit_indices(score: Score):
    """Word indices and public units in canonical slot order."""
    slots = score.slots()
    word_of_slot = tuple(
        word for word, score_word in enumerate(score.words)
        for _ in score_word.slots
    )
    units = tuple(
        nd.unit_of(word_of_slot[index], slot) for index, slot in enumerate(slots)
    )
    return word_of_slot, units


def assemble(
    session: Session,
    pen: Pen,
    alphabet: Alphabet,
    *,
    extra_phonemes: frozenset[str] = frozenset(),
) -> Assembled:
    score = session.score
    word_of_slot, units = _unit_indices(score)

    glyphs, glyph_of = _glyphs(session.inscription, word_of_slot)
    spellings = _spellings(session.inscription, glyph_of)

    performance = session.performance
    sound_ids = sounds_in_order(performance)
    sound_of = {sound_id.seq: i for i, sound_id in enumerate(sound_ids)}
    by_id = {sound_id.seq: sound for sound_id, sound in performance.sounds}
    sounds = tuple(
        _sound(by_id[sound_id.seq], alphabet, extra_phonemes)
        for sound_id in sound_ids
    )

    occurrence_of = {o.id.seq: i for i, o in enumerate(performance.occurrences)}
    mergers = _merger_occurrences(performance)
    rules = [_rule_instance(o, mergers) for o in performance.occurrences]
    attributions = _attributions(performance, sound_of, occurrence_of)
    modifiers = _modifiers(performance, sound_of, occurrence_of)

    open_vowel = open_vowel_units(attributions, sounds)
    groups = silent_groups(
        glyphs, spellings, open_vowel, decoration_targets(glyphs, spellings)
    )
    rules.extend(
        nd.RuleInstance(Rule.ORTHOGRAPHIC_SILENCE, None, None) for _ in groups
    )

    rendered = _rendered(
        session.score, session.inscription, performance, pen, glyph_of,
    )
    words = _words(session, glyphs)

    return Assembled(
        words=words, glyphs=glyphs, rendered=rendered, units=units,
        sounds=sounds, rules=tuple(rules), spellings=spellings,
        attributions=attributions, modifiers=modifiers,
    )


def _glyphs(inscription: Inscription, word_of_slot):
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
            word_of_slot[slot.ordinal]
            if slot is not None and grapheme.id not in structural
            else None
        )
        glyphs.append(nd.Glyph(
            word=word, char=grapheme.char,
            kind=nd.glyph_kind_of(
                grapheme.cls,
                vowel_absent=grapheme.id in vowel_absent,
                structural=grapheme.id in structural,
            ),
            word_index=grapheme.index if word is not None else None,
            source_index=index,
        ))
        glyph_of[grapheme.id] = index
    return tuple(glyphs), glyph_of


def _spellings(inscription: Inscription, glyph_of):
    out = []
    for spelling in inscription.spellings:
        match spelling:
            case Evidences(grapheme=g, slot=s, fact=f):
                fact = _FACT_OF.get(f)
                if fact is None:
                    raise ValueError(f"{s}: unmapped spelling fact {f!r}")
                out.append(ed.Supplies(glyph_of[g], s.ordinal, fact))
            case Attests(grapheme=g, anchor=s):
                out.append(ed.Witnesses(glyph_of[g], s.ordinal))
            case InscDecorates(grapheme=g, slot=s):
                out.append(ed.Decorates(glyph_of[g], s.ordinal))
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
        a.by.seq for a in performance.attributions
        if isinstance(a, PerfMergedInto)
    )


def _rule_instance(occurrence, mergers) -> nd.RuleInstance:
    """`host` is published only for a merger."""
    parts = occurrence.parts
    host = None
    if parts.host is not None and occurrence.id.seq in mergers:
        host = parts.host.ordinal
    return nd.RuleInstance(occurrence.rule, parts.source.ordinal, host)


def _attributions(performance: Performance, sound_of, occurrence_of):
    out = []
    for attribution in performance.attributions:
        by = occurrence_of.get(attribution.by.seq) if attribution.by else None
        match attribution:
            case PerfHosts(slots=slots, aspect=a, sound=s):
                out.append(ed.Hosts(slots[0].ordinal, _PART_OF[a],
                                     sound_of[s.seq], by))
            case Inserted(anchor=(slot, _), aspect=a, sound=s):
                out.append(ed.Hosts(slot.ordinal, _PART_OF[a],
                                     sound_of[s.seq], by))
            case PerfMergedInto(slots=slots, aspect=a, sound=s):
                out.append(ed.MergedInto(slots[0].ordinal, _PART_OF[a],
                                          sound_of[s.seq], by))
            case PerfSilent(slots=slots, aspect=a):
                out.append(ed.Silent(slots[0].ordinal, _PART_OF[a], by))
    return tuple(out)


def _modifiers(performance: Performance, sound_of, occurrence_of):
    out = []
    for modifier in performance.modifiers:
        by = occurrence_of[modifier.by.seq]
        match modifier:
            case Recolours(sound=s):
                out.append(ed.Recolours(sound_of[s.seq], by))
            case SetsLength(sound=s, length=length):
                out.append(ed.SetsLength(sound_of[s.seq], by, length))
            case Classifies(sound=s):
                out.append(ed.Classifies(sound_of[s.seq], by))
    return tuple(out)


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


def _rendered(score: Score, inscription, performance, pen: Pen, glyph_of):
    written = write_recited(score, inscription, performance, pen)
    word_of = _rendered_words(written)
    counters: dict[int, int] = {}
    glyphs = []
    for index, glyph in enumerate(written):
        word = word_of[index]
        word_index = None
        if word is not None:
            word_index = counters.get(word, 0)
            counters[word] = word_index + 1
        glyphs.append(nd.RenderGlyph(
            word=word, char=glyph.char, kind=glyph.kind, word_index=word_index,
            source_index=index,
            from_glyphs=tuple(glyph_of[g] for g in glyph.from_glyphs),
            unit=glyph.slot.ordinal if glyph.slot is not None else None))
    return tuple(glyphs)


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


__all__ = ["Assembled", "assemble"]
