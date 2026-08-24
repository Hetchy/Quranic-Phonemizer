from __future__ import annotations

import pytest

from tests.support import (
    Case,
    Expect,
    R,
    Site,
    StateCase,
    assert_case,
    case_runs,
    isolated,
    joining,
    pick,
    through,
)


CASES = (
    # Hafs: لَّهُۥ
    # Warsh: لَّهُۥ
    StateCase(id="damma-silah", site=Site.shared("112:4", (3,)), states={
        "joined": Expect(read=joining(), phonemes="l a h u:",
                         char_rules={"@small_waw": R(
                             "madd_silah", "madd_tabii")},
                         sound_rules={"u:": R(
                             "madd_silah", "madd_tabii")}),
        "stopped": Expect(read=isolated(), phonemes="l a h",
                          char_rules=pick(
                              hafs_uthmani={
                                  "@damma": R("waqf_silah_drop"),
                                  "@small_waw": R("waqf_silah_drop"),
                              },
                              hafs_indopak={"@small_waw": R("waqf_silah_drop")},
                              warsh_uthmani={
                                  "@damma": R("waqf_silah_drop"),
                                  "@small_waw": R("waqf_silah_drop"),
                              },
                          ),
                          absent_char_rules={"@small_waw": R(
                              "madd_silah", "madd_tabii")},
                          silent=("@small_waw",)),
    }),
    # Hafs: بِهِۦ
    # Warsh: بِهِۦ
    StateCase(id="kasra-silah", site=Site.shared("2:26", (30,)), states={
        "joined": Expect(read=joining(), phonemes="b i h i:",
                         char_rules={"@small_yaa": R(
                             "madd_silah", "madd_tabii")},
                         sound_rules={"i:": R(
                             "madd_silah", "madd_tabii")}),
        "stopped": Expect(read=isolated(), phonemes="b i h",
                          char_rules=pick(
                              hafs_uthmani={
                                  "@kasra[2]": R("waqf_silah_drop"),
                                  "@small_yaa": R("waqf_silah_drop"),
                              },
                              hafs_indopak={"@small_yaa": R("waqf_silah_drop")},
                              warsh_uthmani={
                                  "@kasra[2]": R("waqf_silah_drop"),
                                  "@small_yaa": R("waqf_silah_drop"),
                              },
                          ),
                          absent_char_rules={"@small_yaa": R(
                              "madd_silah", "madd_tabii")},
                          silent=("@small_yaa",)),
    }),
    # Hafs: فَلَهُۥٓ أَجْرُهُۥ
    # Warsh: فَلَهُۥٓ أَجْرُهُۥ
    Case(id="silah-kubra", site=Site.shared("2:112", (8, 9)), read=through(),
         phonemes=("f a l a h u:", "ʔ a ʒ Q rˤ u h"),
         char_rules={"@small_waw[1]": R(
             "madd_silah", "madd_munfasil")},
         sound_rules={"u:": R("madd_silah", "madd_munfasil")}),
    # Hafs: فِيهِ
    # Warsh: فِيهِۖ
    StateCase(id="after-sakin", site=Site.shared("2:20", (9,)), states={
        "joined": Expect(read=joining(), phonemes="f i: h i",
                         absent_char_rules={"ه": R("madd_tabii")}),
        "stopped": Expect(read=isolated(), phonemes="f i: h",
                          absent_char_rules={"ه": R("madd_tabii")}),
    }),
    # Hafs: أَنَّهُ
    # Warsh: أَنَّهُ
    StateCase(id="before-sakin", site=Site.shared("2:26", (16,)), states={
        "joined": Expect(read=joining(), phonemes="ʔ a ñ a h u",
                         absent_char_rules={"ه": R("madd_tabii")}),
        "stopped": Expect(read=isolated(), phonemes="ʔ a ñ a h",
                          absent_char_rules={"ه": R("madd_tabii")}),
    }),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_haa_silah(run):
    assert_case(run)
