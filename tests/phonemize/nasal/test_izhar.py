from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated, joining, through


MUTLAQ = (
    ("2:85", 38),
    ("37:97", 4),
    ("13:4", 10),
    ("6:99", 23),
)


CASES = (
    # مِنْ أَحَدٍ حَتَّىٰ
    Case(
        id="hamza-ha",
        site=Site(hafs=("2:102", (26, 27, 28))),
        read=through(),
        phonemes=("m i n", "ʔ a ħ a d i n", "ħ a tt a:"),
        char_rules={"ن": R("izhar"), "@kasratan": R("izhar")},
        sound_rules={"n[1]": R("izhar"), "n[2]": R("izhar")},
    ),
    # مِنْهَا رَغَدًا حَيْثُ
    Case(
        id="heh-ha",
        site=Site.shared("2:35", (8, 9, 10)),
        read=through(),
        phonemes=("m i n h a:", "rˤ aˤ ɣ aˤ d a n", "ħ a j θ"),
        char_rules={"ن": R("izhar"), "@fathatan": R("izhar")},
        sound_rules={"n[1]": R("izhar"), "n[2]": R("izhar")},
    ),
    # يَكُنْ غَنِيًّا أَوْ
    Case(
        id="ghayn-hamza",
        site=Site.shared("4:135", (16, 17, 18)),
        read=through(),
        phonemes=("j a k u n", "ɣ aˤ n i jj a n", "ʔ a w"),
        char_rules={"ن[1]": R("izhar"), "@fathatan": R("izhar")},
        sound_rules={"n[1]": R("izhar"), "n[3]": R("izhar")},
    ),
    # قِرَدَةً خَاسِئِينَ
    Case(
        id="kha",
        site=Site.shared("2:65", (11, 12)),
        read=through(),
        phonemes=("q i rˤ aˤ d a t a n", "x aˤ: s i ʔ i: n"),
        char_rules={"@fathatan": R("izhar")},
        sound_rules={"n[1]": R("izhar")},
    ),
    # مِنْ عِلْمٍ
    Case(
        id="ayn",
        site=Site.shared("4:157", (27, 28)),
        read=through(),
        phonemes=("m i n", "ʕ i l m"),
        char_rules={"ن": R("izhar")},
        sound_rules={"n": R("izhar")},
    ),
    # شَىْءٍ عَلِيمٌ
    Case(
        id="kasratan",
        site=Site.shared("2:29", (18, 19)),
        read=through(),
        phonemes=("ʃ a j ʔ i n", "ʕ a l i: m"),
        char_rules={"@kasratan": R("izhar")},
        sound_rules={"n": R("izhar")},
    ),
    # قَدِيرٌ أَلَمْ
    Case(
        id="verse-seam",
        site=Site.shared("2:106", (19,)),
        read=joining(),
        phonemes="q aˤ d i: rˤ u n",
        char_rules={"@dammatan": R("izhar")},
        sound_rules={"n": R("izhar")},
    ),
    # ٱلدُّنْيَا
    Case(
        id="mutlaq-dunya",
        site=Site.shared("2:85", (38,)),
        read=isolated(),
        phonemes="ʔ a dd u n j a:",
        char_rules={"ن": R("izhar")},
        sound_rules={"n": R("izhar")},
    ),
    # بُنْيَانًا
    Case(
        id="mutlaq-bunyan",
        site=Site.shared("37:97", (4,)),
        read=isolated(),
        phonemes="b u n j a: n a:",
        char_rules={"ن[1]": R("izhar")},
        sound_rules={"n[1]": R("izhar")},
    ),
    # قِنْوَانٌ
    Case(
        id="mutlaq-qinwan",
        site=Site.shared("6:99", (23,)),
        read=isolated(),
        phonemes="q i n w a: n",
        char_rules={"ن[1]": R("izhar")},
        sound_rules={"n[1]": R("izhar")},
    ),
    # نَسْتَعِينُ
    Case(
        id="pausal-noon-after-haraka",
        site=Site.shared("1:5", (4,)),
        read=isolated(),
        phonemes="n a s t a ʕ i: n",
        char_rules={"ن[2]": R("izhar")},
        sound_rules={"n[2]": R("izhar")},
    ),
    # مُبِينٌ
    Case(
        id="pausal-noon-after-tanwin",
        site=Site.shared("37:113", (10,)),
        read=isolated(),
        phonemes="m u b i: n",
        char_rules={"ن": R("izhar")},
        sound_rules={"n": R("izhar")},
        silent=("@dammatan",),
    ),
)


def test_the_mutlaq_register_is_closed():
    assert MUTLAQ == (
        ("2:85", 38),
        ("37:97", 4),
        ("13:4", 10),
        ("6:99", 23),
    )


@pytest.mark.parametrize("run", case_runs(CASES))
def test_izhar(run):
    assert_case(run)
