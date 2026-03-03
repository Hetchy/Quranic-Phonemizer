from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import List, Literal, Optional
from pathlib import Path

from .parser import Parser, load_symbol_mappings
from .word import Word
from .text_matcher import TextMatcher
from .mapping import PhonemizationMapping, WordMapping, AlignmentEntry, MaddMapping
from .madd import build_madd_mappings, classify_madd_types

DATA_DIR = Path(__file__).resolve().parent / "resources"

_VOWEL_PHONEMES = {
    "a",
    "aˤ",
    "u",
    "i",
    "a:",
    "aˤ:",
    "u:",
    "i:",
}

_IDGHAM_NASALIZED_PHONEMES = {"m̃", "ñ", "w̃", "j̃"}


class Phonemizer:
    def __init__(
        self,
        db_path: str | Path = DATA_DIR / "Quran.json",
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
        self.valid_stops = {
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
        stops: List[str] = [],
        debug: bool = False,
        iqlab_phoneme: Optional[str] = None,
        ikhfaa_shafawi_phoneme: Optional[str] = None,
    ) -> PhonemizeResult:
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
            return PhonemizeResult("", "", [], [], stops, match_score)
        
        self._validate_refs(ref)

        invalid_stops = set(stops) - self.valid_stops
        if invalid_stops:
            raise ValueError(f"Invalid stop types: {invalid_stops}. Valid stops are: {self.valid_stops}")

        # Set phoneme overrides if explicitly passed (don't clear existing ones)
        if iqlab_phoneme is not None or ikhfaa_shafawi_phoneme is not None:
            from .phoneme_registry import set_phoneme_override
            if iqlab_phoneme is not None:
                set_phoneme_override("iqlab", "phoneme", iqlab_phoneme)
            if ikhfaa_shafawi_phoneme is not None:
                set_phoneme_override("ikhfaa", "shafawi_phoneme", ikhfaa_shafawi_phoneme)

        words = self.parser.load_words(ref, self.db_path, stop_types=stops)
        for word in words:
            word.phonemize()

        all_phonemes = []
        for word in words:
            all_phonemes.append(word.get_phonemes())
            if debug:
                print(word.debug_print())

        return PhonemizeResult(ref, " ".join(w.text for w in words), all_phonemes, words, stops, match_score)

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
    stops: List[str]
    match_score: float = None

    def phonemes_list(self, split: Literal["word", "verse", "both"] = "word") -> list:
        if split == "word":
            return self._nested

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
                for ph in word.get_phonemes():
                    current_verse_phonemes.append(str(ph))

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
                current_word_ph = [str(p) for p in word.get_phonemes()]
                current_words_in_verse.append(current_word_ph)

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

            for ph in word.get_phonemes():
                if have_prev_ph:
                    parts.append(phoneme_sep)
                parts.append(str(ph))
                have_prev_ph = True

            prev_verse, prev_word = cur_verse, cur_word

        return "".join(parts) or word_sep.join(
            phoneme_sep.join(word) for word in self._nested
        )

    def get_mapping(self) -> PhonemizationMapping:
        """Build the full phonemization mapping with alignment."""
        word_mappings = [word.build_mapping() for word in self._words]
        
        flat_phonemes = []
        for word in self._words:
            flat_phonemes.extend(word.get_phonemes())

        self._assign_phoneme_scoped_rules(word_mappings)
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

    def _assign_phoneme_scoped_rules(self, word_mappings: List[WordMapping]) -> None:
        """Populate per-phoneme multi-tag rules (`phoneme_rules`) on LetterMappings.

        The phonemizer computes rule context at the letter level, but some letters emit
        multiple phonemes (e.g. shaddah + tanween). This routine maps letter-scoped
        rules to the specific emitted phoneme(s) they actually affect.

        Silent-letter rules remain in `letter_rules` only (since no phoneme is emitted).
        """

        def _ensure_phoneme_rules(letter_map) -> None:
            if letter_map.phoneme_rules and len(letter_map.phoneme_rules) == len(letter_map.phonemes):
                return
            letter_map.phoneme_rules = [[] for _ in letter_map.phonemes]

        def _add_rule(letter_map, phoneme_idx: int, rule: str) -> None:
            if phoneme_idx < 0 or phoneme_idx >= len(letter_map.phonemes):
                return
            _ensure_phoneme_rules(letter_map)
            bucket = letter_map.phoneme_rules[phoneme_idx]
            if rule not in bucket:
                bucket.append(rule)

        def _tag_all(letter_map, rule: str) -> None:
            for i in range(len(letter_map.phonemes)):
                _add_rule(letter_map, i, rule)

        def _tag_first_non_vowel(letter_map, rule: str) -> None:
            for i, ph in enumerate(letter_map.phonemes):
                if ph and ph not in _VOWEL_PHONEMES:
                    _add_rule(letter_map, i, rule)
                    return

        # Flatten letter mappings in reading order for cross-letter tagging (iltiqaa).
        flat_letters: List[tuple[int, int]] = []
        for w_idx, word_map in enumerate(word_mappings):
            for l_idx, _ in enumerate(word_map.letter_mappings):
                flat_letters.append((w_idx, l_idx))

        # Pass 1: letter-local mapping (rules applied to this letter's own emitted phonemes).
        for w_idx, word_map in enumerate(word_mappings):
            for letter_map in word_map.letter_mappings:
                if not letter_map.phonemes:
                    continue
                _ensure_phoneme_rules(letter_map)

                rules = list(letter_map.letter_rules) if letter_map.letter_rules else []

                for rule in rules:
                    if rule in ("ikhfaa_noon", "ikhfaa_tanween", "ikhfaa_shafawi"):
                        for i, ph in enumerate(letter_map.phonemes):
                            if ph == "ŋ":
                                _add_rule(letter_map, i, rule)
                        continue

                    if rule in ("iqlab_noon", "iqlab_tanween"):
                        for i, ph in enumerate(letter_map.phonemes):
                            if ph == "m̃":
                                _add_rule(letter_map, i, rule)
                        continue

                    if rule == "izhar_tanween":
                        for i, ph in enumerate(letter_map.phonemes):
                            if ph == "n":
                                _add_rule(letter_map, i, rule)
                        continue

                    if rule == "noon_ghunnah":
                        for i, ph in enumerate(letter_map.phonemes):
                            if ph == "ñ":
                                _add_rule(letter_map, i, rule)
                        continue

                    if rule in ("meem_ghunnah", "idgham_shafawi"):
                        for i, ph in enumerate(letter_map.phonemes):
                            if ph == "m̃":
                                _add_rule(letter_map, i, rule)
                        continue

                    if rule in ("idgham_ghunnah_noon", "idgham_ghunnah_tanween"):
                        for i, ph in enumerate(letter_map.phonemes):
                            if ph in _IDGHAM_NASALIZED_PHONEMES:
                                _add_rule(letter_map, i, rule)
                        continue

                    if rule in ("idgham_bila_ghunnah_noon", "idgham_bila_ghunnah_tanween"):
                        # Tag the assimilated consonant on the target letter (typically lam/raa).
                        # Avoid tagging the preceding tanween short vowel by requiring a non-vowel phoneme.
                        _tag_first_non_vowel(letter_map, rule)
                        continue

                    if rule in ("raa_heavy", "raa_light", "lam_heavy", "lam_light"):
                        _tag_first_non_vowel(letter_map, rule)
                        continue

                    if rule in ("qalqala_sughra", "qalqala_kubra"):
                        # Only tag the inserted "Q" phoneme (not the consonant).
                        for i, ph in enumerate(letter_map.phonemes):
                            if ph == "Q":
                                _add_rule(letter_map, i, rule)
                        continue

                    if rule == "taa_marbuta_waqf":
                        for i, ph in enumerate(letter_map.phonemes):
                            if ph == "h":
                                _add_rule(letter_map, i, rule)
                        continue

                    if rule in ("hamza_wasl_noun", "hamza_wasl_verb_damma", "hamza_wasl_verb_kasra"):
                        _tag_all(letter_map, rule)
                        continue

                    if rule == "waqf_tanween":
                        _tag_all(letter_map, rule)
                        continue

                    # Silent rules or metadata-only rules: keep as letter_rules only.

        # Pass 2: cross-letter effects for silent hamza-wasl iltiqaa rules.
        for flat_idx, (w_idx, l_idx) in enumerate(flat_letters):
            letter_map = word_mappings[w_idx].letter_mappings[l_idx]
            rules = list(letter_map.letter_rules) if letter_map.letter_rules else []

            for rule in rules:
                if rule not in ("iltiqaa_tanween", "iltiqaa_vowel"):
                    continue
                # Find previous letter that emitted at least one phoneme.
                prev_idx = flat_idx - 1
                while prev_idx >= 0:
                    pw_idx, pl_idx = flat_letters[prev_idx]
                    prev_letter_map = word_mappings[pw_idx].letter_mappings[pl_idx]
                    if prev_letter_map.phonemes:
                        target_phoneme_idx = len(prev_letter_map.phonemes) - 1
                        _add_rule(prev_letter_map, target_phoneme_idx, rule)
                        break
                    prev_idx -= 1

    def _build_alignment(self, word_mappings: List[WordMapping]) -> List[AlignmentEntry]:
        alignment = []
        phoneme_idx = 0
        
        for word_idx, word_map in enumerate(word_mappings):
            for letter_map in word_map.letter_mappings:
                for local_idx, phoneme in enumerate(letter_map.phonemes):
                    rules: List[str] = []
                    if (
                        letter_map.phoneme_rules
                        and local_idx < len(letter_map.phoneme_rules)
                        and letter_map.phoneme_rules[local_idx]
                    ):
                        rules = list(letter_map.phoneme_rules[local_idx])
                    entry = AlignmentEntry(
                        phoneme_index=phoneme_idx,
                        phoneme=phoneme,
                        word_index=word_idx,
                        letter_index=letter_map.index,
                        source_char=letter_map.char,
                        rules=rules,
                    )
                    alignment.append(entry)
                    phoneme_idx += 1
        
        return alignment

    def show_table(self, phoneme_sep: str = "", split: Literal["word", "verse", "both"] = "word") -> "pd.DataFrame":
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for show_table(). Install with: pip install pandas")
        
        if split == "word":
            rows = []
            for word in self._words:
                clean_word_text = re.sub(r"</?rule[^>]*?>", "", word.text)
                phoneme_str = phoneme_sep.join(str(p) for p in word.get_phonemes())
                rows.append({
                    'location': word.location.location_key,
                    'word': clean_word_text,
                    'phonemes': phoneme_str,
                })
            rows.sort(key=lambda x: tuple(map(int, x['location'].split(':'))))
            return pd.DataFrame(rows)

        if split == "verse":
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
                current_list.extend(str(p) for p in word.get_phonemes())
            if current_key is not None:
                rows.append({
                    'location': current_key,
                    'text': " ".join(current_text_parts),
                    'phonemes': phoneme_sep.join(current_list),
                })
            rows.sort(key=lambda x: tuple(map(int, x['location'].split(':'))))
            return pd.DataFrame(rows)

        if split == "both":
            rows = []
            for word in self._words:
                parts = word.location.location_key.split(":")
                verse_key = ":".join(parts[:2])
                clean_word_text = re.sub(r"</?rule[^>]*?>", "", word.text)
                phoneme_str = phoneme_sep.join(str(p) for p in word.get_phonemes())
                rows.append({
                    'verse': verse_key,
                    'location': word.location.location_key,
                    'word': clean_word_text,
                    'phonemes': phoneme_str,
                })
            rows.sort(key=lambda x: tuple(map(int, x['location'].split(':'))))
            return pd.DataFrame(rows)

        raise ValueError("split must be one of: 'word', 'verse', 'both'")

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
                    phoneme_map[ref_key] = [str(p) for p in word.get_phonemes()]
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
                    current_list.extend(str(p) for p in word.get_phonemes())
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
                    current_list.append([str(p) for p in word.get_phonemes()])
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
            lines.append(f"  \"stops\": {json.dumps(self.stops, ensure_ascii=False)},")
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
                        w.writerow([ref_key, word_text, " ".join(str(p) for p in word.get_phonemes())])
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
                        current_list.extend(str(p) for p in word.get_phonemes())
                    if current_key is not None:
                        w.writerow([current_key, " ".join(current_text_parts), " ".join(current_list)])
        elif fmt == "mapping":
            mapping = self.get_mapping()
            path.write_text(mapping.to_json(), encoding="utf-8")
        else:
            raise ValueError(f"Unknown format: {fmt}")
        return path
