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


def _wasl_chars(rule: str, hafs_indopak: str = "ا", warsh: str = "ا"):
    return pick(
        hafs_uthmani={"ٱ": R(rule)},
        hafs_indopak={hafs_indopak: R(rule)},
        warsh_uthmani={warsh: R(rule)},
    )


CASES = (
    # Hafs: وَلَا ٱلضَّآلِّينَ
    # Warsh: وَلَا اَ۬لضَّآلِّينَۖ
    Case(id="long-a", site=Site.shared("1:7", (8, 9)), read=through(),
         phonemes=("w a l a", "dˤdˤ aˤ: ll i: n"),
         char_rules={"ا[1]": R("iltiqa_shortening")},
         absent_char_rules={"@fatha[2]": R("iltiqa_shortening")},
         sound_rules={"a[2]": R("iltiqa_shortening")}),
    # Hafs: فِى ٱلْأَرْضِ
    Case(id="long-i", site=Site(hafs=("2:11", (6, 7))), read=through(),
         phonemes=("f i", "l ʔ a rˤ dˤ"),
         char_rules=pick(
             hafs_uthmani={"ى": R("iltiqa_shortening")},
             hafs_indopak={"ي": R("iltiqa_shortening")},
         ),
         absent_char_rules={"@kasra[1]": R("iltiqa_shortening")},
         sound_rules={"i": R("iltiqa_shortening")}),
    # Warsh: فِے اِ۬لسَّبْتِ
    Case(id="long-i-warsh", site=Site(warsh=("2:65", (6, 7))), read=through(),
         phonemes=("f i", "ss a b Q t"),
         char_rules={"ے": R("iltiqa_shortening")},
         absent_char_rules={"@kasra[1]": R("iltiqa_shortening")},
         sound_rules={"i": R("iltiqa_shortening")}),
    # Warsh: فِے اِ۬لَارْضِۖ
    Case(id="long-i-before-article-naql",
         site=Site(warsh=("42:27", (7, 8))), read=through(),
         phonemes=("f i", "l a rˤ dˤ"),
         char_rules={"ے": R("iltiqa_shortening")},
         absent_char_rules={"@kasra[1]": R("iltiqa_shortening")},
         sound_rules={"i": R("iltiqa_shortening")}),
    # Hafs: قَالُوا۟ ٱدْعُ
    # Warsh: قَالُواْ اُ۟دْعُ
    Case(id="long-u", site=Site.shared("2:68", (1, 2)), read=through(),
         phonemes=("q aˤ: l u", "d Q ʕ"),
         char_rules={"و": R("iltiqa_shortening")},
         absent_char_rules={"@damma[1]": R("iltiqa_shortening")},
         sound_rules={"u": R("iltiqa_shortening")}),
    # Hafs: وَعَمِلُوا۟ ٱلصَّـٰلِحَـٰتِ
    # Warsh: وَعَمِلُواْ اُ۬لصَّٰلِحَٰتِ
    StateCase(id="plural-waw", site=Site.shared("2:25", (4, 5)), states={
        "joined": Expect(read=through(), phonemes=("w a ʕ a m i l u", "sˤsˤ aˤ: l i ħ a: t"),
                         char_rules={"و[2]": R("iltiqa_shortening")},
                         absent_char_rules={"@damma": R("iltiqa_shortening")},
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
    Case(id="lexical-meem-connected-i", site=Site.shared("73:2", (1, 2)), read=through(),
         phonemes=("q u m i", "ll a j l"),
         char_rules={}),
    # Hafs: أَنِ ٱقْتُلُوٓا۟
    Case(id="lexical-noon-connected-i", site=Site(hafs=("4:66", (5, 6))), read=through(),
         phonemes=("ʔ a n i", "q Q t u l u:"),
         char_rules={}),
    # Hafs: قُلِ ٱنظُرُوا۟
    Case(id="lexical-lam-connected-i", site=Site(hafs=("10:101", (1, 2))), read=through(),
         phonemes=("q u l i", "ŋ ðˤ u rˤ u:"),
         char_rules={}),
    # Hafs: قَالَتِ ٱمْرَأَتُ
    # Warsh: قَالَتِ اِ۪مْرَأَتُ
    Case(id="feminine-taa-connected-i", site=Site.shared("3:35", (2, 3)), read=through(),
         phonemes=("q aˤ: l a t i", "m rˤ aˤ ʔ a t"),
         char_rules={}),
    # Hafs: خَيْرٌ ۚ ٱهْبِطُوا۟
    # Warsh: خَيْرٌۖ اِ۪هْبِطُواْ
    Case(id="dammatan", site=Site.shared("2:61", (30, 31)), read=through(),
         phonemes=pick(
             hafs=("x aˤ j rˤ u n i", "h b i tˤ u:"),
             warsh=("x aˤ j r u n i", "h b i tˤ u:"),
         ),
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
         char_rules={},
         absent_sound_rules={"u[2]": R("iltiqa_haraka")}),
)


WARSH_U_CONTRASTS = (
    # Hafs: قُلِ ٱدْعُوا۟
    # Warsh: قُلُ اُ۟دْعُواْ
    StateCase(id="lexical-lam-connected-u", site=Site.shared("7:195", (20, 21)), states={
        "joined": Expect(
            read=through(),
            phonemes=pick(
                hafs=("q u l i", "d Q ʕ u:"),
                warsh=("q u l u", "d Q ʕ u:"),
            ),
            char_rules=_wasl_chars("hamza_wasl_silent", "ا[1]", "ا[1]"),
            silent=pick(
                hafs_uthmani=("ٱ",),
                hafs_indopak=("ا[1]",),
                warsh_uthmani=("ا[1]",),
            ),
            absent_sound_rules=pick(
                hafs={"i": R("iltiqa_haraka")},
                warsh={"u[2]": R("iltiqa_haraka")},
            ),
        ),
        "restarted": Expect(
            read=explicit(ibtidaa=20, waqf=(20, 21)),
            phonemes=("q u l", "ʔ u d Q ʕ u:"),
            char_rules=_wasl_chars("hamza_wasl_damma", "ا[1]", "ا[1]"),
            sound_rules={"ʔ": R("hamza_wasl_damma")},
            absent_char_rules=_wasl_chars(
                "hamza_wasl_silent", "ا[1]", "ا[1]"
            ),
        ),
    }),
    # Hafs: بَعْضٍ ۗ ٱنظُرْ
    # Warsh: بَعْضٍۖ اُ۟نظُرْ
    StateCase(id="damm-copy-tanwin", site=Site.shared("6:65", (21, 22)), states={
        "joined": Expect(
            read=through(),
            phonemes=pick(
                hafs=("b a ʕ dˤ i n i", "ŋ ðˤ u rˤ"),
                warsh=("b a ʕ dˤ i n u", "ŋ ðˤ u rˤ"),
            ),
            char_rules=_wasl_chars("hamza_wasl_silent"),
            sound_rules=pick(
                hafs={"i[2]": R("iltiqa_haraka")},
                warsh={"u[1]": R("iltiqa_haraka")},
            ),
        ),
        "stopped": Expect(
            read=explicit(ibtidaa=21, waqf=(21, 22)),
            phonemes=("b a ʕ dˤ", "ʔ u ŋ ðˤ u rˤ"),
            char_rules=_wasl_chars("hamza_wasl_damma"),
            sound_rules={"ʔ": R("hamza_wasl_damma")},
            absent_sound_rules={"u[1]": R("iltiqa_haraka")},
        ),
    }),
    # Hafs: أَنِ ٱتَّقُوا۟
    # Warsh: أَنِ اِ۪تَّقُواْ
    Case(
        id="damm-needs-original-stem-vowel",
        site=Site.shared("4:131", (16, 17)),
        read=through(),
        phonemes=("ʔ a n i", "tt a q u:"),
        char_rules=_wasl_chars("hamza_wasl_silent", "ا[2]", "ا[1]"),
    ),
    # Hafs: وَقَالَتِ ٱخْرُجْ
    # Warsh: وَقَالَتُ اُ۟خْرُجْ
    Case(
        id="feminine-taa-connected-u",
        site=Site.shared("12:31", (14, 15)),
        read=through(),
        phonemes=pick(
            hafs=("w a q aˤ: l a t i", "x rˤ u ʒ Q"),
            warsh=("w a q aˤ: l a t u", "x rˤ u ʒ Q"),
        ),
        char_rules=_wasl_chars("hamza_wasl_silent", "ا[2]", "ا[2]"),
    ),
)


@pytest.mark.parametrize("run", case_runs((*CASES, *WARSH_U_CONTRASTS)))
def test_iltiqa(run):
    assert_case(run)
