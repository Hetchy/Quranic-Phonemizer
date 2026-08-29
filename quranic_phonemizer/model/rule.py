"""The closed tajwid rule vocabulary and its semantic families."""

from enum import StrEnum


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
    TAQLIL = "taqlil"
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
    MADD_LEEN_MAHMUZ = "madd_leen_mahmuz"
    MADD_SILAH = "madd_silah"
    MADD_MIM_AL_JAM = "madd_mim_al_jam"
    MADD_YAA_ZAWAID = "madd_yaa_zawaid"
    IBDAL_HAMZA = "ibdal_hamza"
    NAQL = "naql"
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


HAMZA_WASL_START: frozenset[Rule] = frozenset({
    Rule.HAMZA_WASL_FATHA, Rule.HAMZA_WASL_KASRA, Rule.HAMZA_WASL_DAMMA,
})
IDGHAM_RULES: frozenset[Rule] = frozenset({
    Rule.IDGHAM_BI_GHUNNAH, Rule.IDGHAM_BILA_GHUNNAH, Rule.IDGHAM_SHAFAWI,
    Rule.IDGHAM_MUTAMATHILAYN, Rule.IDGHAM_MUTAQARIBAYN,
    Rule.IDGHAM_MUTAJANISAYN_KAMIL, Rule.IDGHAM_MUTAJANISAYN_NAQIS,
})
ILTIQA_RULES: frozenset[Rule] = frozenset({
    Rule.ILTIQA_HARAKA, Rule.ILTIQA_SHORTENING,
})
CLASSIFICATION_ONLY: frozenset[Rule] = frozenset({
    Rule.NAQL, Rule.TARQEEQ, Rule.GHUNNAH_MUSHADDADAH,
    Rule.IDGHAM_MUTAJANISAYN_NAQIS, Rule.IZHAR, Rule.IZHAR_SHAFAWI,
    Rule.LAM_QAMARIYYAH, Rule.MADD_BADAL, Rule.MADD_SILAH,
    Rule.MADD_MIM_AL_JAM, Rule.MADD_YAA_ZAWAID, Rule.MADD_MUTTASIL,
    Rule.MADD_MUNFASIL, Rule.MADD_LAZIM, Rule.MADD_ARID_LISSUKUN,
    Rule.MADD_LEEN, Rule.MADD_LEEN_MAHMUZ, Rule.IBDAL_HAMZA,
    Rule.TAQLIL, Rule.IMALA, Rule.TASHIL, Rule.ISHMAM,
}) | HAMZA_WASL_START


__all__ = [
    "CLASSIFICATION_ONLY", "HAMZA_WASL_START", "IDGHAM_RULES",
    "ILTIQA_RULES", "Rule",
]
