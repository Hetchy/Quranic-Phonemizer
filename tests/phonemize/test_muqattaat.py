from __future__ import annotations

import pytest

from quranic_phonemizer.model.address import KhilafId
from tests.support import (
    Case,
    Expect,
    R,
    Site,
    StateCase,
    VariantCase,
    assert_case,
    case_runs,
    explicit,
    isolated,
    joining,
    through,
)


LAM_TO_MEEM = {
    "لام/@madd": R("madd_lazim"),
    "لام/م": R("idgham_shafawi"),
    "ميم/م[1]": R("idgham_shafawi"),
    "ميم/@madd": R("madd_lazim"),
    "ميم/م[2]": R("izhar_shafawi"),
}
LAM_IZHAR = {
    "لام/@madd": R("madd_lazim"),
    "لام/م": R("izhar_shafawi"),
}
RAA = {
    "را/ر": R("tafkheem"),
    "را/@fatha": R("tafkheem"),
    "را/@madd": R("madd_tabii", "tafkheem"),
}
TAA = {
    "طا/ط": R("tafkheem"),
    "طا/@fatha": R("tafkheem"),
    "طا/@madd": R("madd_tabii", "tafkheem"),
}
SAAD = {
    "صاد/ص": R("tafkheem"),
    "صاد/@fatha": R("tafkheem"),
    "صاد/@madd": R("madd_lazim", "tafkheem"),
    "صاد/د": R("qalqala_sughra"),
}
QAAF = {
    "قاف/ق": R("tafkheem"),
    "قاف/@fatha": R("tafkheem"),
    "قاف/@madd": R("madd_lazim", "tafkheem"),
}


CASES = (
    # Hafs: الٓمٓ
    # Warsh: أَلَٓمِّٓۖ
    Case(id="alif-lam-meem", site=Site.shared("2:1", (1,)), read=joining(),
         phonemes="ʔ a l i f l a: m̃ i: m",
         all_rules=R("idgham_shafawi", "izhar_shafawi", "madd_lazim"),
         char_rules=LAM_TO_MEEM,
         sound_rules={"a:": R("madd_lazim"), "m̃": R("idgham_shafawi"),
                      "i:": R("madd_lazim"), "m": R("izhar_shafawi")}),
    # Hafs: الٓمٓصٓ
    # Warsh: اَلَٓمِّٓصَٓۖ
    Case(id="alif-lam-meem-saad", site=Site.shared("7:1", (1,)), read=joining(),
         phonemes="ʔ a l i f l a: m̃ i: m sˤ aˤ: d Q",
         all_rules=R("idgham_shafawi", "izhar_shafawi", "madd_lazim", "tafkheem", "qalqala_sughra"),
         char_rules=LAM_TO_MEEM | SAAD,
         sound_rules={"a:": R("madd_lazim"), "m̃": R("idgham_shafawi"),
                      "i:": R("madd_lazim"), "m": R("izhar_shafawi"),
                      "sˤ": R("tafkheem"), "aˤ:": R("madd_lazim", "tafkheem"),
                      "Q": R("qalqala_sughra")}),
    # Hafs: الٓر ۚ
    Case(id="alif-lam-raa", site=Site(hafs=("10:1", (1,))), read=joining(),
         phonemes="ʔ a l i f l a: m rˤ aˤ:",
         all_rules=R("izhar_shafawi", "madd_lazim", "madd_tabii", "tafkheem"),
         char_rules=LAM_IZHAR | RAA,
         sound_rules={"a:": R("madd_lazim"), "m": R("izhar_shafawi"),
                      "rˤ": R("tafkheem"), "aˤ:": R("madd_tabii", "tafkheem")}),
    # Hafs: الٓمٓر ۚ
    Case(id="alif-lam-meem-raa", site=Site(hafs=("13:1", (1,))), read=joining(),
         phonemes="ʔ a l i f l a: m̃ i: m rˤ aˤ:",
         all_rules=R("idgham_shafawi", "izhar_shafawi", "madd_lazim", "madd_tabii", "tafkheem"),
         char_rules=LAM_TO_MEEM | RAA,
         sound_rules={"a:": R("madd_lazim"), "m̃": R("idgham_shafawi"),
                      "i:": R("madd_lazim"), "m": R("izhar_shafawi"),
                      "rˤ": R("tafkheem"), "aˤ:": R("madd_tabii", "tafkheem")}),
    # Hafs: كٓهيعٓصٓ
    Case(id="kaaf-haa-yaa-ayn-saad", site=Site(hafs=("19:1", (1,))), read=joining(),
         phonemes="k a: f h a: j a: ʕ a j ŋ sˤ aˤ: d Q",
         all_rules=R("ikhfaa", "madd_lazim", "madd_tabii", "tafkheem", "qalqala_sughra"),
         char_rules={
             "كاف/@madd": R("madd_lazim"),
             "ها/@madd": R("madd_tabii"),
             "يا/@madd": R("madd_tabii"),
             "عين/ي": R("madd_lazim"),
             "عين/ن": R("ikhfaa", "tafkheem"),
         } | SAAD,
         sound_rules={"a:[1]": R("madd_lazim"), "a:[2]": R("madd_tabii"),
                      "a:[3]": R("madd_tabii"), "j[2]": R("madd_lazim"),
                      "ŋ": R("ikhfaa", "tafkheem"),
                      "sˤ": R("tafkheem"), "aˤ:": R("madd_lazim", "tafkheem"),
                      "Q": R("qalqala_sughra")}),
    # Hafs: طه
    Case(id="taa-haa", site=Site(hafs=("20:1", (1,))), read=joining(),
         phonemes="tˤ aˤ: h a:", all_rules=R("madd_tabii", "tafkheem"),
         char_rules=TAA | {"ها/@madd": R("madd_tabii")},
         sound_rules={"tˤ": R("tafkheem"), "aˤ:": R("madd_tabii", "tafkheem"),
                      "a:": R("madd_tabii")}),
    # Warsh: طَه۪ۖ
    Case(id="warsh-taa-haa-kubra-collapsed", site=Site(warsh=("20:1", (1,))),
         read=isolated(), phonemes="tˤ aˤ: h ɛ:",
         char_rules={"هي/@madd": R("imala", "madd_tabii")},
         sound_rules={"ɛ:": R("imala", "madd_tabii")},
         extra_phonemes=()),
    # Warsh: طَه۪ۖ
    Case(id="warsh-taa-haa-kubra-rendered", site=Site(warsh=("20:1", (1,))),
         read=isolated(), phonemes="tˤ aˤ: h e:",
         char_rules={"هي/@madd": R("imala", "madd_tabii")},
         sound_rules={"e:": R("imala", "madd_tabii")},
         extra_phonemes=("imala",)),
    # Hafs: طسٓمٓ
    # Warsh: طَسِٓمِّٓۖ
    Case(id="taa-seen-meem", site=Site.shared("26:1", (1,)), read=joining(),
         phonemes="tˤ aˤ: s i: m̃ i: m",
         all_rules=R("idgham_bi_ghunnah", "izhar_shafawi", "madd_tabii", "madd_lazim", "tafkheem"),
         char_rules=TAA | {
             "سين/@madd": R("madd_lazim"),
             "سين/ن": R("idgham_bi_ghunnah"),
             "ميم/م[1]": R("idgham_bi_ghunnah"),
             "ميم/@madd": R("madd_lazim"),
             "ميم/م[2]": R("izhar_shafawi"),
         },
         sound_rules={"tˤ": R("tafkheem"), "aˤ:": R("madd_tabii", "tafkheem"),
                      "i:[1]": R("madd_lazim"), "m̃": R("idgham_bi_ghunnah"),
                      "i:[2]": R("madd_lazim"), "m": R("izhar_shafawi")}),
    # Hafs: طسٓ ۚ تِلْكَ
    # Warsh: طَسِٓۖ تِلْكَ
    StateCase(
        id="taa-seen", site=Site.shared("27:1", (1, 2)),
        states={
            "joined": Expect(
                read=through(), phonemes=("tˤ aˤ: s i: ŋ", "t i l k"),
                all_rules=R("ikhfaa", "madd_tabii", "madd_lazim", "tafkheem", "waqf_diacritic_drop"),
                char_rules=TAA | {
                    "سين/@madd": R("madd_lazim"),
                    "سين/ن": R("ikhfaa"),
                },
                sound_rules={"tˤ": R("tafkheem"),
                             "aˤ:": R("madd_tabii", "tafkheem"),
                             "i:": R("madd_lazim"), "ŋ": R("ikhfaa")},
            ),
            "stopped": Expect(
                read=explicit(ibtidaa=1, waqf=1),
                phonemes=("tˤ aˤ: s i: n", "t i l k a"),
                all_rules=R("izhar", "madd_tabii", "madd_lazim", "tafkheem"),
                char_rules=TAA | {
                    "سين/@madd": R("madd_lazim"),
                    "سين/ن": R("izhar"),
                },
                sound_rules={"tˤ": R("tafkheem"),
                             "aˤ:": R("madd_tabii", "tafkheem"),
                             "i:": R("madd_lazim"), "n": R("izhar")},
            ),
        },
    ),
    # Hafs: يسٓ
    Case(id="yaa-seen", site=Site(hafs=("36:1", (1,))), read=joining(),
         phonemes="j a: s i: n", all_rules=R("izhar", "madd_tabii", "madd_lazim"),
         char_rules={"يا/@madd": R("madd_tabii"),
                     "سين/@madd": R("madd_lazim"),
                     "سين/ن": R("izhar")},
         sound_rules={"a:": R("madd_tabii"), "i:": R("madd_lazim"), "n": R("izhar")}),
    # Hafs: صٓ ۚ
    # Warsh: صَٓۖ
    Case(id="saad", site=Site.shared("38:1", (1,)), read=joining(),
         phonemes="sˤ aˤ: d Q", all_rules=R("madd_lazim", "tafkheem", "qalqala_sughra"),
         char_rules=SAAD,
         sound_rules={"sˤ": R("tafkheem"), "aˤ:": R("madd_lazim", "tafkheem"),
                      "Q": R("qalqala_sughra")}),
    # Hafs: حمٓ
    Case(id="haa-meem", site=Site(hafs=("40:1", (1,))), read=joining(),
         phonemes="ħ a: m i: m", all_rules=R("izhar_shafawi", "madd_tabii", "madd_lazim"),
         char_rules={"حا/@madd": R("madd_tabii"),
                     "ميم/@madd": R("madd_lazim"),
                     "ميم/م[2]": R("izhar_shafawi")},
         sound_rules={"a:": R("madd_tabii"), "i:": R("madd_lazim"),
                      "m[2]": R("izhar_shafawi")}),
    # Warsh: ح۪مِٓۖ
    Case(id="warsh-haa-meem", site=Site(warsh=("40:1", (1,))),
         read=isolated(), phonemes="ħ ɛ: m i: m",
         char_rules={"حا/@madd": R("taqlil", "madd_tabii")},
         sound_rules={"ɛ:": R("taqlil", "madd_tabii")}),
    # Hafs: عٓسٓقٓ
    # Warsh: عَٓسِٓقَٓۖ
    Case(id="ayn-seen-qaaf", site=Site.shared("42:2", (1,)), read=joining(),
         phonemes="ʕ a j ŋ s i: ŋ q aˤ: f",
         all_rules=R("ikhfaa", "madd_lazim", "tafkheem"),
         char_rules={"عين/ي": R("madd_lazim"),
                     "عين/ن": R("ikhfaa"),
                     "سين/@madd": R("madd_lazim"),
                     "سين/ن": R("ikhfaa", "tafkheem")} | QAAF,
         sound_rules={"j": R("madd_lazim"), "ŋ[1]": R("ikhfaa"),
                      "i:": R("madd_lazim"),
                      "ŋ[2]": R("ikhfaa", "tafkheem"),
                      "q": R("tafkheem"), "aˤ:": R("madd_lazim", "tafkheem")}),
    # Hafs: قٓ ۚ
    # Warsh: قَٓۖ
    Case(id="qaaf", site=Site.shared("50:1", (1,)), read=joining(),
         phonemes="q aˤ: f", all_rules=R("madd_lazim", "tafkheem"),
         char_rules=QAAF,
         sound_rules={"q": R("tafkheem"), "aˤ:": R("madd_lazim", "tafkheem")}),
    # Hafs: نٓ ۚ
    # Warsh: نُّٓۖ
    Case(id="noon", site=Site.shared("68:1", (1,)), read=joining(),
         phonemes="n u: n", all_rules=R("izhar", "madd_lazim"),
         char_rules={"نون/@madd": R("madd_lazim"),
                     "نون/ن[2]": R("izhar")},
         sound_rules={"u:": R("madd_lazim"), "n[2]": R("izhar")}),
    # Hafs: نٓ ۚ وَٱلْقَلَمِ
    VariantCase(
        id="noon-wasl",
        site=Site(hafs=("68:1", (1, 2))),
        selector=KhilafId.NOON_YASEEN_WASL,
        faces={
            "izhar": Expect(
                read=joining(),
                phonemes=("n u: n", "w a l q aˤ l a m i"),
                char_rules={"نون/ن[2]": R("izhar")},
                sound_rules={"n[2]": R("izhar")},
            ),
            "idgham": Expect(
                read=joining(),
                phonemes=("n u:", "w̃ a l q aˤ l a m i"),
                char_rules={"نون/ن[2]": R("idgham_bi_ghunnah"),
                            "و": R("idgham_bi_ghunnah")},
                sound_rules={"w̃": R("idgham_bi_ghunnah")},
            ),
        },
        default="izhar",
        masked=Expect(
            read=explicit(ibtidaa=1, waqf=1),
            phonemes=("n u: n", "w a l q aˤ l a m i"),
            char_rules={"نون/ن[2]": R("izhar")},
            sound_rules={"n[2]": R("izhar")},
            absent_char_rules={"نون/ن[2]": R("idgham_bi_ghunnah")},
        ),
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_muqattaat(run):
    assert_case(run)
