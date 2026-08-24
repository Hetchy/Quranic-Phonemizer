"""Build producer-decided visual groups over projected columns."""
from __future__ import annotations

from dataclasses import replace

from ...model.performance import Vowel
from ..facts import AnalysisFacts
from ..ids import CellColumnId, SoundId
from .dtos import (
    CellGroup,
    CellGroupKind,
    CellRole,
    CellTier,
    CellWord,
)


def _sound_ids(word: CellWord, ids: set[CellColumnId]) -> tuple[SoundId, ...]:
    owned = {
        sound for col in word.columns if col.id in ids
        for sound in col.owned_sound_ids
    }
    return tuple(sound.sound_id for sound in word.sounds if sound.sound_id in owned)


def _vowel_groups(word, facts, by_id, attached, claimed) -> list[CellGroup]:
    groups: list[CellGroup] = []
    for sound in word.sounds:
        value = facts.sounds[sound.sound_id.value].value
        if not isinstance(value, Vowel) or not value.long:
            continue
        carrier = next((
            by_id[column] for column in sound.column_ids
            if by_id[column].role is CellRole.MADD
        ), None)
        if carrier is None:
            continue
        quality = [
            column for column in sound.column_ids
            if column != carrier.id
            and by_id[column].tier is not CellTier.MAIN
        ]
        ids = tuple((*quality, carrier.id, *[
            column for column in attached.get(carrier.id, ())
            if column not in quality
        ]))
        claimed.update(ids)
        groups.append(CellGroup(
            carrier.id, CellGroupKind.VOWEL, ids, _sound_ids(word, set(ids))
        ))
    for carrier in (
        column for column in word.columns
        if column.role is CellRole.MADD and column.id not in claimed
    ):
        ids = (*attached.get(carrier.id, ()), carrier.id)
        claimed.update(ids)
        groups.append(CellGroup(
            carrier.id, CellGroupKind.VOWEL, ids, _sound_ids(word, set(ids))
        ))
    return groups


def _groups(word: CellWord, facts: AnalysisFacts) -> tuple[CellGroup, ...]:
    by_id = {column.id: column for column in word.columns}
    attached: dict[CellColumnId, list[CellColumnId]] = {}
    for column in word.columns:
        if column.attached_to_column_id is not None:
            attached.setdefault(column.attached_to_column_id, []).append(column.id)
    claimed: set[CellColumnId] = set()
    groups = _vowel_groups(word, facts, by_id, attached, claimed)
    for main in (c for c in word.columns if c.tier is CellTier.MAIN):
        if main.id in claimed:
            continue
        ids = (main.id, *(c for c in attached.get(main.id, ()) if c not in claimed))
        claimed.update(ids)
        groups.append(CellGroup(
            main.id, CellGroupKind.BASE, ids, _sound_ids(word, set(ids))
        ))
    for column in word.columns:
        if column.id not in claimed:
            groups.append(CellGroup(
                column.id, CellGroupKind.BASE, (column.id,),
                _sound_ids(word, {column.id}),
            ))
    order = {column.id: index for index, column in enumerate(word.columns)}
    return tuple(sorted(groups, key=lambda group: min(
        order[column] for column in group.column_ids
    )))


def group_words(
    words: tuple[CellWord, ...], facts: AnalysisFacts,
) -> tuple[CellWord, ...]:
    return tuple(replace(word, groups=_groups(word, facts)) for word in words)


__all__ = ["group_words"]
