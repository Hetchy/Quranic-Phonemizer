"""
LetterSymbol class for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import List, Optional, final, TYPE_CHECKING

from ..symbol import Symbol
from ..diacritic import DiacriticSymbol
from ..extension import ExtensionSymbol
from ..other import OtherSymbol

from ...phoneme_registry import get_rule_phoneme
from ...tajweed_rule import TajweedRule, TajweedRuleTag


if TYPE_CHECKING:
    from ...word import Word


class LetterSymbol(Symbol):
    """Represents a consonant or vowel letter with associated diacritics, extensions, and other symbols."""

    def __init__(self, name: str, char: str, base_phoneme: str):
        super().__init__(name, char, base_phoneme)

        self.parent_word: Word
        self.index_in_word: int
        self.has_shaddah: bool = False
        self.diacritic: Optional[DiacriticSymbol] = None
        self.extensions: List[ExtensionSymbol] = []
        self.other_symbols: List[OtherSymbol] = []

        self.phonemes: List[str] = []
        self.is_phonemized: bool = False
        self.affected_by: Optional["LetterSymbol"] = None

        self._tajweed_rules: List[TajweedRuleTag] = []

    def prev_letter(self, n: int = 1) -> Optional["LetterSymbol"]:
        return self.parent_word.get_prev_letter(self.index_in_word, n)

    def next_letter(self, n: int = 1) -> Optional["LetterSymbol"]:
        return self.parent_word.get_next_letter(self.index_in_word, n)

    def prev_phoneme(self) -> Optional[str]:
        current_word = self.parent_word
        current_index = self.index_in_word

        while current_index > 0:
            current_index -= 1
            prev_letter = current_word.letters[current_index]
            if prev_letter.phonemes and prev_letter.phonemes:
                return prev_letter.phonemes[-1]

        prev_word = current_word.prev_word
        if prev_word:
            for letter in reversed(prev_word.letters):
                if letter.phonemes and letter.phonemes:
                    return letter.phonemes[-1]

        return None

    def find_prev_phoneme_letter(self) -> Optional[tuple["LetterSymbol", int]]:
        current_word = self.parent_word
        current_index = self.index_in_word

        while current_index > 0:
            current_index -= 1
            prev_letter = current_word.letters[current_index]
            if prev_letter.phonemes and prev_letter.phonemes:
                return (prev_letter, len(prev_letter.phonemes) - 1)

        prev_word = current_word.prev_word
        if prev_word.letters:
            for letter in reversed(prev_word.letters):
                if letter.phonemes and letter.phonemes:
                    return (letter, len(letter.phonemes) - 1)

        return None

    def modify_prev_phoneme(self, new_phoneme: str) -> bool:
        result = self.find_prev_phoneme_letter()
        if result:
            letter, phoneme_idx = result
            letter.phonemes[phoneme_idx] = new_phoneme
            return True
        return False

    def can_phonemize(self) -> bool:
        return not self.is_phonemized

    def mark_phonemized(self, phonemes: Optional[List[str]] = None, affected_by: Optional["LetterSymbol"] = None):
        self.phonemes = phonemes or []
        self.is_phonemized = True
        self.affected_by = affected_by

    def set_tajweed_rule(self, rule: TajweedRule, target: Optional["LetterSymbol"] = None):
        """Tag a TajweedRule on this letter (source) and optionally on a target letter."""
        tag = TajweedRuleTag(rule=rule, is_source=True)
        if tag not in self._tajweed_rules:
            self._tajweed_rules.append(tag)
        if target is not None:
            target_tag = TajweedRuleTag(rule=rule, is_source=False)
            if target_tag not in target._tajweed_rules:
                target._tajweed_rules.append(target_tag)

    @property
    def tajweed_rules(self) -> List[TajweedRuleTag]:
        return list(self._tajweed_rules)

    @final
    def phonemize(self) -> List[str]:
        # Preserve original state for mapping
        original_diacritic = self.diacritic
        original_shaddah = self.has_shaddah

        # Remove shaddah on starting letter
        if self.is_first and self.parent_word.is_starting:
            self.has_shaddah = False

        # Apply stopping transformations
        if self.is_last and self.parent_word.is_stopping:
            if self.char == "ء" and self.has_fathatan:
                self.diacritic = DiacriticSymbol("FATHA", "َ", "a")
                self.extend()
            elif self.char == "ا" or (self.char == "ى" and not self.has_sukun):
                self.diacritic = None
            else:  # Change diacritic to sukun
                self.diacritic = DiacriticSymbol("SUKUN", "۟", None)

        elif self.parent_word.is_stopping and self.diacritic \
            and self.next_letter() and self.next_letter().is_last and self.next_letter().has_symbol("SILENT_ALWAYS"):
            # e.g. stop on ٱلْعُلَمَـٰٓؤُا۟
            self.diacritic = DiacriticSymbol("SUKUN", "۟", None)

        # Phonemize letter and modifiers
        self.phonemes = self.phonemize_letter() + self.phonemize_modifiers()

        # Istilaa consonants get tafkheem (raa excluded by is_heavy; lam deduped)
        if self.is_heavy:
            self.set_tajweed_rule(TajweedRule.TAFKHEEM)

        # Restore original state for mapping
        self.diacritic = original_diacritic
        self.has_shaddah = original_shaddah

        return self.phonemes

    # Dispatch map for idgham silent types → TajweedRule
    IDGHAM_RULE_MAP = {
        "idgham_mutamathilayn": TajweedRule.IDGHAM_MUTAMATHILAYN,
        "idgham_mutaqaribayn": TajweedRule.IDGHAM_MUTAQARIBAYN,
        "lam_shamsiyah": TajweedRule.LAM_SHAMSIYAH,
        "idgham_mutajanisayn_kamil": TajweedRule.IDGHAM_MUTAJANISAYN_KAMIL,
        "idgham_mutajanisayn_naqis": TajweedRule.IDGHAM_MUTAJANISAYN_NAQIS,
    }

    def phonemize_letter(self) -> List[str]:
        if not self.diacritic and not self.has_shaddah:
            rule = self.classify_idgham_silent_type()
            if rule:
                if rule in self.IDGHAM_RULE_MAP:
                    self.set_tajweed_rule(self.IDGHAM_RULE_MAP[rule], target=self.next_letter())
            return [self.base_phoneme] if rule == "idgham_mutajanisayn_naqis" else []

        return self.apply_shaddah()

    def apply_shaddah(self, phoneme: Optional[str] = None) -> List[str]:
        if self.has_shaddah:
            base = phoneme or self.base_phoneme
            return [base + base]
        return [phoneme or self.base_phoneme]

    def phonemize_modifiers(self) -> List[str]:
        if not self.diacritic:
            return []
        if self.has_sukun:
            return []
        if self.has_tanween:
            return self.apply_tanween()

        result = self.diacritic.base_phoneme
        if self.has_fatha and (self.is_heavy or self.char == "ر"):
            result += "ˤ"

        if self.extensions:
            result += ":"

        return [result]

    def apply_tanween(self) -> List[str]:
        short_vowel_ph = self.diacritic.base_phoneme[0]
        noon_ph = self.diacritic.base_phoneme[1]

        if self.has_fathatan and (self.is_heavy or self.char == 'ر'):
            short_vowel_ph += "ˤ"

        next_letter = self.next_letter(1)
        if not next_letter:
            return []

        if next_letter.char in ["ا", "ى"]:
            if self.parent_word.is_stopping:
                return [short_vowel_ph + ":"]
            else:
                next_letter.mark_phonemized(None, affected_by=self.diacritic)
                next_letter = self.next_letter(2)
                if not next_letter:
                    return [short_vowel_ph + ":"]

        # Iqlab
        if next_letter.char == "ب":
            self.set_tajweed_rule(TajweedRule.IQLAB_TANWEEN, target=next_letter)
            return [short_vowel_ph, get_rule_phoneme("iqlab", "phoneme")]

        # Ikhfaa
        if next_letter.is_ikhfaa:
            self.set_tajweed_rule(TajweedRule.IKHFAA_TANWEEN, target=next_letter)
            ikhfaa_key = "heavy_phoneme" if next_letter.is_heavy else "light_phoneme"
            return [short_vowel_ph, get_rule_phoneme("ikhfaa", ikhfaa_key)]

        # Idgham Ghunnah
        if next_letter.is_idgham_ghunnah:
            self.set_tajweed_rule(TajweedRule.IDGHAM_GHUNNAH_TANWEEN, target=next_letter)
            nasal_map = get_rule_phoneme("idgham", "nasalized_map")
            target_phoneme = nasal_map.get(next_letter.base_phoneme)
            # Note: Don't clear has_shaddah - it's part of the canonical text and should be preserved
            next_phonemes = [target_phoneme] + next_letter.phonemize_modifiers()
            next_letter.mark_phonemized(next_phonemes, affected_by=self)
            return [short_vowel_ph]

        # Idgham no Ghunnah
        if next_letter.char in ["ل", "ر"]:
            self.set_tajweed_rule(TajweedRule.IDGHAM_BILA_GHUNNAH_TANWEEN, target=next_letter)
            return [short_vowel_ph]

        # Izhar
        return [short_vowel_ph, noon_ph]

    def classify_idgham_silent_type(self) -> Optional[str]:
        if self.next_letter() and self.next_letter().char == self.char:
            # Within-word ل→ل is lam shamsiyah (definite article), not mutamathilayn
            if self.char == "ل" and self.next_letter().parent_word == self.parent_word:
                return "lam_shamsiyah"
            return "idgham_mutamathilayn"

        mutaqaribayn_map = {
            "ل": ("ر",), # e.g. بَل رَّبُّكُمۡ
            "ق": ("ك",)  # only نَخۡلُقكُّم
        }

        mutajanisayn_kamil_map = {
            "ذ": ("ظ",), # e.g. إِذ ظَّلَمۡتُمۡ
            "د": ("ت",), # e.g. أَرَدتُّمۡ
            "ت": ("د", "ط"), # e.g. أَثۡقَلَت دَّعَوَا, وَدَّت طَّآئِفَةࣱ
            "ث": ("ذ",), # only يَلۡهَث‌ۚ ذّٰلِكَ
            "ب": ("م",)  # only ٱرۡكَب مَّعَنَا
        }

        mutajanisayn_naqis_map = {
            "ط": ("ت",),
        }

        next_char = self.next_letter().char if self.next_letter() else None
        if not next_char:
            return None

        if next_char in mutaqaribayn_map.get(self.char, ()):
            if self.char == "ل" and self.next_letter().parent_word == self.parent_word:
                return "lam_shamsiyah"
            return "idgham_mutaqaribayn"
        if next_char in mutajanisayn_kamil_map.get(self.char, ()):
            return "idgham_mutajanisayn_kamil"
        if next_char in mutajanisayn_naqis_map.get(self.char, ()):
            return "idgham_mutajanisayn_naqis"

        if self.char == "ل":
            return "lam_shamsiyah"

        return "idgham_unknown"


    def has_symbol(self, symbol_name: str) -> bool:
        return any(symbol.name == symbol_name for symbol in self.other_symbols)

    def extend(self):
        if not self.extensions:
            self.extensions.append(ExtensionSymbol("", "", None))

    @property
    def is_first(self) -> bool:
        return self.index_in_word == 0

    @property
    def is_last(self) -> bool:
        return self.index_in_word == len(self.parent_word.letters) - 1

    @property
    def is_heavy(self) -> bool:
        return self.char in ["خ", "ص", "ض", "غ", "ط", "ق", "ظ"]

    @property
    def is_qalqala(self) -> bool:
        return self.char in ["ق", "ط", "ب", "ج", "د"]

    @property
    def is_ikhfaa(self) -> bool:
        return self.char in ["ت", "ث", "ج", "د", "ذ", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ف", "ق", "ك"]

    @property
    def is_idgham_ghunnah(self) -> bool:
        return self.char in ["ي", "ن", "م", "و"]

    @property
    def has_sukun(self) -> bool:
        return self.diacritic and self.diacritic.is_sukun

    @property
    def has_fatha(self) -> bool:
        return self.diacritic and self.diacritic.is_fatha

    @property
    def has_damma(self) -> bool:
        return self.diacritic and self.diacritic.is_damma

    @property
    def has_kasra(self) -> bool:
        return self.diacritic and self.diacritic.is_kasra

    @property
    def has_tanween(self) -> bool:
        return self.diacritic and self.diacritic.is_tanween

    @property
    def has_fathatan(self) -> bool:
        return self.diacritic and self.diacritic.is_fathatan
