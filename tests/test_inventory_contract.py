"""The Python-to-YAML role contract for script inventories.

`Cluster.has(role)` returns `False` for an undeclared role rather than
raising, so a typo in a role name can silently change output.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from quranic_phonemizer.canon import derive
from quranic_phonemizer.model.address import Script
from quranic_phonemizer.orthography.inventory import InventoryError, load_inventory
from quranic_phonemizer.riwayat.hafs.resources import DATA, RIWAYAH, SCRIPTS

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


def test_the_registry_is_complete_without_importing_the_builder():
    """The registry must be populated without importing `canon.build`, or a
    validator that inspects it first would see it empty."""
    assert len(derive.registered()) >= 12
    assert "length_a" in derive.registered()
