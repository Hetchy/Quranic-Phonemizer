"""Written-mark composition and reading-specific cell glyph changes."""
from __future__ import annotations

from dataclasses import replace

from ...model.performance import Consonant
from ...orthography.write import Pen
from ..facts import AnalysisFacts
from ..ids import CellColumnId
from .dtos import CellColumn, CellRole, CellStatus, CellTier, CellWord

DAGGER_ALIF = "ٰ"
MADD_SIGN = "ٓ"
MAQSURA = "ى"
TATWEEL = "ـ"


def _merged_carrier(base: CellColumn, mark: CellColumn) -> CellColumn:
    owned = tuple(dict.fromkeys((*base.owned_sound_ids, *mark.owned_sound_ids)))
    presented = tuple(dict.fromkeys(
        (*base.presented_sound_ids, *mark.presented_sound_ids)
    ))
    active = bool(owned or presented)
    return replace(
        base,
        role=CellRole.MADD if CellRole.MADD in {base.role, mark.role} else base.role,
        text=base.text + mark.text,
        source_character_ids=(*base.source_character_ids, *mark.source_character_ids),
        source_unit_ids=(*base.source_unit_ids, *mark.source_unit_ids),
        status=CellStatus.PRESENT if active else base.status,
        rule_occurrence_ids=tuple(dict.fromkeys(
            (*base.rule_occurrence_ids, *mark.rule_occurrence_ids)
        )),
        silence=None if active else base.silence,
        owned_sound_ids=owned,
        presented_sound_ids=presented,
    )


def _remap_column(word: CellWord, removed: CellColumnId,
                  kept: CellColumnId) -> CellWord:
    columns = tuple(replace(
        col,
        attached_to_column_id=(
            kept if col.attached_to_column_id == removed else col.attached_to_column_id
        ),
    ) for col in word.columns if col.id != removed)
    sounds = tuple(replace(sound, column_ids=tuple(dict.fromkeys(
        kept if col == removed else col for col in sound.column_ids
    ))) for sound in word.sounds)
    return replace(word, columns=columns, sounds=sounds)


def fold_maqsura_daggers(word: CellWord) -> CellWord:
    """Compose a maqsura and its riding dagger/maddah as one carrier."""
    index = 0
    while index + 1 < len(word.columns):
        base, mark = word.columns[index:index + 2]
        if (
            base.tier is CellTier.MAIN and mark.tier is CellTier.MAIN
            and base.text.endswith(MAQSURA) and mark.text.startswith(DAGGER_ALIF)
        ):
            folded = _merged_carrier(base, mark)
            columns = tuple(folded if col.id == base.id else col for col in word.columns)
            word = _remap_column(replace(word, columns=columns), mark.id, base.id)
            continue
        index += 1
    return word


def clean_structural_marks(word: CellWord) -> CellWord:
    """A tatweel positions source ink; it is not a standalone rendered mark."""
    return replace(word, columns=tuple(
        replace(col, text=col.text.replace(TATWEEL, ""))
        if col.role in {CellRole.HARAKA, CellRole.TANWEEN} else col
        for col in word.columns
    ))


def _rule_names(col: CellColumn, facts: AnalysisFacts) -> set[str]:
    return {
        facts.occurrences[occurrence.value].rule.value
        for occurrence in col.rule_occurrence_ids
    }


def recover_nasal_sukun(words, facts: AnalysisFacts, pen: Pen):
    """Show the sukun reclaimed when waqf cancels a cross-word nasal rule."""
    rules = {"izhar", "izhar_shafawi"}
    return tuple(replace(word, columns=tuple(
        replace(
            col, text=col.text + pen.role("sukun"),
            status=(CellStatus.REPLACED
                    if col.status is CellStatus.PRESENT else col.status),
        ) if (
            col.tier is CellTier.MAIN and col.role is CellRole.LETTER
            and not col.text.endswith(pen.role("sukun"))
            and bool(_rule_names(col, facts) & rules)
            and any(isinstance(facts.sounds[s.value].value, Consonant)
                    for s in col.owned_sound_ids)
        ) else col for col in word.columns
    )) for word in words)


def transform_plain_madd(words, facts: AnalysisFacts):
    """A munfasil shortened to tabii at waqf no longer displays a maddah."""
    return tuple(replace(word, columns=tuple(
        replace(
            col, text=col.text.replace(MADD_SIGN, ""),
            status=(CellStatus.REPLACED
                    if col.status is CellStatus.PRESENT else col.status),
        ) if (
            col.role is CellRole.MADD and MADD_SIGN in col.text
            and "madd_tabii" in _rule_names(col, facts)
            and not any(name != "madd_tabii" and name.startswith("madd_")
                        for name in _rule_names(col, facts))
        ) else col for col in word.columns
    )) for word in words)


__all__ = [
    "DAGGER_ALIF",
    "MAQSURA",
    "clean_structural_marks",
    "fold_maqsura_daggers",
    "recover_nasal_sukun",
    "transform_plain_madd",
]
