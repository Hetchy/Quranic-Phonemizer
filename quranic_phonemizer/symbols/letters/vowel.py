from typing import List
from .letter import LetterSymbol
from ...tajweed_rule import TajweedRule


class VowelLetter(LetterSymbol):
    def _lengthen_compatible_phoneme(self, compatible_phonemes: List[str]) -> List[str]:
        prev_phoneme = self.prev_phoneme()
        if prev_phoneme in compatible_phonemes:
            # Remove short vowel from previous letter and return long vowel here
            result = self.find_prev_phoneme_letter()
            if result:
                letter, idx = result
                short_vowel = letter.phonemes.pop(idx)
                return [short_vowel + ":"]
        self.set_tajweed_rule(TajweedRule.VOWEL_SILENT)
        return []


class Alef(VowelLetter):
    def phonemize_letter(self) -> List[str]:
        if self.has_symbol("SILENT_ALWAYS"):
            self.set_tajweed_rule(TajweedRule.VOWEL_SILENT)
            return []
        if not self.parent_word.is_stopping and self.has_symbol("SILENT_AT_CONTINUATION"):
            self.set_tajweed_rule(TajweedRule.VOWEL_SILENT)
            return []
        return self._lengthen_compatible_phoneme(["a", "aˤ"])


class AlefMaksura(VowelLetter):
    COMPATIBLE_PHONEMES = ["a", "aˤ", "i"]

    def phonemize_letter(self) -> List[str]:
        if self.has_symbol("SILENT_ALWAYS"):
            self.set_tajweed_rule(TajweedRule.VOWEL_SILENT)
            return []

        if self.diacritic or self.has_shaddah:
            return super().phonemize_letter()

        # mid-word alef maksura
        if not self.is_last:
            self.set_tajweed_rule(TajweedRule.VOWEL_SILENT)

        # When stopping, ى is consonant yaa if prev vowel can't be lengthened
        # e.g. ٱلْبَغْىِ , ٱلْهَدْىِ but NOT when ى is tanween companion (e.g. مُصَلًّى, أَذًى)
        if self.is_last and self.parent_word.is_stopping:
            prev = self.prev_letter()
            if prev and not prev.has_tanween:
                if self.prev_phoneme() not in self.COMPATIBLE_PHONEMES:
                    return [self.base_phoneme]

        return self._lengthen_compatible_phoneme(self.COMPATIBLE_PHONEMES)


class Waw(VowelLetter):
    def phonemize_letter(self) -> List[str]:
        if self.has_symbol("SILENT_ALWAYS"):
            self.set_tajweed_rule(TajweedRule.VOWEL_SILENT)
            return []

        # Idgham mutamathilayn أَو وَّزَنُوهُمْ
        next_letter = self.next_letter()
        if self.next_letter() and self.next_letter().char == "و" and self.next_letter().has_shaddah:
            self.set_tajweed_rule(TajweedRule.IDGHAM_MUTAMATHILAYN, target=self.next_letter())
            return []

        # Idgham mutamathilayn e.g. ءَاتَوا۟ وَّقُلُوبُهُمْ
        if self.next_letter() and (self.next_letter().char == "ا"):
            # stop on ءَاتَوا۟
            if (self.parent_word.is_stopping and self.prev_letter().has_fatha
                and not self.diacritic and not self.extensions):
                return ["w"]

            # continue
            if (self.next_letter(2) and self.next_letter(2).char == "و" and self.next_letter(2).has_shaddah):
                self.set_tajweed_rule(TajweedRule.IDGHAM_MUTAMATHILAYN, target=self.next_letter(2))
                return []

        # Stopping gives waw sukun, but if prev letter has damma
        # waw acts as vowel letter (e.g. هُوَ → hu:)
        if self.diacritic and not (
            self.has_sukun and self.is_last and self.parent_word.is_stopping
            and not self.has_shaddah
            and self.prev_letter() and self.prev_letter().has_damma
        ):
            return super().phonemize_letter()

        # "a" for cases like الصَّلَوٰة , ٱلۡحَيَوٰةِ
        if self.prev_phoneme() == "a":
            self.set_tajweed_rule(TajweedRule.VOWEL_SILENT)
        
        return self._lengthen_compatible_phoneme(["a", "u"])


class Yaa(VowelLetter):
    def phonemize_letter(self) -> List[str]:
        if self.has_symbol("SILENT_ALWAYS"):
            self.set_tajweed_rule(TajweedRule.VOWEL_SILENT)
            return []

        # Stopping gives yaa sukun, but if prev letter has kasra
        # yaa acts as vowel letter (e.g. ـِيَ → i:)
        if self.diacritic and not (
            self.has_sukun and self.is_last and self.parent_word.is_stopping
            and not self.has_shaddah
            and self.prev_letter() and self.prev_letter().has_kasra
        ):
            return super().phonemize_letter()

        if self.next_letter() and self.next_letter().char == "ي": # بِأَييِّكُمُ
            self.set_tajweed_rule(TajweedRule.IDGHAM_MUTAMATHILAYN, target=self.next_letter())
            return []

        return self._lengthen_compatible_phoneme(["i"])
