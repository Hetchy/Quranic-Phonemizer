"""Semantic relations retained when a reading drops their performed sound."""
from __future__ import annotations

from dataclasses import replace

from ..facts import AnalysisFacts
from .dtos import CellRole, CellStatus, CellTier, CellWord


def _has_rule(column, rule: str, facts: AnalysisFacts) -> bool:
    return any(
        facts.occurrences[occurrence.value].rule.value == rule
        for occurrence in column.rule_occurrence_ids
    )


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
            if not _has_rule(column, "waqf_silah_drop", facts):
                continue
            carrier_at = next((
                index for index in range(at + 1, len(columns))
                if columns[index].tier is CellTier.MAIN
                and columns[index].status is CellStatus.DROPPED
                and columns[index].silence == "orthographic_silence"
            ), None)
            if carrier_at is None:
                continue
            carrier = replace(columns[carrier_at], role=CellRole.MADD)
            columns[at] = replace(column, attached_to_column_id=carrier.id)
            columns[carrier_at] = carrier
        out.append(replace(word, columns=tuple(columns)))
    return tuple(out)


__all__ = ["preserve_semantic_cells"]
