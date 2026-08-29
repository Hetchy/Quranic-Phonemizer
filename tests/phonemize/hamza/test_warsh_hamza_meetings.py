"""Warsh adjacent-qata selected defaults, fixed forms, and boundaries.

Default collections cover only the selected value; they are not fixed-face claims.
"""

import pytest

from tests.support import Case, Expect, R, Site, StateCase, assert_case, case_runs, explicit, isolated, through


DHAT_FATH_DEFAULT_CASES = (
    # Warsh: ءَآنذَرْتَهُمُۥٓ
    Case(
        id="default-ibdal-before-sakin",
        site=Site(warsh=("2:6", (6,))),
        read=isolated(),
        phonemes="ʔ a: ŋ ð a rˤ t a h u m",
        char_rules={"ا": R("ibdal_hamza", "madd_lazim")},
        sound_rules={"a:": R("ibdal_hamza", "madd_lazim")},
        absent_sound_rules={"a:": R("madd_badal")},
    ),
    # Warsh: ءَالِدُ
    Case(
        id="default-ibdal-before-moving",
        site=Site(warsh=("11:72", (3,))),
        read=isolated(),
        phonemes="ʔ a: l i d Q",
        char_rules={"ا": R("ibdal_hamza", "madd_tabii")},
        sound_rules={"a:": R("ibdal_hamza", "madd_tabii")},
        absent_sound_rules={"a:": R("madd_badal", "madd_lazim")},
    ),
    # Warsh: قُلَ آٰنتُمُۥٓ
    Case(
        id="default-ibdal-after-naql",
        site=Site(warsh=("2:140", (13, 14))),
        read=through(),
        phonemes=("q u l", "a: ŋ t u m"),
        sound_rules={"a:": R("naql", "ibdal_hamza", "madd_lazim")},
        absent_sound_rules={"a:": R("madd_badal", "madd_tabii")},
    ),
    # Warsh: رَّحِيمٌۖ آٰشْفَقْتُمُۥٓ
    Case(
        id="default-ibdal-after-naql-at-ayah-edge",
        site=Site(warsh=("58:12", (22, 23))),
        read=through(),
        phonemes=("rˤ aˤ ħ i: m u n", "a: ʃ f a q Q t u m"),
        sound_rules={"a:": R("naql", "ibdal_hamza", "madd_lazim")},
        absent_sound_rules={"a:": R("madd_badal", "madd_tabii")},
    ),
)


NON_ADJACENT_CASES = (
    # Warsh: إِسْرَآءِيلَ إِلَّا
    Case(
        id="internal-hamza-before-final-lam-is-not-a-meeting",
        site=Site(warsh=("3:93", (6, 7))),
        read=through(),
        phonemes=("ʔ i s rˤ aˤ: ʔ i: l a", "ʔ i ll a:"),
        sound_rules={"i:": R("madd_badal")},
        absent_sound_rules={"ʔ[2]": R("ibdal_hamza")},
    ),
    # Warsh: اُ۬لسُّوٓأ۪ىٰٓ أَن كَذَّبُواْ
    Case(
        id="final-inclined-vowel-separates-across-word-hamzas",
        site=Site(warsh=("30:10", (6, 7, 8))),
        read=through(),
        phonemes=("ʔ a ss u: ʔ ɛ:", "ʔ a ŋ", "k a ðð a b u:"),
        char_rules={"ى": R("taqlil")},
        sound_rules={"ɛ:": R("taqlil")},
        absent_sound_rules={"ʔ[2]": R("ibdal_hamza", "tashil")},
    ),
)


BARE_ANTA_PAUSAL_CASES = (
    # Warsh: ءَآنتَ فَعَلْتَ
    Case(
        id="continuing-default-ibdal",
        site=Site(warsh=("21:62", (2, 3))),
        read=through(),
        phonemes=("ʔ a: ŋ t a", "f a ʕ a l t"),
        sound_rules={"a:": R("ibdal_hamza", "madd_lazim")},
    ),
    # Warsh: ءَآنتَ
    Case(
        id="waqf-forces-tashil",
        site=Site(warsh=("21:62", (2,))),
        read=isolated(),
        phonemes="ʔ a ʔ̞ a ŋ t",
        sound_rules={"ʔ̞": R("tashil")},
        absent_sound_rules={"ʔ̞": R("ibdal_hamza")},
    ),
)


FIXED_ONE_WORD_CASES = (
    # Warsh: أَئِنَّكُمْ
    Case(
        id="one-word-second-i-fixed-tashil",
        site=Site(warsh=("6:19", (19,))),
        read=isolated(),
        phonemes="ʔ a ʔ̞ i ñ a k u m",
        char_rules={"ئ": R("tashil")},
        sound_rules={"ʔ̞": R("tashil")},
    ),
    # Warsh: اَ۟لْقِيَ
    Case(
        id="one-word-second-u-fixed-tashil",
        site=Site(warsh=("54:25", (1,))),
        read=isolated(),
        phonemes="ʔ a ʔ̞ u l q i:",
        char_rules={"@round_zero": R("tashil")},
        sound_rules={"ʔ̞": R("tashil")},
    ),
    # Warsh: ءَاٰ۬مَنتُم
    Case(
        id="triple-keeps-lexical-badal",
        site=Site(warsh=("7:123", (3,))),
        read=isolated(),
        phonemes="ʔ a ʔ̞ a: m a ŋ t u m",
        sound_rules={"ʔ̞": R("tashil"), "a:": R("madd_badal")},
        absent_sound_rules={"a:": R("ibdal_hamza", "madd_tabii")},
    ),
    # Warsh: ءَاٰ۬لِهَتُنَا
    Case(
        id="triple-aaliha-keeps-lexical-badal",
        site=Site(warsh=("43:58", (2,))),
        read=isolated(),
        phonemes="ʔ a ʔ̞ a: l i h a t u n a:",
        char_rules={"@tashil_mark": R("tashil")},
        sound_rules={"ʔ̞": R("tashil"), "a:[1]": R("madd_badal")},
        absent_sound_rules={"a:[1]": R("ibdal_hamza", "madd_tabii")},
    ),
)


FIXED_AAJAMI_CASES = (
    # Warsh: ءَآعْجَمِيّٞ وَعَرَبِيّٞۖ
    Case(
        id="fixed-tashil-before-tanwin-waw",
        site=Site(warsh=("41:44", (9, 10))),
        read=through(),
        phonemes=(
            "ʔ a ʔ̞ a ʕ ʒ a m i jj u",
            "w̃ a ʕ a rˤ aˤ b i jj",
        ),
        char_rules={
            "ا": R("tashil"),
            "@dammatan[1]": R("idgham_bi_ghunnah"),
            "و": R("idgham_bi_ghunnah"),
        },
        sound_rules={
            "ʔ̞": R("tashil"),
            "w̃": R("idgham_bi_ghunnah"),
        },
    ),
)


AIMMA_DEFAULT_CASES = (
    # Warsh: أَي۪مَّةَ
    Case(
        id="default-tashil",
        site=Site(warsh=("9:12", (11,))),
        read=isolated(),
        phonemes="ʔ a ʔ̞ i m̃ a h",
        char_rules={"ي": R("tashil")},
        sound_rules={"ʔ̞": R("tashil"), "m̃": R("ghunnah_mushaddadah")},
    ),
)


MUTTAFIQ_DEFAULT_CASES = (
    # Warsh: جَآءَ احَدٞ مِّنكُم
    StateCase(id="default-a-a-ibdal-boundaries", site=Site(warsh=("4:43", (27, 28, 29))), states={
        "stopped-before": Expect(
            read=explicit(ibtidaa=27, waqf=(27, 29)),
            phonemes=("ʒ a: ʔ", "ʔ a ħ a d u", "m̃ i ŋ k u m"),
            char_rules={
                "@dammatan": R("idgham_bi_ghunnah"),
                "م[1]": R("idgham_bi_ghunnah"),
            },
            sound_rules={"m̃": R("idgham_bi_ghunnah")},
            absent_sound_rules={"ʔ[2]": R("ibdal_hamza", "tashil")},
        ),
        "joined": Expect(
            read=through(),
            phonemes=("ʒ a: ʔ", "a: ħ a d u", "m̃ i ŋ k u m"),
            char_rules={
                "ا[2]": R("ibdal_hamza", "madd_tabii"),
                "@dammatan": R("idgham_bi_ghunnah"),
                "م[1]": R("idgham_bi_ghunnah"),
            },
            sound_rules={
                "a:[2]": R("ibdal_hamza", "madd_tabii"),
                "m̃": R("idgham_bi_ghunnah"),
            },
        ),
    }),
    # Warsh: اَ۬لنِّسَآءِ الَّا
    Case(
        id="default-i-i-ibdal",
        site=Site(warsh=("4:22", (7, 8))),
        read=through(),
        phonemes=("ʔ a ñ i s a: ʔ", "i: l a:"),
        char_rules={"ا[3]": R("ibdal_hamza", "madd_tabii")},
        sound_rules={"i:": R("ibdal_hamza", "madd_tabii")},
        absent_sound_rules={"i:": R("madd_badal", "madd_lazim")},
    ),
    # Warsh: أَوْلِيَآءُۖ اوْلَٰٓئِكَ
    Case(
        id="default-u-u-ibdal-fuses-carrier",
        site=Site(warsh=("46:32", (14, 15))),
        read=through(),
        phonemes=("ʔ a w l i j a: ʔ", "u: l a: ʔ i k"),
        char_rules={"ا[2]": R("ibdal_hamza")},
        sound_rules={"u:": R("ibdal_hamza", "madd_badal")},
        absent_sound_rules={"u:": R("madd_tabii", "madd_lazim")},
    ),
)


FIXED_DIFFERENT_VOWEL_CASES = (
    # Warsh: اِ۬لنِّسَآءِ اَ۬وَ اَكْنَنتُمْ فِےٓ
    Case(
        id="different-i-a-through-following-naql",
        site=Site(warsh=("2:235", (9, 10, 11, 12))),
        read=through(),
        phonemes=(
            "ʔ a ñ i s a: ʔ i",
            "j a w a",
            "k n a ŋ t u m",
            "f i:",
        ),
        char_rules={
            "@tashil_mark[2]": R("ibdal_hamza"),
            "ا[4]": R("naql"),
        },
        sound_rules={"j": R("ibdal_hamza"), "a[3]": R("naql")},
        absent_sound_rules={"j": R("madd_tabii")},
    ),
    # Warsh: وَيَٰسَمَآءُ اَ۬قْلِعِےۖ
    Case(
        id="different-u-a-moving-waw",
        site=Site(warsh=("11:44", (5, 6))),
        read=explicit(ibtidaa=5, waqf=6),
        phonemes=("w a j a: s a m a: ʔ u", "w a q Q l i ʕ i:"),
        sound_rules={"w[2]": R("ibdal_hamza")},
        absent_sound_rules={"w[2]": R("madd_tabii")},
    ),
    # Warsh: تَفِےٓءَ ا۪لَىٰٓ
    Case(
        id="different-a-i-fixed-tashil",
        site=Site(warsh=("49:9", (17, 18))),
        read=explicit(ibtidaa=17, waqf=18),
        phonemes=("t a f i: ʔ a", "ʔ̞ i l a:"),
        sound_rules={"ʔ̞": R("tashil")},
    ),
    # Warsh: جَآءَ اُ۟مَّةٗ رَّسُولُهَا
    Case(
        id="different-a-u-fixed-tashil",
        site=Site(warsh=("23:44", (7, 8, 9))),
        read=through(),
        phonemes=(
            "ʒ a: ʔ a",
            "ʔ̞ u m̃ a t a",
            "rˤrˤ aˤ s u: l u h a:",
        ),
        char_rules={
            "@round_zero": R("tashil"),
            "@fathatan": R("idgham_bila_ghunnah"),
            "ر": R("idgham_bila_ghunnah"),
        },
        sound_rules={
            "ʔ̞": R("tashil"),
            "rˤrˤ": R("idgham_bila_ghunnah"),
        },
    ),
)


CROSS_AYAH_FIXED_CASES = (
    # Warsh: يَشَآءُۖ اَ۬لَمْ
    Case(
        id="joined-ayah-u-a-moving-waw",
        site=Site(warsh=("14:27", (18, 19))),
        read=explicit(ibtidaa=18, waqf=19),
        phonemes=("j a ʃ a: ʔ u", "w a l a m"),
        char_rules={"@tashil_mark": R("ibdal_hamza")},
        sound_rules={"w": R("ibdal_hamza")},
        absent_sound_rules={"w": R("madd_tabii")},
    ),
    # Warsh: زَكَرِيَّآءَ ا۪ذْ
    Case(
        id="joined-ayah-a-i-fixed-tashil",
        site=Site(warsh=("19:2", (5, 6))),
        read=explicit(ibtidaa=5, waqf=6),
        phonemes=("z a k a r i jj a: ʔ a", "ʔ̞ i ð"),
        char_rules={"ا[2]": R("tashil")},
        sound_rules={"ʔ̞": R("tashil")},
    ),
)


DAMM_KASR_DEFAULT_CASES = (
    # Warsh: يَٰزَكَرِيَّآءُ اِ۪نَّا
    Case(
        id="default-ibdal-moving-waw",
        site=Site(warsh=("19:7", (1, 2))),
        read=explicit(ibtidaa=1, wasl=2),
        phonemes=("j a: z a k a r i jj a: ʔ u", "w i ñ a:"),
        sound_rules={"w": R("ibdal_hamza")},
    ),
)


@pytest.mark.parametrize("run", case_runs(DHAT_FATH_DEFAULT_CASES))
def test_dhat_fath_default(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(NON_ADJACENT_CASES))
def test_non_adjacent_internal_hamza(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(FIXED_ONE_WORD_CASES))
def test_fixed_one_word_meetings(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(FIXED_AAJAMI_CASES))
def test_fixed_aajami(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(BARE_ANTA_PAUSAL_CASES))
def test_bare_anta_pausal_mask(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(AIMMA_DEFAULT_CASES))
def test_aimma_default(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(MUTTAFIQ_DEFAULT_CASES))
def test_muttafiq_default(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(FIXED_DIFFERENT_VOWEL_CASES))
def test_fixed_different_vowel_meetings(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(CROSS_AYAH_FIXED_CASES))
def test_cross_ayah_fixed_meetings(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(DAMM_KASR_DEFAULT_CASES))
def test_damm_kasr_default(run):
    assert_case(run)
