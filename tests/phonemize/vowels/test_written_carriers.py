from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated, pick

CASES = (
    # Warsh: وَمَحْي۪آےْ
    Case(
        id="mahyaya-selected-sakin-yaa",
        site=Site(warsh=("6:162", (5,))),
        read=isolated(),
        phonemes="w a m a ħ j ɛ: j",
    ),
    # Hafs: ٱلصَّلَوٰةَ
    # Warsh: اَ۬لصَّلَوٰةَ
    Case(
        id="salah-waw-carrier",
        site=Site.shared("2:3", (5,)),
        read=isolated(),
        phonemes=pick(
            hafs="ʔ a sˤsˤ aˤ l a: h",
            warsh="ʔ a sˤsˤ aˤ lˤ aˤ: h",
        ),
        char_rules=pick(
            hafs_uthmani={"@dagger_alif": R("madd_arid_lissukun")},
            hafs_indopak={"و": R("madd_arid_lissukun")},
            warsh_uthmani={
                "@dagger_alif": R("madd_arid_lissukun", "tafkheem"),
                "ل[2]": R("tafkheem"),
            },
        ),
        sound_rules=pick(
            hafs={"a:": R("madd_arid_lissukun")},
            warsh={
                "lˤ": R("tafkheem"),
                "aˤ:": R("madd_arid_lissukun", "tafkheem"),
            },
        ),
    ),
    # Hafs: ٱلزَّكَوٰةَ
    # Warsh: اُ۬لزَّكَوٰةَۖ
    Case(
        id="zakah-waw-carrier",
        site=Site.shared("2:43", (4,)),
        read=isolated(),
        phonemes="ʔ a zz a k a: h",
        char_rules=pick(
            hafs_uthmani={"@dagger_alif": R("madd_arid_lissukun")},
            hafs_indopak={"و": R("madd_arid_lissukun")},
            warsh_uthmani={"@dagger_alif": R("madd_arid_lissukun")},
        ),
        sound_rules={"a:": R("madd_arid_lissukun")},
    ),
    # Hafs: ٱلْحَيَوٰةَ
    # Warsh: اُ۬لْحَيَوٰةَ
    Case(
        id="hayah-waw-carrier",
        site=Site.shared("2:86", (4,)),
        read=isolated(),
        phonemes="ʔ a l ħ a j a: h",
        char_rules=pick(
            hafs_uthmani={"@dagger_alif": R("madd_arid_lissukun")},
            hafs_indopak={"و": R("madd_arid_lissukun")},
            warsh_uthmani={"@dagger_alif": R("madd_arid_lissukun")},
        ),
        sound_rules={"a:": R("madd_arid_lissukun")},
    ),
    # Hafs: صَلَوَٰتٌ
    # Warsh: صَلَوَٰتٞ
    Case(
        id="salawat-sounded-waw",
        site=Site.shared("2:157", (3,)),
        read=isolated(),
        phonemes=pick(
            hafs="sˤ aˤ l a w a: t",
            warsh="sˤ aˤ lˤ aˤ w a: t",
        ),
        char_rules={"@dagger_alif": R("madd_arid_lissukun")},
        sound_rules={"a:": R("madd_arid_lissukun")},
    ),
    # Hafs: قَالُوٓا۟
    # Warsh: قَالُوٓاْ
    Case(
        id="qalu-plural-alif",
        site=Site.shared("2:11", (8,)),
        read=isolated(),
        phonemes="q aˤ: l u:",
        char_rules={"ا[2]": R("orthographic_silence")},
    ),
    # Hafs: ذَٰلِكَ
    # Warsh: ذَٰلِكَ
    Case(
        id="dagger-alif",
        site=Site.shared("2:2", (1,)),
        read=isolated(),
        phonemes="ð a: l i k",
        char_rules={"@dagger_alif": R("madd_tabii")},
        sound_rules={"a:": R("madd_tabii")},
    ),
    # Hafs: مُوسَىٰٓ
    Case(
        id="maqsura-dagger-carrier",
        site=Site(hafs=("2:51", (3,))),
        read=isolated(),
        phonemes="m u: s a:",
        char_rules=pick(
            hafs_uthmani={"@dagger_alif": R("madd_tabii")},
            hafs_indopak={"ي": R("madd_tabii")},
        ),
        sound_rules={"a:": R("madd_tabii")},
    ),
    # Hafs: فَٱدَّٰرَْٰٔتُمْ
    # Warsh: فَادَّٰرَٰءْتُمْ
    Case(
        id="iddaratum-two-daggers",
        site=Site.shared("2:72", (4,)),
        read=isolated(),
        phonemes="f a dd a: rˤ aˤ ʔ t u m",
        char_rules=pick(
            hafs_uthmani={
                "@dagger_alif[1]": R("madd_tabii"),
                "@dagger_alif[2]": R("orthographic_silence"),
            },
            hafs_indopak={"@dagger_alif": R("madd_tabii")},
            warsh_uthmani={
                "@dagger_alif[1]": R("madd_tabii"),
                "@dagger_alif[2]": R("orthographic_silence"),
            },
        ),
        sound_rules={"a:": R("madd_tabii")},
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_written_carriers(run):
    assert_case(run)
