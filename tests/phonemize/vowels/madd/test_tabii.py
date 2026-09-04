from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated, joining, pick

CASES = (
    # Hafs: بِمَا
    # Warsh: بِمَا
    Case(id="long-a", site=Site.shared("2:10", (10,)), read=isolated(),
         phonemes="b i m a:", char_rules={"ا": R("madd_tabii")},
         sound_rules={"a:": R("madd_tabii")}),
    # Hafs: فِيهِ
    # Warsh: فِيهِۖ
    Case(id="long-i", site=Site.shared("2:20", (9,)), read=joining(),
         phonemes="f i: h i", char_rules={"ي": R("madd_tabii")},
         sound_rules={"i:": R("madd_tabii")}),
    # Hafs: مُوسَىٰٓ
    Case(id="two-ordinary-longs", site=Site(hafs=("20:9", (4,))), read=isolated(),
         phonemes="m u: s a:",
         char_rules=pick(
             hafs_uthmani={"و": R("madd_tabii"), "ى": R("madd_tabii")},
             hafs_indopak={"و": R("madd_tabii"),
                           "ي": R("madd_tabii")},
         ),
         sound_rules={"u:": R("madd_tabii"), "a:": R("madd_tabii")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_madd_tabii(run):
    assert_case(run)
