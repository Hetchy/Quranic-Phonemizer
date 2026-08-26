"""Warsh adjacent-qata selected defaults, fixed forms, and boundaries.

Default collections cover only the selected value; they are not fixed-face claims.
"""

import pytest

from tests.support import Case, Expect, R, Site, StateCase, assert_case, case_runs, explicit, isolated


DHAT_FATH_DEFAULT_CASES = (
    # Warsh: ءَآنذَرْتَهُمُۥٓ
    Case(
        id="default-ibdal-before-sakin",
        site=Site(warsh=("2:6", (6,))),
        read=isolated(),
        phonemes="ʔ a: ŋ ð a rˤ t a h u m u:",
        char_rules={"ا": R("ibdal_hamza", "madd_lazim")},
        sound_rules={"a:": R("ibdal_hamza", "madd_lazim")},
        absent_sound_rules={"a:": R("madd_badal")},
    ),
    # Warsh: ءَآنتَ
    StateCase(id="default-ibdal-with-pausal-mask", site=Site(warsh=("21:62", (2,))), states={
        "continuing": Expect(
            read=explicit(ibtidaa=2, wasl=2),
            phonemes="ʔ a: ŋ t a",
            sound_rules={"a:": R("ibdal_hamza", "madd_lazim")},
        ),
        "stopped": Expect(
            read=isolated(),
            phonemes="ʔ a ʔ̞ a ŋ t",
            sound_rules={"ʔ̞": R("tashil")},
            absent_sound_rules={"ʔ̞": R("ibdal_hamza")},
            extra_phonemes=("tashil",),
        ),
    }),
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
        extra_phonemes=("tashil",),
    ),
    # Warsh: أَئِنَّكُمْ
    Case(
        id="one-word-tashil-token-disabled",
        site=Site(warsh=("6:19", (19,))),
        read=isolated(),
        phonemes="ʔ a ʔ i ñ a k u m",
        char_rules={"ئ": R("tashil")},
        sound_rules={"ʔ[2]": R("tashil")},
        extra_phonemes=(),
    ),
    # Warsh: اَ۟لْقِيَ
    Case(
        id="one-word-second-u-fixed-tashil",
        site=Site(warsh=("54:25", (1,))),
        read=isolated(),
        phonemes="ʔ a ʔ̞ u l q i:",
        char_rules={"ا": R("tashil")},
        sound_rules={"ʔ̞": R("tashil")},
        extra_phonemes=("tashil",),
    ),
    # Warsh: ءَاٰ۬مَنتُم
    Case(
        id="triple-keeps-lexical-badal",
        site=Site(warsh=("7:123", (3,))),
        read=isolated(),
        phonemes="ʔ a ʔ̞ a: m a ŋ t u m",
        sound_rules={"ʔ̞": R("tashil"), "a:": R("madd_badal")},
        absent_sound_rules={"a:": R("ibdal_hamza", "madd_tabii")},
        extra_phonemes=("tashil",),
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
        extra_phonemes=("tashil",),
    ),
)


MUTTAFIQ_DEFAULT_CASES = (
    # Warsh: جَآءَ احَدٞ
    StateCase(id="default-ibdal-boundaries", site=Site(warsh=("4:43", (27, 28))), states={
        "joined": Expect(
            read=explicit(ibtidaa=27, wasl=28),
            phonemes=("ʒ a: ʔ", "a: ħ a d u"),
            sound_rules={"a:[2]": R("ibdal_hamza", "madd_tabii")},
        ),
        "stopped-before": Expect(
            read=explicit(ibtidaa=27, waqf=(27, 28)),
            phonemes=("ʒ a: ʔ", "ʔ a ħ a d Q"),
            absent_sound_rules={"ʔ[2]": R("ibdal_hamza", "tashil")},
        ),
        "joined-then-stop": Expect(
            read=explicit(ibtidaa=27, waqf=28),
            phonemes=("ʒ a: ʔ", "a: ħ a d Q"),
            sound_rules={"a:[2]": R("ibdal_hamza", "madd_tabii")},
        ),
    }),
    # Warsh: احَدٞ
    Case(
        id="matching-start-second",
        site=Site(warsh=("4:43", (28,))),
        read=explicit(ibtidaa=28, waqf=28),
        phonemes="ʔ a ħ a d Q",
        absent_sound_rules={"ʔ": R("ibdal_hamza", "tashil")},
    ),
)


FIXED_DIFFERENT_VOWEL_CASES = (
    # Warsh: اِ۬لنِّسَآءِ اَ۬وَ
    Case(
        id="different-i-a-moving-yaa",
        site=Site(warsh=("2:235", (9, 10))),
        read=explicit(ibtidaa=9, wasl=10),
        phonemes=("ʔ a ñ i s a: ʔ i", "j a w a"),
        sound_rules={"j": R("ibdal_hamza")},
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
        extra_phonemes=("tashil",),
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


@pytest.mark.parametrize("run", case_runs(FIXED_ONE_WORD_CASES))
def test_fixed_one_word_meetings(run):
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


@pytest.mark.parametrize("run", case_runs(DAMM_KASR_DEFAULT_CASES))
def test_damm_kasr_default(run):
    assert_case(run)
