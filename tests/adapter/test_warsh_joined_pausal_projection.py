"""Selected-script projection for Warsh joined-only and pausal shapes."""
from __future__ import annotations

import pytest

from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Riwayah, Script, VerseRef
from quranic_phonemizer.model.canon import (
    CanonLetter,
    Onset,
    Quality,
    SlotOrigin,
)


def _built(ref: str, words: tuple[int, ...]):
    surah, ayah = (int(part) for part in ref.split(":"))
    verse = VerseRef(surah, ayah)
    package = recitation(Riwayah.WARSH)
    source = package.words(verse)
    selected = tuple(source[word - 1] for word in words)
    return package.build(package.read(Script.UTHMANI, verse, selected))


def test_plural_mim_before_qata_projects_a_neutral_joined_only_long():
    word = _built("60:1", (24,)).score.words[0]
    mim = word.slots[-1]

    assert mim.letter is CanonLetter.MEEM
    assert mim.nucleus.is_joined_only_long
    assert mim.nucleus.quality is Quality.U


def test_verbal_plural_mim_before_qata_projects_the_same_shape():
    word = _built("2:28", (4,)).score.words[0]
    mim = word.slots[-1]

    assert mim.letter is CanonLetter.MEEM
    assert mim.nucleus.is_joined_only_long
    assert mim.nucleus.quality is Quality.U


def test_plural_mim_before_wasl_projects_the_short_boundary_shape():
    host, following = _built("2:10", (4, 5)).score.words

    assert host.slots[-1].letter is CanonLetter.MEEM
    assert host.slots[-1].nucleus == host.slots[-1].nucleus.short(Quality.U)
    assert following.slots[0].onset is Onset.WASL


def test_verbal_plural_mim_before_wasl_projects_the_same_short_shape():
    host, following = _built("2:51", (7, 8)).score.words

    assert host.slots[-1].letter is CanonLetter.MEEM
    assert host.slots[-1].nucleus == host.slots[-1].nucleus.short(Quality.U)
    assert following.slots[0].onset is Onset.WASL


def test_plural_mim_before_a_moving_onset_stays_sakin():
    host, following = _built("2:4", (11, 12)).score.words

    assert host.slots[-1].letter is CanonLetter.MEEM
    assert host.slots[-1].nucleus.is_silent
    assert following.slots[0].onset is Onset.PLAIN


def test_lexical_haaum_is_not_projected_as_plural_mim():
    host, following = _built("69:19", (7, 8)).score.words

    assert host.slots[-1].letter is CanonLetter.MEEM
    assert host.slots[-1].nucleus == host.slots[-1].nucleus.short(Quality.U)
    assert following.slots[0].onset is Onset.WASL


@pytest.mark.parametrize(
    ("ref", "word", "letter"),
    (
        ("2:186", 11, CanonLetter.NOON),
        ("2:186", 9, CanonLetter.AIN),
        ("14:40", 9, CanonLetter.HAMZA),
    ),
)
def test_ordinary_yaa_zawaid_project_joined_only_long_i(ref, word, letter):
    host = _built(ref, (word,)).score.words[0].slots[-1]

    assert host.letter is letter
    assert host.nucleus.is_joined_only_long
    assert host.nucleus.quality is Quality.I


def test_the_naml_yaa_zawaid_is_a_joined_only_glide_with_fatha():
    word = _built("27:36", (8,)).score.words[0]
    noon, yaa = word.slots[-2:]

    assert noon.letter is CanonLetter.NOON
    assert noon.nucleus == noon.nucleus.short(Quality.I)
    assert yaa.letter is CanonLetter.YA
    assert yaa.onset is Onset.GLIDE
    assert yaa.nucleus == yaa.nucleus.short(Quality.A)


def test_small_yaa_on_pronoun_haa_keeps_the_silah_shape():
    word = _built("2:22", (13,)).score.words[0]
    haa = word.slots[-1]

    assert haa.letter is CanonLetter.HEH
    assert haa.nucleus.is_joined_only_long


def test_small_yaa_after_a_written_yaa_stays_an_ordinary_long():
    word = _built("2:258", (22,)).score.words[0]
    yaa = word.slots[-1]

    assert yaa.letter is CanonLetter.YA
    assert yaa.nucleus.is_long
    assert not yaa.nucleus.is_joined_only_long


@pytest.mark.parametrize(
    ("ref", "word"),
    (
        ("7:188", 23),
        ("26:115", 2),
        ("46:9", 21),
        ("12:90", 6),
        ("18:38", 1),
    ),
)
def test_plain_ana_and_lakinna_alifs_project_pausal_longs(ref, word):
    nucleus = _built(ref, (word,)).score.words[0].slots[-1].nucleus
    assert nucleus.is_pausal_long


def test_a_lexeme_ending_like_ana_does_not_project_a_pausal_alif():
    nucleus = _built("9:94", (13,)).score.words[0].slots[-1].nucleus
    assert not nucleus.is_pausal_long


@pytest.mark.parametrize(
    ("ref", "word"),
    (
        ("2:258", 21),
        ("6:163", 6),
        ("7:143", 39),
        ("12:45", 8),
        ("12:69", 10),
        ("18:34", 8),
        ("18:39", 15),
        ("27:39", 5),
        ("27:40", 7),
        ("40:42", 11),
        ("43:81", 6),
        ("60:1", 36),
        ("33:10", 16),
        ("33:66", 11),
        ("33:67", 8),
    ),
)
def test_retained_ana_and_ahzab_alifs_stay_ordinary_longs(ref, word):
    nucleus = _built(ref, (word,)).score.words[0].slots[-1].nucleus
    assert nucleus.is_long
    assert not nucleus.is_pausal_long


@pytest.mark.parametrize(
    ("ref", "word"), (("76:4", 4), ("76:15", 8), ("76:16", 1))
)
def test_insan_alternate_fathatan_projects_ordinary_nunation(ref, word):
    slots = _built(ref, (word,)).score.words[0].slots

    assert slots[-2].nucleus == slots[-2].nucleus.short(Quality.A)
    assert slots[-1].letter is CanonLetter.NOON
    assert slots[-1].origin is SlotOrigin.NUNATION
