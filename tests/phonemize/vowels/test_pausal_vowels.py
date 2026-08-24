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


def _case(
    name: str,
    ref: str,
    word: int,
    joined: str,
    stopped: str,
    ending: str,
    base: str,
    *,
    indopak_ending: str | None = None,
):
    del base
    endings = (
        {ending: R("waqf_diacritic_drop")}
        if indopak_ending is None
        else pick(
            hafs_uthmani={ending: R("waqf_diacritic_drop")},
            hafs_indopak={indopak_ending: R("waqf_diacritic_drop")},
            warsh_uthmani={ending: R("waqf_diacritic_drop")},
        )
    )
    silent = (
        (ending,)
        if indopak_ending is None
        else pick(
            hafs_uthmani=(ending,),
            hafs_indopak=(indopak_ending,),
            warsh_uthmani=(ending,),
        )
    )
    return StateCase(id=name, site=Site.shared(ref, (word,)), states={
        "joined": Expect(read=joining(), phonemes=joined,
                         absent_char_rules=endings),
        "stopped": Expect(read=isolated(), phonemes=stopped,
                          char_rules=endings,
                          silent=silent),
    })


CASES = (
    # ذَٰلِكَ
    _case(
        "fatha", "2:2", 1, "ð a: l i k a", "ð a: l i k", "@fatha[2]", "ك",
        indopak_ending="@fatha",
    ),
    # ٱلْكِتَابُ
    _case("damma", "2:2", 2, "ʔ a l k i t a: b u", "ʔ a l k i t a: b Q",
          "@damma", "ب"),
    # رَبِّ
    _case("kasra", "1:2", 3, "rˤ aˤ bb i", "rˤ aˤ bb Q", "@kasra", "ب"),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_pausal_vowels(run):
    assert_case(run)
