"""Words the two scripts write differently and must still read the same.

One site per orthographic difference, with the reading spelled out, so a
regression names the phenomenon rather than moving a percentage.
"""
from __future__ import annotations

import pytest

from conftest import sources  # noqa: F401  (fixture)
from quranic_phonemizer.canon.build import build
from quranic_phonemizer.engine.run import perform
from quranic_phonemizer.model.address import (
    BoundaryPlan,
    Junction,
    Script,
    VerseRef,
)
from quranic_phonemizer.render.recite import phonemes_by_word
from quranic_phonemizer.riwayat.hafs import HAFS, script_adapter

#: (surah, ayah, word), the reading, and what the two scripts disagree about.
SITES = [
    ((2, 1, 1), "ʔalifla:m̃i:m", "the muqattaat: IndoPak marks them its own way"),
    ((2, 61, 52), "ʔañabijji:n", "the small yaa sits on the shadda in IndoPak"),
    ((4, 7, 7), "waliñisa:ʔ", "the article after a lam proclitic and a waw"),
    ((6, 143, 10), "ʔa:ððakarˤaˤjn", "the article after an interrogative hamza"),
    ((8, 63, 1), "waʔallaf", "IndoPak writes hamzat qat as a bare alif"),
    ((12, 87, 14), "jajʔas", "the alif inside a leen, marked only by Uthmani"),
    ((22, 72, 23), "ʔaña:rˤ", "IndoPak writes the article's helping vowel"),
    ((12, 101, 14), "walijji:", "a small yaa on a doubled yaa is its vowel"),
    ((46, 33, 15), "juħji:", "a small yaa that is a consonant, not a length"),
    ((56, 23, 2), "ʔalluʔluʔ", "IndoPak writes the hamza's seat out"),
    ((35, 43, 5), "ʔassajjiʔ", "the seat is a maqsura, and silent"),
    ((2, 72, 4), "fadda:rˤaˤʔtum", "a hamza drawn on a small alif, not on the raa"),
    ((41, 44, 9), "ʔaʔaʕʒamijj", "the facilitated hamza is voweled"),
    ((18, 16, 7), "faʔwu:", "a prosthetic hamza never carries a sukun"),
    ((49, 11, 29), "biʔs", "a carrier does not lengthen across a word boundary"),
    ((49, 11, 30), "ʔalism", "the article before a word that itself begins with a wasl"),
    ((68, 6, 1), "biʔajjikum", "IndoPak's maqsura spells no sound of its own"),
    ((46, 4, 18), "ʔi:tu:ni:", "a quiescent hamza after a prosthetic one, started on"),
    ((11, 41, 6), "maʒQri:ha:", "the imala, which only Uthmani marks"),
]


@pytest.mark.parametrize(("site", "reading", "difference"), SITES)
def test_both_scripts_read_the_same_word(
    sources, hafs, alphabet, site, reading, difference
) -> None:
    surah, ayah, word = site
    got = {
        script: "".join(
            _phonemes(sources, script, surah, ayah, hafs, alphabet)[word - 1]
        )
        for script in Script
    }
    assert got[Script.UTHMANI] == reading, difference
    assert got[Script.INDOPAK] == reading, difference


def _phonemes(sources, script, surah, ayah, hafs, alphabet,
              junction=Junction.STOP):
    words = sources[script][(surah, ayah)]
    score = hafs.build(hafs.read(script, VerseRef(surah, ayah), words)).score
    plan = BoundaryPlan(
        (junction,) * (len(score.words) - 1) + (Junction.EDGE,)
    )
    performance = hafs.perform(score, plan)
    return [list(w) for w in phonemes_by_word(performance, score, alphabet)]


def test_a_stem_writes_the_same_pair_of_lams_as_the_article(
    sources, hafs, alphabet
) -> None:
    """`زَلَلْتُمْ` is a voweled lam then a sakin one, the pair the article
    writes in `لِلنَّاسِ`. Only the head of the word tells them apart."""
    got = _phonemes(sources, Script.UTHMANI, 2, 209, hafs, alphabet)
    assert "".join(got[1]) == "zalaltum"


def test_the_silah_is_still_conditional(sources, hafs, alphabet) -> None:
    """The pronoun haa's vowel is a `Silah`, not a `Long`: it sounds joined
    and is absent at a stop. The small waw is a letter now, and that must
    not have turned it into an ordinary length."""
    for script in Script:
        joined = _phonemes(
            sources, script, 2, 26, hafs, alphabet, Junction.JOIN
        )
        assert "".join(joined[29]) == "bihi:", script
    stopped = {
        script: "".join(
            _phonemes(sources, script, 2, 26, hafs, alphabet)[29]
        )
        for script in Script
    }
    assert stopped[Script.UTHMANI] == stopped[Script.INDOPAK] == "bih"
