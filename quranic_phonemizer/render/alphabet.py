"""Maps a sound-feature tuple to a notation token.

One entry per letter, quality and qalqala degree, features composed over it.
Total by coverage, so a feature no entry offers raises at lookup.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from ..dataio import load_yaml, require_keys
from ..model.address import Riwayah
from ..model.canon import CanonLetter, Quality
from ..model.performance import Consonant, Degree, Release, Sound, Vowel

SCHEMA_VERSION = 2

#: The packaged notation data. IPA is what the native result emits.
_NOTATION = Path(__file__).resolve().parent.parent / "data" / "render"

#: What a long vowel adds. One character, but it is notation, so it lives
#: beside the tokens rather than inside the resolver's control flow.
LENGTH = ":"

#: Each gates one distinction that a `Sound` always carries; the alphabet
#: spends a token on it only when named.
EXTRA_PHONEMES = frozenset(
    {"tashil", "emphatic_fatha", "emphatic_ikhfaa", "qalqala_degree", "imala"}
)

_ALWAYS_RENDERED: dict[Riwayah, frozenset[str]] = {
    Riwayah.WARSH: frozenset({"tashil"}),
}


def allowed_extra_phonemes(riwayah: Riwayah) -> frozenset[str]:
    """Optional rendering distinctions accepted for one riwayah."""
    return EXTRA_PHONEMES - _ALWAYS_RENDERED.get(riwayah, frozenset())


def effective_extra_phonemes(
    riwayah: Riwayah, requested: frozenset[str]
) -> frozenset[str]:
    """Rendering distinctions active after riwayah-fixed notation."""
    unknown = requested - allowed_extra_phonemes(riwayah)
    if unknown:
        raise ValueError(
            f"{sorted(unknown)} is not optional for {riwayah.value}"
        )
    return requested | _ALWAYS_RENDERED.get(riwayah, frozenset())

#: `token(sound)` with no `extra_phonemes` argument -- every caller that
#: predates the toggle -- must keep reading exactly as it does today, which
#: is `emphatic_fatha` spent and the rest withheld. A caller that passes an
#: explicit set, even empty, gets the contract's own default: every name
#: withheld unless asked for.
_LEGACY_ACTIVE = frozenset({"emphatic_fatha"})

#: Which quality a collapsed inclined vowel reads as when `imala` is not
#: spent. The riwayah package owns the real mapping -- Hafs collapses kubra
#: to I, Warsh to taqlil -- and a caller that passes none keeps the reading
#: callers had before the mapping existed.
_LEGACY_FALLBACKS: dict[Quality, Quality] = {Quality.KUBRA: Quality.I}


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
    hum: str | None = None
    heavy_hum: str | None = None
    eased: str | None = None
    """Read from the data but not yet composed: gated at the notation once
    an `extra_phonemes` toggle exists to ask for it."""


@dataclass(frozen=True, slots=True)
class Alphabet:
    notation: str
    consonants: dict[CanonLetter, Entry]
    vowels: dict[Quality, Entry]
    releases: dict[Degree, str]

    def token(
        self,
        sound: Sound,
        *,
        extra_phonemes: frozenset[str] | None = None,
        quality_fallbacks: dict[Quality, Quality] | None = None,
    ) -> str:
        active = _LEGACY_ACTIVE if extra_phonemes is None else frozenset(extra_phonemes)
        fallbacks = (
            _LEGACY_FALLBACKS if quality_fallbacks is None else quality_fallbacks
        )
        match sound:
            case Consonant():
                return self._consonant(sound, active)
            case Vowel():
                return self._vowel(sound, active, fallbacks)
            case Release():
                return self._release(sound, active)
        raise NotationError(f"{type(sound).__name__} is not a Sound")

    def tokens(
        self,
        sounds,
        *,
        extra_phonemes: frozenset[str] | None = None,
        quality_fallbacks: dict[Quality, Quality] | None = None,
    ) -> tuple[str, ...]:
        return tuple(
            self.token(
                sound,
                extra_phonemes=extra_phonemes,
                quality_fallbacks=quality_fallbacks,
            )
            for sound in sounds
        )

    # -- composition -------------------------------------------------------
    def _consonant(self, sound: Consonant, active: frozenset[str]) -> str:
        entry = self.consonants[sound.letter]
        # Validated regardless of the toggle: a sound this feature-less
        # cannot come from the model, so a missing entry is a data bug.
        if sound.eased and entry.eased is None:
            raise self._absent("eased", sound)
        if sound.ghunnah:
            return self._hum(entry, sound, active)
        # Checked before composing the plain token, which would otherwise
        # answer for a letter that takes no emphasis and quietly drop the
        # feature -- the one way a wrong tuple could still come back with a
        # plausible token.
        if sound.emphatic and entry.emphatic is None:
            raise self._absent("emphatic", sound)
        if sound.eased and "tashil" in active:
            token = entry.eased
        else:
            token = entry.emphatic if sound.emphatic else entry.plain
        assert token is not None
        return token * 2 if sound.geminate else token

    def _hum(self, entry: Entry, sound: Consonant, active: frozenset[str]) -> str:
        if sound.emphatic and entry.heavy_hum is None:
            raise self._absent("heavy_hum", sound)
        if sound.emphatic and "emphatic_ikhfaa" in active:
            return entry.heavy_hum
        if not sound.geminate and entry.hum is not None:
            return entry.hum
        # A held ghunnah is already the sound of a doubled letter, so
        # gemination adds nothing further to write.
        return self._feature(entry.nasal, "nasal", sound)

    def _vowel(
        self, sound: Vowel, active: frozenset[str],
        fallbacks: dict[Quality, Quality],
    ) -> str:
        quality = sound.quality
        if "imala" not in active:
            # The typed quality survives the collapse; only the token reads
            # as the riwayah's fallback quality.
            quality = fallbacks.get(quality, quality)
        entry = self.vowels[quality]
        if sound.emphatic and (sound.long or "emphatic_fatha" in active):
            token = self._feature(entry.emphatic, "emphatic", sound)
        else:
            token = entry.plain
        return token + LENGTH if sound.long else token

    def _release(self, sound: Release, active: frozenset[str]) -> str:
        # Kubra and akbar share a token, so the extended form is the
        # sughra token doubled rather than a third data row.
        if "qalqala_degree" in active and sound.degree is not Degree.SUGHRA:
            return self.releases[Degree.SUGHRA] * 2
        return self.releases[sound.degree]

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
        {"schema_version", "notation", "consonants", "vowels", "releases"},
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
        releases=_tokens(Degree, data["releases"], "releases", path),
    )


@lru_cache(maxsize=None)
def packaged_alphabet(notation: str = "ipa") -> Alphabet:
    """The notation shipped with the package, loaded once and cached."""
    return load_alphabet(_NOTATION / f"{notation}.yaml")


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

    A missing member marks a gap; an unknown entry marks a dropped letter.
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
    require_keys(
        raw, {"plain"}, name=where,
        optional={"emphatic", "nasal", "hum", "heavy_hum", "eased"},
    )
    return Entry(
        plain=str(raw["plain"]),
        emphatic=_optional(raw, "emphatic"),
        nasal=_optional(raw, "nasal"),
        hum=_optional(raw, "hum"),
        heavy_hum=_optional(raw, "heavy_hum"),
        eased=_optional(raw, "eased"),
    )


def _optional(raw: Any, key: str) -> str | None:
    return str(raw[key]) if key in raw else None
