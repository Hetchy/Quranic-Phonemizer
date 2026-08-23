"""The transformed cell columns: the source-to-recited delta over the cells.

A letter read differently is replaced from the pen, a silent one is dropped,
a sound with no glyph is inserted; status is the kind and letter, not a rule.
"""
from __future__ import annotations

from dataclasses import replace

from ...model.canon import CanonLetter, Onset, Quality
from ...model.performance import Consonant, Vowel
from ...orthography.write import Pen
from ...render.alphabet import packaged_alphabet
from ...session import Session
from ..facts import AnalysisFacts, analyse
from ..inscription import InscriptionFacts, inscribe
from ..ids import CellColumnId, LetterUnitId, SoundId
from ..source_dtos import SourceView
from .dtos import CellColumn, CellRole, CellSide, CellStatus, CellTier, CellWord
from .align import next_column_id

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
    """A started prosthetic hamza, or a letter the reading swaps for another
    (a taa marbuta read as a haa). A meem hidden with ghunnah keeps its letter:
    the reader still says a meem, nasalised, so it is not a replacement."""
    if cons.ghunnah and slot.letter is CanonLetter.MEEM:
        return False
    return slot.onset is Onset.WASL or cons.letter is not slot.letter


def _transform_letter(col: CellColumn, cons: Consonant, slot, pen: Pen) -> CellColumn:
    shadda = pen.role("shadda")
    lost_shadda = shadda in col.text and not cons.geminate
    if not _is_replaced(cons, slot) and not lost_shadda:
        return col
    text = _consonant_spelling(cons, pen) if _is_replaced(cons, slot) else col.text.replace(shadda, "")
    return replace(
        col, status=CellStatus.REPLACED, text=text
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


def _insertions(
    words: tuple[CellWord, ...], facts: AnalysisFacts,
) -> tuple[CellWord, ...]:
    """No Hafs reading inserts a slot-less sound. Assembling an inserted column
    at its anchor and spanning its sound belongs to the reading that mints one;
    `_inserted_column` states the shape such a column takes."""
    if facts.insertions:
        raise NotImplementedError("inserting a slot-less sound is unimplemented")
    return words


def _wasl_sounds(col: CellColumn, facts: AnalysisFacts, slot) -> tuple[list[int], list[int]]:
    if slot is None or slot.onset is not Onset.WASL:
        return [], []
    consonants: list[int] = []
    vowels: list[int] = []
    for sound in col.owned_sound_ids:
        value = facts.sounds[sound.value].value
        (consonants if isinstance(value, Consonant) else vowels).append(sound.value)
    return consonants, vowels


def _wasl_mark(new_id: int, col: CellColumn, sound: int,
               facts: AnalysisFacts, pen: Pen) -> CellColumn:
    value = facts.sounds[sound].value
    assert isinstance(value, Vowel)
    return CellColumn(
        id=CellColumnId(new_id), role=CellRole.HARAKA,
        text=pen.role(_VOWEL_ROLE[value.quality]),
        source_character_ids=(), source_unit_ids=(),
        tier=CellTier.BELOW if value.quality is Quality.I else CellTier.ABOVE,
        attached_to_column_id=col.id, status=CellStatus.INSERTED,
        rule_occurrence_ids=(), silence=None, variant_id=col.variant_id,
        variant_choice=col.variant_choice, owned_sound_ids=(SoundId(sound),),
        presented_sound_ids=(), anchor_unit_id=col.source_unit_ids[0],
        side=CellSide.AFTER,
    )


def _split_wasl_word(word: CellWord, facts: AnalysisFacts, slot_of_unit,
                     pen: Pen, next_id: int) -> tuple[CellWord, int]:
    columns: list[CellColumn] = []
    sounds = list(word.sounds)
    for col in word.columns:
        slot_id = slot_of_unit.get(col.source_unit_ids[0].value) if col.source_unit_ids else None
        slot = None if slot_id is None else facts.slots[facts.slot_index[slot_id]]
        consonants, vowels = _wasl_sounds(col, facts, slot)
        if len(consonants) != 1 or len(vowels) != 1:
            columns.append(col)
            continue
        value = facts.sounds[vowels[0]].value
        base = replace(
            col, text=pen.seated_hamza(value.quality),
            owned_sound_ids=(SoundId(consonants[0]),),
        )
        mark = _wasl_mark(next_id, base, vowels[0], facts, pen)
        next_id += 1
        columns.extend((base, mark))
        sounds = [
            replace(s, column_ids=(mark.id,)) if s.sound_id.value == vowels[0] else s
            for s in sounds
        ]
    return replace(word, columns=tuple(columns), sounds=tuple(sounds)), next_id


def _split_started_wasl(words, facts, slot_of_unit, pen):
    next_id = next_column_id(words)
    out = []
    for word in words:
        split, next_id = _split_wasl_word(word, facts, slot_of_unit, pen, next_id)
        out.append(split)
    return tuple(out)


def transform_words(
    words: tuple[CellWord, ...], session: Session, source: SourceView, pen: Pen,
    *, extra_phonemes: frozenset[str] = frozenset(),
    facts: AnalysisFacts | None = None,
    insc: InscriptionFacts | None = None,
) -> tuple[CellWord, ...]:
    if facts is None:
        facts = analyse(session, packaged_alphabet(), extra_phonemes=extra_phonemes)
    if insc is None:
        insc = inscribe(session)
    slot_of_unit = _slot_of_unit(source, insc)
    out = tuple(
        replace(word, columns=tuple(
            _transform_column(col, facts, slot_of_unit, pen)
            for col in word.columns
        ))
        for word in words
    )
    out = _insertions(out, facts)
    return _split_started_wasl(out, facts, slot_of_unit, pen)


__all__ = ["transform_words"]
