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
BUDGETS = {
    "wasl_particles": 10,
    "wasl_exempt": 30,
    "silah_exempt": 200,
    "pausal_lexemes": 10,
}

#: The attached pronouns, in canonical letters. Closed in Arabic, so a lexeme
#: entry covers its whole inflectional family without enumerating it.
CLITIC_PRONOUNS: frozenset[str] = frozenset(
    {"ه", "هم", "هما", "هن", "ك", "كم", "كما", "كن", "نا", "ي", "ني", "همء"}
)


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
    pausal_lexemes: frozenset[str] = frozenset()
    """The seven alifs: words whose final ālif is short in waṣl and long at
    pause. IndoPak's inventory has no grapheme that distinguishes them, so it
    gives no evidence and this is not a contradiction (ADR-008 §4.1)."""
    source: Path | None = field(default=None, compare=False)

    def is_wasl_exempt(self, skeleton: str) -> bool:
        return self._matches(self.wasl_particles, skeleton) or self._matches(
            self.wasl_exempt, skeleton
        )

    @staticmethod
    def _matches(entries: frozenset[str], skeleton: str) -> bool:
        """A lexeme, with or without a clitic pronoun.

        `إيمان`, `إيمانكم`, `إيمانهم` and `إيمانها` are one lexical fact, and
        listing four skeletons for it would be the location table this design
        keeps arguing against. Arabic's clitic pronouns are a closed set, so
        the stem plus that set is a rule.
        """
        if skeleton in entries:
            return True
        return any(
            skeleton == stem + clitic
            for stem in entries
            for clitic in CLITIC_PRONOUNS
        )

    def is_pausal(self, skeleton: str) -> bool:
        """Matched as a suffix, because only proclitics attach on the left:
        `وَأَنَا` is `أَنَا` with a wāw, not a different lexeme."""
        return any(skeleton.endswith(entry) for entry in self.pausal_lexemes)

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
