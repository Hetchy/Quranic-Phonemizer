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
    isolated,
    through,
)

CASES = (
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


VARIANT_CASES = (
    # Warsh: اَرَٰٓيْتُمُۥٓ
    VariantCase(
        id="arayta-faces",
        site=Site(warsh=("46:10", (2,))),
        selector=KhilafId.HAMZA_ARAYTA,
        faces={
            "ibdal": Expect(
                read=isolated(),
                phonemes="ʔ a rˤ aˤ: j t u m",
                sound_rules={
                    "aˤ:": R("ibdal_hamza", "madd_lazim", "tafkheem"),
                },
            ),
            "tashil": Expect(
                read=isolated(),
                phonemes="ʔ a rˤ aˤ ʔ̞ a j t u m",
                sound_rules={"ʔ̞": R("tashil"), "aˤ": R("tafkheem")},
                absent_sound_rules={"ʔ̞": R("ibdal_hamza")},
            ),
        },
        default="ibdal",
    ),
    # Warsh: اَرَٰٓيْتَ
    VariantCase(
        id="arayta-bare-waqf-mask",
        site=Site(warsh=("107:1", (1, 2))),
        selector=KhilafId.HAMZA_ARAYTA,
        faces={
            "ibdal": Expect(
                read=explicit(ibtidaa=1, wasl=1, waqf=2),
                phonemes=("ʔ a rˤ aˤ: j t a", "ll a ð i:"),
                sound_rules={"aˤ:": R("ibdal_hamza", "madd_lazim")},
            ),
            "tashil": Expect(
                read=explicit(ibtidaa=1, wasl=1, waqf=2),
                phonemes=("ʔ a rˤ aˤ ʔ̞ a j t a", "ll a ð i:"),
                sound_rules={"ʔ̞": R("tashil")},
            ),
        },
        default="ibdal",
        masked=Expect(
            read=explicit(ibtidaa=1, waqf=(1, 2)),
            phonemes=("ʔ a rˤ aˤ ʔ̞ a j t", "ʔ a ll a ð i:"),
            sound_rules={"ʔ̞": R("tashil")},
            absent_sound_rules={"ʔ̞": R("ibdal_hamza")},
        ),
    ),
    # Warsh: هَآنتُمْ
    VariantCase(
        id="ha-antum-three-faces",
        site=Site(warsh=("3:66", (1,))),
        selector=KhilafId.HA_ANTUM,
        faces={
            "ibdal": Expect(
                read=isolated(),
                phonemes="h a: ŋ t u m",
                sound_rules={
                    "a:": R("ibdal_hamza", "madd_lazim"),
                    "ŋ": R("ikhfaa"),
                },
            ),
            "ithbat": Expect(
                read=isolated(),
                phonemes="h a: ʔ̞ a ŋ t u m",
                sound_rules={
                    "a:": R("madd_munfasil"),
                    "ʔ̞": R("tashil"),
                    "ŋ": R("ikhfaa"),
                },
            ),
            "hadhf": Expect(
                read=isolated(),
                phonemes="h a ʔ̞ a ŋ t u m",
                sound_rules={"ʔ̞": R("tashil"), "ŋ": R("ikhfaa")},
            ),
        },
        default="ibdal",
    ),
    # Warsh: اُ۬ل۪ےْ
    VariantCase(
        id="allai-waqf-faces",
        site=Site(warsh=("33:4", (12, 13))),
        selector=KhilafId.ALLAI_WAQF,
        faces={
            "tashil": Expect(
                read=explicit(ibtidaa=12, waqf=(12, 13)),
                phonemes=("ʔ a ll ɛ: ʔ̞ i", "t a ðˤðˤ aˤ hh a rˤ u: n"),
                sound_rules={
                    "ɛ:": R("madd_muttasil", "taqlil"),
                    "ʔ̞": R("tashil"),
                },
            ),
            "ibdal_yaa": Expect(
                read=explicit(ibtidaa=12, waqf=(12, 13)),
                phonemes=("ʔ a ll ɛ: j", "t a ðˤðˤ aˤ hh a rˤ u: n"),
                sound_rules={
                    "ɛ:": R("madd_lazim", "taqlil"),
                    "j": R("ibdal_hamza"),
                },
            ),
        },
        default="tashil",
        masked=Expect(
            read=explicit(ibtidaa=12, wasl=12, waqf=13),
            phonemes=("ʔ a ll ɛ: ʔ̞ i", "t a ðˤðˤ aˤ hh a rˤ u: n"),
            sound_rules={"ʔ̞": R("tashil")},
            absent_sound_rules={"ʔ̞": R("ibdal_hamza")},
        ),
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_warsh_single_hamza(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(VARIANT_CASES))
def test_warsh_single_hamza_selectors(run):
    assert_case(run)


def _register_rows():
    from quranic_phonemizer.riwayat.warsh.single_hamza import (
        authored_locations,
    )

    rows = []
    for name, khilaf, options, stopped in (
        ("arayta", KhilafId.HAMZA_ARAYTA, ("ibdal", "tashil"), False),
        ("ha_antum", KhilafId.HA_ANTUM, ("hadhf", "ibdal", "ithbat"), True),
        ("allai", KhilafId.ALLAI_WAQF, ("tashil", "ibdal_yaa"), True),
    ):
        for location in sorted(
            authored_locations(name),
            key=lambda item: (item.surah, item.ayah, item.word),
        ):
            rows.append(pytest.param(
                khilaf, options, f"{location.surah}:{location.ayah}",
                location.word, stopped,
                id=f"{name}-{location}",
            ))
    return tuple(rows)


@pytest.mark.parametrize(
    ("khilaf", "options", "verse", "word", "stopped"), _register_rows()
)
def test_every_single_hamza_selector_site_separates_its_faces(
    khilaf, options, verse, word, stopped
):
    from tests.support import selected

    site = Site(warsh=(verse, (word,)))
    faces = {
        option: tuple(
            selected(site, word, khilaf, option, stopped=stopped,
                     riwayah="warsh").sounds(word)
        )
        for option in options
    }
    assert len(set(faces.values())) == len(options)
