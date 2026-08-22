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
    pick,
    through,
)


def _chars(source: str | None, rule: str | None, indopak_wasl: str = "ا"):
    def per_script(wasl: str):
        rules = {wasl: R("wasl_elision")}
        if source is not None and rule is not None:
            rules[source] = R(rule)
        return rules

    return pick(
        hafs_uthmani=per_script("ٱ"),
        hafs_indopak=per_script(indopak_wasl),
    )


CASES = (
    # وَلَا ٱلضَّالِّينَ
    Case(id="long-a", site=Site(hafs=("1:7", (8, 9))), read=through(),
         phonemes=("w a l a", "dˤdˤ aˤ: ll i: n"),
         char_rules=_chars("ا[1]", "iltiqa_shortening", "ا[2]"),
         sound_rules={"a[2]": R("iltiqa_shortening")}),
    # فِي ٱلْأَرْضِ
    Case(id="long-i", site=Site(hafs=("2:11", (6, 7))), read=through(),
         phonemes=("f i", "l ʔ a rˤ dˤ"),
         char_rules=pick(
             hafs_uthmani={"ٱ": R("wasl_elision"),
                           "ى": R("iltiqa_shortening")},
             hafs_indopak={"ا[1]": R("wasl_elision"),
                           "ي": R("iltiqa_shortening")},
         ),
         sound_rules={"i": R("iltiqa_shortening")}),
    # قَالُوا ٱدْعُ
    Case(id="long-u", site=Site(hafs=("2:68", (1, 2))), read=through(),
         phonemes=("q aˤ: l u", "d Q ʕ"),
         char_rules=_chars("و", "iltiqa_shortening", "ا[3]"),
         sound_rules={"u": R("iltiqa_shortening")}),
    # وَعَمِلُوا ٱلصَّالِحَاتِ
    StateCase(id="plural-waw", site=Site(hafs=("2:25", (4, 5))), states={
        "joined": Expect(read=through(), phonemes=("w a ʕ a m i l u", "sˤsˤ aˤ: l i ħ a: t"),
                         char_rules=_chars("و[2]", "iltiqa_shortening", "ا[2]"),
                         sound_rules={"u": R("iltiqa_shortening")}),
        "stopped": Expect(read=explicit(ibtidaa=4, waqf=4),
                          phonemes=("w a ʕ a m i l u:", "ʔ a sˤsˤ aˤ: l i ħ a: t i"),
                          absent_char_rules={"و[2]": R("iltiqa_shortening")}),
    }),
    # قُمِ ٱللَّيْلَ
    Case(id="meem-repair", site=Site(hafs=("73:2", (1, 2))), read=through(),
         phonemes=("q u m i", "ll a j l"),
         char_rules=_chars("@kasra", "iltiqa_kasra"),
         sound_rules={"i": R("iltiqa_kasra")}),
    # أَنِ ٱقْتُلُوا
    Case(id="noon-repair", site=Site(hafs=("4:66", (5, 6))), read=through(),
         phonemes=("ʔ a n i", "q Q t u l u:"),
         char_rules=_chars("@kasra", "iltiqa_kasra", "ا[2]"),
         sound_rules={"i[2]": R("iltiqa_kasra")}),
    # قُلِ ٱنظُرُوا
    Case(id="lam-repair", site=Site(hafs=("10:101", (1, 2))), read=through(),
         phonemes=("q u l i", "ŋ ðˤ u rˤ u:"),
         char_rules=_chars("@kasra", "iltiqa_kasra", "ا[1]"),
         sound_rules={"i": R("iltiqa_kasra")}),
    # قَالَتِ ٱمْرَأَتُ
    Case(id="feminine-taa-repair", site=Site(hafs=("3:35", (2, 3))), read=through(),
         phonemes=("q aˤ: l a t i", "m rˤ aˤ ʔ a t"),
         char_rules=_chars("@kasra", "iltiqa_kasra", "ا[2]"),
         sound_rules={"i": R("iltiqa_kasra")}),
    # خَيْرٌ ٱهْبِطُوا
    Case(id="dammatan", site=Site(hafs=("2:61", (30, 31))), read=through(),
         phonemes=("x aˤ j rˤ u n i", "h b i tˤ u:"),
         char_rules=_chars("@dammatan", "iltiqa_kasra", "ا[1]"),
         sound_rules={"i[1]": R("iltiqa_kasra")}),
    # يَوْمَئِذٍ ٱلْحَقُّ
    Case(id="kasratan", site=Site(hafs=("7:8", (2, 3))), read=through(),
         phonemes=("j a w m a ʔ i ð i n i", "l ħ a qq Q"),
         char_rules=_chars("@kasratan", "iltiqa_kasra"),
         sound_rules={"i[3]": R("iltiqa_kasra")}),
    # أَنفُسَكُمُ ٱلْيَوْمَ
    Case(id="plural-meem", site=Site(hafs=("6:93", (34, 35))), read=through(),
         phonemes=("ʔ a ŋ f u s a k u m u", "l j a w m"),
         char_rules=_chars(None, None, "ا[2]")),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_iltiqa(run):
    assert_case(run)
