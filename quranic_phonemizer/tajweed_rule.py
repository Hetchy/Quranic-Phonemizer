"""TajweedRule enum and tagging dataclass for structured tajweed annotations."""

from dataclasses import dataclass
from enum import Enum


class TajweedRule(Enum):
    # Ghunnah — nasalization rules
    NOON_GHUNNAH = "noon_ghunnah"
    MEEM_GHUNNAH = "meem_ghunnah"
    IKHFAA_NOON = "ikhfaa_noon"
    IKHFAA_TANWEEN = "ikhfaa_tanween"
    IKHFAA_SHAFAWI = "ikhfaa_shafawi"
    IQLAB_NOON = "iqlab_noon"
    IQLAB_TANWEEN = "iqlab_tanween"
    IDGHAM_GHUNNAH_NOON = "idgham_ghunnah_noon"
    IDGHAM_GHUNNAH_TANWEEN = "idgham_ghunnah_tanween"
    IDGHAM_SHAFAWI = "idgham_shafawi"

    # Silent — letter produces no sound
    VOWEL_SILENT = "vowel_silent"
    HAMZA_WASL_SILENT = "hamza_wasl_silent"
    LAM_SHAMSIYAH = "lam_shamsiyah"
    IDGHAM_BILA_GHUNNAH_NOON = "idgham_bila_ghunnah_noon"
    IDGHAM_BILA_GHUNNAH_TANWEEN = "idgham_bila_ghunnah_tanween"
    IDGHAM_MUTAMATHILAYN = "idgham_mutamathilayn"
    IDGHAM_MUTAQARIBAYN = "idgham_mutaqaribayn"
    IDGHAM_MUTAJANISAYN_KAMIL = "idgham_mutajanisayn_kamil"
    SILENT_ILTIQAA_SAKINAYN = "silent_iltiqaa_sakinayn"

    # Tafkheem — heaviness
    TAFKHEEM = "tafkheem"

    # Qalqala
    QALQALA_SUGHRA = "qalqala_sughra"
    QALQALA_KUBRA = "qalqala_kubra"

    # Hamza wasl vowel (when starting)
    HAMZA_WASL_FATHA = "hamza_wasl_fatha"
    HAMZA_WASL_KASRA = "hamza_wasl_kasra"
    HAMZA_WASL_DAMMA = "hamza_wasl_damma"

    # Iltiqaa (meeting of two sukuns)
    ILTIQAA_SAKINAYN_TANWEEN = "iltiqaa_sakinayn_tanween"

    # Idgham mutajanisayn naqis (partial)
    IDGHAM_MUTAJANISAYN_NAQIS = "idgham_mutajanisayn_naqis"

    # Madd — vowel lengthening
    MADD_TABII = "madd_tabii"
    MADD_WAJIB_MUTTASIL = "madd_wajib_muttasil"
    MADD_JAIZ_MUNFASIL = "madd_jaiz_munfasil"
    MADD_LAZIM = "madd_lazim"
    MADD_ARID_LISSUKUN = "madd_arid_lissukun"
    MADD_LEEN = "madd_leen"


@dataclass(frozen=True)
class TajweedRuleTag:
    rule: TajweedRule
    is_source: bool = True
