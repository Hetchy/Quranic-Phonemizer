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


WARSH_VARIANTS = {
    "raa_firq": (["light", "heavy"], "light"),
    "raa_alqitr_waqf": (["light", "heavy"], "light"),
    "raa_misr_waqf": (["heavy", "light"], "heavy"),
    "raa_wanuthur_waqf": (["light", "heavy"], "light"),
    "raa_yasr_waqf": (["light", "heavy"], "light"),
    "raa_asr_waqf": (["heavy", "light"], "heavy"),
    "raa_fathatan": (["light", "heavy_wasl", "heavy"], "light"),
    "raa_damma": (["light", "heavy"], "light"),
    "raa_ishruna_kibr": (["light", "heavy"], "light"),
    "raa_alishraq": (["heavy", "light"], "heavy"),
    "raa_hayran": (["heavy", "light"], "heavy"),
    "raa_bisharar": (["light", "heavy"], "light"),
    "raa_five_words": (["heavy", "light"], "heavy"),
    "raa_sihra": (["heavy", "light"], "heavy"),
    "raa_iram": (["heavy", "light"], "heavy"),
    "raa_alif_ayn": (["light", "heavy"], "light"),
    "raa_alif_hamza": (["light", "heavy"], "light"),
    "raa_dual_alif": (["light", "heavy"], "light"),
    "raa_ashiratukum": (["light", "heavy"], "light"),
    "raa_wizraka": (["light", "heavy"], "light"),
    "raa_dhikraka": (["light", "heavy"], "light"),
    "raa_wizra_ukhra": (["light", "heavy"], "light"),
    "raa_ijrami": (["light", "heavy"], "light"),
    "raa_hidhrakum": (["light", "heavy"], "light"),
    "raa_ibrah_kibrahu": (["light", "heavy"], "light"),
    "raa_hasirat_suduruhum": (["light", "heavy"], "light"),
}


def test_catalogues_are_riwayah_specific():
    expected = {
        name: {"options": options, "default": default}
        for name, (options, default) in WARSH_VARIANTS.items()
    }
    assert available_variants("warsh") == expected
    with pytest.raises(ValueError):
        Phonemizer(riwayah="warsh", variants={"yabsut": "seen"})
    with pytest.raises(ValueError):
        Phonemizer(variants={"raa_fathatan": "light"})


def test_warsh_catalogue_rows_carry_registers_and_dynamic_scopes():
    catalogue = variant_catalogue("warsh")
    assert len(catalogue) == 26
    assert {row["id"] for row in catalogue} == set(WARSH_VARIANTS)
    assert all(row["group"] == "raa_pronunciation" for row in catalogue)
    assert all(
        row["display_name"] == row["id"].replace("_", " ").title()
        for row in catalogue
    )
    by_id = {row["id"]: row for row in catalogue}
    systematic = {"raa_fathatan", "raa_damma"}
    assert {
        row_id for row_id, row in by_id.items()
        if row["subgroup"] == "systematic"
    } == systematic
    assert all(
        row["subgroup"] == "lexical"
        for row_id, row in by_id.items() if row_id not in systematic
    )
    assert by_id["raa_five_words"]["occurrence_count"] == 16
    assert by_id["raa_ibrah_kibrahu"]["occurrence_count"] == 7
    assert by_id["raa_wizra_ukhra"]["occurrence_count"] == 5
    assert by_id["raa_fathatan"]["occurrence_count"] is None
    pair = by_id["raa_hasirat_suduruhum"]["occurrences"][0]
    assert pair["anchor"] == "boundary"
    assert pair["word_refs"] == ["4:89:11", "4:89:12"]
    assert pair["requires"] == "wasl"


def test_warsh_systematic_selectors_report_dynamic_occurrences():
    joined = Phonemizer(riwayah="warsh").analyse("2:157:20-2:157:21")
    rows = [
        row for row in joined.variant_occurrences()
        if row["variant_id"] == "raa_fathatan"
    ]
    assert len(rows) == 1
    assert rows[0]["selected"] == "light"
    assert rows[0]["word_ids"] == [0]
    assert not [
        row for row in joined.variant_occurrences()
        if row["variant_id"] == "raa_damma"
    ]


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


def test_catalogue_rows_expose_the_raa_subgroup_and_moved_group():
    catalogue = variant_catalogue("hafs")
    by_id = {row["id"]: row for row in catalogue}
    lexical = {
        "raa_firq", "raa_alqitr_waqf", "raa_misr_waqf",
        "raa_wanuthur_waqf", "raa_yasr_waqf", "raa_asr_waqf",
    }
    assert {row_id for row_id, row in by_id.items() if row["subgroup"]} == lexical
    assert all(by_id[row_id]["subgroup"] == "lexical" for row_id in lexical)
    assert by_id["maliyah_halak"]["group"] == "joined_readings"


def test_dynamic_nasal_selectors_report_realized_occurrences():
    joined = Phonemizer().analyse("2:56:3-2:56:4")
    rows = [
        row for row in joined.variant_occurrences()
        if row["variant_id"] == "iqlab_nasal"
    ]
    assert len(rows) == 1
    assert rows[0]["selected"] == "open"
    assert rows[0]["active"] is True and rows[0]["masked"] is False
    stopped = Phonemizer().analyse("2:56:3-2:56:4", stop_refs=("2:56:3",))
    assert not [
        row for row in stopped.variant_occurrences()
        if row["variant_id"] == "iqlab_nasal"
    ]


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
