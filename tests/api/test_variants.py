from __future__ import annotations

import pytest

from quranic_phonemizer import Phonemizer, available_variants, variant_catalogue
from quranic_phonemizer.model.address import KhilafId, Option, VariantSelection
from tests.support import Site, reading

VARIANTS = {
    "yabsut": (["seen", "saad"], "seen"),
    "bastah": (["seen", "saad"], "seen"),
    "almusaytirun": (["saad", "seen"], "saad"),
    "bimusaytir": (["saad", "seen"], "saad"),
    "iqlab_nasal": (["open", "closed"], "open"),
    "ikhfaa_shafawi_nasal": (["open", "closed"], "open"),
    "raa_firq": (["light", "heavy"], "light"),
    "raa_alqitr_waqf": (["light", "heavy"], "light"),
    "raa_misr_waqf": (["heavy", "light"], "heavy"),
    "raa_wanuthur_waqf": (["light", "heavy"], "light"),
    "raa_yasr_waqf": (["light", "heavy"], "light"),
    "raa_asr_waqf": (["light", "heavy"], "light"),
    "daaf_haraka": (["fatha", "damma"], "fatha"),
    "yaa_aatani_waqf": (["hadhf", "ithbat"], "ithbat"),
    "noon_wasl": (["izhar", "idgham"], "izhar"),
    "yaseen_wasl": (["izhar", "idgham"], "izhar"),
    "istifham_article": (["ibdal", "tashil"], "ibdal"),
    "tamanna_noon": (["ishmam", "ikhtilas"], "ishmam"),
    "maliyah_halak": (["sakt", "idgham"], "sakt"),
    "salasila_waqf": (["hadhf", "ithbat"], "hadhf"),
    "alism_ibtidaa": (["hamza", "lam"], "hamza"),
    "irkab_maana": (["idgham", "izhar"], "idgham"),
    "yalhath_dhalik": (["idgham", "izhar"], "idgham"),
    "iwaja_qayyima": (["sakt", "idraj"], "sakt"),
    "man_raq": (["sakt", "idraj"], "sakt"),
    "bal_ran": (["sakt", "idraj"], "sakt"),
}


def test_public_catalogue_and_defaults_are_scalar():
    expected = {
        name: {"options": options, "default": default}
        for name, (options, default) in VARIANTS.items()
    }
    assert available_variants("hafs") == expected
    resolved = Phonemizer().analyse("1:1").analysis.variant
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


def test_selecting_one_variant_leaves_other_defaults_unchanged():
    result = Phonemizer(
        variants={"iqlab_nasal": "closed"}
    ).analyse("1:1")
    assert result.analysis.variant["iqlab_nasal"] == "closed"
    assert result.analysis.variant["ikhfaa_shafawi_nasal"] == "open"


def test_catalogues_are_riwayah_specific():
    assert available_variants("warsh") == {}
    with pytest.raises(ValueError):
        Phonemizer(riwayah="warsh", variants={"yabsut": "seen"})


def test_variant_catalogue_owns_website_metadata_and_occurrences():
    catalogue = variant_catalogue("hafs")
    assert len(catalogue) == 26
    assert {row["id"] for row in catalogue} == set(VARIANTS)
    assert all(row["display_name"] and row["group"] for row in catalogue)
    assert all(
        row["display_name"] == row["id"].replace("_", " ").title()
        for row in catalogue
    )
    hidden = {row["id"] for row in catalogue if not row["website_visible"]}
    assert hidden == {"iqlab_nasal", "ikhfaa_shafawi_nasal"}
    istifham = next(row for row in catalogue if row["id"] == "istifham_article")
    assert istifham["occurrence_count"] == 6
    assert "ءَآلذَّكَرَيْنِ" in istifham["description"]
    assert "ءَآلْـَٔـٰنَ" in istifham["description"]
    assert "ءَآللَّهُ" in istifham["description"]
    wanuthur = next(row for row in catalogue if row["id"] == "raa_wanuthur_waqf")
    assert "وَنُذُرِ" in wanuthur["description"]


def test_analysis_reports_active_and_masked_variant_occurrences():
    joined = Phonemizer().analyse("11:42:14-11:42:15")
    assert joined.variant_occurrences() == ({
        "variant_id": "irkab_maana",
        "selected": "idgham",
        "word_ids": [0, 1],
        "anchor": "boundary",
        "anchor_word_id": 0,
        "anchor_boundary_id": 1,
        "requires": "wasl",
        "active": True,
        "masked": False,
    },)
    stopped = Phonemizer().analyse(
        "11:42:14-11:42:15", stop_refs=("11:42:14",)
    )
    assert stopped.variant_occurrences()[0]["masked"] is True
