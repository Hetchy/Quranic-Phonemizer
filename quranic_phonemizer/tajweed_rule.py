"""TajweedRule enum and tagging dataclass for structured tajweed annotations."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple


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


# Flyweight pool: at most ~36 rules x 2 is_source values = 72 distinct tags.
# Pre-populated lazily; subsequent allocations return the cached instance.
_TAG_POOL: Dict[Tuple[TajweedRule, bool], TajweedRuleTag] = {}

_orig_tag_new = TajweedRuleTag.__new__


def _intern_tag_new(cls, rule: TajweedRule, is_source: bool = True):
    key = (rule, is_source)
    cached = _TAG_POOL.get(key)
    if cached is not None:
        return cached
    obj = _orig_tag_new(cls)
    object.__setattr__(obj, "rule", rule)
    object.__setattr__(obj, "is_source", is_source)
    _TAG_POOL[key] = obj
    return obj


def _intern_tag_init(self, rule: TajweedRule = None, is_source: bool = True):  # noqa: ARG001
    # Attributes are already set by __new__ (or were the first time the
    # instance was created). Frozen dataclass __init__ would attempt to
    # re-set frozen fields, raising FrozenInstanceError, so override.
    pass


TajweedRuleTag.__new__ = _intern_tag_new
TajweedRuleTag.__init__ = _intern_tag_init
