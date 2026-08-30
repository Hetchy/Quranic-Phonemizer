"""Load a riwayah's scalar khilaf catalogue and runtime sites."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..canon.khilaf import (
    CanonicalKhilaf,
    LetterSite,
    MaddSite,
    SpecialSite,
    VowelKhilaf,
    VowelSite,
)
from ..dataio import load_yaml, require_keys
from ..model.address import KhilafId, Location
from ..model.canon import CanonLetter, Quality
from ..rules.khilaf import HEAVY, KEPT, KhilafError, Site, SitedKhilaf

SCHEMA_VERSION = 3

#: Rule IDs whose occurrences realize a dynamic-scope selector, so the
#: analysis can report the sites the authored catalogue cannot enumerate.
DYNAMIC_SCOPE_RULES: dict[str, tuple[str, ...]] = {
    "all_iqlab": ("iqlab",),
    "all_ikhfaa_shafawi": ("ikhfaa_shafawi",),
}


@dataclass(frozen=True, slots=True)
class VariantSpan:
    words: tuple[Location, ...]
    anchor: str
    requires: str

    @property
    def ref(self) -> str:
        first, last = self.words[0], self.words[-1]
        return str(first) if first == last else f"{first}-{last}"


@dataclass(frozen=True, slots=True)
class VariantCatalogueEntry:
    khilaf: KhilafId
    group: str
    display_name: str
    description: str | None
    website_visible: bool
    spans: tuple[VariantSpan, ...]
    dynamic_scope: str | None = None
    subgroup: str | None = None


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
    catalogue: dict[KhilafId, VariantCatalogueEntry]
    group_order: tuple[str, ...] = ()
    dynamic_sites: dict = field(default_factory=dict)
    """Scope name to resolver callable over (score, boundaries), yielding
    (selector id, word index) pairs for occurrences no authored list holds."""

    def definition(self, khilaf: KhilafId) -> VariantDefinition:
        try:
            return self.variants[khilaf]
        except KeyError:
            raise KhilafError(
                f"{khilaf.value!r} is not a variant for this riwayah; "
                f"choose from {[point.value for point in self.variants]}"
            ) from None

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

    def public_catalogue(self) -> tuple[dict[str, object], ...]:
        rows = []
        points = list(self.variants)
        if self.group_order:
            rank = {group: index for index, group in enumerate(self.group_order)}
            points.sort(key=lambda point: rank[self.catalogue[point].group])
        for point in points:
            spec = self.variants[point]
            meta = self.catalogue[point]
            occurrences = [
                {
                    "ref": span.ref,
                    "word_refs": [str(word) for word in span.words],
                    "anchor": span.anchor,
                    "requires": span.requires,
                }
                for span in meta.spans
            ]
            rows.append({
                "id": point.value,
                "options": list(spec.options),
                "default": spec.default,
                "group": meta.group,
                "subgroup": meta.subgroup,
                "display_name": meta.display_name,
                "description": meta.description,
                "website_visible": meta.website_visible,
                "occurrence_count": len(occurrences) if not meta.dynamic_scope else None,
                "representative": occurrences[0] if occurrences else None,
                "occurrences": occurrences,
                "dynamic_scope": meta.dynamic_scope,
            })
        return tuple(rows)


EMPTY = Khilaf({}, SitedKhilaf(), SitedKhilaf(), CanonicalKhilaf(), {})


def load_khilaf(
    path: Path,
    registers: dict[str, tuple[VariantSpan, ...]] | None = None,
    dynamic_sites: dict | None = None,
) -> Khilaf:
    if not path.exists():
        return EMPTY
    data = load_yaml(path)
    require_keys(
        data,
        {"schema_version", "variants", "catalogue"},
        optional={"group_order"},
        name=str(path),
    )
    if data["schema_version"] != SCHEMA_VERSION:
        raise KhilafError(
            f"{path}: schema_version {data['schema_version']!r}, expected "
            f"{SCHEMA_VERSION}"
        )
    raw = data["variants"]
    definitions = _definitions(raw, path)
    catalogue = _catalogue(data["catalogue"], definitions, registers or {}, path)
    group_order = _group_order(data.get("group_order", ()), catalogue, path)
    raa = _sited(
        raw, definitions, _points_of_kind(raw, definitions, "raa_weight"),
        HEAVY, path,
    )
    yaa = _sited(
        raw, definitions, _points_of_kind(raw, definitions, "final_yaa"),
        KEPT, path,
    )
    vowels = tuple(
        _vowel(point, raw[point.value], definitions[point], path)
        for point in _points_of_kind(raw, definitions, "vowel")
    )
    letters = tuple(
        site
        for point in _points_of_kind(raw, definitions, "letter")
        for site in _letters(point, raw[point.value], definitions[point], path)
    )
    madd_points = _points_of_kind(raw, definitions, "madd_tasheel")
    if len(madd_points) > 1:
        raise KhilafError(f"{path}: more than one madd-tasheel variant")
    madd = None
    if madd_points:
        point = madd_points[0]
        madd = MaddSite(
            point, definitions[point].locations, definitions[point].default
        )
    tamanna = _one_special(raw, definitions, "tamanna")
    salasila = _one_special(raw, definitions, "salasila")
    sakt = tuple(
        SpecialSite(point, location, definitions[point].default)
        for point in _points_of_kind(raw, definitions, "sakt")
        for location in definitions[point].locations
    )
    return Khilaf(
        definitions,
        raa,
        yaa,
        CanonicalKhilaf(VowelKhilaf(vowels), letters, madd, tamanna, salasila, sakt),
        catalogue,
        group_order,
        dynamic_sites or {},
    )


def _group_order(raw, catalogue, path) -> tuple[str, ...]:
    order = tuple(str(group) for group in raw)
    if len(order) != len(set(order)):
        raise KhilafError(f"{path}: group_order contains duplicates")
    groups = {entry.group for entry in catalogue.values()}
    if order and set(order) != groups:
        missing = sorted(groups - set(order))
        extra = sorted(set(order) - groups)
        raise KhilafError(
            f"{path}: group_order mismatch; missing={missing}, extra={extra}"
        )
    return order


def _catalogue(raw, definitions, registers, path):
    if set(raw) != {point.value for point in definitions}:
        missing = sorted({point.value for point in definitions} - set(raw))
        extra = sorted(set(raw) - {point.value for point in definitions})
        raise KhilafError(f"{path}: catalogue mismatch; missing={missing}, extra={extra}")
    result = {}
    for point in definitions:
        spec = raw[point.value]
        where = f"{path} catalogue[{point.value}]"
        require_keys(
            spec,
            {"group", "display_name", "website_visible"},
            optional={
                "description", "occurrences", "dynamic_scope", "subgroup",
                "register",
            },
            name=where,
        )
        sources = [
            key for key in ("occurrences", "register", "dynamic_scope")
            if spec.get(key)
        ]
        if len(sources) > 1:
            raise KhilafError(f"{where}: {sources} are mutually exclusive")
        spans = tuple(_span(value) for value in spec.get("occurrences", ()))
        if spec.get("register"):
            name = str(spec["register"])
            if name not in registers:
                raise KhilafError(f"{where}: unknown register {name!r}")
            spans = registers[name]
        result[point] = VariantCatalogueEntry(
            point,
            str(spec["group"]),
            str(spec["display_name"]),
            str(spec["description"]) if spec.get("description") else None,
            bool(spec["website_visible"]),
            spans,
            str(spec["dynamic_scope"]) if spec.get("dynamic_scope") else None,
            str(spec["subgroup"]) if spec.get("subgroup") else None,
        )
    return result


def _span(raw) -> VariantSpan:
    require_keys(raw, {"words", "anchor", "requires"}, name="variant occurrence")
    words = tuple(_location(value) for value in raw["words"])
    if not words or len(words) > 2:
        raise KhilafError("variant occurrence must cover one or two words")
    anchor = str(raw["anchor"])
    requires = str(raw["requires"])
    if anchor not in {"word", "boundary"}:
        raise KhilafError(f"bad variant anchor {anchor!r}")
    if requires not in {"all", "wasl", "waqf", "ibtidaa", "joined"}:
        raise KhilafError(f"bad variant requirement {requires!r}")
    return VariantSpan(words, anchor, requires)


def _one_special(raw, definitions, kind: str) -> SpecialSite | None:
    points = _points_of_kind(raw, definitions, kind)
    if not points:
        return None
    if len(points) != 1 or len(definitions[points[0]].locations) != 1:
        raise KhilafError(f"{kind}: expected exactly one location")
    point = points[0]
    return SpecialSite(
        point, next(iter(definitions[point].locations)), definitions[point].default
    )


def _definitions(raw, path) -> dict[KhilafId, VariantDefinition]:
    definitions = {}
    for name, spec in raw.items():
        try:
            point = KhilafId(str(name))
        except ValueError as error:
            raise KhilafError(f"{path}: {error}") from None
        definitions[point] = _definition(point, spec, path)
    return definitions


def _points_of_kind(raw, definitions, kind: str) -> tuple[KhilafId, ...]:
    return tuple(
        point
        for point in definitions
        if raw[point.value]["kind"] == kind
    )


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
    # The public option index is a reading aid, not a source transcription.
    # Keep face 1 consistent across riwayat by publishing the default first.
    options = (default, *(option for option in options if option != default))
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
