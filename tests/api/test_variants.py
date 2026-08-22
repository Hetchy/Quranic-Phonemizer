from __future__ import annotations

import pytest

from quranic_phonemizer import Phonemizer, available_variants
from quranic_phonemizer.model.address import KhilafId, Option, VariantSelection
from tests.support import Site, reading


VARIANTS = {
    "seen_sad_yabsut": (["seen", "saad"], "seen"),
    "seen_sad_bastah": (["seen", "saad"], "seen"),
    "seen_sad_al_musaytirun": (["saad", "seen"], "saad"),
    "seen_sad_bimusaytir": (["saad", "seen"], "saad"),
    "iqlab_nasal": (["assimilated", "bilabial"], "assimilated"),
    "ikhfaa_shafawi_nasal": (["assimilated", "bilabial"], "assimilated"),
    "raa_firq_wasl": (["heavy", "light"], "heavy"),
    "raa_alqitr_waqf": (["light", "heavy"], "light"),
    "raa_misr_waqf": (["heavy", "light"], "heavy"),
    "raa_nuthur_waqf": (["heavy", "light"], "heavy"),
    "raa_yasr_waqf": (["light", "heavy"], "light"),
    "raa_asr_waqf": (["light", "heavy"], "light"),
    "daaf_haraka": (["fatha", "damma"], "fatha"),
    "yaa_aatani_waqf": (["hadhf", "ithbat"], "hadhf"),
    "noon_yaseen_wasl": (["izhar", "idgham"], "izhar"),
    "madd_lazim_tasheel": (["madd_lazim", "tasheel"], "madd_lazim"),
}


def test_public_catalogue_and_defaults_are_scalar():
    expected = {
        name: {"options": options, "default": default}
        for name, (options, default) in VARIANTS.items()
    }
    assert available_variants("hafs") == expected
    resolved = Phonemizer().phonemize("1:1").variant
    assert resolved == {name: default for name, (_, default) in VARIANTS.items()}


@pytest.mark.parametrize(
    "removed", ("raa_tafkheem", "yaa_ithbat", "seen_sad", "nucleus_vowel")
)
def test_removed_aggregate_ids_are_rejected(removed):
    with pytest.raises(ValueError):
        Phonemizer(variants={removed: "unused"})


def test_nested_and_duplicate_scalar_selections_are_rejected():
    with pytest.raises(TypeError, match="scalar strings"):
        Phonemizer(variants={"raa_misr_waqf": {"misr": "light"}})
    with pytest.raises(TypeError):
        Option(KhilafId.RAA_MISR_WAQF, "light", "misr")
    duplicate = VariantSelection(
        (Option(KhilafId.DAAF_HARAKA, "fatha"),
         Option(KhilafId.DAAF_HARAKA, "damma"))
    )
    with pytest.raises(ValueError, match="more than one"):
        reading(Site(hafs=("30:54", (5,))), selection=duplicate, isolated=5)


def test_invalid_scalar_choice_is_rejected_before_phonemizing():
    with pytest.raises(ValueError, match="not an option"):
        Phonemizer(variants={"daaf_haraka": "kasra"})
