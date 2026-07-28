"""The Ledger loader's rejection cases, one test each.

Each test states its falsifier: if the loader stops raising, an authored
file could quietly become the authority for a fact it should only witness.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from quranic_phonemizer.canon.ledger import LedgerError, load_ledger
from quranic_phonemizer.model.address import Riwayah, Script
from quranic_phonemizer.model.canon import CanonLetter, Onset, Quality
from quranic_phonemizer.model.inscription import SlotFact

HEADER = "schema_version: 1\nriwayah: hafs\n"

VALID_SUPPLY = """
supplies:
  - {slot: "2:245:14#5", skeleton: "ويبصط", fact: LETTER, value: SEEN,
     citation: "Shatibiyyah; khilaf site 1 of 4"}
"""


def write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "ledger.yaml"
    path.write_text(HEADER + textwrap.dedent(body), encoding="utf-8")
    return path


def test_loads_a_well_formed_file(tmp_path: Path) -> None:
    ledger = load_ledger(write(tmp_path, VALID_SUPPLY), riwayah=Riwayah.HAFS)
    (supply,) = ledger.supplies
    assert supply.fact is SlotFact.LETTER
    assert supply.value is CanonLetter.SEEN
    assert supply.citation.startswith("Shatibiyyah")


def test_parses_every_canonical_value_shape(tmp_path: Path) -> None:
    ledger = load_ledger(
        write(
            tmp_path,
            """
            supplies:
              - {slot: "27:36:8#7", skeleton: "ءاتىن", fact: ONSET,
                 value: SILAH, citation: "Hafs; pronoun ya dropped at waqf"}
              - {slot: "2:2#1", skeleton: "ءلم", fact: NUCLEUS,
                 value: {kind: PausalLong, quality: A}, citation: "seven alifs"}
              - {slot: "18:1#9", skeleton: "عوجا", fact: SAKT,
                 value: true, citation: "Hafs sakt"}
            """,
        ),
        riwayah=Riwayah.HAFS,
    )
    onset, nucleus, sakt = ledger.supplies
    assert onset.value is Onset.SILAH
    assert nucleus.value.quality is Quality.A
    assert sakt.value is True


def test_rejects_a_duplicate_supply_for_one_key(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        """
        supplies:
          - {slot: "2:245#17", skeleton: "ويبصط", fact: LETTER, value: SEEN,
             citation: "one"}
          - {slot: "2:245#17", skeleton: "ويبصط", fact: LETTER, value: SAD,
             citation: "two"}
        """,
    )
    with pytest.raises(LedgerError, match="two supplies"):
        load_ledger(path, riwayah=Riwayah.HAFS)


def test_rejects_a_value_outside_the_canonical_vocabulary(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        """
        supplies:
          - {slot: "2:245#17", skeleton: "ويبصط", fact: LETTER, value: PEH,
             citation: "not an Arabic letter"}
        """,
    )
    with pytest.raises(LedgerError, match="not a CanonLetter"):
        load_ledger(path, riwayah=Riwayah.HAFS)


def test_rejects_an_orphan_assert(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        """
        asserts:
          - {script: uthmani, slot: "2:245#17", skeleton: "ويبصط",
             fact: LETTER, value: SEEN}
        """,
    )
    with pytest.raises(LedgerError, match="no supply to agree with"):
        load_ledger(path, riwayah=Riwayah.HAFS)


def test_accepts_an_assert_that_has_a_supply(tmp_path: Path) -> None:
    ledger = load_ledger(
        write(
            tmp_path,
            """
            supplies:
              - {slot: "2:245#17", skeleton: "ويبصط", fact: LETTER,
                 value: SEEN, citation: "Shatibiyyah"}
            asserts:
              - {script: uthmani, slot: "2:245#17", skeleton: "ويبصط",
                 fact: LETTER, value: SEEN}
            """,
        ),
        riwayah=Riwayah.HAFS,
    )
    (witness,) = ledger.asserts
    assert witness.script is Script.UTHMANI


@pytest.mark.parametrize("key", ["2:245:14", "chapter two", "2:245#x", "#5"])
def test_rejects_a_key_that_is_not_a_slot_id(tmp_path: Path, key: str) -> None:
    path = write(
        tmp_path,
        f"""
        supplies:
          - {{slot: "{key}", skeleton: "ويبصط", fact: LETTER, value: SEEN,
             citation: "c"}}
        """,
    )
    with pytest.raises(LedgerError, match="not a SlotId"):
        load_ledger(path, riwayah=Riwayah.HAFS)


def test_rejects_a_missing_skeleton(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        """
        supplies:
          - {slot: "2:245#17", skeleton: "  ", fact: LETTER, value: SEEN,
             citation: "c"}
        """,
    )
    with pytest.raises(LedgerError, match="skeleton"):
        load_ledger(path, riwayah=Riwayah.HAFS)


def test_rejects_a_value_in_output_vocabulary(tmp_path: Path) -> None:
    """A phoneme string belongs to the output vocabulary, not the Ledger's."""
    path = write(
        tmp_path,
        """
        supplies:
          - {slot: "2:245#17", skeleton: "ويبصط", fact: LETTER, value: "sˤ",
             citation: "c"}
        """,
    )
    with pytest.raises(LedgerError, match="output vocabulary"):
        load_ledger(path, riwayah=Riwayah.HAFS)


def test_rejects_an_unknown_schema_version(tmp_path: Path) -> None:
    path = tmp_path / "ledger.yaml"
    path.write_text("schema_version: 2\nriwayah: hafs\n", encoding="utf-8")
    with pytest.raises(LedgerError, match="schema_version"):
        load_ledger(path, riwayah=Riwayah.HAFS)


def test_rejects_a_ledger_authored_for_another_riwayah(tmp_path: Path) -> None:
    """Falsifier: the key was required present but never read, so a ledger
    for another reading supplied its facts to this one."""
    path = tmp_path / "ledger.yaml"
    path.write_text("schema_version: 1\nriwayah: warsh\n", encoding="utf-8")
    with pytest.raises(LedgerError, match="not a Riwayah"):
        load_ledger(path, riwayah=Riwayah.HAFS)


def test_rejects_a_duplicate_yaml_key(tmp_path: Path) -> None:
    path = tmp_path / "ledger.yaml"
    path.write_text(HEADER + "riwayah: warsh\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate YAML key"):
        load_ledger(path, riwayah=Riwayah.HAFS)


def test_an_entry_for_this_verse_that_does_not_resolve_is_an_error(
    packed, hafs
) -> None:
    """An unresolvable ledger address is an error, not a skip.

    Falsifier: if `_apply_ledger` skips an unresolvable address instead of
    raising, the skeleton check behind it never runs.
    """
    from conftest import words_of

    from quranic_phonemizer.canon.build import build
    from quranic_phonemizer.canon.passes import LedgerAddressError
    from quranic_phonemizer.canon.ledger import Ledger, Supply, WordSlot
    from quranic_phonemizer.model.address import Location, Script, VerseRef
    from quranic_phonemizer.model.canon import Long
    from quranic_phonemizer.riwayat.hafs import script_adapter

    reading = script_adapter(Script.UTHMANI).read(
        VerseRef(112, 2), words_of(packed, 112, 2)
    )
    beyond = Ledger(
        supplies=(
            Supply(
                ref=WordSlot(Location(112, 2, 1), 99),
                skeleton="ءلله",
                fact=SlotFact.NUCLEUS,
                value=Long(Quality.A),
                citation="deliberately out of range",
            ),
        ),
        asserts=(),
    )
    with pytest.raises(LedgerAddressError, match="does not resolve"):
        build(reading, lexicon=hafs.lexicon, ledger=beyond)


def test_an_entry_for_another_verse_is_not_an_error(packed, hafs) -> None:
    """The two meanings of an unresolved address must stay separate, or every
    verse raises on every other verse's entries."""
    from conftest import words_of

    from quranic_phonemizer.canon.build import build
    from quranic_phonemizer.canon.ledger import Ledger, Supply, WordSlot
    from quranic_phonemizer.model.address import Location, Script, VerseRef
    from quranic_phonemizer.model.canon import Long
    from quranic_phonemizer.riwayat.hafs import script_adapter

    reading = script_adapter(Script.UTHMANI).read(
        VerseRef(112, 2), words_of(packed, 112, 2)
    )
    elsewhere = Ledger(
        supplies=(
            Supply(
                ref=WordSlot(Location(2, 1, 1), 99),
                skeleton="whatever",
                fact=SlotFact.NUCLEUS,
                value=Long(Quality.A),
                citation="a different verse entirely",
            ),
        ),
        asserts=(),
    )
    build(reading, lexicon=hafs.lexicon, ledger=elsewhere)
