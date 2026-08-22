from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated, pick, through


CASES = (
    # رَبِّ
    Case(id="moving-fatha", site=Site(hafs=("1:2", (3,))), read=isolated(),
         phonemes="rˤ aˤ bb Q", extra_phonemes=("emphatic_fatha",),
         char_rules={"ر": R("tafkheem"), "@fatha": R("tafkheem")},
         sound_rules={"rˤ": R("tafkheem"), "aˤ": R("tafkheem")}),
    # رُزِقْنَا
    Case(id="moving-damma", site=Site(hafs=("2:25", (22,))), read=isolated(),
         phonemes="rˤ u z i q Q n a:", char_rules={"ر": R("tafkheem")},
         sound_rules={"rˤ": R("tafkheem")}),
    # رِجَالٌ
    Case(id="moving-kasra", site=Site(hafs=("7:46", (5,))), read=isolated(),
         phonemes="r i ʒ a: l", char_rules={"ر": R("tarqeeq")},
         sound_rules={"r": R("tarqeeq")}),
    # مَرْيَمَ
    Case(id="sakin-after-fatha", site=Site(hafs=("2:87", (12,))), read=isolated(),
         phonemes="m a rˤ j a m", char_rules={"ر": R("tafkheem")},
         sound_rules={"rˤ": R("tafkheem")}),
    # ٱلْأَرْضِ
    Case(id="sakin-before-istilaa", site=Site(hafs=("2:11", (7,))), read=isolated(),
         phonemes="ʔ a l ʔ a rˤ dˤ", char_rules={"ر": R("tafkheem")},
         sound_rules={"rˤ": R("tafkheem")}),
    # قُرْآنٍ
    Case(id="sakin-after-damma", site=Site(hafs=("10:61", (9,))), read=isolated(),
         phonemes="q u rˤ ʔ a: n", char_rules={"ر": R("tafkheem")},
         sound_rules={"rˤ": R("tafkheem")}),
    # فِرْعَوْنَ
    Case(id="sakin-after-kasra", site=Site(hafs=("2:49", (5,))), read=isolated(),
         phonemes="f i r ʕ a w n", char_rules={"ر": R("tarqeeq")},
         sound_rules={"r": R("tarqeeq")}),
    # قِرْطَاسٍ
    Case(id="sakin-before-taa", site=Site(hafs=("6:7", (6,))), read=isolated(),
         phonemes="q i rˤ tˤ aˤ: s", char_rules={"ر": R("tafkheem")},
         sound_rules={"rˤ": R("tafkheem")}),
    # مِرْصَادًا
    Case(id="sakin-before-saad", site=Site(hafs=("78:21", (4,))), read=isolated(),
         phonemes="m i rˤ sˤ aˤ: d a:", char_rules={"ر": R("tafkheem")},
         sound_rules={"rˤ": R("tafkheem")}),
    # فِرْقَةٍ
    Case(id="sakin-before-qaaf", site=Site(hafs=("9:122", (10,))), read=isolated(),
         phonemes="f i rˤ q aˤ h", char_rules={"ر": R("tafkheem")},
         sound_rules={"rˤ": R("tafkheem")}),
    # ٱرْجِعِي
    Case(id="prosthetic-kasra", site=Site(hafs=("89:28", (1,))), read=isolated(),
         phonemes="ʔ i rˤ ʒ i ʕ i:", char_rules={"ر": R("tafkheem")},
         sound_rules={"rˤ": R("tafkheem")}),
    # ٱرْتَابُوا
    Case(id="started-irtabu", site=Site(hafs=("24:50", (5,))), read=isolated(),
         phonemes="ʔ i rˤ t a: b u:", char_rules={"ر": R("tafkheem")},
         sound_rules={"rˤ": R("tafkheem")}),
    # أَمِ ٱرْتَابُوا
    Case(id="joined-incidental-kasra", site=Site(hafs=("24:50", (4, 5))), read=through(),
         phonemes=("ʔ a m i", "rˤ t a: b u:"), char_rules={"ر": R("tafkheem")},
         sound_rules={"rˤ": R("tafkheem")}),
    # خَيْرٌ
    Case(id="stopped-after-sakin-yaa", site=Site(hafs=("2:54", (17,))), read=isolated(),
         phonemes="x aˤ j r", char_rules={"ر": R("tarqeeq")},
         sound_rules={"r": R("tarqeeq")}),
    # حِجْرٌ
    Case(id="stopped-after-separated-kasra", site=Site(hafs=("6:138", (5,))), read=isolated(),
         phonemes="ħ i ʒ Q r", char_rules={"ر": R("tarqeeq")},
         sound_rules={"r": R("tarqeeq")}),
    # ٱلنَّهَارِ
    Case(id="stopped-after-alif", site=Site(hafs=("3:27", (4,))), read=isolated(),
         phonemes="ʔ a ñ a h a: rˤ", char_rules={"ر": R("tafkheem")},
         sound_rules={"rˤ": R("tafkheem")}),
    # قَدِيرٌ
    Case(id="stopped-after-long-yaa", site=Site(hafs=("2:20", (25,))), read=isolated(),
         phonemes="q aˤ d i: r", char_rules={"ر": R("tarqeeq")},
         sound_rules={"r": R("tarqeeq")}),
    # ٱلرَّحْمَانِ
    Case(id="geminate-fatha", site=Site(hafs=("1:1", (3,))), read=isolated(),
         phonemes="ʔ a rˤrˤ aˤ ħ m a: n", extra_phonemes=("emphatic_fatha",),
         char_rules=pick(
             hafs={"ر": R("tafkheem"), "@fatha[1]": R("tafkheem")},
             hafs_indopak={"ر": R("tafkheem"), "@fatha": R("tafkheem")},
         ),
         sound_rules={"rˤrˤ": R("tafkheem"), "aˤ": R("tafkheem")}),
    # مُسْتَمِرٌّ
    Case(id="stopped-geminate-after-kasra", site=Site(hafs=("54:2", (7,))), read=isolated(),
         phonemes="m u s t a m i rr", char_rules={"ر": R("tarqeeq")},
         sound_rules={"rr": R("tarqeeq")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_hafs_raa(run):
    assert_case(run)
