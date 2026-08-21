"""The transformed cell columns: the source-to-recited delta over the cells.

A letter read differently is replaced from the pen, a silent one is dropped,
a sound with no glyph is inserted; status is the kind and letter, not a rule.
"""
from __future__ import annotations

from dataclasses import replace

from ...model.canon import Onset, Quality
from ...model.performance import Consonant, Side, Vowel
from ...orthography.write import Pen
from ...render.alphabet import packaged_alphabet
from ...session import Session
from ..facts import AnalysisFacts, analyse
from ..inscription import InscriptionFacts, inscribe
from ..ids import CellColumnId, LetterUnitId, SoundId
from ..source_dtos import SourceView
from .dtos import CellColumn, CellRole, CellSide, CellStatus, CellTier, CellWord

#: The haraka role that writes each short quality, for spelling an inserted
#: connecting vowel.
_VOWEL_ROLE = {Quality.A: "fatha", Quality.U: "damma", Quality.I: "kasra"}


def _slot_of_unit(source: SourceView, insc: InscriptionFacts) -> dict[int, object]:
    return {
        unit.id.value: insc.slot_of[min(c.value for c in unit.character_ids)]
        for unit in source.units if unit.character_ids
    }


def _owned_consonant(col: CellColumn, facts: AnalysisFacts) -> Consonant | None:
    for sound in col.owned_sound_ids:
        value = facts.sounds[sound.value].value
        if isinstance(value, Consonant):
            return value
    return None


def _consonant_spelling(cons: Consonant, pen: Pen) -> str:
    return pen.letter(cons.letter) + (pen.role("shadda") if cons.geminate else "")


def _is_replaced(cons: Consonant, slot) -> bool:
    """A started prosthetic hamza -- a wasl connector now sounding -- or a
    letter the reading swaps for another, e.g. a taa marbuta read as a haa."""
    return slot.onset is Onset.WASL or cons.letter is not slot.letter


def _transform_letter(col: CellColumn, cons: Consonant, slot, pen: Pen) -> CellColumn:
    if not _is_replaced(cons, slot):
        return col
    return replace(
        col, status=CellStatus.REPLACED, text=_consonant_spelling(cons, pen)
    )


def _transform_column(
    col: CellColumn, facts: AnalysisFacts, slot_of_unit: dict[int, object], pen: Pen
) -> CellColumn:
    if col.status is CellStatus.DROPPED:
        return col
    if col.role not in (CellRole.LETTER, CellRole.MADD) or not col.source_unit_ids:
        return col
    slot = slot_of_unit.get(col.source_unit_ids[0].value)
    cons = _owned_consonant(col, facts)
    if slot is None or cons is None:
        return col
    return _transform_letter(col, cons, facts.slots[facts.slot_index[slot]], pen)


def _spell_sound(value, pen: Pen) -> str:
    if isinstance(value, Vowel):
        return pen.role(_VOWEL_ROLE[value.quality])
    if isinstance(value, Consonant):
        return _consonant_spelling(value, pen)
    return ""


def _inserted_column(
    new_id: int, anchor: LetterUnitId, side: CellSide, sound: int,
    facts: AnalysisFacts, pen: Pen,
) -> CellColumn:
    """A performed sound with no source glyph: empty provenance, a unit/side
    anchor, and its label from the pen."""
    value = facts.sounds[sound].value
    return CellColumn(
        id=CellColumnId(new_id),
        role=CellRole.HARAKA if isinstance(value, Vowel) else CellRole.LETTER,
        text=_spell_sound(value, pen),
        source_character_ids=(),
        source_unit_ids=(),
        tier=CellTier.MAIN,
        attached_to_column_id=None,
        status=CellStatus.INSERTED,
        rule_occurrence_ids=(),
        silence=None,
        variant_id=None,
        variant_choice=None,
        owned_sound_ids=(SoundId(sound),),
        presented_sound_ids=(),
        anchor_unit_id=anchor,
        side=side,
    )


def _unit_of_slot(slot_of_unit: dict[int, object]) -> dict[object, int]:
    out: dict[object, int] = {}
    for unit, slot in sorted(slot_of_unit.items()):
        out.setdefault(slot, unit)
    return out


def _insertions(
    words: tuple[CellWord, ...], facts: AnalysisFacts,
    slot_of_unit: dict[int, object], pen: Pen,
) -> tuple[CellWord, ...]:
    """Hafs mints no insertion, so this yields nothing over the corpus; the
    machinery stands for the reading that will."""
    if not facts.insertions:
        return words
    unit_of_slot = _unit_of_slot(slot_of_unit)
    next_id = 1 + max(c.id.value for w in words for c in w.columns)
    by_word: dict[int, list[CellColumn]] = {}
    for edge in facts.insertions:
        slot, side = edge.anchor
        anchor = unit_of_slot.get(slot)
        if anchor is None:
            continue
        by_word.setdefault(facts.word_of_slot[slot.ordinal], []).append(
            _inserted_column(
                next_id, LetterUnitId(anchor),
                CellSide.BEFORE if side is Side.BEFORE else CellSide.AFTER,
                edge.sound, facts, pen,
            )
        )
        next_id += 1
    return tuple(
        replace(w, columns=(*w.columns, *by_word.get(w.word_id.value, ())))
        if w.word_id.value in by_word else w
        for w in words
    )


def transform_words(
    words: tuple[CellWord, ...], session: Session, source: SourceView, pen: Pen,
    *, extra_phonemes: frozenset[str] = frozenset(),
) -> tuple[CellWord, ...]:
    facts = analyse(session, packaged_alphabet(), extra_phonemes=extra_phonemes)
    insc = inscribe(session)
    slot_of_unit = _slot_of_unit(source, insc)
    out = tuple(
        replace(word, columns=tuple(
            _transform_column(col, facts, slot_of_unit, pen)
            for col in word.columns
        ))
        for word in words
    )
    return _insertions(out, facts, slot_of_unit, pen)


__all__ = ["transform_words"]
