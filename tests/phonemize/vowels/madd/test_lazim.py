from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated, pick


CASES = (
    # ٱلضَّالِّينَ
    Case(id="before-geminate", site=Site.shared("1:7", (9,)), read=isolated(),
         phonemes="ʔ a dˤdˤ aˤ: ll i: n",
         char_rules=pick(
             hafs_uthmani={"ا": R("madd_lazim")},
             hafs_indopak={"ا[2]": R("madd_lazim")},
             warsh_uthmani={"ا[2]": R("madd_lazim")},
         ),
         sound_rules={"aˤ:": R("madd_lazim")}),
    # ٱلْحَآقَّةُ
    Case(id="before-geminate-qaf", site=Site.shared("69:1", (1,)),
         read=isolated(), phonemes="ʔ a l ħ a: qq aˤ h",
         char_rules=pick(
             hafs_uthmani={"ا": R("madd_lazim")},
             hafs_indopak={"ا[2]": R("madd_lazim")},
             warsh_uthmani={"ا[2]": R("madd_lazim")},
         ),
         sound_rules={"a:": R("madd_lazim")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_madd_lazim(run):
    assert_case(run)
