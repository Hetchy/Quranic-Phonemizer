from __future__ import annotations

import pytest

from tests.support import (
    Case,
    R,
    Site,
    assert_case,
    case_runs,
    explicit,
    isolated,
)


CASES = (
    # Warsh: اَرَٰٓيْتُمُۥٓ
    Case(
        id="arayta-ibdal-keeps-sakin-yaa",
        site=Site(warsh=("46:10", (2,))),
        read=isolated(),
        phonemes="ʔ a rˤ aˤ: j t u m",
    ),
    # Warsh: يُومِنُونَ
    Case(
        id="sakin-root-after-u",
        site=Site(warsh=("2:3", (2,))),
        read=isolated(),
        phonemes="j u: m i n u: n",
        char_rules={"و[1]": R("ibdal_hamza", "madd_tabii")},
        sound_rules={"u:[1]": R("ibdal_hamza", "madd_tabii")},
    ),
    # Warsh: يَالَمُونَ
    Case(
        id="sakin-root-after-a",
        site=Site(warsh=("4:104", (10,))),
        read=isolated(),
        phonemes="j a: l a m u: n",
        char_rules={"ا": R("ibdal_hamza", "madd_tabii")},
        sound_rules={"a:": R("ibdal_hamza", "madd_tabii")},
    ),
    # Warsh: مُّوَ۬جَّلاٗۖ
    Case(
        id="open-root-after-u",
        site=Site(warsh=("3:145", (10,))),
        read=isolated(),
        phonemes="m u w a ʒʒ a l a:",
        char_rules={"و": R("ibdal_hamza")},
        sound_rules={"w": R("ibdal_hamza")},
        absent_sound_rules={"w": R("madd_tabii")},
    ),
    # Warsh: بِيسَمَا
    Case(
        id="bis",
        site=Site(warsh=("2:90", (1,))),
        read=isolated(),
        phonemes="b i: s a m a:",
        char_rules={"ي": R("ibdal_hamza", "madd_tabii")},
        sound_rules={"i:": R("ibdal_hamza", "madd_tabii")},
    ),
    # Warsh: لِيَ۬لَّا
    Case(
        id="liila",
        site=Site(warsh=("2:150", (15,))),
        read=isolated(),
        phonemes="l i j a ll a:",
        char_rules={"ي": R("ibdal_hamza")},
        sound_rules={"j": R("ibdal_hamza")},
        absent_sound_rules={"j": R("madd_tabii")},
    ),
    # Warsh: اَ۬لنَّسِيُّ
    Case(
        id="nasi",
        site=Site(warsh=("9:37", (2,))),
        read=isolated(),
        phonemes="ʔ a ñ a s i jj",
        char_rules={"ي": R("ibdal_hamza")},
        sound_rules={"jj": R("ibdal_hamza")},
        absent_sound_rules={"jj": R("madd_tabii")},
    ),
    # Warsh: اُ۬لذِّيبُ
    Case(
        id="dhib",
        site=Site(warsh=("12:13", (10,))),
        read=isolated(),
        phonemes="ʔ a ðð i: b Q",
        char_rules={"ي": R("ibdal_hamza", "madd_arid_lissukun")},
        sound_rules={"i:": R("ibdal_hamza", "madd_arid_lissukun")},
    ),
    # Warsh: يَاجُوجَ
    Case(
        id="yajuj",
        site=Site(warsh=("18:94", (5,))),
        read=isolated(),
        phonemes="j a: ʒ u: ʒ Q",
        char_rules={"ا": R("ibdal_hamza", "madd_tabii")},
        sound_rules={"a:": R("ibdal_hamza", "madd_tabii")},
    ),
    # Warsh: لِاَهَبَ
    Case(
        id="lahab",
        site=Site(warsh=("19:19", (6,))),
        read=isolated(),
        phonemes="l i j a h a b Q",
        char_rules={"ا": R("ibdal_hamza")},
        sound_rules={"j": R("ibdal_hamza")},
        absent_sound_rules={"j": R("madd_tabii")},
    ),
    # Warsh: وَبِيرٖ
    Case(
        id="bir",
        site=Site(warsh=("22:45", (11,))),
        read=isolated(),
        phonemes="w a b i: r",
        char_rules={"ي": R("ibdal_hamza", "madd_arid_lissukun")},
        sound_rules={"i:": R("ibdal_hamza", "madd_arid_lissukun")},
    ),
    # Warsh: مِنسَاتَهُۥۖ
    Case(
        id="minsa",
        site=Site(warsh=("34:14", (13,))),
        read=isolated(),
        phonemes="m i ŋ s a: t a h",
        char_rules={"ا": R("ibdal_hamza", "madd_tabii")},
        sound_rules={"a:": R("ibdal_hamza", "madd_tabii")},
    ),
    # Warsh: سَالَ
    Case(
        id="saal",
        site=Site(warsh=("70:1", (1,))),
        read=isolated(),
        phonemes="s a: l",
        char_rules={"ا": R("ibdal_hamza", "madd_arid_lissukun")},
        sound_rules={"a:": R("ibdal_hamza", "madd_arid_lissukun")},
    ),
    # Warsh: اِ۬لذِے اِ۟وتُمِنَ
    Case(
        id="joined-silent-qata",
        site=Site(warsh=("2:283", (15, 16))),
        read=explicit(ibtidaa=15, waqf=16),
        phonemes=("ʔ a ll a ð", "i: t u m i n"),
        char_rules={"و": R("ibdal_hamza")},
        sound_rules={"i:": R("ibdal_hamza", "madd_tabii")},
        absent_char_rules={"ل": R("lam_shamsiyyah")},
        absent_sound_rules={"ʔ": R("ibdal_hamza"), "ll": R("lam_shamsiyyah")},
    ),
    # Warsh: وَمَأْو۪يٰهُمُ
    Case(
        id="tahqiq-mawahum",
        site=Site(warsh=("3:151", (15,))),
        read=isolated(),
        phonemes="w a m a ʔ w ɛ: h u m",
        absent_char_rules={"أ": R("ibdal_hamza")},
        absent_sound_rules={"ʔ": R("ibdal_hamza")},
    ),
    # Warsh: وَمَأْو۪يٰكُمُ
    Case(
        id="tahqiq-mawakum",
        site=Site(warsh=("29:25", (22,))),
        read=isolated(),
        phonemes="w a m a ʔ w ɛ: k u m",
        absent_char_rules={"أ": R("ibdal_hamza")},
        absent_sound_rules={"ʔ": R("ibdal_hamza")},
    ),
    # Warsh: فَأْوُۥٓاْ
    Case(
        id="tahqiq-fawu",
        site=Site(warsh=("18:16", (7,))),
        read=isolated(),
        phonemes="f a ʔ w u:",
        absent_char_rules={"أ": R("ibdal_hamza")},
        absent_sound_rules={"ʔ": R("ibdal_hamza")},
    ),
    # Warsh: اُ۬لْمَأْو۪ىٰ
    Case(
        id="tahqiq-almawa",
        site=Site(warsh=("32:19", (8,))),
        read=isolated(),
        phonemes="ʔ a l m a ʔ w ɛ:",
        char_rules={"ى": R("taqlil", "madd_tabii")},
        sound_rules={"ɛ:": R("taqlil", "madd_tabii")},
        absent_char_rules={"أ": R("ibdal_hamza")},
        absent_sound_rules={"ʔ[2]": R("ibdal_hamza")},
    ),
    # Warsh: وَتُـْٔوِےٓ
    Case(
        id="tahqiq-tuwi",
        site=Site(warsh=("33:51", (5,))),
        read=isolated(),
        phonemes="w a t u ʔ w i:",
        absent_char_rules={"@hamza_mark": R("ibdal_hamza")},
        absent_sound_rules={"ʔ": R("ibdal_hamza")},
    ),
    # Warsh: تُـْٔوِيهِ
    Case(
        id="tahqiq-tuwihi",
        site=Site(warsh=("70:13", (3,))),
        read=isolated(),
        phonemes="t u ʔ w i: h",
        absent_char_rules={"@hamza_mark": R("ibdal_hamza")},
        absent_sound_rules={"ʔ": R("ibdal_hamza")},
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_warsh_single_hamza(run):
    assert_case(run)
