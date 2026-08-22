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
)


def _case(name: str, ref: str, word: int, joined: str, stopped: str, ending: str | None,
          base: str):
    return StateCase(id=name, site=Site(hafs=(ref, (word,))), states={
        "joined": Expect(read=joining(), phonemes=joined,
                         absent_char_rules={base: R("pausal_sukun")}),
        "stopped": Expect(read=isolated(), phonemes=stopped,
                          char_rules={base: R("pausal_sukun")},
                          silent=(ending,) if ending else ()),
    })


CASES = (
    # ذَٰلِكَ
    _case("fatha", "2:2", 1, "ð a: l i k a", "ð a: l i k", None, "ك"),
    # ٱلْكِتَابُ
    _case("damma", "2:2", 2, "ʔ a l k i t a: b u", "ʔ a l k i t a: b Q",
          "@damma", "ب"),
    # رَبِّ
    _case("kasra", "1:2", 3, "rˤ aˤ bb i", "rˤ aˤ bb Q", "@kasra", "ب"),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_pausal_vowels(run):
    assert_case(run)
