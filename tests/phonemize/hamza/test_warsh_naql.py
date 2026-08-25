"""Warsh naql: the qata's vowel moves to the sakin host in joined speech,
and the qata is restored at every other boundary. The article family and
the lexical ridan never restore it."""
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
)

CASES = (
    # Warsh: قَدَ اَفْلَحَ
    StateCase(id="qad-aflaha", site=Site(warsh=("23:1", (1, 2))), states={
        "joined": Expect(
            read=explicit(ibtidaa=1, wasl=2),
            phonemes=("q aˤ d a", "f l a ħ a"),
            char_rules={"ا": R("naql"), "@fatha[2]": R("naql")},
            sound_rules={"a[1]": R("naql")},
            absent_char_rules={"د": R("qalqala_sughra"), "ف": R("naql")},
        ),
        "stopped-before": Expect(
            read=explicit(ibtidaa=1, waqf=(1, 2)),
            phonemes=("q aˤ d Q", "ʔ a f l a ħ"),
            sound_rules={"Q": R("qalqala_kubra")},
            absent_char_rules={"د": R("naql"), "ا": R("naql")},
            absent_sound_rules={"ʔ": R("naql")},
        ),
    }),
    # Warsh: عَذَابٌ اَلِيمٞۖ
    Case(
        id="tanwin-noon",
        site=Site(warsh=("2:104", (11, 12))),
        read=explicit(ibtidaa=11, waqf=12),
        phonemes=("ʕ a ð a: b u n a", "l i: m"),
        char_rules={"ا[2]": R("naql")},
        sound_rules={"a[2]": R("naql")},
        absent_sound_rules={"n": R("izhar")},
    ),
    # Warsh: يَوْمٍ ا۟جِّلَتْ
    Case(
        id="tanwin-damm",
        site=Site(warsh=("77:12", (2, 3))),
        read=explicit(ibtidaa=2, waqf=3),
        phonemes=("j a w m i n u", "ʒʒ i l a t"),
        char_rules={"ا": R("naql"), "@round_zero": R("naql")},
        sound_rules={"u": R("naql")},
    ),
    # Warsh: بَغَتِ
    Case(
        id="feminine-taa",
        site=Site(warsh=("49:9", (9,))),
        read=explicit(ibtidaa=9, waqf=10),
        phonemes="b a ɣ aˤ t i",
        sound_rules={"i": R("naql")},
        absent_sound_rules={"t": R("naql")},
    ),
    # Warsh: تَعَالَوَاْ اَتْلُ
    Case(
        id="leen-waw",
        site=Site(warsh=("6:151", (2, 3))),
        read=explicit(ibtidaa=2, wasl=3),
        phonemes=("t a ʕ a: l a w a", "t l u"),
        char_rules={"ا[3]": R("naql"), "@fatha[4]": R("naql")},
        sound_rules={"a[3]": R("naql")},
        absent_sound_rules={"w": R("naql")},
    ),
    # Warsh: اِ۬لَارْضِ
    StateCase(id="article-alard", site=Site(warsh=("2:11", (7,))), states={
        "joined": Expect(
            read=explicit(ibtidaa=6, wasl=7),
            phonemes="l a rˤ dˤ i",
            char_rules={
                "@fatha": R("naql"), "ا[2]": R("naql"),
                "ا[1]": R("hamza_wasl_silent"),
            },
            sound_rules={"a": R("naql")},
            absent_char_rules={"ر": R("naql")},
        ),
        "ibtidaa": Expect(
            read=explicit(ibtidaa=7, wasl=7),
            phonemes="ʔ a l a rˤ dˤ i",
            char_rules={"ا[1]": R("hamza_wasl_fatha"), "ا[2]": R("naql")},
            sound_rules={"ʔ": R("hamza_wasl_fatha"), "a[2]": R("naql")},
        ),
        "stopped": Expect(
            read=explicit(ibtidaa=6, waqf=7),
            phonemes="l a rˤ dˤ",
            char_rules={"ا[2]": R("naql")},
            sound_rules={"a": R("naql")},
        ),
    }),
    # Warsh: رِداٗ يُصَدِّقْنِےٓۖ
    Case(
        id="ridan-joined",
        site=Site(warsh=("28:34", (9, 10))),
        read=explicit(ibtidaa=9, waqf=10),
        phonemes=("r i d a", "j̃ u sˤ aˤ dd i q Q n i:"),
        char_rules={"@fathatan": R("naql")},
        sound_rules={
            "a": R("naql"), "j̃": R("idgham_bi_ghunnah"),
            "Q": R("qalqala_sughra"),
        },
    ),
    # Warsh: رِداٗ
    Case(
        id="ridan-waqf",
        site=Site(warsh=("28:34", (9,))),
        read=explicit(ibtidaa=9, waqf=9),
        phonemes="r i d a:",
        char_rules={"ا": R("naql", "madd_iwad", "madd_tabii")},
        sound_rules={"a:": R("naql", "madd_iwad", "madd_tabii")},
    ),
    # Warsh: كِتَٰبِيَهْۖ إِنِّے
    Case(
        id="kitabiyah-tahqiq",
        site=Site(warsh=("69:19", (9, 10))),
        read=explicit(ibtidaa=9, waqf=10),
        phonemes=("k i t a: b i j a h", "ʔ i ñ i:"),
        sound_rules={"ñ": R("ghunnah_mushaddadah")},
        absent_char_rules={"ه": R("naql"), "إ": R("naql")},
        absent_sound_rules={"ʔ": R("naql"), "h": R("naql")},
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_warsh_naql(run):
    assert_case(run)
