"""The transformed cell columns: the source-to-recited delta over the cells.

A letter read differently is replaced from the pen, a silent one is dropped,
a sound with no glyph is inserted; status is the kind and letter, not a rule.
"""

from __future__ import annotations

from dataclasses import replace

from ...model.canon import CanonLetter, Onset, Quality
from ...model.inscription import GlyphKind
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
from .transform_tashil import split_compact_tashil

#: The haraka role that writes each short quality, for spelling an inserted
#: connecting vowel.
_VOWEL_ROLE = {Quality.A: "fatha", Quality.U: "damma", Quality.I: "kasra"}
_HAMZA_GLYPHS = frozenset("ءأإؤئٕٔ")


def _slot_of_unit(source: SourceView, insc: InscriptionFacts) -> dict[int, object]:
    return {
        unit.id.value: insc.slot_of[min(c.value for c in unit.character_ids)]
        for unit in source.units
        if unit.character_ids
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


def _needs_written_hamza(
    col: CellColumn,
    cons: Consonant,
    facts: AnalysisFacts,
) -> bool:
    compact_tashil = any(
        isinstance((value := facts.sounds[sound.value].value), Consonant)
        and value.letter is CanonLetter.HAMZA
        and value.eased
        for sound in col.owned_sound_ids
    )
    return (
        cons.letter is CanonLetter.HAMZA
        and not cons.eased
        and not compact_tashil
        and not any(glyph in col.text for glyph in _HAMZA_GLYPHS)
    )


def _hamza_spelling(slot, pen: Pen) -> str:
    quality = slot.nucleus.quality
    return (
        pen.letter(CanonLetter.HAMZA) if quality is None else pen.seated_hamza(quality)
    )


def _transform_letter(
    col: CellColumn,
    cons: Consonant,
    slot,
    pen: Pen,
    facts: AnalysisFacts,
) -> CellColumn:
    shadda = pen.role("shadda")
    lost_shadda = shadda in col.text and not cons.geminate
    gained_shadda = shadda not in col.text and cons.geminate
    needs_hamza = _needs_written_hamza(col, cons, facts)
    eased_hamza = (
        cons.eased
        and cons.letter is CanonLetter.HAMZA
        and not any(glyph in col.text for glyph in _HAMZA_GLYPHS)
        and not any(
            isinstance(facts.sounds[sound.value].value, Vowel)
            and facts.sounds[sound.value].value.long
            for sound in col.owned_sound_ids
        )
    )
    if (
        not _is_replaced(cons, slot)
        and not needs_hamza
        and not eased_hamza
        and not lost_shadda
        and not gained_shadda
    ):
        return col
    if needs_hamza or eased_hamza:
        text = _hamza_spelling(slot, pen)
    elif _is_replaced(cons, slot):
        text = _consonant_spelling(cons, pen)
    elif lost_shadda:
        text = col.text.replace(shadda, "")
    else:
        text = col.text + shadda
    return replace(col, status=CellStatus.REPLACED, text=text)


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
    return _transform_letter(col, cons, facts.slots[facts.slot_index[slot]], pen, facts)


def _spell_sound(value, pen: Pen) -> str:
    if isinstance(value, Vowel):
        return pen.role(_VOWEL_ROLE[value.quality])
    if isinstance(value, Consonant):
        return _consonant_spelling(value, pen)
    return ""


def _inserted_column(
    new_id: int,
    anchor: LetterUnitId,
    side: CellSide,
    sound: int,
    facts: AnalysisFacts,
    pen: Pen,
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
    words: tuple[CellWord, ...],
    facts: AnalysisFacts,
) -> tuple[CellWord, ...]:
    """No Hafs reading inserts a slot-less sound. Assembling an inserted column
    at its anchor and spanning its sound belongs to the reading that mints one;
    `_inserted_column` states the shape such a column takes."""
    if facts.insertions:
        raise NotImplementedError("inserting a slot-less sound is unimplemented")
    return words


def _wasl_sounds(
    col: CellColumn, facts: AnalysisFacts, slot
) -> tuple[list[int], list[int]]:
    if slot is None or slot.onset is not Onset.WASL:
        return [], []
    consonants: list[int] = []
    vowels: list[int] = []
    for sound in col.owned_sound_ids:
        value = facts.sounds[sound.value].value
        (consonants if isinstance(value, Consonant) else vowels).append(sound.value)
    return consonants, vowels


def _inserted_haraka(
    new_id: int, col: CellColumn, sound: int, facts: AnalysisFacts, pen: Pen
) -> CellColumn:
    value = facts.sounds[sound].value
    assert isinstance(value, Vowel)
    return CellColumn(
        id=CellColumnId(new_id),
        role=CellRole.HARAKA,
        text=pen.role(_VOWEL_ROLE[value.quality]),
        source_character_ids=(),
        source_unit_ids=(),
        tier=CellTier.BELOW if value.quality is Quality.I else CellTier.ABOVE,
        attached_to_column_id=col.id,
        status=CellStatus.INSERTED,
        rule_occurrence_ids=(),
        silence=None,
        variant_id=col.variant_id,
        variant_choice=col.variant_choice,
        owned_sound_ids=(SoundId(sound),),
        presented_sound_ids=(),
        anchor_unit_id=col.source_unit_ids[0],
        side=CellSide.AFTER,
    )


def _split_wasl_word(
    word: CellWord, facts: AnalysisFacts, slot_of_unit, pen: Pen, next_id: int
) -> tuple[CellWord, int]:
    columns: list[CellColumn] = []
    sounds = list(word.sounds)
    for col in word.columns:
        slot_id = (
            slot_of_unit.get(col.source_unit_ids[0].value)
            if col.source_unit_ids
            else None
        )
        slot = None if slot_id is None else facts.slots[facts.slot_index[slot_id]]
        consonants, vowels = _wasl_sounds(col, facts, slot)
        if len(consonants) != 1 or len(vowels) != 1:
            columns.append(col)
            continue
        value = facts.sounds[vowels[0]].value
        base = replace(
            col,
            text=pen.seated_hamza(value.quality),
            owned_sound_ids=(SoundId(consonants[0]),),
        )
        mark = _inserted_haraka(next_id, base, vowels[0], facts, pen)
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


def _native_vowel_marks(word):
    return {
        column.id: tuple(
            mark for mark in word.columns
            if mark.role is CellRole.HARAKA
            and mark.attached_to_column_id == column.id
            and mark.source_character_ids
            and mark.status is not CellStatus.DROPPED
        )
        for column in word.columns
    }


def _unwritten_short_vowel(col, facts, slot_of_unit, insc):
    if col.role is not CellRole.LETTER or not col.source_unit_ids:
        return None
    slot_id = slot_of_unit.get(col.source_unit_ids[0].value)
    slot = None if slot_id is None else facts.slots[facts.slot_index[slot_id]]
    if slot is None or slot.onset is Onset.WASL:
        return None
    kinds = {insc.glyphs[glyph.value].kind for glyph in col.source_character_ids}
    if kinds.difference({GlyphKind.BASE, GlyphKind.SHADDA, GlyphKind.TAJWEED_MARK}):
        return None
    consonants = [
        sound.value for sound in col.owned_sound_ids
        if isinstance(facts.sounds[sound.value].value, Consonant)
    ]
    vowels = [
        sound.value for sound in col.owned_sound_ids
        if isinstance(facts.sounds[sound.value].value, Vowel)
        and not facts.sounds[sound.value].value.long
        and facts.sounds[sound.value].value.quality in _VOWEL_ROLE
    ]
    return vowels[0] if len(consonants) == 1 and len(vowels) == 1 else None


def _split_word_short_vowels(word, facts, slot_of_unit, insc, pen, next_id):
    columns, sounds = [], list(word.sounds)
    native_marks = _native_vowel_marks(word)
    native_sounds: dict[CellColumnId, list[SoundId]] = {}
    for col in word.columns:
        columns.append(col)
        vowel = _unwritten_short_vowel(col, facts, slot_of_unit, insc)
        if vowel is None:
            continue
        base = replace(col, owned_sound_ids=tuple(
            sound for sound in col.owned_sound_ids if sound.value != vowel
        ))
        columns[-1] = base
        text = pen.role(_VOWEL_ROLE[facts.sounds[vowel].value.quality])
        written = [mark for mark in native_marks[col.id] if mark.text == text]
        if len(written) == 1:
            mark = written[0]
            native_sounds.setdefault(mark.id, []).append(SoundId(vowel))
        else:
            mark = _inserted_haraka(next_id, base, vowel, facts, pen)
            next_id += 1
            columns.append(mark)
        sounds = [
            replace(sound, column_ids=(mark.id,))
            if sound.sound_id.value == vowel else sound
            for sound in sounds
        ]
    columns = [
        replace(column, owned_sound_ids=tuple(dict.fromkeys(
            (*column.owned_sound_ids, *native_sounds[column.id])
        ))) if column.id in native_sounds else column
        for column in columns
    ]
    return replace(word, columns=tuple(columns), sounds=tuple(sounds)), next_id


def _split_unwritten_short_vowels(words, facts, slot_of_unit, insc, pen):
    """Give an unwritten short vowel its own inserted mark cell."""
    next_id, out = next_column_id(words), []
    for word in words:
        split, next_id = _split_word_short_vowels(
            word, facts, slot_of_unit, insc, pen, next_id
        )
        out.append(split)
    return tuple(out)


def transform_words(
    words: tuple[CellWord, ...],
    session: Session,
    source: SourceView,
    pen: Pen,
    *,
    extra_phonemes: frozenset[str] = frozenset(),
    facts: AnalysisFacts | None = None,
    insc: InscriptionFacts | None = None,
) -> tuple[CellWord, ...]:
    if facts is None:
        facts = analyse(session, packaged_alphabet(), extra_phonemes=extra_phonemes)
    if insc is None:
        insc = inscribe(session)
    slot_of_unit = _slot_of_unit(source, insc)
    out = split_compact_tashil(
        words, facts, source, insc, pen, _inserted_haraka
    )
    out = tuple(
        replace(
            word,
            columns=tuple(
                _transform_column(col, facts, slot_of_unit, pen) for col in word.columns
            ),
        )
        for word in out
    )
    out = _split_unwritten_short_vowels(out, facts, slot_of_unit, insc, pen)
    out = _insertions(out, facts)
    return _split_started_wasl(out, facts, slot_of_unit, pen)


__all__ = ["transform_words"]
