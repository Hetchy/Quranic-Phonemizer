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
    joining,
    pick,
    through,
)


def _pausal(
    name: str,
    ref: str,
    word: int,
    joined: str,
    stopped: str,
    short: str,
    long: str,
    fatha: str,
    *,
    indopak_fatha: str | None = None,
    indopak_inserts_carrier: bool = False,
):
    stopped_rules = R("pausal_alif", "madd_tabii")
    joined_char_rules = (
        {fatha: R("pausal_alif")}
        if indopak_fatha is None
        else pick(
            hafs_uthmani={fatha: R("pausal_alif")},
            hafs_indopak={indopak_fatha: R("pausal_alif")},
        )
    )
    return StateCase(id=name, site=Site(hafs=(ref, (word,))), states={
        "joined": Expect(read=joining(), phonemes=joined,
                         char_rules=joined_char_rules,
                         sound_rules={short: R("pausal_alif")}),
        "stopped": Expect(read=isolated(), phonemes=stopped,
                          char_rules=pick(
                              hafs_uthmani={"@pausal_alif": stopped_rules},
                              hafs_indopak=(
                                  {} if indopak_inserts_carrier
                                  else {"@pausal_alif": stopped_rules}
                              ),
                          ),
                          sound_rules={long: stopped_rules}),
    })


CASES = (
    # Hafs: قَوَارِيرَا۠
    _pausal("qawarira-first", "76:15", 8, "q aˤ w a: r i: rˤ aˤ",
            "q aˤ w a: r i: rˤ aˤ:", "aˤ[2]", "aˤ:", "@fatha[3]",
            indopak_inserts_carrier=True),
    # Hafs: ٱلظُّنُونَا۠
    _pausal("al-thununa", "33:10", 16, "ʔ a ðˤðˤ u n u: n a",
            "ʔ a ðˤðˤ u n u: n a:", "a[2]", "a:", "@fatha"),
    # Hafs: ٱلرَّسُولَا۠
    _pausal("al-rasula", "33:66", 11, "ʔ a rˤrˤ aˤ s u: l a",
            "ʔ a rˤrˤ aˤ s u: l a:", "a[2]", "a:", "@fatha[2]"),
    # Hafs: ٱلسَّبِيلَا۠
    _pausal("al-sabila", "33:67", 8, "ʔ a ss a b i: l a",
            "ʔ a ss a b i: l a:", "a[3]", "a:", "@fatha[2]"),
    # Hafs: أَنَا۠
    _pausal(
        "ana", "2:258", 21, "ʔ a n a", "ʔ a n a:",
        "a[2]", "a:", "@fatha[2]"
    ),
    # Hafs: لَّـٰكِنَّا۠
    _pausal("lakinna", "18:38", 1, "l a: k i ñ a", "l a: k i ñ a:",
            "a", "a:[2]", "@fatha[2]", indopak_fatha="@fatha",
            indopak_inserts_carrier=True),
    # Hafs: قَوَارِيرَا۟
    StateCase(id="qawarira-second", site=Site(hafs=("76:16", (1,))), states={
        "joined": Expect(read=joining(), phonemes="q aˤ w a: r i: rˤ aˤ",
                         absent_char_rules={"ا[2]": R("pausal_alif")}),
        "stopped": Expect(read=isolated(), phonemes="q aˤ w a: r i: r",
                          absent_char_rules={"ا[2]": R("pausal_alif")}),
    }),
    # Hafs: سَلَـٰسِلَا۟
    StateCase(id="salasila", site=Site(hafs=("76:4", (4,))), states={
        "joined": Expect(read=joining(), phonemes="s a l a: s i l a",
                         absent_char_rules={"ا": R("pausal_alif")}),
        "stopped": Expect(read=isolated(), phonemes="s a l a: s i l",
                          absent_char_rules={"ا": R("pausal_alif")}),
    }),
)


WARSH_CASES = (
    # Warsh: اَنَآ أُنَبِّئُكُم
    StateCase(id="warsh-ana-retained-u", site=Site(warsh=("12:45", (8, 9))), states={
        "joined": Expect(
            read=through(), phonemes=("ʔ a n a:", "ʔ u n a bb i ʔ u k u m"),
            char_rules={"ا[2]": R("madd_munfasil")},
            sound_rules={"a:": R("madd_munfasil")},
        ),
        "host-waqf": Expect(
            read=explicit(ibtidaa=8, waqf=(8, 9)),
            phonemes=("ʔ a n a:", "ʔ u n a bb i ʔ u k u m"),
            char_rules={"ا[2]": R("madd_tabii")},
            sound_rules={"a:": R("madd_tabii")},
            absent_char_rules={"ا[2]": R("pausal_alif", "madd_munfasil")},
        ),
    }),
    # Warsh: أَنَآ أَخُوكَ
    Case(
        id="warsh-ana-retained-a",
        site=Site(warsh=("12:69", (10, 11))),
        read=through(),
        phonemes=("ʔ a n a:", "ʔ a x u: k"),
        char_rules={"ا": R("madd_munfasil")},
        sound_rules={"a:": R("madd_munfasil")},
    ),
    # Warsh: اَنَا إِلَّا
    StateCase(id="warsh-ana-qata-i", site=Site(warsh=("7:188", (23, 24))), states={
        "joined": Expect(
            read=through(), phonemes=("ʔ a n a", "ʔ i ll a:"),
            char_rules={"ا[2]": R("pausal_alif")},
            sound_rules={"a[2]": R("pausal_alif")},
            absent_char_rules={"ا[2]": R("madd_munfasil")},
        ),
        "host-waqf": Expect(
            read=explicit(ibtidaa=23, waqf=(23, 24)),
            phonemes=("ʔ a n a:", "ʔ i ll a:"),
            char_rules={"ا[2]": R("pausal_alif", "madd_tabii")},
            sound_rules={"a:[1]": R("pausal_alif", "madd_tabii")},
        ),
    }),
    # Warsh: أَنَا بِبَاسِطٍ
    Case(
        id="warsh-ana-moving-onset",
        site=Site(warsh=("5:28", (7, 8))),
        read=through(),
        phonemes=("ʔ a n a", "b i b a: s i tˤ Q"),
        char_rules={"ا[1]": R("pausal_alif")},
        sound_rules={"a[2]": R("pausal_alif")},
    ),
    # Warsh: أَنَا اَ۬لْغَفُورُ
    # Ana's joined short A is the pausal-alif joined face, not iltiqa shortening.
    Case(
        id="warsh-ana-wasl-onset",
        site=Site(warsh=("15:49", (4, 5))),
        read=through(),
        phonemes=("ʔ a n a", "l ɣ aˤ f u: rˤ"),
        char_rules={"ا[1]": R("pausal_alif"), "ا[2]": R("hamza_wasl_silent")},
        sound_rules={"a[2]": R("pausal_alif")},
        absent_sound_rules={"a[2]": R("iltiqa_shortening")},
    ),
    # Warsh: لَّٰكِنَّا هُوَ اَ۬للَّهُ
    StateCase(id="warsh-lakinna", site=Site(warsh=("18:38", (1, 2, 3))), states={
        "joined": Expect(
            read=through(),
            phonemes=("l a: k i ñ a", "h u w a", "lˤlˤ aˤ: h"),
            char_rules={"ا[1]": R("pausal_alif")},
            sound_rules={"a[1]": R("pausal_alif")},
        ),
        "host-waqf": Expect(
            read=explicit(ibtidaa=1, waqf=(1, 3)),
            phonemes=("l a: k i ñ a:", "h u w a", "lˤlˤ aˤ: h"),
            char_rules={"ا[1]": R("pausal_alif", "madd_tabii")},
            sound_rules={"a:[2]": R("pausal_alif", "madd_tabii")},
        ),
    }),
    # Warsh: اِ۬لظُّنُونَاۖ هُنَالِكَ
    StateCase(id="warsh-thununa", site=Site(warsh=("33:10", (16, 17))), states={
        "joined": Expect(
            read=through(),
            phonemes=("ʔ a ðˤðˤ u n u: n a:", "h u n a: l i k"),
            char_rules={"ا[2]": R("madd_tabii")},
            sound_rules={"a:[1]": R("madd_tabii")},
        ),
        "host-waqf": Expect(
            read=explicit(ibtidaa=16, waqf=(16, 17)),
            phonemes=("ʔ a ðˤðˤ u n u: n a:", "h u n a: l i k"),
            char_rules={"ا[2]": R("madd_tabii")},
        ),
    }),
    # Warsh: اَ۬لرَّسُولَاۖ وَقَالُواْ
    StateCase(id="warsh-rasula", site=Site(warsh=("33:66", (11, 12))), states={
        "joined": Expect(
            read=through(),
            phonemes=("ʔ a rˤrˤ aˤ s u: l a:", "w a q aˤ: l u:"),
            char_rules={"ا[2]": R("madd_tabii")},
        ),
        "host-waqf": Expect(
            read=explicit(ibtidaa=11, waqf=(11, 12)),
            phonemes=("ʔ a rˤrˤ aˤ s u: l a:", "w a q aˤ: l u:"),
            char_rules={"ا[2]": R("madd_tabii")},
        ),
    }),
    # Warsh: اَ۬لسَّبِيلَاۖ رَبَّنَآ
    StateCase(id="warsh-sabila", site=Site(warsh=("33:67", (8, 9))), states={
        "joined": Expect(
            read=through(),
            phonemes=("ʔ a ss a b i: l a:", "rˤ aˤ bb a n a:"),
            char_rules={"ا[2]": R("madd_tabii")},
        ),
        "host-waqf": Expect(
            read=explicit(ibtidaa=8, waqf=(8, 9)),
            phonemes=("ʔ a ss a b i: l a:", "rˤ aˤ bb a n a:"),
            char_rules={"ا[2]": R("madd_tabii")},
        ),
    }),
    # Warsh: سَلَٰسِلاٗ وَأَغْلَٰلاٗ
    StateCase(id="warsh-salasila", site=Site(warsh=("76:4", (4, 5))), states={
        "joined": Expect(
            read=through(),
            phonemes=("s a l a: s i l a", "w̃ a ʔ a ɣ l a: l a:"),
            char_rules={
                "@fathatan[1]": R("idgham_bi_ghunnah"),
                "و": R("idgham_bi_ghunnah"),
            },
            sound_rules={"w̃": R("idgham_bi_ghunnah")},
        ),
        "host-waqf": Expect(
            read=explicit(ibtidaa=4, waqf=(4, 5)),
            phonemes=("s a l a: s i l a:", "w a ʔ a ɣ l a: l a:"),
            sound_rules={"a:[2]": R("madd_iwad", "madd_tabii")},
        ),
    }),
)


QAWARIRA_CASES = (
    # Warsh: قَوَارِيراٗۖ قَوَارِيراٗ
    Case(
        id="warsh-qawarira-first",
        site=Site(warsh=("76:15", (8, 9))),
        read=through(),
        phonemes=("q aˤ w a: r i: r a ŋˤ", "q aˤ w a: r i: r a:"),
        char_rules={"@fathatan[1]": R("ikhfaa")},
        sound_rules={"ŋˤ": R("ikhfaa"), "a:[3]": R("madd_iwad", "madd_tabii")},
        extra_phonemes=("emphatic_fatha", "emphatic_ikhfaa"),
    ),
    # Warsh: قَوَارِيراٗ مِّن
    StateCase(id="warsh-qawarira-second", site=Site(warsh=("76:16", (1, 2))), states={
        "joined": Expect(
            read=through(),
            phonemes=("q aˤ w a: r i: r a", "m̃ i n"),
            char_rules={"@fathatan": R("idgham_bi_ghunnah"), "م": R("idgham_bi_ghunnah")},
            sound_rules={"m̃": R("idgham_bi_ghunnah")},
        ),
        "host-waqf": Expect(
            read=explicit(ibtidaa=1, waqf=(1, 2)),
            phonemes=("q aˤ w a: r i: r a:", "m i n"),
            sound_rules={"a:[2]": R("madd_iwad", "madd_tabii")},
        ),
    }),
)


@pytest.mark.parametrize("run", case_runs((*CASES, *WARSH_CASES)))
def test_seven_alifs(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(QAWARIRA_CASES))
def test_seven_alifs_qawarira_raa_interaction(run):
    assert_case(run)
