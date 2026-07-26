"""The Score: canonical positions, and the closed rule vocabulary.

The Score is boundary-free and script-free. It varies with the riwayah and the
variant selection, and with nothing else (ADR-001 §1).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

from .address import Location, Riwayah, SlotId, VariantSelection


class CanonLetter(StrEnum):
    """The 28 letters, plus HAMZA, plus TAA_MARBUTA. Thirty members.

    No ALEF_WASLA — that is an `Onset`. No ALIF_MAQSURA — that is a glyph.
    Letter identity is phonological, not glyphic (ADR-001 §3.1).
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


#: The canonical spelling of each letter — the abstract letter itself, not any
#: script's rendering of it. It exists so a `skeleton` stays human-checkable:
#: a verse-scoped ordinal is robust and unreadable, and every Ledger and
#: lexicon entry is reviewed by eye (ADR-001 §5.1).
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
    *length* lives on `Nucleus`. `WASL` and `SILAH` are exact mirrors.
    """

    PLAIN = "plain"
    GEMINATE = "geminate"
    WASL = "wasl"
    SILAH = "silah"
    TASHIL = "tashil"


class Quality(StrEnum):
    A = "a"
    U = "u"
    I = "i"
    IMALA = "imala"
    ISHMAM = "ishmam"


class NucleusKind(StrEnum):
    """The union's discriminant, exposed so `Trigger` can index on it."""

    SILENT = "silent"
    SHORT = "short"
    LONG = "long"
    SILAH = "silah"
    PAUSAL_LONG = "pausal_long"


@dataclass(frozen=True, slots=True)
class Silent:
    """No vowel at this position. Uthmani's absent harakah and IndoPak's
    `ْ` are two spellings of this one value."""

    kind: NucleusKind = NucleusKind.SILENT


@dataclass(frozen=True, slots=True)
class Short:
    quality: Quality
    kind: NucleusKind = NucleusKind.SHORT


@dataclass(frozen=True, slots=True)
class Long:
    quality: Quality
    kind: NucleusKind = NucleusKind.LONG


@dataclass(frozen=True, slots=True)
class Silah:
    """Long in waṣl, absent at pause."""

    quality: Quality
    kind: NucleusKind = NucleusKind.SILAH


@dataclass(frozen=True, slots=True)
class PausalLong:
    """Short in waṣl, long at pause. The seven alifs."""

    quality: Quality
    kind: NucleusKind = NucleusKind.PAUSAL_LONG


Nucleus: TypeAlias = Silent | Short | Long | Silah | PausalLong

SILENT = Silent()


@dataclass(frozen=True, slots=True)
class Slot:
    """A canonical position: something that can sound at its own position in at
    least one boundary state or reading (ADR-001 §3.1)."""

    id: SlotId
    letter: CanonLetter
    onset: Onset
    nucleus: Nucleus
    spelled: bool = False


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


class RuleFamily(StrEnum):
    """What a script adapter can genuinely see. Attestation names one of
    these, never a `Rule` — choosing between ≥7 idghām members needs the
    previous word, the pair tables and the ghunnah split (ADR-003 §4.1)."""

    ASSIMILATION = "assimilation"
    NASALIZATION = "nasalization"
    INSERTION = "insertion"
    LENGTHENING = "lengthening"
    EMPHASIS = "emphasis"
    RELEASE = "release"


class Phase(StrEnum):
    """Closed and ordered. Within a phase rules are unordered and conflicts
    are errors (ADR-004 §3)."""

    BOUNDARY = "boundary"
    MERGE = "merge"
    LENGTH = "length"
    COLOUR = "colour"
    RELEASE = "release"


class Rule(StrEnum):
    """The only rule vocabulary. One name, one place."""

    IZHAR_HALQI = "izhar_halqi"
    IZHAR_MUTLAQ = "izhar_mutlaq"
    IKHFAA_HAQIQI = "ikhfaa_haqiqi"
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
    MADD_WAJIB_MUTTASIL = "madd_wajib_muttasil"
    MADD_JAIZ_MUNFASIL = "madd_jaiz_munfasil"
    MADD_LAZIM = "madd_lazim"
    MADD_ARID_LIL_SUKUN = "madd_arid_lil_sukun"
    MADD_LEEN = "madd_leen"
    IWAD = "iwad"

    WASL_ELISION = "wasl_elision"
    WASL_START = "wasl_start"
    ILTIQA_REPAIR = "iltiqa_repair"
    WAQF_ENDING = "waqf_ending"
    SILAH = "silah"
    SAKT = "sakt"

    PLAIN = "plain"


#: Every `Rule` declares its family (ADR-002 §5.1). A family gives projections
#: a coarse grouping for free and is what a script may attest.
FAMILY_OF: dict[Rule, RuleFamily] = {
    Rule.IZHAR_HALQI: RuleFamily.NASALIZATION,
    Rule.IZHAR_MUTLAQ: RuleFamily.NASALIZATION,
    Rule.IKHFAA_HAQIQI: RuleFamily.NASALIZATION,
    Rule.IQLAB: RuleFamily.NASALIZATION,
    Rule.IDGHAM_BI_GHUNNAH: RuleFamily.ASSIMILATION,
    Rule.IDGHAM_BILA_GHUNNAH: RuleFamily.ASSIMILATION,
    Rule.GHUNNAH_MUSHADDADAH: RuleFamily.NASALIZATION,
    Rule.IZHAR_SHAFAWI: RuleFamily.NASALIZATION,
    Rule.IKHFAA_SHAFAWI: RuleFamily.NASALIZATION,
    Rule.IDGHAM_SHAFAWI: RuleFamily.ASSIMILATION,
    Rule.IDGHAM_MUTAMATHILAYN: RuleFamily.ASSIMILATION,
    Rule.IDGHAM_MUTAQARIBAYN: RuleFamily.ASSIMILATION,
    Rule.IDGHAM_MUTAJANISAYN_KAMIL: RuleFamily.ASSIMILATION,
    Rule.IDGHAM_MUTAJANISAYN_NAQIS: RuleFamily.ASSIMILATION,
    Rule.LAM_SHAMSIYYAH: RuleFamily.ASSIMILATION,
    Rule.LAM_QAMARIYYAH: RuleFamily.ASSIMILATION,
    Rule.QALQALA_SUGHRA: RuleFamily.RELEASE,
    Rule.QALQALA_KUBRA: RuleFamily.RELEASE,
    Rule.QALQALA_AKBAR: RuleFamily.RELEASE,
    Rule.TAFKHEEM: RuleFamily.EMPHASIS,
    Rule.TARQEEQ: RuleFamily.EMPHASIS,
    Rule.IMALA: RuleFamily.EMPHASIS,
    Rule.TASHIL: RuleFamily.EMPHASIS,
    Rule.ISHMAM: RuleFamily.EMPHASIS,
    Rule.MADD_TABII: RuleFamily.LENGTHENING,
    Rule.MADD_WAJIB_MUTTASIL: RuleFamily.LENGTHENING,
    Rule.MADD_JAIZ_MUNFASIL: RuleFamily.LENGTHENING,
    Rule.MADD_LAZIM: RuleFamily.LENGTHENING,
    Rule.MADD_ARID_LIL_SUKUN: RuleFamily.LENGTHENING,
    Rule.MADD_LEEN: RuleFamily.LENGTHENING,
    Rule.IWAD: RuleFamily.LENGTHENING,
    Rule.WASL_ELISION: RuleFamily.ASSIMILATION,
    Rule.WASL_START: RuleFamily.INSERTION,
    Rule.ILTIQA_REPAIR: RuleFamily.INSERTION,
    Rule.WAQF_ENDING: RuleFamily.ASSIMILATION,
    Rule.SILAH: RuleFamily.LENGTHENING,
    Rule.SAKT: RuleFamily.RELEASE,
    Rule.PLAIN: RuleFamily.ASSIMILATION,
}

#: Rules that classify without producing a sound of their own. Invariant E4
#: checks a rule's emissions against its declaration here.
CLASSIFICATION_ONLY: frozenset[Rule] = frozenset(
    {
        Rule.TARQEEQ,
        Rule.IZHAR_HALQI,
        Rule.IZHAR_MUTLAQ,
        Rule.IZHAR_SHAFAWI,
        Rule.LAM_QAMARIYYAH,
        Rule.MADD_TABII,
        Rule.MADD_WAJIB_MUTTASIL,
        Rule.MADD_JAIZ_MUNFASIL,
        Rule.MADD_LAZIM,
        Rule.MADD_ARID_LIL_SUKUN,
        Rule.MADD_LEEN,
    }
)
