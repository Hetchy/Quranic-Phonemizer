from __future__ import annotations

import pytest

from tests.support import (
    Expect,
    R,
    Site,
    StateCase,
    assert_case,
    case_runs,
    isolated,
    joining,
    pick,
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
    # قَوَارِيرَا۠
    _pausal("qawarira-first", "76:15", 8, "q aˤ w a: r i: rˤ aˤ",
            "q aˤ w a: r i: rˤ aˤ:", "aˤ[2]", "aˤ:", "@fatha[3]",
            indopak_inserts_carrier=True),
    # ٱلظُّنُونَا۠
    _pausal("al-thununa", "33:10", 16, "ʔ a ðˤðˤ u n u: n a",
            "ʔ a ðˤðˤ u n u: n a:", "a[2]", "a:", "@fatha"),
    # ٱلرَّسُولَا۠
    _pausal("al-rasula", "33:66", 11, "ʔ a rˤrˤ aˤ s u: l a",
            "ʔ a rˤrˤ aˤ s u: l a:", "a[2]", "a:", "@fatha[2]"),
    # ٱلسَّبِيلَا۠
    _pausal("al-sabila", "33:67", 8, "ʔ a ss a b i: l a",
            "ʔ a ss a b i: l a:", "a[3]", "a:", "@fatha[2]"),
    # أَنَا۠
    _pausal(
        "ana", "2:258", 21, "ʔ a n a", "ʔ a n a:",
        "a[2]", "a:", "@fatha[2]"
    ),
    # لَكِنَّا۠
    _pausal("lakinna", "18:38", 1, "l a: k i ñ a", "l a: k i ñ a:",
            "a", "a:[2]", "@fatha[2]", indopak_fatha="@fatha",
            indopak_inserts_carrier=True),
    # قَوَارِيرَا۟
    StateCase(id="qawarira-second", site=Site(hafs=("76:16", (1,))), states={
        "joined": Expect(read=joining(), phonemes="q aˤ w a: r i: rˤ aˤ",
                         absent_char_rules={"ا[2]": R("pausal_alif")}),
        "stopped": Expect(read=isolated(), phonemes="q aˤ w a: r i: r",
                          absent_char_rules={"ا[2]": R("pausal_alif")}),
    }),
    # سَلَاسِلَا۟
    StateCase(id="salasila", site=Site(hafs=("76:4", (4,))), states={
        "joined": Expect(read=joining(), phonemes="s a l a: s i l a",
                         absent_char_rules={"ا": R("pausal_alif")}),
        "stopped": Expect(read=isolated(), phonemes="s a l a: s i l",
                          absent_char_rules={"ا": R("pausal_alif")}),
    }),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_seven_alifs(run):
    assert_case(run)
