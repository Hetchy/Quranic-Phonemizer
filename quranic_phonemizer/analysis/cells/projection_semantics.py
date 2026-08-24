"""Semantic relations retained when a reading drops their performed sound."""
from __future__ import annotations

from dataclasses import replace

from ...model.performance import Vowel
from ..attributions import Recoloured
from ..facts import AnalysisFacts
from ..ids import OccurrenceId
from .dtos import CellRole, CellStatus, CellTier, CellWord


def _has_rule(column, rule: str, facts: AnalysisFacts) -> bool:
    return any(
        facts.occurrences[occurrence.value].rule.value == rule
        for occurrence in column.rule_occurrence_ids
    )


def _occurrence_for(column, rule: str, facts: AnalysisFacts) -> OccurrenceId | None:
    candidates = list(column.rule_occurrence_ids)
    if isinstance(column.silence, OccurrenceId):
        candidates.append(column.silence)
    return next((
        occurrence for occurrence in candidates
        if facts.occurrences[occurrence.value].rule.value == rule
    ), None)


def _with_occurrence(column, occurrence: OccurrenceId):
    return replace(column, rule_occurrence_ids=tuple(dict.fromkeys(
        (*column.rule_occurrence_ids, occurrence)
    )))


def preserve_semantic_cells(
    words: tuple[CellWord, ...], facts: AnalysisFacts
) -> tuple[CellWord, ...]:
    """Keep semantic silence and dropped vowel units explicit in the wire."""
    out = []
    for word in words:
        columns = list(word.columns)
        for at, column in enumerate(columns):
            if (
                _has_rule(column, "lam_shamsiyyah", facts)
                and not column.owned_sound_ids and column.presented_sound_ids
            ):
                occurrence = next(
                    one for one in column.rule_occurrence_ids
                    if facts.occurrences[one.value].rule.value == "lam_shamsiyyah"
                )
                columns[at] = replace(column, silence=occurrence)
                continue
            occurrence = _occurrence_for(column, "waqf_silah_drop", facts)
            if occurrence is None:
                continue
            if (
                column.silence == occurrence
                and column.role is not CellRole.HARAKA
            ):
                columns[at] = replace(
                    _with_occurrence(column, occurrence), role=CellRole.MADD
                )
                continue
            carrier_at = next((
                index for index in range(at + 1, len(columns))
                if columns[index].tier is CellTier.MAIN
                and columns[index].status is CellStatus.DROPPED
                and columns[index].silence == occurrence
            ), None)
            if carrier_at is None:
                continue
            carrier = replace(
                _with_occurrence(columns[carrier_at], occurrence),
                role=CellRole.MADD,
            )
            columns[at] = replace(column, attached_to_column_id=carrier.id)
            columns[carrier_at] = carrier
        out.append(replace(word, columns=tuple(columns)))
    return tuple(out)


def separate_tanween_vowel_colours(
    words: tuple[CellWord, ...], facts: AnalysisFacts
) -> tuple[CellWord, ...]:
    """Keep vowel colouring on the sound, not the composite tanween glyph."""
    vowel_colours = {
        OccurrenceId(modifier.by)
        for modifier in facts.modifiers
        if isinstance(modifier, Recoloured)
        and isinstance(facts.sounds[modifier.sound].value, Vowel)
    }
    if not vowel_colours:
        return words
    return tuple(replace(word, columns=tuple(
        replace(column, rule_occurrence_ids=tuple(
            occurrence for occurrence in column.rule_occurrence_ids
            if occurrence not in vowel_colours
        )) if column.role is CellRole.TANWEEN else column
        for column in word.columns
    )) for word in words)


def keep_madd_rules_on_carriers(
    words: tuple[CellWord, ...], facts: AnalysisFacts
) -> tuple[CellWord, ...]:
    """Name a performed madd on its carrier rather than its vowel mark."""
    out = []
    for word in words:
        carrier_rules = {
            occurrence
            for column in word.columns if column.role is CellRole.MADD
            for occurrence in column.rule_occurrence_ids
            if facts.occurrences[occurrence.value].rule.value.startswith("madd_")
        }
        out.append(replace(word, columns=tuple(
            replace(column, rule_occurrence_ids=tuple(
                occurrence for occurrence in column.rule_occurrence_ids
                if occurrence not in carrier_rules
            )) if column.role is not CellRole.MADD else column
            for column in word.columns
        )))
    return tuple(out)


__all__ = [
    "keep_madd_rules_on_carriers",
    "preserve_semantic_cells",
    "separate_tanween_vowel_colours",
]
