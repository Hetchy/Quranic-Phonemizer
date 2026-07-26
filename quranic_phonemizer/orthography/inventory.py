"""The scalar inventory: schema, not content.

Total over a script's scalars — an unlisted scalar is a parse error (L3). This
module knows the *shape* of an inventory and nothing about any writing system;
every scalar lives in `data/riwayat/<r>/scripts/<script>.yaml`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..dataio import load_yaml, require_keys
from ..model.address import Riwayah, Script
from ..model.canon import (
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
    "letters",
    "seats",
    "combining_hamza",
    "evidences",
    "attests",
    "decorates",
    "advice",
    "structural",
    "polysemous",
}


class InventoryError(ValueError):
    """Names the scalar and the file. Never a sentinel."""


@dataclass(frozen=True, slots=True)
class LetterEntry:
    """A base scalar: its canonical letter, plus what the *glyph* implies."""

    letter: CanonLetter
    onset: Onset | None = None
    dagger_host: bool = False
    """The glyph may carry a lengthening dagger for the previous slot — it is
    rasm with no letter identity of its own (Uthmani `ى`, `و`)."""
    bare_rasm: bool = False
    """Bare, word-finally, the glyph stands for an unwritten alif."""


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
    """The mark declares its host to be rasm — Uthmani's `۟`. An annotation
    that merely points at a live letter must not set this."""
    advice: StopAdvice | None = None
    structural: bool = False
    polysemous: tuple[str, ...] = ()

    @property
    def is_evidence(self) -> bool:
        return self.fact is not None


@dataclass(frozen=True, slots=True)
class Inventory:
    script: Script
    riwayah: Riwayah
    letters: dict[str, LetterEntry]
    marks: dict[str, MarkEntry]
    seats: frozenset[str]
    combining_hamza: frozenset[str]
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

    def advice_scalars(self) -> dict[str, StopAdvice]:
        return {c: m.advice for c, m in self.marks.items() if m.advice is not None}


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
    raise InventoryError(f"{where}: unhandled fact {fact!r}")


# --------------------------------------------------------------------- loading
def load_inventory(path: Path) -> Inventory:
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

    letters = {
        char: _letter(spec, where=f"{path} letters[{char!r}]")
        for char, spec in (data.get("letters") or {}).items()
    }
    marks: dict[str, MarkEntry] = {}
    _load_evidences(data, path, marks)
    _load_decorates(data, path, marks)
    _load_advice(data, path, marks)
    _load_structural(data, path, marks)
    _load_polysemous(data, path, marks)

    overlap = sorted(set(letters) & set(marks))
    if overlap:
        raise InventoryError(
            f"{path}: {overlap} are declared both as letters and as marks; a "
            f"scalar resolves to exactly one classification"
        )
    return Inventory(
        script=_member(Script, data["script"], where=str(path)),
        riwayah=_member(Riwayah, data["riwayah"], where=str(path)),
        letters=letters,
        marks=marks,
        seats=frozenset(data.get("seats") or ()),
        combining_hamza=frozenset(data.get("combining_hamza") or ()),
        source=path,
    )


def _letter(spec: Any, *, where: str) -> LetterEntry:
    if isinstance(spec, str):
        return LetterEntry(_member(CanonLetter, spec, where=where))
    require_keys(
        spec,
        {"letter"},
        name=where,
        optional={"onset", "dagger_host", "bare_rasm"},
    )
    onset = spec.get("onset")
    return LetterEntry(
        letter=_member(CanonLetter, spec["letter"], where=where),
        onset=_member(Onset, onset, where=where) if onset else None,
        dagger_host=bool(spec.get("dagger_host", False)),
        bare_rasm=bool(spec.get("bare_rasm", False)),
    )


def _load_evidences(data: Any, path: Path, marks: dict[str, MarkEntry]) -> None:
    for char, spec in (data.get("evidences") or {}).items():
        where = f"{path} evidences[{char!r}]"
        require_keys(
            spec,
            {"fact", "cls"},
            name=where,
            optional={"value", "derivation", "role"},
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
        )


def _load_decorates(data: Any, path: Path, marks: dict[str, MarkEntry]) -> None:
    for char, spec in (data.get("decorates") or {}).items():
        where = f"{path} decorates[{char!r}]"
        require_keys(
            spec, {"slot", "cls"}, name=where, optional={"role", "silences"}
        )
        marks[char] = MarkEntry(
            role=f"decorates:{spec['slot']}",
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


def _load_polysemous(data: Any, path: Path, marks: dict[str, MarkEntry]) -> None:
    """Declaring the ambiguity forces the adapter to defer to the Ledger
    rather than guess (ADR-007 §3)."""
    for char, senses in (data.get("polysemous") or {}).items():
        where = f"{path} polysemous[{char!r}]"
        if char not in marks:
            raise InventoryError(
                f"{where}: a polysemous scalar must also be declared in one of "
                f"{sorted(_SECTIONS - {'polysemous'})}"
            )
        base = marks[char]
        marks[char] = MarkEntry(
            role=base.role,
            cls=base.cls,
            fact=base.fact,
            value=base.value,
            derivation=base.derivation,
            decorates=base.decorates,
            silences=base.silences,
            advice=base.advice,
            structural=base.structural,
            polysemous=tuple(str(s) for s in senses),
        )
