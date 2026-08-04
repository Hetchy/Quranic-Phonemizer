"""What `schema.py`'s canonical shape must reject -- 02-gate section 5.

One check function per tagged union, plus the document- and pairing-array
passes; raises `SchemaError` and never repairs a document.
"""
from __future__ import annotations

from .document import SCHEMA_VERSION
from .schema import SchemaError

_VOWEL_KINDS = frozenset({"absent", "short", "long"})
_SOUND_FIELDS = {
    "consonant": frozenset({"letter", "geminate", "emphatic", "ghunnah", "eased"}),
    "vowel": frozenset({"quality", "long", "emphatic"}),
    "qalqala": frozenset({"degree"}),
}
_SPELLING_KEYS = {
    "supplies": frozenset({"kind", "glyph", "unit", "fact"}),
    "witnesses": frozenset({"kind", "glyph", "unit"}),
    "decorates": frozenset({"kind", "glyph", "unit"}),
    "structural": frozenset({"kind", "glyph"}),
}
_ATTRIBUTION_KEYS = {
    "hosts": frozenset({"kind", "unit", "part", "sound", "by"}),
    "mergedinto": frozenset({"kind", "unit", "part", "sound", "by"}),
    "silent": frozenset({"kind", "unit", "part", "by"}),
}
_MODIFIER_KEYS = {
    "recolours": frozenset({"kind", "sound", "by"}),
    "setslength": frozenset({"kind", "sound", "by", "length"}),
    "classifies": frozenset({"kind", "sound", "by"}),
}


def _exact_keys(row: dict, allowed: frozenset[str], where: str) -> None:
    if set(row) != allowed:
        raise SchemaError(f"{where}: keys {sorted(row)}, expected {sorted(allowed)}")


def check_version(data: dict) -> None:
    if data.get("schema_version") != SCHEMA_VERSION:
        raise SchemaError(
            f"unknown schema version {data.get('schema_version')!r}, "
            f"this reader knows {SCHEMA_VERSION!r}"
        )


def check_vowel_state(state: dict, where: str) -> None:
    kind = state.get("kind")
    if kind not in _VOWEL_KINDS:
        raise SchemaError(f"{where}: {kind!r} is not a vowel kind")
    has_quality = "quality" in state and state["quality"] is not None
    if kind == "absent":
        if "quality" in state:
            raise SchemaError(f"{where}: absent carries a quality field")
    elif not has_quality:
        raise SchemaError(f"{where}: {kind} carries no quality")


def check_sound(sound: dict, where: str) -> None:
    kind = sound.get("kind")
    if kind not in _SOUND_FIELDS:
        raise SchemaError(f"{where}: {kind!r} is not a sound kind")
    extra = set(sound) - {"token", "kind"} - _SOUND_FIELDS[kind]
    if extra:
        raise SchemaError(f"{where}: {kind} sound carries {sorted(extra)}")


def check_spelling(edge: dict, n_glyphs: int, n_units: int) -> None:
    kind = edge.get("kind")
    if kind not in _SPELLING_KEYS:
        raise SchemaError(f"spelling: {kind!r} is not a spelling kind")
    _exact_keys(edge, _SPELLING_KEYS[kind], f"spelling[{kind}]")
    if not 0 <= edge["glyph"] < n_glyphs:
        raise SchemaError(f"spelling[{kind}]: glyph {edge['glyph']} out of range")
    if kind != "structural" and not 0 <= edge["unit"] < n_units:
        raise SchemaError(f"spelling[{kind}]: unit {edge['unit']} out of range")


def check_attribution(edge: dict, n_units: int, n_sounds: int) -> None:
    kind = edge.get("kind")
    if kind not in _ATTRIBUTION_KEYS:
        raise SchemaError(f"attribution: {kind!r} is not an attribution kind")
    _exact_keys(edge, _ATTRIBUTION_KEYS[kind], f"attribution[{kind}]")
    if not 0 <= edge["unit"] < n_units:
        raise SchemaError(f"attribution[{kind}]: unit {edge['unit']} out of range")
    if kind != "silent" and not 0 <= edge["sound"] < n_sounds:
        raise SchemaError(f"attribution[{kind}]: sound {edge['sound']} out of range")
    if edge.get("part") not in ("consonant", "vowel"):
        raise SchemaError(f"attribution[{kind}]: {edge.get('part')!r} is not a part")


def check_modifier(edge: dict, n_sounds: int, n_rules: int) -> None:
    kind = edge.get("kind")
    if kind not in _MODIFIER_KEYS:
        raise SchemaError(f"modifier: {kind!r} is not a modifier kind")
    _exact_keys(edge, _MODIFIER_KEYS[kind], f"modifier[{kind}]")
    if not 0 <= edge["sound"] < n_sounds:
        raise SchemaError(f"modifier[{kind}]: sound {edge['sound']} out of range")
    if not 0 <= edge["by"] < n_rules:
        raise SchemaError(f"modifier[{kind}]: by {edge['by']} out of range")


def check_rendered_glyph(glyph: dict) -> None:
    if not glyph.get("char"):
        raise SchemaError("rendered glyph carries an empty character")


def check_structural_glyphs(glyphs: list[dict], structural: set[int]) -> None:
    for index, glyph in enumerate(glyphs):
        if index in structural and glyph.get("word") is not None:
            raise SchemaError(f"glyph[{index}]: structural but names a word")


def check_merger_has_host(attributions: list[dict], rules: list[dict]) -> None:
    """Every `MergedInto` names an occurrence whose `RuleInstance.host` is
    set -- a merger with no second unit is not a merger."""
    for edge in attributions:
        if edge.get("kind") != "mergedinto" or edge.get("by") is None:
            continue
        if rules[edge["by"]].get("host") is None:
            raise SchemaError(f"mergedinto: rule {edge['by']} names no host")


def check_no_duplicate_relations(rows: list[dict], where: str) -> None:
    seen = set()
    for row in rows:
        key = tuple(sorted((k, _hashable(v)) for k, v in row.items()))
        if key in seen:
            raise SchemaError(f"{where}: duplicate relation {row}")
        seen.add(key)


def _hashable(value):
    return tuple(value) if isinstance(value, list) else value


def validate(data: dict) -> None:
    """The whole document. Raises on the first violation."""
    check_version(data)
    n_glyphs, n_units = len(data["glyphs"]), len(data["units"])
    n_sounds, n_rules = len(data["sounds"]), len(data["rules"])
    for unit in data["units"]:
        check_vowel_state(unit["vowel"]["joined"], "unit.vowel.joined")
        check_vowel_state(unit["vowel"]["stopped"], "unit.vowel.stopped")
    for sound in data["sounds"]:
        check_sound(sound, "sound")
    structural = {
        e["glyph"] for e in data["spellings"] if e.get("kind") == "structural"
    }
    for edge in data["spellings"]:
        check_spelling(edge, n_glyphs, n_units)
    check_structural_glyphs(data["glyphs"], structural)
    for glyph in data["rendered"]:
        check_rendered_glyph(glyph)
    for edge in data["attributions"]:
        check_attribution(edge, n_units, n_sounds)
    for edge in data["modifiers"]:
        check_modifier(edge, n_sounds, n_rules)
    check_merger_has_host(data["attributions"], data["rules"])
    for name in ("spellings", "attributions", "modifiers"):
        check_no_duplicate_relations(data[name], name)


def check_pairing(pairing: dict, *, n_pairings: int, n_glyphs: int,
                  n_sounds: int, n_rules: int) -> None:
    after = pairing.get("after")
    if after is not None and not 0 <= after < n_pairings:
        raise SchemaError(f"pairing: after {after} out of range")
    if after is not None and pairing.get("glyphs"):
        raise SchemaError("pairing: a gap row carries glyphs")
    for index in pairing.get("glyphs", ()):
        if not 0 <= index < n_glyphs:
            raise SchemaError(f"pairing: glyph {index} out of range")
    for field in ("sounds", "shares"):
        for index in pairing.get(field, ()):
            if not 0 <= index < n_sounds:
                raise SchemaError(f"pairing: {field} index {index} out of range")
    for index in pairing.get("rules", ()):
        if not 0 <= index < n_rules:
            raise SchemaError(f"pairing: rule {index} out of range")


def check_pairings_cover_glyphs(
    pairings: list[dict], glyphs: list[dict], structural: set[int]
) -> None:
    covered = {g for p in pairings for g in p.get("glyphs", ())}
    for index, glyph in enumerate(glyphs):
        if index not in structural and index not in covered:
            raise SchemaError(f"glyph[{index}]: in no pairing")


def validate_pairings(
    pairings: list[dict], glyphs: list[dict], structural: set[int],
    *, n_sounds: int, n_rules: int,
) -> None:
    for pairing in pairings:
        check_pairing(
            pairing, n_pairings=len(pairings), n_glyphs=len(glyphs),
            n_sounds=n_sounds, n_rules=n_rules,
        )
    check_pairings_cover_glyphs(pairings, glyphs, structural)


__all__ = ["validate", "validate_pairings"]
