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
    # Warsh: خَيْراٗ فَإِنَّ
    StateCase(id="fathatan-light-and-iwad", site=Site(warsh=("2:158", (20, 21))), states={
        "joined": Expect(
            read=through(), phonemes=("x aˤ j r a ŋ", "f a ʔ i ñ"),
            char_rules={"ر": R("tarqeeq")},
            sound_rules={"r": R("tarqeeq"), "a[1]": R("tarqeeq")},
            extra_phonemes=("emphatic_fatha",),
        ),
        "stopped": Expect(
            read=explicit(ibtidaa=20, waqf=(20, 21)),
            phonemes=("x aˤ j r a:", "f a ʔ i ñ"),
            char_rules={"ر": R("tarqeeq"), "ا": R("tarqeeq", "madd_iwad", "madd_tabii")},
            sound_rules={"r": R("tarqeeq"), "a:": R("tarqeeq", "madd_iwad", "madd_tabii")},
            extra_phonemes=("emphatic_fatha",),
        ),
    }),
    # Warsh: ذِكْراٗۖ فَمِنَ
    StateCase(id="five-word-heavy-and-iwad", site=Site(warsh=("2:200", (10, 11))), states={
        "joined": Expect(
            read=through(), phonemes=("ð i k rˤ aˤ ŋ", "f a m i n"),
            char_rules={"ر": R("tafkheem")},
            sound_rules={"rˤ": R("tafkheem"), "aˤ": R("tafkheem")},
            extra_phonemes=("emphatic_fatha",),
        ),
        "stopped": Expect(
            read=explicit(ibtidaa=10, waqf=(10, 11)),
            phonemes=("ð i k rˤ aˤ:", "f a m i n"),
            char_rules={"ر": R("tafkheem"), "ا": R("tafkheem", "madd_iwad", "madd_tabii")},
            sound_rules={"rˤ": R("tafkheem"), "aˤ:": R("tafkheem", "madd_iwad", "madd_tabii")},
            extra_phonemes=("emphatic_fatha",),
        ),
    }),
    # Warsh: خَيْرٞ لَّكُمْ
    StateCase(id="damma-light-then-pausal-sakin", site=Site(warsh=("2:54", (17, 18))), states={
        "joined": Expect(
            read=through(), phonemes=("x aˤ j r u", "ll a k u m"),
            char_rules={"ر": R("tarqeeq")}, sound_rules={"r": R("tarqeeq")},
            extra_phonemes=("emphatic_fatha",),
        ),
        "stopped": Expect(
            read=explicit(ibtidaa=17, waqf=(17, 18)),
            phonemes=("x aˤ j r", "l a k u m"),
            char_rules={"ر": R("tarqeeq")}, sound_rules={"r": R("tarqeeq")},
            extra_phonemes=("emphatic_fatha",),
        ),
    }),
    # Warsh: إِخْرَاجُهُمُۥٓۖ
    Case(id="khaa-intervening-exception", site=Site(warsh=("2:85", (22,))), read=isolated(),
         phonemes="ʔ i x r a: ʒ u h u m",
         char_rules={"ر": R("tarqeeq"), "ا": R("tarqeeq")},
         sound_rules={"r": R("tarqeeq"), "a:": R("tarqeeq")}),
    # Warsh: قِطْراٗۖ
    Case(id="intervening-isti-laa-blocker", site=Site(warsh=("18:96", (19,))), read=isolated(),
         phonemes="q i tˤ Q rˤ aˤ:",
         char_rules={"ر": R("tafkheem"), "ا": R("tafkheem", "madd_iwad", "madd_tabii")},
         sound_rules={"rˤ": R("tafkheem"), "aˤ:": R("tafkheem", "madd_iwad", "madd_tabii")}),
    # Warsh: لِرُقِيِّكَ
    Case(id="following-isti-laa-blocker", site=Site(warsh=("17:93", (13,))), read=isolated(),
         phonemes="l i rˤ u q i jj i k", char_rules={"ر": R("tafkheem")},
         sound_rules={"rˤ": R("tafkheem")}),
    # Warsh: إِسْرَآءِيلَ
    Case(id="israil-fixed-heavy", site=Site(warsh=("2:40", (2,))), read=isolated(),
         phonemes="ʔ i s rˤ aˤ: ʔ i: l",
         char_rules={"ر": R("tafkheem"), "ا": R("tafkheem", "madd_muttasil")},
         sound_rules={"rˤ": R("tafkheem"), "aˤ:": R("tafkheem", "madd_muttasil")}),
    # Warsh: إِبْرَٰهِيمَ
    Case(id="ibrahim-fixed-heavy", site=Site(warsh=("2:125", (10,))), read=isolated(),
         phonemes="ʔ i b Q rˤ aˤ: h i: m",
         char_rules={"ر": R("tafkheem"), "@dagger_alif": R("tafkheem", "madd_tabii")},
         sound_rules={"rˤ": R("tafkheem"), "aˤ:": R("tafkheem", "madd_tabii")}),
    # Warsh: عِمْرَٰنَ
    Case(id="imran-fixed-heavy", site=Site(warsh=("3:33", (9,))), read=isolated(),
         phonemes="ʕ i m rˤ aˤ: n",
         char_rules={"ر": R("tafkheem"), "@dagger_alif": R("tafkheem", "madd_arid_lissukun")},
         sound_rules={"rˤ": R("tafkheem"), "aˤ:": R("tafkheem", "madd_arid_lissukun")}),
    # Warsh: ذِرَاعَيْهِ
    Case(id="alif-ayn-fixed-light", site=Site(warsh=("18:18", (12,))), read=isolated(),
         phonemes="ð i r a: ʕ a j h",
         char_rules={"ر": R("tarqeeq"), "ا": R("tarqeeq", "madd_tabii")},
         sound_rules={"r": R("tarqeeq"), "a:": R("tarqeeq", "madd_tabii")}),
    # Warsh: عِشْرُونَ
    Case(id="ishruna-fixed-light", site=Site(warsh=("8:65", (10,))), read=isolated(),
         phonemes="ʕ i ʃ r u: n", char_rules={"ر": R("tarqeeq")},
         sound_rules={"r": R("tarqeeq")}),
    # Warsh: كِبْرٞ مَّا
    Case(id="kibr-damma-fixed-light", site=Site(warsh=("40:56", (14, 15))), read=through(),
         phonemes=("k i b Q r u", "m̃ a:"), char_rules={"ر": R("tarqeeq")},
         sound_rules={"r": R("tarqeeq")}),
    # Warsh: فِرْقٖ
    Case(id="firq-fixed-light", site=Site(warsh=("26:63", (11,))), read=isolated(),
         phonemes="f i r q Q", char_rules={"ر": R("tarqeeq")},
         sound_rules={"r": R("tarqeeq")}),
    # Warsh: اَ۬لْقِطْرِۖ
    Case(id="alqitr-pausal-light", site=Site(warsh=("34:12", (10,))), read=isolated(),
         phonemes="ʔ a l q i tˤ Q r", char_rules={"ر": R("tarqeeq")},
         sound_rules={"r": R("tarqeeq")}),
    # Warsh: بِمِصْرَ
    Case(id="misr-pausal-heavy", site=Site(warsh=("10:87", (8,))), read=isolated(),
         phonemes="b i m i sˤ rˤ", char_rules={"ر": R("tafkheem")},
         sound_rules={"rˤ": R("tafkheem")}),
    # Warsh: فَاسْرِ
    Case(id="asr-pausal-heavy", site=Site(warsh=("11:81", (9,))), read=isolated(),
         phonemes="f a s rˤ", char_rules={"ر": R("tafkheem")},
         sound_rules={"rˤ": R("tafkheem")}),
    # Warsh: يَسْرِۦ
    Case(id="yasr-pausal-light", site=Site(warsh=("89:4", (3,))), read=isolated(),
         phonemes="j a s r", char_rules={"ر": R("tarqeeq")},
         sound_rules={"r": R("tarqeeq")}),
    # Warsh: وَنُذُرِۦۖ
    Case(id="wanuthur-pausal-light", site=Site(warsh=("54:16", (4,))), read=isolated(),
         phonemes="w a n u ð u r", char_rules={"ر": R("tarqeeq")},
         sound_rules={"r": R("tarqeeq")}),
    # Warsh: وَالِاشْرَاقِ
    Case(id="alishraq-heavy", site=Site(warsh=("38:18", (7,))), read=isolated(),
         phonemes="w a l i ʃ rˤ aˤ: q Q",
         char_rules={"ر": R("tafkheem"), "ا[3]": R("tafkheem")},
         sound_rules={"rˤ": R("tafkheem"), "aˤ:": R("tafkheem")},
         extra_phonemes=("emphatic_fatha",)),
    # Warsh: حَيْرَانَۖ
    Case(id="hayran-heavy", site=Site(warsh=("6:71", (23,))), read=isolated(),
         phonemes="ħ a j rˤ aˤ: n",
         char_rules={"ر": R("tafkheem"), "ا": R("tafkheem")},
         sound_rules={"rˤ": R("tafkheem"), "aˤ:": R("tafkheem")},
         extra_phonemes=("emphatic_fatha",)),
    # Warsh: بِشَرَرٖ
    Case(id="bisharar-both-light-at-waqf", site=Site(warsh=("77:32", (3,))), read=isolated(),
         phonemes="b i ʃ a r a r", char_rules={"ر[1]": R("tarqeeq"), "ر[2]": R("tarqeeq")},
         sound_rules={"r[1]": R("tarqeeq"), "a[2]": R("tarqeeq"), "r[2]": R("tarqeeq")}),
    # Warsh: حَصِرَتْ صُدُورُهُمُۥٓ
    StateCase(id="hasirat-cross-word-owner", site=Site(warsh=("4:90", (11, 12))), states={
        "joined": Expect(
            read=through(), phonemes=("ħ a sˤ i r a t", "sˤ u d u: rˤ u h u m"),
            char_rules={"ر[1]": R("tarqeeq")}, sound_rules={"r": R("tarqeeq"), "a[2]": R("tarqeeq")},
        ),
        "stopped": Expect(
            read=explicit(ibtidaa=11, waqf=(11, 12)),
            phonemes=("ħ a sˤ i r a t", "sˤ u d u: rˤ u h u m"),
            char_rules={"ر[1]": R("tarqeeq")}, sound_rules={"r": R("tarqeeq"), "a[2]": R("tarqeeq")},
        ),
    }),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_warsh_raa(run):
    assert_case(run)
