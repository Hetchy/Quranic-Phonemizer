"""The canonical-skeleton lexicon: closed classes of Arabic, not of this corpus.

Keyed by canonical letters so one entry serves every script of the riwayah.
A budget ceiling turns growth past it into a build failure, not a silent list.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..dataio import load_yaml, require_keys

SCHEMA_VERSION = 1

#: Exceeding a budget fails the build instead of absorbing growth silently.
#: `wasl_exempt` needs headroom because `ال` is genuinely ambiguous between
#: the article and a root lam, with no orthographic test to tell them apart.
BUDGETS = {
    "wasl_particles": 10,
    "wasl_exempt": 60,
    "wasl_exempt_doubled": 10,
    "pausal_lexemes": 10,
    "form_eight_lam": 10,
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
    """`إن`, `إذ`, `إذا` - hamza-initial particles that look prosthetic."""
    wasl_exempt: frozenset[str] = frozenset()
    """Proper nouns and form-IV verbal nouns the three rules over-accept."""
    wasl_exempt_doubled: frozenset[str] = frozenset()
    """`ألَّف`, `إلَّم` - hamza plus a doubled lam that is not the article."""
    wasl_nouns: frozenset[str] = frozenset()
    """The ten nouns, whose helping vowel is kasra regardless of the third
    letter - `اسم` would otherwise derive damma."""
    pausal_lexemes: frozenset[str] = frozenset()
    """The seven alifs: words whose final alif is short in wasl and long at
    pause. IndoPak's script has no grapheme that distinguishes them, so the
    absence of evidence is not a contradiction."""
    form_eight_lam: frozenset[str] = frozenset()
    """Form-VIII verbs whose first radical is lam, e.g. `ٱلْتَقَى`. After a
    wasl hamza these look identical to the definite article before a sun
    letter, and canonical facts alone cannot tell them apart."""
    source: Path | None = field(default=None, compare=False)

    def is_wasl_exempt(self, skeleton: str) -> bool:
        return self._matches(self.wasl_particles, skeleton) or self._matches(
            self.wasl_exempt, skeleton
        )

    @staticmethod
    def _matches(entries: frozenset[str], skeleton: str) -> bool:
        """A lexeme, with or without a clitic pronoun.

        Arabic's clitic pronouns are a closed set, so matching stem + pronoun
        avoids enumerating every inflected form of `إيمان` separately.
        """
        if skeleton in entries:
            return True
        for stem in entries:
            if any(skeleton == stem + clitic for clitic in CLITIC_PRONOUNS):
                return True
            # A 3+ letter stem is specific enough to match as a prefix, e.g.
            # `ألقى`, `ألقينا`, `ألقوا`; shorter stems must match exactly.
            #
            # A hamza+lam entry is safe here only because `is_wasl` checks
            # the article first; swapping that order lets `ءلق` match
            # `القرآن`. See the ordering comment in canon/derive/wasl.py.
            if len(stem) >= _PREFIX_MIN and skeleton.startswith(stem):
                return True
        return False

    def is_wasl_exempt_doubled(self, skeleton: str) -> bool:
        return self._matches(self.wasl_exempt_doubled, skeleton)

    def is_pausal(self, skeleton: str) -> bool:
        """Matched exactly, or after a single proclitic.

        A proclitic is one letter with one vowel, which keeps `وَأَنَا` matched
        without matching any longer word ending the same way.
        """
        if skeleton in self.pausal_lexemes:
            return True
        return any(
            len(skeleton) - len(entry) in (2, 3) and skeleton.endswith(entry)
            for entry in self.pausal_lexemes
        )

    def is_wasl_noun(self, skeleton: str) -> bool:
        return self._matches(self.wasl_nouns, skeleton)

    def is_form_eight_lam(self, skeleton: str) -> bool:
        return self._matches(self.form_eight_lam, skeleton)


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
