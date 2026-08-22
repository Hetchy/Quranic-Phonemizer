from __future__ import annotations

import pytest

from quranic_phonemizer.model.address import KhilafId
from tests.support import (
    Case,
    Expect,
    R,
    Site,
    VariantCase,
    assert_case,
    case_runs,
    explicit,
    joining,
)


CASES = (
    # الم
    Case(id="alif-lam-meem", site=Site(hafs=("2:1", (1,))), read=joining(),
         phonemes="ʔ a l i f l a: m̃ i: m",
         all_rules=R("idgham_shafawi", "izhar_shafawi", "madd_lazim"),
         char_rules={"ل": R("madd_lazim"),
                     "م": R("idgham_shafawi", "madd_lazim")},
         sound_rules={"a:": R("madd_lazim"), "m̃": R("idgham_shafawi"),
                      "i:": R("madd_lazim"), "m": R("izhar_shafawi")}),
    # المص
    Case(id="alif-lam-meem-saad", site=Site(hafs=("7:1", (1,))), read=joining(),
         phonemes="ʔ a l i f l a: m̃ i: m sˤ aˤ: d Q",
         all_rules=R("idgham_shafawi", "izhar_shafawi", "madd_lazim", "tafkheem", "qalqala_sughra"),
         char_rules={"ل": R("madd_lazim"),
                     "م": R("idgham_shafawi", "madd_lazim"),
                     "ص": R("madd_lazim", "tafkheem")},
         sound_rules={"a:": R("madd_lazim"), "m̃": R("idgham_shafawi"),
                      "i:": R("madd_lazim"), "m": R("izhar_shafawi"),
                      "sˤ": R("tafkheem"), "aˤ:": R("madd_lazim", "tafkheem"),
                      "Q": R("qalqala_sughra")}),
    # الر
    Case(id="alif-lam-raa", site=Site(hafs=("10:1", (1,))), read=joining(),
         phonemes="ʔ a l i f l a: m rˤ aˤ:",
         all_rules=R("izhar_shafawi", "madd_lazim", "madd_tabii", "tafkheem"),
         char_rules={"ل": R("madd_lazim"), "ر": R("madd_tabii", "tafkheem")},
         sound_rules={"a:": R("madd_lazim"), "m": R("izhar_shafawi"),
                      "rˤ": R("tafkheem"), "aˤ:": R("madd_tabii", "tafkheem")}),
    # المر
    Case(id="alif-lam-meem-raa", site=Site(hafs=("13:1", (1,))), read=joining(),
         phonemes="ʔ a l i f l a: m̃ i: m rˤ aˤ:",
         all_rules=R("idgham_shafawi", "izhar_shafawi", "madd_lazim", "madd_tabii", "tafkheem"),
         char_rules={"ل": R("madd_lazim"),
                     "م": R("idgham_shafawi", "madd_lazim"),
                     "ر": R("madd_tabii", "tafkheem")},
         sound_rules={"a:": R("madd_lazim"), "m̃": R("idgham_shafawi"),
                      "i:": R("madd_lazim"), "m": R("izhar_shafawi"),
                      "rˤ": R("tafkheem"), "aˤ:": R("madd_tabii", "tafkheem")}),
    # كهيعص
    Case(id="kaaf-haa-yaa-ayn-saad", site=Site(hafs=("19:1", (1,))), read=joining(),
         phonemes="k a: f h a: j a: ʕ a j ŋ sˤ aˤ: d Q",
         all_rules=R("ikhfaa_haqiqi", "madd_lazim", "madd_tabii", "tafkheem", "qalqala_sughra"),
         char_rules={"ك": R("madd_lazim"), "ه": R("madd_tabii"), "ي": R("madd_tabii"),
                     "ع": R("madd_lazim"),
                     "ص": R("madd_lazim", "tafkheem")},
         sound_rules={"a:[1]": R("madd_lazim"), "a:[2]": R("madd_tabii"),
                      "a:[3]": R("madd_tabii"), "j[2]": R("madd_lazim"),
                      "ŋ": R("ikhfaa_haqiqi", "tafkheem"),
                      "sˤ": R("tafkheem"), "aˤ:": R("madd_lazim", "tafkheem"),
                      "Q": R("qalqala_sughra")}),
    # طه
    Case(id="taa-haa", site=Site(hafs=("20:1", (1,))), read=joining(),
         phonemes="tˤ aˤ: h a:", all_rules=R("madd_tabii", "tafkheem"),
         char_rules={"ط": R("madd_tabii", "tafkheem"),
                     "ه": R("madd_tabii")},
         sound_rules={"tˤ": R("tafkheem"), "aˤ:": R("madd_tabii", "tafkheem")}),
    # طسم
    Case(id="taa-seen-meem", site=Site(hafs=("26:1", (1,))), read=joining(),
         phonemes="tˤ aˤ: s i: m̃ i: m",
         all_rules=R("idgham_bi_ghunnah", "izhar_shafawi", "madd_tabii", "madd_lazim", "tafkheem"),
         char_rules={"ط": R("madd_tabii", "tafkheem"),
                     "س": R("madd_lazim"),
                     "م": R("idgham_bi_ghunnah", "madd_lazim")},
         sound_rules={"tˤ": R("tafkheem"), "aˤ:": R("madd_tabii", "tafkheem"),
                      "i:[1]": R("madd_lazim"), "m̃": R("idgham_bi_ghunnah"),
                      "i:[2]": R("madd_lazim"), "m": R("izhar_shafawi")}),
    # طس
    Case(id="taa-seen", site=Site(hafs=("27:1", (1,))), read=joining(),
         phonemes="tˤ aˤ: s i: n",
         all_rules=R("izhar", "madd_tabii", "madd_lazim", "tafkheem"),
         char_rules={"ط": R("madd_tabii", "tafkheem"), "س": R("madd_lazim")},
         sound_rules={"tˤ": R("tafkheem"), "aˤ:": R("madd_tabii", "tafkheem"),
                      "i:": R("madd_lazim"), "n": R("izhar")}),
    # يس
    Case(id="yaa-seen", site=Site(hafs=("36:1", (1,))), read=joining(),
         phonemes="j a: s i: n", all_rules=R("izhar", "madd_tabii", "madd_lazim"),
         char_rules={"ي": R("madd_tabii"), "س": R("madd_lazim")},
         sound_rules={"a:": R("madd_tabii"), "i:": R("madd_lazim"), "n": R("izhar")}),
    # ص
    Case(id="saad", site=Site(hafs=("38:1", (1,))), read=joining(),
         phonemes="sˤ aˤ: d Q", all_rules=R("madd_lazim", "tafkheem", "qalqala_sughra"),
         char_rules={"ص": R("madd_lazim", "tafkheem")},
         sound_rules={"sˤ": R("tafkheem"), "aˤ:": R("madd_lazim", "tafkheem"),
                      "Q": R("qalqala_sughra")}),
    # حم
    Case(id="haa-meem", site=Site(hafs=("40:1", (1,))), read=joining(),
         phonemes="ħ a: m i: m", all_rules=R("izhar_shafawi", "madd_tabii", "madd_lazim"),
         char_rules={"ح": R("madd_tabii"), "م": R("madd_lazim")},
         sound_rules={"a:": R("madd_tabii"), "i:": R("madd_lazim"),
                      "m[2]": R("izhar_shafawi")}),
    # عسق
    Case(id="ayn-seen-qaaf", site=Site(hafs=("42:2", (1,))), read=joining(),
         phonemes="ʕ a j ŋ s i: ŋ q aˤ: f",
         all_rules=R("ikhfaa_haqiqi", "madd_lazim", "tafkheem"),
         char_rules={"ع": R("madd_lazim"),
                     "س": R("madd_lazim"),
                     "ق": R("madd_lazim", "tafkheem")},
         sound_rules={"j": R("madd_lazim"), "ŋ[1]": R("ikhfaa_haqiqi"),
                      "i:": R("madd_lazim"),
                      "ŋ[2]": R("ikhfaa_haqiqi", "tafkheem"),
                      "q": R("tafkheem"), "aˤ:": R("madd_lazim", "tafkheem")}),
    # ق
    Case(id="qaaf", site=Site(hafs=("50:1", (1,))), read=joining(),
         phonemes="q aˤ: f", all_rules=R("madd_lazim", "tafkheem"),
         char_rules={"ق": R("madd_lazim", "tafkheem")},
         sound_rules={"q": R("tafkheem"), "aˤ:": R("madd_lazim", "tafkheem")}),
    # ن
    Case(id="noon", site=Site(hafs=("68:1", (1,))), read=joining(),
         phonemes="n u: n", all_rules=R("izhar", "madd_lazim"),
         char_rules={"ن": R("izhar", "madd_lazim")},
         sound_rules={"u:": R("madd_lazim"), "n[2]": R("izhar")}),
    # نٓ وَٱلْقَلَمِ
    VariantCase(
        id="noon-wasl",
        site=Site(hafs=("68:1", (1, 2))),
        selector=KhilafId.NOON_YASEEN_WASL,
        faces={
            "izhar": Expect(
                read=joining(),
                phonemes=("n u: n", "w a l q aˤ l a m i"),
                char_rules={"ن": R("izhar")},
                sound_rules={"n[2]": R("izhar")},
            ),
            "idgham": Expect(
                read=joining(),
                phonemes=("n u:", "w̃ a l q aˤ l a m i"),
                char_rules={"ن": R("idgham_bi_ghunnah"),
                            "و": R("idgham_bi_ghunnah")},
                sound_rules={"w̃": R("idgham_bi_ghunnah")},
            ),
        },
        default="izhar",
        masked=Expect(
            read=explicit(ibtidaa=1, waqf=1),
            phonemes=("n u: n", "w a l q aˤ l a m i"),
            char_rules={"ن": R("izhar")},
            sound_rules={"n[2]": R("izhar")},
            absent_char_rules={"ن": R("idgham_bi_ghunnah")},
        ),
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_muqattaat(run):
    assert_case(run)
