"""Load a riwayah's khilaf: where it disagrees with itself, and by default how."""
from __future__ import annotations

from pathlib import Path

from dataclasses import dataclass

from ..canon.khilaf import VowelKhilaf, VowelSite
from ..dataio import load_yaml, require_keys
from ..model.address import KhilafId
from ..model.canon import ABJAD, Annotation, Quality
from ..rules.khilaf import OPTIONS, KhilafError, Site, SitedKhilaf

SCHEMA_VERSION = 1

#: One top-level key per khilaf point that names sites word by word.
SITED = {
    KhilafId.RAA_TAFKHEEM: "raa_tafkheem",
    KhilafId.NUCLEUS_VOWEL: "nucleus_vowel",
    KhilafId.IMALA_QUALITY: "imala_quality",
    KhilafId.YAA_ITHBAT: "yaa_ithbat",
}

#: The points a rule settles while performing one Score, word by word.
SITED_POINTS = (KhilafId.RAA_TAFKHEEM, KhilafId.YAA_ITHBAT)

#: The points whose sites the Score carries, so the choice is made at build.
VOWEL_POINTS = (KhilafId.NUCLEUS_VOWEL, KhilafId.IMALA_QUALITY)

JUNCTIONS = {"stop": True, "join": False}

#: The alphabet a site key is written in: canonical letters, the geminate
#: mark, and the vowel letters `_vocalised` spells a nucleus with.
KEY_ALPHABET = frozenset(ABJAD.values()) | {"~"} | {q.value for q in Quality}


@dataclass(frozen=True, slots=True)
class Khilaf:
    """One riwayah's disputes, split by the layer that settles them."""

    sited: dict[KhilafId, SitedKhilaf]
    vowel: VowelKhilaf

    @property
    def raa(self) -> SitedKhilaf:
        return self.sited[KhilafId.RAA_TAFKHEEM]

    @property
    def yaa(self) -> SitedKhilaf:
        return self.sited[KhilafId.YAA_ITHBAT]

    def points(self) -> dict[str, dict]:
        """Every choice a caller may make, keyed by khilaf point."""
        return {
            **{point.value: k.points() for point, k in self.sited.items()},
            "vowel": self.vowel.points(),
        }


EMPTY = Khilaf(
    {point: SitedKhilaf(point) for point in SITED_POINTS}, VowelKhilaf({})
)


def load_khilaf(path: Path) -> Khilaf:
    """Absent file, empty khilaf: a riwayah with no recorded dispute is not
    an error."""
    if not path.exists():
        return EMPTY
    data = load_yaml(path)
    version = data.pop("schema_version", None)
    if version != SCHEMA_VERSION:
        raise KhilafError(
            f"{path}: schema_version {version!r}, expected {SCHEMA_VERSION}"
        )
    require_keys(data, set(SITED.values()), name=str(path))
    return Khilaf(
        sited={
            point: SitedKhilaf(
                point,
                {
                    key: _site(point, key, spec, path)
                    for key, spec in (data[SITED[point]] or {}).items()
                },
            )
            for point in SITED_POINTS
        },
        vowel=VowelKhilaf(
            {
                name: _vowel(point, name, spec, path)
                for point in VOWEL_POINTS
                for name, spec in (data[SITED[point]] or {}).items()
            }
        ),
    )


def _vowel(point: KhilafId, name: str, spec: dict, path: Path) -> VowelSite:
    where = f"{path} {SITED[point]}[{name!r}]"
    require_keys(
        spec, {"slot", "default", "options", "forms"}, name=where,
        optional={"annotate"},
    )
    options = {
        option: _quality(option, raw, where)
        for option, raw in spec["options"].items()
    }
    if spec["default"] not in options:
        raise KhilafError(
            f"{where}: default {spec['default']!r} is not one of "
            f"{sorted(options)}"
        )
    return VowelSite(
        khilaf=point,
        index=int(spec["slot"]),
        options=options,
        default=str(spec["default"]),
        forms=frozenset(spec["forms"]),
        annotation=_annotation(spec.get("annotate"), where),
    )


def _annotation(raw: object, where: str) -> Annotation | None:
    if raw is None:
        return None
    try:
        return Annotation(str(raw))
    except ValueError:
        raise KhilafError(
            f"{where}: annotate {raw!r}, expected one of "
            f"{sorted(a.value for a in Annotation)}"
        ) from None


def _quality(option: str, raw: object, where: str) -> Quality:
    try:
        return Quality(str(raw))
    except ValueError:
        raise KhilafError(
            f"{where}: option {option!r} reads {raw!r}, which is not a vowel"
        ) from None


def _site(point: KhilafId, skeleton: str, spec: dict, path: Path) -> Site:
    where = f"{path} {SITED[point]}[{skeleton!r}]"
    require_keys(spec, {"disputed_at", "default"}, name=where)
    unknown = sorted(set(skeleton) - KEY_ALPHABET)
    if unknown:
        raise KhilafError(
            f"{where}: {unknown} are not part of a site key. Keys are canonical "
            f"letters and vowels, so one entry serves every script."
        )
    at_stop = JUNCTIONS.get(str(spec["disputed_at"]))
    if at_stop is None:
        raise KhilafError(
            f"{where}: disputed_at {spec['disputed_at']!r}, expected one of "
            f"{sorted(JUNCTIONS)}"
        )
    options = OPTIONS[point]
    if str(spec["default"]) not in options:
        raise KhilafError(
            f"{where}: default {spec['default']!r}, expected one of "
            f"{sorted(options)}"
        )
    return Site(at_stop=at_stop, default=options[str(spec["default"])])
