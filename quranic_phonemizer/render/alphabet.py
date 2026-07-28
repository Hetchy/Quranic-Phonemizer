"""Maps a sound-feature tuple to a notation token.

The lookup is total and performs no composition: it may map two distinct
tuples to the same token, never the reverse.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..dataio import load_yaml, require_keys
from ..model.performance import Consonant, Nasal, Release, Sound, Vowel

SCHEMA_VERSION = 1


class NotationError(KeyError):
    """A tuple the notation does not cover. The lookup is meant to be total."""


@dataclass(frozen=True, slots=True)
class Alphabet:
    notation: str
    consonants: dict[str, str]
    vowels: dict[str, str]
    nasals: dict[str, str]
    releases: dict[str, str]

    def token(self, sound: Sound) -> str:
        table, key = _key(sound)
        found = getattr(self, table).get(key)
        if found is None:
            raise NotationError(
                f"{self.notation} has no token for {table}[{key!r}]; the "
                f"render map is total over the feature space by construction, "
                f"so this is a missing row rather than a missing feature"
            )
        return found

    def tokens(self, sounds) -> tuple[str, ...]:
        return tuple(self.token(sound) for sound in sounds)


def _key(sound: Sound) -> tuple[str, str]:
    match sound:
        case Consonant():
            return "consonants", (
                f"{sound.letter.value}|{int(sound.geminate)}|"
                f"{int(sound.emphatic)}|{int(sound.nasal)}"
            )
        case Vowel():
            return "vowels", (
                f"{sound.quality.value}|{int(sound.long)}|{int(sound.emphatic)}"
            )
        case Nasal():
            return "nasals", f"{sound.place.value}|{int(sound.emphatic)}"
        case Release():
            return "releases", sound.kind.value
    raise NotationError(f"{type(sound).__name__} is not a Sound")


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
        consonants=dict(data["consonants"]),
        vowels=dict(data["vowels"]),
        nasals=dict(data["nasals"]),
        releases=dict(data["releases"]),
    )
