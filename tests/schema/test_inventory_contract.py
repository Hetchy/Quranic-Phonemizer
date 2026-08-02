"""The Python-to-YAML role contract for script inventories.

`Cluster.has(role)` returns `False` for an undeclared role rather than
raising, so a typo in a role name can silently change output.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from quranic_phonemizer.canon import derive
from quranic_phonemizer.model.address import Location, Script, VerseRef
from quranic_phonemizer.model.canon import CanonLetter
from quranic_phonemizer.orthography.cluster import read_verse
from quranic_phonemizer.orthography.inventory import InventoryError, load_inventory
from quranic_phonemizer.riwayat.hafs.resources import DATA, RIWAYAH, SCRIPTS

#: IndoPak spells `ئ` as a yaa carrying a combining hamza, so the yaa is the
#: shortest word in either script that reaches the seat branch.
SEATED_HAMZA = "ئ"

CONTRACT = {
    "riwayah": RIWAYAH,
    "derivations": frozenset(derive.registered()),
    "roles": derive.required_roles(),
}


def _inventory_text(script: Script) -> str:
    return (DATA / "scripts" / f"{script.value}.yaml").read_text(encoding="utf-8")


def _load(tmp_path: Path, text: str, script: Script = Script.UTHMANI):
    path = tmp_path / "inventory.yaml"
    path.write_text(text, encoding="utf-8")
    return load_inventory(path, script=script, **CONTRACT)


@pytest.mark.parametrize("script", SCRIPTS)
def test_the_shipped_inventories_satisfy_the_contract(script):
    _load_ok = load_inventory(
        DATA / "scripts" / f"{script.value}.yaml", script=script, **CONTRACT
    )
    assert _load_ok.marks


def test_an_inventory_loaded_as_the_wrong_script_is_rejected(tmp_path):
    """Falsifier: without this the loader believes the caller, so a Score
    would record a script the file never claimed to describe."""
    with pytest.raises(InventoryError, match="loaded as"):
        _load(tmp_path, _inventory_text(Script.UTHMANI), script=Script.INDOPAK)


@pytest.mark.parametrize("role", ["fatha", "shadda", "sukun", "dagger"])
def test_a_renamed_role_is_a_load_error(tmp_path, role):
    """Falsifier: if this stops raising, a one-character slip in a script
    inventory becomes a silent output change instead of a startup failure."""
    original = _inventory_text(Script.UTHMANI)
    text = original.replace(f"role: {role},", f"role: {role}_typo,")
    assert text != original, f"the fixture no longer writes `role: {role},`"
    with pytest.raises(InventoryError, match=role):
        _load(tmp_path, text)


def test_an_unregistered_derivation_is_a_load_error(tmp_path):
    """An unregistered derivation must fail at load time, not on first use."""
    text = _inventory_text(Script.UTHMANI).replace(
        "derivation: length_a", "derivation: no_such_thing", 1
    )
    with pytest.raises(InventoryError, match="no_such_thing"):
        _load(tmp_path, text)


def test_a_script_specific_role_is_not_required_of_every_script(tmp_path):
    """`cross_word_noon` is IndoPak's convention and `small_ya` is Uthmani's.
    Requiring either globally rejects a script for not writing something it
    does not write, so the contract is checked per named derivation."""
    read = derive.required_roles()
    assert "cross_word_noon" not in read.get("carrier", frozenset())
    _load(tmp_path, _inventory_text(Script.UTHMANI))
    _load(tmp_path, _inventory_text(Script.INDOPAK), Script.INDOPAK)


def _first_letter(inventory, text: str) -> CanonLetter | None:
    reading = read_verse(
        inventory, VerseRef(1, 1), ((Location(1, 1, 1), text),)
    )
    return reading.clusters[0].letter


def test_a_hamza_written_on_a_seat_becomes_the_hamza(tmp_path):
    """The behaviour `SEATABLE` used to carry, now read off the script."""
    inventory = _load(tmp_path, _inventory_text(Script.INDOPAK), Script.INDOPAK)
    assert _first_letter(inventory, SEATED_HAMZA) is CanonLetter.HAMZA


def test_a_scalar_the_script_does_not_call_a_seat_does_not_fold(tmp_path):
    """Falsifier: without the flag being read, every carrier is seatable
    again and the script has no say -- which is what put four Hafs glyphs in
    a Python frozenset to begin with."""
    text = _inventory_text(Script.INDOPAK).replace(
        '"ي": {letter: YA, bare_rasm: true, seat: true}',
        '"ي": {letter: YA, bare_rasm: true}',
    )
    inventory = _load(tmp_path, text, Script.INDOPAK)
    assert _first_letter(inventory, SEATED_HAMZA) is not CanonLetter.HAMZA


def test_an_unknown_capability_is_a_load_error(tmp_path):
    """A capability the loader does not know is a misspelling, and a
    misspelled flag that parses is a capability silently switched off."""
    text = _inventory_text(Script.INDOPAK).replace("seat: true", "seet: true", 1)
    with pytest.raises(ValueError, match="seet"):
        _load(tmp_path, text, Script.INDOPAK)


def test_the_registry_is_complete_without_importing_the_builder():
    """The registry must be populated without importing `canon.build`, or a
    validator that inspects it first would see it empty."""
    assert len(derive.registered()) >= 12
    assert "length_a" in derive.registered()
