"""The inscription tier: the facts about the written source.

Built on demand from `session.inscription`. The graphemes are ordered by
offset -- the position in that order is the source index every edge names.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from ..model.address import GraphemeId, SlotId
from ..model.canon import Score
from ..model.inscription import (
    Attests,
    Decorates,
    Evidences,
    Inscription,
    SlotFact,
    Structural as InscStructural,
)
from ..session import Session
from .glyphs import Glyph, glyph_kind_of


@dataclass(frozen=True, slots=True)
class Supplied:
    glyph: int
    slot: SlotId
    fact: SlotFact


@dataclass(frozen=True, slots=True)
class Witnessed:
    glyph: int
    slot: SlotId


@dataclass(frozen=True, slots=True)
class Decorated:
    glyph: int
    slot: SlotId


@dataclass(frozen=True, slots=True)
class Structural:
    glyph: int


SpellingEdge: TypeAlias = Supplied | Witnessed | Decorated | Structural


@dataclass(frozen=True, slots=True)
class InscriptionFacts:
    """What one script wrote, resolved to source-index positions."""

    glyphs: tuple[Glyph, ...]
    spellings: tuple[SpellingEdge, ...]
    grapheme_index: dict[GraphemeId, int]
    slot_of: dict[int, SlotId]
    structural: frozenset[int]
    vowel_absent: frozenset[int]


def _word_of_slot(score: Score) -> tuple[int, ...]:
    return tuple(
        word for word, score_word in enumerate(score.words)
        for _ in score_word.slots
    )


def _bindings(inscription: Inscription):
    """Structural and vowel-absent grapheme ids, and each grapheme's slot."""
    structural: set[GraphemeId] = set()
    vowel_absent: set[GraphemeId] = set()
    slot_of_grapheme: dict[GraphemeId, SlotId] = {}
    for spelling in inscription.spellings:
        grapheme = getattr(spelling, "grapheme", None)
        if isinstance(spelling, InscStructural):
            structural.add(grapheme)
        elif isinstance(spelling, Evidences) and spelling.fact is SlotFact.VOWEL_ABSENCE:
            vowel_absent.add(grapheme)
        slot = getattr(spelling, "slot", None) or getattr(spelling, "anchor", None)
        if grapheme is not None and slot is not None:
            slot_of_grapheme.setdefault(grapheme, slot)
    return structural, vowel_absent, slot_of_grapheme


def _glyphs(inscription: Inscription, word_of_slot, structural, vowel_absent,
            slot_of_grapheme):
    ordered = sorted(inscription.graphemes, key=lambda g: g.id.offset)
    glyphs: list[Glyph] = []
    grapheme_index: dict[GraphemeId, int] = {}
    slot_of: dict[int, SlotId] = {}
    for index, grapheme in enumerate(ordered):
        slot = slot_of_grapheme.get(grapheme.id)
        word = (
            word_of_slot[slot.ordinal]
            if slot is not None and grapheme.id not in structural
            else None
        )
        glyphs.append(Glyph(
            word=word, char=grapheme.char,
            kind=glyph_kind_of(
                grapheme.cls,
                vowel_absent=grapheme.id in vowel_absent,
                structural=grapheme.id in structural,
            ),
            word_index=grapheme.index if word is not None else None,
            source_index=index,
        ))
        grapheme_index[grapheme.id] = index
        if slot is not None:
            slot_of[index] = slot
    return tuple(glyphs), grapheme_index, slot_of


def _spellings(inscription: Inscription, grapheme_index) -> tuple[SpellingEdge, ...]:
    out: list[SpellingEdge] = []
    for spelling in inscription.spellings:
        match spelling:
            case Evidences(grapheme=g, slot=s, fact=f):
                out.append(Supplied(grapheme_index[g], s, f))
            case Attests(grapheme=g, anchor=s):
                out.append(Witnessed(grapheme_index[g], s))
            case Decorates(grapheme=g, slot=s):
                out.append(Decorated(grapheme_index[g], s))
            case InscStructural(grapheme=g):
                out.append(Structural(grapheme_index[g]))
    return tuple(out)


def inscribe(session: Session) -> InscriptionFacts:
    inscription = session.inscription
    word_of_slot = _word_of_slot(session.score)
    structural, vowel_absent, slot_of_grapheme = _bindings(inscription)
    glyphs, grapheme_index, slot_of = _glyphs(
        inscription, word_of_slot, structural, vowel_absent, slot_of_grapheme
    )
    return InscriptionFacts(
        glyphs=glyphs,
        spellings=_spellings(inscription, grapheme_index),
        grapheme_index=grapheme_index,
        slot_of=slot_of,
        structural=frozenset(grapheme_index[g] for g in structural),
        vowel_absent=frozenset(grapheme_index[g] for g in vowel_absent),
    )


__all__ = [
    "Decorated",
    "InscriptionFacts",
    "Structural",
    "Supplied",
    "Witnessed",
    "inscribe",
]
