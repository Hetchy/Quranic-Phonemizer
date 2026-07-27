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

#: One letter and its vowel, in the vocalised notation `_vocalised` writes.
#: `الآن` is three past `أنا` and is not it.
_PROCLITIC = 2


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
    wasl_kasra: frozenset[str] = frozenset()
    """Words whose wasl hamza takes kasra although their third letter carries
    damma, because that damma is not the stem's: `اسم`, `ٱمْشُوا۟`."""
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
        return _inflected(self.wasl_particles, skeleton) or _inflected(
            self.wasl_exempt, skeleton
        )

    def is_wasl_exempt_doubled(self, skeleton: str) -> bool:
        return _inflected(self.wasl_exempt_doubled, skeleton)

    def is_pausal(self, skeleton: str) -> bool:
        """Matched exactly, or after a single proclitic: `وَأَنَا` is `أنا`."""
        if skeleton in self.pausal_lexemes:
            return True
        return any(
            len(skeleton) - len(entry) == _PROCLITIC and skeleton.endswith(entry)
            for entry in self.pausal_lexemes
        )

    def takes_wasl_kasra(self, skeleton: str) -> bool:
        """Matched as it stands: `است` heads every form-X verb, whose helping
        vowel its own third letter decides."""
        return _bare(self.wasl_kasra, skeleton)

    def is_form_eight_lam(self, skeleton: str) -> bool:
        """Matched as it stands: `ٱلتَّقْوَىٰ` and `ٱلتَّمَاثِيل` extend the
        stems of `ٱلْتَقَى` and `ٱلْتَمِسُوا` and are not them."""
        return _bare(self.form_eight_lam, skeleton)


def _bare(entries: frozenset[str], skeleton: str) -> bool:
    """A lexeme, with or without a clitic pronoun.

    Arabic's clitic pronouns are a closed set, so matching stem plus pronoun
    avoids enumerating every inflected form of `إيمان` separately.
    """
    return skeleton in entries or any(
        skeleton == stem + clitic
        for stem in entries
        for clitic in CLITIC_PRONOUNS
    )


def _inflected(entries: frozenset[str], skeleton: str) -> bool:
    """That, or a stem long enough to be specific as a prefix -- `ألقى`,
    `ألقينا`, `ألقوا` are one entry."""
    return _bare(entries, skeleton) or any(
        len(stem) >= _PREFIX_MIN and skeleton.startswith(stem)
        for stem in entries
    )


EMPTY = Lexicon()


def load_lexicon(path: Path) -> Lexicon:
    data = load_yaml(path)
    require_keys(
        data,
        {"schema_version"},
        name=str(path),
        optional=set(BUDGETS) | {"wasl_kasra"},
    )
    if data["schema_version"] != SCHEMA_VERSION:
        raise LexiconError(
            f"{path}: schema_version {data['schema_version']!r}, expected "
            f"{SCHEMA_VERSION}"
        )
    sections = {
        name: frozenset(data.get(name) or ())
        for name in (*BUDGETS, "wasl_kasra")
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
