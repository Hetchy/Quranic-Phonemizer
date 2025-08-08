from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import List, Literal
from pathlib import Path

from .parser import Parser, load_symbol_mappings
from .word import Word

# Data directory
DATA_DIR = Path(__file__).resolve().parent.parent / "resources"

class Phonemizer:
    def __init__(
        self,
        db_path: str | Path = DATA_DIR / "Quran.json",
        map_path: str | Path = DATA_DIR / "base_phonemes.yaml",
        special_words_path: str | Path = DATA_DIR / "special_words.yaml",
    ) -> None:
        self.db_path = str(db_path)
        self.map_path = str(map_path)
        symbol_mappings = load_symbol_mappings(map_path)
        self.parser = Parser(symbol_mappings, special_words_path)
        # Load surah/verse/word boundaries for reference validation
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

    def phonemize(
        self,
        ref: str,
        *,
        stops: List[str] = [],
        debug: bool = False,
    ) -> PhonemizeResult:
        """
        Phonemize a reference range.
        
        Parameters
        ----------
        ref : str
            Qurʾānic reference.
        stops : List[str], default []
            List of stop types to mark as boundaries.
        debug : bool, default False
            Whether to print debug information.
            
        Returns
        -------
        PhonemizeResult
            Object containing reference, text and phonemes.
        """
        # Validate reference against known bounds
        self._validate_refs(ref)

        invalid_stops = set(stops) - self.valid_stops
        if invalid_stops:
            raise ValueError(f"Invalid stop types: {invalid_stops}. Valid stops are: {self.valid_stops}")

        words = self.parser.load_words(ref, self.db_path, stop_types=stops)
        for word in words:
            word.phonemize()

        all_phonemes = []
        for word in words:
            all_phonemes.append(word.get_phonemes())
            if debug:
                print(word.debug_print())

        return PhonemizeResult(ref, " ".join(w.text for w in words), all_phonemes, words, stops)

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
            # Ensure ordering (start <= end) on (surah, verse, word); None treated as 0
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

    # ---  convenience views  ---------------------------------
    def phonemes_list(self, split: Literal["word", "verse", "both"] = "word") -> list:
        """
        Return phonemes grouped according to the requested split mode.

        split="word":  List[List[str]] — one list per word (default)
        split="verse": List[List[str]] — one list per verse (all phonemes in that verse)
        split="both":  List[List[List[str]]] — per verse, per word
        """
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
        """Return the full text with Arabic verse numbers like (١) between verses."""
        parts: list[str] = []
        prev_verse: str | None = None
        for word in self._words:
            cur_verse = str(word.location.ayah_num)
            if prev_verse is not None and cur_verse != prev_verse:
                # Insert Arabic-indic verse number in parentheses
                arabic_digits = {
                    '0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
                    '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩',
                }
                arabic_num = ''.join(arabic_digits[d] for d in prev_verse)
                parts.append(f" ({arabic_num}) ")
            parts.append(re.sub(r"</?rule[^>]*?>", "", word.text))
            prev_verse = cur_verse
        # Append the final verse number
        if prev_verse is not None:
            arabic_digits = {
                '0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
                '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩',
            }
            arabic_num = ''.join(arabic_digits[d] for d in prev_verse)
            parts.append(f" ({arabic_num}) ")
        return " ".join(parts)

    def phonemes_str(
        self,
        phoneme_sep: str = "",
        word_sep:    str = " ",
        verse_sep:   str = "\n",
    ) -> str:
        """
        Flatten phonemes to a single string.

        • phoneme_sep – between adjacent phonemes
        • word_sep    – between words  (falls back to phoneme_sep if blank)
        • verse_sep   – between verses (falls back to word_sep → phoneme_sep if blank)
        """
        parts: list[str] = []
        prev_verse: str | None = None
        prev_word:  str | None = None
        have_prev_ph = False           # have we just emitted a phoneme?

        def _add_sep(sep: str) -> None:
            """Append a separator, avoiding consecutive duplicates."""
            if sep and (not parts or parts[-1] != sep):
                parts.append(sep)

        for word in self._words:
            cur_verse = str(word.location.ayah_num)
            cur_word = str(word.location.word_num)

            # -------- verse boundary --------------------------------------
            if prev_verse is not None and cur_verse != prev_verse:
                chosen = verse_sep if verse_sep else (word_sep if word_sep else phoneme_sep)
                _add_sep(chosen)
                have_prev_ph = False

            # -------- word boundary ---------------------------------------
            elif prev_word is not None and cur_word != prev_word:
                chosen = word_sep if word_sep else phoneme_sep
                _add_sep(chosen)
                have_prev_ph = False

            # -------- emit phonemes ---------------------------------------
            for ph in word.get_phonemes():
                if have_prev_ph:
                    parts.append(phoneme_sep)
                parts.append(str(ph))
                have_prev_ph = True

            prev_verse, prev_word = cur_verse, cur_word

        return "".join(parts) or word_sep.join(
            phoneme_sep.join(word) for word in self._nested
        )

    def show_table(self, phoneme_sep: str = "", split: Literal["word", "verse", "both"] = "word") -> "pd.DataFrame":
        """
        Create a pandas DataFrame according to the split strategy.

        - split="word":  one row per word; columns: location (s:v:w), word, phonemes
        - split="verse": one row per verse; columns: location (s:v), text, phonemes
        - split="both":  one row per word; columns: verse (s:v), location (s:v:w), word, phonemes
        """
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
        """Persist the result (ref + text + phonemes) to *path*.

        - fmt: "json" or "csv"
        - split: "word" | "verse" | "both". For CSV, "both" is not supported.
        JSON layout:
          { "ref": <range>, "text": <full text>, "phonemes": { <ref>: [<ph> ...], ... } }
          Values are rendered on a single line (newline per list only).
        """
        path = Path(path)

        def _clean_text(s: str) -> str:
            return re.sub(r"</?rule[^>]*?>", "", s)

        if fmt == "json":
            # Build mappings: ref -> phoneme list(s), and ref -> text
            phoneme_map: dict[str, list] = {}
            text_map: dict[str, str] = {}
            if split == "word":
                for word in self._words:
                    ref_key = word.location.location_key  # s:v:w
                    phoneme_map[ref_key] = [str(p) for p in word.get_phonemes()]
                    text_map[ref_key] = _clean_text(word.text)
            elif split == "verse":
                current_key: str | None = None
                current_list: list[str] = []
                current_text_parts: list[str] = []
                for word in self._words:
                    parts = word.location.location_key.split(":")
                    verse_key = ":".join(parts[:2])  # s:v
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
                    verse_key = ":".join(parts[:2])  # s:v
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

            # Manual formatting to keep each list on a single line
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
                        ref_key = word.location.location_key  # s:v:w
                        word_text = _clean_text(word.text)
                        w.writerow([ref_key, word_text, " ".join(str(p) for p in word.get_phonemes())])
                elif split == "verse":
                    current_key: str | None = None
                    current_text_parts: list[str] = []
                    current_list: list[str] = []
                    for word in self._words:
                        parts = word.location.location_key.split(":")
                        verse_key = ":".join(parts[:2])  # s:v
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
        else:
            raise ValueError(f"Unknown format: {fmt}")
        return path