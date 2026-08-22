from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, through


CASES = (
    # ٱللَّهِ ٱلرَّحْمَنِ
    Case(id="lam-raa", site=Site(hafs=("1:1", (2, 3))), read=through(),
         phonemes=("ʔ a lˤlˤ aˤ: h i", "rˤrˤ aˤ ħ m a: n"),
         char_rules={"ل[1]": R("lam_shamsiyyah"), "ل[2]": R("lam_shamsiyyah"),
                     "ل[3]": R("lam_shamsiyyah"), "ر": R("lam_shamsiyyah")},
         sound_rules={"lˤlˤ": R("lam_shamsiyyah"), "rˤrˤ": R("lam_shamsiyyah")}),
    # وَٱلنَّصَارَىٰ وَٱلصَّابِئِينَ
    Case(id="noon-sad", site=Site(hafs=("2:62", (6, 7))), read=through(),
         phonemes=("w a ñ a sˤ aˤ: rˤ aˤ:", "w a sˤsˤ aˤ: b i ʔ i: n"),
         char_rules={"ل[1]": R("lam_shamsiyyah"), "ن[1]": R("lam_shamsiyyah"),
                     "ل[2]": R("lam_shamsiyyah"), "ص[2]": R("lam_shamsiyyah")},
         sound_rules={"ñ": R("lam_shamsiyyah"), "sˤsˤ": R("lam_shamsiyyah")}),
    # ٱلزَّادِ ٱلتَّقْوَىٰ
    Case(id="zay-taa", site=Site(hafs=("2:197", (25, 26))), read=through(),
         phonemes=("ʔ a zz a: d i", "tt a q Q w a:"),
         char_rules={"ل[1]": R("lam_shamsiyyah"), "ز": R("lam_shamsiyyah"),
                     "ل[2]": R("lam_shamsiyyah"), "ت": R("lam_shamsiyyah")},
         sound_rules={"zz": R("lam_shamsiyyah"), "tt": R("lam_shamsiyyah")}),
    # ٱلسَّرَّاءِ وَٱلضَّرَّاءِ
    Case(id="seen-dad", site=Site(hafs=("3:134", (4, 5))), read=through(),
         phonemes=("ʔ a ss a rˤrˤ aˤ: ʔ i", "w a dˤdˤ aˤ rˤrˤ aˤ: ʔ"),
         char_rules={"ل[1]": R("lam_shamsiyyah"), "س": R("lam_shamsiyyah"),
                     "ل[2]": R("lam_shamsiyyah"), "ض": R("lam_shamsiyyah")},
         sound_rules={"ss": R("lam_shamsiyyah"), "dˤdˤ": R("lam_shamsiyyah")}),
    # وَٱلشَّجَرُ وَٱلدَّوَابُّ
    Case(id="sheen-dal", site=Site(hafs=("22:18", (17, 18))), read=through(),
         phonemes=("w a ʃʃ a ʒ a rˤ u", "w a dd a w a: bb Q"),
         char_rules={"ل[1]": R("lam_shamsiyyah"), "ش": R("lam_shamsiyyah"),
                     "ل[2]": R("lam_shamsiyyah"), "د": R("lam_shamsiyyah")},
         sound_rules={"ʃʃ": R("lam_shamsiyyah"), "dd": R("lam_shamsiyyah")}),
    # مِنَ ٱلثَّمَرَاتِ
    Case(id="tha", site=Site(hafs=("2:22", (14, 15))), read=through(),
         phonemes=("m i n a", "θθ a m a rˤ aˤ: t"),
         char_rules={"ل": R("lam_shamsiyyah"), "ث": R("lam_shamsiyyah")},
         sound_rules={"θθ": R("lam_shamsiyyah")}),
    # مِنَ ٱلظَّالِمِينَ
    Case(id="zhaa", site=Site(hafs=("2:35", (17, 18))), read=through(),
         phonemes=("m i n a", "ðˤðˤ aˤ: l i m i: n"),
         char_rules={"ل[1]": R("lam_shamsiyyah"), "ظ": R("lam_shamsiyyah")},
         sound_rules={"ðˤðˤ": R("lam_shamsiyyah")}),
    # عَلَيْهِمُ ٱلذِّلَّةُ
    Case(id="thal", site=Site(hafs=("2:61", (38, 39))), read=through(),
         phonemes=("ʕ a l a j h i m u", "ðð i ll a h"),
         char_rules={"ل[2]": R("lam_shamsiyyah"), "ذ": R("lam_shamsiyyah")},
         sound_rules={"ðð": R("lam_shamsiyyah")}),
    # فَوْقَكُمُ ٱلطُّورَ
    Case(id="tah", site=Site(hafs=("2:63", (5, 6))), read=through(),
         phonemes=("f a w q aˤ k u m u", "tˤtˤ u: rˤ"),
         char_rules={"ل": R("lam_shamsiyyah"), "ط": R("lam_shamsiyyah")},
         sound_rules={"tˤtˤ": R("lam_shamsiyyah")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_lam_shamsiyyah(run):
    assert_case(run)
