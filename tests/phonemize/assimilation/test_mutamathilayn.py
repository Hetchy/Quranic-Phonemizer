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
    # Hafs: رَبِحَت تِّجَـٰرَتُهُمْ
    # Warsh: رَبِحَت تِّجَٰرَتُهُمْ
    Case(id="taa", site=Site.shared("2:16", (7, 8)), read=through(),
         phonemes=("rˤ aˤ b i ħ a", "tt i ʒ a: rˤ aˤ t u h u m"),
         char_rules={"ت[1]": R("idgham_mutamathilayn"),
                     "ت[2]": R("idgham_mutamathilayn")},
         sound_rules={"tt": R("idgham_mutamathilayn")}),
    # Hafs: أَقُل لَّكُمْ
    StateCase(id="lam", site=Site(hafs=("2:33", (10, 11))), states={
        "joined": Expect(read=through(), phonemes=("ʔ a q u", "ll a k u m"),
                         char_rules={"ل[1]": R("idgham_mutamathilayn"),
                                     "ل[2]": R("idgham_mutamathilayn")},
                         sound_rules={"ll": R("idgham_mutamathilayn")}),
        "ibtidaa-on-host": Expect(read=explicit(ibtidaa=10, waqf=10),
                          phonemes=("ʔ a q u l", "l a k u m"),
                          absent_char_rules={"ل[1]": R("idgham_mutamathilayn"),
                                             "ل[2]": R("idgham_mutamathilayn")}),
    }),
    # Warsh: قُل لَّا
    Case(id="lam-warsh", site=Site(warsh=("5:100", (1, 2))), read=through(),
         phonemes=("q u", "ll a:"),
         char_rules={"ل[1]": R("idgham_mutamathilayn"),
                     "ل[2]": R("idgham_mutamathilayn")},
         sound_rules={"ll": R("idgham_mutamathilayn")}),
    # Hafs: ٱضْرِب بِّعَصَاكَ
    # Warsh: اَ۪ضْرِب بِّعَصَاكَ
    Case(id="baa", site=Site.shared("2:60", (6, 7)), read=through(),
         phonemes=("ʔ i dˤ r i", "bb i ʕ a sˤ aˤ: k"),
         char_rules={"ب[1]": R("idgham_mutamathilayn"),
                     "ب[2]": R("idgham_mutamathilayn")},
         sound_rules={"bb": R("idgham_mutamathilayn")}),
    # Hafs: عَصَوا۟ وَّكَانُوا۟
    # Warsh: عَصَواْ وَّكَانُواْ
    Case(id="waw", site=Site.shared("2:61", (57, 58)), read=through(),
         phonemes=("ʕ a sˤ aˤ", "ww a k a: n u:"),
         char_rules={"و[1]": R("idgham_mutamathilayn"),
                     "و[2]": R("idgham_mutamathilayn")},
         sound_rules={"ww": R("idgham_mutamathilayn")}),
    # Hafs: وَٱذْكُر رَّبَّكَ
    # Warsh: وَاذْكُر رَّبَّكَ
    Case(id="raa", site=Site.shared("3:41", (15, 16)), read=through(),
         phonemes=("w a ð k u", "rˤrˤ aˤ bb a k"),
         char_rules={"ر[1]": R("idgham_mutamathilayn"),
                     "ر[2]": R("idgham_mutamathilayn")},
         sound_rules={"rˤrˤ": R("idgham_mutamathilayn")}),
    # Hafs: وَقَد دَّخَلُوا۟
    # Warsh: وَقَد دَّخَلُواْ
    StateCase(id="daal", site=Site.shared("5:61", (5, 6)), states={
        "joined": Expect(read=through(), phonemes=("w a q aˤ", "dd a x aˤ l u:"),
                         char_rules={"د[1]": R("idgham_mutamathilayn"),
                                     "د[2]": R("idgham_mutamathilayn")},
                         sound_rules={"dd": R("idgham_mutamathilayn")},
                         absent_char_rules={"د[1]": R("qalqala_sughra", "qalqala_kubra", "qalqala_akbar")}),
        "ibtidaa-on-host": Expect(read=explicit(ibtidaa=5, waqf=5),
                          phonemes=("w a q aˤ d Q", "d a x aˤ l u:"),
                          char_rules={"د[1]": R("qalqala_kubra")},
                          absent_char_rules={"د[1]": R("idgham_mutamathilayn"),
                                             "د[2]": R("idgham_mutamathilayn")}),
    }),
    # Hafs: إِذ ذَّهَبَ
    # Warsh: إِذ ذَّهَبَ
    Case(id="dhal", site=Site.shared("21:87", (3, 4)), read=through(),
         phonemes=("ʔ i", "ðð a h a b Q"),
         char_rules={"ذ[1]": R("idgham_mutamathilayn"),
                     "ذ[2]": R("idgham_mutamathilayn")},
         sound_rules={"ðð": R("idgham_mutamathilayn")}),
    # Hafs: تَسْتَطِع عَّلَيْهِ
    # Warsh: تَسْتَطِع عَّلَيْهِ
    Case(id="ayn", site=Site.shared("18:78", (10, 11)), read=through(),
         phonemes=("t a s t a tˤ i", "ʕʕ a l a j h"),
         char_rules={"ع[1]": R("idgham_mutamathilayn"),
                     "ع[2]": R("idgham_mutamathilayn")},
         sound_rules={"ʕʕ": R("idgham_mutamathilayn")}),
    # Hafs: يُسْرِف فِّى
    # Warsh: يُسْرِف فِّے
    Case(id="faa", site=Site.shared("17:33", (17, 18)), read=through(),
         phonemes=("j u s r i", "ff i:"),
         char_rules={"ف[1]": R("idgham_mutamathilayn"),
                     "ف[2]": R("idgham_mutamathilayn")},
         sound_rules={"ff": R("idgham_mutamathilayn")}),
    # Hafs: يُدْرِككُّمُ
    # Warsh: يُدْرِككُّمُ
    Case(id="inside-word", site=Site.shared("4:78", (3,)), read=isolated(),
         phonemes="j u d Q r i kk u m",
         char_rules={"ك[1]": R("idgham_mutamathilayn"),
                     "ك[2]": R("idgham_mutamathilayn")},
         sound_rules={"kk": R("idgham_mutamathilayn")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_mutamathilayn(run):
    assert_case(run)
