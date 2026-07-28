"""Maps a sound-feature tuple to a notation token.

One entry per letter, quality, nasal place and release kind, features composed
over it. Total by coverage, so a feature no entry offers raises at lookup.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..dataio import load_yaml, require_keys
from ..model.canon import CanonLetter, Quality
from ..model.performance import (
    Consonant,
    Nasal,
    NasalPlace,
    Release,
    ReleaseKind,
    Sound,
    Vowel,
)

SCHEMA_VERSION = 2

#: What a long vowel adds. One character, but it is notation, so it lives
#: beside the tokens rather than inside the resolver's control flow.
LENGTH = ":"


class NotationError(KeyError):
    """A sound this notation cannot write. Never a silent gap."""


@dataclass(frozen=True, slots=True)
class Entry:
    """The tokens one letter or quality may take.

    A feature left `None` is not one this entry admits: the model should
    never ask for it, and it raises rather than resolving if it does.
    """

    plain: str
    emphatic: str | None = None
    nasal: str | None = None


@dataclass(frozen=True, slots=True)
class Alphabet:
    notation: str
    consonants: dict[CanonLetter, Entry]
    vowels: dict[Quality, Entry]
    nasals: dict[NasalPlace, str]
    releases: dict[ReleaseKind, str]

    def token(self, sound: Sound) -> str:
        match sound:
            case Consonant():
                return self._consonant(sound)
            case Vowel():
                return self._vowel(sound)
            case Nasal():
                if sound.emphatic:
                    raise self._absent("emphatic", sound)
                return self.nasals[sound.place]
            case Release():
                return self.releases[sound.kind]
        raise NotationError(f"{type(sound).__name__} is not a Sound")

    def tokens(self, sounds) -> tuple[str, ...]:
        return tuple(self.token(sound) for sound in sounds)

    # -- composition -------------------------------------------------------
    def _consonant(self, sound: Consonant) -> str:
        entry = self.consonants[sound.letter]
        # Checked before the nasal branch, which would otherwise answer for a
        # letter that takes no emphasis and quietly drop the feature -- the
        # one way a wrong tuple could still come back with a plausible token.
        if sound.emphatic and entry.emphatic is None:
            raise self._absent("emphatic", sound)
        if sound.nasal:
            # A held nasal is already the sound of a doubled letter, so
            # gemination adds nothing to write.
            return self._feature(entry.nasal, "nasal", sound)
        token = entry.emphatic if sound.emphatic else entry.plain
        assert token is not None
        return token * 2 if sound.geminate else token

    def _vowel(self, sound: Vowel) -> str:
        entry = self.vowels[sound.quality]
        if sound.emphatic:
            token = self._feature(entry.emphatic, "emphatic", sound)
        else:
            token = entry.plain
        return token + LENGTH if sound.long else token

    def _feature(self, token: str | None, name: str, sound: Sound) -> str:
        if token is None:
            raise self._absent(name, sound)
        return token

    def _absent(self, name: str, sound: Sound) -> NotationError:
        return NotationError(
            f"{self.notation} declares no {name} form for {sound!r}. The "
            f"entry omits it because the letter does not take that feature, "
            f"so this is a sound the model should not have produced rather "
            f"than a row the alphabet is missing."
        )


# --------------------------------------------------------------------- loading
def load_alphabet(path: Path) -> Alphabet:
    data = load_yaml(path)
    require_keys(
        data,
        {"schema_version", "notation", "consonants", "vowels", "nasals",
         "releases"},
        name=str(path),
    )
    if data["schema_version"] != SCHEMA_VERSION:
        raise NotationError(
            f"{path}: schema_version {data['schema_version']!r}, expected "
            f"{SCHEMA_VERSION}"
        )
    return Alphabet(
        notation=str(data["notation"]),
        consonants=_entries(CanonLetter, data["consonants"], "consonants", path),
        vowels=_entries(Quality, data["vowels"], "vowels", path),
        nasals=_tokens(NasalPlace, data["nasals"], "nasals", path),
        releases=_tokens(ReleaseKind, data["releases"], "releases", path),
    )


def _entries(enum: type, raw: Any, section: str, path: Path) -> dict:
    return {
        member: _entry(raw[member.value], f"{path} {section}[{member.value}]")
        for member in _covered(enum, raw, section, path)
    }


def _tokens(enum: type, raw: Any, section: str, path: Path) -> dict:
    return {
        member: str(raw[member.value])
        for member in _covered(enum, raw, section, path)
    }


def _covered(enum: type, raw: Any, section: str, path: Path) -> tuple:
    """Every member has an entry, and every entry names a member.

    A member with no entry is the gap that used to be a missing row; an entry
    naming nothing is a letter the model has since dropped.
    """
    if not isinstance(raw, dict):
        raise NotationError(f"{path}: {section} must be a mapping, got {raw!r}")
    declared, expected = set(raw), {member.value for member in enum}
    missing, unknown = sorted(expected - declared), sorted(declared - expected)
    if missing or unknown:
        raise NotationError(
            f"{path}: {section} is not total over {enum.__name__}. "
            f"Missing {missing}; not a member: {unknown}. The alphabet is "
            f"total by coverage, so adding a letter to the model is one "
            f"entry here and forgetting it is this error."
        )
    return tuple(enum)


def _entry(raw: Any, where: str) -> Entry:
    if isinstance(raw, str):
        return Entry(plain=raw)
    require_keys(raw, {"plain"}, name=where, optional={"emphatic", "nasal"})
    return Entry(
        plain=str(raw["plain"]),
        emphatic=_optional(raw, "emphatic"),
        nasal=_optional(raw, "nasal"),
    )


def _optional(raw: Any, key: str) -> str | None:
    return str(raw[key]) if key in raw else None
