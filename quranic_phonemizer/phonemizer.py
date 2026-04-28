from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import List, Literal, Optional
from pathlib import Path

from .parser import Parser, load_symbol_mappings
from .word import Word
from .text_matcher import TextMatcher
from .mapping import PhonemizationMapping, WordMapping, AlignmentEntry
from .madd import build_madd_mappings, classify_madd_types
from .phonetic_text import build_phonetic_text
from .tajweed_rule import TajweedRule
from .tajweed_mapping import (
    TajweedMapping, TajweedWordMapping, TajweedEntry,
    _build_word_entries, _apply_madd_rules,
)
from .specials import get_tajweed_mapping
from .letter_phoneme_mapping import (
    FlatMappingResult, build_letter_phoneme_mapping,
)

DATA_DIR = Path(__file__).resolve().parent / "resources"


def _format_text_table(rows: list[dict]) -> str:
    if not rows:
        return ""
    columns = list(rows[0].keys())
    widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in columns}
    sep = "+".join("-" * (widths[c] + 2) for c in columns)
    sep = f"+{sep}+"
    header = "| " + " | ".join(c.ljust(widths[c]) for c in columns) + " |"
    body = [
        "| " + " | ".join(str(r.get(c, "")).ljust(widths[c]) for c in columns) + " |"
        for r in rows
    ]
    return "\n".join([sep, header, sep, *body, sep])


class Phonemizer:
    def __init__(
        self,
        db_path: str | Path = DATA_DIR / "quran_db.bin",
        map_path: str | Path = DATA_DIR / "base_phonemes.yaml",
        special_words_path: str | Path = DATA_DIR / "special_words.yaml",
        extra_symbols: Optional[dict[str, dict]] = None,
    ) -> None:
        self.db_path = str(db_path)
        self.map_path = str(map_path)
        self.special_words_path = str(special_words_path)
        symbol_mappings = load_symbol_mappings(map_path)
        
        # Merge extra symbols if provided
        if extra_symbols:
            for category, items in extra_symbols.items():
                if category not in symbol_mappings:
                    symbol_mappings[category] = {}
                symbol_mappings[category].update(items)
        
        self.parser = Parser(symbol_mappings, special_words_path)
        self.text_matcher = TextMatcher(db_path, symbol_mappings)
        with (DATA_DIR / "surah_info.json").open("r", encoding="utf-8") as fh:
            self._surah_info: dict[str, dict] = json.load(fh)
        self.valid_stop_signs = {
            "verse",
            "preferred_continue",
            "preferred_stop", 
            "optional_stop",
            "compulsory_stop",
            "prohibited_stop",
        }

    def _is_text_reference(self, ref: str) -> bool:
        ref = ref.strip()
        traditional_pattern = r'^[\d:\s-]+$'
        
        if re.match(traditional_pattern, ref):
            try:
                if "-" in ref:
                    left, right = [p.strip() for p in ref.split("-", 1)]
                    self._parse_traditional_endpoint(left)
                    self._parse_traditional_endpoint(right)
                else:
                    self._parse_traditional_endpoint(ref)
                return False
            except:
                pass
        
        return True
    
    def _parse_traditional_endpoint(self, text: str) -> tuple[int, int | None, int | None]:
        parts = text.strip().split(":")
        if not 1 <= len(parts) <= 3:
            raise ValueError(f"Invalid reference endpoint: '{text}'")
        try:
            surah = int(parts[0])
            verse = int(parts[1]) if len(parts) >= 2 and parts[1] != "" else None
            word = int(parts[2]) if len(parts) == 3 and parts[2] != "" else None
        except ValueError:
            raise ValueError(f"Reference components must be integers: '{text}'")
        return surah, verse, word

    def phonemize(
        self,
        ref: str = None,
        *,
        ref_text: str = None,
        stop_signs: List[str] = [],
        stop_refs: List[str] = [],
        debug: bool = False,
        iqlab_phoneme: Optional[str] = None,
        ikhfaa_shafawi_phoneme: Optional[str] = None,
        mode: Literal["full", "simple"] = "full",
    ) -> PhonemizeResult:
        if mode not in ("full", "simple"):
            raise ValueError(f"Invalid mode: {mode!r}. Must be 'full' or 'simple'.")
        if ref is None and ref_text is None:
            raise ValueError("Either 'ref' or 'ref_text' must be provided")
        
        match_score = None
        failed_match = False
        
        if ref_text is not None:
            if ref is not None:
                if self._is_text_reference(ref):
                    raise ValueError("When both 'ref' and 'ref_text' are provided, 'ref' must be a traditional reference format (e.g., '2', '2:1', '2:1-2:5')")
                
                if debug:
                    print(f"Searching for text '{ref_text}' within scope '{ref}'")
                ref_result, match_score = self.text_matcher.find_matching_range_scoped_with_score_space_robust(ref_text, ref)
                if ref_result is None:
                    failed_match = True
                    if debug:
                        print(f"No good match found within scope '{ref}' (score: {match_score:.3f}) - will return null phonemes")
                else:
                    ref = ref_result
                    if debug:
                        print(f"Found scoped match: {ref} (score: {match_score:.3f})")
            else:
                if debug:
                    print(f"Searching for text '{ref_text}' in entire database")
                ref_result, match_score = self.text_matcher.find_matching_range_with_score(ref_text)
                if ref_result is None:
                    failed_match = True
                    if debug:
                        print(f"No good match found in database (score: {match_score:.3f}) - will return null phonemes")
                else:
                    ref = ref_result
                    if debug:
                        print(f"Found match: {ref} (score: {match_score:.3f})")
        else:
            original_ref = ref
            if self._is_text_reference(ref):
                if debug:
                    print(f"Detected text reference: {ref}")
                ref_result, match_score = self.text_matcher.find_matching_range_with_score(ref)
                if ref_result is None:
                    failed_match = True
                    if debug:
                        print(f"No good match found for text (score: {match_score:.3f}) - will return null phonemes")
                else:
                    ref = ref_result
                    if debug:
                        print(f"Converted to traditional reference: {ref} (score: {match_score:.3f})")
        
        if failed_match:
            return PhonemizeResult("", "", [], [], stop_signs, stop_refs, match_score, mode)
        
        self._validate_refs(ref)

        invalid_stops = set(stop_signs) - self.valid_stop_signs
        if invalid_stops:
            raise ValueError(f"Invalid stop sign types: {invalid_stops}. Valid stop signs are: {self.valid_stop_signs}")

        # Set phoneme overrides if explicitly passed (don't clear existing ones)
        if iqlab_phoneme is not None or ikhfaa_shafawi_phoneme is not None:
            from .phoneme_registry import set_phoneme_override
            if iqlab_phoneme is not None:
                set_phoneme_override("iqlab", "phoneme", iqlab_phoneme)
            if ikhfaa_shafawi_phoneme is not None:
                set_phoneme_override("ikhfaa", "shafawi_phoneme", ikhfaa_shafawi_phoneme)

        words = self.parser.load_words(ref, self.db_path, stop_signs=stop_signs, stop_refs=stop_refs)
        for word in words:
            word.phonemize()
        for word in words:
            word.apply_phoneme_overrides()

        all_phonemes = []
        for word in words:
            all_phonemes.append(word.get_phonemes())
            if debug:
                print(word.debug_print())

        return PhonemizeResult(ref, " ".join(w.text for w in words), all_phonemes, words, stop_signs, stop_refs, match_score, mode)

    def _validate_refs(self, ref: str) -> None:
        ref = ref.strip()

        def parse_endpoint(text: str) -> tuple[int, int | None, int | None]:
            parts = text.strip().split(":")
            if not 1 <= len(parts) <= 3:
                raise ValueError(f"Invalid reference endpoint: '{text}'")
            try:
                surah = int(parts[0])
                verse = int(parts[1]) if len(parts) >= 2 and parts[1] != "" else None
                word  = int(parts[2]) if len(parts) == 3 and parts[2] != "" else None
            except ValueError:
                raise ValueError(f"Reference components must be integers: '{text}'")
            return surah, verse, word

        def check_bounds(surah: int, verse: int | None, word: int | None) -> None:
            s_key = str(surah)
            if s_key not in self._surah_info:
                raise ValueError(f"Surah out of range: {surah}")
            s_info = self._surah_info[s_key]
            if verse is not None:
                if verse < 1 or verse > int(s_info["num_verses"]):
                    raise ValueError(f"Verse out of range: {surah}:{verse}")
                if word is not None:
                    v_info = s_info["verses"][verse - 1]
                    max_words = int(v_info["num_words"])
                    if word < 1 or word > max_words:
                        raise ValueError(f"Word out of range: {surah}:{verse}:{word} (max {max_words})")

        if "-" in ref:
            left, right = [p.strip() for p in ref.split("-", 1)]
            s1, v1, w1 = parse_endpoint(left)
            s2, v2, w2 = parse_endpoint(right)
            check_bounds(s1, v1, w1)
            check_bounds(s2, v2, w2)
            def norm(t: tuple[int, int | None, int | None]) -> tuple[int, int, int]:
                a, b, c = t
                return a, (b if b is not None else 0), (c if c is not None else 0)
            if norm((s1, v1, w1)) > norm((s2, v2, w2)):
                raise ValueError(f"Invalid range: start '{left}' comes after end '{right}'")
        else:
            s, v, w = parse_endpoint(ref)
            check_bounds(s, v, w)


@dataclass(slots=True)
class PhonemizeResult:
    ref: str
    _text: str
    _nested: List[List[str]]
    _words: List[Word]
    stop_signs: List[str]
    stop_refs: List[str]
    match_score: float = None
    mode: Literal["full", "simple"] = "full"

    def _view(self, phonemes) -> list[str]:
        """Return phonemes as a plain list of strings, applying simple-mode collapse when enabled.

        Simple mode only affects the raw phoneme output views
        (phonemes_list / phonemes_str / show_table / save). Structural outputs
        (tajweed_mappings, get_mapping, letter_phoneme_mappings) use the full
        phoneme vocabulary so alignment and rule indices remain consistent.
        """
        if self.mode == "simple":
            from .simple_mode import collapse_phonemes
            return collapse_phonemes(phonemes)
        return [str(p) for p in phonemes]

    def phonemes_list(self, split: Literal["word", "verse", "both"] = "word") -> list:
        if split == "word":
            return [self._view(word_ph) for word_ph in self._nested]

        if split == "verse":
            verses: list[list[str]] = []
            current_verse_id: str | None = None
            current_verse_phonemes: list[str] = []

            for word in self._words:
                verse_id = str(word.location.ayah_num)
                if current_verse_id is None:
                    current_verse_id = verse_id
                if verse_id != current_verse_id:
                    verses.append(current_verse_phonemes)
                    current_verse_phonemes = []
                    current_verse_id = verse_id
                current_verse_phonemes.extend(self._view(word.get_phonemes()))

            if current_verse_phonemes:
                verses.append(current_verse_phonemes)
            return verses

        if split == "both":
            verses_words: list[list[list[str]]] = []
            current_verse_id: str | None = None
            current_words_in_verse: list[list[str]] = []

            for word in self._words:
                verse_id = str(word.location.ayah_num)
                if current_verse_id is None:
                    current_verse_id = verse_id
                if verse_id != current_verse_id:
                    verses_words.append(current_words_in_verse)
                    current_words_in_verse = []
                    current_verse_id = verse_id
                current_words_in_verse.append(self._view(word.get_phonemes()))

            if current_words_in_verse:
                verses_words.append(current_words_in_verse)
            return verses_words

        raise ValueError("split must be one of: 'word', 'verse', 'both'")

    def text(self) -> str:
        parts: list[str] = []
        prev_verse: str | None = None
        for word in self._words:
            cur_verse = str(word.location.ayah_num)
            if prev_verse is not None and cur_verse != prev_verse:
                arabic_digits = {
                    '0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
                    '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩',
                }
                arabic_num = ''.join(arabic_digits[d] for d in prev_verse)
                parts.append(f" {arabic_num} ")
            parts.append(re.sub(r"</?rule[^>]*?>", "", word.text))
            prev_verse = cur_verse
        if prev_verse is not None:
            arabic_digits = {
                '0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
                '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩',
            }
            arabic_num = ''.join(arabic_digits[d] for d in prev_verse)
            parts.append(f" {arabic_num} ")
        return " ".join(parts)

    def phonetic_text(self, word_sep: str = " ", verse_sep: str = "\n") -> str | None:
        if not self._words:
            return None
        return build_phonetic_text(self._words, word_sep=word_sep, verse_sep=verse_sep)

    def phonemes_str(
        self,
        phoneme_sep: str = "",
        word_sep:    str = " ",
        verse_sep:   str = "\n",
    ) -> str | None:
        if not self._words:
            return None
        parts: list[str] = []
        prev_verse: str | None = None
        prev_word:  str | None = None
        have_prev_ph = False

        def _add_sep(sep: str) -> None:
            if sep and (not parts or parts[-1] != sep):
                parts.append(sep)

        for word in self._words:
            cur_verse = str(word.location.ayah_num)
            cur_word = str(word.location.word_num)

            if prev_verse is not None and cur_verse != prev_verse:
                _add_sep(word_sep if word_sep else phoneme_sep)
                _add_sep(verse_sep if verse_sep else (word_sep if word_sep else phoneme_sep))
                have_prev_ph = False

            elif prev_word is not None and cur_word != prev_word:
                chosen = word_sep if word_sep else phoneme_sep
                _add_sep(chosen)
                have_prev_ph = False

            for ph in self._view(word.get_phonemes()):
                if have_prev_ph:
                    parts.append(phoneme_sep)
                parts.append(ph)
                have_prev_ph = True

            prev_verse, prev_word = cur_verse, cur_word

        return "".join(parts) or word_sep.join(
            phoneme_sep.join(self._view(word)) for word in self._nested
        )

    def tajweed_mappings(self) -> TajweedMapping:
        """Build structured tajweed rule annotations."""
        # Pass 1: build word mappings for cross-word madd detection
        word_maps: dict[str, WordMapping] = {}
        all_word_maps: list[WordMapping] = []
        for word in self._words:
            location_key = word.location.location_key
            if get_tajweed_mapping(location_key) is not None:
                continue
            word_map = word.build_mapping()
            word_maps[location_key] = word_map
            all_word_maps.append(word_map)

        build_madd_mappings(all_word_maps)
        classify_madd_types(all_word_maps)

        # Pass 2: build tajweed entries per word
        tajweed_words: list[TajweedWordMapping] = []

        for word in self._words:
            location_key = word.location.location_key

            # Check for special words with YAML-defined tajweed_mapping
            yaml_tm = get_tajweed_mapping(location_key)
            if yaml_tm is not None:
                for sub_idx, sub_word in enumerate(yaml_tm):
                    entries = []
                    for entry_data in sub_word.get("entries", []):
                        source_rules = [TajweedRule(r) for r in entry_data.get("source_rules", [])]
                        target_rules = [TajweedRule(r) for r in entry_data.get("target_rules", [])]
                        entries.append(TajweedEntry(
                            char=entry_data["char"],
                            source_rules=source_rules,
                            target_rules=target_rules,
                        ))
                    is_stop = word.is_stopping and (sub_idx == len(yaml_tm) - 1)
                    sub_loc = f"{location_key}:{sub_idx}" if len(yaml_tm) > 1 else location_key
                    tajweed_words.append(TajweedWordMapping(location=sub_loc, entries=entries, is_stopping=is_stop))
                continue

            # Normal word: build entries from letters + tajweed rules
            word_map = word_maps[location_key]
            entries, letter_to_entry, extension_to_entry = _build_word_entries(word, word_map)

            # Apply madd post-pass
            _apply_madd_rules(entries, word_map, letter_to_entry, extension_to_entry)

            tajweed_words.append(TajweedWordMapping(
                location=location_key, entries=entries, is_stopping=word.is_stopping,
            ))

        return TajweedMapping(ref=self.ref, words=tajweed_words)

    def letter_phoneme_mappings(self, validate_result: bool = False) -> FlatMappingResult:
        """Build flat letter-to-phoneme mappings for forced alignment."""
        mapping = self.get_mapping()
        flat = build_letter_phoneme_mapping(mapping)

        result = FlatMappingResult(entries=flat, mapping=mapping, ref=self.ref)

        if validate_result:
            violations = result.validate()
            if violations:
                raise ValueError("Validation failed:\n" + "\n".join(violations))

        return result

    def get_mapping(self) -> PhonemizationMapping:
        """Build the full phonemization mapping with alignment."""
        word_mappings = [word.build_mapping() for word in self._words]
        
        flat_phonemes = []
        for word in self._words:
            flat_phonemes.extend(word.get_phonemes())

        build_madd_mappings(word_mappings)
        classify_madd_types(word_mappings)
        alignment = self._build_alignment(word_mappings)
        
        clean_text = re.sub(r"</?rule[^>]*?>", "", self._text)
        
        return PhonemizationMapping(
            ref=self.ref,
            text=clean_text,
            words=word_mappings,
            phoneme_sequence=flat_phonemes,
            alignment=alignment,
        )

    def _build_alignment(self, word_mappings: List[WordMapping]) -> List[AlignmentEntry]:
        alignment = []
        phoneme_idx = 0

        for word_idx, word_map in enumerate(word_mappings):
            for letter_map in word_map.letter_mappings:
                for phoneme in letter_map.phonemes:
                    entry = AlignmentEntry(
                        phoneme_index=phoneme_idx,
                        phoneme=phoneme,
                        word_index=word_idx,
                        letter_index=letter_map.index,
                        source_char=letter_map.char,
                    )
                    alignment.append(entry)
                    phoneme_idx += 1

        return alignment

    def show_table(self, phoneme_sep: str = "", split: Literal["word", "verse", "both"] = "word"):
        if split == "word":
            rows = []
            for word in self._words:
                clean_word_text = re.sub(r"</?rule[^>]*?>", "", word.text)
                phoneme_str = phoneme_sep.join(self._view(word.get_phonemes()))
                rows.append({
                    'location': word.location.location_key,
                    'word': clean_word_text,
                    'phonemes': phoneme_str,
                })
            rows.sort(key=lambda x: tuple(map(int, x['location'].split(':'))))
        elif split == "verse":
            rows = []
            current_key: str | None = None
            current_text_parts: list[str] = []
            current_list: list[str] = []
            for word in self._words:
                parts = word.location.location_key.split(":")
                verse_key = ":".join(parts[:2])
                if current_key is None:
                    current_key = verse_key
                if verse_key != current_key:
                    rows.append({
                        'location': current_key,
                        'text': " ".join(current_text_parts),
                        'phonemes': phoneme_sep.join(current_list),
                    })
                    current_key = verse_key
                    current_text_parts = []
                    current_list = []
                current_text_parts.append(re.sub(r"</?rule[^>]*?>", "", word.text))
                current_list.extend(self._view(word.get_phonemes()))
            if current_key is not None:
                rows.append({
                    'location': current_key,
                    'text': " ".join(current_text_parts),
                    'phonemes': phoneme_sep.join(current_list),
                })
            rows.sort(key=lambda x: tuple(map(int, x['location'].split(':'))))
        elif split == "both":
            rows = []
            for word in self._words:
                parts = word.location.location_key.split(":")
                verse_key = ":".join(parts[:2])
                clean_word_text = re.sub(r"</?rule[^>]*?>", "", word.text)
                phoneme_str = phoneme_sep.join(self._view(word.get_phonemes()))
                rows.append({
                    'verse': verse_key,
                    'location': word.location.location_key,
                    'word': clean_word_text,
                    'phonemes': phoneme_str,
                })
            rows.sort(key=lambda x: tuple(map(int, x['location'].split(':'))))
        else:
            raise ValueError("split must be one of: 'word', 'verse', 'both'")

        try:
            import pandas as pd
            return pd.DataFrame(rows)
        except ImportError:
            print(_format_text_table(rows))
            return rows

    def save(self, path: str | Path, *, fmt, split: Literal["word", "verse", "both"] = "word") -> Path:
        path = Path(path)

        def _clean_text(s: str) -> str:
            return re.sub(r"</?rule[^>]*?>", "", s)

        if fmt == "json":
            phoneme_map: dict[str, list] = {}
            text_map: dict[str, str] = {}
            if split == "word":
                for word in self._words:
                    ref_key = word.location.location_key
                    phoneme_map[ref_key] = self._view(word.get_phonemes())
                    text_map[ref_key] = _clean_text(word.text)
            elif split == "verse":
                current_key: str | None = None
                current_list: list[str] = []
                current_text_parts: list[str] = []
                for word in self._words:
                    parts = word.location.location_key.split(":")
                    verse_key = ":".join(parts[:2])
                    if current_key is None:
                        current_key = verse_key
                    if verse_key != current_key:
                        phoneme_map[current_key] = current_list
                        text_map[current_key] = " ".join(current_text_parts)
                        current_list = []
                        current_text_parts = []
                        current_key = verse_key
                    current_list.extend(self._view(word.get_phonemes()))
                    current_text_parts.append(_clean_text(word.text))
                if current_key is not None:
                    phoneme_map[current_key] = current_list
                    text_map[current_key] = " ".join(current_text_parts)
            elif split == "both":
                current_key: str | None = None
                current_list: list[list[str]] = []
                current_text_parts: list[str] = []
                for word in self._words:
                    parts = word.location.location_key.split(":")
                    verse_key = ":".join(parts[:2])
                    if current_key is None:
                        current_key = verse_key
                    if verse_key != current_key:
                        phoneme_map[current_key] = current_list
                        text_map[current_key] = " ".join(current_text_parts)
                        current_list = []
                        current_text_parts = []
                        current_key = verse_key
                    current_list.append(self._view(word.get_phonemes()))
                    current_text_parts.append(_clean_text(word.text))
                if current_key is not None:
                    phoneme_map[current_key] = current_list
                    text_map[current_key] = " ".join(current_text_parts)
            else:
                raise ValueError("split must be one of: 'word', 'verse', 'both'")

            lines: list[str] = []
            lines.append("{")
            lines.append(f"  \"ref\": {json.dumps(self.ref, ensure_ascii=False)},")
            lines.append(f"  \"text\": {json.dumps(self._text, ensure_ascii=False)},")
            lines.append(f"  \"stop_signs\": {json.dumps(self.stop_signs, ensure_ascii=False)},")
            lines.append(f"  \"stop_refs\": {json.dumps(self.stop_refs, ensure_ascii=False)},")
            lines.append("  \"texts\": {")
            text_items = list(text_map.items())
            for idx, (k, v) in enumerate(text_items):
                comma = "," if idx < len(text_items) - 1 else ""
                v_str = json.dumps(v, ensure_ascii=False)
                lines.append(f"    \"{k}\": {v_str}{comma}")
            lines.append("  },")
            lines.append("  \"phonemes\": {")
            items = list(phoneme_map.items())
            for idx, (k, v) in enumerate(items):
                comma = "," if idx < len(items) - 1 else ""
                v_str = json.dumps(v, ensure_ascii=False, separators=(",", ":"))
                lines.append(f"    \"{k}\": {v_str}{comma}")
            lines.append("  }")
            lines.append("}")
            path.write_text("\n".join(lines), encoding="utf-8")
        elif fmt == "csv":
            if split == "both":
                raise ValueError("CSV format does not support split='both'; use fmt='json' instead")
            import csv
            with path.open("w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(["ref", "text", "phoneme_seq"])
                if split == "word":
                    for word in self._words:
                        ref_key = word.location.location_key
                        word_text = _clean_text(word.text)
                        w.writerow([ref_key, word_text, " ".join(self._view(word.get_phonemes()))])
                elif split == "verse":
                    current_key: str | None = None
                    current_text_parts: list[str] = []
                    current_list: list[str] = []
                    for word in self._words:
                        parts = word.location.location_key.split(":")
                        verse_key = ":".join(parts[:2])
                        if current_key is None:
                            current_key = verse_key
                        if verse_key != current_key:
                            w.writerow([current_key, " ".join(current_text_parts), " ".join(current_list)])
                            current_key = verse_key
                            current_text_parts = []
                            current_list = []
                        current_text_parts.append(_clean_text(word.text))
                        current_list.extend(self._view(word.get_phonemes()))
                    if current_key is not None:
                        w.writerow([current_key, " ".join(current_text_parts), " ".join(current_list)])
        elif fmt == "mapping":
            mapping = self.get_mapping()
            path.write_text(mapping.to_json(), encoding="utf-8")
        elif fmt == "tajweed":
            path.write_text(self.tajweed_mappings().to_json(), encoding="utf-8")
        elif fmt == "letter_phoneme":
            path.write_text(self.letter_phoneme_mappings().to_json(), encoding="utf-8")
        else:
            raise ValueError(f"Unknown format: {fmt}")
        return path
