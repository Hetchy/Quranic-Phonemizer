from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated


CASES = (
    # Hafs: خَلَقَ
    # Warsh: خَلَقَ
    Case(id="khaa", site=Site.shared("2:29", (3,)), read=isolated(),
         phonemes="x aˤ l a q Q",
         extra_phonemes=("emphatic_fatha",),
         char_rules={"خ": R("tafkheem"), "@fatha[1]": R("tafkheem")},
         sound_rules={"x": R("tafkheem"), "aˤ": R("tafkheem")}),
    # Hafs: صَبَرُوا۟
    # Warsh: صَبَرُواْ
    Case(id="saad", site=Site.shared("11:11", (3,)), read=isolated(),
         phonemes="sˤ aˤ b a rˤ u:",
         extra_phonemes=("emphatic_fatha",),
         char_rules={"ص": R("tafkheem"), "@fatha[1]": R("tafkheem")},
         sound_rules={"sˤ": R("tafkheem"), "aˤ": R("tafkheem")}),
    # Hafs: ضَرَبَ
    # Warsh: ضَرَبَ
    Case(id="daad", site=Site.shared("30:28", (1,)), read=isolated(),
         phonemes="dˤ aˤ rˤ aˤ b Q",
         extra_phonemes=("emphatic_fatha",),
         char_rules={"ض": R("tafkheem"), "@fatha[1]": R("tafkheem")},
         sound_rules={"dˤ": R("tafkheem"), "aˤ[1]": R("tafkheem")}),
    # Hafs: غُفْرَانَكَ
    # Warsh: غُفْرَانَكَ
    Case(id="ghayn", site=Site.shared("2:285", (24,)), read=isolated(),
         phonemes="ɣ u f rˤ aˤ: n a k",
         char_rules={"غ": R("tafkheem")}, sound_rules={"ɣ": R("tafkheem")}),
    # Hafs: طَبَعَ
    # Warsh: طَبَعَ
    Case(id="taa", site=Site.shared("16:108", (3,)), read=isolated(),
         phonemes="tˤ aˤ b a ʕ",
         extra_phonemes=("emphatic_fatha",),
         char_rules={"ط": R("tafkheem"), "@fatha[1]": R("tafkheem")},
         sound_rules={"tˤ": R("tafkheem"), "aˤ": R("tafkheem")}),
    # Hafs: قَالَ
    # Warsh: قَالَ
    Case(id="qaaf", site=Site.shared("2:33", (1,)), read=isolated(),
         phonemes="q aˤ: l",
         extra_phonemes=("emphatic_fatha",),
         char_rules={"ق": R("tafkheem"), "@fatha[1]": R("tafkheem"), "ا": R("tafkheem")},
         sound_rules={"q": R("tafkheem"), "aˤ:": R("tafkheem")}),
    # Hafs: ظَلَمَ
    # Warsh: ظَّلَمَ
    Case(id="zhaa", site=Site.shared("2:231", (19,)), read=isolated(),
         phonemes="ðˤ aˤ l a m",
         extra_phonemes=("emphatic_fatha",),
         char_rules={"ظ": R("tafkheem"), "@fatha[1]": R("tafkheem")},
         sound_rules={"ðˤ": R("tafkheem"), "aˤ": R("tafkheem")}),
    # Hafs: سَمِعُوا۟
    # Warsh: سَمِعُواْ
    Case(id="seen-light", site=Site.shared("5:83", (2,)), read=isolated(),
         phonemes="s a m i ʕ u:",
         absent_char_rules={"س": R("tafkheem"), "@fatha": R("tafkheem")},
         absent_sound_rules={"s": R("tafkheem"), "a": R("tafkheem")}),
    # Hafs: تَبِعَ
    # Warsh: تَبِعَ
    Case(id="taa-light", site=Site.shared("2:38", (10,)), read=isolated(),
         phonemes="t a b i ʕ",
         absent_char_rules={"ت": R("tafkheem"), "@fatha[1]": R("tafkheem")},
         absent_sound_rules={"t": R("tafkheem"), "a": R("tafkheem")}),
    # Hafs: دَعَا
    # Warsh: دَعَا
    Case(id="daal-light", site=Site.shared("3:38", (2,)), read=isolated(),
         phonemes="d a ʕ a:",
         absent_char_rules={"د": R("tafkheem"), "@fatha[1]": R("tafkheem")},
         absent_sound_rules={"d": R("tafkheem"), "a": R("tafkheem")}),
    # Hafs: ذَهَبَ
    # Warsh: ذَهَبَ
    Case(id="dhal-light", site=Site.shared("2:17", (10,)), read=isolated(),
         phonemes="ð a h a b Q",
         absent_char_rules={"ذ": R("tafkheem"), "@fatha[1]": R("tafkheem")},
         absent_sound_rules={"ð": R("tafkheem"), "a[1]": R("tafkheem")}),
    # Hafs: كَانَ
    # Warsh: كَانَ
    Case(id="kaaf-light", site=Site.shared("2:97", (3,)), read=isolated(),
         phonemes="k a: n",
         absent_char_rules={"ك": R("tafkheem"), "@fatha[1]": R("tafkheem"), "ا": R("tafkheem")},
         absent_sound_rules={"k": R("tafkheem"), "a:": R("tafkheem")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_istilaa(run):
    assert_case(run)
