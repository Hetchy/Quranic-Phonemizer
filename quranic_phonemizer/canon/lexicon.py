"""The canonical-skeleton lexicon: closed classes of Arabic, not of this corpus.

Keyed by canonical letters so one entry serves every script of the riwayah.
The sections are data; the ways of matching one are a closed set in here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from ..dataio import load_yaml, require_keys

SCHEMA_VERSION = 2

#: Versioned per file, not per package: this one has never had to move.
MORPHOLOGY_SCHEMA_VERSION = 1


class MatchMode(StrEnum):
    """How an entry is compared against the skeleton being tested."""

    EXACT = "exact"
    CLITIC = "clitic"
    INFLECTED = "inflected"
    PROCLITIC = "proclitic"


#: Below this length a stem is not specific enough to match a prefix.
_PREFIX_MIN = 3

#: One letter and its vowel, in the vocalised notation `_vocalised` writes.
#: `الآن` is three past `أنا` and is not it.
_PROCLITIC = 2


class LexiconError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Section:
    """One closed class: how to match it, and how large it may grow."""

    match: MatchMode
    budget: int
    """A ceiling the gate enforces. Growth past it means a rule is missing,
    not that the corpus is irregular, so it is reviewed rather than raised."""
    entries: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class Affixes:
    """What may attach to a lexeme and leave it that lexeme. Arabic, so it
    is shared data rather than a set per riwayah."""

    clitics: frozenset[str] = frozenset()
    """The attached pronouns. A closed set, so a stem entry covers its whole
    inflectional family without enumerating it."""
    proclitics: frozenset[str] = frozenset()
    """The single letters that may stand before a word. Closed for the same
    reason, and what keeps `جَآءَنَا` from reading as `أَنَا` behind a prefix."""


@dataclass(frozen=True, slots=True)
class Lexicon:
    sections: dict[str, Section] = field(default_factory=dict)
    affixes: Affixes = field(default_factory=Affixes)
    source: Path | None = field(default=None, compare=False)

    def is_divine_name(self, tail: str) -> bool:
        """The whole remainder of the word, so a third radical excludes it."""
        return self._matches("divine_name", tail)

    def is_wasl_exempt(self, skeleton: str) -> bool:
        return self._matches("wasl_particles", skeleton) or self._matches(
            "wasl_exempt", skeleton
        )

    def is_wasl_exempt_doubled(self, skeleton: str) -> bool:
        return self._matches("wasl_exempt_doubled", skeleton)

    def is_pausal(self, skeleton: str) -> bool:
        """Matched exactly, or after a single proclitic: `وَأَنَا` is `أنا`."""
        return self._matches("pausal_lexemes", skeleton)

    def takes_wasl_kasra(self, skeleton: str) -> bool:
        """Matched as it stands: `است` heads every form-X verb, whose helping
        vowel its own third letter decides."""
        return self._matches("wasl_kasra", skeleton)

    def joins_a_particle(self, skeleton: str) -> bool:
        """Is a word of this shape `ها`/`يا` plus a word, or one lexeme?

        `هَآؤُمُ` is shaped exactly like `هَـٰٓؤُلَآءِ` and its hamza is a
        radical of `هاء`, so only a dictionary separates them.
        """
        return not self._matches("joined_particle_exempt", skeleton)

    def is_form_eight_lam(self, skeleton: str) -> bool:
        """Matched as it stands: `ٱلتَّقْوَىٰ` and `ٱلتَّمَاثِيل` extend the
        stems of `ٱلْتَقَى` and `ٱلْتَمِسُوا` and are not them."""
        return self._matches("form_eight_lam", skeleton)

    @property
    def pausal_lexemes(self) -> frozenset[str]:
        """The pass that applies them skips its whole loop when there are
        none, so it asks for the entries rather than testing a skeleton."""
        section = self.sections.get("pausal_lexemes")
        return section.entries if section else frozenset()

    def _matches(self, name: str, key: str) -> bool:
        section = self.sections.get(name)
        if section is None:
            return False
        return _MATCHERS[section.match](section.entries, key, self.affixes)


def _exact(entries: frozenset[str], key: str, affixes: Affixes) -> bool:
    return key in entries


def _clitic(entries: frozenset[str], key: str, affixes: Affixes) -> bool:
    """A lexeme, with or without a clitic pronoun."""
    return key in entries or any(
        key == stem + clitic for stem in entries for clitic in affixes.clitics
    )


def _inflected(entries: frozenset[str], key: str, affixes: Affixes) -> bool:
    """That, or a stem long enough to be specific as a prefix -- `ألقى`,
    `ألقينا`, `ألقوا` are one entry."""
    return _clitic(entries, key, affixes) or any(
        len(stem) >= _PREFIX_MIN and key.startswith(stem) for stem in entries
    )


def _proclitic(entries: frozenset[str], key: str, affixes: Affixes) -> bool:
    """A lexeme, or one behind a single proclitic: `وَأَنَا` is `أنا`."""
    # The prefix has to *be* a proclitic, not merely two characters long: the
    # vocalised notation writes no length, so `جَآءَنَا` and `وَأَنَا` are one
    # shape to a counting test and only the letter tells them apart.
    return key in entries or (
        len(key) > _PROCLITIC
        and key[0] in affixes.proclitics
        and key[_PROCLITIC:] in entries
    )


_MATCHERS = {
    MatchMode.EXACT: _exact,
    MatchMode.CLITIC: _clitic,
    MatchMode.INFLECTED: _inflected,
    MatchMode.PROCLITIC: _proclitic,
}

EMPTY = Lexicon()


def _entries(raw, name: str, path: Path) -> frozenset[str]:
    """A repeated entry is rejected: a set would swallow it before the budget
    counts, so the file would show more rows than the ceiling ever sees."""
    seen: set[str] = set()
    for entry in raw or ():
        if entry in seen:
            raise LexiconError(f"{path}: {name} lists {entry!r} twice")
        seen.add(entry)
    return frozenset(seen)


def _section(raw, name: str, path: Path) -> Section:
    where = f"{path} sections[{name}]"
    require_keys(raw, {"match", "budget", "entries"}, name=where)
    try:
        match = MatchMode(raw["match"])
    except ValueError:
        raise LexiconError(
            f"{where}: {raw['match']!r} is not a match mode. The modes are "
            f"code and closed: {sorted(m.value for m in MatchMode)}"
        ) from None
    return Section(
        match=match,
        budget=int(raw["budget"]),
        entries=_entries(raw["entries"], name, path),
    )


def load_lexicon(path: Path, *, affixes: Affixes = Affixes()) -> Lexicon:
    data = load_yaml(path)
    require_keys(data, {"schema_version", "sections"}, name=str(path))
    if data["schema_version"] != SCHEMA_VERSION:
        raise LexiconError(
            f"{path}: schema_version {data['schema_version']!r}, expected "
            f"{SCHEMA_VERSION}"
        )
    sections = data["sections"] or {}
    if not isinstance(sections, dict):
        raise LexiconError(f"{path}: sections must be a mapping, got {sections!r}")
    return Lexicon(
        sections={
            name: _section(raw, name, path) for name, raw in sections.items()
        },
        affixes=affixes,
        source=path,
    )


def load_affixes(path: Path) -> Affixes:
    """Arabic morphology, invariant across riwayat, so it is shared data."""
    data = load_yaml(path)
    require_keys(
        data,
        {"schema_version", "clitic_pronouns", "proclitics"},
        name=str(path),
    )
    if data["schema_version"] != MORPHOLOGY_SCHEMA_VERSION:
        raise LexiconError(
            f"{path}: schema_version {data['schema_version']!r}, expected "
            f"{MORPHOLOGY_SCHEMA_VERSION}"
        )
    return Affixes(
        clitics=_entries(data["clitic_pronouns"], "clitic_pronouns", path),
        proclitics=_entries(data["proclitics"], "proclitics", path),
    )
