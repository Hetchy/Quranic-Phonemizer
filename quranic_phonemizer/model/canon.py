"""The Score: canonical positions, and the closed rule vocabulary.

Boundary-free and script-free: varies only with the riwayah and the
variant selection.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .address import Location, Riwayah, SlotId, SpellingRunId, VariantSelection
from . import rule as _rule

Rule = _rule.Rule
HAMZA_WASL_START = _rule.HAMZA_WASL_START
IDGHAM_RULES = _rule.IDGHAM_RULES
ILTIQA_RULES = _rule.ILTIQA_RULES
CLASSIFICATION_ONLY = _rule.CLASSIFICATION_ONLY


class CanonLetter(StrEnum):
    """The 28 letters, plus HAMZA and TAA_MARBUTA.

    No ALEF_WASLA (that is an `Onset`); no ALIF_MAQSURA (that is a glyph).
    Letter identity is phonological, not glyphic.
    """

    ALIF = "alif"
    BA = "ba"
    TA = "ta"
    THA = "tha"
    JEEM = "jeem"
    HA = "ha"
    KHA = "kha"
    DAL = "dal"
    THAL = "thal"
    RA = "ra"
    ZAY = "zay"
    SEEN = "seen"
    SHEEN = "sheen"
    SAD = "sad"
    DAD = "dad"
    TAH = "tah"
    ZAH = "zah"
    AIN = "ain"
    GHAIN = "ghain"
    FA = "fa"
    QAF = "qaf"
    KAF = "kaf"
    LAM = "lam"
    MEEM = "meem"
    NOON = "noon"
    HEH = "heh"
    WAW = "waw"
    YA = "ya"
    HAMZA = "hamza"
    TAA_MARBUTA = "taa_marbuta"


#: The canonical spelling of each letter, not any script's rendering of it.
#: Used so a `skeleton` stays human-checkable instead of a bare ordinal.
ABJAD: dict[str, str] = {
    "alif": "ا",
    "ba": "ب",
    "ta": "ت",
    "tha": "ث",
    "jeem": "ج",
    "ha": "ح",
    "kha": "خ",
    "dal": "د",
    "thal": "ذ",
    "ra": "ر",
    "zay": "ز",
    "seen": "س",
    "sheen": "ش",
    "sad": "ص",
    "dad": "ض",
    "tah": "ط",
    "zah": "ظ",
    "ain": "ع",
    "ghain": "غ",
    "fa": "ف",
    "qaf": "ق",
    "kaf": "ك",
    "lam": "ل",
    "meem": "م",
    "noon": "ن",
    "heh": "ه",
    "waw": "و",
    "ya": "ي",
    "hamza": "ء",
    "taa_marbuta": "ة",
}


class Onset(StrEnum):
    """The closed set of mutually exclusive onset states.

    Boundary-conditional onset *presence* lives here; boundary-conditional
    *length* lives on `Nucleus`. `WASL` and `GLIDE` are exact mirrors.
    """

    PLAIN = "plain"
    GEMINATE = "geminate"
    WASL = "wasl"
    GLIDE = "glide"
    TASHIL = "tashil"


class Quality(StrEnum):
    """The vowel letters. One character each, so a vocalised skeleton reads.

    TAQLIL and KUBRA are the two inclination grades: distinct typed
    qualities, not renderings of one inclined vowel."""

    A = "a"
    U = "u"
    I = "i"
    TAQLIL = "ɛ"
    KUBRA = "e"


#: The letter each quality lengthens into. A property of the canonical model,
#: not of any script: every script writes these three and no other.
CARRIER_OF: dict[Quality, CanonLetter] = {
    Quality.A: CanonLetter.ALIF,
    Quality.U: CanonLetter.WAW,
    Quality.I: CanonLetter.YA,
}

CARRIERS = frozenset(CARRIER_OF.values())


class Annotation(StrEnum):
    """A canonical fact that changes no sound.

    Ishmam is lips rounding to show a vowel that is not pronounced, so it has
    no phoneme and cannot be a Quality. It is here so a projection can name it.
    """

    ISHMAM = "ishmam"
    DIVINE_NAME = "divine_name"
    IMALA = "imala"
    JOINED_PARTICLE = "joined_particle"
    """This slot ends a particle the rasm joined to the word after it, so
    what follows opens a word: `هَـٰٓؤُلَآءِ` is `ها` + `أولاء`."""
    NAQL = "naql"
    """This slot's vowel was carried from a qata hamza deleted after it, and
    the deletion holds in every boundary state: the article family and the
    lexical `ردءا`."""
    NAQL_WITNESS = "naql_witness"
    """This sakin host carries a written moved haraka only during naql."""
    IBDAL = "ibdal"
    """This slot is the selected script's replacement for a lexical hamza."""
    BADAL = "badal"
    """This long retains an after-hamza origin after an independent change."""
    MIM_AL_JAM = "mim_al_jam"  # the plural-pronoun mim's joined-only nucleus
    YAA_ZAWAID = "yaa_zawaid"  # a retained extra yaa nucleus or glide


class VowelForm(StrEnum):
    """A vowel's shape in one boundary reading, apart from its quality."""

    ABSENT = "absent"
    SHORT = "short"
    LONG = "long"


@dataclass(frozen=True, slots=True)
class VowelState:
    """One boundary reading of a vowel: its form, and its quality if voiced."""

    form: VowelForm
    quality: Quality | None = None


_ABSENT_STATE = VowelState(VowelForm.ABSENT)


@dataclass(frozen=True, slots=True)
class Nucleus:
    """A vowel's two readings: joined to what follows, and stopped on.

    An ordinary vowel reads the same both ways; the pronoun haa's vowel and
    the seven alifs are the two ways the readings can differ.
    """

    joined: VowelState
    stopped: VowelState

    @property
    def quality(self) -> Quality | None:
        return self.joined.quality

    @property
    def is_silent(self) -> bool:
        return self.joined.form is VowelForm.ABSENT

    @property
    def is_short(self) -> bool:
        return (
            self.joined.form is VowelForm.SHORT and self.stopped.form is VowelForm.SHORT
        )

    @property
    def is_long(self) -> bool:
        return (
            self.joined.form is VowelForm.LONG and self.stopped.form is VowelForm.LONG
        )

    @property
    def is_joined_only_long(self) -> bool:
        """Long when joined to, absent at a stop: pronoun silah, and the
        Warsh joined-only families that reuse the same shape."""
        return (
            self.joined.form is VowelForm.LONG and self.stopped.form is VowelForm.ABSENT
        )

    @property
    def is_pausal_long(self) -> bool:
        return (
            self.joined.form is VowelForm.SHORT and self.stopped.form is VowelForm.LONG
        )

    @property
    def sounds_long(self) -> bool:
        """Long in either reading: an ordinary long vowel, a silah, or one
        of the seven alifs."""
        return self.joined.form is VowelForm.LONG or self.stopped.form is VowelForm.LONG

    def with_quality(self, quality: Quality) -> Nucleus:
        """The same joined/stopped shape, holding a different quality --
        a khilaf site disputes the vowel, never the shape it takes."""
        return Nucleus(
            VowelState(self.joined.form, quality)
            if self.joined.form is not VowelForm.ABSENT
            else _ABSENT_STATE,
            VowelState(self.stopped.form, quality)
            if self.stopped.form is not VowelForm.ABSENT
            else _ABSENT_STATE,
        )

    @classmethod
    def silent(cls) -> Nucleus:
        return cls(_ABSENT_STATE, _ABSENT_STATE)

    @classmethod
    def short(cls, quality: Quality) -> Nucleus:
        state = VowelState(VowelForm.SHORT, quality)
        return cls(state, state)

    @classmethod
    def long(cls, quality: Quality) -> Nucleus:
        state = VowelState(VowelForm.LONG, quality)
        return cls(state, state)

    @classmethod
    def joined_only_long(cls, quality: Quality) -> Nucleus:
        return cls(VowelState(VowelForm.LONG, quality), _ABSENT_STATE)

    @classmethod
    def pausal_long(cls, quality: Quality) -> Nucleus:
        return cls(
            VowelState(VowelForm.SHORT, quality),
            VowelState(VowelForm.LONG, quality),
        )


class SlotOrigin(StrEnum):
    """Which part of `canon.build` produced the slot.

    `SPELLED` marks a muqattaat letter; `NUNATION` distinguishes a tanween
    nun from a root nun, which the Score cannot otherwise tell apart.
    """

    WRITTEN = "written"
    SPELLED = "spelled"
    NUNATION = "nunation"


@dataclass(frozen=True, slots=True)
class Slot:
    """A canonical position: something that can sound in at least one
    boundary state or reading."""

    id: SlotId
    letter: CanonLetter
    onset: Onset
    nucleus: Nucleus
    origin: SlotOrigin = SlotOrigin.WRITTEN
    annotations: frozenset[Annotation] = frozenset()

    @property
    def spelled(self) -> bool:
        return self.origin is SlotOrigin.SPELLED


@dataclass(frozen=True, slots=True)
class SpellingRun:
    """The canonical slots that spell one compact muqattaat letter."""

    id: SpellingRunId
    source_letter: CanonLetter
    slot_ids: tuple[SlotId, ...]


@dataclass(frozen=True, slots=True)
class ScoreWord:
    location: Location
    slots: tuple[Slot, ...]
    sakt_after: bool = False
    spelling_runs: tuple[SpellingRun, ...] = ()


@dataclass(frozen=True, slots=True)
class Score:
    riwayah: Riwayah
    words: tuple[ScoreWord, ...]
    selection: VariantSelection
    digest: str

    def slots(self) -> tuple[Slot, ...]:
        return tuple(slot for word in self.words for slot in word.slots)
