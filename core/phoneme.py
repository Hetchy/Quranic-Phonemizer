import yaml
from pathlib import Path
from typing import Dict, List, Optional, Union, Type
from enum import Enum

class Phoneme:
    def __init__(self, name: str = "", cp: int = 0, char: str = "", phoneme: str = "", category: str = ""):
        self.name = name
        self.cp = cp
        self.char = char
        self.phoneme = phoneme
        self.category = category  # e.g. 'letters', 'diacritics'

    def __str__(self) -> str:
        return self.phoneme

    def __repr__(self):
        return (
            f"Phoneme(name={self.name}, cp=0x{self.cp:X}, char='{self.char}', "
            f"phoneme='{self.phoneme}', category='{self.category}')"
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, Phoneme):
            return self.phoneme == other.phoneme
        elif isinstance(other, str):
            return self.phoneme == other
        return False

    def __hash__(self) -> int:
        return hash(self.phoneme)

    def __bool__(self) -> bool:
        return bool(self.phoneme)

    # Helper methods for category checking
    def is_diacritic(self) -> bool:
        """Check if this phoneme represents a diacritic"""
        return self.category.lower() == "diacritics"

    def is_tanween(self) -> bool:
        """Check if this phoneme represents a tanween"""
        return self.name in ["FATHATAN", "KASRATAN", "DAMMATAN"]
    
    def is_letter(self) -> bool:
        """Check if this phoneme represents a letter"""
        return self.category.lower() == "letters"

    def is_conditional(self) -> bool:
        """Check if this phoneme has conditional options like <opt1/opt2>"""
        return (self.phoneme.startswith("<") and "/" in self.phoneme and
                self.phoneme.endswith(">"))

    def get_conditional_options(self) -> List[str]:
        """Extract conditional options from phoneme like <t/h> -> ['t', 'h']"""
        if self.is_conditional():
            return self.phoneme[1:-1].split('/')
        return []

    def assign(self, other: Union[str, 'Phoneme']) -> None:
        """Update this phoneme's content from a string or another Phoneme"""
        if isinstance(other, str):
            self.phoneme = other
        elif isinstance(other, Phoneme):
            self.phoneme = other.phoneme

    @classmethod
    def from_string(cls, phoneme_str: str, category: str = "unknown") -> 'Phoneme':
        """Create a Phoneme from just a phoneme string"""
        return cls(phoneme=phoneme_str, category=category)


# Module-level mappings and enums (initialized on import)
_by_cp: Dict[int, Phoneme] = {}
_by_char: Dict[str, Phoneme] = {}
_by_name: Dict[str, Phoneme] = {}
Letter: Type[Enum] = None
Diacritic: Type[Enum] = None


def load_phoneme_data(yaml_path: Union[str, Path] = None) -> None:
    """
    Load phoneme data from YAML file and initialize module-level mappings and enums.
    
    Args:
        yaml_path: Path to phoneme mapping YAML file. If None, uses default path.
    """
    global _by_cp, _by_char, _by_name, Letter, Diacritic
    
    if not yaml_path:
        yaml_path = Path(__file__).parent.parent / "resources" / "base_phonemes.yaml"

    _by_cp.clear()
    _by_char.clear()
    _by_name.clear()

    letters_names = []
    diacritics_names = []

    data = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("phoneme map YAML must be a mapping with groups")

    for category, group_dict in data.items():
        if not isinstance(group_dict, dict):
            continue
        for name, entry in group_dict.items():
            if not isinstance(entry, dict):
                continue
            cp = entry.get("cp")
            char = entry.get("char")
            phoneme = entry.get("phoneme", "")

            cp_int = int(cp, 0) if isinstance(cp, str) else int(cp)
            pe = Phoneme(
                name=name, cp=cp_int, char=char, phoneme=phoneme, category=category
            )
            _by_cp[cp_int] = pe
            _by_char[char] = pe
            _by_name[name] = pe
            
            if category.lower() == "letters":
                letters_names.append(name)
            elif category.lower() == "diacritics":
                diacritics_names.append(name)

    # Create enums for letter and diacritic names
    Letter = Enum("Letter", {n: _by_name[n].phoneme for n in letters_names}, type=str)
    Diacritic = Enum("Diacritic", {n: _by_name[n].phoneme for n in diacritics_names}, type=str)


def tanween_to_diacritic(tanween_ph: Phoneme) -> Phoneme:
    """Convert tanween to its corresponding diacritic"""
    if tanween_ph == Diacritic.FATHATAN:
        return _by_name["FATHA"]
    elif tanween_ph == Diacritic.KASRATAN:
        return _by_name["KASRA"]
    elif tanween_ph == Diacritic.DAMMATAN:
        return _by_name["DAMMA"]
    else:
        raise ValueError(f"Invalid tanween: {tanween_ph}")


def map_word(word: str) -> List[Phoneme]:
    """Map a word to a list of Phoneme objects"""
    return [
        Phoneme(entry.name, entry.cp, entry.char, entry.phoneme, entry.category)
        for ch in word
        if (entry := _by_char.get(ch)) and entry.phoneme
    ]


def create_phoneme(phoneme_str: str, category: str) -> Phoneme:
    """Create a Phoneme object from a string (used for rule transformations)"""
    return Phoneme.from_string(phoneme_str, category)

load_phoneme_data()
