"""Tajweed mapping output schema and builder functions."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .tajweed_rule import TajweedRule, TajweedRuleTag
from .mapping import WordMapping, MaddMapping

# Extensions that should be split into separate entries
SPLITTABLE_EXTENSIONS = {"DAGGER_ALEF", "MINI_WAW", "MINI_YA_END"}

# Fallback chars for extensions with empty char
EXTENSION_FALLBACK_CHARS = {
    "DAGGER_ALEF": "\u0670",  # ٰ
}

MADD_TYPE_MAP = {
    None: TajweedRule.MADD_TABII,
    "wajib_muttasil": TajweedRule.MADD_WAJIB_MUTTASIL,
    "jaiz_munfasil": TajweedRule.MADD_JAIZ_MUNFASIL,
    "lazim": TajweedRule.MADD_LAZIM,
    "arid_lissukun": TajweedRule.MADD_ARID_LISSUKUN,
    "leen": TajweedRule.MADD_LEEN,
    "iwad": TajweedRule.MADD_TABII,
}

HEAVY_VOWEL_PHONEMES = {"aˤ:"}


@dataclass
class TajweedEntry:
    char: str
    source_rules: List[TajweedRule] = field(default_factory=list)
    target_rules: List[TajweedRule] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"char": self.char}
        if self.source_rules:
            d["source_rules"] = [r.value for r in self.source_rules]
        if self.target_rules:
            d["target_rules"] = [r.value for r in self.target_rules]
        return d


@dataclass
class TajweedWordMapping:
    location: str
    entries: List[TajweedEntry]
    is_stopping: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "location": self.location,
            "entries": [e.to_dict() for e in self.entries],
            "is_stopping": self.is_stopping,
        }
        return d


@dataclass
class TajweedMapping:
    ref: str
    words: List[TajweedWordMapping]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ref": self.ref,
            "words": [w.to_dict() for w in self.words],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


def _build_word_entries(word, word_map: WordMapping) -> tuple[List[TajweedEntry], Dict[int, int]]:
    """Build TajweedEntry list from a word and its mapping.

    Returns (entries, letter_to_entry_map) where letter_to_entry_map maps
    letter_index -> first entry_index for that letter.
    """
    entries: List[TajweedEntry] = []
    letter_to_entry: Dict[int, int] = {}
    # Also track extension entries: (letter_index, ext_index) -> entry_index
    extension_to_entry: Dict[tuple[int, int], int] = {}

    for i, letter in enumerate(word.letters):
        letter_to_entry[i] = len(entries)

        # Partition tajweed rules by source/target
        source_rules: List[TajweedRule] = []
        target_rules: List[TajweedRule] = []
        for tag in letter._tajweed_rules:
            if tag.is_source:
                if tag.rule not in source_rules:
                    source_rules.append(tag.rule)
            else:
                if tag.rule not in target_rules:
                    target_rules.append(tag.rule)

        # Main letter entry
        entry = TajweedEntry(
            char=letter.char,
            source_rules=list(source_rules),
            target_rules=list(target_rules),
        )
        entries.append(entry)

        # Check for splittable extensions
        if i < len(word_map.letter_mappings):
            lm = word_map.letter_mappings[i]
            for ext_idx, ext in enumerate(lm.extensions):
                if ext.name in SPLITTABLE_EXTENSIONS:
                    ext_char = ext.char or EXTENSION_FALLBACK_CHARS.get(ext.name, "")
                    if ext_char:
                        ext_entry_idx = len(entries)
                        extension_to_entry[(i, ext_idx)] = ext_entry_idx
                        entries.append(TajweedEntry(char=ext_char))

    return entries, letter_to_entry, extension_to_entry


def _apply_madd_rules(entries: List[TajweedEntry], word_map: WordMapping,
                       letter_to_entry: Dict[int, int],
                       extension_to_entry: Dict[tuple[int, int], int]) -> None:
    """Apply madd rules from madd_mappings as a post-pass."""
    for mm in word_map.madd_mappings:
        madd_rule = MADD_TYPE_MAP.get(mm.madd_type)
        if madd_rule is None:
            continue

        # Determine which entry gets the madd rule
        target_entry_idx = None

        if mm.extension_index is not None:
            # Extension split entry
            key = (mm.letter_index, mm.extension_index)
            target_entry_idx = extension_to_entry.get(key)
        elif mm.is_hamza_fathatan:
            # Hamza letter entry (last letter)
            target_entry_idx = letter_to_entry.get(mm.letter_index)
        elif mm.is_lafdh_jalalah:
            # Lam's dagger alef extension entry
            key = (mm.letter_index, 0)  # First extension of the lam
            target_entry_idx = extension_to_entry.get(key)
        else:
            # Vowel letter entry
            target_entry_idx = letter_to_entry.get(mm.letter_index)

        if target_entry_idx is not None and target_entry_idx < len(entries):
            entry = entries[target_entry_idx]
            # Madd carriers aren't truly silent — remove VOWEL_SILENT if present
            if TajweedRule.VOWEL_SILENT in entry.source_rules:
                entry.source_rules.remove(TajweedRule.VOWEL_SILENT)
            if madd_rule not in entry.source_rules:
                entry.source_rules.append(madd_rule)

            # Heavy vowel tafkheem (skip for lafdh_jalalah — lam already has it)
            if mm.phoneme in HEAVY_VOWEL_PHONEMES and not mm.is_lafdh_jalalah:
                if TajweedRule.TAFKHEEM not in entry.source_rules:
                    entry.source_rules.append(TajweedRule.TAFKHEEM)
