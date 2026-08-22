from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated


CASES = (
    # خَلَقَ
    Case(id="khaa", site=Site(hafs=("2:29", (3,))), read=isolated(),
         phonemes="x aˤ l a q Q",
         extra_phonemes=("emphatic_fatha",),
         char_rules={"خ": R("tafkheem"), "@fatha[1]": R("tafkheem")},
         sound_rules={"x": R("tafkheem"), "aˤ": R("tafkheem")}),
    # صَبَرُوا
    Case(id="saad", site=Site(hafs=("11:11", (3,))), read=isolated(),
         phonemes="sˤ aˤ b a rˤ u:",
         extra_phonemes=("emphatic_fatha",),
         char_rules={"ص": R("tafkheem"), "@fatha[1]": R("tafkheem")},
         sound_rules={"sˤ": R("tafkheem"), "aˤ": R("tafkheem")}),
    # ضَرَبَ
    Case(id="daad", site=Site(hafs=("30:28", (1,))), read=isolated(),
         phonemes="dˤ aˤ rˤ aˤ b Q",
         extra_phonemes=("emphatic_fatha",),
         char_rules={"ض": R("tafkheem"), "@fatha[1]": R("tafkheem")},
         sound_rules={"dˤ": R("tafkheem"), "aˤ[1]": R("tafkheem")}),
    # غُفْرَانَكَ
    Case(id="ghayn", site=Site(hafs=("2:285", (24,))), read=isolated(),
         phonemes="ɣ u f rˤ aˤ: n a k",
         char_rules={"غ": R("tafkheem")}, sound_rules={"ɣ": R("tafkheem")}),
    # طَبَعَ
    Case(id="taa", site=Site(hafs=("16:108", (3,))), read=isolated(),
         phonemes="tˤ aˤ b a ʕ",
         extra_phonemes=("emphatic_fatha",),
         char_rules={"ط": R("tafkheem"), "@fatha[1]": R("tafkheem")},
         sound_rules={"tˤ": R("tafkheem"), "aˤ": R("tafkheem")}),
    # قَالَ
    Case(id="qaaf", site=Site(hafs=("2:33", (1,))), read=isolated(),
         phonemes="q aˤ: l",
         extra_phonemes=("emphatic_fatha",),
         char_rules={"ق": R("tafkheem"), "@fatha[1]": R("tafkheem"), "ا": R("tafkheem")},
         sound_rules={"q": R("tafkheem"), "aˤ:": R("tafkheem")}),
    # ظَلَمَ
    Case(id="zhaa", site=Site(hafs=("2:231", (19,))), read=isolated(),
         phonemes="ðˤ aˤ l a m",
         extra_phonemes=("emphatic_fatha",),
         char_rules={"ظ": R("tafkheem"), "@fatha[1]": R("tafkheem")},
         sound_rules={"ðˤ": R("tafkheem"), "aˤ": R("tafkheem")}),
    # سَمِعُوا
    Case(id="seen-light", site=Site(hafs=("5:83", (2,))), read=isolated(),
         phonemes="s a m i ʕ u:",
         absent_char_rules={"س": R("tafkheem"), "@fatha": R("tafkheem")},
         absent_sound_rules={"s": R("tafkheem"), "a": R("tafkheem")}),
    # تَبِعَ
    Case(id="taa-light", site=Site(hafs=("2:38", (10,))), read=isolated(),
         phonemes="t a b i ʕ",
         absent_char_rules={"ت": R("tafkheem"), "@fatha[1]": R("tafkheem")},
         absent_sound_rules={"t": R("tafkheem"), "a": R("tafkheem")}),
    # دَعَا
    Case(id="daal-light", site=Site(hafs=("3:38", (2,))), read=isolated(),
         phonemes="d a ʕ a:",
         absent_char_rules={"د": R("tafkheem"), "@fatha[1]": R("tafkheem")},
         absent_sound_rules={"d": R("tafkheem"), "a": R("tafkheem")}),
    # ذَهَبَ
    Case(id="dhal-light", site=Site(hafs=("2:17", (10,))), read=isolated(),
         phonemes="ð a h a b Q",
         absent_char_rules={"ذ": R("tafkheem"), "@fatha[1]": R("tafkheem")},
         absent_sound_rules={"ð": R("tafkheem"), "a[1]": R("tafkheem")}),
    # كَانَ
    Case(id="kaaf-light", site=Site(hafs=("2:97", (3,))), read=isolated(),
         phonemes="k a: n",
         absent_char_rules={"ك": R("tafkheem"), "@fatha[1]": R("tafkheem"), "ا": R("tafkheem")},
         absent_sound_rules={"k": R("tafkheem"), "a:": R("tafkheem")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_istilaa(run):
    assert_case(run)
