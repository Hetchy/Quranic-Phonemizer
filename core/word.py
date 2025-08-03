"""
Word class for the Quranic phonemizer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .symbols import Symbol, LetterSymbol, StopSymbol
    from .location import Location


@dataclass
class Word:
    """Represents a single word with all its components and metadata."""
    location: Location
    symbols: List[Symbol] = field(default_factory=list)
    text: str = ""
    stop_sign: Optional[StopSymbol] = None

    def first_letter(self) -> Optional[LetterSymbol]:
        """Get the first letter symbol in the word."""
        for symbol in self.symbols:
            if isinstance(symbol, LetterSymbol):
                return symbol
        return None

    def last_letter(self) -> Optional[LetterSymbol]:
        """Get the last letter symbol in the word."""
        for symbol in reversed(self.symbols):
            if isinstance(symbol, LetterSymbol):
                return symbol
        return None

    def debug_print(self) -> str:
        """Pretty print the word structure for debugging purposes."""
        result = f"Word at {self.location.location_key}:\n"
        result += f"  Text: {self.text}\n"
        if self.stop_sign:
            result += f"  Stop Sign: {self.stop_sign.char} (type: {self.stop_sign.type})\n"
        else:
            result += "  Stop Sign: None\n"
        
        result += "  Symbols:\n"
        for i, symbol in enumerate(self.symbols):
            symbol_type = symbol.__class__.__name__
            result += f"    {i}: {symbol_type} '{symbol.char}'"
            if symbol.phoneme:
                result += f" -> {symbol.phoneme}"
            if hasattr(symbol, 'type') and symbol.type:
                result += f" (type: {symbol.type})"
            
            # For LetterSymbols, show associated diacritics, extensions, and shaddah
            if symbol.__class__.__name__ == 'LetterSymbol':
                # Show diacritics
                if symbol.diacritics:
                    for diacritic in symbol.diacritics:
                        result += f"\n      Diacritic: '{diacritic.char}'"
                        if diacritic.phoneme:
                            result += f" -> {diacritic.phoneme}"
                        if hasattr(diacritic, 'type') and diacritic.type:
                            result += f" (type: {diacritic.type})"
                
                # Show extension
                if symbol.extension:
                    result += f"\n      Extension: '{symbol.extension.char}'"
                    if symbol.extension.phoneme:
                        result += f" -> {symbol.extension.phoneme}"
                    if hasattr(symbol.extension, 'type') and symbol.extension.type:
                        result += f" (type: {symbol.extension.type})"
                
                # Show shaddah
                if symbol.has_shaddah:
                    result += "\n      Shaddah: ّ (gemination)"
            result += "\n"
        
        return result
