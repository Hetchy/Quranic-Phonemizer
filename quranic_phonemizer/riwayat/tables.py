"""Load the rule letter tables: the shared ones, then a riwayah's overrides."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..dataio import load_yaml, require_keys
from ..model.canon import ABJAD, CanonLetter, Rule
from ..rules.tables import Followers, Pairs

SCHEMA_VERSION = 1

LETTER_SETS = ("never_follows", "qalqala", "always_heavy")
FOLLOWER_SETS = ("followers_of_noon", "followers_of_meem")
KEYS = {*LETTER_SETS, *FOLLOWER_SETS, "pairs"}


class RuleTableError(ValueError):
    """A name in rules.yaml that is not a Rule, or a letter that is not one."""


@dataclass(frozen=True, slots=True)
class RuleTables:
    followers_of_noon: Followers
    followers_of_meem: Followers
    never_follows: frozenset[CanonLetter]
    qalqala: frozenset[CanonLetter]
    always_heavy: frozenset[CanonLetter]
    pairs: Pairs


#: Arabic glyph to canonical letter. The tables are written in Arabic
#: because the people who check them read Arabic; `ABJAD` is the one
#: statement of which glyph names which letter.
GLYPHS = {glyph: CanonLetter(name) for name, glyph in ABJAD.items()}


def load_rule_tables(shared: Path, riwayah: Path | None = None) -> RuleTables:
    """`riwayah` overrides the shared file one top-level key at a time, so a
    riwayah that differs on one family inherits the rest rather than copying."""
    data = _versioned(shared, KEYS)
    if riwayah is not None and riwayah.exists():
        data.update(_versioned(riwayah, KEYS, partial=True))
    where = str(shared if riwayah is None else riwayah)
    never = _letters(data["never_follows"], where)
    return RuleTables(
        followers_of_noon=_followers(
            data["followers_of_noon"], never, where
        ),
        followers_of_meem=_followers(
            data["followers_of_meem"], never, where
        ),
        never_follows=never,
        qalqala=_letters(data["qalqala"], where),
        always_heavy=_letters(data["always_heavy"], where),
        pairs=Pairs(_pairs(data["pairs"], where)),
    )


def _versioned(path: Path, keys: set[str], *, partial: bool = False) -> dict:
    data = load_yaml(path)
    version = data.pop("schema_version", None)
    if version != SCHEMA_VERSION:
        raise RuleTableError(
            f"{path}: schema_version {version!r}, expected {SCHEMA_VERSION}"
        )
    require_keys(data, set() if partial else keys, name=str(path),
                 optional=keys if partial else set())
    return data


def _rule(name: str, where: str) -> Rule:
    try:
        return Rule(name)
    except ValueError:
        raise RuleTableError(f"{where}: {name!r} is not a Rule") from None


def _letter(glyph: str, where: str) -> CanonLetter:
    letter = GLYPHS.get(glyph)
    if letter is None:
        raise RuleTableError(f"{where}: {glyph!r} is not a letter")
    return letter


def _letters(names: list[str], where: str) -> frozenset[CanonLetter]:
    return frozenset(_letter(name, where) for name in names)


def _followers(
    block: dict[str, list[str]],
    never: frozenset[CanonLetter],
    where: str,
) -> Followers:
    by_rule = {
        _rule(name, where): _letters(letters, where)
        for name, letters in block.items()
    }
    _reject_overlap(by_rule, where)
    return Followers(by_rule=by_rule, never_follows=never)


def _reject_overlap(by_rule: dict[Rule, frozenset[CanonLetter]], where: str) -> None:
    """Outcomes are read in order, so an overlap would be a silent precedence
    rule rather than the partition the domain describes."""
    seen: dict[CanonLetter, Rule] = {}
    for rule, letters in by_rule.items():
        for letter in letters:
            if letter in seen:
                raise RuleTableError(
                    f"{where}: {letter.value} is claimed by both "
                    f"{seen[letter].value} and {rule.value}"
                )
            seen[letter] = rule


def _pairs(
    block: dict[str, list[list[str]]], where: str
) -> dict[tuple[CanonLetter, CanonLetter], Rule]:
    out: dict[tuple[CanonLetter, CanonLetter], Rule] = {}
    for name, entries in block.items():
        rule = _rule(name, where)
        for entry in entries:
            if len(entry) != 2:
                raise RuleTableError(f"{where}: {name} entry {entry} is not a pair")
            pair = (
                _letter(entry[0], where),
                _letter(entry[1], where),
            )
            if pair in out:
                raise RuleTableError(f"{where}: pair {entry} is listed twice")
            out[pair] = rule
    return out
