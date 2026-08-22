from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated, reading


CASES = (
    # رَزَقْنَاهُمْ
    Case(id="sughra-qaf", site=Site(hafs=("2:3", (7,))), read=isolated(),
         phonemes="rˤ aˤ z a q Q n a: h u m",
         char_rules={"ق": R("qalqala_sughra")},
         sound_rules={"Q": R("qalqala_sughra")}),
    # أَطْعَمَهُم
    Case(id="sughra-taa", site=Site(hafs=("106:4", (2,))), read=isolated(),
         phonemes="ʔ a tˤ Q ʕ a m a h u m",
         char_rules={"ط": R("qalqala_sughra")},
         sound_rules={"Q": R("qalqala_sughra")}),
    # يُبْصِرُونَ
    Case(id="sughra-baa", site=Site(hafs=("2:17", (17,))), read=isolated(),
         phonemes="j u b Q sˤ i rˤ u: n",
         char_rules={"ب": R("qalqala_sughra")},
         sound_rules={"Q": R("qalqala_sughra")}),
    # يَجْعَلُونَ
    Case(id="sughra-jeem", site=Site(hafs=("2:19", (9,))), read=isolated(),
         phonemes="j a ʒ Q ʕ a l u: n",
         char_rules={"ج": R("qalqala_sughra")},
         sound_rules={"Q": R("qalqala_sughra")}),
    # تَدْعُونَ
    Case(id="sughra-dal", site=Site(hafs=("46:4", (4,))), read=isolated(),
         phonemes="t a d Q ʕ u: n",
         char_rules={"د": R("qalqala_sughra")},
         sound_rules={"Q": R("qalqala_sughra")}),
    # ٱلصَّوَاعِقِ
    Case(id="kubra-qaf", site=Site(hafs=("2:19", (14,))), read=isolated(),
         phonemes="ʔ a sˤsˤ aˤ w a: ʕ i q Q",
         char_rules={"ق": R("qalqala_kubra")},
         sound_rules={"Q": R("qalqala_kubra")}),
    # مُحِيطٌ
    Case(id="kubra-taa-tanwin", site=Site(hafs=("2:19", (18,))), read=isolated(),
         phonemes="m u ħ i: tˤ Q",
         char_rules={"ط": R("qalqala_kubra")},
         sound_rules={"Q": R("qalqala_kubra")}),
    # ٱلْمَغْضُوبِ
    Case(id="kubra-baa", site=Site(hafs=("1:7", (6,))), read=isolated(),
         phonemes="ʔ a l m a ɣ dˤ u: b Q",
         char_rules={"ب": R("qalqala_kubra")},
         sound_rules={"Q": R("qalqala_kubra")}),
    # فَأَخْرَجَ
    Case(id="kubra-jeem", site=Site(hafs=("2:22", (12,))), read=isolated(),
         phonemes="f a ʔ a x rˤ aˤ ʒ Q",
         char_rules={"ج": R("qalqala_kubra")},
         sound_rules={"Q": R("qalqala_kubra")}),
    # وَرَعْدٌ
    Case(id="kubra-dal-tanwin", site=Site(hafs=("2:19", (7,))), read=isolated(),
         phonemes="w a rˤ aˤ ʕ d Q",
         char_rules={"د": R("qalqala_kubra")},
         sound_rules={"Q": R("qalqala_kubra")}),
    # ٱلْحَقُّ
    Case(id="akbar-qaf", site=Site(hafs=("2:26", (17,))), read=isolated(),
         phonemes="ʔ a l ħ a qq Q",
         char_rules={"ق": R("qalqala_akbar")},
         sound_rules={"Q": R("qalqala_akbar")}),
    # رَبِّ
    Case(id="akbar-baa", site=Site(hafs=("1:2", (3,))), read=isolated(),
         phonemes="rˤ aˤ bb Q",
         char_rules={"ب": R("qalqala_akbar")},
         sound_rules={"Q": R("qalqala_akbar")}),
    # بِمَا
    Case(id="voweled-negative", site=Site(hafs=("2:10", (10,))), read=isolated(),
         phonemes="b i m a:", absent_char_rules={"ب": R(
             "qalqala_sughra", "qalqala_kubra", "qalqala_akbar")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_qalqala(run):
    assert_case(run)


def test_qalqala_degree_extra_changes_only_the_kubra_release():
    # ٱقْرَأْ ... خَلَقَ
    site = Site(hafs=("96:1", (1, 5)))
    off = reading(site, extra_phonemes=(), ibtidaa=1, waqf=5)
    on = reading(site, extra_phonemes=("qalqala_degree",), ibtidaa=1, waqf=5)
    assert off.sounds(1) == on.sounds(1) == ("ʔ", "i", "q", "Q", "rˤ", "a", "ʔ")
    assert off.sounds(5) == ("x", "a", "l", "a", "q", "Q")
    assert on.sounds(5) == ("x", "a", "l", "a", "q", "QQ")
