from __future__ import annotations

from typing import List
from pathlib import Path

from .parser import Parser, load_symbol_mappings
from .word_processor import WordProcessor
from .phonemize_result import PhonemizeResult

# Data directory
DATA_DIR = Path(__file__).resolve().parent.parent / "resources"


class Phonemizer:
    def __init__(
        self,
        db_path: str | Path = DATA_DIR / "Quran.json",
        map_path: str | Path = DATA_DIR / "base_phonemes.yaml",
    ) -> None:
        self.db_path = str(db_path)
        self.map_path = str(map_path)
        # Initialize parser with symbol mappings
        symbol_mappings = load_symbol_mappings(map_path)
        self.parser = Parser(symbol_mappings)
        self.word_processor = WordProcessor()

    def phonemize(
        self,
        ref: str,
        *,
        stops: List[str] = [],
    ) -> PhonemizeResult:
        """
        Phonemize a reference range.
        
        Parameters
        ----------
        ref : str
            Qurʾānic reference.
        stops : List[str], default []
            List of stop types to mark as boundaries.
            
        Returns
        -------
        PhonemizeResult
            Object containing reference, text and phonemes.
        """
        # Load words using the consolidated parser
        words = self.parser.load_words(ref, self.db_path, stop_types=stops)

        # Process each word
        all_phonemes = []
        full_text = " ".join(word.text for word in words)
        
        for word in words:
            phonemes = self.word_processor.process_word(word)
            all_phonemes.append(phonemes)
        
        return PhonemizeResult(ref, full_text, all_phonemes)
