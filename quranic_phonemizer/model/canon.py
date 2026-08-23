"""The Score: canonical positions, and the closed rule vocabulary.

Boundary-free and script-free: varies only with the riwayah and the
variant selection.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .address import Location, Riwayah, SlotId, VariantSelection


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
    "alif": "ا", "ba": "ب", "ta": "ت", "tha": "ث", "jeem": "ج", "ha": "ح",
    "kha": "خ", "dal": "د", "thal": "ذ", "ra": "ر", "zay": "ز", "seen": "س",
    "sheen": "ش", "sad": "ص", "dad": "ض", "tah": "ط", "zah": "ظ", "ain": "ع",
    "ghain": "غ", "fa": "ف", "qaf": "ق", "kaf": "ك", "lam": "ل", "meem": "م",
    "noon": "ن", "heh": "ه", "waw": "و", "ya": "ي", "hamza": "ء",
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
    """The vowel letters. One character each, so a vocalised skeleton reads."""

    A = "a"
    U = "u"
    I = "i"
    E = "e"


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
            self.joined.form is VowelForm.SHORT
            and self.stopped.form is VowelForm.SHORT
        )

    @property
    def is_long(self) -> bool:
        return (
            self.joined.form is VowelForm.LONG
            and self.stopped.form is VowelForm.LONG
        )

    @property
    def is_silah(self) -> bool:
        return (
            self.joined.form is VowelForm.LONG
            and self.stopped.form is VowelForm.ABSENT
        )

    @property
    def is_pausal_long(self) -> bool:
        return (
            self.joined.form is VowelForm.SHORT
            and self.stopped.form is VowelForm.LONG
        )

    @property
    def sounds_long(self) -> bool:
        """Long in either reading: an ordinary long vowel, a silah, or one
        of the seven alifs."""
        return (
            self.joined.form is VowelForm.LONG
            or self.stopped.form is VowelForm.LONG
        )

    def with_quality(self, quality: Quality) -> Nucleus:
        """The same joined/stopped shape, holding a different quality --
        a khilaf site disputes the vowel, never the shape it takes."""
        return Nucleus(
            VowelState(self.joined.form, quality)
            if self.joined.form is not VowelForm.ABSENT else _ABSENT_STATE,
            VowelState(self.stopped.form, quality)
            if self.stopped.form is not VowelForm.ABSENT else _ABSENT_STATE,
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
    def silah(cls, quality: Quality) -> Nucleus:
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
class ScoreWord:
    location: Location
    slots: tuple[Slot, ...]
    sakt_after: bool = False


@dataclass(frozen=True, slots=True)
class Score:
    riwayah: Riwayah
    words: tuple[ScoreWord, ...]
    selection: VariantSelection
    digest: str

    def slots(self) -> tuple[Slot, ...]:
        return tuple(slot for word in self.words for slot in word.slots)


class Rule(StrEnum):
    """The only rule vocabulary. One name, one place."""

    IZHAR = "izhar"
    IKHFAA = "ikhfaa"
    IQLAB = "iqlab"
    IDGHAM_BI_GHUNNAH = "idgham_bi_ghunnah"
    IDGHAM_BILA_GHUNNAH = "idgham_bila_ghunnah"
    GHUNNAH_MUSHADDADAH = "ghunnah_mushaddadah"

    IZHAR_SHAFAWI = "izhar_shafawi"
    IKHFAA_SHAFAWI = "ikhfaa_shafawi"
    IDGHAM_SHAFAWI = "idgham_shafawi"

    IDGHAM_MUTAMATHILAYN = "idgham_mutamathilayn"
    IDGHAM_MUTAQARIBAYN = "idgham_mutaqaribayn"
    IDGHAM_MUTAJANISAYN_KAMIL = "idgham_mutajanisayn_kamil"
    IDGHAM_MUTAJANISAYN_NAQIS = "idgham_mutajanisayn_naqis"

    LAM_SHAMSIYYAH = "lam_shamsiyyah"
    LAM_QAMARIYYAH = "lam_qamariyyah"

    QALQALA_SUGHRA = "qalqala_sughra"
    QALQALA_KUBRA = "qalqala_kubra"
    QALQALA_AKBAR = "qalqala_akbar"

    TAFKHEEM = "tafkheem"
    TARQEEQ = "tarqeeq"
    IMALA = "imala"
    TASHIL = "tashil"
    ISHMAM = "ishmam"

    MADD_TABII = "madd_tabii"
    MADD_MUTTASIL = "madd_muttasil"
    MADD_MUNFASIL = "madd_munfasil"
    MADD_LAZIM = "madd_lazim"
    MADD_ARID_LISSUKUN = "madd_arid_lissukun"
    MADD_LEEN = "madd_leen"
    MADD_IWAD = "madd_iwad"
    MADD_BADAL = "madd_badal"
    MADD_SILAH = "madd_silah"

    IBDAL_HAMZA = "ibdal_hamza"
    HAMZA_WASL_SILENT = "hamza_wasl_silent"
    HAMZA_WASL_FATHA = "hamza_wasl_fatha"
    HAMZA_WASL_KASRA = "hamza_wasl_kasra"
    HAMZA_WASL_DAMMA = "hamza_wasl_damma"
    ILTIQA_HARAKA = "iltiqa_haraka"
    ILTIQA_SHORTENING = "iltiqa_shortening"
    WAQF_DIACRITIC_DROP = "waqf_diacritic_drop"
    WAQF_SILAH_DROP = "waqf_silah_drop"
    WAQF_TAA_MARBUTA = "waqf_taa_marbuta"
    PAUSAL_ALIF = "pausal_alif"


#: A prosthetic hamza started on, one rule per helping vowel.
HAMZA_WASL_START: frozenset[Rule] = frozenset(
    {Rule.HAMZA_WASL_FATHA, Rule.HAMZA_WASL_KASRA, Rule.HAMZA_WASL_DAMMA}
)

#: The idgham family: a quiescent letter folds into the letter after it.
IDGHAM_RULES: frozenset[Rule] = frozenset(
    {
        Rule.IDGHAM_BI_GHUNNAH,
        Rule.IDGHAM_BILA_GHUNNAH,
        Rule.IDGHAM_SHAFAWI,
        Rule.IDGHAM_MUTAMATHILAYN,
        Rule.IDGHAM_MUTAQARIBAYN,
        Rule.IDGHAM_MUTAJANISAYN_KAMIL,
        Rule.IDGHAM_MUTAJANISAYN_NAQIS,
    }
)

#: The two repairs where quiescent letters may not meet.
ILTIQA_RULES: frozenset[Rule] = frozenset(
    {Rule.ILTIQA_HARAKA, Rule.ILTIQA_SHORTENING}
)

#: Rules whose occurrence may produce no effect; `engine/run.py` mints each
#: one a `Classifies` edge in place of an attribution, and only where it
#: produced nothing. `ghunnah_mushaddadah` is here for the article's noon
#: alone: `ٱلنَّاسِ` is doubled by a merger `lam_shamsiyyah` owns, and
#: a merger's two edges belong to one occurrence.
CLASSIFICATION_ONLY: frozenset[Rule] = frozenset(
    {
        Rule.TARQEEQ,
        Rule.GHUNNAH_MUSHADDADAH,
        Rule.IDGHAM_MUTAJANISAYN_NAQIS,
        Rule.IZHAR,
        Rule.IZHAR_SHAFAWI,
        Rule.LAM_QAMARIYYAH,
        Rule.MADD_BADAL,
        Rule.MADD_SILAH,
        Rule.MADD_MUTTASIL,
        Rule.MADD_MUNFASIL,
        Rule.MADD_LAZIM,
        Rule.MADD_ARID_LISSUKUN,
        Rule.MADD_LEEN,
        Rule.IBDAL_HAMZA,
        Rule.IMALA,
        Rule.TASHIL,
        Rule.ISHMAM,
    }
) | HAMZA_WASL_START
