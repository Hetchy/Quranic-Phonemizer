from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


SHADDAH = "\N{ARABIC SHADDA}"


class Letter(StrEnum):
    ALIF = "ا"
    HAMZA_WASL = "ٱ"
    HAMZA = "ء"
    BA = "ب"
    TA = "ت"
    THA = "ث"
    JEEM = "ج"
    HHA = "ح"
    KHA = "خ"
    DAL = "د"
    THAL = "ذ"
    RA = "ر"
    ZAIN = "ز"
    SEEN = "س"
    SHEEN = "ش"
    SAD = "ص"
    DAD = "ض"
    TTA = "ط"
    DTHA = "ظ"
    AIN = "ع"
    GHAIN = "غ"
    FA = "ف"
    QAF = "ق"
    KAF = "ك"
    LAM = "ل"
    MEEM = "م"
    NOON = "ن"
    HA = "ه"
    TAA_MARBUTA = "ة"
    WAW = "و"
    YA = "ي"
    ALIF_MAQSURA = "ى"


class VowelQuality(StrEnum):
    A = "a"
    U = "u"
    I_VOWEL = "i"
    IMALA = "imala"


class Harakah(StrEnum):
    FATHA = "َ"
    DAMMA = "ُ"
    KASRA = "ِ"
    SUKUN = "ْ"

    @property
    def quality(self) -> VowelQuality | None:
        return {
            Harakah.FATHA: VowelQuality.A,
            Harakah.DAMMA: VowelQuality.U,
            Harakah.KASRA: VowelQuality.I_VOWEL,
        }.get(self)


class Tanween(StrEnum):
    FATH = "ً"
    DAMM = "ٌ"
    KASR = "ٍ"

    @property
    def quality(self) -> VowelQuality:
        return {
            Tanween.FATH: VowelQuality.A,
            Tanween.DAMM: VowelQuality.U,
            Tanween.KASR: VowelQuality.I_VOWEL,
        }[self]


class SmallVowel(StrEnum):
    DAGGER_ALIF = "ٰ"
    MINI_WAW = "ۥ"
    MINI_YA = "ۦ"


class SourceMark(StrEnum):
    MADD = "madd"
    SILENT_ALWAYS = "silent_always"
    SILENT_IN_WASL = "silent_in_wasl"
    IMALA = "imala"
    SECOND_HAMZA = "second_hamza"


class OrthographicHint(StrEnum):
    SMALL_YA_LETTER = "small_ya_letter"


class StopSign(StrEnum):
    PREFERRED_CONTINUE = "preferred_continue"
    PREFERRED_STOP = "preferred_stop"
    OPTIONAL_STOP = "optional_stop"
    COMPULSORY_STOP = "compulsory_stop"
    PROHIBITED_STOP = "prohibited_stop"
    EITHER_STOP = "either_stop"


class GraphemeRole(StrEnum):
    BASE = "base"
    MARK = "mark"
    STOP = "stop"
    STRUCTURAL = "structural"


@dataclass(frozen=True, slots=True)
class SourceGrapheme:
    char: str
    offset: int
    role: GraphemeRole
    letter_index: int | None


@dataclass(frozen=True, slots=True)
class Location:
    surah: int
    ayah: int
    word: int

    @classmethod
    def parse(cls, value: str) -> Location:
        surah, ayah, word = value.split(":")
        return cls(int(surah), int(ayah), int(word))

    def __str__(self) -> str:
        return f"{self.surah}:{self.ayah}:{self.word}"


@dataclass(frozen=True, slots=True)
class LetterForm:
    letter: Letter
    harakah: Harakah | None = None
    tanween: Tanween | None = None
    shaddah: bool = False
    small_vowels: tuple[SmallVowel, ...] = ()
    marks: frozenset[SourceMark] = frozenset()
    hints: frozenset[OrthographicHint] = frozenset()

    def has_mark(self, mark: SourceMark) -> bool:
        return mark in self.marks

    @property
    def length_marked(self) -> bool:
        return bool(self.small_vowels) or SourceMark.MADD in self.marks


@dataclass(frozen=True, slots=True)
class LetterUnit:
    form: LetterForm


@dataclass(frozen=True, slots=True)
class SourceWord:
    location: Location
    text: str
    letters: tuple[LetterUnit, ...]
    graphemes: tuple[SourceGrapheme, ...]
    stop_sign: StopSign | None = None

    def reconstruct(self) -> str:
        return "".join(grapheme.char for grapheme in self.graphemes)
