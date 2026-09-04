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
    "yaa_aatani_waqf": (["ithbat", "hadhf"], "ithbat"),
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
    "raa_fathatan": (["light", "heavy", "heavy_wasl"], "light"),
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
    "dhat_yaa": (["taqlil", "fath"], "taqlil"),
    "arakahum": (["taqlil", "fath"], "taqlil"),
    "al_jar": (["taqlil", "fath"], "taqlil"),
    "jabbarin": (["taqlil", "fath"], "taqlil"),
    "haa_verse_heads": (["fath", "taqlil"], "fath"),
    "maryam_haa_yaa": (["taqlil", "fath"], "taqlil"),
    "yaseen_yaa": (["fath", "taqlil"], "fath"),
    "lam_dhat_yaa": (["fath_tafkheem", "taqlil_tarqiq"], "fath_tafkheem"),
    "lam_verse_heads": (["taqlil_tarqiq", "fath_tafkheem"], "taqlil_tarqiq"),
    "lam_separated_by_alif": (["tafkheem", "tarqiq"], "tafkheem"),
    "lam_final_waqf": (["tafkheem", "tarqiq"], "tafkheem"),
    "lam_after_taa": (["tafkheem", "tarqiq"], "tafkheem"),
    "lam_after_zhaa": (["tafkheem", "tarqiq"], "tafkheem"),
    "lam_salsal": (["tarqiq", "tafkheem"], "tarqiq"),
    "tamanna_noon": (["ishmam", "ikhtilas"], "ishmam"),
    "istifham_article": (["ibdal", "tashil"], "ibdal"),
    "noon_wasl": (["izhar", "idgham"], "izhar"),
    "maliyah_halak": (["idgham", "sakt"], "idgham"),
    "kitabiyah_inni": (["tahqiq", "naql"], "tahqiq"),
    "article_ibtidaa": (["hamza", "lam"], "hamza"),
    "hamza_dhat_fath": (["ibdal", "tashil"], "ibdal"),
    "hamza_muttafiq": (["ibdal", "tashil"], "ibdal"),
    "hamza_damm_kasr": (["ibdal", "tashil"], "ibdal"),
    "jaa_aal": (["tashil", "ibdal"], "tashil"),
    "hamza_kasr_yaa": (["ibdal", "tashil", "yaa"], "ibdal"),
    "hamza_aimma": (["tashil", "ibdal"], "tashil"),
    "hamza_arayta": (["ibdal", "tashil"], "ibdal"),
    "ha_antum": (["ibdal", "hadhf", "ithbat"], "ibdal"),
    "allai_waqf": (["tashil", "ibdal_yaa"], "tashil"),
    "iqlab_nasal": (["open", "closed"], "open"),
    "ikhfaa_shafawi_nasal": (["open", "closed"], "open"),
}

WARSH_GROUPS = {
    **dict.fromkeys(
        (name for name in WARSH_VARIANTS if name.startswith("raa_")),
        "raa_pronunciation",
    ),
    "dhat_yaa": "inclination",
    "arakahum": "inclination",
    "al_jar": "inclination",
    "jabbarin": "inclination",
    "haa_verse_heads": "inclination",
    "maryam_haa_yaa": "inclination",
    "yaseen_yaa": "inclination",
    "lam_dhat_yaa": "lam_pronunciation",
    "lam_verse_heads": "lam_pronunciation",
    "lam_separated_by_alif": "lam_pronunciation",
    "lam_final_waqf": "lam_pronunciation",
    "lam_after_taa": "lam_pronunciation",
    "lam_after_zhaa": "lam_pronunciation",
    "lam_salsal": "lam_pronunciation",
    "tamanna_noon": "word_readings",
    "istifham_article": "word_readings",
    "noon_wasl": "joined_readings",
    "maliyah_halak": "joined_readings",
    "kitabiyah_inni": "joined_readings",
    "article_ibtidaa": "stopping_starting",
    "hamza_dhat_fath": "hamza_readings",
    "hamza_muttafiq": "hamza_readings",
    "hamza_damm_kasr": "hamza_readings",
    "jaa_aal": "hamza_readings",
    "hamza_kasr_yaa": "hamza_readings",
    "hamza_aimma": "hamza_readings",
    "hamza_arayta": "hamza_readings",
    "ha_antum": "hamza_readings",
    "allai_waqf": "hamza_readings",
    "iqlab_nasal": "nasal_variants",
    "ikhfaa_shafawi_nasal": "nasal_variants",
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


@pytest.mark.parametrize("riwayah", ("hafs", "warsh"))
def test_catalogue_publishes_every_default_as_option_one(riwayah):
    assert all(
        row["options"][0] == row["default"]
        for row in variant_catalogue(riwayah)
    )


def test_warsh_catalogue_rows_carry_registers_and_dynamic_scopes():
    catalogue = variant_catalogue("warsh")
    assert len(catalogue) == 57
    assert {row["id"] for row in catalogue} == set(WARSH_VARIANTS)
    assert {row["id"]: row["group"] for row in catalogue} == WARSH_GROUPS
    assert all(
        row["display_name"] == row["id"].replace("_", " ").title()
        for row in catalogue
    )
    hidden = {row["id"] for row in catalogue if not row["website_visible"]}
    assert hidden == {"iqlab_nasal", "ikhfaa_shafawi_nasal"}
    by_id = {row["id"]: row for row in catalogue}
    systematic = {"raa_fathatan", "raa_damma"}
    assert {
        row_id for row_id, row in by_id.items()
        if row["subgroup"] == "systematic" and row_id.startswith("raa_")
    } == systematic
    assert all(
        row["subgroup"] == "lexical"
        for row_id, row in by_id.items()
        if row_id not in systematic and row_id.startswith("raa_")
    )
    lam_systematic = {"lam_after_taa", "lam_after_zhaa"}
    assert {
        row_id for row_id, row in by_id.items()
        if row["subgroup"] == "systematic" and row_id.startswith("lam_")
    } == lam_systematic
    assert all(
        row["subgroup"] == "lexical"
        for row_id, row in by_id.items()
        if row_id not in lam_systematic and row_id.startswith("lam_")
    )
    assert all(
        row["subgroup"] is None
        for row_id, row in by_id.items()
        if not row_id.startswith(("raa_", "lam_"))
    )
    assert list(dict.fromkeys(
        row["group"] for row in catalogue if row["website_visible"]
    )) == [
        "word_readings", "joined_readings", "stopping_starting",
        "inclination", "hamza_readings", "lam_pronunciation",
        "raa_pronunciation",
    ]
    assert by_id["raa_five_words"]["occurrence_count"] == 16
    assert by_id["raa_ibrah_kibrahu"]["occurrence_count"] == 7
    assert by_id["raa_wizra_ukhra"]["occurrence_count"] == 5
    assert by_id["raa_fathatan"]["occurrence_count"] is None
    pair = by_id["raa_hasirat_suduruhum"]["occurrences"][0]
    assert pair["anchor"] == "boundary"
    assert pair["word_refs"] == ["4:89:11", "4:89:12"]
    assert pair["target_word_refs"] == ["4:89:11"]
    assert pair["requires"] == "wasl"


def test_warsh_inclination_and_lam_rows_resolve_their_registers():
    by_id = {row["id"]: row for row in variant_catalogue("warsh")}
    counts = {
        "arakahum": 1, "al_jar": 2, "jabbarin": 2, "haa_verse_heads": 25,
        "maryam_haa_yaa": 1, "yaseen_yaa": 1, "lam_dhat_yaa": 7,
        "lam_verse_heads": 3, "lam_separated_by_alif": 5,
        "lam_final_waqf": 9, "lam_salsal": 4,
    }
    for row_id, count in counts.items():
        assert by_id[row_id]["occurrence_count"] == count, row_id
    assert by_id["dhat_yaa"]["occurrence_count"] == 1154
    assert by_id["lam_after_taa"]["dynamic_scope"] == "eligible_lam_taa"
    assert by_id["lam_after_zhaa"]["dynamic_scope"] == "eligible_lam_zhaa"
    assert all(
        occurrence["requires"] == "waqf"
        for occurrence in by_id["lam_final_waqf"]["occurrences"]
    )
    masked = {
        occurrence["ref"]
        for occurrence in by_id["lam_dhat_yaa"]["occurrences"]
        if occurrence["requires"] == "waqf"
    }
    assert masked == {"2:124:11", "87:12:2"}
    arakahum = by_id["arakahum"]["occurrences"][0]
    assert arakahum["ref"] == "8:44:8"
    assert arakahum["requires"] == "all"
    waqf_only = [
        occurrence for occurrence in by_id["dhat_yaa"]["occurrences"]
        if occurrence["requires"] == "waqf"
    ]
    assert len(waqf_only) == 82


def test_warsh_hamza_and_boundary_rows_resolve_their_registers():
    by_id = {row["id"]: row for row in variant_catalogue("warsh")}
    counts = {
        "tamanna_noon": 1, "istifham_article": 6, "noon_wasl": 1,
        "maliyah_halak": 1, "kitabiyah_inni": 1,
        "hamza_dhat_fath": 20, "hamza_muttafiq": 36, "hamza_damm_kasr": 23,
        "jaa_aal": 2, "hamza_kasr_yaa": 2, "hamza_aimma": 5,
        "hamza_arayta": 34, "ha_antum": 4, "allai_waqf": 4,
    }
    for row_id, count in counts.items():
        assert by_id[row_id]["occurrence_count"] == count, row_id
    assert by_id["article_ibtidaa"]["dynamic_scope"] == "article_starts"
    assert by_id["article_ibtidaa"]["occurrence_count"] is None
    assert all(
        occurrence["requires"] == "waqf"
        for occurrence in by_id["allai_waqf"]["occurrences"]
    )
    assert all(
        occurrence["requires"] == "wasl"
        for occurrence in by_id["hamza_muttafiq"]["occurrences"]
    )
    kitabiyah = by_id["kitabiyah_inni"]["occurrences"][0]
    assert kitabiyah["anchor"] == "boundary"
    assert kitabiyah["word_refs"] == ["69:18:9", "69:19:1"]
    assert kitabiyah["requires"] == "wasl"


def test_warsh_article_ibtidaa_reports_started_sites_only():
    started = Phonemizer(riwayah="warsh").analyse("2:21:4-2:21:5")
    rows = [
        row for row in started.variant_occurrences()
        if row["variant_id"] == "article_ibtidaa"
    ]
    assert len(rows) == 1
    assert rows[0]["selected"] == "hamza"
    assert rows[0]["word_ids"] == [0]
    joined = Phonemizer(riwayah="warsh").analyse("2:21:3-2:21:5")
    assert not [
        row for row in joined.variant_occurrences()
        if row["variant_id"] == "article_ibtidaa"
    ]


def test_warsh_lam_generals_report_dynamic_occurrences():
    joined = Phonemizer(riwayah="warsh").analyse("97:5")
    rows = [
        row for row in joined.variant_occurrences()
        if row["variant_id"] == "lam_after_taa"
    ]
    assert len(rows) == 1
    assert rows[0]["selected"] == "tafkheem"
    assert not [
        row for row in joined.variant_occurrences()
        if row["variant_id"] == "lam_after_zhaa"
    ]
    stopped = Phonemizer(riwayah="warsh").analyse(
        "7:117:1-7:117:4", stop_refs=("7:117:3",)
    )
    taa_rows = [
        row for row in stopped.variant_occurrences()
        if row["variant_id"] == "lam_after_taa"
    ]
    assert not taa_rows  # the stopped final lam belongs to lam_final_waqf


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
    assert list(dict.fromkeys(
        row["group"] for row in catalogue if row["website_visible"]
    )) == [
        "word_readings", "joined_readings", "stopping_starting", "sakt",
        "raa_pronunciation",
    ]
    istifham = next(row for row in catalogue if row["id"] == "istifham_article")
    assert istifham["occurrence_count"] == 6
    assert "ءَآلذَّكَرَيْنِ" in istifham["description"]
    assert "ءَآلْـَٔـٰنَ" in istifham["description"]
    assert "ءَآللَّهُ" in istifham["description"]
    wanuthur = next(row for row in catalogue if row["id"] == "raa_wanuthur_waqf")
    assert "وَنُذُرِ" in wanuthur["description"]


def test_catalogue_rows_expose_the_raa_subgroup_and_sakt_group():
    catalogue = variant_catalogue("hafs")
    by_id = {row["id"]: row for row in catalogue}
    lexical = {
        "raa_firq", "raa_alqitr_waqf", "raa_misr_waqf",
        "raa_wanuthur_waqf", "raa_yasr_waqf", "raa_asr_waqf",
    }
    assert {row_id for row_id, row in by_id.items() if row["subgroup"]} == lexical
    assert all(by_id[row_id]["subgroup"] == "lexical" for row_id in lexical)
    assert by_id["maliyah_halak"]["group"] == "sakt"


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
        "target_word_ids": [0, 1],
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
