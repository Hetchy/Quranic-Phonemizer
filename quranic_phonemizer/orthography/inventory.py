"""The scalar inventory: schema, not content.

Total over a script's scalars: an unlisted scalar is a parse error. Scalars
themselves live in `data/riwayat/<r>/scripts/<script>.yaml`.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..dataio import load_yaml, require_keys
from ..model.address import Riwayah, Script
from ..model.canon import (
    Annotation,
    CanonLetter,
    Long,
    Nucleus,
    Onset,
    PausalLong,
    Quality,
    Short,
    Silah,
    Silent,
)
from ..model.inscription import GraphemeClass, SlotFact, StopAdvice

SCHEMA_VERSION = 1

_SECTIONS = {
    "marks_what_it_sounds",
    "letters",
    "seats",
    "combining_hamza",
    "evidences",
    "decorates",
    "advice",
    "structural",
}


#: Derivations `canon.build` names itself, for every script.
ALWAYS_RUN = frozenset({"carrier", "hamzat_wasl", "wasl_helping_vowel"})

#: Roles one script spells and another has no mark for. `ٖ` writes a kasra
#: and its yaa together where Uthmani writes the two separately, so only
#: IndoPak can declare it.
SCRIPT_OPTIONAL = frozenset({"silah_waw", "silah_ya", "small_waw", "small_ya"})


class InventoryError(ValueError):
    """Names the scalar and the file. Never a sentinel."""


@dataclass(frozen=True, slots=True)
class LetterEntry:
    """A base scalar: its canonical letter, plus what the *glyph* implies."""

    letter: CanonLetter
    onset: Onset | None = None
    dagger_host: bool = False
    """The glyph may carry a lengthening dagger for the previous slot: rasm
    with no letter identity of its own (Uthmani `ى`, `و`)."""
    bare_rasm: bool = False
    """Bare, word-finally, the glyph stands for an unwritten alif."""
    rasm_only: bool = False
    """The glyph never spells a sound of its own. IndoPak draws the maqsura
    only as a hamza's seat or as rasm, and writes a sounded yaa as `ي`."""
    seat: bool = False
    """A combining hamza written here rests on the glyph rather than being a
    letter of its own, so the cluster becomes the hamza: `ٮ` + `ٔ` is `ئ`."""


@dataclass(frozen=True, slots=True)
class MarkEntry:
    """A non-base scalar and what it declares."""

    role: str
    cls: GraphemeClass
    fact: SlotFact | None = None
    value: object | None = None
    derivation: str | None = None
    decorates: str | None = None
    silences: bool = False
    """The mark declares its host to be rasm (Uthmani's `۟`); an annotation
    that merely points at a live letter must not set this."""
    omitted: bool = False
    """A letter of the reading the rasm leaves out, written small: Uthmani's
    `ۥ ۦ ۧ ۨ`. It is a letter, so it takes a position of its own rather than
    saying something about the one before it."""
    advice: StopAdvice | None = None
    structural: bool = False


@dataclass(frozen=True, slots=True)
class Inventory:
    script: Script
    riwayah: Riwayah
    letters: dict[str, LetterEntry]
    marks: dict[str, MarkEntry]
    seats: frozenset[str]
    combining_hamza: frozenset[str]
    marks_what_it_sounds: bool
    """Every letter this script sounds carries a haraka, a sukun or a shadda,
    so a letter with no mark at all is rasm. Scripts that leave their length
    carriers bare say `false` and mark the silent letters instead."""

    source: Path

    #: A seat is a base position with no letter identity of its own. It shows
    #: nothing until a hamza or a dagger is written on it.
    SEAT = MarkEntry(role="seat", cls=GraphemeClass.STRUCTURAL)

    def classify(self, char: str) -> LetterEntry | MarkEntry:
        if char in self.seats:
            return self.SEAT
        entry = self.letters.get(char) or self.marks.get(char)
        if entry is None:
            raise InventoryError(
                f"{self.source}: U+{ord(char):04X} {char!r} is not declared. "
                f"The inventory is total over the script's scalars; an "
                f"unlisted scalar is a parse error, not a silent skip."
            )
        return entry


# ---------------------------------------------------------------- value parsing
_NUCLEUS_KINDS = {
    "silent": Silent,
    "short": Short,
    "long": Long,
    "silah": Silah,
    "pausallong": PausalLong,
}


def _nucleus(raw: Any, *, where: str) -> Nucleus:
    if not isinstance(raw, dict) or "kind" not in raw:
        raise InventoryError(f"{where}: a nucleus needs a `kind`, got {raw!r}")
    factory = _NUCLEUS_KINDS.get(str(raw["kind"]).replace("_", "").lower())
    if factory is None:
        raise InventoryError(f"{where}: unknown nucleus kind {raw['kind']!r}")
    if factory is Silent:
        return Silent()
    return factory(_member(Quality, raw.get("quality"), where=where))  # type: ignore[operator]


def _member(enum: type, raw: Any, *, where: str):
    try:
        return enum(str(raw).lower())
    except ValueError:
        raise InventoryError(
            f"{where}: {raw!r} is not a {enum.__name__}; expected one of "
            f"{[m.value for m in enum]}"
        ) from None


def _fact_value(fact: SlotFact, raw: Any, *, where: str) -> object:
    match fact:
        case SlotFact.LETTER:
            return _member(CanonLetter, raw, where=where)
        case SlotFact.ONSET:
            return _member(Onset, raw, where=where)
        case SlotFact.NUCLEUS:
            return _nucleus(raw, where=where)
        case SlotFact.SAKT:
            return bool(raw)
        case SlotFact.ANNOTATION:
            return _member(Annotation, raw, where=where)
    raise InventoryError(f"{where}: unhandled fact {fact!r}")


# --------------------------------------------------------------------- loading
def load_inventory(
    path: Path,
    *,
    riwayah: Riwayah,
    script: Script,
    derivations: frozenset[str] | None = None,
    roles: dict[str, frozenset[str]] | None = None,
) -> Inventory:
    """`riwayah` and `script` are what the caller believes it is loading; a
    file that declares otherwise is rejected rather than silently believed."""
    data = _header(path, riwayah, script)

    letters = {
        char: _letter(spec, where=f"{path} letters[{char!r}]")
        for char, spec in (data.get("letters") or {}).items()
    }
    marks: dict[str, MarkEntry] = {}
    _load_evidences(data, path, marks)
    _load_decorates(data, path, marks)
    _load_advice(data, path, marks)
    _load_structural(data, path, marks)

    overlap = sorted(set(letters) & set(marks))
    if overlap:
        raise InventoryError(
            f"{path}: {overlap} are declared both as letters and as marks; a "
            f"scalar resolves to exactly one classification"
        )
    _check_contract(path, letters, marks, derivations, roles)
    return Inventory(
        script=script,
        riwayah=riwayah,
        letters=letters,
        marks=marks,
        seats=frozenset(data.get("seats") or ()),
        combining_hamza=frozenset(data.get("combining_hamza") or ()),
        marks_what_it_sounds=bool(data.get("marks_what_it_sounds", False)),
        source=path,
    )


def _header(path: Path, riwayah: Riwayah, script: Script) -> dict:
    """The file's own declarations, checked before anything is parsed."""
    data = load_yaml(path)
    require_keys(
        data,
        {"schema_version", "script", "riwayah"},
        name=str(path),
        optional=_SECTIONS,
    )
    if data["schema_version"] != SCHEMA_VERSION:
        raise InventoryError(
            f"{path}: schema_version {data['schema_version']!r}, expected "
            f"{SCHEMA_VERSION}"
        )
    _check_identity(path, data, riwayah, script)
    return data


def _check_identity(path, data, riwayah: Riwayah, script: Script) -> None:
    declared = (
        _member(Riwayah, data["riwayah"], where=str(path)),
        _member(Script, data["script"], where=str(path)),
    )
    if declared != (riwayah, script):
        raise InventoryError(
            f"{path}: declares {declared[0].value}/{declared[1].value}, "
            f"loaded as {riwayah.value}/{script.value}"
        )


def _check_contract(path, letters, marks, derivations, roles) -> None:
    """Verify every named derivation and required role actually exists.

    `derivations` and `roles` are injected, not imported: `orthography` may
    not depend on `canon`.
    """
    if derivations is not None:
        named = {
            entry.derivation
            for entry in marks.values()
            if getattr(entry, "derivation", None)
        }
        named |= {
            spec.derivation
            for spec in letters.values()
            if getattr(spec, "derivation", None)
        }
        unknown = sorted(named - derivations)
        if unknown:
            raise InventoryError(
                f"{path}: names derivation(s) {unknown} that canon/derive/ "
                f"does not register. Known: {sorted(derivations)}"
            )
    if roles is not None:
        declared = {entry.role for entry in marks.values() if entry.role}
        needed: set[str] = set()
        for derivation in named | ALWAYS_RUN:
            needed |= roles.get(derivation, frozenset())
        missing = sorted(needed - declared - SCRIPT_OPTIONAL)
        if missing:
            raise InventoryError(
                f"{path}: names a derivation reading role(s) {missing} and "
                f"declares no mark with them. A role nothing declares is "
                f"silently absent, never an error at use -- so it is one "
                f"here. Declared: {sorted(declared)}"
            )


def _letter(spec: Any, *, where: str) -> LetterEntry:
    if isinstance(spec, str):
        return LetterEntry(_member(CanonLetter, spec, where=where))
    require_keys(
        spec,
        {"letter"},
        name=where,
        optional={"onset", "dagger_host", "bare_rasm", "rasm_only", "seat"},
    )
    onset = spec.get("onset")
    return LetterEntry(
        letter=_member(CanonLetter, spec["letter"], where=where),
        onset=_member(Onset, onset, where=where) if onset else None,
        dagger_host=bool(spec.get("dagger_host", False)),
        bare_rasm=bool(spec.get("bare_rasm", False)),
        rasm_only=bool(spec.get("rasm_only", False)),
        seat=bool(spec.get("seat", False)),
    )


def _load_evidences(data: Any, path: Path, marks: dict[str, MarkEntry]) -> None:
    for char, spec in (data.get("evidences") or {}).items():
        where = f"{path} evidences[{char!r}]"
        require_keys(
            spec,
            {"fact", "cls"},
            name=where,
            optional={"value", "derivation", "role", "omitted"},
        )
        fact = _member(SlotFact, spec["fact"], where=where)
        has_value, has_derivation = "value" in spec, "derivation" in spec
        if has_value == has_derivation:
            raise InventoryError(
                f"{where}: declare exactly one of `value` or `derivation`. A "
                f"scalar either carries a canonical value outright or defers "
                f"to a named derivation; it never does both or neither."
            )
        marks[char] = MarkEntry(
            role=str(spec.get("role", char)),
            cls=_member(GraphemeClass, spec["cls"], where=where),
            fact=fact,
            value=_fact_value(fact, spec["value"], where=where) if has_value else None,
            derivation=str(spec["derivation"]) if has_derivation else None,
            omitted=bool(spec.get("omitted", False)),
        )


def _load_decorates(data: Any, path: Path, marks: dict[str, MarkEntry]) -> None:
    for char, spec in (data.get("decorates") or {}).items():
        where = f"{path} decorates[{char!r}]"
        require_keys(
            spec, {"slot", "cls"}, name=where, optional={"role", "silences"}
        )
        marks[char] = MarkEntry(
            role=str(spec.get("role", f"decorates:{spec['slot']}")),
            cls=_member(GraphemeClass, spec["cls"], where=where),
            decorates=str(spec["slot"]),
            silences=bool(spec.get("silences", False)),
        )


def _load_advice(data: Any, path: Path, marks: dict[str, MarkEntry]) -> None:
    for char, spec in (data.get("advice") or {}).items():
        where = f"{path} advice[{char!r}]"
        marks[char] = MarkEntry(
            role="advice",
            cls=GraphemeClass.ADVICE,
            advice=_member(StopAdvice, spec, where=where),
        )


def _load_structural(data: Any, path: Path, marks: dict[str, MarkEntry]) -> None:
    for char in data.get("structural") or ():
        marks[char] = MarkEntry(
            role="structural", cls=GraphemeClass.STRUCTURAL, structural=True
        )


