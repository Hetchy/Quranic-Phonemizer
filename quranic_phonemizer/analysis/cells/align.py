"""Align each core sound to the columns that own or present it.

One CellSound per sound spans its owner and presenter columns in render order;
a sound the source presents nowhere takes a minted gap column anchored beside it.
"""
from __future__ import annotations

from dataclasses import replace

from ..dtos import Sound
from ..ids import CellColumnId, LetterUnitId
from .dtos import (
    CellColumn,
    CellRole,
    CellSide,
    CellSound,
    CellStatus,
    CellTier,
    CellWord,
)


def _columns_of_sound(words: tuple[CellWord, ...]) -> dict[int, list[CellColumn]]:
    """Per sound, the columns whose own owned/presented set names it, in the
    render order the columns appear across the words."""
    out: dict[int, list[CellColumn]] = {}
    for word in words:
        for column in word.columns:
            for sound in (*column.owned_sound_ids, *column.presented_sound_ids):
                out.setdefault(sound.value, []).append(column)
    return out


def next_column_id(words: tuple[CellWord, ...]) -> int:
    return 1 + max(
        (col.id.value for word in words for col in word.columns), default=-1
    )


def _gap_column(new_id: int, anchor: LetterUnitId | None,
                side: CellSide | None) -> CellColumn:
    return CellColumn(
        id=CellColumnId(new_id),
        role=CellRole.GAP,
        text="",
        source_character_ids=(),
        source_unit_ids=(),
        tier=CellTier.MAIN,
        attached_to_column_id=None,
        status=CellStatus.GAP,
        rule_occurrence_ids=(),
        silence=None,
        variant_id=None,
        variant_choice=None,
        owned_sound_ids=(),
        presented_sound_ids=(),
        anchor_unit_id=anchor,
        side=side,
    )


def _anchor(word: CellWord, sounds: list[Sound], gap_index: int,
            spans: dict[int, list[CellColumn]]) -> tuple[LetterUnitId | None, CellSide]:
    """The unit a gap column hangs beside: the nearest neighbouring sound of the
    same word that a source column carries, on the side the gap sits."""
    own = {col.id.value for col in word.columns}
    for neighbour, side, edge in (
        (reversed(sounds[:gap_index]), CellSide.AFTER, -1),
        (sounds[gap_index + 1:], CellSide.BEFORE, 0),
    ):
        for sound in neighbour:
            here = [c for c in spans.get(sound.id.value, ()) if c.id.value in own
                    and c.source_unit_ids]
            if here:
                return here[edge].source_unit_ids[0], side
    return None, CellSide.AFTER


def _place_gap(columns: tuple[CellColumn, ...], gap: CellColumn,
               anchor: LetterUnitId | None) -> tuple[CellColumn, ...]:
    """Fold the gap column into the row beside its anchor, on its side."""
    if anchor is None:
        return (*columns, gap)
    index = next(
        i for i, c in enumerate(columns) if anchor in c.source_unit_ids
    )
    at = index + 1 if gap.side is CellSide.AFTER else index
    return (*columns[:at], gap, *columns[at:])


def _align_word(word: CellWord, sounds: list[Sound],
                spans: dict[int, list[CellColumn]], next_id: int
                ) -> tuple[CellWord, int]:
    columns = word.columns
    cells: list[CellSound] = []
    for i, sound in enumerate(sounds):
        span = spans.get(sound.id.value, [])
        if span:
            column_ids = tuple(col.id for col in span)
        else:
            anchor, side = _anchor(word, sounds, i, spans)
            gap = _gap_column(next_id, anchor, side)
            next_id += 1
            columns = _place_gap(columns, gap, anchor)
            column_ids = (gap.id,)
        cells.append(CellSound(sound.id, column_ids, sound.rule_occurrence_ids))
    return replace(word, columns=columns, sounds=tuple(cells)), next_id


def build_cell_sounds(
    words: tuple[CellWord, ...], sounds: tuple[Sound, ...]
) -> tuple[CellWord, ...]:
    """Fill each word's sounds and fold in any gap column its sounds need."""
    spans = _columns_of_sound(words)
    by_word: dict[int, list[Sound]] = {}
    for sound in sounds:
        by_word.setdefault(sound.word_id.value, []).append(sound)
    next_id = next_column_id(words)
    out: list[CellWord] = []
    for word in words:
        ordered = sorted(by_word.get(word.word_id.value, ()), key=lambda s: s.order)
        aligned, next_id = _align_word(word, ordered, spans, next_id)
        out.append(aligned)
    return tuple(out)


__all__ = ["build_cell_sounds", "next_column_id"]
