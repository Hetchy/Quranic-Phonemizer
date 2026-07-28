"""The composition root: one riwayah, assembled, and the calls it answers.

Nothing here decides anything. It exists so that a caller states a riwayah
once instead of gathering its adapters, data and rules by hand.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .canon.build import Built, Provenance, build
from .canon.ledger import Ledger
from .canon.lexicon import Lexicon
from .canon.passes import LexemePass
from .canon.spell import Muqattaat
from .corpus import PackedCorpus
from .engine.classifier import RuleSet
from .engine.run import perform
from .model.address import (
    BoundaryPlan,
    Location,
    Riwayah,
    Script,
    VariantSelection,
    VerseRef,
)
from .model.canon import Score
from .model.performance import Performance
from .orthography.adapter import Reading, ScriptAdapter
from .orthography.inventory import Inventory
from .render.alphabet import Alphabet, load_alphabet
from .riwayat import hafs
from .riwayat.khilaf import Khilaf

DATA = Path(__file__).resolve().parent / "data"

#: Every riwayah this build ships. Adding one is one row plus its package.
PACKAGES = {Riwayah.HAFS: hafs}


class UnknownRiwayah(ValueError):
    """Named rather than a KeyError, so the message lists what is shipped."""


@dataclass(frozen=True, slots=True)
class Recitation:
    """One riwayah's scripts, data and rules, already loaded."""

    riwayah: Riwayah
    scripts: tuple[Script, ...]
    rules: RuleSet
    corpus: PackedCorpus
    khilaf: Khilaf
    muqattaat: Muqattaat
    lexicon: Lexicon
    ledger: Ledger
    passes: tuple[LexemePass, ...]
    adapters: dict[Script, ScriptAdapter]

    def read(
        self,
        script: Script,
        verse: VerseRef,
        words: tuple[tuple[Location, str], ...],
    ) -> Reading:
        if script not in self.adapters:
            raise UnknownRiwayah(
                f"{self.riwayah.value} is packaged for "
                f"{[s.value for s in self.scripts]}, not {script.value}"
            )
        return self.adapters[script].read(verse, words)

    def inventory(self, script: Script) -> Inventory:
        return self.adapters[script].inventory

    def build(
        self,
        reading: Reading,
        *,
        selection: VariantSelection = VariantSelection(),
        right_context: Reading | None = None,
        provenance: Provenance | None = None,
    ) -> Built:
        return build(
            reading,
            lexicon=self.lexicon,
            ledger=self.ledger,
            passes=self.passes,
            selection=selection,
            right_context=right_context,
            provenance=provenance,
        )

    def perform(
        self,
        score: Score,
        boundaries: BoundaryPlan,
        *,
        selection: VariantSelection = VariantSelection(),
    ) -> Performance:
        return perform(score, self.rules, boundaries, selection=selection)

    def words(self, verse: VerseRef) -> tuple[tuple[Location, str], ...]:
        """The verse's words from the packed corpus, sized by `surah_info`."""
        count = self.corpus.surah_info[str(verse.surah)][verse.ayah - 1]
        return tuple(
            (location, self.corpus.word(location))
            for location in (
                Location(verse.surah, verse.ayah, index)
                for index in range(1, count + 1)
            )
        )


def recitation(riwayah: Riwayah) -> Recitation:
    """Load everything one riwayah needs. One call, one process-local copy."""
    package = PACKAGES.get(riwayah)
    if package is None:
        raise UnknownRiwayah(
            f"{riwayah.value} is not packaged; this build ships "
            f"{[r.value for r in PACKAGES]}"
        )
    return Recitation(
        riwayah=package.RIWAYAH,
        scripts=package.SCRIPTS,
        rules=package.rules_for(riwayah),
        corpus=package.corpus(),
        khilaf=package.khilaf(),
        muqattaat=package.muqattaat(),
        lexicon=package.lexicon(),
        ledger=package.ledger(),
        passes=package.lexeme_passes(),
        adapters=package.adapters_for(riwayah),
    )


def alphabet(notation: str = "ipa") -> Alphabet:
    """The output notation. Shared across riwayat: it names sounds, not
    readings, so it is not part of a `Recitation`."""
    return load_alphabet(DATA / "render" / f"{notation}.yaml")
