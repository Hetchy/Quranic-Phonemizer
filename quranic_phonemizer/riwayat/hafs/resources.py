"""Hafs: where its data lives, and how its adapters are assembled.

Resources are instance-local: two riwayat, two scripts, and two notations
can coexist in one process, so there is no module-level cache here.
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
from ...canon.spell import Muqattaat, load_muqattaat
from ...corpus import PackedCorpus, load_corpus
from ...model.address import Location, Riwayah, Script, VerseRef
from ..tables import RuleTables, load_rule_tables
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


def rule_tables() -> RuleTables:
    """Shared tajweed tables, plus whatever this riwayah overrides."""
    shared = DATA.parents[1] / "shared" / "rules.yaml"
    return load_rule_tables(shared, DATA / "rules.yaml")


def muqattaat() -> Muqattaat:
    """Shared across riwayat: which openings are named, and what each letter is
    called, are facts about Arabic."""
    return load_muqattaat(DATA.parents[1] / "shared" / "muqattaat.yaml")


def lexeme_passes() -> tuple:
    """Hafs' verse-level passes, in order.

    `canon` supplies the shared two; spelling the muqattaat needs the
    opening and letter-name tables, so it is bound here instead.
    """
    from ...canon.passes import LEXEME_PASSES
    from ...canon.spell import spell_muqattaat

    return (*LEXEME_PASSES, spell_muqattaat(muqattaat()))


def corpus() -> PackedCorpus:
    return load_corpus(DATA / "corpus" / "quran_db.bin",
                       DATA / "corpus" / "surah_info.json")
