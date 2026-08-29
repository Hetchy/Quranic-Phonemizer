from __future__ import annotations

import unicodedata

from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Location, Riwayah
from quranic_phonemizer.riwayat.warsh.raa import PROFILE, RaaKey

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
