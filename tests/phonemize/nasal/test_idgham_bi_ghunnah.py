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
    # مَن يَشَآءُ
    Case(
        id="noon-yaa",
        site=Site(hafs=("3:74", (3, 4))),
        read=through(),
        phonemes=("m a", "j̃ a ʃ a: ʔ"),
        char_rules={"ن": R("idgham_bi_ghunnah"),
                    "ي": R("idgham_bi_ghunnah")},
        sound_rules={"j̃": R("idgham_bi_ghunnah")},
    ),
    # حَيَوٰةٌ يَـٰٓأُو۟لِى
    Case(
        id="dammatan-yaa",
        site=Site(hafs=("2:179", (4, 5))),
        read=through(),
        phonemes=("ħ a j a: t u", "j̃ a: ʔ u l i:"),
        char_rules={"@dammatan": R("idgham_bi_ghunnah"),
                    "ي[2]": R("idgham_bi_ghunnah")},
        sound_rules={"j̃": R("idgham_bi_ghunnah")},
    ),
    # صِدِّيقًا نَّبِيًّا
    Case(
        id="fathatan-noon",
        site=Site(hafs=("19:41", (7, 8))),
        read=through(),
        phonemes=("sˤ i dd i: q aˤ", "ñ a b i jj a:"),
        char_rules={"@fathatan[1]": R("idgham_bi_ghunnah"),
                    "ن": R("idgham_bi_ghunnah")},
        sound_rules={"ñ": R("idgham_bi_ghunnah")},
    ),
    # تَكُن مِّنَ
    StateCase(
        id="noon-meem-boundary",
        site=Site(hafs=("3:60", (5, 6))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("t a k u", "m̃ i n"),
                char_rules={"ن[1]": R("idgham_bi_ghunnah"),
                            "م": R("idgham_bi_ghunnah")},
                sound_rules={"m̃": R("idgham_bi_ghunnah")},
            ),
            "stopped": Expect(
                read=explicit(ibtidaa=5, waqf=(5, 6)),
                phonemes=("t a k u n", "m i n"),
                char_rules={"ن[1]": R("izhar")},
                sound_rules={"n[1]": R("izhar")},
                absent_char_rules={"ن[1]": R("idgham_bi_ghunnah"),
                                   "م": R("idgham_bi_ghunnah")},
            ),
        },
    ),
    # بَعْضٍ وَٱللَّهُ
    Case(
        id="kasratan-waw",
        site=Site(hafs=("3:34", (4, 5))),
        read=through(),
        phonemes=("b a ʕ dˤ i", "w̃ a lˤlˤ aˤ: h"),
        char_rules={"@kasratan": R("idgham_bi_ghunnah"),
                    "و": R("idgham_bi_ghunnah")},
        sound_rules={"w̃": R("idgham_bi_ghunnah")},
    ),
    # عَظِيمٌ وَمِنَ
    Case(
        id="verse-seam",
        site=Site(hafs=("2:7", (12, 13))),
        read=explicit(ibtidaa=12, wasl=12, waqf=13),
        phonemes=("ʕ a ðˤ i: m u", "w̃ a m i n"),
        char_rules={"@dammatan": R("idgham_bi_ghunnah"),
                    "و": R("idgham_bi_ghunnah")},
        sound_rules={"w̃": R("idgham_bi_ghunnah")},
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_idgham_bi_ghunnah(run):
    assert_case(run)
