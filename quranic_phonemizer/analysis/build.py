"""Assemble the core DTO bundle from a resolved request.

Reshapes the performance and inscription tiers into the public records, native
throughout: no derivation here reads the public assembler.
"""
from __future__ import annotations

from ..model.address import Junction, SlotId
from ..model.inscription import SlotFact
from ..render.alphabet import packaged_alphabet
from ..session import Session
from . import ids
from .attributions import Hosted, Insertion
from .dtos import (
    AnalysisBundle,
    Boundary,
    BoundaryState,
    Merger,
    RuleOccurrence,
    Sound,
    Word,
)
from .facts import AnalysisFacts, analyse
from .glyphs import GlyphKind
from .inscription import InscriptionFacts, Supplied, inscribe

_STATE_OF = {
    Junction.JOIN: BoundaryState.JOIN,
    Junction.SAKT: BoundaryState.SAKT,
    Junction.STOP: BoundaryState.STOP,
    Junction.EDGE: BoundaryState.STOP,
}


def _word_of(facts: AnalysisFacts, slot: SlotId) -> int:
    return facts.word_of_slot[facts.slot_index[slot]]


def _sound_word(facts: AnalysisFacts) -> dict[int, int]:
    """Each sound's primary word: the word of the slot that realizes it."""
    out: dict[int, int] = {}
    for edge in facts.attributions:
        if isinstance(edge, Hosted):
            out[edge.sound] = _word_of(facts, edge.slots[0])
        elif isinstance(edge, Insertion):
            out[edge.sound] = _word_of(facts, edge.anchor[0])
    return out


def _sound_occurrences(facts: AnalysisFacts) -> list[list[int]]:
    """Per sound, the occurrences that classify or change it, in firing order."""
    out: list[list[int]] = [[] for _ in facts.sounds]
    for edge in facts.attributions:
        sound = getattr(edge, "sound", None)
        if sound is not None and edge.by is not None:
            out[sound].append(edge.by)
    for modifier in facts.modifiers:
        out[modifier.sound].append(modifier.by)
    return [sorted(set(occs)) for occs in out]


def _word_texts(insc: InscriptionFacts, n_words: int) -> list[str]:
    parts: list[list[str]] = [[] for _ in range(n_words)]
    for glyph in insc.glyphs:
        if glyph.word is not None:
            parts[glyph.word].append(glyph.char)
    return ["".join(chars) for chars in parts]


def _advice_signs(insc: InscriptionFacts) -> dict[int, str]:
    """The stop-sign character written after each word, by word."""
    out: dict[int, str] = {}
    current: int | None = None
    for glyph in insc.glyphs:
        if glyph.word is not None:
            current = glyph.word
        elif glyph.kind is GlyphKind.STOP_SIGN and current is not None:
            out[current] = glyph.char
    return out


def _sakt_signs(facts: AnalysisFacts, insc: InscriptionFacts) -> dict[int, str]:
    """The sakt sign character, by the word it is written after."""
    out: dict[int, str] = {}
    for edge in insc.spellings:
        if isinstance(edge, Supplied) and edge.fact is SlotFact.SAKT:
            out[_word_of(facts, edge.slot)] = insc.glyphs[edge.glyph].char
    return out


def _build_sounds(
    facts: AnalysisFacts, sound_word: dict[int, int], sound_occ: list[list[int]]
) -> tuple[Sound, ...]:
    return tuple(
        Sound(
            id=ids.SoundId(i),
            order=i,
            token=fact.token,
            word_id=ids.WordId(sound_word[i]),
            rule_occurrence_ids=tuple(ids.OccurrenceId(o) for o in sound_occ[i]),
        )
        for i, fact in enumerate(facts.sounds)
    )


def _build_words(
    facts: AnalysisFacts,
    session: Session,
    texts: list[str],
    sound_word: dict[int, int],
) -> tuple[Word, ...]:
    per_word: list[list[int]] = [[] for _ in texts]
    for sound, word in sorted(sound_word.items()):
        per_word[word].append(sound)
    words = []
    for i, score_word in enumerate(session.score.words):
        words.append(Word(
            id=ids.WordId(i),
            ref=str(score_word.location),
            text=texts[i],
            before_boundary_id=ids.BoundaryId(i),
            after_boundary_id=ids.BoundaryId(i + 1),
            sound_ids=tuple(ids.SoundId(s) for s in per_word[i]),
        ))
    return tuple(words)


def _build_boundaries(
    session: Session,
    facts: AnalysisFacts,
    advice_signs: dict[int, str],
    sakt_signs: dict[int, str],
) -> tuple[Boundary, ...]:
    n_words = len(session.score.words)
    advice = session.inscription.advice
    out: list[Boundary] = []
    for i in range(n_words + 1):
        before = ids.WordId(i - 1) if i else None
        after = ids.WordId(i) if i < n_words else None
        if i == 0:
            state, sign, note = BoundaryState.START, None, None
        else:
            word = i - 1
            state = _STATE_OF[facts.junctions[word]]
            note = advice[word]
            sign = advice_signs.get(word) if note is not None else sakt_signs.get(word)
        out.append(Boundary(ids.BoundaryId(i), before, after, state, sign, note))
    return tuple(out)


def _build_occurrences(
    facts: AnalysisFacts, sound_occ: list[list[int]]
) -> tuple[RuleOccurrence, ...]:
    occ_sounds: list[list[int]] = [[] for _ in facts.occurrences]
    for sound, occs in enumerate(sound_occ):
        for occ in occs:
            occ_sounds[occ].append(sound)
    out: list[RuleOccurrence] = []
    for i, occurrence in enumerate(facts.occurrences):
        affected = set(occurrence.subjects) | set(
            facts.effect_targets.get(occurrence.id, ())
        )
        words = sorted({_word_of(facts, slot) for slot in affected})
        boundary = occurrence.boundary
        boundary_ids = (
            (ids.BoundaryId(boundary + 1),) if boundary is not None else ()
        )
        out.append(RuleOccurrence(
            id=ids.OccurrenceId(i),
            rule_id=ids.RuleId(occurrence.rule.value),
            word_ids=tuple(ids.WordId(w) for w in words),
            boundary_ids=boundary_ids,
            sound_ids=tuple(ids.SoundId(s) for s in sorted(occ_sounds[i])),
        ))
    return tuple(out)


def _build_mergers(
    facts: AnalysisFacts, sound_word: dict[int, int]
) -> tuple[Merger, ...]:
    hosts: dict[int, Hosted] = {
        edge.sound: edge
        for edge in facts.attributions
        if isinstance(edge, Hosted)
    }
    out: list[Merger] = []
    for merged in facts.merges:
        before = _word_of(facts, merged.slots[0])
        after = sound_word[merged.sound]
        if before == after:
            continue
        occs = {merged.by}
        host = hosts.get(merged.sound)
        if host is not None and host.by is not None:
            occs.add(host.by)
        out.append(Merger(
            id=ids.MergerId(len(out)),
            boundary_id=ids.BoundaryId(max(before, after)),
            before_word_id=ids.WordId(before),
            after_word_id=ids.WordId(after),
            sound_id=ids.SoundId(merged.sound),
            rule_occurrence_ids=tuple(ids.OccurrenceId(o) for o in sorted(occs)),
        ))
    return tuple(out)


def build_bundle(
    session: Session,
    *,
    ref: str,
    riwayah: str,
    script: str,
    variant: dict,
    extra_phonemes: frozenset[str] = frozenset(),
) -> AnalysisBundle:
    alphabet = packaged_alphabet()
    facts = analyse(session, alphabet, extra_phonemes=extra_phonemes)
    insc = inscribe(session)

    sound_word = _sound_word(facts)
    sound_occ = _sound_occurrences(facts)
    texts = _word_texts(insc, len(session.score.words))

    return AnalysisBundle(
        ref=ref,
        riwayah=riwayah,
        script=script,
        variant=variant,
        extra_phonemes=extra_phonemes,
        schema_version=ids.SCHEMA_VERSION,
        canon_digest=session.score.digest,
        source_text="".join(glyph.char for glyph in insc.glyphs),
        tokens=tuple(fact.token for fact in facts.sounds),
        words=_build_words(facts, session, texts, sound_word),
        boundaries=_build_boundaries(
            session, facts, _advice_signs(insc), _sakt_signs(facts, insc)
        ),
        sounds=_build_sounds(facts, sound_word, sound_occ),
        rule_occurrences=_build_occurrences(facts, sound_occ),
        mergers=_build_mergers(facts, sound_word),
    )


__all__ = ["build_bundle"]
