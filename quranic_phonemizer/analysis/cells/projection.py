"""Compose transformed columns into the renderer-ready cell projection."""
from __future__ import annotations

from dataclasses import replace

from ...model.inscription import GlyphKind
from ...model.performance import Aspect, Consonant, Vowel
from ...orthography.write import Pen
from ..attributions import Hosted, Insertion, Merged, Silenced
from ..facts import AnalysisFacts
from ..ids import CellColumnId, OccurrenceId, SoundId
from ..inscription import InscriptionFacts
from ..source_dtos import SourceView
from .align import next_column_id
from .dtos import (
    CellColumn,
    CellGroup,
    CellGroupKind,
    CellRole,
    CellSide,
    CellStatus,
    CellTier,
    CellWord,
)


def _fold_sukun(word: CellWord) -> CellWord:
    hosts = {
        c.id.value: c for c in word.columns if c.tier is CellTier.MAIN
    }
    folded: dict[int, CellColumn] = {}
    removed: set[int] = set()
    for mark in word.columns:
        if mark.role is not CellRole.SUKUN or mark.attached_to_column_id is None:
            continue
        host = folded.get(mark.attached_to_column_id.value) or hosts[mark.attached_to_column_id.value]
        folded[host.id.value] = replace(
            host,
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


def _pausal_slots(facts: AnalysisFacts) -> set[object]:
    return {
        slot
        for edge in facts.silences
        if edge.aspect is Aspect.VOWEL
        and edge.by is not None
        and facts.occurrences[edge.by].boundary is not None
        for slot in edge.slots
    }


def _fold_pausal_sukun(word: CellWord, facts: AnalysisFacts,
                       slot_of_unit, pen: Pen) -> CellWord:
    pausal = _pausal_slots(facts)
    columns = []
    for col in word.columns:
        slots = {
            slot_of_unit[unit.value] for unit in col.source_unit_ids
            if unit.value in slot_of_unit
        }
        consonantal = any(
            isinstance(facts.sounds[sound.value].value, Consonant)
            for sound in col.owned_sound_ids
        )
        if (
            col.tier is CellTier.MAIN
            and slots & pausal
            and consonantal
            and not col.text.endswith(pen.role("sukun"))
        ):
            status = (
                CellStatus.REPLACED
                if col.status is CellStatus.PRESENT else col.status
            )
            col = replace(col, text=col.text + pen.role("sukun"), status=status)
        columns.append(col)
    return replace(word, columns=tuple(columns))


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


def _carrier_text(value: Vowel, pen: Pen) -> str:
    return pen.performed_carrier(value.quality)[1]


def _inserted_carrier(new_id: int, seat: CellColumn, sound: SoundId,
                      value: Vowel, pen: Pen) -> CellColumn:
    anchor = seat.source_unit_ids[0] if seat.source_unit_ids else seat.anchor_unit_id
    return CellColumn(
        id=CellColumnId(new_id), role=CellRole.MADD,
        text=_carrier_text(value, pen), source_character_ids=(), source_unit_ids=(),
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
    columns, start, target, facts, slot_of_unit, text, insc
):
    for index in range(start + 1, len(columns)):
        col = columns[index]
        if any(not isinstance(facts.sounds[s.value].value, Vowel)
               for s in col.owned_sound_ids):
            break
        if col.status is not CellStatus.DROPPED or not col.source_unit_ids:
            continue
        slot_id = slot_of_unit.get(col.source_unit_ids[0].value)
        if slot_id is None:
            continue
        slot = facts.slots[facts.slot_index[slot_id]]
        kinds = {insc.glyphs[c.value].kind for c in col.source_character_ids}
        if (
            slot.letter is target
            or col.text == text
            or GlyphKind.SMALL_VOWEL in kinds
        ):
            return index
    return None


def _ensure_carriers(word: CellWord, facts: AnalysisFacts, insc: InscriptionFacts,
                     slot_of_unit, pen: Pen, next_id: int) -> tuple[CellWord, int]:
    columns = list(word.columns)
    sounds = list(word.sounds)
    for sound_index, cell in enumerate(list(sounds)):
        value = facts.sounds[cell.sound_id.value].value
        if not isinstance(value, Vowel) or not value.long:
            continue
        by_id = {c.id.value: i for i, c in enumerate(columns)}
        span = [columns[by_id[c.value]] for c in cell.column_ids]
        if any(c.role is CellRole.MADD for c in span):
            continue
        seat = span[0]
        if _has_maddah(seat, insc):
            continue
        at = by_id[seat.id.value]
        target, text = pen.performed_carrier(value.quality)
        candidate = _candidate_carrier(
            columns, at, target, facts, slot_of_unit,
            text, insc,
        )
        if candidate is None:
            carrier = _inserted_carrier(next_id, seat, cell.sound_id, value, pen)
            next_id += 1
            columns.insert(at + 1, carrier)
        else:
            carrier = columns[candidate]
        seat, carrier = _move_sound(seat, carrier, cell.sound_id)
        if seat.role is CellRole.TANWEEN:
            seat = replace(
                seat, role=CellRole.HARAKA,
                text=pen.short_vowel(value.quality),
                status=CellStatus.REPLACED,
            )
        columns[columns.index(next(c for c in columns if c.id == seat.id))] = seat
        columns[columns.index(next(c for c in columns if c.id == carrier.id))] = carrier
        ordered = tuple(c.id for c in columns if c.id in {seat.id, carrier.id})
        sounds[sound_index] = replace(cell, column_ids=ordered)
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
        col for col in columns if col.role in roles and any(
            slot_of_unit.get(unit.value) in slots for unit in col.source_unit_ids
        )
    ]


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
        if isinstance(edge, Hosted) and (edge.by, edge.sound) in merged:
            continue
        occurrence = OccurrenceId(edge.by)
        if isinstance(edge, Merged):
            targets = _column_targets(words, edge.sound, presenters=True)
        elif isinstance(edge, Silenced):
            targets = _silenced_targets(columns, edge, slot_of_unit)
        elif isinstance(edge, (Hosted, Insertion)):
            targets = _column_targets(words, edge.sound)
        else:
            targets = []
        for col in targets:
            if occurrence not in placed[col.id.value]:
                placed[col.id.value].append(occurrence)
    for modifier in facts.modifiers:
        occurrence = OccurrenceId(modifier.by)
        for col in _column_targets(words, modifier.sound):
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
        if isinstance(edge, Merged)
    }
    out = []
    for word in words:
        columns = []
        for col in word.columns:
            cause = next((o for o in col.rule_occurrence_ids if o.value in silenced), None)
            if cause is None and not col.owned_sound_ids:
                cause = next((OccurrenceId(merged[s.value])
                              for s in col.presented_sound_ids if s.value in merged), None)
            empty = not col.owned_sound_ids and not col.presented_sound_ids
            merger_source = cause is not None and not col.owned_sound_ids
            if cause is not None and (empty or merger_source):
                col = replace(col, status=CellStatus.DROPPED, silence=cause)
            columns.append(col)
        out.append(replace(word, columns=tuple(columns)))
    return tuple(out)


def _group_sound_ids(word: CellWord, ids: set[CellColumnId]) -> tuple[SoundId, ...]:
    owned = {
        sound for col in word.columns if col.id in ids
        for sound in col.owned_sound_ids
    }
    return tuple(sound.sound_id for sound in word.sounds if sound.sound_id in owned)


def _groups(word: CellWord, facts: AnalysisFacts) -> tuple[CellGroup, ...]:
    by_id = {c.id: c for c in word.columns}
    attached: dict[CellColumnId, list[CellColumnId]] = {}
    for col in word.columns:
        if col.attached_to_column_id is not None:
            attached.setdefault(col.attached_to_column_id, []).append(col.id)
    claimed: set[CellColumnId] = set()
    groups: list[CellGroup] = []
    for sound in word.sounds:
        value = facts.sounds[sound.sound_id.value].value
        if not isinstance(value, Vowel) or not value.long:
            continue
        carrier = next((by_id[c] for c in sound.column_ids
                        if by_id[c].role is CellRole.MADD), None)
        quality = [c for c in sound.column_ids if by_id[c].tier is not CellTier.MAIN]
        if carrier is None:
            continue
        ids = tuple((*quality, carrier.id, *[
            c for c in attached.get(carrier.id, ()) if c not in quality
        ]))
        claimed.update(ids)
        groups.append(CellGroup(
            carrier.id, CellGroupKind.VOWEL, ids, _group_sound_ids(word, set(ids))
        ))
    for main in (c for c in word.columns if c.tier is CellTier.MAIN):
        if main.id in claimed:
            continue
        ids = (main.id, *(c for c in attached.get(main.id, ()) if c not in claimed))
        claimed.update(ids)
        groups.append(CellGroup(
            main.id, CellGroupKind.BASE, ids, _group_sound_ids(word, set(ids))
        ))
    for col in word.columns:
        if col.id not in claimed:
            groups.append(CellGroup(
                col.id, CellGroupKind.BASE, (col.id,),
                _group_sound_ids(word, {col.id}),
            ))
    order = {c.id: i for i, c in enumerate(word.columns)}
    return tuple(sorted(groups, key=lambda g: min(order[c] for c in g.column_ids)))


def project_words(words: tuple[CellWord, ...], facts: AnalysisFacts,
                  source: SourceView, insc: InscriptionFacts,
                  pen: Pen) -> tuple[CellWord, ...]:
    """Fold marks, supply carriers, place rules, and state every visual group."""
    out = tuple(_fold_sukun(word) for word in words)
    slot_of_unit = _slot_of_columns(source, insc)
    out = tuple(
        _fold_pausal_sukun(word, facts, slot_of_unit, pen) for word in out
    )
    next_id = next_column_id(out)
    carried = []
    for word in out:
        projected, next_id = _ensure_carriers(
            word, facts, insc, slot_of_unit, pen, next_id
        )
        carried.append(projected)
    out = _place_rules(tuple(carried), facts, slot_of_unit)
    out = _visual_statuses(out, facts)
    return tuple(replace(word, groups=_groups(word, facts)) for word in out)


__all__ = ["project_words"]
