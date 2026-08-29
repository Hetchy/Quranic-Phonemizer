from __future__ import annotations

import unicodedata

import pytest

from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import (
    BoundaryPlan,
    Junction,
    Location,
    Riwayah,
    Script,
    VerseRef,
)
from quranic_phonemizer.riwayat.warsh.raa import (
    PROFILE,
    SELECTOR_BY_OWNER,
    SELECTOR_JUNCTIONS,
    RaaKey,
    selector_profile,
)
from quranic_phonemizer.rules.raa import systematic_sites

REPEATED_HEAVY = frozenset({
    Location(2, 231, 13),
    Location(9, 107, 4),
    Location(18, 18, 19),
    Location(33, 13, 25),
    Location(71, 6, 5),
    Location(33, 16, 4),
    Location(71, 9, 7),
    Location(6, 6, 19),
    Location(11, 52, 10),
    Location(71, 11, 4),
})
OTHER_ASHIR = frozenset({
    Location(22, 13, 10),
    Location(26, 214, 2),
    Location(58, 22, 21),
})


def _keys(locations) -> frozenset[RaaKey]:
    return frozenset((location, 1) for location in locations)


def test_only_fixed_exclusion_owners_are_bound():
    assert set(PROFILE.by_owner) == {
        "raa_fixed_ibrahim_heavy",
        "raa_fixed_israil_heavy",
        "raa_fixed_imran_heavy",
        "raa_fixed_repeated_heavy",
        "raa_fixed_hidhrahum_light",
        "raa_fixed_other_ashir_light",
    }


def test_fixed_register_subtotals_and_exact_members_are_stable():
    assert PROFILE.by_owner["raa_fixed_repeated_heavy"] == _keys(REPEATED_HEAVY)
    assert PROFILE.by_owner["raa_fixed_hidhrahum_light"] == {
        (Location(4, 102, 26), 1)
    }
    assert PROFILE.by_owner["raa_fixed_other_ashir_light"] == _keys(OTHER_ASHIR)
    assert sum(map(len, PROFILE.by_owner.values())) == 129


def test_no_fixed_target_has_two_weight_owners():
    owners = tuple(PROFILE.by_owner.values())

    assert sum(map(len, owners)) == len(set().union(*owners))


def test_fixed_lexeme_subtotals_match_the_closed_foreign_name_families():
    package = recitation(Riwayah.WARSH)

    def plain(text: str) -> str:
        return "".join(
            char
            for char in unicodedata.normalize("NFD", text)
            if unicodedata.category(char)[0] != "M" and char != "ـ"
        )

    families = {
        "raa_fixed_ibrahim_heavy": ("ابرهيم", 69),
        "raa_fixed_israil_heavy": ("اسراءيل", 43),
        "raa_fixed_imran_heavy": ("عمرن", 3),
    }
    for owner, (skeleton, count) in families.items():
        found = {
            (location, 1)
            for location in package.corpus.entries
            if plain(package.corpus.entries[location].text).endswith(skeleton)
        }
        assert len(found) == count
        assert PROFILE.by_owner[owner] == found

    assert (Location(10, 16, 14), 1) not in PROFILE.heavy  # عُمُراٗ
    assert (Location(35, 11, 22), 1) not in PROFILE.heavy  # مُّعَمَّرٖ


def test_selector_register_subtotals_are_stable():
    assert {
        owner: len(keys) for owner, keys in SELECTOR_BY_OWNER.items()
    } == {
        "raa_firq": 1, "raa_alqitr_waqf": 1, "raa_misr_waqf": 4,
        "raa_wanuthur_waqf": 6, "raa_yasr_waqf": 1, "raa_asr_waqf": 3,
        "raa_ishruna_kibr": 2, "raa_alishraq": 1, "raa_hayran": 1,
        "raa_bisharar": 2, "raa_five_words": 16, "raa_sihra": 1,
        "raa_iram": 1, "raa_alif_ayn": 4, "raa_alif_hamza": 3,
        "raa_dual_alif": 4, "raa_ashiratukum": 1, "raa_wizraka": 1,
        "raa_dhikraka": 1, "raa_wizra_ukhra": 5, "raa_ijrami": 1,
        "raa_hidhrakum": 2, "raa_ibrah_kibrahu": 7,
        "raa_hasirat_suduruhum": 1,
    }


def test_no_raa_key_has_both_a_fixed_and_a_selector_owner():
    fixed = PROFILE.heavy | PROFILE.light
    selected = frozenset().union(*SELECTOR_BY_OWNER.values())
    assert not fixed & selected
    owners = tuple(SELECTOR_BY_OWNER.values())
    assert sum(map(len, owners)) == len(selected)


def test_every_published_raa_selector_has_register_or_dynamic_sites():
    package = recitation(Riwayah.WARSH)
    published = {point.value for point in package.khilaf.variants}
    assert published == set(SELECTOR_JUNCTIONS) | {
        "raa_fathatan", "raa_damma",
    }


@pytest.mark.slow
def test_systematic_consumer_counts_match_the_research():
    package = recitation(Riwayah.WARSH)
    profile = selector_profile(package.khilaf.variants)
    counts = {"raa_fathatan": 0, "raa_damma": 0}
    for surah_key, word_counts in sorted(
        package.corpus.surah_info.items(), key=lambda item: int(item[0])
    ):
        for ayah in range(1, len(word_counts) + 1):
            verse = VerseRef(int(surah_key), ayah)
            words = package.words(verse)
            built = package.build(package.read(Script.UTHMANI, verse, words))
            plan = BoundaryPlan(
                (Junction.JOIN,) * (len(built.score.words) - 1)
                + (Junction.STOP,)
            )
            for owner, _ in systematic_sites(built.score, plan, profile):
                counts[owner] += 1
    assert counts == {"raa_fathatan": 259, "raa_damma": 851}
