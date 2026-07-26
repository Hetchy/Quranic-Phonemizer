"""The Ledger: authored canonical facts, and the witnesses that agree with them.

The value type is a canonical `SlotFact` value — the same closed union the
adapters emit. There is no syntax for "do something", so the Ledger cannot grow
into a rule engine (ADR-003 §7).

Two roles, and the difference is the whole point of L2:

  * `Supply` is script-independent and carries a citation. Exactly one per
    `(SlotId, SlotFact)` per build.
  * `Assert` is script-scoped and carries none. It must agree with its supply.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias

from ..dataio import load_yaml, require_keys
from ..model.address import Location, Script, SlotId, VerseRef
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
from ..model.inscription import SlotFact

SCHEMA_VERSION = 1

#: Every canonical value spells as a lowercase ASCII identifier. Testing for
#: that — rather than for the notation characters of some alphabet — keeps the
#: check a statement about the *canonical* vocabulary, which is what `canon/`
#: is allowed to know (ADR-007 §4.9).
_CANONICAL_SPELLING = frozenset("abcdefghijklmnopqrstuvwxyz_")


class LedgerError(ValueError):
    """Every message names the address and the two disagreeing sources."""


@dataclass(frozen=True, slots=True)
class VerseSlot:
    """`2:245#17` — the normal form."""

    verse: VerseRef
    ordinal: int

    def __str__(self) -> str:
        return f"{self.verse}#{self.ordinal}"


@dataclass(frozen=True, slots=True)
class WordSlot:
    """`2:245:14#5` — a reviewable alias the builder resolves and normalizes."""

    location: Location
    index: int

    def __str__(self) -> str:
        return f"{self.location}#{self.index}"


SlotRef: TypeAlias = VerseSlot | WordSlot


@dataclass(frozen=True, slots=True)
class Supply:
    ref: SlotRef
    fact: SlotFact
    value: object
    skeleton: str
    citation: str


@dataclass(frozen=True, slots=True)
class Assert:
    script: Script
    ref: SlotRef
    fact: SlotFact
    value: object
    skeleton: str


@dataclass(frozen=True, slots=True)
class Ledger:
    supplies: tuple[Supply, ...]
    asserts: tuple[Assert, ...]

    def supply_for(self, slot: SlotId, fact: SlotFact) -> Supply | None:
        for supply in self.supplies:
            if isinstance(supply.ref, VerseSlot) and supply.fact is fact:
                if SlotId(supply.ref.verse, supply.ref.ordinal) == slot:
                    return supply
        return None


EMPTY = Ledger((), ())


# ------------------------------------------------------------------ parsing
def parse_slot_ref(raw: object) -> SlotRef:
    if not isinstance(raw, str) or "#" not in raw:
        raise LedgerError(f"slot key {raw!r} is not a SlotId or a word alias")
    address, _, index = raw.partition("#")
    parts = address.split(":")
    if not index.isdigit() or not all(p.isdigit() for p in parts):
        raise LedgerError(f"slot key {raw!r} is not a SlotId or a word alias")
    if len(parts) == 2:
        return VerseSlot(VerseRef(int(parts[0]), int(parts[1])), int(index))
    if len(parts) == 3:
        return WordSlot(Location(*(int(p) for p in parts)), int(index))
    raise LedgerError(f"slot key {raw!r} is not a SlotId or a word alias")


def parse_fact(raw: object) -> SlotFact:
    try:
        return SlotFact(str(raw).lower())
    except ValueError:
        raise LedgerError(
            f"fact {raw!r} is outside the canonical vocabulary "
            f"{[f.value for f in SlotFact]}"
        ) from None


def parse_value(fact: SlotFact, raw: object, *, where: str) -> object:
    """Into the closed canonical vocabulary, or raise naming the address."""
    _reject_output_vocabulary(raw, where=where)
    match fact:
        case SlotFact.LETTER:
            return _enum(CanonLetter, raw, where=where, what="CanonLetter")
        case SlotFact.ONSET:
            return _enum(Onset, raw, where=where, what="Onset")
        case SlotFact.NUCLEUS:
            return _nucleus(raw, where=where)
        case SlotFact.SAKT:
            if not isinstance(raw, bool):
                raise LedgerError(f"{where}: SAKT takes a boolean, got {raw!r}")
            return raw
    raise LedgerError(f"{where}: unhandled fact {fact!r}")


def _reject_output_vocabulary(raw: object, *, where: str) -> None:
    if not isinstance(raw, str):
        return
    if not set(raw.lower()) <= _CANONICAL_SPELLING:
        raise LedgerError(
            f"{where}: value {raw!r} does not spell as a canonical name, so it "
            f"is expressed in output vocabulary; the Ledger holds canonical "
            f"facts only"
        )


def _enum(enum: type, raw: object, *, where: str, what: str) -> object:
    try:
        return enum(str(raw).lower())
    except ValueError:
        raise LedgerError(
            f"{where}: {raw!r} is not a {what}; "
            f"expected one of {[m.value for m in enum]}"
        ) from None


_NUCLEUS_KINDS = {
    "silent": Silent,
    "short": Short,
    "long": Long,
    "silah": Silah,
    "pausallong": PausalLong,
}


def _nucleus(raw: object, *, where: str) -> Nucleus:
    if not isinstance(raw, dict) or "kind" not in raw:
        raise LedgerError(f"{where}: a nucleus needs a `kind`, got {raw!r}")
    kind = str(raw["kind"]).replace("_", "").lower()
    factory = _NUCLEUS_KINDS.get(kind)
    if factory is None:
        raise LedgerError(
            f"{where}: nucleus kind {raw['kind']!r} is outside the vocabulary "
            f"{sorted(_NUCLEUS_KINDS)}"
        )
    if factory is Silent:
        return Silent()
    quality = _enum(Quality, raw.get("quality"), where=where, what="Quality")
    return factory(quality)  # type: ignore[operator]


# ------------------------------------------------------------------- loading
def load_ledger(path: Path) -> Ledger:
    """Rejects, by name: a duplicate `Supply` for one key; a value outside the
    canonical vocabulary; an `Assert` with no matching `Supply`; a key that is
    not a `SlotId`; a missing `skeleton`; a value in output vocabulary."""
    data = load_yaml(path)
    require_keys(
        data,
        {"schema_version", "riwayah"},
        name=str(path),
        optional={"supplies", "asserts"},
    )
    if data["schema_version"] != SCHEMA_VERSION:
        raise LedgerError(
            f"{path}: schema_version {data['schema_version']!r}, expected "
            f"{SCHEMA_VERSION}"
        )

    supplies = tuple(
        _supply(row, where=f"{path} supplies[{i}]")
        for i, row in enumerate(data.get("supplies") or ())
    )
    _reject_duplicate_supply(supplies, path)

    asserts = tuple(
        _assert(row, where=f"{path} asserts[{i}]")
        for i, row in enumerate(data.get("asserts") or ())
    )
    _reject_orphan_assert(supplies, asserts, path)
    return Ledger(supplies, asserts)


def _supply(row: Any, *, where: str) -> Supply:
    require_keys(
        row, {"slot", "fact", "value", "skeleton", "citation"}, name=where
    )
    fact = parse_fact(row["fact"])
    return Supply(
        ref=parse_slot_ref(row["slot"]),
        fact=fact,
        value=parse_value(fact, row["value"], where=where),
        skeleton=_skeleton(row["skeleton"], where=where),
        citation=str(row["citation"]),
    )


def _assert(row: Any, *, where: str) -> Assert:
    require_keys(row, {"script", "slot", "fact", "value", "skeleton"}, name=where)
    fact = parse_fact(row["fact"])
    return Assert(
        script=_enum(Script, row["script"], where=where, what="Script"),
        ref=parse_slot_ref(row["slot"]),
        fact=fact,
        value=parse_value(fact, row["value"], where=where),
        skeleton=_skeleton(row["skeleton"], where=where),
    )


def _skeleton(raw: object, *, where: str) -> str:
    text = str(raw).strip()
    if not text:
        raise LedgerError(
            f"{where}: `skeleton` is mandatory — it is what keeps a "
            f"verse-scoped ordinal reviewable and catches ordinal drift"
        )
    return text


def _reject_duplicate_supply(supplies: tuple[Supply, ...], path: Path) -> None:
    seen: dict[tuple[str, SlotFact], Supply] = {}
    for supply in supplies:
        key = (str(supply.ref), supply.fact)
        if key in seen:
            raise LedgerError(
                f"{path}: two supplies for {supply.ref} {supply.fact.value} — "
                f"{seen[key].citation!r} and {supply.citation!r}. Exactly one "
                f"canonical supplier per (SlotId, SlotFact)."
            )
        seen[key] = supply


def _reject_orphan_assert(
    supplies: tuple[Supply, ...], asserts: tuple[Assert, ...], path: Path
) -> None:
    keys = {(str(s.ref), s.fact) for s in supplies}
    for row in asserts:
        if (str(row.ref), row.fact) not in keys:
            raise LedgerError(
                f"{path}: {row.script.value} asserts {row.fact.value} at "
                f"{row.ref} with no supply to agree with. An assert is a "
                f"witness, not an authority."
            )
