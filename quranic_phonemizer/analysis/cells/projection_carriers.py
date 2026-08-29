"""Materialize one visible carrier for each performed long vowel."""

from __future__ import annotations

from dataclasses import replace

from ...model.canon import Annotation, Quality
from ...model.inscription import GlyphKind
from ...model.performance import Vowel
from ...orthography.write import Pen
from ..facts import AnalysisFacts
from ..ids import CellColumnId, SoundId
from ..inscription import InscriptionFacts
from ..source_dtos import SourceView
from .dtos import (
    CellColumn,
    CellRole,
    CellSide,
    CellStatus,
    CellTier,
    CellWord,
)
from .projection_marks import DAGGER_ALIF, MAQSURA


def slot_of_columns(source: SourceView, insc: InscriptionFacts) -> dict[int, object]:
    return {
        unit.id.value: insc.slot_of[min(c.value for c in unit.character_ids)]
        for unit in source.units
        if unit.character_ids
    }


def _has_maddah(col: CellColumn, insc: InscriptionFacts) -> bool:
    return any(
        insc.glyphs[c.value].kind is GlyphKind.MADD_SIGN
        for c in col.source_character_ids
    )


def _inserted_carrier(
    new_id: int, seat: CellColumn, sound: SoundId, text: str
) -> CellColumn:
    anchor = seat.source_unit_ids[0] if seat.source_unit_ids else seat.anchor_unit_id
    return CellColumn(
        id=CellColumnId(new_id), role=CellRole.MADD, text=text,
        source_character_ids=(), source_unit_ids=(), tier=CellTier.MAIN,
        attached_to_column_id=None, status=CellStatus.INSERTED,
        rule_occurrence_ids=(), silence=None, variant_id=seat.variant_id,
        variant_choice=seat.variant_choice, owned_sound_ids=(sound,),
        presented_sound_ids=(), anchor_unit_id=anchor, side=CellSide.AFTER,
    )


def _move_sound(
    seat: CellColumn, carrier: CellColumn, sound: SoundId
) -> tuple[CellColumn, CellColumn]:
    presented = tuple(s for s in seat.presented_sound_ids if s != sound)
    if seat.role in {CellRole.HARAKA, CellRole.TANWEEN}:
        presented = tuple(dict.fromkeys((*presented, sound)))
    seat = replace(
        seat,
        owned_sound_ids=tuple(s for s in seat.owned_sound_ids if s != sound),
        presented_sound_ids=presented,
    )
    carrier = replace(
        carrier, role=CellRole.MADD,
        status=(CellStatus.PRESENT if carrier.status is CellStatus.DROPPED else carrier.status),
        silence=None,
        owned_sound_ids=tuple(dict.fromkeys((*carrier.owned_sound_ids, sound))),
    )
    return seat, carrier


def _candidate_carrier(
    columns, start, target, sound, value, facts, slot_of_unit, text, insc
):
    for index in range(start + 1, len(columns)):
        col = columns[index]
        if any(
            not isinstance(facts.sounds[s.value].value, Vowel)
            for s in col.owned_sound_ids
        ):
            break
        if not col.source_unit_ids:
            continue
        slot_id = slot_of_unit.get(col.source_unit_ids[0].value)
        if slot_id is None:
            continue
        slot = facts.slots[facts.slot_index[slot_id]]
        kinds = {insc.glyphs[c.value].kind for c in col.source_character_ids}
        target_presenter = slot.letter is target and (
            col.status is CellStatus.DROPPED or sound in col.presented_sound_ids
        )
        ibdal_source = any(
            slot_id in edge.slots
            and edge.by is not None
            and facts.occurrences[edge.by].rule.value == "ibdal_hamza"
            for edge in facts.silences
        )
        maqsura_a = value.quality is Quality.A and col.text == MAQSURA
        carried_naql_alif = (
            value.quality is Quality.A
            and col.text.endswith(text)
            and len(col.source_character_ids) > 1
            and Annotation.NAQL in slot.annotations
        )
        if (
            target_presenter
            or (
                col.status is CellStatus.DROPPED
                and (
                    col.text == text
                    or GlyphKind.SMALL_VOWEL in kinds
                    or ibdal_source
                    or maqsura_a
                )
            )
            or carried_naql_alif
        ):
            return index
    return None


def _new_carrier(columns, seat, cell, value, facts, slot_of_unit, pen, insc, next_id):
    at = next(i for i, column in enumerate(columns) if column.id == seat.id)
    target, text = pen.performed_carrier(value.quality)
    candidate = _candidate_carrier(
        columns, at, target, cell.sound_id, value, facts, slot_of_unit, text, insc
    )
    if candidate is not None:
        return columns[candidate], text, next_id
    slot_id = (
        slot_of_unit.get(seat.source_unit_ids[0].value)
        if seat.source_unit_ids else None
    )
    slot = None if slot_id is None else facts.slots[facts.slot_index[slot_id]]
    inserted_text = (
        DAGGER_ALIF
        if slot is not None and Annotation.DIVINE_NAME in slot.annotations
        else text
    )
    carrier = _inserted_carrier(next_id, seat, cell.sound_id, inserted_text)
    columns.insert(at + 1, carrier)
    return carrier, text, next_id + 1


def _adjust_carrier(carrier, value, text, facts, slot_of_unit, was_dropped):
    carrier_slot = (
        slot_of_unit.get(carrier.source_unit_ids[0].value)
        if carrier.source_unit_ids else None
    )
    ibdal = carrier_slot is not None and any(
        carrier_slot in edge.slots
        and edge.by is not None
        and facts.occurrences[edge.by].rule.value == "ibdal_hamza"
        for edge in facts.silences
    )
    if was_dropped and value.quality is Quality.A and carrier.text == MAQSURA:
        return replace(
            carrier, text=carrier.text + DAGGER_ALIF, status=CellStatus.REPLACED
        )
    if ibdal and carrier.text != text:
        return replace(carrier, text=text, status=CellStatus.REPLACED)
    return carrier


def _transform_existing_carrier(columns, by_id, span, existing, value, pen):
    if (
        value.quality in {Quality.A, Quality.KUBRA, Quality.TAQLIL}
        and existing.text == MAQSURA
    ):
        columns[by_id[existing.id.value]] = replace(
            existing, text=existing.text + DAGGER_ALIF, status=CellStatus.REPLACED
        )
    for column in span:
        if column.role is CellRole.TANWEEN:
            columns[by_id[column.id.value]] = replace(
                column, role=CellRole.HARAKA,
                text=pen.short_vowel(value.quality), status=CellStatus.REPLACED,
            )


def _ensure_one_carrier(
    columns, sounds, sound_index, cell, value, facts, insc,
    slot_of_unit, pen, next_id,
):
    by_id = {column.id.value: index for index, column in enumerate(columns)}
    span = [column for column in columns if column.id in cell.column_ids]
    existing = next((c for c in span if c.role is CellRole.MADD), None)
    if existing is not None:
        _transform_existing_carrier(columns, by_id, span, existing, value, pen)
        return next_id
    seat = span[0]
    if _has_maddah(seat, insc):
        return next_id
    carrier, text, next_id = _new_carrier(
        columns, seat, cell, value, facts, slot_of_unit, pen, insc, next_id
    )
    was_dropped = carrier.status is CellStatus.DROPPED
    seat, carrier = _move_sound(seat, carrier, cell.sound_id)
    carrier = replace(
        carrier,
        presented_sound_ids=tuple(
            sound for sound in carrier.presented_sound_ids if sound != cell.sound_id
        ),
    )
    carrier = _adjust_carrier(carrier, value, text, facts, slot_of_unit, was_dropped)
    if seat.role is CellRole.TANWEEN:
        seat = replace(
            seat, role=CellRole.HARAKA, text=pen.short_vowel(value.quality),
            status=CellStatus.REPLACED,
        )
    for changed in (seat, carrier):
        at = next(i for i, column in enumerate(columns) if column.id == changed.id)
        columns[at] = changed
    ids = {carrier.id}
    if seat.role in {CellRole.HARAKA, CellRole.TANWEEN}:
        ids.add(seat.id)
    sounds[sound_index] = replace(
        cell, column_ids=tuple(c.id for c in columns if c.id in ids)
    )
    return next_id


def ensure_carriers(
    word: CellWord, facts: AnalysisFacts, insc: InscriptionFacts,
    slot_of_unit, pen: Pen, next_id: int,
) -> tuple[CellWord, int]:
    columns, sounds = list(word.columns), list(word.sounds)
    for sound_index, cell in enumerate(list(sounds)):
        value = facts.sounds[cell.sound_id.value].value
        if isinstance(value, Vowel) and value.long:
            next_id = _ensure_one_carrier(
                columns, sounds, sound_index, cell, value, facts, insc,
                slot_of_unit, pen, next_id,
            )
    return replace(word, columns=tuple(columns), sounds=tuple(sounds)), next_id


__all__ = ["ensure_carriers", "slot_of_columns"]
