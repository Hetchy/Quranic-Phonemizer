from __future__ import annotations

import pytest

from quranic_phonemizer.model.address import KhilafId
from quranic_phonemizer.riwayat.warsh.raa import (
    SELECTOR_JUNCTIONS,
    SELECTOR_SITES,
)
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
from tests.support.variant import selected

MOVING_STRUCTURAL_CASES = (
    # Warsh: قِرَدَةً
    Case(
        id="direct-original-kasra",
        site=Site(warsh=("2:65", (11,))),
        read=isolated(),
        phonemes="q i r a d a h",
        char_rules={"ر": R("tarqeeq")},
        sound_rules={"r": R("tarqeeq"), "a[1]": R("tarqeeq")},
    ),
    # Warsh: اُ۬لْخَيْرَٰتِۖ
    Case(
        id="sakin-yaa-and-carrier-coloring",
        site=Site(warsh=("2:148", (6,))),
        read=isolated(),
        phonemes="ʔ a l x aˤ j r a: t",
        char_rules={
            "ر": R("tarqeeq"),
            "@dagger_alif": R("tarqeeq", "madd_arid_lissukun"),
        },
        sound_rules={
            "r": R("tarqeeq"),
            "a:": R("tarqeeq", "madd_arid_lissukun"),
        },
        extra_phonemes=("emphatic_fatha",),
    ),
    # Warsh: ذِكْرَ رَبِّهِۦ
    Case(
        id="one-sakin-extension",
        site=Site(warsh=("12:42", (12, 13))),
        read=through(),
        phonemes=("ð i k r a", "rˤ aˤ bb i h"),
        char_rules={"ر[1]": R("tarqeeq")},
        sound_rules={"r": R("tarqeeq"), "a": R("tarqeeq")},
        extra_phonemes=("emphatic_fatha",),
    ),
    # Warsh: إِخْرَاجُهُمُۥٓۖ
    Case(
        id="khaa-intervening-exception",
        site=Site(warsh=("2:85", (22,))),
        read=isolated(),
        phonemes="ʔ i x r a: ʒ u h u m",
        char_rules={"ر": R("tarqeeq"), "ا": R("tarqeeq")},
        sound_rules={"r": R("tarqeeq"), "a:": R("tarqeeq")},
    ),
    # Warsh: قِطْراٗۖ
    Case(
        id="intervening-isti-laa-blocker",
        site=Site(warsh=("18:96", (19,))),
        read=isolated(),
        phonemes="q i tˤ Q rˤ aˤ:",
        char_rules={
            "ر": R("tafkheem"),
            "ا": R("tafkheem", "madd_iwad", "madd_tabii"),
        },
        sound_rules={
            "rˤ": R("tafkheem"),
            "aˤ:": R("tafkheem", "madd_iwad", "madd_tabii"),
        },
    ),
    # Warsh: لِرُقِيِّكَ
    Case(
        id="following-isti-laa-blocker",
        site=Site(warsh=("17:93", (13,))),
        read=isolated(),
        phonemes="l i rˤ u q i jj i k",
        char_rules={"ر": R("tafkheem")},
        sound_rules={"rˤ": R("tafkheem")},
    ),
    # Warsh: رَبِّهِۦ
    Case(
        id="ordinary-open-heavy",
        site=Site(warsh=("12:42", (13,))),
        read=isolated(),
        phonemes="rˤ aˤ bb i h",
        char_rules={"ر": R("tafkheem")},
        sound_rules={"rˤ": R("tafkheem"), "aˤ": R("tafkheem")},
    ),
)


SAKIN_AND_BOUNDARY_CASES = (
    # Warsh: خَيْرَ اَ۬لزَّادِ
    StateCase(
        id="final-open-raa-recomputed-at-waqf",
        site=Site(warsh=("2:197", (24, 25))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("x aˤ j r a", "zz a: d Q"),
                char_rules={"ر": R("tarqeeq")},
                sound_rules={"r": R("tarqeeq"), "a": R("tarqeeq")},
                extra_phonemes=("emphatic_fatha",),
            ),
            "stopped": Expect(
                read=explicit(ibtidaa=24, waqf=(24, 25)),
                phonemes=("x aˤ j r", "ʔ a zz a: d Q"),
                char_rules={"ر": R("tarqeeq")},
                sound_rules={"r": R("tarqeeq")},
                extra_phonemes=("emphatic_fatha",),
            ),
        },
    ),
    # Warsh: وَاذْكُرْ فِے
    Case(
        id="sakin-raa-governed-by-damma",
        site=Site(warsh=("19:16", (1, 2))),
        read=through(),
        phonemes=("w a ð k u rˤ", "f i:"),
        char_rules={"ر": R("tafkheem")},
        sound_rules={"rˤ": R("tafkheem")},
    ),
    # Warsh: اِ۪رْتَبْتُمْ
    Case(
        id="wasl-start-kasra-is-not-original",
        site=Site(warsh=("5:106", (35,))),
        read=isolated(),
        phonemes="ʔ i rˤ t a b Q t u m",
        char_rules={"ر": R("tafkheem")},
        sound_rules={"rˤ": R("tafkheem")},
    ),
    # Warsh: اَمِ اِ۪رْتَابُوٓاْ
    Case(
        id="cross-word-kasra-is-not-original",
        site=Site(warsh=("24:50", (4, 5))),
        read=through(),
        phonemes=("ʔ a m i", "rˤ t a: b u:"),
        char_rules={"ر": R("tafkheem")},
        sound_rules={"rˤ": R("tafkheem")},
    ),
)


FIXED_LEXICAL_EXCLUSION_CASES = (
    # Warsh: إِسْرَآءِيلَ
    Case(
        id="israil-fixed-heavy",
        site=Site(warsh=("2:40", (2,))),
        read=isolated(),
        phonemes="ʔ i s rˤ aˤ: ʔ i: l",
        char_rules={"ر": R("tafkheem"), "ا": R("tafkheem", "madd_muttasil")},
        sound_rules={"rˤ": R("tafkheem"), "aˤ:": R("tafkheem", "madd_muttasil")},
    ),
    # Warsh: إِبْرَٰهِيمَ
    Case(
        id="ibrahim-fixed-heavy",
        site=Site(warsh=("2:125", (10,))),
        read=isolated(),
        phonemes="ʔ i b Q rˤ aˤ: h i: m",
        char_rules={
            "ر": R("tafkheem"),
            "@dagger_alif": R("tafkheem", "madd_tabii"),
        },
        sound_rules={
            "rˤ": R("tafkheem"),
            "aˤ:": R("tafkheem", "madd_tabii"),
        },
    ),
    # Warsh: عِمْرَٰنَ
    Case(
        id="imran-fixed-heavy",
        site=Site(warsh=("3:33", (9,))),
        read=isolated(),
        phonemes="ʕ i m rˤ aˤ: n",
        char_rules={
            "ر": R("tafkheem"),
            "@dagger_alif": R("tafkheem", "madd_arid_lissukun"),
        },
        sound_rules={
            "rˤ": R("tafkheem"),
            "aˤ:": R("tafkheem", "madd_arid_lissukun"),
        },
    ),
    # Warsh: ضِرَاراٗ
    Case(
        id="repeated-raa-fixed-heavy",
        site=Site(warsh=("2:231", (13,))),
        read=isolated(),
        phonemes="dˤ i rˤ aˤ: rˤ aˤ:",
        char_rules={"ر[1]": R("tafkheem"), "ر[2]": R("tafkheem")},
        sound_rules={"rˤ[1]": R("tafkheem"), "rˤ[2]": R("tafkheem")},
        extra_phonemes=("emphatic_fatha",),
    ),
    # Warsh: حِذْرَهُمْ
    Case(
        id="hidhrahum-fixed-light",
        site=Site(warsh=("4:102", (26,))),
        read=isolated(),
        phonemes="ħ i ð r a h u m",
        char_rules={"ر": R("tarqeeq")},
        sound_rules={"r": R("tarqeeq"), "a": R("tarqeeq")},
    ),
    # Warsh: اَ۬لْعَشِيرُۖ
    Case(
        id="other-ashir-fixed-light",
        site=Site(warsh=("22:13", (10,))),
        read=isolated(),
        phonemes="ʔ a l ʕ a ʃ i: r",
        char_rules={"ر": R("tarqeeq")},
        sound_rules={"r": R("tarqeeq")},
    ),
    # Warsh: فَاحْذَرْهُمْۖ
    Case(
        id="hidhrahum-lookalike-keeps-structural-weight",
        site=Site(warsh=("63:4", (18,))),
        read=isolated(),
        phonemes="f a ħ ð a rˤ h u m",
        char_rules={"ر": R("tafkheem")},
        sound_rules={"rˤ": R("tafkheem")},
    ),
)


def _face(read, phonemes, rule, char="ر", sound=None, extra=("emphatic_fatha",)):
    if sound is None:
        sound = "rˤ" if rule == "tafkheem" else "r"
    return Expect(
        read=read,
        phonemes=phonemes,
        char_rules={char: R(rule)},
        sound_rules={sound: R(rule)},
        extra_phonemes=extra,
    )


def _word_case(case_id, site, selector, heavy, light, default, masked=None):
    return VariantCase(
        id=case_id,
        site=site,
        selector=selector,
        faces={
            "heavy": _face(isolated(), heavy, "tafkheem"),
            "light": _face(isolated(), light, "tarqeeq"),
        },
        default=default,
        masked=masked,
    )


LEXICAL_VARIANT_CASES = (
    # Warsh: فِرْقٖ
    _word_case("firq", Site(warsh=("26:63", (11,))), KhilafId.RAA_FIRQ,
               "f i rˤ q Q", "f i r q Q", "light"),
    # Warsh: اَ۬لْقِطْرِۖ
    _word_case("alqitr", Site(warsh=("34:12", (10,))), KhilafId.RAA_ALQITR_WAQF,
               "ʔ a l q i tˤ Q rˤ", "ʔ a l q i tˤ Q r", "light",
               masked=_face(joining(), "ʔ a l q i tˤ Q r i", "tarqeeq")),
    # Warsh: مِصْرَ
    _word_case("misr", Site(warsh=("12:99", (10,))), KhilafId.RAA_MISR_WAQF,
               "m i sˤ rˤ", "m i sˤ r", "heavy",
               masked=_face(joining(), "m i sˤ rˤ aˤ", "tafkheem")),
    # Warsh: وَنُذُرِۦۖ
    _word_case("wanuthur", Site(warsh=("54:16", (4,))),
               KhilafId.RAA_WANUTHUR_WAQF,
               "w a n u ð u rˤ", "w a n u ð u r", "light",
               masked=_face(joining(), "w a n u ð u r i:", "tarqeeq")),
    # Warsh: يَسْرِۦ
    _word_case("yasr", Site(warsh=("89:4", (3,))), KhilafId.RAA_YASR_WAQF,
               "j a s rˤ", "j a s r", "light",
               masked=_face(joining(), "j a s r i:", "tarqeeq")),
    # Warsh: فَاسْرِ
    _word_case("asr", Site(warsh=("11:81", (9,))), KhilafId.RAA_ASR_WAQF,
               "f a s rˤ", "f a s r", "heavy",
               masked=_face(joining(), "f a s r i", "tarqeeq")),
    # Warsh: عِشْرُونَ
    _word_case("ishruna", Site(warsh=("8:65", (10,))),
               KhilafId.RAA_ISHRUNA_KIBR,
               "ʕ i ʃ rˤ u: n", "ʕ i ʃ r u: n", "light"),
    # Warsh: وَالِاشْرَاقِ
    _word_case("alishraq", Site(warsh=("38:18", (7,))), KhilafId.RAA_ALISHRAQ,
               "w a l i ʃ rˤ aˤ: q Q", "w a l i ʃ r a: q Q", "heavy"),
    # Warsh: حَيْرَانَۖ
    _word_case("hayran", Site(warsh=("6:71", (23,))), KhilafId.RAA_HAYRAN,
               "ħ a j rˤ aˤ: n", "ħ a j r a: n", "heavy"),
    # Warsh: ذِكْراٗۖ
    _word_case("five-words", Site(warsh=("2:200", (10,))),
               KhilafId.RAA_FIVE_WORDS,
               "ð i k rˤ aˤ:", "ð i k r a:", "heavy"),
    # Warsh: وَصِهْراٗۖ
    _word_case("sihra", Site(warsh=("25:54", (9,))), KhilafId.RAA_SIHRA,
               "w a sˤ i h rˤ aˤ:", "w a sˤ i h r a:", "heavy"),
    # Warsh: اِرَمَ
    _word_case("iram", Site(warsh=("89:7", (1,))), KhilafId.RAA_IRAM,
               "ʔ i rˤ aˤ m", "ʔ i r a m", "heavy"),
    # Warsh: ذِرَاعَيْهِ
    _word_case("alif-ayn", Site(warsh=("18:18", (12,))), KhilafId.RAA_ALIF_AYN,
               "ð i rˤ aˤ: ʕ a j h", "ð i r a: ʕ a j h", "light"),
    # Warsh: مِرَآءٗ
    _word_case("alif-hamza", Site(warsh=("18:22", (27,))),
               KhilafId.RAA_ALIF_HAMZA,
               "m i rˤ aˤ: ʔ a:", "m i r a: ʔ a:", "light"),
    # Warsh: لَسَٰحِرَٰنِ
    _word_case("dual-alif", Site(warsh=("20:63", (4,))), KhilafId.RAA_DUAL_ALIF,
               "l a s a: ħ i rˤ aˤ: n", "l a s a: ħ i r a: n", "light"),
    # Warsh: وَعَشِيرَتُكُمْ
    _word_case("ashiratukum", Site(warsh=("9:24", (8,))),
               KhilafId.RAA_ASHIRATUKUM,
               "w a ʕ a ʃ i: rˤ aˤ t u k u m",
               "w a ʕ a ʃ i: r a t u k u m", "light"),
    # Warsh: وِزْرَكَ
    _word_case("wizraka", Site(warsh=("94:2", (3,))), KhilafId.RAA_WIZRAKA,
               "w i z rˤ aˤ k", "w i z r a k", "light"),
    # Warsh: ذِكْرَكَۖ
    _word_case("dhikraka", Site(warsh=("94:4", (3,))), KhilafId.RAA_DHIKRAKA,
               "ð i k rˤ aˤ k", "ð i k r a k", "light"),
    # Warsh: إِجْرَامِے
    _word_case("ijrami", Site(warsh=("11:35", (8,))), KhilafId.RAA_IJRAMI,
               "ʔ i ʒ Q rˤ aˤ: m i:", "ʔ i ʒ Q r a: m i:", "light"),
    # Warsh: حِذْرَكُمْ
    _word_case("hidhrakum", Site(warsh=("4:71", (5,))), KhilafId.RAA_HIDHRAKUM,
               "ħ i ð rˤ aˤ k u m", "ħ i ð r a k u m", "light"),
    # Warsh: لَعِبْرَةٗ
    _word_case("ibrah", Site(warsh=("3:13", (27,))),
               KhilafId.RAA_IBRAH_KIBRAHU,
               "l a ʕ i b Q rˤ aˤ h", "l a ʕ i b Q r a h", "light"),
)


SYSTEMATIC_AND_PAIR_VARIANT_CASES = (
    # Warsh: خَيْراٗ فَإِنَّ
    VariantCase(
        id="fathatan-joined",
        site=Site(warsh=("2:158", (20, 21))),
        selector=KhilafId.RAA_FATHATAN,
        faces={
            "light": _face(
                through(), ("x aˤ j r a ŋ", "f a ʔ i ñ"), "tarqeeq"),
            "heavy_wasl": _face(
                through(), ("x aˤ j rˤ aˤ ŋ", "f a ʔ i ñ"), "tafkheem"),
            "heavy": _face(
                through(), ("x aˤ j rˤ aˤ ŋ", "f a ʔ i ñ"), "tafkheem"),
        },
        default="light",
    ),
    # Warsh: خَيْراٗ
    VariantCase(
        id="fathatan-waqf",
        site=Site(warsh=("2:158", (20,))),
        selector=KhilafId.RAA_FATHATAN,
        faces={
            "light": _face(isolated(), "x aˤ j r a:", "tarqeeq"),
            "heavy_wasl": _face(isolated(), "x aˤ j r a:", "tarqeeq"),
            "heavy": _face(isolated(), "x aˤ j rˤ aˤ:", "tafkheem"),
        },
        default="light",
    ),
    # Warsh: خَيْرٞ لَّكُمْ
    VariantCase(
        id="damma-joined",
        site=Site(warsh=("2:54", (17, 18))),
        selector=KhilafId.RAA_DAMMA,
        faces={
            "light": _face(through(), ("x aˤ j r u", "ll a k u m"), "tarqeeq"),
            "heavy": _face(
                through(), ("x aˤ j rˤ u", "ll a k u m"), "tafkheem"),
        },
        default="light",
        masked=Expect(
            read=explicit(ibtidaa=17, waqf=(17, 18)),
            phonemes=("x aˤ j r", "l a k u m"),
            extra_phonemes=("emphatic_fatha",),
        ),
    ),
    # Warsh: كِبْرٞ مَّا
    VariantCase(
        id="kibr-joined",
        site=Site(warsh=("40:56", (14, 15))),
        selector=KhilafId.RAA_ISHRUNA_KIBR,
        faces={
            "light": _face(through(), ("k i b Q r u", "m̃ a:"), "tarqeeq"),
            "heavy": _face(through(), ("k i b Q rˤ u", "m̃ a:"), "tafkheem"),
        },
        default="light",
        masked=Expect(
            read=explicit(ibtidaa=14, waqf=(14, 15)),
            phonemes=("k i b Q r", "m a:"),
            extra_phonemes=("emphatic_fatha",),
        ),
    ),
    # Warsh: بِشَرَرٖ كَالْقَصْرِ
    VariantCase(
        id="bisharar-joined",
        site=Site(warsh=("77:32", (3, 4))),
        selector=KhilafId.RAA_BISHARAR,
        faces={
            "light": _face(
                through(), ("b i ʃ a r a r i ŋ", "k a l q aˤ sˤ rˤ"),
                "tarqeeq", char="ر[1]", sound="r[1]"),
            "heavy": _face(
                through(), ("b i ʃ a rˤ aˤ r i ŋ", "k a l q aˤ sˤ rˤ"),
                "tafkheem", char="ر[1]", sound="rˤ[1]"),
        },
        default="light",
    ),
    # Warsh: بِشَرَرٖ
    VariantCase(
        id="bisharar-waqf",
        site=Site(warsh=("77:32", (3,))),
        selector=KhilafId.RAA_BISHARAR,
        faces={
            "light": _face(
                isolated(), "b i ʃ a r a r", "tarqeeq",
                char="ر[1]", sound="r[1]"),
            "heavy": _face(
                isolated(), "b i ʃ a rˤ aˤ rˤ", "tafkheem",
                char="ر[1]", sound="rˤ[1]"),
        },
        default="light",
    ),
    # Warsh: وِزْرَ أُخْر۪ىٰ
    VariantCase(
        id="wizra-ukhra",
        site=Site(warsh=("6:164", (19, 20))),
        selector=KhilafId.RAA_WIZRA_UKHRA,
        faces={
            "light": _face(
                through(), ("w i z r a", "ʔ u x r ɛ:"), "tarqeeq",
                char="ر[1]", sound="r[1]"),
            "heavy": _face(
                through(), ("w i z rˤ aˤ", "ʔ u x r ɛ:"), "tafkheem",
                char="ر[1]"),
        },
        default="light",
        masked=Expect(
            read=explicit(ibtidaa=19, waqf=(19, 20)),
            phonemes=("w i z r", "ʔ u x r ɛ:"),
            extra_phonemes=("emphatic_fatha",),
        ),
    ),
    # Warsh: حَصِرَتْ صُدُورُهُمُۥٓۖ
    VariantCase(
        id="hasirat-suduruhum",
        site=Site(warsh=("4:90", (11, 12))),
        selector=KhilafId.RAA_HASIRAT_SUDURUHUM,
        faces={
            "light": _face(
                through(), ("ħ a sˤ i r a t", "sˤ u d u: rˤ u h u m"),
                "tarqeeq", char="ر[1]"),
            "heavy": _face(
                through(), ("ħ a sˤ i rˤ aˤ t", "sˤ u d u: rˤ u h u m"),
                "tafkheem", char="ر[1]", sound="rˤ[1]"),
        },
        default="light",
        masked=Expect(
            read=explicit(ibtidaa=11, waqf=(11, 12)),
            phonemes=("ħ a sˤ i r a t", "sˤ u d u: rˤ u h u m"),
            extra_phonemes=("emphatic_fatha",),
        ),
    ),
)


SELECTOR_SWEEP = tuple(
    pytest.param(
        site,
        site.junction or SELECTOR_JUNCTIONS[site.owner],
        id=f"{site.owner}-{site.canonical}-{site.raa}",
    )
    for site in SELECTOR_SITES
)


@pytest.mark.parametrize("run", case_runs(MOVING_STRUCTURAL_CASES))
def test_moving_structural_law(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(LEXICAL_VARIANT_CASES))
def test_lexical_raa_variants(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(SYSTEMATIC_AND_PAIR_VARIANT_CASES))
def test_systematic_and_pair_raa_variants(run):
    assert_case(run)


@pytest.mark.parametrize(("raa_site", "junction"), SELECTOR_SWEEP)
def test_every_selector_site_accepts_both_faces(raa_site, junction):
    location = raa_site.canonical
    site = Site(warsh=(f"{location.surah}:{location.ayah}", (location.word,)))
    khilaf = KhilafId(raa_site.owner)
    stopped = junction != "wasl"
    heavy = selected(
        site, location.word, khilaf, "heavy", stopped=stopped, riwayah="warsh"
    )
    light = selected(
        site, location.word, khilaf, "light", stopped=stopped, riwayah="warsh"
    )
    assert heavy.sounds(location.word) != light.sounds(location.word)


@pytest.mark.parametrize(
    ("site", "word"),
    ((Site(warsh=("20:77", (6,))), 6), (Site(warsh=("26:52", (5,))), 5)),
)
def test_an_asr_sites_are_fixed_light_outside_warsh_asr_selector(site, word):
    light = selected(
        site, word, KhilafId.RAA_ASR_WAQF, "light", stopped=True,
        riwayah="warsh",
    )
    heavy = selected(
        site, word, KhilafId.RAA_ASR_WAQF, "heavy", stopped=True,
        riwayah="warsh",
    )
    assert light.sounds(word) == heavy.sounds(word) == ("ʔ", "i", "s", "r")


@pytest.mark.parametrize("run", case_runs(SAKIN_AND_BOUNDARY_CASES))
def test_sakin_and_boundary_law(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(FIXED_LEXICAL_EXCLUSION_CASES))
def test_fixed_lexical_exclusions(run):
    assert_case(run)
