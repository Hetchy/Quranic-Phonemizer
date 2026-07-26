"""The canonical-skeleton lexicon: closed classes of Arabic, not of this corpus.

Every key is canonical letters, so the same entry serves every script of the
riwayah. The budget in ADR-008 §4.2 is a gate, not a guideline: **a lexicon
growing past its ceiling means a rule is missing, not that the corpus is
irregular.**
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..dataio import load_yaml, require_keys

SCHEMA_VERSION = 1

#: ADR-008 §4.2. Exceeding one of these fails the build rather than being
#: absorbed quietly, which is how a derivation turns into curation.
BUDGETS = {"wasl_particles": 10, "wasl_exempt": 30, "silah_exempt": 200}


class LexiconError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Lexicon:
    wasl_particles: frozenset[str] = frozenset()
    """`إن`, `إذ`, `إذا` — hamza-initial particles that look prosthetic."""
    wasl_exempt: frozenset[str] = frozenset()
    """Proper nouns and form-IV verbal nouns the three rules over-accept."""
    wasl_nouns: frozenset[str] = frozenset()
    """The ten nouns, whose helping vowel is kasra regardless of the third
    letter — `اسم` would otherwise derive damma."""
    silah_exempt: frozenset[str] = frozenset()
    source: Path | None = field(default=None, compare=False)

    def is_wasl_exempt(self, skeleton: str) -> bool:
        return skeleton in self.wasl_particles or skeleton in self.wasl_exempt

    def is_wasl_noun(self, skeleton: str) -> bool:
        return skeleton in self.wasl_nouns

    def is_silah_exempt(self, skeleton: str) -> bool:
        return skeleton in self.silah_exempt


EMPTY = Lexicon()


def load_lexicon(path: Path) -> Lexicon:
    data = load_yaml(path)
    require_keys(
        data,
        {"schema_version"},
        name=str(path),
        optional=set(BUDGETS) | {"wasl_nouns"},
    )
    if data["schema_version"] != SCHEMA_VERSION:
        raise LexiconError(
            f"{path}: schema_version {data['schema_version']!r}, expected "
            f"{SCHEMA_VERSION}"
        )
    sections = {
        name: frozenset(data.get(name) or ())
        for name in (*BUDGETS, "wasl_nouns")
    }
    for name, ceiling in BUDGETS.items():
        size = len(sections[name])
        if size > ceiling:
            raise LexiconError(
                f"{path}: {name} has {size} entries, over its budget of "
                f"{ceiling}. A location table growing toward 10^4 is a signal "
                f"that a rule is missing, not that the corpus is irregular."
            )
    return Lexicon(source=path, **sections)
