"""Fold written sukun marks into their visible host cell."""
from __future__ import annotations

from dataclasses import replace

from .dtos import CellColumn, CellRole, CellStatus, CellTier, CellWord


def fold_sukun(word: CellWord) -> CellWord:
    hosts = {c.id.value: c for c in word.columns if c.tier is CellTier.MAIN}
    folded: dict[int, CellColumn] = {}
    removed: set[int] = set()
    remapped: dict[int, int] = {}
    previous_main: CellColumn | None = None
    for mark in word.columns:
        if mark.tier is CellTier.MAIN:
            previous_main = mark
        if (
            mark.role is not CellRole.SUKUN and mark.text != "ْ"
        ) or mark.attached_to_column_id is None:
            continue
        host_id = mark.attached_to_column_id.value
        # The Warsh source writes the final sukun after a silent separating
        # alif. Its generic written-on relation points back to the last sounded
        # consonant; the cell projection keeps it inside that written alif.
        if (
            mark.text == "ْ"
            and previous_main is not None
            and previous_main.status is CellStatus.DROPPED
            and "ا" in previous_main.text
        ):
            host_id = previous_main.id.value
        host = folded.get(host_id) or hosts[host_id]
        folded[host.id.value] = replace(
            host,
            text=host.text + mark.text,
            source_character_ids=(*host.source_character_ids, *mark.source_character_ids),
            source_unit_ids=(*host.source_unit_ids, *mark.source_unit_ids),
            rule_occurrence_ids=tuple(dict.fromkeys(
                (*host.rule_occurrence_ids, *mark.rule_occurrence_ids)
            )),
            owned_sound_ids=tuple(dict.fromkeys(
                (*host.owned_sound_ids, *mark.owned_sound_ids)
            )),
            presented_sound_ids=tuple(dict.fromkeys(
                (*host.presented_sound_ids, *mark.presented_sound_ids)
            )),
        )
        removed.add(mark.id.value)
        remapped[mark.id.value] = host.id.value
    return replace(
        word,
        columns=tuple(
            folded.get(c.id.value, c)
            for c in word.columns if c.id.value not in removed
        ),
        sounds=tuple(replace(sound, column_ids=tuple(dict.fromkeys(
            type(column)(remapped.get(column.value, column.value))
            for column in sound.column_ids
        ))) for sound in word.sounds),
    )


__all__ = ["fold_sukun"]
