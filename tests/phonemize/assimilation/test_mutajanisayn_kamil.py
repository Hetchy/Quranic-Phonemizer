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
    explicit,
    isolated,
    through,
)


CASES = (
    # قَد تَّبَيَّنَ
    StateCase(id="daal-taa", site=Site(hafs=("2:256", (5, 6))), states={
        "joined": Expect(read=through(), phonemes=("q aˤ", "tt a b a jj a n"),
                         char_rules={"د": R("idgham_mutajanisayn_kamil"),
                                     "ت": R("idgham_mutajanisayn_kamil")},
                         sound_rules={"tt": R("idgham_mutajanisayn_kamil")}),
        "ibtidaa-on-host": Expect(read=explicit(ibtidaa=5, waqf=5),
                          phonemes=("q aˤ d Q", "t a b a jj a n a"),
                          absent_char_rules={"د": R("idgham_mutajanisayn_kamil"),
                                             "ت": R("idgham_mutajanisayn_kamil")}),
    }),
    # وَدَّت طَّائِفَةٌ
    Case(id="taa-taa", site=Site(hafs=("3:69", (1, 2))), read=through(),
         phonemes=("w a dd a", "tˤtˤ aˤ: ʔ i f a h"),
         char_rules={"ت": R("idgham_mutajanisayn_kamil"),
                     "ط": R("idgham_mutajanisayn_kamil")},
         sound_rules={"tˤtˤ": R("idgham_mutajanisayn_kamil")}),
    # إِذ ظَّلَمُوا
    Case(id="dhal-zhaa", site=Site(hafs=("4:64", (11, 12))), read=through(),
         phonemes=("ʔ i", "ðˤðˤ aˤ l a m u:"),
         char_rules={"ذ": R("idgham_mutajanisayn_kamil"),
                     "ظ": R("idgham_mutajanisayn_kamil")},
         sound_rules={"ðˤðˤ": R("idgham_mutajanisayn_kamil")}),
    # يَلْهَث ذَّلِكَ
    Case(id="thaa-dhal", site=Site(hafs=("7:176", (20, 21))), read=through(),
         phonemes=("j a l h a", "ðð a: l i k"),
         char_rules={"ث": R("idgham_mutajanisayn_kamil"),
                     "ذ": R("idgham_mutajanisayn_kamil")},
         sound_rules={"ðð": R("idgham_mutajanisayn_kamil")}),
    # أَثْقَلَت دَّعَوَا
    Case(id="taa-daal", site=Site(hafs=("7:189", (20, 21))), read=through(),
         phonemes=("ʔ a θ q aˤ l a", "dd a ʕ a w a:"),
         char_rules={"ت": R("idgham_mutajanisayn_kamil"),
                     "د": R("idgham_mutajanisayn_kamil")},
         sound_rules={"dd": R("idgham_mutajanisayn_kamil")}),
    # أَرَدتُّمْ
    Case(id="aradttum", site=Site(hafs=("2:233", (45,))), read=isolated(),
         phonemes="ʔ a rˤ aˤ tt u m",
         char_rules={"د": R("idgham_mutajanisayn_kamil"),
                     "ت": R("idgham_mutajanisayn_kamil")},
         sound_rules={"tt": R("idgham_mutajanisayn_kamil")}),
    # رَاوَدتُّهُ
    Case(id="rawadttuhu", site=Site(hafs=("12:32", (7,))), read=isolated(),
         phonemes="rˤ aˤ: w a tt u h",
         char_rules={"د": R("idgham_mutajanisayn_kamil"),
                     "ت": R("idgham_mutajanisayn_kamil")},
         sound_rules={"tt": R("idgham_mutajanisayn_kamil")}),
    # أَيَّدتُّكَ
    Case(id="ayyadttuka", site=Site(hafs=("5:110", (13,))), read=isolated(),
         phonemes="ʔ a jj a tt u k",
         char_rules={"د": R("idgham_mutajanisayn_kamil"),
                     "ت": R("idgham_mutajanisayn_kamil")},
         sound_rules={"tt": R("idgham_mutajanisayn_kamil")}),
    # رَاوَدتُّنَّ
    Case(id="rawadttunna", site=Site(hafs=("12:51", (5,))), read=isolated(),
         phonemes="rˤ aˤ: w a tt u ñ",
         char_rules={"د": R("idgham_mutajanisayn_kamil"),
                     "ت": R("idgham_mutajanisayn_kamil")},
         sound_rules={"tt": R("idgham_mutajanisayn_kamil")}),
    # ٱرْكَب مَّعَنَا
    Case(id="irkab-maana", site=Site(hafs=("11:42", (14, 15))), read=through(),
         phonemes=("ʔ i rˤ k a", "m̃ a ʕ a n a:"),
         char_rules={"ب": R("idgham_mutajanisayn_kamil"),
                     "م": R("idgham_mutajanisayn_kamil")},
         sound_rules={"m̃": R("idgham_mutajanisayn_kamil")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_mutajanisayn_kamil(run):
    assert_case(run)
