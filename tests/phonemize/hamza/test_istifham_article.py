from __future__ import annotations

import pytest

from quranic_phonemizer.model.address import KhilafId
from quranic_phonemizer.model.canon import Rule
from tests.support import (
    Expect,
    R,
    Site,
    VariantCase,
    assert_case,
    case_runs,
    isolated,
    pick,
    selected,
)


DHAKARAYN = (Site(hafs=("6:143", (10,))), 10)
ALAN = (Site(hafs=("10:51", (7,))), 7)
ALLAH = (Site(hafs=("10:59", (14,))), 14)

REGISTERS = {
    "dhakarayn": (
        DHAKARAYN,
        (Site(hafs=("6:144", (8,))), 8),
    ),
    "alan": (
        ALAN,
        (Site(hafs=("10:91", (1,))), 1),
    ),
    "allah": (
        ALLAH,
        (Site(hafs=("27:59", (9,))), 9),
    ),
}


def _case(
    case_id: str,
    target: tuple[Site, int],
    ibdal: str,
    tashil: str,
    madd_sound: str,
    indopak_ibdal_source: str,
    indopak_tashil_source: str,
) -> VariantCase:
    site, _ = target
    return VariantCase(
        id=case_id,
        site=site,
        selector=KhilafId.MADD_LAZIM_TASHEEL,
        faces={
            "madd_lazim": Expect(
                read=isolated(),
                phonemes=ibdal,
                char_rules=pick(
                    hafs_uthmani={"ا": R(
                        "ibdal_hamza", "madd_badal", "madd_lazim")},
                    hafs_indopak={indopak_ibdal_source: R(
                        "ibdal_hamza", "madd_badal", "madd_lazim")},
                ),
                sound_rules={madd_sound: R(
                    "ibdal_hamza", "madd_badal", "madd_lazim")},
            ),
            "tasheel": Expect(
                read=isolated(),
                phonemes=tashil,
                char_rules=pick(
                    hafs_uthmani={"ا": R("tashil")},
                    hafs_indopak={indopak_tashil_source: R("tashil")},
                ),
                sound_rules={"ʔ̞": R("tashil")},
                extra_phonemes=("tashil", "emphatic_fatha"),
            ),
        },
        default="madd_lazim",
    )


CASES = (
    # Hafs: ءَآلذَّكَرَيْنِ
    _case("dhakarayn", DHAKARAYN,
          "ʔ a: ðð a k a rˤ aˤ j n", "ʔ a ʔ̞ a ðð a k a rˤ aˤ j n",
          "a:", "ا", "ا"),
    # Hafs: ءَآلْـَٔـٰنَ
    _case("alan", ALAN,
          "ʔ a: l ʔ a: n", "ʔ a ʔ̞ a l ʔ a: n",
          "a:[1]", "@dagger_alif[1]", "@dagger_alif[1]"),
    # Hafs: ءَآللَّهُ
    _case("allah", ALLAH,
          "ʔ a: lˤlˤ aˤ: h", "ʔ a ʔ̞ a lˤlˤ aˤ: h",
          "a:", "@dagger_alif[1]", "@dagger_alif[1]"),
)

REGISTER_CASES = tuple(
    pytest.param(site, word, id=f"{form}-{site.address('hafs').verse}-{word}")
    for form, sites in REGISTERS.items()
    for site, word in sites
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_istifham_article_faces(run):
    assert_case(run)


@pytest.mark.parametrize(("site", "word"), REGISTER_CASES)
def test_every_istifham_article_site_accepts_both_faces(site, word):
    ibdal = selected(
        site, word, KhilafId.MADD_LAZIM_TASHEEL, "madd_lazim"
    )
    tashil = selected(site, word, KhilafId.MADD_LAZIM_TASHEEL, "tasheel")
    assert Rule.MADD_LAZIM in {
        occurrence.rule for occurrence in ibdal.performance.occurrences
    }
    assert Rule.TASHIL in {
        occurrence.rule for occurrence in tashil.performance.occurrences
    }


def test_tashil_extra_changes_only_the_eased_token():
    # ءَآلْـَٰٔنَ
    site, word = ALAN
    plain = selected(
        site, word, KhilafId.MADD_LAZIM_TASHEEL, "tasheel", extra=()
    )
    extra = selected(
        site, word, KhilafId.MADD_LAZIM_TASHEEL, "tasheel",
        extra=("tashil",),
    )
    assert plain.sounds(word)[2] == "ʔ"
    assert extra.sounds(word)[2] == "ʔ̞"
    assert extra.rules_on_sound(word, "ʔ̞") == {"tashil"}
