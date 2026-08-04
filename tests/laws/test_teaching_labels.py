"""Each predicate is checked against a specific instance of Ayat al-Kursi so
reverting `phonemize/labels.py` fails these rather than emptying a set."""
from __future__ import annotations

from quranic_phonemizer import Phonemizer
from quranic_phonemizer.model.canon import CanonLetter, Rule


def test_silah_labels_a_madd_on_the_pronoun_haas_vowel():
    r = Phonemizer().phonemize("2:255")
    instance = r.rules[34]
    assert instance.rule is Rule.MADD_TABII
    assert instance.labels == ("silah",)
    assert r.units[instance.source].vowel.is_silah


def test_silah_kubra_labels_only_a_madd_jaiz_munfasil_silah():
    r = Phonemizer().phonemize("2:255")
    instance = r.rules[48]
    assert instance.rule is Rule.MADD_JAIZ_MUNFASIL
    assert instance.labels == ("silah", "silah_kubra")


def test_madd_badal_labels_a_madd_on_a_hamza():
    r = Phonemizer().phonemize("2:255")
    instance = r.rules[64]
    assert instance.rule is Rule.MADD_TABII
    assert instance.labels == ("madd_badal",)
    assert r.units[instance.source].letter is CanonLetter.HAMZA


def test_labels_mint_no_instance_of_their_own():
    """Applying labels twice is idempotent: no row is added either time."""
    from quranic_phonemizer.phonemize.labels import with_labels

    r = Phonemizer().phonemize("2:255")
    twice = with_labels(r.rules, r.units)
    assert len(twice) == len(r.rules)
    assert twice == r.rules
    assert any(instance.labels for instance in r.rules)


def test_only_three_labels_are_ever_produced():
    """Only three labels exist. `iwad`'s length is on its own occurrence, so
    no madd instance is ever left to carry a fourth."""
    r = Phonemizer().phonemize("2:255")
    seen = {label for instance in r.rules for label in instance.labels}
    assert seen <= {"madd_badal", "silah", "silah_kubra"}
    assert "madd_iwad" not in seen


def test_a_rule_outside_the_madd_family_never_takes_a_label():
    r = Phonemizer().phonemize("2:255")
    assert all(
        instance.labels == ()
        for instance in r.rules
        if instance.rule not in (
            Rule.MADD_TABII, Rule.MADD_WAJIB_MUTTASIL,
            Rule.MADD_JAIZ_MUNFASIL, Rule.MADD_LAZIM, Rule.MADD_ARID_LIL_SUKUN,
        )
    )
