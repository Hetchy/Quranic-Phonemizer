"""`madd_tabii` applies to ordinary cases: an instance, never a new sound."""
from __future__ import annotations

from conftest import score_for
from quranic_phonemizer.engine.run import perform
from quranic_phonemizer.model.address import BoundaryPlan, Junction
from quranic_phonemizer.model.canon import Rule
from quranic_phonemizer.model.performance import Aspect, Hosts, MergedInto
from quranic_phonemizer.phonemize.legacy_views import phonemes_by_word
from quranic_phonemizer.riwayat.hafs import HAFS


def _stopped_on(score, word_number: int) -> BoundaryPlan:
    return BoundaryPlan(
        tuple(
            Junction.STOP if word == word_number - 1 else Junction.JOIN
            for word in range(len(score.words) - 1)
        )
        + (Junction.EDGE,)
    )


def test_an_ordinary_mid_word_long_vowel_takes_madd_tabii(packed, hafs) -> None:
    """1:1 word 2, `ٱللَّهِ`: the long alif is not adjacent to a hamza or a
    sakin, so nothing but the default outcome applies to it."""
    score = score_for(packed, hafs, 1, 1)
    long_vowel = next(
        s for s in score.words[1].slots if s.nucleus.is_long
    )
    plan = BoundaryPlan((Junction.JOIN,) * (len(score.words) - 1) + (Junction.EDGE,))
    performance = perform(score, HAFS, plan)
    rules = {o.rule for o in performance.occurrences if o.parts.source == long_vowel.id}
    assert Rule.MADD_TABII in rules


def test_a_stopped_pausal_alif_takes_madd_tabii_over_its_own_realization(
    packed, hafs, alphabet
) -> None:
    """Word 21 here, `أَنَا۠`: `WaqfEnding` realizes the long vowel;
    `madd_tabii` only names its length, so the token does not double."""
    score = score_for(packed, hafs, 2, 258)
    alif = score.words[20].slots[-1]
    plan = _stopped_on(score, 21)
    performance = perform(score, HAFS, plan)

    rules = {o.rule for o in performance.occurrences if o.parts.source == alif.id}
    assert Rule.MADD_TABII in rules

    hosts = [
        a for a in performance.attributions
        if isinstance(a, Hosts) and alif.id in a.slots and a.aspect is Aspect.VOWEL
    ]
    assert len(hosts) == 1, "one sound per aspect, not a second realization"

    word = "".join(phonemes_by_word(performance, score, alphabet)[20])
    assert word == "ʔana:"


def test_madd_tabii_names_the_vowel_it_lengthens_and_nothing_else() -> None:
    """20:1, `طه`: the rule holds the alif for two counts and says nothing
    about the taa before it, so its edge names one sound of the two."""
    from quranic_phonemizer import Phonemizer
    from quranic_phonemizer.phonemize import edges as ed

    result = Phonemizer().phonemize("20:1")
    named = {
        m.sound for m in result.modifiers
        if result.rules[m.by].rule is Rule.MADD_TABII
        and isinstance(m, ed.Classifies)
    }
    assert named == {1, 3}  # tˤ a: h a: -- the two alifs, neither consonant


def test_a_stopped_final_glide_takes_madd_tabii_over_its_own_consonant(
    packed, hafs
) -> None:
    """2:29:1, `هُوَ`: stopped, the waw merges into the damma before it
    rather than being said as its own consonant."""
    score = score_for(packed, hafs, 2, 29)
    heh, waw = score.words[0].slots
    plan = _stopped_on(score, 1)
    performance = perform(score, HAFS, plan)

    rules = {o.rule for o in performance.occurrences if o.parts.source == waw.id}
    assert Rule.MADD_TABII in rules

    merge = next(
        a for a in performance.attributions
        if isinstance(a, MergedInto) and waw.id in a.slots
    )
    host = next(
        a for a in performance.attributions
        if isinstance(a, Hosts) and heh.id in a.slots and a.aspect is Aspect.VOWEL
    )
    assert merge.sound == host.sound
