"""The Ledger: authored canonical facts, and the witnesses that agree with them.

Values are closed `SlotFact` variants only, with no syntax for "do something",
so the Ledger cannot grow into a rule engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias

from ..dataio import load_yaml, require_keys
from ..model.address import Location, Riwayah, Script, SlotId, VerseRef
from ..model.canon import Annotation, CanonLetter, Nucleus, Onset, Quality
from ..model.inscription import VOWEL_FACTS, SlotFact

SCHEMA_VERSION = 1

#: Every canonical value spells as a lowercase ASCII identifier. Checking that,
#: rather than any script's notation, keeps this a statement about canonical
#: vocabulary alone.
_CANONICAL_SPELLING = frozenset("abcdefghijklmnopqrstuvwxyz_")


class LedgerError(ValueError):
    """Every message names the address and the two disagreeing sources."""


@dataclass(frozen=True, slots=True)
class VerseSlot:
    """`2:5#7` - the normal form."""

    verse: VerseRef
    ordinal: int

    def __str__(self) -> str:
        return f"{self.verse}#{self.ordinal}"


@dataclass(frozen=True, slots=True)
class WordSlot:
    """`2:5:4#1` - a reviewable alias the builder resolves and normalizes."""

    location: Location
    index: int

    def __str__(self) -> str:
        return f"{self.location}#{self.index}"


SlotRef: TypeAlias = VerseSlot | WordSlot


@dataclass(frozen=True, slots=True)
class Supply:
    """Script-independent and cited; exactly one per `(SlotId, SlotFact)`."""

    ref: SlotRef
    fact: SlotFact
    value: object
    skeleton: str
    citation: str


@dataclass(frozen=True, slots=True)
class Assert:
    """Script-scoped and uncited; must agree with its matching `Supply`."""

    script: Script
    ref: SlotRef
    fact: SlotFact
    value: object
    skeleton: str


@dataclass(frozen=True, slots=True)
class Ledger:
    supplies: tuple[Supply, ...]
    asserts: tuple[Assert, ...]


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
        case _ if fact in VOWEL_FACTS:
            return _nucleus(raw, where=where)
        case SlotFact.TAJWEED_MARK:
            return _enum(Annotation, raw, where=where, what="Annotation")
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
    "silent": Nucleus.silent,
    "short": Nucleus.short,
    "long": Nucleus.long,
    "silah": Nucleus.silah,
    "pausallong": Nucleus.pausal_long,
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
    if kind == "silent":
        return Nucleus.silent()
    quality = _enum(Quality, raw.get("quality"), where=where, what="Quality")
    return factory(quality)


# ------------------------------------------------------------------- loading
def load_ledger(path: Path, *, riwayah: Riwayah) -> Ledger:
    """Rejects, by name: another riwayah's file; a duplicate `Supply`; a value
    outside the canonical vocabulary or inside the output one; an orphan
    `Assert`; a key that is not a `SlotId`; a missing `skeleton`."""
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
    declared = _enum(Riwayah, data["riwayah"], where=str(path), what="Riwayah")
    if declared is not riwayah:
        raise LedgerError(
            f"{path}: authored for {declared.value}, loaded as {riwayah.value}"
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
    _check_asserts(supplies, asserts, path)
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


def _check_asserts(
    supplies: tuple[Supply, ...], asserts: tuple[Assert, ...], path: Path
) -> None:
    """An assert must have a supply to agree with, and must agree with it."""
    by_key = {(str(s.ref), s.fact): s for s in supplies}
    for row in asserts:
        supply = by_key.get((str(row.ref), row.fact))
        if supply is None:
            raise LedgerError(
                f"{path}: {row.script.value} asserts {row.fact.value} at "
                f"{row.ref} with no supply to agree with. An assert is a "
                f"witness, not an authority."
            )
        if supply.value != row.value:
            raise LedgerError(
                f"{path}: {row.script.value} asserts {row.fact.value} at "
                f"{row.ref} is {row.value!r}, but the supply says "
                f"{supply.value!r}. A witness that disagrees is a "
                f"contradiction, not a witness."
            )
