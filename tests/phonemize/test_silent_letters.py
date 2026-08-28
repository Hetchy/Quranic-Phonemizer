from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated, pick


CASES = (
    # Hafs: أُو۟لَـٰٓئِكَ
    # Warsh: أُوْلَٰٓئِكَ
    Case(
        id="ulaika-waw",
        site=Site.shared("2:5", (1,)),
        read=isolated(),
        phonemes="ʔ u l a: ʔ i k",
        char_rules={"و": R("orthographic_silence")},
    ),
    # Hafs: وَأُو۟لَـٰٓئِكَ
    # Warsh: وَأُوْلَٰٓئِكَ
    Case(
        id="waulaika-waw",
        site=Site.shared("2:5", (6,)),
        read=isolated(),
        phonemes="w a ʔ u l a: ʔ i k",
        char_rules={"و[2]": R("orthographic_silence")},
    ),
    # Hafs: أُو۟لُوا۟
    # Warsh: أُوْلُواْ
    Case(
        id="ulu-plural-waw",
        site=Site.shared("27:33", (3,)),
        read=isolated(),
        phonemes="ʔ u l u:",
        char_rules={"و[1]": R("orthographic_silence")},
    ),
    # Hafs: خَلَقُوا۟
    # Warsh: خَلَقُواْ
    Case(
        id="plural-waw-long",
        site=Site.shared("46:4", (10,)),
        read=isolated(),
        phonemes="x aˤ l a q u:",
        char_rules={"ا": R("orthographic_silence")},
    ),
    # Hafs: خَلَوْا۟
    # Warsh: خَلَوِاْ
    Case(
        id="plural-waw-leen",
        site=Site.shared("2:14", (8,)),
        read=isolated(),
        phonemes="x aˤ l a w",
        char_rules={"ا": R("orthographic_silence")},
    ),
    # Hafs: ٱشْتَرَوُا۟
    # Warsh: اَ۪شْتَرَوُاْ
    Case(
        id="plural-waw-short",
        site=Site.shared("2:16", (3,)),
        read=isolated(),
        phonemes="ʔ i ʃ t a rˤ aˤ w",
        char_rules=pick(
            hafs_uthmani={"ا": R("orthographic_silence")},
            hafs_indopak={"ا[2]": R("orthographic_silence")},
            warsh_uthmani={"ا[2]": R("orthographic_silence")},
        ),
    ),
    # Hafs: مِا۟ئَةَ
    # Warsh: مِاْئَةَ
    Case(
        id="miata-alif",
        site=Site.shared("2:259", (19,)),
        read=isolated(),
        phonemes="m i ʔ a h",
        char_rules={"ا": R("orthographic_silence")},
    ),
    # Hafs: مِّا۟ئَةُ
    # Warsh: مِّاْئَةُ
    Case(
        id="miata-geminated-alif",
        site=Site.shared("2:261", (16,)),
        read=isolated(),
        phonemes="m i ʔ a h",
        char_rules={"ا": R("orthographic_silence")},
    ),
    # Hafs: يَبْدَؤُا۟
    # Warsh: يَبْدَؤُاْ
    Case(
        id="yabdau-final-alif",
        site=Site.shared("10:4", (8,)),
        read=isolated(),
        phonemes="j a b Q d a ʔ",
        char_rules={"ا": R("orthographic_silence")},
    ),
    # Hafs: ٱلرِّبَوٰا۟ ۗ
    # Warsh: اُ۬لرِّبَوٰاْۖ
    Case(
        id="arriba-final-alif",
        site=Site.shared("2:275", (20,)),
        read=isolated(),
        phonemes="ʔ a rr i b a:",
        char_rules=pick(
            hafs_uthmani={"ا": R("orthographic_silence")},
            hafs_indopak={},
            warsh_uthmani={"ا[2]": R("orthographic_silence")},
        ),
    ),
    # Hafs: بِأَيْي۟دٍ
    # Warsh: بِأَيَيْدٖۖ
    Case(
        id="biaydin-second-yaa",
        site=Site.shared("51:47", (3,)),
        read=isolated(),
        phonemes="b i ʔ a j d Q",
        char_rules=pick(
            hafs_uthmani={"ي[2]": R("orthographic_silence")},
            hafs_indopak={"ى": R("orthographic_silence")},
            warsh_uthmani={"ي[2]": R("orthographic_silence")},
        ),
    ),
    # Hafs: أَفَإِي۟ن
    # Warsh: أَفَإِيْن
    Case(
        id="afain-yaa",
        site=Site.shared("3:144", (10,)),
        read=isolated(),
        phonemes="ʔ a f a ʔ i n",
        char_rules=pick(
            hafs_uthmani={"ي": R("orthographic_silence")},
            hafs_indopak={"ى": R("orthographic_silence")},
            warsh_uthmani={"ي": R("orthographic_silence")},
        ),
    ),
    # Hafs: وَمَلَإِي۟هِۦ
    # Warsh: وَمَلَإِيْهِۦ
    Case(
        id="wamalaihi-yaa",
        site=Site.shared("7:103", (9,)),
        read=isolated(),
        phonemes="w a m a l a ʔ i h",
        char_rules=pick(
            hafs_uthmani={"ي": R("orthographic_silence")},
            hafs_indopak={"ى": R("orthographic_silence")},
            warsh_uthmani={"ي": R("orthographic_silence")},
        ),
    ),
    # Hafs: نَّبَإِى۟
    # Warsh: نَّبَإِےْ
    Case(
        id="nabai-final-yaa",
        site=Site.shared("6:34", (21,)),
        read=isolated(),
        phonemes="n a b a ʔ",
        char_rules=pick(
            hafs_uthmani={"ى": R("orthographic_silence")},
            hafs_indopak={"ي": R("orthographic_silence")},
            warsh_uthmani={"ے": R("orthographic_silence")},
        ),
    ),
    # Hafs: تَا۟يْـَٔسُوا۟
    # Warsh: تَاْيْـَٔسُواْ
    Case(
        id="tayasu-alif",
        site=Site.shared("12:87", (8,)),
        read=isolated(),
        phonemes="t a j ʔ a s u:",
        char_rules={"ا[1]": R("orthographic_silence")},
    ),
    # Hafs: يَا۟يْـَٔسِ
    # Warsh: يَاْيْـَٔسِ
    Case(
        id="yayasi-alif",
        site=Site.shared("13:31", (20,)),
        read=isolated(),
        phonemes="j a j ʔ a s",
        char_rules={"ا": R("orthographic_silence")},
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_silent_letters(run):
    assert_case(run)
