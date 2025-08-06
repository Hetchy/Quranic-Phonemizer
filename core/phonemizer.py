from __future__ import annotations

from typing import List
from pathlib import Path

from .parser import Parser, load_symbol_mappings
from .phonemize_result import PhonemizeResult

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
        words = self.parser.load_words(ref, self.db_path, stop_types=stops)
        for word in words:
            word.phonemize()

        all_phonemes = []
        for word in words:
            all_phonemes.append(word.get_phonemes())
            if debug:
                print(word.debug_print())
        
        return PhonemizeResult(ref, " ".join(w.text for w in words), all_phonemes)
