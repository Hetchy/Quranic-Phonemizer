"""Projection repair for a written qata alif whose haraka participates in naql."""

from __future__ import annotations

from dataclasses import replace

from ..dtos import AnalysisBundle
from ..facts import AnalysisFacts
from ..ids import CellColumnId
from ..source_dtos import SourceView
from .align import next_column_id
from .dtos import (
    CellBoundary,
    CellColumn,
    CellRole,
    CellStatus,
    CellTier,
    CellWord,
)

_CARRIED_QATA = frozenset({"َا", "ُا", "ِا"})
_HARAKA_OF_TOKEN = {"a": "َ", "i": "ِ", "u": "ُ"}
_SOURCE_HARAKA_OF_TOKEN = {
    "a": frozenset({"َ", "ٰ"}),
    "i": frozenset({"ِ"}),
    "u": frozenset({"ُ", "۟"}),
}


def split_carried_naql_alif(
    words: tuple[CellWord, ...],
    facts: AnalysisFacts,
    source: SourceView,
) -> tuple[CellWord, ...]:
    """Keep a written qata alif visible when naql carries its haraka left."""
    next_id = next_column_id(words)
    characters = {character.id: character for character in source.characters}
    out = []
    for word in words:
        columns = []
        for column in word.columns:
            occurrence = next(
                (
                    item
                    for item in column.rule_occurrence_ids
                    if facts.occurrences[item.value].rule.value == "naql"
                ),
                None,
            )
            if (
                occurrence is None
                or column.role is not CellRole.HARAKA
                or column.text not in _CARRIED_QATA
                or len(column.source_character_ids) != 2
            ):
                columns.append(column)
                continue
            haraka_id, alif_id = column.source_character_ids
            columns.append(
                replace(
                    column,
                    text=characters[haraka_id].text,
                    source_character_ids=(haraka_id,),
                )
            )
            columns.append(
                CellColumn(
                    id=CellColumnId(next_id),
                    role=CellRole.LETTER,
                    text=characters[alif_id].text,
                    source_character_ids=(alif_id,),
                    source_unit_ids=column.source_unit_ids,
                    tier=CellTier.MAIN,
                    attached_to_column_id=None,
                    status=CellStatus.DROPPED,
                    rule_occurrence_ids=(occurrence,),
                    silence=occurrence,
                    variant_id=column.variant_id,
                    variant_choice=column.variant_choice,
                    owned_sound_ids=(),
                    presented_sound_ids=(),
                    anchor_unit_id=None,
                    side=None,
                    slot_ids=column.slot_ids,
                )
            )
            next_id += 1
        out.append(replace(word, columns=tuple(columns)))
    return tuple(out)


def place_tanween_naql_on_written_haraka(
    words: tuple[CellWord, ...],
    bundle: AnalysisBundle,
) -> tuple[CellWord, ...]:
    """Label both written endpoints of a tanween Naql merger.

    Restore Naql on the owning qata haraka without leaking merger rules.
    """
    out = list(words)
    for merger in bundle.mergers:
        if merger.boundary_id is None:
            continue
        sound = bundle.sounds[merger.sound_id.value]
        occurrence = next(
            (
                item
                for item in sound.rule_occurrence_ids
                if bundle.rule_occurrences[item.value].rule_id.value == "naql"
            ),
            None,
        )
        if occurrence is None:
            continue
        before = next(word for word in out if word.word_id == merger.before_word_id)
        if not any(
            column.role is CellRole.TANWEEN
            and merger.sound_id in column.presented_sound_ids
            for column in before.columns
        ):
            continue
        after_at = next(
            at for at, word in enumerate(out) if word.word_id == merger.after_word_id
        )
        after = out[after_at]
        columns = tuple(
            replace(
                column,
                rule_occurrence_ids=tuple(
                    dict.fromkeys(
                        (
                            *column.rule_occurrence_ids,
                            occurrence,
                        )
                    )
                ),
            )
            if (
                column.role is CellRole.HARAKA
                and merger.sound_id in column.owned_sound_ids
            )
            else column
            for column in after.columns
        )
        out[after_at] = replace(after, columns=columns)
    return tuple(out)


def _without_column(word: CellWord, column_id: CellColumnId) -> CellWord:
    """Remove a boundary-hosted source column from its former word groups."""
    return replace(
        word,
        columns=tuple(column for column in word.columns if column.id != column_id),
        groups=tuple(
            replace(
                group,
                column_ids=tuple(
                    item for item in group.column_ids if item != column_id
                ),
            )
            for group in word.groups
            if group.column_ids != (column_id,)
        ),
        runs=tuple(
            replace(
                run,
                column_ids=tuple(item for item in run.column_ids if item != column_id),
            )
            for run in word.runs
        ),
    )


def _naql_occurrence(merger, bundle):
    return next((
        item for item in merger.rule_occurrence_ids
        if bundle.rule_occurrences[item.value].rule_id.value == "naql"
    ), None)


def _tanween_and_haraka(before, after, merger):
    tanween = next((
        column for column in before.columns
        if column.role is CellRole.TANWEEN
        and merger.sound_id in column.presented_sound_ids
    ), None)
    haraka = next((
        column for column in after.columns
        if column.role is CellRole.HARAKA
        and merger.sound_id in column.owned_sound_ids
        and column.source_character_ids
    ), None)
    return tanween, haraka


def _compact_haraka(after, merger, occurrence, bundle, characters, next_id):
    token = bundle.sounds[merger.sound_id.value].token
    glyph = _HARAKA_OF_TOKEN.get(token)
    source_glyphs = _SOURCE_HARAKA_OF_TOKEN.get(token, frozenset())
    compact = next((
        column for column in after.columns
        if column.role is CellRole.LETTER
        and merger.sound_id in column.owned_sound_ids
        and any(characters[item].text in source_glyphs
                for item in column.source_character_ids)
    ), None)
    if compact is None:
        return after, None, None, next_id
    haraka_id = next(
        item for item in compact.source_character_ids
        if characters[item].text in source_glyphs
    )
    source_glyph = characters[haraka_id].text
    remaining = tuple(item for item in compact.source_character_ids if item != haraka_id)
    changed = replace(
        compact,
        text=(
            compact.text
            if compact.status is CellStatus.REPLACED
            else "".join(characters[item].text for item in remaining)
        ),
        source_character_ids=remaining,
        owned_sound_ids=tuple(
            sound for sound in compact.owned_sound_ids if sound != merger.sound_id
        ),
    )
    after = replace(after, columns=tuple(
        changed if column.id == compact.id else column for column in after.columns
    ))
    haraka = CellColumn(
        id=CellColumnId(next_id), role=CellRole.HARAKA, text=glyph,
        source_character_ids=(haraka_id,), source_unit_ids=compact.source_unit_ids,
        tier=CellTier.BELOW if glyph == "ِ" else CellTier.ABOVE,
        attached_to_column_id=None,
        status=CellStatus.PRESENT if source_glyph == glyph else CellStatus.REPLACED,
        rule_occurrence_ids=(occurrence,), silence=None,
        variant_id=compact.variant_id, variant_choice=compact.variant_choice,
        owned_sound_ids=(merger.sound_id,), presented_sound_ids=(),
        anchor_unit_id=None, side=None, slot_ids=compact.slot_ids,
    )
    return after, haraka, compact, next_id + 1


def _without_tanween_naql(word, tanween, occurrence):
    return replace(word, columns=tuple(
        replace(column, rule_occurrence_ids=tuple(
            item for item in column.rule_occurrence_ids if item != occurrence
        )) if column.id == tanween.id else column
        for column in word.columns
    ))


def _retarget_bridge(bridges, merger, compact, haraka):
    if compact is None:
        return bridges
    def moved(column):
        return haraka.id if column == compact.id else column
    return tuple(
        replace(
            bridge,
            after_column_ids=tuple(moved(column) for column in bridge.after_column_ids),
            sound=replace(
                bridge.sound,
                column_ids=tuple(moved(column) for column in bridge.sound.column_ids),
            ),
        ) if bridge.merger_id == merger.id else bridge
        for bridge in bridges
    )


def move_tanween_naql_haraka_to_boundary(
    words: tuple[CellWord, ...], boundaries: tuple[CellBoundary, ...],
    bundle: AnalysisBundle, source: SourceView,
) -> tuple[tuple[CellWord, ...], tuple[CellBoundary, ...]]:
    """Move a tanween-triggered source haraka into its merger boundary."""
    word_at = {word.word_id: at for at, word in enumerate(words)}
    boundary_at = {item.boundary_id: at for at, item in enumerate(boundaries)}
    out_words, out_boundaries = list(words), list(boundaries)
    characters = {character.id: character for character in source.characters}
    next_id = 1 + max(
        column.id.value for item in (*words, *boundaries) for column in item.columns
    )
    for merger in bundle.mergers:
        occurrence = _naql_occurrence(merger, bundle)
        if (merger.boundary_id is None or occurrence is None
                or bundle.sounds[merger.sound_id.value].token.endswith(":")):
            continue
        before_at, after_at = word_at[merger.before_word_id], word_at[merger.after_word_id]
        before, after = out_words[before_at], out_words[after_at]
        tanween, haraka = _tanween_and_haraka(before, after, merger)
        compact = None
        if haraka is None:
            after, haraka, compact, next_id = _compact_haraka(
                after, merger, occurrence, bundle, characters, next_id
            )
        if tanween is None or haraka is None:
            continue
        out_words[before_at] = _without_tanween_naql(before, tanween, occurrence)
        out_words[after_at] = after if compact is not None else _without_column(after, haraka.id)
        at = boundary_at[merger.boundary_id]
        boundary = out_boundaries[at]
        out_boundaries[at] = replace(
            boundary,
            columns=(*boundary.columns, replace(haraka, attached_to_column_id=None)),
            bridges=_retarget_bridge(boundary.bridges, merger, compact, haraka),
        )
    return tuple(out_words), tuple(out_boundaries)


__all__ = [
    "move_tanween_naql_haraka_to_boundary",
    "place_tanween_naql_on_written_haraka",
    "split_carried_naql_alif",
]
