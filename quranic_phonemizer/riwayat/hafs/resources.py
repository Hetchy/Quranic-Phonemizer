"""Hafs: where its data lives, and how its adapters are assembled.

`riwayat` is the only package that may import anything, because it is the
assembly point. Nothing imports *it*, which is what keeps a second riwayah
additive: adding Warsh adds `riwayat/warsh/` plus its YAML and touches nothing
above (ADR-007 §1.1, §2).

Resources are **instance-local** (ADR-007 §4.12). Two riwayāt, two scripts and
two notations must coexist in one process, keyed by immutable identity — so
there is no module-level cache and no process-global override here.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from ...canon import derive
from ...canon.ledger import EMPTY as EMPTY_LEDGER
from ...canon.ledger import Ledger, load_ledger
from ...canon.lexicon import EMPTY as EMPTY_LEXICON
from ...canon.lexicon import Lexicon, load_lexicon
from ...canon.spell import Names, load_names
from ...corpus import PackedCorpus, load_corpus
from ...model.address import Location, Riwayah, Script, VerseRef
from ...orthography.adapter import Reading
from ...orthography.cluster import read_verse
from ...orthography.inventory import Inventory, load_inventory

RIWAYAH = Riwayah.HAFS
DATA = Path(__file__).resolve().parents[2] / "data" / "riwayat" / "hafs"


@dataclass(frozen=True, slots=True)
class Adapter:
    """One script of one riwayah. The whole of its script knowledge is the
    `Inventory` it holds; the code below is shared with every other script."""

    script: Script
    inventory: Inventory

    def read(
        self, verse: VerseRef, words: tuple[tuple[Location, str], ...]
    ) -> Reading:
        return read_verse(self.inventory, verse, words)


@lru_cache(maxsize=None)
def _inventory(script: Script) -> Inventory:
    """The assembly point is where the two halves of the role contract meet.

    `orthography` cannot import `canon`, so what a derivation needs from an
    inventory is passed in here rather than looked up there.
    """
    return load_inventory(
        DATA / "scripts" / f"{script.value}.yaml",
        derivations=frozenset(derive.registered()),
        roles=derive.required_roles(),
    )


def script_adapter(script: Script) -> Adapter:
    return Adapter(script=script, inventory=_inventory(script))


def adapters_for(riwayah: Riwayah) -> dict[Script, Adapter]:
    if riwayah is not RIWAYAH:
        raise ValueError(f"{__name__} assembles {RIWAYAH.value}, not {riwayah.value}")
    return {script: script_adapter(script) for script in Script}


def ledger() -> Ledger:
    path = DATA / "ledger.yaml"
    return load_ledger(path) if path.exists() else EMPTY_LEDGER


def lexicon() -> Lexicon:
    path = DATA / "lexicon.yaml"
    return load_lexicon(path) if path.exists() else EMPTY_LEXICON


def letter_names() -> Names:
    """Shared across riwayat: what a letter is *called* is a fact about Arabic."""
    return load_names(DATA.parents[1] / "shared" / "muqattaat.yaml")


def lexeme_passes() -> tuple:
    """Hafs' verse-level passes, in order.

    The riwayah owns this list the way it owns its `RuleSet`. `canon` supplies
    the shared two; spelling the muqaṭṭaʿāt needs the letter-name table, so it
    is bound here rather than reached for from inside the builder.
    """
    from ...canon.passes import LEXEME_PASSES
    from ...canon.spell import spell_muqattaat

    return (*LEXEME_PASSES, spell_muqattaat(letter_names()))


def corpus() -> PackedCorpus:
    return load_corpus(DATA / "corpus" / "quran_db.bin",
                       DATA / "corpus" / "surah_info.json")
