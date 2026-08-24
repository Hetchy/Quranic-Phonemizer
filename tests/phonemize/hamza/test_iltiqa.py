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
    del indopak_wasl
    rules = {} if source is None or rule is None else {source: R(rule)}

    return pick(
        hafs_uthmani=rules,
        hafs_indopak=rules,
        warsh_uthmani=rules,
    )


CASES = (
    # Hafs: وَلَا ٱلضَّآلِّينَ
    # Warsh: وَلَا اَ۬لضَّآلِّينَۖ
    Case(id="long-a", site=Site.shared("1:7", (8, 9)), read=through(),
         phonemes=("w a l a", "dˤdˤ aˤ: ll i: n"),
         char_rules=_chars("@fatha[2]", "iltiqa_shortening", "ا[2]"),
         sound_rules={"a[2]": R("iltiqa_shortening")}),
    # Hafs: فِى ٱلْأَرْضِ
    Case(id="long-i", site=Site(hafs=("2:11", (6, 7))), read=through(),
         phonemes=("f i", "l ʔ a rˤ dˤ"),
         char_rules=pick(
             hafs_uthmani={"@kasra[1]": R("iltiqa_shortening")},
             hafs_indopak={"@kasra[1]": R("iltiqa_shortening")},
         ),
         sound_rules={"i": R("iltiqa_shortening")}),
    # Warsh: فِے اِ۬لسَّبْتِ
    Case(id="long-i-warsh", site=Site(warsh=("2:65", (6, 7))), read=through(),
         phonemes=("f i", "ss a b Q t"),
         char_rules={"@kasra[1]": R("iltiqa_shortening")},
         sound_rules={"i": R("iltiqa_shortening")}),
    # Hafs: قَالُوا۟ ٱدْعُ
    # Warsh: قَالُواْ اُ۟دْعُ
    Case(id="long-u", site=Site.shared("2:68", (1, 2)), read=through(),
         phonemes=("q aˤ: l u", "d Q ʕ"),
         char_rules=_chars("@damma[1]", "iltiqa_shortening", "ا[3]"),
         sound_rules={"u": R("iltiqa_shortening")}),
    # Hafs: وَعَمِلُوا۟ ٱلصَّـٰلِحَـٰتِ
    # Warsh: وَعَمِلُواْ اُ۬لصَّٰلِحَٰتِ
    StateCase(id="plural-waw", site=Site.shared("2:25", (4, 5)), states={
        "joined": Expect(read=through(), phonemes=("w a ʕ a m i l u", "sˤsˤ aˤ: l i ħ a: t"),
                         char_rules=_chars("@damma", "iltiqa_shortening", "ا[2]"),
                         sound_rules={"u": R("iltiqa_shortening")}),
        "stopped": Expect(read=explicit(ibtidaa=4, waqf=4),
                          phonemes=("w a ʕ a m i l u:", "ʔ a sˤsˤ aˤ: l i ħ a: t i"),
                          absent_char_rules={"و[2]": R("iltiqa_shortening")}),
    }),
    # Hafs: وَمِنَ ٱلنَّاسِ
    # Warsh: وَمِنَ اَ۬لنَّاسِ
    Case(id="lexical-fatha-host", site=Site.shared("2:8", (1, 2)), read=through(),
         phonemes=("w a m i n a", "ñ a: s"),
         char_rules=pick(
             hafs_uthmani={"ٱ": R("hamza_wasl_silent")},
             hafs_indopak={"ا[1]": R("hamza_wasl_silent")},
             warsh_uthmani={"ا[1]": R("hamza_wasl_silent")},
         )),
    # Hafs: قُمِ ٱلَّيْلَ
    # Warsh: قُمِ اِ۬ليْلَ
    Case(id="meem-repair", site=Site.shared("73:2", (1, 2)), read=through(),
         phonemes=("q u m i", "ll a j l"),
         char_rules={}),
    # Hafs: أَنِ ٱقْتُلُوٓا۟
    Case(id="noon-repair", site=Site(hafs=("4:66", (5, 6))), read=through(),
         phonemes=("ʔ a n i", "q Q t u l u:"),
         char_rules={}),
    # Hafs: قُلِ ٱنظُرُوا۟
    Case(id="lam-repair", site=Site(hafs=("10:101", (1, 2))), read=through(),
         phonemes=("q u l i", "ŋ ðˤ u rˤ u:"),
         char_rules={}),
    # Hafs: قَالَتِ ٱمْرَأَتُ
    # Warsh: قَالَتِ اِ۪مْرَأَتُ
    Case(id="feminine-taa-repair", site=Site.shared("3:35", (2, 3)), read=through(),
         phonemes=("q aˤ: l a t i", "m rˤ aˤ ʔ a t"),
         char_rules={}),
    # Hafs: خَيْرٌ ۚ ٱهْبِطُوا۟
    # Warsh: خَيْرٌۖ اِ۪هْبِطُواْ
    Case(id="dammatan", site=Site.shared("2:61", (30, 31)), read=through(),
         phonemes=("x aˤ j rˤ u n i", "h b i tˤ u:"),
         sound_rules={"i[1]": R("iltiqa_haraka")}),
    # Hafs: يَوْمَئِذٍ ٱلْحَقُّ ۚ
    # Warsh: يَوْمَئِذٍ اِ۬لْحَقُّۖ
    Case(id="kasratan", site=Site.shared("7:8", (2, 3)), read=through(),
         phonemes=("j a w m a ʔ i ð i n i", "l ħ a qq Q"),
         sound_rules={"i[3]": R("iltiqa_haraka")}),
    # Hafs: أَنفُسَكُمُ ۖ ٱلْيَوْمَ
    # Warsh: أَنفُسَكُمُۖ اُ۬لْيَوْمَ
    Case(id="plural-meem", site=Site.shared("6:93", (34, 35)), read=through(),
         phonemes=("ʔ a ŋ f u s a k u m u", "l j a w m"),
         char_rules=_chars(None, None, "ا[2]")),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_iltiqa(run):
    assert_case(run)
