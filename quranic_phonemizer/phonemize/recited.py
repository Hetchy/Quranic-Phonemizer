"""The recited text: what a `Performance` says, not what the Score allows.

`orthography/write.py` spells a Score's joined form and cannot see a
`BoundaryPlan`; this walks the `Performance` a plan already produced.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..model.canon import CARRIER_OF, CanonLetter, Rule, Score, ScoreWord, SlotOrigin
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
    Silent,
    Vowel,
)
from ..orthography.write import MADD, Pen, WriteError

#: Which role writes each short vowel quality. Kept local rather than
#: imported: `orthography.write`'s own table is private to that module.
_SHORT_ROLE = {"a": "fatha", "u": "damma", "i": "kasra"}

#: A tanween noon these rules realize is left bare -- no sukun mark -- because
#: bareness is what signals the assimilation; every other realization keeps
#: the mark. 06-two-texts.md section 4.1a.
_BARE_TANWEEN_NOON = frozenset({Rule.IKHFAA_HAQIQI, Rule.IQLAB})

#: 01-contract section 1.1: a hamza wasl started on is the hamza its vowel
#: calls for, never the bare letter or the seat the rasm wrote.
_WASL_HAMZA_SHAPE = {"a": "أ", "u": "أ", "i": "إ"}

#: Which `SlotFact` a source glyph supplies for the consonant part, as
#: opposed to `VOWEL_FACTS` for the vowel part -- the split `from_glyphs`
#: needs to tell a kept letter from a kept haraka.
_CONSONANT_FACTS = frozenset({SlotFact.LETTER, SlotFact.ONSET})


@dataclass(frozen=True, slots=True)
class RenderGlyph:
    """One scalar of the recited text. `from_glyphs` mirrors 01-contract
    section 4.3: empty is an insertion, several is a merge."""

    char: str
    kind: GraphemeClass
    from_glyphs: tuple = ()


def text(rendered: tuple[RenderGlyph, ...]) -> str:
    """`r.text("recited")` serializes exactly what `rendered` holds."""
    return "".join(glyph.char for glyph in rendered)


def write_recited(
    score: Score, inscription: Inscription, performance: Performance, pen: Pen
) -> tuple[RenderGlyph, ...]:
    """One word's worth of glyphs at a time, a space between words, and any
    stop sign the source carries after that word -- 06-two-texts row 31, 30."""
    attrs = _by_slot_aspect(performance)
    sounds = dict(performance.sounds)
    occurrences = {o.id: o for o in performance.occurrences}
    started = _slots_by_rule(performance, Rule.WASL_START)
    sources = _source_graphemes(inscription)
    signs = _stop_signs_by_word(score, inscription)

    out: list[RenderGlyph] = []
    for index, word in enumerate(score.words):
        if index:
            out.append(RenderGlyph(" ", GraphemeClass.STRUCTURAL))
        out.extend(
            _write_word(word, attrs, sounds, occurrences, started, sources, pen)
        )
        out.extend(
            RenderGlyph(sign.char, GraphemeClass.ADVICE, (sign.id,))
            for sign in signs.get(index, ())
        )
    return tuple(out)


def _write_word(word: ScoreWord, attrs, sounds, occurrences, started, sources,
                pen: Pen):
    for slot in word.slots:
        yield from _write_unit(
            slot, attrs, sounds, occurrences, started, sources, pen
        )


def _write_unit(slot, attrs, sounds, occurrences, started, sources, pen: Pen):
    """A unit whose consonant is gone -- merged or silenced -- writes
    nothing at all: 06-two-texts rows 6 and 7, "goes, with its sukun"."""
    consonant = attrs.get((slot.id, Aspect.CONSONANT))
    if isinstance(consonant, (Silent, MergedInto)):
        return
    if not isinstance(consonant, Hosts):
        raise WriteError(f"{slot.id} has no consonant realization to write")

    vowel = attrs.get((slot.id, Aspect.VOWEL))
    vowel_sound = sounds[vowel.sound] if isinstance(vowel, Hosts) else None
    yield RenderGlyph(
        _write_consonant(
            sounds[consonant.sound], slot.id in started, vowel_sound, pen
        ),
        GraphemeClass.BASE,
        sources.get((slot.id, Aspect.CONSONANT), ()),
    )

    if vowel_sound is not None:
        glyph = _write_vowel(vowel_sound, pen)
        if glyph:
            yield RenderGlyph(
                glyph, GraphemeClass.HARAKA,
                sources.get((slot.id, Aspect.VOWEL), ()),
            )
    elif not (
        slot.origin is SlotOrigin.NUNATION
        and _by_rule(consonant, occurrences) in _BARE_TANWEEN_NOON
    ):
        yield RenderGlyph(
            pen.role("sukun"), GraphemeClass.HARAKA,
            sources.get((slot.id, Aspect.VOWEL), ()),
        )


def _slots_by_rule(performance: Performance, rule: Rule) -> frozenset:
    """`WaslHamza` records its occurrence with no effect at all when
    started on -- the plain fill spells the canonical value untouched, so
    only the occurrence, not the attribution, says which rule that was."""
    return frozenset(
        occurrence.parts.source
        for occurrence in performance.occurrences
        if occurrence.rule is rule
    )


def _by_rule(attribution, occurrences) -> Rule | None:
    if attribution.by is None:
        return None
    occurrence = occurrences.get(attribution.by)
    return occurrence.rule if occurrence is not None else None


def _write_consonant(sound: Consonant, started: bool, vowel_sound, pen: Pen) -> str:
    if sound.letter is CanonLetter.HAMZA and started and vowel_sound:
        out = _WASL_HAMZA_SHAPE.get(vowel_sound.quality.value, pen.letter(sound.letter))
    else:
        out = pen.letter(sound.letter)
    if sound.geminate:
        out += pen.role("shadda")
    return out


def _write_vowel(sound: Vowel, pen: Pen) -> str:
    """Length is already resolved on the sound, so no boundary check here:
    the writer only ever spells what the Performance already decided."""
    role = _SHORT_ROLE.get(sound.quality.value)
    if role is None:
        raise WriteError(f"no haraka writes quality {sound.quality}")
    out = pen.role(role)
    if sound.long:
        carrier = CARRIER_OF[sound.quality]
        out += pen.carriers.get(carrier) or pen.letter(carrier)
        out += pen.roles.get(MADD, "")
    return out


def _source_graphemes(inscription: Inscription) -> dict:
    """Every `Evidences` edge, grouped by the (slot, aspect) it supplies --
    a kept or substituted glyph's `from_glyphs`. A `Decorates`/`Attests`
    edge names no fact and so no aspect; it is not part of this."""
    out: dict[tuple, list] = {}
    for spelling in inscription.spellings:
        fact = getattr(spelling, "fact", None)
        if fact in _CONSONANT_FACTS:
            aspect = Aspect.CONSONANT
        elif fact in VOWEL_FACTS:
            aspect = Aspect.VOWEL
        else:
            continue
        out.setdefault((spelling.slot, aspect), []).append(spelling.grapheme)
    return {key: tuple(graphemes) for key, graphemes in out.items()}


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
        preceding = [offset for offset in ordered if offset < grapheme.id.offset]
        if preceding:
            out.setdefault(word_of[max(preceding)], []).append(grapheme)
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
