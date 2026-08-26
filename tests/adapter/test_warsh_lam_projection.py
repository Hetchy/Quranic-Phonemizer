from __future__ import annotations

from dataclasses import dataclass

import pytest

from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import (
    Location,
    Riwayah,
    Script,
    SourceLocation,
)
from quranic_phonemizer.model.canon import CanonLetter, Quality
from quranic_phonemizer.riwayat.warsh.resources import (
    ARTIFACT,
    corpus,
    script_adapter,
)
from quranic_phonemizer.riwayat.warsh.lam import SITES


@dataclass(frozen=True, slots=True)
class RegisterRow:
    owner: str
    source: tuple[int, int, int]
    canonical: tuple[int, int, int]
    text: str
    lam: int = 1


ROWS = (
    RegisterRow("lam_dhat_yaa", (2, 124, 11), (2, 125, 11), "مُصَلّىٗۖ"),
    RegisterRow("lam_dhat_yaa", (17, 18, 16), (17, 18, 16), "يَصْلَيٰهَا"),
    RegisterRow("lam_dhat_yaa", (84, 12, 1), (84, 12, 1), "وَيُصَلَّىٰ"),
    RegisterRow("lam_dhat_yaa", (87, 12, 2), (87, 12, 2), "يَصْلَى"),
    RegisterRow("lam_dhat_yaa", (88, 4, 1), (88, 4, 1), "تَصْلَىٰ"),
    RegisterRow("lam_dhat_yaa", (92, 15, 2), (92, 15, 2), "يَصْلَيٰهَآ"),
    RegisterRow("lam_dhat_yaa", (111, 3, 1), (111, 3, 1), "سَيَصْلَىٰ"),
    RegisterRow("lam_verse_heads", (75, 30, 4), (75, 31, 4), "صَلّ۪ىٰۖ"),
    RegisterRow("lam_verse_heads", (87, 15, 4), (87, 15, 4), "فَصَلّ۪ىٰۖ"),
    RegisterRow("lam_verse_heads", (96, 10, 3), (96, 10, 3), "صَلّ۪ىٰٓۖ"),
    RegisterRow("lam_separated_by_alif", (2, 231, 36), (2, 233, 36), "فِصَالاً"),
    RegisterRow("lam_separated_by_alif", (4, 127, 13), (4, 128, 13), "يَّصَّٰلَحَا"),
    RegisterRow("lam_separated_by_alif", (20, 85, 1), (20, 86, 14), "اَفَطَالَ"),
    RegisterRow("lam_separated_by_alif", (21, 44, 6), (21, 44, 6), "طَالَ"),
    RegisterRow("lam_separated_by_alif", (57, 15, 21), (57, 16, 21), "فَطَالَ"),
    RegisterRow("lam_final_waqf", (2, 26, 14), (2, 27, 14), "يُّوصَلَ"),
    RegisterRow("lam_final_waqf", (2, 247, 2), (2, 249, 2), "فَصَلَ"),
    RegisterRow("lam_final_waqf", (6, 120, 11), (6, 119, 11), "فَصَّلَ"),
    RegisterRow("lam_final_waqf", (7, 117, 3), (7, 118, 3), "وَبَطَلَ"),
    RegisterRow("lam_final_waqf", (13, 23, 8), (13, 21, 8), "يُّوصَلَ"),
    RegisterRow("lam_final_waqf", (13, 26, 14), (13, 25, 14), "يُّوصَلَ"),
    RegisterRow("lam_final_waqf", (16, 58, 5), (16, 58, 5), "ظَلَّ"),
    RegisterRow("lam_final_waqf", (38, 19, 5), (38, 20, 5), "وَفَصْلَ"),
    RegisterRow("lam_final_waqf", (43, 16, 8), (43, 17, 8), "ظَلَّ"),
    RegisterRow("lam_salsal", (15, 26, 5), (15, 26, 5), "صَلْصَٰلٖ"),
    RegisterRow("lam_salsal", (15, 28, 9), (15, 28, 9), "صَلْصَٰلٖ"),
    RegisterRow("lam_salsal", (15, 33, 8), (15, 33, 8), "صَلْصَٰلٖ"),
    RegisterRow("lam_salsal", (55, 12, 4), (55, 14, 4), "صَلْصَٰلٖ"),
)


def test_the_runtime_register_matches_the_independent_source_fixture():
    actual = tuple(
        RegisterRow(
            site.owner,
            (site.source.surah, site.source.ayah, site.source.word),
            (site.canonical.surah, site.canonical.ayah, site.canonical.word),
            site.text,
            site.lam,
        )
        for site in SITES
    )

    assert actual == ROWS


def _entry(row: RegisterRow):
    location = Location(*row.canonical)
    return corpus().entries[corpus().canonical_to_runtime[location]]


@pytest.mark.parametrize("row", ROWS, ids=lambda row: f"{row.owner}-{row.canonical}")
def test_every_finite_lam_row_preserves_exact_selected_source_alignment(row):
    entry = _entry(row)

    assert entry.text == row.text
    assert entry.canonical == (Location(*row.canonical),)
    assert entry.sources[0].location == SourceLocation(ARTIFACT, *row.source)


@pytest.mark.parametrize("row", ROWS, ids=lambda row: f"{row.owner}-{row.canonical}")
def test_every_finite_lam_target_projects_as_the_authored_canonical_lam(row):
    location = Location(*row.canonical)
    entry = _entry(row)
    reading = script_adapter(Script.UTHMANI).read(
        location.verse, ((location, entry.text),)
    )
    projected_lams = [
        cluster for cluster in reading.clusters if cluster.letter is CanonLetter.LAM
    ]

    assert len(projected_lams) >= row.lam
    assert projected_lams[row.lam - 1].letter is CanonLetter.LAM
    assert reading.graphemes[projected_lams[row.lam - 1].offset].char == "ل"


@pytest.mark.parametrize(
    ("ref", "text", "before", "target"),
    (
        ((2, 157, 3), "صَلَوَٰتٮ", "صَلَ", Quality.A),
        ((2, 160, 4), "وَأَصْلَحُواْ", "صْلَ", Quality.A),
        ((2, 230, 2), "طَلَّقَهَا", "طَلَّ", Quality.A),
        ((97, 5, 4), "مَطْلَعِ", "طْلَ", Quality.A),
        ((2, 54, 7), "ظَلَمْتُمُۥٓ", "ظَلَ", Quality.A),
        ((2, 272, 28), "تُظْلَمُونَۖ", "ظْلَ", Quality.A),
    ),
)
def test_the_six_direct_source_families_project_without_a_color_hint(
    ref, text, before, target
):
    location = Location(*ref)
    entry = _entry(RegisterRow("ordinary", ref, ref, text))
    package = recitation(Riwayah.WARSH)
    words = package.words(location.verse)
    score = package.build(
        package.read(Script.UTHMANI, location.verse, words)
    ).score
    word = score.words[location.word - 1]
    lam = next(slot for slot in word.slots if slot.letter is CanonLetter.LAM)

    assert before in entry.text
    assert "۪" not in before
    assert lam.nucleus.quality is target


@pytest.mark.parametrize(
    ("ref", "text"),
    (
        ((2, 25, 5), "اُ۬لصَّٰلِحَٰتِ"),
        ((3, 191, 17), "بَٰطِلاٗ"),
        ((2, 210, 8), "ظُلَلٖ"),
        ((2, 264, 27), "صَلْداٗۖ"),
    ),
)
def test_dangerous_source_lookalikes_remain_ordinary_projection(ref, text):
    location = Location(*ref)
    entry = _entry(RegisterRow("lookalike", ref, ref, text))
    reading = script_adapter(Script.UTHMANI).read(
        location.verse, ((location, entry.text),)
    )

    assert entry.text == text
    assert any(cluster.letter is CanonLetter.LAM for cluster in reading.clusters)
    assert all(mark.role != "tafkheem" for cluster in reading.clusters for mark in cluster.marks)
