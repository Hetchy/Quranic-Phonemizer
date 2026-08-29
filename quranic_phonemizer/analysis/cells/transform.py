"""The transformed cell columns: the source-to-recited delta over the cells.

A letter read differently is replaced from the pen, a silent one is dropped,
a sound with no glyph is inserted; status is the kind and letter, not a rule.
"""

from __future__ import annotations

from dataclasses import replace

from ...model.address import KhilafId, VariantSelection
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
    if (
        not _is_replaced(cons, slot)
        and not needs_hamza
        and not lost_shadda
        and not gained_shadda
    ):
        return col
    if needs_hamza:
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


def _variant_column(
    col: CellColumn, variant_id: KhilafId, choice: str, **changes
) -> CellColumn:
    return replace(
        col, variant_id=variant_id, variant_choice=choice, **changes
    )


def _transform_haraka(
    col: CellColumn,
    facts: AnalysisFacts,
    selection: VariantSelection,
    pen: Pen,
) -> CellColumn:
    """Draw the selected short vowel rather than retaining the source mark."""
    choice = selection.chosen(KhilafId.DAAF_HARAKA)
    if choice is None or col.role is not CellRole.HARAKA:
        return col
    vowels = [
        facts.sounds[sound.value].value
        for sound in col.owned_sound_ids
        if isinstance(facts.sounds[sound.value].value, Vowel)
    ]
    if len(vowels) != 1 or vowels[0].long:
        return col
    text = pen.short_vowel(vowels[0].quality)
    if text == col.text:
        return col
    return _variant_column(
        col,
        KhilafId.DAAF_HARAKA,
        choice,
        text=text,
        status=CellStatus.REPLACED,
    )


def _transform_plain_seen(
    col: CellColumn,
    facts: AnalysisFacts,
    selection: VariantSelection,
    pen: Pen,
) -> CellColumn:
    """Bimusaytir has no written small-seen cell to expose as the seen face."""
    choice = selection.chosen(KhilafId.BIMUSAYTIR)
    cons = _owned_consonant(col, facts)
    if (
        choice != "seen"
        or cons is None
        or cons.letter is not CanonLetter.SEEN
        or pen.letter(CanonLetter.SAD) not in col.text
    ):
        return col
    return _variant_column(
        col,
        KhilafId.BIMUSAYTIR,
        choice,
        text=_consonant_spelling(cons, pen),
        status=CellStatus.REPLACED,
    )


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
        anchor_unit_id=(
            col.source_unit_ids[0]
            if col.source_unit_ids
            else col.anchor_unit_id
        ),
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


def _split_tashil_words(
    words: tuple[CellWord, ...],
    facts: AnalysisFacts,
    selection: VariantSelection,
    pen: Pen,
) -> tuple[CellWord, ...]:
    """Expose the compact article hamza as a replaced hamza plus its fatha."""
    if selection.chosen(KhilafId.ISTIFHAM_ARTICLE) != "tashil":
        return words
    next_id = next_column_id(words)
    out = []
    for word in words:
        columns = []
        sounds = list(word.sounds)
        for col in word.columns:
            consonants = [
                sound.value for sound in col.owned_sound_ids
                if isinstance(facts.sounds[sound.value].value, Consonant)
                and facts.sounds[sound.value].value.eased
            ]
            vowels = [
                sound.value for sound in col.owned_sound_ids
                if isinstance(facts.sounds[sound.value].value, Vowel)
                and not facts.sounds[sound.value].value.long
            ]
            if len(consonants) != 1 or len(vowels) != 1:
                columns.append(col)
                continue
            base = _variant_column(
                col,
                KhilafId.ISTIFHAM_ARTICLE,
                "tashil",
                text=pen.letter(CanonLetter.HAMZA),
                status=CellStatus.REPLACED,
                owned_sound_ids=(SoundId(consonants[0]),),
            )
            mark = _inserted_haraka(next_id, base, vowels[0], facts, pen)
            next_id += 1
            columns.extend((base, mark))
            sounds = [
                replace(sound, column_ids=(mark.id,))
                if sound.sound_id.value == vowels[0]
                else replace(sound, column_ids=(base.id,))
                if sound.sound_id.value == consonants[0]
                else sound
                for sound in sounds
            ]
        out.append(replace(word, columns=tuple(columns), sounds=tuple(sounds)))
    return tuple(out)


def _split_tamanna_words(
    words: tuple[CellWord, ...],
    facts: AnalysisFacts,
    selection: VariantSelection,
    pen: Pen,
) -> tuple[CellWord, ...]:
    """Ikhtilas writes the reduced first noon and damma as inserted cells."""
    if selection.chosen(KhilafId.TAMANNA_NOON) != "ikhtilas":
        return words
    next_id = next_column_id(words)
    out = []
    for word in words:
        columns = []
        sounds = list(word.sounds)
        for col in word.columns:
            consonants = [
                sound.value for sound in col.owned_sound_ids
                if isinstance(facts.sounds[sound.value].value, Consonant)
                and facts.sounds[sound.value].value.letter is CanonLetter.NOON
            ]
            vowels = [
                sound.value for sound in col.owned_sound_ids
                if isinstance(facts.sounds[sound.value].value, Vowel)
                and facts.sounds[sound.value].value.quality is Quality.U
            ]
            if len(consonants) != 2 or len(vowels) != 1 or not col.source_unit_ids:
                columns.append(col)
                continue
            first = _inserted_column(
                next_id,
                col.source_unit_ids[0],
                CellSide.BEFORE,
                consonants[0],
                facts,
                pen,
            )
            first = _variant_column(
                first, KhilafId.TAMANNA_NOON, "ikhtilas"
            )
            next_id += 1
            mark = _inserted_haraka(next_id, first, vowels[0], facts, pen)
            next_id += 1
            final = _variant_column(
                col,
                KhilafId.TAMANNA_NOON,
                "ikhtilas",
                text=pen.letter(CanonLetter.NOON),
                status=CellStatus.REPLACED,
                owned_sound_ids=(SoundId(consonants[1]),),
            )
            columns.extend((first, mark, final))
            targets = {
                consonants[0]: first.id,
                vowels[0]: mark.id,
                consonants[1]: final.id,
            }
            sounds = [
                replace(sound, column_ids=(targets[sound.sound_id.value],))
                if sound.sound_id.value in targets else sound
                for sound in sounds
            ]
        out.append(replace(word, columns=tuple(columns), sounds=tuple(sounds)))
    return tuple(out)


def _transform_iwaja_idraj(
    words: tuple[CellWord, ...],
    facts: AnalysisFacts,
    selection: VariantSelection,
    pen: Pen,
) -> tuple[CellWord, ...]:
    """Restore the written tanwin shape and silence its following alif."""
    if selection.chosen(KhilafId.IWAJA_QAYYIMA) != "idraj":
        return words
    out = []
    for word in words:
        marker = next(
            (
                col for col in word.columns
                if col.text in {"ۜ", "ۣ"}
                and any(
                    isinstance(facts.sounds[sound.value].value, Consonant)
                    and facts.sounds[sound.value].value.letter is CanonLetter.NOON
                    for sound in col.owned_sound_ids
                )
            ),
            None,
        )
        if marker is None:
            out.append(word)
            continue
        marker_at = word.columns.index(marker)
        carrier = next(
            (
                col for col in reversed(word.columns[:marker_at])
                if col.role in (CellRole.LETTER, CellRole.MADD)
                and col.text == pen.letter(CanonLetter.ALIF)
            ),
            None,
        )
        carrier_at = -1 if carrier is None else word.columns.index(carrier)
        vowel = next(
            (
                col for col in reversed(word.columns[:carrier_at])
                if col.role is CellRole.HARAKA
            ),
            None,
        )
        if carrier is None or vowel is None:
            out.append(word)
            continue
        # PausalAlif shortens the joined face before this display transform.
        # Depending on the projection stage, that short vowel can still point
        # at the written carrier.  The restored fathatan must own it because
        # the carrier is absent in idraj.
        vowel_sounds = tuple(
            sound.sound_id
            for sound in word.sounds
            if vowel.id in sound.column_ids or carrier.id in sound.column_ids
        )
        noon_sounds = marker.owned_sound_ids
        tanween = _variant_column(
            vowel,
            KhilafId.IWAJA_QAYYIMA,
            "idraj",
            role=CellRole.TANWEEN,
            text=pen.role("fathatan"),
            status=CellStatus.REPLACED,
            owned_sound_ids=tuple(dict.fromkeys((*vowel_sounds, *noon_sounds))),
            presented_sound_ids=vowel.presented_sound_ids,
            rule_occurrence_ids=tuple(dict.fromkeys(
                (*vowel.rule_occurrence_ids, *marker.rule_occurrence_ids)
            )),
        )
        silent_carrier = _variant_column(
            carrier,
            KhilafId.IWAJA_QAYYIMA,
            "idraj",
            status=CellStatus.DROPPED,
            owned_sound_ids=(),
        )
        columns = tuple(
            tanween if col is vowel
            else silent_carrier if col is carrier
            else col
            for col in word.columns
            if col is not marker
        )
        moved = {*vowel_sounds, *noon_sounds}
        sounds = tuple(
            replace(sound, column_ids=(tanween.id,))
            if sound.sound_id in moved else sound
            for sound in word.sounds
        )
        out.append(replace(word, columns=columns, sounds=sounds))
    return tuple(out)


def _omit_inactive_sakt_marks(
    words: tuple[CellWord, ...],
) -> tuple[CellWord, ...]:
    """An unselected sakt sign has no transformed word cell."""
    return tuple(
        replace(
            word,
            columns=tuple(
                col for col in word.columns
                if not (
                    col.text in {"ۜ", "ۣ"}
                    and col.status is CellStatus.DROPPED
                )
            ),
        )
        for word in words
    )


def _split_unwritten_short_vowels(words, facts, slot_of_unit, insc, pen):
    """Give an unwritten short vowel its own inserted mark cell."""
    next_id = next_column_id(words)
    out = []
    for word in words:
        columns = []
        sounds = list(word.sounds)
        native_marks = {
            column.id: tuple(
                mark
                for mark in word.columns
                if mark.role is CellRole.HARAKA
                and mark.attached_to_column_id == column.id
                and mark.source_character_ids
                and mark.status is not CellStatus.DROPPED
            )
            for column in word.columns
        }
        native_sounds: dict[CellColumnId, list[SoundId]] = {}
        for col in word.columns:
            columns.append(col)
            if col.role is not CellRole.LETTER or not col.source_unit_ids:
                continue
            slot_id = slot_of_unit.get(col.source_unit_ids[0].value)
            slot = None if slot_id is None else facts.slots[facts.slot_index[slot_id]]
            if slot is None or slot.onset is Onset.WASL:
                continue
            kinds = {
                insc.glyphs[glyph.value].kind for glyph in col.source_character_ids
            }
            if kinds.difference({GlyphKind.BASE, GlyphKind.SHADDA}):
                continue
            consonants = [
                sound.value
                for sound in col.owned_sound_ids
                if isinstance(facts.sounds[sound.value].value, Consonant)
            ]
            vowels = [
                sound.value
                for sound in col.owned_sound_ids
                if isinstance(facts.sounds[sound.value].value, Vowel)
                and not facts.sounds[sound.value].value.long
                and facts.sounds[sound.value].value.quality in _VOWEL_ROLE
            ]
            if len(consonants) != 1 or len(vowels) != 1:
                continue
            vowel = vowels[0]
            base = replace(
                col,
                owned_sound_ids=tuple(
                    sound for sound in col.owned_sound_ids if sound.value != vowel
                ),
            )
            columns[-1] = base
            written = [
                mark
                for mark in native_marks[col.id]
                if mark.text == pen.role(_VOWEL_ROLE[facts.sounds[vowel].value.quality])
            ]
            if len(written) == 1:
                mark = written[0]
                native_sounds.setdefault(mark.id, []).append(SoundId(vowel))
            else:
                mark = _inserted_haraka(next_id, base, vowel, facts, pen)
                next_id += 1
                columns.append(mark)
            sounds = [
                replace(sound, column_ids=(mark.id,))
                if sound.sound_id.value == vowel
                else sound
                for sound in sounds
            ]
        columns = [
            replace(
                column,
                owned_sound_ids=tuple(
                    dict.fromkeys(
                        (
                            *column.owned_sound_ids,
                            *native_sounds[column.id],
                        )
                    )
                ),
            )
            if column.id in native_sounds
            else column
            for column in columns
        ]
        out.append(replace(word, columns=tuple(columns), sounds=tuple(sounds)))
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
    selection = session.performance.selection
    out = tuple(
        replace(
            word,
            columns=tuple(
                _transform_plain_seen(
                    _transform_haraka(
                        _transform_column(col, facts, slot_of_unit, pen),
                        facts,
                        selection,
                        pen,
                    ),
                    facts,
                    selection,
                    pen,
                )
                for col in word.columns
            ),
        )
        for word in words
    )
    out = _split_tashil_words(out, facts, selection, pen)
    out = _split_tamanna_words(out, facts, selection, pen)
    out = _transform_iwaja_idraj(out, facts, selection, pen)
    out = _omit_inactive_sakt_marks(out)
    out = _split_unwritten_short_vowels(out, facts, slot_of_unit, insc, pen)
    out = _insertions(out, facts)
    return _split_started_wasl(out, facts, slot_of_unit, pen)


__all__ = ["transform_words"]
