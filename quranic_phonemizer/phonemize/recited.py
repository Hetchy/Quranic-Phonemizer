"""The recited text: what a `Performance` says, not what the Score allows.

`orthography/write.py` spells a Score's joined form and cannot see a
`BoundaryPlan`; this walks the `Performance` a plan already produced.
"""
from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass

from ..model.address import SlotId, SoundId
from ..model.canon import (
    HAMZA_WASL_START,
    CanonLetter,
    Rule,
    Score,
    ScoreWord,
    SlotOrigin,
)
from ..model.inscription import (
    VOWEL_FACTS,
    Grapheme,
    GraphemeClass,
    Inscription,
    SlotFact,
)
from ..model.performance import (
    Aspect,
    Consonant,
    Hosts,
    MergedInto,
    Performance,
    Release,
    Silent,
    Vowel,
    effect_targets,
)
from ..orthography.write import MADD, Pen, WriteError
from . import nodes as nd

#: A tanween noon these rules realize is left bare -- no sukun mark -- because
#: bareness is what signals the assimilation; every other realization keeps
#: the mark.
_BARE_TANWEEN_NOON = frozenset({Rule.IKHFAA, Rule.IQLAB})

#: A hamza wasl started on is the hamza its vowel calls for, never the bare
#: letter or the seat the rasm wrote.
_WASL_HAMZA_SHAPE = {"a": "أ", "u": "أ", "i": "إ"}

#: `SlotFact`s a source glyph may supply for the consonant part, as opposed
#: to `VOWEL_FACTS` for the vowel part -- `_source_graphemes` keys on the
#: fact itself so a base letter and a shadda mark, once split into their own
#: render glyphs, each cite only the source glyph that actually evidences
#: them rather than sharing one merged list.
_CONSONANT_FACTS = frozenset({SlotFact.LETTER, SlotFact.ONSET})


@dataclass(frozen=True, slots=True)
class RenderGlyph:
    """One scalar of the recited text. `from_glyphs`: empty is an insertion,
    several is a merge. `slot`/`sound`/`release` are `assemble.py`'s own
    machinery, naming which unit and sound this glyph presents."""

    char: str
    kind: nd.GlyphKind
    from_glyphs: tuple = ()
    slot: SlotId | None = None
    sound: SoundId | None = None
    release: SoundId | None = None


def text(rendered: tuple[RenderGlyph, ...]) -> str:
    """`r.text("recited")` serializes exactly what `rendered` holds."""
    return "".join(glyph.char for glyph in rendered)


def write_recited(
    score: Score, inscription: Inscription, performance: Performance, pen: Pen,
    targets: dict | None = None,
) -> tuple[RenderGlyph, ...]:
    """One word's worth of glyphs at a time, a space between words, and any
    stop sign the source carries after that word."""
    attrs = _by_slot_aspect(performance)
    releases = _releases_by_slot(performance)
    sounds = dict(performance.sounds)
    occurrences = {o.id: o for o in performance.occurrences}
    started = _slots_by_rule(performance, HAMZA_WASL_START)
    sources = _source_graphemes(inscription, performance, targets)
    signs = _stop_signs_by_word(score, inscription)

    out: list[RenderGlyph] = []
    for index, word in enumerate(score.words):
        if index:
            out.append(RenderGlyph(" ", nd.GlyphKind.STRUCTURAL))
        out.extend(
            _write_word(
                word, attrs, releases, sounds, occurrences, started, sources, pen
            )
        )
        out.extend(
            RenderGlyph(sign.char, nd.GlyphKind.STOP_SIGN, (sign.id,))
            for sign in signs.get(index, ())
        )
    return tuple(out)


def _write_word(word: ScoreWord, attrs, releases, sounds, occurrences, started,
                fact_glyphs, pen: Pen):
    for slot in word.slots:
        yield from _write_unit(
            slot, attrs, releases, sounds, occurrences, started, fact_glyphs, pen
        )


def _write_unit(slot, attrs, releases, sounds, occurrences, started,
                fact_glyphs, pen: Pen):
    """A unit whose consonant is gone -- merged or silenced -- writes nothing
    at all. Each scalar the unit spells is its own glyph."""
    consonant = attrs.get((slot.id, Aspect.CONSONANT))
    if isinstance(consonant, (Silent, MergedInto)):
        return
    if not isinstance(consonant, Hosts):
        raise WriteError(f"{slot.id} has no consonant realization to write")

    vowel = attrs.get((slot.id, Aspect.VOWEL))
    vowel_sound = sounds[vowel.sound] if isinstance(vowel, Hosts) else None
    consonant_sound = sounds[consonant.sound]
    yield RenderGlyph(
        _write_letter(consonant_sound, slot.id in started, vowel_sound, pen),
        nd.GlyphKind.BASE,
        _fact_glyphs(fact_glyphs, slot.id, SlotFact.LETTER),
        slot.id,
        consonant.sound,
        releases.get(slot.id),
    )
    if consonant_sound.geminate:
        yield RenderGlyph(
            pen.role("shadda"), nd.GlyphKind.SHADDA,
            _fact_glyphs(fact_glyphs, slot.id, SlotFact.ONSET),
            slot.id, consonant.sound,
        )

    if vowel_sound is not None:
        yield from _write_vowel(
            vowel_sound, vowel.sound, slot.id, fact_glyphs, pen
        )
    elif not (
        slot.origin is SlotOrigin.NUNATION
        and _by_rule(consonant, occurrences) in _BARE_TANWEEN_NOON
    ):
        yield RenderGlyph(
            pen.role("sukun"), nd.GlyphKind.SUKUN,
            _fact_glyphs(fact_glyphs, slot.id, SlotFact.VOWEL_ABSENCE), slot.id,
        )


def _releases_by_slot(performance: Performance) -> dict:
    """The qalqala echo shares its slot with the plain consonant, so it
    needs its own lookup rather than `_by_slot_aspect`'s single entry."""
    sounds = dict(performance.sounds)
    return {
        attribution.slots[0]: attribution.sound
        for attribution in performance.attributions
        if isinstance(attribution, Hosts)
        and isinstance(sounds[attribution.sound], Release)
    }


def _slots_by_rule(performance: Performance, rules: frozenset[Rule]) -> frozenset:
    """`WaslHamza` records its occurrence with no effect at all when
    started on -- the plain fill spells the canonical value untouched, so
    only the occurrence, not the attribution, says which rule that was."""
    return frozenset(
        subject
        for occurrence in performance.occurrences
        if occurrence.rule in rules
        for subject in occurrence.subjects
    )


def _by_rule(attribution, occurrences) -> Rule | None:
    if attribution.by is None:
        return None
    occurrence = occurrences.get(attribution.by)
    return occurrence.rule if occurrence is not None else None


def _write_letter(sound: Consonant, started: bool, vowel_sound, pen: Pen) -> str:
    if sound.letter is CanonLetter.HAMZA and started and vowel_sound:
        return _WASL_HAMZA_SHAPE.get(vowel_sound.quality.value, pen.letter(sound.letter))
    return pen.letter(sound.letter)


def _write_vowel(sound: Vowel, sound_id, slot_id, fact_glyphs, pen: Pen):
    """Length is already resolved on the sound, so no boundary check here.
    A long vowel is up to three glyphs: the haraka, the vowel letter, and the
    madd sign."""
    yield RenderGlyph(
        pen.short_vowel(sound.quality), nd.GlyphKind.HARAKA,
        _fact_glyphs(fact_glyphs, slot_id, SlotFact.VOWEL_QUALITY),
        slot_id, sound_id,
    )
    if not sound.long:
        return
    carrier, carrier_text = pen.performed_carrier(sound.quality)
    yield RenderGlyph(
        carrier_text, nd.GlyphKind.VOWEL_LETTER,
        _fact_glyphs(fact_glyphs, slot_id, SlotFact.VOWEL_LENGTH),
        slot_id, sound_id,
    )
    madd = pen.roles.get(MADD)
    if madd:
        yield RenderGlyph(
            madd, nd.GlyphKind.MADD_SIGN,
            _fact_glyphs(fact_glyphs, slot_id, SlotFact.VOWEL_LENGTH),
            slot_id, sound_id,
        )


def _source_graphemes(
    inscription: Inscription, performance: Performance, targets: dict | None
) -> dict:
    """Every `Evidences` edge, keyed by (slot, fact): a base letter, a
    shadda, a haraka and its carrier each cite only their own source glyph.
    A `Decorates`/`Attests` edge names no fact; not part of this."""
    out: dict[tuple, list] = {}
    for spelling in inscription.spellings:
        fact = getattr(spelling, "fact", None)
        if fact not in _CONSONANT_FACTS and fact not in VOWEL_FACTS:
            continue
        out.setdefault((spelling.slot, fact), []).append(spelling.grapheme)
    for carrier, quiescent in _ibdal_carriers(performance, targets):
        out.setdefault((carrier, SlotFact.VOWEL_LENGTH), []).extend(
            out.get((quiescent, SlotFact.LETTER), ())
        )
    return {key: tuple(graphemes) for key, graphemes in out.items()}


def _ibdal_carriers(performance: Performance, targets: dict | None = None):
    """(lengthened slot, the quiescent hamza it carries) for each ibdal.

    The rasm writes no length on the prosthetic hamza, so the hamza this
    rule silences is the one the reading writes that length on."""
    if targets is None:
        targets = effect_targets(performance)
    return [
        (targets[occurrence.id][0], occurrence.subjects[0])
        for occurrence in performance.occurrences
        if occurrence.rule is Rule.IBDAL_HAMZA and targets.get(occurrence.id)
    ]


def _fact_glyphs(fact_glyphs: dict, slot_id, fact: SlotFact) -> tuple:
    return fact_glyphs.get((slot_id, fact), ())


def _by_slot_aspect(performance: Performance) -> dict:
    out: dict = {}
    for attribution in performance.attributions:
        if isinstance(attribution, (Hosts, MergedInto, Silent)):
            for slot_id in attribution.slots:
                out[(slot_id, attribution.aspect)] = attribution
    return out


def _stop_signs_by_word(
    score: Score, inscription: Inscription
) -> dict[int, tuple[Grapheme, ...]]:
    """Every advice-class grapheme, attached to the word it follows."""
    word_of = _word_of_offset(score, inscription)
    ordered = sorted(word_of)
    out: dict[int, list[Grapheme]] = {}
    for grapheme in inscription.graphemes:
        if grapheme.cls is not GraphemeClass.ADVICE:
            continue
        preceding = bisect_left(ordered, grapheme.id.offset) - 1
        if preceding >= 0:
            out.setdefault(word_of[ordered[preceding]], []).append(grapheme)
    return {index: tuple(signs) for index, signs in out.items()}


def _word_of_offset(score: Score, inscription: Inscription) -> dict[int, int]:
    """The word index of every grapheme offset that spells part of a slot."""
    slot_word = {
        slot.id: index
        for index, word in enumerate(score.words)
        for slot in word.slots
    }
    out: dict[int, int] = {}
    for spelling in inscription.spellings:
        slot_id = getattr(spelling, "slot", None)
        word_index = slot_word.get(slot_id)
        if word_index is not None:
            out[spelling.grapheme.offset] = word_index
    return out


__all__ = ["RenderGlyph", "text", "write_recited"]
