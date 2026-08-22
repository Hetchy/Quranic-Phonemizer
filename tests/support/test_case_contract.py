from __future__ import annotations

import pytest

from quranic_phonemizer.api import alphabet
from quranic_phonemizer.model.address import Script, VariantSelection

from tests.support import (
    Case,
    Expect,
    R,
    SelectorError,
    Site,
    StateCase,
    VariantCase,
    assert_case,
    case_runs,
    explicit,
    isolated,
    joining,
    parse_phonemes,
    pick,
    reading,
    registered_selectors,
    through,
)
from tests.support.case import resolve
from tests.support.selectors import resolve_glyph, resolve_sound


def test_phoneme_strings_are_tokenized_by_one_ascii_space():
    assert parse_phonemes("ʕ i ŋ d Q", alphabet()) == ("ʕ", "i", "ŋ", "d", "Q")


@pytest.mark.parametrize("value", [" ʕ i", "ʕ i ", "ʕ  i", "ʕ\ti"])
def test_phoneme_spacing_noise_is_rejected(value):
    with pytest.raises(ValueError):
        parse_phonemes(value, alphabet())


def test_unknown_phoneme_tokens_are_rejected():
    with pytest.raises(ValueError, match="unknown phoneme"):
        parse_phonemes("dʒ", alphabet())


def test_atomic_geminates_and_qalqala_are_inventory_tokens():
    assert parse_phonemes("lˤlˤ a: q Q", alphabet()) == ("lˤlˤ", "a:", "q", "Q")


def test_shared_site_reuses_one_canonical_address():
    site = Site.shared("2:42", (7,), riwayat=("hafs", "warsh"))
    assert site.address("hafs") == site.address("warsh")


def test_pick_requires_an_expectation_for_the_running_riwayah():
    value = pick(hafs="a", warsh="i")
    assert resolve(value, "hafs") == "a"
    with pytest.raises(KeyError):
        resolve(pick(hafs="a"), "warsh")


def test_pick_prefers_an_exact_riwayah_script_value():
    value = pick(hafs="a", hafs_indopak="i")
    assert resolve(value, "hafs", Script.UTHMANI) == "a"
    assert resolve(value, "hafs", Script.INDOPAK) == "i"


def test_boundary_intents_use_the_focused_span():
    assert isolated().kwargs((7,)) == {"isolated": 7}
    assert joining().kwargs((7,)) == {"ibtidaa": 7, "wasl": 7}
    assert through().kwargs((7, 8)) == {"ibtidaa": 7, "waqf": 8}
    assert explicit(ibtidaa=7, waqf=8).kwargs((7, 8)) == {
        "ibtidaa": 7,
        "waqf": 8,
    }


def test_isolated_rejects_a_multiword_focus():
    with pytest.raises(ValueError, match="one focused word"):
        isolated().kwargs((7, 8))


def test_registered_selectors_cover_harakat_tanwin_and_mini_marks():
    assert {
        "@fatha",
        "@damma",
        "@kasra",
        "@fathatan",
        "@dammatan",
        "@kasratan",
        "@small_noon",
        "@mini_meem",
    } <= registered_selectors()


def test_a_unique_literal_needs_no_occurrence_suffix():
    result = reading(Site(hafs=("3:163", (3,))), isolated=3)
    assert result._assembled.glyphs[
        resolve_glyph(result._assembled, (3,), "ن")
    ].char == "ن"


def test_an_occurrence_suffix_is_rejected_on_a_unique_literal():
    result = reading(Site(hafs=("3:163", (3,))), isolated=3)
    with pytest.raises(SelectorError, match="is unique"):
        resolve_glyph(result._assembled, (3,), "ن[1]")


def test_an_ambiguous_literal_requires_an_occurrence_suffix():
    result = reading(Site(hafs=("1:1", (1, 2))), ibtidaa=1, waqf=2)
    with pytest.raises(SelectorError, match=r"add \[n\]"):
        resolve_glyph(result._assembled, (1, 2), "ل")


def test_a_registered_selector_resolves_a_visually_subtle_mark():
    result = reading(Site(hafs=("4:48", (19,))), isolated=19)
    glyph = resolve_glyph(result._assembled, (19,), "@fathatan")
    assert result._assembled.glyphs[glyph].char == "ً"


def test_a_raw_combining_mark_is_rejected_as_a_selector():
    result = reading(Site(hafs=("4:48", (19,))), isolated=19)
    with pytest.raises(SelectorError, match="registered @selector"):
        resolve_glyph(result._assembled, (19,), "ً")


def test_unknown_semantic_selectors_fail_loudly():
    result = reading(Site(hafs=("4:48", (19,))), isolated=19)
    with pytest.raises(SelectorError, match="unknown source selector"):
        resolve_glyph(result._assembled, (19,), "@mystery")


def test_sound_occurrence_suffixes_follow_the_same_noise_rule():
    result = reading(Site(hafs=("3:163", (3,))), isolated=3)
    assert result._assembled.sounds[
        resolve_sound(result._assembled, result._sound_word, (3,), "ŋ")
    ].token == "ŋ"
    with pytest.raises(SelectorError, match="is unique"):
        resolve_sound(result._assembled, result._sound_word, (3,), "ŋ[1]")


def test_case_runs_expand_each_supported_script():
    case = Case(
        id="and",
        site=Site(hafs=("3:163", (3,))),
        read=isolated(),
        phonemes="ʕ i ŋ d Q",
    )
    assert [param.values[0].script.value for param in case_runs((case,))] == [
        "uthmani",
        "indopak",
    ]


def test_one_case_asserts_phonemes_and_connected_rule_reach():
    # عِندَ
    case = Case(
        id="ikhfaa",
        site=Site(hafs=("3:163", (3,))),
        read=isolated(),
        phonemes="ʕ i ŋ d Q",
        all_rules=R("ikhfaa_haqiqi", "qalqala_kubra", "pausal_sukun"),
        char_rules={"ن": R("ikhfaa_haqiqi")},
        sound_rules={"ŋ": R("ikhfaa_haqiqi")},
    )
    for param in case_runs((case,)):
        assert_case(param.values[0])


def test_state_cases_expand_each_named_boundary_state():
    case = StateCase(
        id="iwad",
        site=Site(hafs=("4:48", (19,))),
        states={
            "stopped": Expect(read=isolated(), phonemes="ʔ i θ m a:"),
            "joined": Expect(read=joining(), phonemes="ʔ i θ m a n"),
        },
    )
    assert {param.values[0].state for param in case_runs((case,))} == {
        "stopped",
        "joined",
    }


def test_variant_cases_expand_values_default_and_masked_state():
    from quranic_phonemizer.model.address import KhilafId

    case = VariantCase(
        id="raa",
        site=Site(hafs=("34:12", (10,))),
        selector=KhilafId.RAA_ALQITR_WAQF,
        faces={
            "light": Expect(read=isolated(), phonemes="ʔ a l q i tˤ Q r"),
            "heavy": Expect(read=isolated(), phonemes="ʔ a l q i tˤ Q rˤ"),
        },
        default="light",
        masked=Expect(read=joining(), phonemes="ʔ a l q i tˤ Q r i"),
    )
    runs = [param.values[0] for param in case_runs((case,))]
    assert {run.state for run in runs} == {
        "value-light", "value-heavy", "default", "masked-light", "masked-heavy"
    }
    assert runs[2].expect.selection == VariantSelection()


def test_multiword_cases_require_one_phoneme_string_per_word():
    case = Case(
        id="bad-shape",
        site=Site(hafs=("1:1", (1, 2))),
        read=through(),
        phonemes="b i s m i",
    )
    with pytest.raises(ValueError, match="multiword"):
        assert_case(case_runs((case,))[0].values[0])
