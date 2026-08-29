"""Split compact fixed-tashil writing into semantic transformed cells."""
from __future__ import annotations

from dataclasses import replace

from ...model.canon import CanonLetter, Quality
from ...model.inscription import GlyphKind
from ...model.performance import Consonant, Vowel
from ..facts import AnalysisFacts
from ..ids import CellColumnId, SoundId
from ..inscription import InscriptionFacts
from ..source_dtos import SourceView
from .align import next_column_id
from .dtos import CellColumn, CellRole, CellStatus, CellTier, CellWord


_VOWEL_ROLE = {Quality.A: "fatha", Quality.U: "damma", Quality.I: "kasra"}


def _sequence(column: CellColumn, facts: AnalysisFacts):
    """Return a collapsed pair of vocalised hamzas, if this column is one."""
    if column.role is not CellRole.LETTER or len(column.owned_sound_ids) != 4:
        return None
    values = tuple(
        facts.sounds[sound.value].value for sound in column.owned_sound_ids
    )
    first, first_vowel, second, second_vowel = values
    if not (
        isinstance(first, Consonant)
        and first.letter is CanonLetter.HAMZA
        and not first.eased
        and isinstance(first_vowel, Vowel)
        and not first_vowel.long
        and first_vowel.quality in _VOWEL_ROLE
        and isinstance(second, Consonant)
        and second.letter is CanonLetter.HAMZA
        and second.eased
        and isinstance(second_vowel, Vowel)
        and not second_vowel.long
        and second_vowel.quality in _VOWEL_ROLE
    ):
        return None
    return first_vowel, second_vowel


def _source_parts(column, sequence, source, insc, pen):
    characters = tuple(
        source.characters[item.value] for item in column.source_character_ids
    )
    bases = tuple(
        item for item in characters
        if insc.glyphs[item.id.value].kind is GlyphKind.BASE
    )
    first_text = pen.role(_VOWEL_ROLE[sequence[0].quality])
    first_marks = tuple(item for item in characters if item.text == first_text)
    eased_marks = tuple(
        item for item in characters if item not in (*bases, *first_marks)
    )
    if not (
        len(characters) == 3
        and len(bases) == len(first_marks) == len(eased_marks) == 1
        and insc.glyphs[eased_marks[0].id.value].kind is GlyphKind.TAJWEED_MARK
    ):
        return None
    return bases[0], first_marks[0], eased_marks[0], first_text


def _split_column(column, sequence, parts, facts, pen, insert_haraka, next_id):
    base_char, first_char, eased_char, first_text = parts
    first_sound, first_vowel, second_sound, second_vowel = (
        sound.value for sound in column.owned_sound_ids
    )
    first_base = replace(
        column,
        text=pen.seated_hamza(sequence[0].quality),
        source_character_ids=(base_char.id,),
        status=CellStatus.REPLACED,
        rule_occurrence_ids=(),
        owned_sound_ids=(SoundId(first_sound),),
    )
    first_mark = replace(
        column,
        id=CellColumnId(next_id),
        role=CellRole.HARAKA,
        text=first_text,
        source_character_ids=(first_char.id,),
        tier=CellTier.BELOW if sequence[0].quality is Quality.I else CellTier.ABOVE,
        attached_to_column_id=first_base.id,
        status=CellStatus.PRESENT,
        rule_occurrence_ids=(),
        silence=None,
        owned_sound_ids=(SoundId(first_vowel),),
        presented_sound_ids=(),
        anchor_unit_id=None,
        side=None,
    )
    second_base = replace(
        column,
        id=CellColumnId(next_id + 1),
        text=pen.seated_hamza(sequence[1].quality),
        source_character_ids=(eased_char.id,),
        tier=CellTier.MAIN,
        attached_to_column_id=None,
        status=CellStatus.REPLACED,
        rule_occurrence_ids=(),
        silence=None,
        owned_sound_ids=(SoundId(second_sound),),
        presented_sound_ids=(),
        anchor_unit_id=None,
        side=None,
    )
    second_mark = insert_haraka(
        next_id + 2, second_base, second_vowel, facts, pen
    )
    columns = first_base, first_mark, second_base, second_mark
    targets = dict(zip(
        (first_sound, first_vowel, second_sound, second_vowel),
        (item.id for item in columns),
        strict=True,
    ))
    return columns, targets, next_id + 3


def _split_word(word, facts, source, insc, pen, insert_haraka, next_id):
    columns, sounds = [], list(word.sounds)
    for column in word.columns:
        sequence = _sequence(column, facts)
        parts = (
            None if sequence is None or len(column.source_unit_ids) != 1
            else _source_parts(column, sequence, source, insc, pen)
        )
        if sequence is None or parts is None:
            columns.append(column)
            continue
        split, targets, next_id = _split_column(
            column, sequence, parts, facts, pen, insert_haraka, next_id
        )
        columns.extend(split)
        sounds = [
            replace(sound, column_ids=(targets[sound.sound_id.value],))
            if sound.sound_id.value in targets
            else sound
            for sound in sounds
        ]
    return replace(word, columns=tuple(columns), sounds=tuple(sounds)), next_id


def split_compact_tashil(words, facts, source, insc, pen, insert_haraka):
    """Project one written two-hamza compound as two semantic cell groups."""
    next_id, out = next_column_id(words), []
    for word in words:
        split, next_id = _split_word(
            word, facts, source, insc, pen, insert_haraka, next_id
        )
        out.append(split)
    return tuple(out)


__all__ = ["split_compact_tashil"]
