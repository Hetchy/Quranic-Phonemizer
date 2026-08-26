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
        char_rules={"ا": R("tashil")},
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
    # Warsh: جَآءَ احَدٞ
    StateCase(id="default-ibdal-boundaries", site=Site(warsh=("4:43", (27, 28))), states={
        "stopped-before": Expect(
            read=explicit(ibtidaa=27, waqf=(27, 28)),
            phonemes=("ʒ a: ʔ", "ʔ a ħ a d Q"),
            absent_sound_rules={"ʔ[2]": R("ibdal_hamza", "tashil")},
        ),
        "joined": Expect(
            read=explicit(ibtidaa=27, waqf=28),
            phonemes=("ʒ a: ʔ", "a: ħ a d Q"),
            sound_rules={"a:[2]": R("ibdal_hamza", "madd_tabii")},
        ),
    }),
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


@pytest.mark.parametrize("run", case_runs(DAMM_KASR_DEFAULT_CASES))
def test_damm_kasr_default(run):
    assert_case(run)
