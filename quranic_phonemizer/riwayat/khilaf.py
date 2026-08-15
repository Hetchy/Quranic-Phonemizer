"""Load a riwayah's scalar khilaf catalogue and runtime sites."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..canon.khilaf import (
    CanonicalKhilaf,
    LetterSite,
    MaddSite,
    VowelKhilaf,
    VowelSite,
)
from ..dataio import load_yaml, require_keys
from ..model.address import KhilafId, Location
from ..model.canon import CanonLetter, Quality
from ..rules.khilaf import HEAVY, KEPT, KhilafError, Site, SitedKhilaf

SCHEMA_VERSION = 2


@dataclass(frozen=True, slots=True)
class VariantDefinition:
    khilaf: KhilafId
    options: tuple[str, ...]
    default: str
    source: str
    locations: frozenset[Location] = frozenset()
    junction: str | None = None

    def choose(self, selection) -> str:
        chosen = selection.chosen(self.khilaf) or self.default
        if chosen not in self.options:
            raise KhilafError(
                f"{self.khilaf.value}: {chosen!r} is not an option; expected "
                f"one of {list(self.options)}"
            )
        return chosen


@dataclass(frozen=True, slots=True)
class Khilaf:
    variants: dict[KhilafId, VariantDefinition]
    raa: SitedKhilaf
    yaa: SitedKhilaf
    canonical: CanonicalKhilaf

    def definition(self, khilaf: KhilafId) -> VariantDefinition:
        return self.variants[khilaf]

    def validate(self, selection) -> None:
        seen = set()
        for option in selection.options:
            if option.khilaf in seen:
                raise KhilafError(
                    f"{option.khilaf.value}: more than one option was selected"
                )
            seen.add(option.khilaf)
            self.definition(option.khilaf).choose(selection)

    def points(self) -> dict[str, dict[str, object]]:
        return {
            point.value: {
                "options": list(spec.options),
                "default": spec.default,
            }
            for point, spec in self.variants.items()
        }


EMPTY = Khilaf({}, SitedKhilaf(), SitedKhilaf(), CanonicalKhilaf())


def load_khilaf(path: Path) -> Khilaf:
    if not path.exists():
        return EMPTY
    data = load_yaml(path)
    require_keys(data, {"schema_version", "variants"}, name=str(path))
    if data["schema_version"] != SCHEMA_VERSION:
        raise KhilafError(
            f"{path}: schema_version {data['schema_version']!r}, expected "
            f"{SCHEMA_VERSION}"
        )
    raw = data["variants"]
    _require_all_variants(raw, path)
    definitions = {
        point: _definition(point, raw[point.value], path) for point in KhilafId
    }
    raa = _sited(raw, definitions, _raa_points(), HEAVY, path)
    yaa = _sited(raw, definitions, (KhilafId.YAA_AATANI_WAQF,), KEPT, path)
    vowels = (
        _vowel(
            KhilafId.DAAF_HARAKA,
            raw[KhilafId.DAAF_HARAKA.value],
            definitions[KhilafId.DAAF_HARAKA],
            path,
        ),
    )
    letters = tuple(
        site
        for point in _letter_points()
        for site in _letters(point, raw[point.value], definitions[point], path)
    )
    madd = MaddSite(
        KhilafId.MADD_LAZIM_TASHEEL,
        definitions[KhilafId.MADD_LAZIM_TASHEEL].locations,
        definitions[KhilafId.MADD_LAZIM_TASHEEL].default,
    )
    return Khilaf(
        definitions,
        raa,
        yaa,
        CanonicalKhilaf(VowelKhilaf(vowels), letters, madd),
    )


def _require_all_variants(raw, path) -> None:
    declared = set(raw)
    expected = {point.value for point in KhilafId}
    missing = sorted(expected - declared)
    unknown = sorted(declared - expected)
    if missing or unknown:
        raise KhilafError(f"{path}: missing variants {missing}; unknown {unknown}")


def _definition(point, spec, path) -> VariantDefinition:
    where = f"{path} variants[{point.value}]"
    require_keys(
        spec,
        {"kind", "options", "default", "source"},
        name=where,
        optional={"forms", "locations", "slot", "junction", "values"},
    )
    options = tuple(str(value) for value in spec["options"])
    default = str(spec["default"])
    if default not in options:
        raise KhilafError(f"{where}: default {default!r} is not in {options}")
    locations = frozenset(
        _location(value)
        for value in spec.get("locations", ())
        if str(value).count(":") == 2
    )
    junction = str(spec["junction"]) if "junction" in spec else None
    return VariantDefinition(
        point, options, default, str(spec["source"]), locations, junction
    )


def _sited(raw, definitions, points, values, path) -> SitedKhilaf:
    sites = {}
    options = {}
    for point in points:
        spec = raw[point.value]
        junction = str(spec["junction"])
        if junction not in {"waqf", "wasl"}:
            raise KhilafError(f"{path}: {point.value} has bad junction {junction}")
        mapping = {name: values[name] for name in definitions[point].options}
        options[point] = mapping
        default = mapping[definitions[point].default]
        for form in spec["forms"]:
            sites[str(form)] = Site(point, junction == "waqf", default)
    return SitedKhilaf(sites, options)


def _vowel(point, spec, definition, path) -> VowelSite:
    where = f"{path} variants[{point.value}]"
    values = {}
    for option in definition.options:
        try:
            values[option] = Quality(str(spec["values"][option]))
        except ValueError:
            raise KhilafError(f"{where}: {option} is not a vowel") from None
    return VowelSite(
        point,
        int(spec["slot"]),
        values,
        definition.default,
        frozenset(str(form) for form in spec["forms"]),
    )


def _letters(point, spec, definition, path) -> tuple[LetterSite, ...]:
    where = f"{path} variants[{point.value}]"
    try:
        values = {
            option: CanonLetter(str(spec["values"][option]))
            for option in definition.options
        }
    except ValueError as error:
        raise KhilafError(f"{where}: bad letter value: {error}") from None
    return tuple(
        LetterSite(
            point,
            _location(value),
            int(spec["slot"]),
            values,
            definition.default,
        )
        for value in definition.locations
    )


def _location(raw: str) -> Location:
    surah, ayah, word = (int(part) for part in str(raw).split(":"))
    return Location(surah, ayah, word)


def _raa_points() -> tuple[KhilafId, ...]:
    return (
        KhilafId.RAA_FIRQ_WASL,
        KhilafId.RAA_ALQITR_WAQF,
        KhilafId.RAA_MISR_WAQF,
        KhilafId.RAA_NUTHUR_WAQF,
        KhilafId.RAA_YASR_WAQF,
        KhilafId.RAA_ASR_WAQF,
    )


def _letter_points() -> tuple[KhilafId, ...]:
    return (
        KhilafId.SEEN_SAD_YABSUT,
        KhilafId.SEEN_SAD_BASTAH,
        KhilafId.SEEN_SAD_AL_MUSAYTIRUN,
        KhilafId.SEEN_SAD_BIMUSAYTIR,
    )
