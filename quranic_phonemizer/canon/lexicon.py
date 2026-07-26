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
#:
#: `wasl_exempt` was budgeted at 30 from an analysis that counted only the
#: sites where IndoPak writes the helping vowel. Implementation raised it to
#: 60: `ال` is genuinely ambiguous between the article and a root lām — `ألف`
#: and `الفجر` begin identically — and no orthographic test separates them.
#: That is a lexical fact about Arabic, which is what the list is for. The
#: guard did its job by making the gap visible instead of letting the list
#: grow quietly. See docs/adr/phase-1-report.md §6.
BUDGETS = {
    "wasl_particles": 10,
    "wasl_exempt": 60,
    "silah_exempt": 200,
    "pausal_lexemes": 10,
}

#: The attached pronouns, in canonical letters. Closed in Arabic, so a lexeme
#: entry covers its whole inflectional family without enumerating it.
CLITIC_PRONOUNS: frozenset[str] = frozenset(
    {"ه", "هم", "هما", "هن", "ك", "كم", "كما", "كن", "نا", "ي", "ني", "همء"}
)


#: Below this length a stem is not specific enough to match a prefix.
_PREFIX_MIN = 3


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
        for stem in entries:
            if any(skeleton == stem + clitic for clitic in CLITIC_PRONOUNS):
                return True
            # A stem of three or more canonical letters is specific enough
            # to match a prefix: `ألقى`, `ألقينا`, `ألقوا` are one lexeme
            # with ordinary verbal inflection. Shorter stems stay exact.
            #
            # An entry beginning hamza + lām is safe here **only because
            # `is_wasl` consults the article before it**: the article puts a
            # lām at that position in every word it prefixes, so reordering
            # those two checks makes `ءلق` swallow `القرآن`. Measured: it
            # takes the residue from 23 to 671. See the ordering comment in
            # canon/derive/wasl.py.
            if len(stem) >= _PREFIX_MIN and skeleton.startswith(stem):
                return True
        return False

    def is_pausal(self, skeleton: str) -> bool:
        """Matched exactly, or after a single proclitic.

        Suffix matching was too loose: `ٱلْـَٔـٰنَ` ends in the same three
        symbols as `أَنَا` and is not it. A proclitic is one letter with one
        vowel, so allowing that and nothing more keeps `وَأَنَا` covered without
        matching a whole word that happens to end the same way.
        """
        if skeleton in self.pausal_lexemes:
            return True
        return any(
            len(skeleton) - len(entry) in (2, 3) and skeleton.endswith(entry)
            for entry in self.pausal_lexemes
        )

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
