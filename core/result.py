"""
core/result.py
==============
Result data class for phonemization operations.

Contains PhonemizeResult which provides various views and formats for phonemized output.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .tokenizer import Token


@dataclass(slots=True)
class PhonemizeResult:
    ref: str
    text: str                     
    _nested: List[List[str]]       
    _tokens: List[Token]

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

        for tok in self._tokens:
            _, cur_verse, cur_word = tok.location.split(":")

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
            for ph in tok.phonemes:
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
        
        # Group tokens by word location
        word_data = {}
        for tok in self._tokens:
            word_loc = tok.location  # surah:verse:word format
            if word_loc not in word_data:
                word_data[word_loc] = {
                    'location': word_loc,
                    'word': '',
                    'phonemes': []
                }
            word_data[word_loc]['word'] += tok.text
            word_data[word_loc]['phonemes'].extend(str(p) for p in tok.phonemes)
        
        # Build DataFrame rows
        rows = []
        for word_info in word_data.values():
            # Strip rule tags from word text (same pattern as tokenizer.py)
            clean_word_text = re.sub(r"</?rule[^>]*?>", "", word_info['word'])
            phoneme_str = phoneme_sep.join(word_info['phonemes'])
            rows.append({
                'location': word_info['location'],
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