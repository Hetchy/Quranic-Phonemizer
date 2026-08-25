"""Compose transformed columns into the renderer-ready cell projection."""
from __future__ import annotations

from dataclasses import replace

from ...model.canon import Annotation, Quality, Rule
from ...model.inscription import GlyphKind
from ...model.performance import Aspect, Vowel
from ...orthography.write import Pen
from ..attributions import Hosted, Insertion, Merged, Relengthened, Silenced
from ..facts import AnalysisFacts
from ..ids import CellColumnId, OccurrenceId, SoundId
from ..inscription import InscriptionFacts
from ..source_dtos import SourceView
from .align import next_column_id
from .dtos import (
    CellColumn,
    CellRole,
    CellSide,
    CellStatus,
    CellTier,
    CellWord,
)
from .projection_marks import (
    DAGGER_ALIF,
    MAQSURA,
    clean_structural_marks,
    fold_maqsura_daggers,
    fold_pausal_sukun,
    transform_plain_madd,
)
from .projection_groups import group_words
from .projection_semantics import preserve_semantic_cells


def _fold_sukun(word: CellWord) -> CellWord:
    hosts = {c.id.value: c for c in word.columns if c.tier is CellTier.MAIN}
    folded: dict[int, CellColumn] = {}
    removed: set[int] = set()
    for mark in word.columns:
        if mark.role is not CellRole.SUKUN or mark.attached_to_column_id is None:
            continue
        host = folded.get(mark.attached_to_column_id.value) or hosts[mark.attached_to_column_id.value]
        folded[host.id.value] = replace(host,
            text=host.text + mark.text,
            source_character_ids=(*host.source_character_ids, *mark.source_character_ids),
            source_unit_ids=(*host.source_unit_ids, *mark.source_unit_ids),
            rule_occurrence_ids=tuple(dict.fromkeys(
                (*host.rule_occurrence_ids, *mark.rule_occurrence_ids)
            )),
        )
        removed.add(mark.id.value)
    columns = tuple(
        folded.get(c.id.value, c) for c in word.columns if c.id.value not in removed
    )
    return replace(word, columns=columns)


def _slot_of_columns(source: SourceView, insc: InscriptionFacts) -> dict[int, object]:
    return {
        unit.id.value: insc.slot_of[min(c.value for c in unit.character_ids)]
        for unit in source.units if unit.character_ids
    }


def _has_maddah(col: CellColumn, insc: InscriptionFacts) -> bool:
    return any(
        insc.glyphs[c.value].kind is GlyphKind.MADD_SIGN
        for c in col.source_character_ids
    )


def _inserted_carrier(new_id: int, seat: CellColumn, sound: SoundId,
                      text: str) -> CellColumn:
    anchor = seat.source_unit_ids[0] if seat.source_unit_ids else seat.anchor_unit_id
    return CellColumn(
        id=CellColumnId(new_id), role=CellRole.MADD,
        text=text,
        source_character_ids=(), source_unit_ids=(),
        tier=CellTier.MAIN, attached_to_column_id=None,
        status=CellStatus.INSERTED, rule_occurrence_ids=(), silence=None,
        variant_id=seat.variant_id, variant_choice=seat.variant_choice,
        owned_sound_ids=(sound,), presented_sound_ids=(),
        anchor_unit_id=anchor, side=CellSide.AFTER,
    )


def _move_sound(seat: CellColumn, carrier: CellColumn,
                sound: SoundId) -> tuple[CellColumn, CellColumn]:
    seat = replace(
        seat,
        owned_sound_ids=tuple(s for s in seat.owned_sound_ids if s != sound),
        presented_sound_ids=tuple(dict.fromkeys((*seat.presented_sound_ids, sound))),
    )
    carrier = replace(
        carrier, role=CellRole.MADD,
        status=(CellStatus.PRESENT if carrier.status is CellStatus.DROPPED
                else carrier.status),
        silence=None,
        owned_sound_ids=tuple(dict.fromkeys((*carrier.owned_sound_ids, sound))),
    )
    return seat, carrier


def _candidate_carrier(
    columns, start, target, sound, value, facts, slot_of_unit, text, insc
):
    for index in range(start + 1, len(columns)):
        col = columns[index]
        if any(not isinstance(facts.sounds[s.value].value, Vowel)
               for s in col.owned_sound_ids):
            break
        if not col.source_unit_ids:
            continue
        slot_id = slot_of_unit.get(col.source_unit_ids[0].value)
        if slot_id is None:
            continue
        slot = facts.slots[facts.slot_index[slot_id]]
        kinds = {insc.glyphs[c.value].kind for c in col.source_character_ids}
        target_presenter = (
            slot.letter is target and (
                col.status is CellStatus.DROPPED or sound in col.presented_sound_ids
            )
        )
        ibdal_source = any(
            slot_id in edge.slots and edge.by is not None
            and facts.occurrences[edge.by].rule.value == "ibdal_hamza"
            for edge in facts.silences
        )
        maqsura_a = value.quality is Quality.A and col.text == MAQSURA
        if target_presenter or (
            col.status is CellStatus.DROPPED
            and (
                col.text == text or GlyphKind.SMALL_VOWEL in kinds
                or ibdal_source or maqsura_a
            )
        ):
            return index
    return None


def _new_carrier(columns, seat, cell, value, facts, slot_of_unit,
                 pen, insc, next_id):
    at = next(i for i, column in enumerate(columns) if column.id == seat.id)
    target, text = pen.performed_carrier(value.quality)
    candidate = _candidate_carrier(
        columns, at, target, cell.sound_id, value, facts, slot_of_unit,
        text, insc,
    )
    if candidate is not None:
        return columns[candidate], text, next_id
    slot_id = (
        slot_of_unit.get(seat.source_unit_ids[0].value)
        if seat.source_unit_ids else None
    )
    slot = None if slot_id is None else facts.slots[facts.slot_index[slot_id]]
    inserted_text = (
        DAGGER_ALIF if slot is not None
        and Annotation.DIVINE_NAME in slot.annotations else text
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
        carrier_slot in edge.slots and edge.by is not None
        and facts.occurrences[edge.by].rule.value == "ibdal_hamza"
        for edge in facts.silences
    )
    if was_dropped and value.quality is Quality.A and carrier.text == MAQSURA:
        return replace(
            carrier, text=carrier.text + DAGGER_ALIF,
            status=CellStatus.REPLACED,
        )
    if was_dropped and ibdal:
        return replace(carrier, text=text, status=CellStatus.REPLACED)
    return carrier


def _transform_existing_carrier(columns, by_id, span, existing, value, pen):
    if (
        value.quality in {Quality.A, Quality.KUBRA, Quality.TAQLIL}
        and existing.text == MAQSURA
    ):
        columns[by_id[existing.id.value]] = replace(
            existing, text=existing.text + DAGGER_ALIF,
            status=CellStatus.REPLACED,
        )
    for column in span:
        if column.role is not CellRole.TANWEEN:
            continue
        columns[by_id[column.id.value]] = replace(
            column,
            role=CellRole.HARAKA,
            text=pen.short_vowel(value.quality),
            status=CellStatus.REPLACED,
        )


def _ensure_one_carrier(
    columns, sounds, sound_index, cell, value, facts, insc,
    slot_of_unit, pen, next_id,
):
    by_id = {column.id.value: index for index, column in enumerate(columns)}
    span = [columns[by_id[column.value]] for column in cell.column_ids]
    existing = next((c for c in span if c.role is CellRole.MADD), None)
    if existing is not None:
        _transform_existing_carrier(
            columns, by_id, span, existing, value, pen
        )
        return next_id
    seat = span[0]
    if _has_maddah(seat, insc):
        return next_id
    carrier, text, next_id = _new_carrier(
        columns, seat, cell, value, facts, slot_of_unit, pen, insc, next_id
    )
    was_dropped = carrier.status is CellStatus.DROPPED
    seat, carrier = _move_sound(seat, carrier, cell.sound_id)
    carrier = replace(carrier, presented_sound_ids=tuple(
        sound for sound in carrier.presented_sound_ids if sound != cell.sound_id
    ))
    carrier = _adjust_carrier(
        carrier, value, text, facts, slot_of_unit, was_dropped
    )
    if seat.role is CellRole.TANWEEN:
        seat = replace(
            seat, role=CellRole.HARAKA, text=pen.short_vowel(value.quality),
            status=CellStatus.REPLACED,
        )
    for changed in (seat, carrier):
        at = next(i for i, column in enumerate(columns) if column.id == changed.id)
        columns[at] = changed
    ids = {seat.id, carrier.id}
    sounds[sound_index] = replace(
        cell, column_ids=tuple(c.id for c in columns if c.id in ids)
    )
    return next_id


def _ensure_carriers(word: CellWord, facts: AnalysisFacts, insc: InscriptionFacts,
                     slot_of_unit, pen: Pen, next_id: int) -> tuple[CellWord, int]:
    columns, sounds = list(word.columns), list(word.sounds)
    for sound_index, cell in enumerate(list(sounds)):
        value = facts.sounds[cell.sound_id.value].value
        if isinstance(value, Vowel) and value.long:
            next_id = _ensure_one_carrier(
                columns, sounds, sound_index, cell, value, facts, insc,
                slot_of_unit, pen, next_id,
            )
    return replace(word, columns=tuple(columns), sounds=tuple(sounds)), next_id


def _column_targets(words: tuple[CellWord, ...], sound: int, *, presenters=False):
    field = "presented_sound_ids" if presenters else "owned_sound_ids"
    return [
        c for w in words for c in w.columns
        if SoundId(sound) in getattr(c, field)
    ]


def _silenced_targets(columns, edge, slot_of_unit):
    roles = (
        {CellRole.HARAKA, CellRole.TANWEEN, CellRole.MADD}
        if edge.aspect is Aspect.VOWEL else {CellRole.LETTER}
    )
    slots = set(edge.slots)
    return [
        col for col in columns if (
            col.role in roles or col.silence == OccurrenceId(edge.by)
        ) and any(
            slot_of_unit.get(unit.value) in slots for unit in col.source_unit_ids
        )
    ]


def _modifier_targets(words, columns, facts, modifier):
    occurrence = OccurrenceId(modifier.by)
    carrier_only = (
        isinstance(modifier, Relengthened)
        and facts.occurrences[modifier.by].rule is Rule.ILTIQA_SHORTENING
    )
    if carrier_only:
        return [col for col in columns if col.silence == occurrence]
    targets = _column_targets(words, modifier.sound)
    if isinstance(facts.sounds[modifier.sound].value, Vowel):
        targets.extend(_column_targets(words, modifier.sound, presenters=True))
    return targets


def _place_rules(words: tuple[CellWord, ...], facts: AnalysisFacts,
                 slot_of_unit) -> tuple[CellWord, ...]:
    placed: dict[int, list[OccurrenceId]] = {
        c.id.value: [] for w in words for c in w.columns
    }
    columns = [c for w in words for c in w.columns]
    merged = {
        (edge.by, edge.sound) for edge in facts.attributions
        if isinstance(edge, Merged)
    }
    for edge in facts.attributions:
        if edge.by is None:
            continue
        rule = facts.occurrences[edge.by].rule.value
        if isinstance(edge, Merged) and rule.startswith("madd_"):
            continue
        if (
            isinstance(edge, Hosted) and (edge.by, edge.sound) in merged
            and not rule.startswith(("idgham_", "madd_"))
        ):
            continue
        occurrence = OccurrenceId(edge.by)
        if isinstance(edge, Merged):
            targets = _column_targets(words, edge.sound, presenters=True)
        elif isinstance(edge, Silenced):
            targets = [] if (
                rule == Rule.NAQL.value and edge.aspect is Aspect.VOWEL
            ) else _silenced_targets(columns, edge, slot_of_unit)
        elif isinstance(edge, (Hosted, Insertion)):
            targets = _column_targets(words, edge.sound)
        else:
            targets = []
        for col in targets:
            if occurrence not in placed[col.id.value]:
                placed[col.id.value].append(occurrence)
    for modifier in facts.modifiers:
        occurrence = OccurrenceId(modifier.by)
        for col in _modifier_targets(words, columns, facts, modifier):
            if occurrence not in placed[col.id.value]:
                placed[col.id.value].append(occurrence)
    return tuple(replace(w, columns=tuple(
        replace(c, rule_occurrence_ids=tuple(placed[c.id.value])) for c in w.columns
    )) for w in words)


def _visual_statuses(words, facts):
    silenced = {
        edge.by for edge in facts.attributions
        if isinstance(edge, Silenced) and edge.by is not None
    }
    merged = {
        edge.sound: edge.by for edge in facts.attributions
        if isinstance(edge, Merged) and edge.by is not None
        and facts.occurrences[edge.by].rule.value.startswith("idgham_")
    }
    out = []
    for word in words:
        columns = []
        for col in word.columns:
            merger_source = any(s.value in merged for s in col.presented_sound_ids)
            if merger_source:
                columns.append(replace(
                    col, status=CellStatus.PRESENT, silence=None
                ))
                continue
            cause = next((o for o in col.rule_occurrence_ids if o.value in silenced), None)
            empty = not col.owned_sound_ids and not col.presented_sound_ids
            if cause is not None and empty:
                col = replace(col, status=CellStatus.DROPPED, silence=cause)
            columns.append(col)
        out.append(replace(word, columns=tuple(columns)))
    return tuple(out)


def project_words(words: tuple[CellWord, ...], facts: AnalysisFacts,
                  source: SourceView, insc: InscriptionFacts,
                  pen: Pen) -> tuple[CellWord, ...]:
    """Fold marks, supply carriers, place rules, and state every visual group."""
    out = tuple(clean_structural_marks(word) for word in words)
    out = tuple(fold_maqsura_daggers(word) for word in out)
    out = tuple(_fold_sukun(word) for word in out)
    slot_of_unit = _slot_of_columns(source, insc)
    out = tuple(
        fold_pausal_sukun(word, facts, slot_of_unit, pen) for word in out
    )
    next_id = next_column_id(out)
    carried = []
    for word in out:
        projected, next_id = _ensure_carriers(
            word, facts, insc, slot_of_unit, pen, next_id
        )
        carried.append(projected)
    out = _place_rules(tuple(carried), facts, slot_of_unit)
    out = transform_plain_madd(out, facts)
    out = _visual_statuses(out, facts)
    out = preserve_semantic_cells(out, facts)
    return group_words(out, facts)


__all__ = ["project_words"]
