from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated, joining


CASES = (
    # ٱلْحَمْدُ
    Case(
        id="before-dal",
        site=Site(hafs=("1:2", (1,))),
        read=isolated(),
        phonemes="ʔ a l ħ a m d Q",
        char_rules={"م": R("izhar_shafawi")},
        sound_rules={"m": R("izhar_shafawi")},
    ),
    # أَنْعَمْتَ
    Case(
        id="before-taa",
        site=Site(hafs=("1:7", (3,))),
        read=isolated(),
        phonemes="ʔ a n ʕ a m t",
        char_rules={"م": R("izhar_shafawi")},
        sound_rules={"m": R("izhar_shafawi")},
    ),
    # أَمْثَالَهُمْ فَإِذَا
    Case(
        id="verse-seam",
        site=Site(hafs=("47:3", (18,))),
        read=joining(),
        phonemes="ʔ a m θ a: l a h u m",
        char_rules={"م[2]": R("izhar_shafawi")},
        sound_rules={"m[2]": R("izhar_shafawi")},
    ),
    # مَرْيَمَ
    Case(
        id="pausal-meem-after-haraka",
        site=Site(hafs=("2:87", (12,))),
        read=isolated(),
        phonemes="m a rˤ j a m",
        char_rules={"م[2]": R("izhar_shafawi")},
        sound_rules={"m[2]": R("izhar_shafawi")},
    ),
    # عَلِيمٌ
    Case(
        id="pausal-meem-after-tanwin",
        site=Site(hafs=("2:29", (19,))),
        read=isolated(),
        phonemes="ʕ a l i: m",
        char_rules={"م": R("izhar_shafawi")},
        sound_rules={"m": R("izhar_shafawi")},
        silent=("@dammatan",),
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_izhar_shafawi(run):
    assert_case(run)
