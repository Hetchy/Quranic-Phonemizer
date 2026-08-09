"""The Score: canonical positions, and the closed rule vocabulary.

Boundary-free and script-free: varies only with the riwayah and the
variant selection.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

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
    *length* lives on `Nucleus`. `WASL` and `SILAH` are exact mirrors.
    """

    PLAIN = "plain"
    GEMINATE = "geminate"
    WASL = "wasl"
    SILAH = "silah"
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
    """Long in wasl, absent at pause."""

    quality: Quality
    kind: NucleusKind = NucleusKind.SILAH


@dataclass(frozen=True, slots=True)
class PausalLong:
    """Short in wasl, long at pause. The seven alifs."""

    quality: Quality
    kind: NucleusKind = NucleusKind.PAUSAL_LONG


Nucleus: TypeAlias = Silent | Short | Long | Silah | PausalLong

SILENT = Silent()


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


class RuleFamily(StrEnum):
    """What a script adapter can genuinely see. Attestation names one of
    these, never a `Rule`: choosing among idgham members needs the
    previous word, the pair tables and the ghunnah split."""

    ASSIMILATION = "assimilation"
    NASALIZATION = "nasalization"
    INSERTION = "insertion"
    LENGTHENING = "lengthening"
    EMPHASIS = "emphasis"
    RELEASE = "release"
    ELISION = "elision"
    """A sound a boundary removes. No script attests one, so it appears in
    `FAMILY_OF` and never in an inventory."""


class Phase(StrEnum):
    """Closed and ordered. Within a phase, rules are unordered and
    conflicts are errors."""

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

    IBDAL_HAMZA = "ibdal_hamza"
    WASL_ELISION = "wasl_elision"
    WASL_START = "wasl_start"
    ILTIQA_REPAIR = "iltiqa_repair"
    WAQF_ENDING = "waqf_ending"
    PAUSAL_ALIF = "pausal_alif"
    SILAH = "silah"
    SAKT = "sakt"

    PLAIN = "plain"


#: Every `Rule` declares its family, which is what a script may attest
#: and gives projections a coarse grouping for free.
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
    Rule.IBDAL_HAMZA: RuleFamily.LENGTHENING,
    Rule.WASL_ELISION: RuleFamily.ELISION,
    Rule.WASL_START: RuleFamily.INSERTION,
    Rule.ILTIQA_REPAIR: RuleFamily.INSERTION,
    Rule.WAQF_ENDING: RuleFamily.ELISION,
    Rule.PAUSAL_ALIF: RuleFamily.ELISION,
    Rule.SILAH: RuleFamily.LENGTHENING,
    Rule.SAKT: RuleFamily.RELEASE,
    Rule.PLAIN: RuleFamily.ELISION,
}

#: Rules that classify without producing a sound of their own.
CLASSIFICATION_ONLY: frozenset[Rule] = frozenset(
    {
        Rule.TARQEEQ,
        Rule.TAFKHEEM,
        # Both emit `Recolour`, which modifies a sound rather than
        # producing one, so neither owns an attribution.
        Rule.WASL_START,
        # The wasl hamza sounds by the plain default already; the
        # occurrence only records that wasl was started, itself a
        # classification.
        Rule.IDGHAM_MUTAJANISAYN_NAQIS,
        # The first letter colours the second rather than merging into
        # it, so there is no separate sound to attribute.
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
        Rule.ILTIQA_REPAIR,
        Rule.PAUSAL_ALIF,
        # Both emit `Relength`, which modifies a sound rather than producing
        # one - the same footing as TAFKHEEM/TARQEEQ. Listing a rule here
        # permits an occurrence with no attribution; it does not forbid one,
        # so the tanween half of ILTIQA_REPAIR may still realize its kasra.
        Rule.IMALA,
        Rule.TASHIL,
        Rule.ISHMAM,
        Rule.SILAH,
        Rule.SAKT,
        # Canonical Score facts, realized already coloured by the plain
        # default; these rules exist only to give a projection a name for
        # what it sees. See `rules/annotation.py`.
    }
)
