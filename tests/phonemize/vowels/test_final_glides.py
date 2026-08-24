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


def _case(name: str, ref: str, word: int, joined: str, stopped: str,
          source: str, long: str, *, warsh: bool = True):
    site = Site.shared(ref, (word,)) if warsh else Site(hafs=(ref, (word,)))
    return StateCase(id=name, site=site, states={
        "joined": Expect(read=joining(), phonemes=joined,
                         absent_char_rules={source: R("madd_tabii")}),
        "stopped": Expect(read=isolated(), phonemes=stopped,
                          char_rules={source: R("madd_tabii")},
                          sound_rules={long: R("madd_tabii")}),
    })


CASES = (
    # Hafs: هُوَ
    # Warsh: هُوَ
    _case("waw", "2:29", 1, "h u w a", "h u:", "و", "u:"),
    # Hafs: هِىَ
    # Warsh: هِيَ
    _case("yaa", "2:70", 8, "h i j a", "h i:", "@yaa", "i:"),
    # Hafs: يَعْفُوَا۟
    # Warsh: يَعْفُوَاْ
    _case("yafuwa", "2:237", 18, "j a ʕ f u w a", "j a ʕ f u:", "و", "u:"),
    # Hafs: لِّتَتْلُوَا۟
    # Warsh: لِّتَتْلُوَاْ
    _case("litatluwa", "13:30", 10, "l i t a t l u w a", "l i t a t l u:",
          "و", "u:"),
    # Hafs: نَّدْعُوَا۟
    # Warsh: نَّدْعُوَاْ
    _case("naduwa", "18:14", 12, "n a d Q ʕ u w a", "n a d Q ʕ u:", "و", "u:"),
    # Hafs: أَتْلُوَا۟
    # Warsh: اَتْلُوَاْ
    _case("atluwa", "27:92", 2, "ʔ a t l u w a", "ʔ a t l u:", "و", "u:"),
    # Hafs: لِّيَرْبُوَا۟
    _case("liyarbuwa", "30:39", 5, "l i j a rˤ b u w a", "l i j a rˤ b u:",
          "و", "u:", warsh=False),
    # Hafs: لِّيَبْلُوَا۟
    # Warsh: لِّيَبْلُوَاْ
    _case("liyabluwa", "47:4", 28, "l i j a b Q l u w a", "l i j a b Q l u:",
          "و", "u:"),
    # Hafs: وَنَبْلُوَا۟
    # Warsh: وَنَبْلُوَاْ
    _case("wanabluwa", "47:31", 7, "w a n a b Q l u w a", "w a n a b Q l u:",
          "و[2]", "u:"),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_final_glides(run):
    assert_case(run)
