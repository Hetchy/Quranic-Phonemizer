from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, through


CASES = (
    # وَبِٱلْيَوْمِ ٱلْـَٔاخِرِ
    Case(id="yaa-hamza", site=Site(hafs=("2:8", (7, 8))), read=through(),
         phonemes=("w a b i l j a w m i", "l ʔ a: x i r"),
         char_rules={"ل[1]": R("lam_qamariyyah"), "ل[2]": R("lam_qamariyyah")},
         sound_rules={"l[1]": R("lam_qamariyyah"), "l[2]": R("lam_qamariyyah")}),
    # ٱلْعَلِيمُ ٱلْحَكِيمُ
    Case(id="ayn-ha", site=Site(hafs=("2:32", (11, 12))), read=through(),
         phonemes=("ʔ a l ʕ a l i: m u", "l ħ a k i: m"),
         char_rules={"ل[1]": R("lam_qamariyyah"), "ل[3]": R("lam_qamariyyah")},
         sound_rules={"l[1]": R("lam_qamariyyah"), "l[3]": R("lam_qamariyyah")}),
    # ٱلْكِتَابَ وَٱلْفُرْقَانَ
    Case(id="kaf-fa", site=Site(hafs=("2:53", (4, 5))), read=through(),
         phonemes=("ʔ a l k i t a: b a", "w a l f u rˤ q aˤ: n"),
         char_rules={"ل[1]": R("lam_qamariyyah"), "ل[2]": R("lam_qamariyyah")},
         sound_rules={"l[1]": R("lam_qamariyyah"), "l[2]": R("lam_qamariyyah")}),
    # ٱلْخَوْفِ وَٱلْجُوعِ
    Case(id="kha-jeem", site=Site(hafs=("2:155", (4, 5))), read=through(),
         phonemes=("ʔ a l x aˤ w f i", "w a l ʒ u: ʕ"),
         char_rules={"ل[1]": R("lam_qamariyyah"), "ل[2]": R("lam_qamariyyah")},
         sound_rules={"l[1]": R("lam_qamariyyah"), "l[2]": R("lam_qamariyyah")}),
    # ٱلْبَيِّنَاتِ وَٱلْهُدَىٰ
    Case(id="baa-heh", site=Site(hafs=("2:159", (7, 8))), read=through(),
         phonemes=("ʔ a l b a jj i n a: t i", "w a l h u d a:"),
         char_rules={"ل[1]": R("lam_qamariyyah"), "ل[2]": R("lam_qamariyyah")},
         sound_rules={"l[1]": R("lam_qamariyyah"), "l[2]": R("lam_qamariyyah")}),
    # ٱلْغَمَامِ وَٱلْمَلَائِكَةُ
    Case(id="ghayn-meem", site=Site(hafs=("2:210", (10, 11))), read=through(),
         phonemes=("ʔ a l ɣ aˤ m a: m i", "w a l m a l a: ʔ i k a h"),
         char_rules={"ل[1]": R("lam_qamariyyah"), "ل[2]": R("lam_qamariyyah")},
         sound_rules={"l[1]": R("lam_qamariyyah"), "l[2]": R("lam_qamariyyah")}),
    # ٱلْوَاحِدُ ٱلْقَهَّارُ
    Case(id="waw-qaf", site=Site(hafs=("12:39", (8, 9))), read=through(),
         phonemes=("ʔ a l w a: ħ i d u", "l q aˤ hh a: rˤ"),
         char_rules={"ل[1]": R("lam_qamariyyah"), "ل[2]": R("lam_qamariyyah")},
         sound_rules={"l[1]": R("lam_qamariyyah"), "l[2]": R("lam_qamariyyah")}),
    # ٱلْحَمْدُ لِلَّهِ
    Case(id="joined-forward", site=Site(hafs=("1:2", (1, 2))), read=through(),
         phonemes=("ʔ a l ħ a m d u", "l i ll a: h"),
         char_rules={"ل[1]": R("lam_qamariyyah")},
         sound_rules={"l[1]": R("lam_qamariyyah")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_lam_qamariyyah(run):
    assert_case(run)
