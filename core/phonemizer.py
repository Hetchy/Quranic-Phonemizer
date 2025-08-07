from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import List
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

        return PhonemizeResult(ref, " ".join(w.text for w in words), all_phonemes, words)


@dataclass(slots=True)
class PhonemizeResult:
    """Result data class for phonemization operations."""
    ref: str
    text: str                     
    _nested: List[List[str]]       
    _words: List[Word]

    # ---  convenience views  ---------------------------------
    def phonemes_nested(self) -> List[List[str]]:
        return self._nested

    def phonemes_flat(self) -> List[str]:
        return [p for word in self._nested for p in word]

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

    def show_table(self, phoneme_sep: str = "") -> "pd.DataFrame":
        """
        Create a pandas DataFrame where each row represents a word.
        Columns: location, word_text, phoneme_str
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for show_table(). Install with: pip install pandas")
        
        # Build DataFrame rows from words
        rows = []
        for word in self._words:
            # Strip rule tags from word text
            clean_word_text = re.sub(r"</?rule[^>]*?>", "", word.text)
            phoneme_str = phoneme_sep.join(str(p) for p in word.get_phonemes())
            rows.append({
                'location': word.location.location_key,
                'word': clean_word_text,
                'phonemes': phoneme_str
            })
        
        # Sort by location (surah:verse:word)
        rows.sort(key=lambda x: tuple(map(int, x['location'].split(':'))))
        
        return pd.DataFrame(rows)

    def save(self, path: str | Path, *, fmt) -> Path:
        """Persist the result (text + phonemes) to *path*."""
        path = Path(path)
        data = {
            "ref": self.ref,
            "text": self.text,
            "phonemes": self._nested,
        }
        if fmt == "json":
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                            encoding="utf-8")
        elif fmt == "csv":
            import csv
            with path.open("w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(["word_idx", "phoneme_seq"])
                for i, seq in enumerate(self._nested, 1):
                    w.writerow([i, " ".join(seq)])
        else:
            raise ValueError(f"Unknown format: {fmt}")
        return path