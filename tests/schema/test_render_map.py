"""The output alphabet: total by coverage, and closed against wrong tuples.

Totality used to be the row count. It is now these two claims: every tuple
the model can produce resolves, and every tuple it cannot raises.
"""
from __future__ import annotations

import itertools
from pathlib import Path

import pytest

from quranic_phonemizer.model.canon import CanonLetter as L
from quranic_phonemizer.model.canon import Quality
from quranic_phonemizer.model.performance import Consonant, Degree, Release, Vowel
from quranic_phonemizer.render.alphabet import NotationError, load_alphabet
from quranic_phonemizer.riwayat.hafs.resources import rule_tables
from quranic_phonemizer.rules.tafkheem import CONDITIONAL

#: Which letters emphasis can reach, from the two inputs `Emphasis` itself is
#: built from rather than restated here. If the rule's reach changes and the
#: alphabet does not, the coverage test below is what fails.
HEAVY_CAPABLE = frozenset(rule_tables().always_heavy | CONDITIONAL)

#: The four a ghunnah can be held on: the letters a noon or a meem merges
#: into. Nothing else is ever written nasalized.
NASALIZED = frozenset({L.NOON, L.MEEM, L.WAW, L.YA})

#: The one letter `eased` reaches, the corpus site `41:44:9`.
EASED = frozenset({L.HAMZA})


def _consonants():
    return [
        Consonant(letter, geminate=g, emphatic=e, ghunnah=n, eased=z)
        for letter in L
        for g, e, n, z in itertools.product((False, True), repeat=4)
    ]


def _vowels():
    return [
        Vowel(quality, long=lo, emphatic=e)
        for quality in Quality
        for lo, e in itertools.product((False, True), repeat=2)
    ]


def _legal(sound) -> bool:
    """What the model can actually produce, stated independently of the data."""
    match sound:
        case Consonant():
            if sound.ghunnah and sound.letter not in NASALIZED:
                return False
            if sound.eased and sound.letter not in EASED:
                return False
            if not sound.emphatic:
                return True
            # A heavy hum only ever rides the noon; a plain heavy consonant
            # only ever one of tafkheem's own nine.
            return sound.letter is L.NOON if sound.ghunnah else (
                sound.letter in HEAVY_CAPABLE
            )
        case Vowel():
            return not sound.emphatic or sound.quality is Quality.A
    return True


# -- totality and its complement ------------------------------------------
def test_every_producible_tuple_resolves(alphabet):
    """The claim the row count used to make."""
    unresolved = []
    for sound in [*_consonants(), *_vowels(), *[Release(d) for d in Degree]]:
        if not _legal(sound):
            continue
        try:
            assert alphabet.token(sound)
        except NotationError:
            unresolved.append(sound)
    assert not unresolved, f"producible but unwritable: {unresolved}"


def test_every_impossible_tuple_raises(alphabet):
    """Falsifier: without this, a suffix rule could answer for every tuple and
    `NotationError` would be unreachable -- which is what makes a wrong sound
    loud instead of plausible."""
    answered = []
    for sound in [*_consonants(), *_vowels()]:
        if _legal(sound):
            continue
        try:
            answered.append((sound, alphabet.token(sound)))
        except NotationError:
            pass
    assert not answered, f"impossible tuples given a token: {answered}"


def test_emphasis_is_offered_exactly_where_the_rule_can_reach(alphabet):
    """The alphabet's emphatic entries and tafkheem's reach are one claim."""
    offered = {
        letter for letter, entry in alphabet.consonants.items() if entry.emphatic
    }
    assert offered == HEAVY_CAPABLE


def test_nasal_is_offered_exactly_where_a_ghunnah_can_be_held(alphabet):
    offered = {
        letter for letter, entry in alphabet.consonants.items() if entry.nasal
    }
    assert offered == NASALIZED


def test_the_hum_and_heavy_hum_are_offered_on_the_noon_alone(alphabet):
    """The noon is the one letter a ghunnah holds with no letter under it,
    so it is the one letter that needs a token distinct from `nasal`."""
    hum = {letter for letter, entry in alphabet.consonants.items() if entry.hum}
    heavy = {
        letter for letter, entry in alphabet.consonants.items() if entry.heavy_hum
    }
    assert hum == heavy == {L.NOON}


def test_eased_is_offered_exactly_on_the_hamza(alphabet):
    offered = {
        letter for letter, entry in alphabet.consonants.items() if entry.eased
    }
    assert offered == EASED


# -- the composition rules ------------------------------------------------
def test_gemination_says_the_consonant_twice(alphabet):
    assert alphabet.token(Consonant(L.BA)) == "b"
    assert alphabet.token(Consonant(L.BA, geminate=True)) == "bb"
    assert alphabet.token(Consonant(L.RA, geminate=True, emphatic=True)) == "rˤrˤ"


def test_gemination_separates_the_two_noon_hums(alphabet):
    """A held ghunnah and the hum with no letter to hold it are different
    sounds, told apart only by gemination."""
    hum = alphabet.token(Consonant(L.NOON, ghunnah=True))
    held = alphabet.token(Consonant(L.NOON, ghunnah=True, geminate=True))
    assert (hum, held) == ("ŋ", "ñ")


def test_a_letter_with_one_ghunnah_token_reads_it_either_way(alphabet):
    """Meem, waw and yaa never need the noon's split: the same held sound
    is what an un-geminated ghunnah on them writes too."""
    hum = alphabet.token(Consonant(L.MEEM, ghunnah=True))
    held = alphabet.token(Consonant(L.MEEM, ghunnah=True, geminate=True))
    assert hum == held == "m̃"


def test_a_heavy_hum_is_offered_but_not_yet_spent(alphabet):
    """Composed only once `emphatic_ikhfaa` exists to ask for it; until then
    the plain hum answers, same as `eased`."""
    assert alphabet.consonants[L.NOON].heavy_hum == "ŋˤ"
    assert alphabet.token(Consonant(L.NOON, ghunnah=True, emphatic=True)) == "ŋ"


def test_an_inherently_emphatic_letter_reads_the_same_either_way(alphabet):
    """The emphasis is already in the plain token, so the axis adds nothing."""
    assert alphabet.token(Consonant(L.SAD)) == alphabet.token(
        Consonant(L.SAD, emphatic=True)
    )


def test_length_follows_the_emphatic_colouring(alphabet):
    assert alphabet.token(Vowel(Quality.A)) == "a"
    assert alphabet.token(Vowel(Quality.A, long=True)) == "a:"
    assert alphabet.token(Vowel(Quality.A, emphatic=True, long=True)) == "aˤ:"


# -- coverage, checked at load --------------------------------------------
def _text() -> str:
    root = Path(__file__).resolve().parents[2]
    return (
        root / "quranic_phonemizer" / "data" / "render" / "ipa.yaml"
    ).read_text(encoding="utf-8")


def _load(tmp_path: Path, text: str):
    path = tmp_path / "notation.yaml"
    path.write_text(text, encoding="utf-8")
    return load_alphabet(path)


def test_a_letter_with_no_entry_is_a_load_error(tmp_path):
    """Falsifier for the guarantee that replaced the row count: adding a
    letter to `CanonLetter` must be one entry here, and forgetting it must
    fail at load rather than on the verse that first needs it."""
    text = _text().replace('  jeem: "ʒ"\n', "")
    assert text != _text()
    with pytest.raises(NotationError, match="jeem"):
        _load(tmp_path, text)


def test_an_entry_naming_no_letter_is_a_load_error(tmp_path):
    """The other direction: a letter the model has since dropped."""
    text = _text().replace('  jeem: "ʒ"\n', '  jeem: "ʒ"\n  jeeem: "ʒ"\n')
    with pytest.raises(NotationError, match="jeeem"):
        _load(tmp_path, text)


def test_the_schema_version_is_checked(tmp_path):
    with pytest.raises(NotationError, match="schema_version"):
        _load(tmp_path, _text().replace("schema_version: 2", "schema_version: 1"))
