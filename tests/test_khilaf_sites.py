"""Khilaf that names its sites word by word: defaults, both wajh, and reach.

A raa is chosen while performing one Score; a vowel is chosen while building
it, so the two are wired in different layers and both are checked here.
"""
from __future__ import annotations

import pytest

from conftest import sources, words_of  # noqa: F401  (fixture)
from quranic_phonemizer.canon.build import build
from quranic_phonemizer.engine.run import perform
from quranic_phonemizer.model.address import (
    BoundaryPlan,
    Junction,
    KhilafId,
    Option,
    Script,
    VariantSelection,
    VerseRef,
)
from quranic_phonemizer.model.canon import ABJAD, Annotation, Onset
from quranic_phonemizer.render.recite import phonemes_by_word
from quranic_phonemizer.riwayat.hafs import HAFS, khilaf, script_adapter
from quranic_phonemizer.rules.khilaf import KhilafError

RAA = KhilafId.RAA_TAFKHEEM

#: (surah, ayah, word), the site key, and the reading each junction gives by
#: default. A site at the end of its verse is stopped on either plan.
SITES = [
    ((26, 63, 11), "فiرقiن", "firˤqiŋ", "firˤqQ"),
    ((34, 12, 10), "ءaلقiطرi", "lqitˤQri", "ʔalqitˤQr"),
    ((12, 99, 10), "مiصرa", "misˤrˤaˤ", "misˤrˤ"),
    ((10, 87, 8), "بiمiصرa", "bimisˤrˤaˤ", "bimisˤrˤ"),
    ((54, 16, 4), "وaنuذuرi", "wanuðurˤ", "wanuðurˤ"),
    ((54, 23, 3), "بiءaلنuذuرi", "biñuðurˤ", "biñuðurˤ"),
    ((89, 4, 3), "يaسرi", "jasr", "jasr"),
    ((20, 77, 6), "ءaسرi", "ʔasri", "ʔasr"),
    ((11, 81, 9), "فaءaسرi", "faʔasri", "faʔasr"),
]


def _read(packed, shared, alphabet, site, junction, selection):
    """Built with the selection as well as performed with it: a vowel khilaf
    is settled before there is a Performance to choose in."""
    surah, ayah, word = site
    score = build(
        script_adapter(Script.UTHMANI).read(
            VerseRef(surah, ayah), words_of(packed, surah, ayah)
        ),
        selection=selection,
        **shared,
    ).score
    plan = BoundaryPlan(
        tuple(
            Junction.EDGE if i == len(score.words) - 1 else junction
            for i in range(len(score.words))
        )
    )
    performance = perform(score, HAFS, plan, selection=selection)
    return "".join(phonemes_by_word(performance, score, alphabet)[word - 1])


@pytest.mark.parametrize(("site", "key", "joined", "stopped"), SITES)
def test_the_documented_default_is_taken(
    packed, shared, alphabet, site, key, joined, stopped
) -> None:
    plain = VariantSelection()
    assert _read(packed, shared, alphabet, site, Junction.JOIN, plain) == joined
    assert _read(packed, shared, alphabet, site, Junction.STOP, plain) == stopped


@pytest.mark.parametrize(("site", "key", "joined", "stopped"), SITES)
def test_both_wajh_are_reachable(
    packed, shared, alphabet, site, key, joined, stopped
) -> None:
    """A khilaf nothing reads is a khilaf that does not exist."""
    disputed = khilaf().raa.sites[key]
    junction = Junction.STOP if disputed.at_stop else Junction.JOIN
    readings = {
        name: _read(
            packed, shared, alphabet, site, junction,
            VariantSelection((Option(RAA, name),)),
        )
        for name in ("heavy", "light")
    }
    assert readings["heavy"] != readings["light"]
    assert "rˤ" in readings["heavy"] and "rˤ" not in readings["light"]


def test_a_site_choice_outranks_one_made_for_every_site(
    packed, shared, alphabet
) -> None:
    """A reader may take one wajh throughout and another in one word."""
    everywhere = Option(RAA, "light")
    here = Option(RAA, "heavy", site="يaسرi")
    both = VariantSelection((everywhere, here))
    assert _read(packed, shared, alphabet, (89, 4, 3), Junction.STOP, both) == "jasrˤ"
    assert _read(
        packed, shared, alphabet, (20, 77, 6), Junction.STOP,
        VariantSelection((everywhere, here)),
    ) == "ʔasr"


def test_the_undisputed_junction_is_left_to_the_rule(
    packed, shared, alphabet
) -> None:
    """`مِصْرَ` is disputed only at a stop. Joined, its raa carries a fatha and
    no selection may lighten it."""
    light = VariantSelection((Option(RAA, "light"),))
    assert _read(
        packed, shared, alphabet, (12, 99, 10), Junction.JOIN, light
    ) == "misˤrˤaˤ"


def test_the_optional_yaa_is_read_both_ways(packed, shared, alphabet) -> None:
    """27:36. Both scripts write this yaa small where 19:30 writes the same
    word's full, and small is what says the letter may be dropped."""
    readings = {
        name: _read(
            packed, shared, alphabet, (27, 36, 8), Junction.STOP,
            VariantSelection(
                (Option(KhilafId.YAA_ITHBAT, name, site="ءaتaنiيa"),)
            ),
        )
        for name in ("hadhf", "ithbat")
    }
    assert readings == {"hadhf": "ʔa:ta:n", "ithbat": "ʔa:ta:ni:"}
    assert _read(
        packed, shared, alphabet, (27, 36, 8), Junction.STOP, VariantSelection()
    ) == readings["hadhf"]
    assert _read(
        packed, shared, alphabet, (19, 30, 5), Junction.STOP, VariantSelection()
    ) == "ʔa:ta:ni:", "the full yaa of 19:30 is not disputed"


def test_the_optional_yaa_is_always_said_when_joined(
    packed, shared, alphabet
) -> None:
    """The dispute lives at the stop only; joined, both wajh say it."""
    for name in ("hadhf", "ithbat"):
        assert _read(
            packed, shared, alphabet, (27, 36, 8), Junction.JOIN,
            VariantSelection(
                (Option(KhilafId.YAA_ITHBAT, name, site="ءaتaنiيa"),)
            ),
        ) == "ʔa:ta:nija"


def test_an_unknown_option_raises_rather_than_falling_back() -> None:
    with pytest.raises(KhilafError, match="not an option"):
        khilaf().raa.of(
            "مiصرa", True, VariantSelection((Option(RAA, "middling"),))
        )


def test_the_site_keys_reach_the_words_they_name(sources, shared) -> None:
    """A key too loose would silently claim `فَرِيقًا`, which shares five
    letters with `فِرْقٍ` and is not disputed."""
    keys = set(khilaf().raa.sites)
    found = {script: [] for script in Script}
    for script in Script:
        for (surah, ayah), words in sources[script].items():
            score = build(
                script_adapter(script).read(VerseRef(surah, ayah), words),
                **shared,
            ).score
            for index, word in enumerate(score.words, start=1):
                if _vocalised(word) in keys:
                    found[script].append(f"{surah}:{ayah}:{index}")
    assert len(found[Script.UTHMANI]) == 21
    assert sorted(found[Script.UTHMANI]) == sorted(found[Script.INDOPAK])


def _vocalised(word) -> str:
    out = []
    for slot in word.slots:
        quality = getattr(slot.nucleus, "quality", None)
        out.append(
            ABJAD[slot.letter.value]
            + ("~" if slot.onset is Onset.GEMINATE else "")
            + (quality.value if quality else "")
        )
    return "".join(out)


def test_the_vowel_khilaf_takes_its_default(packed, shared, alphabet) -> None:
    """30:54 `ضَعْف` is read with fatha and with damma; Uthmani prints the
    first and IndoPak the second, and the Score is the same either way."""
    plain = VariantSelection()
    assert _read(
        packed, shared, alphabet, (30, 54, 5), Junction.STOP, plain
    ) == "dˤaˤʕf"


def test_both_vowels_are_reachable(packed, shared, alphabet) -> None:
    readings = {
        name: _read(
            packed, shared, alphabet, (30, 54, 5), Junction.STOP,
            VariantSelection((Option(KhilafId.NUCLEUS_VOWEL, name, site="ضعف"),)),
        )
        for name in ("fatha", "damma")
    }
    assert readings == {"fatha": "dˤaˤʕf", "damma": "dˤuʕf"}


def test_the_two_scripts_agree_on_the_vowel_khilaf(sources, shared) -> None:
    """The khilaf is what makes them agree: one script writes each wajh."""
    digests = {
        script: build(
            script_adapter(script).read(
                VerseRef(30, 54), sources[script][(30, 54)]
            ),
            **shared,
        ).score.words[4].slots[0].nucleus
        for script in Script
    }
    assert digests[Script.UTHMANI] == digests[Script.INDOPAK]


def test_the_imala_takes_its_documented_default(packed, shared, alphabet) -> None:
    """11:41 is the only imala in Hafs. Its letter is articulated as an `e`,
    which occurs nowhere else, so the plain `i` is the default and `e` is the
    other reading. The rule is tagged for both."""
    readings = {
        name: _read(
            packed, shared, alphabet, (11, 41, 6), Junction.STOP,
            VariantSelection(
                (Option(KhilafId.IMALA_QUALITY, name, site="مجرىها"),)
            ),
        )
        for name in ("e", "i")
    }
    assert readings == {"e": "maʒQre:ha:", "i": "maʒQri:ha:"}
    assert _read(
        packed, shared, alphabet, (11, 41, 6), Junction.STOP, VariantSelection()
    ) == readings["i"]


def test_both_scripts_reach_the_imala(sources, shared, alphabet) -> None:
    """IndoPak types no imala mark, so the site is what carries it there.
    The annotation is the fact; the vowel read for it is the dispute."""
    from quranic_phonemizer.canon.build import build as _build

    for script in Script:
        score = _build(
            script_adapter(script).read(
                VerseRef(11, 41), sources[script][(11, 41)]
            ),
            **shared,
        ).score
        assert Annotation.IMALA in score.words[5].slots[2].annotations, script
