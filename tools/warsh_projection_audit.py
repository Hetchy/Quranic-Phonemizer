"""Audit every selected Warsh scalar through the public analysis facade."""
from __future__ import annotations

import argparse
import unicodedata
from collections import Counter, defaultdict

from quranic_phonemizer import Phonemizer
from quranic_phonemizer.analysis.ids import SCHEMA_VERSION
from quranic_phonemizer.analysis.source_dtos import CharacterKind
from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Riwayah


class ScalarReach:
    def __init__(self) -> None:
        self.count = 0
        self.routes: set[str] = set()
        self.unit_kinds: set[str] = set()
        self.cell_roles: set[str] = set()
        self.tiers: set[str] = set()
        self.statuses: set[str] = set()


class AuditResult:
    def __init__(self, verses, characters, scalars, failures) -> None:
        self.verses = verses
        self.characters = characters
        self.scalars = scalars
        self.failures = failures


def _columns(view):
    return [
        *(column for word in view.words for column in word.columns),
        *(column for boundary in view.boundaries for column in boundary.columns),
    ]


def _audit_view(ref, source, source_cells, transformed, reaches, failures):
    source_by_char = defaultdict(list)
    transformed_by_char = defaultdict(list)
    for column in _columns(source_cells):
        for character in column.source_character_ids:
            source_by_char[character.value].append(column)
    for column in _columns(transformed):
        for character in column.source_character_ids:
            transformed_by_char[character.value].append(column)
    expanded_units = {
        run.source_unit_id.value
        for word in transformed.words for run in word.runs
    }

    units = {unit.id.value: unit for unit in source.units}
    for character in source.characters:
        if (
            character.kind is CharacterKind.SEPARATOR
            and unicodedata.category(character.text).startswith("L")
            and character.text != "ـ"
        ):
            raise ValueError(
                f"character {character.index} {character.text!r} is a "
                "lexical glyph classified as a separator"
            )
        reach = reaches[character.text]
        reach.count += 1
        source_columns = source_by_char[character.id.value]
        transformed_columns = transformed_by_char[character.id.value]
        if character.kind is CharacterKind.LEXICAL:
            expanded = character.letter_unit_id.value in expanded_units
            if len(source_columns) != 1 or (
                len(transformed_columns) != 1 and not expanded
            ):
                failures.append(
                    f"{ref} character {character.index} {character.text!r}: "
                    f"source columns={len(source_columns)}, "
                    f"transformed columns={len(transformed_columns)}"
                )
                continue
            reach.routes.add("spelled_run" if expanded else "word_cell")
            unit = units[character.letter_unit_id.value]
            reach.unit_kinds.add(unit.kind.value)
            for column in transformed_columns:
                reach.cell_roles.add(column.role.value)
                reach.tiers.add(column.tier.value)
                reach.statuses.add(column.status.value)
            continue

        if character.boundary_id is None or character.letter_unit_id is not None:
            failures.append(
                f"{ref} character {character.index} {character.text!r}: "
                "non-lexical character has no boundary or has a letter unit"
            )
        if transformed_columns:
            reach.routes.add("boundary_cell")
            for column in transformed_columns:
                reach.cell_roles.add(column.role.value)
                reach.tiers.add(column.tier.value)
                reach.statuses.add(column.status.value)
        else:
            reach.routes.add("boundary_character")


def _audit_facade(result, source, transformed) -> None:
    sounds = {sound.id for sound in result.sounds}
    occurrences = {occurrence.id for occurrence in result.rule_occurrences}
    mergers = {
        merger.id for merger in result.mergers
        if merger.boundary_id is not None
    }
    units = {unit.id for unit in source.units}
    highlights = result.highlights()
    columns = _columns(transformed)
    cell_sounds = {
        sound.sound_id
        for word in transformed.words for sound in word.sounds
    } | {
        bridge.sound.sound_id
        for word in transformed.words for bridge in word.bridges
    } | {
        sound.sound_id
        for boundary in transformed.boundaries for sound in boundary.sounds
    } | {
        bridge.sound.sound_id
        for boundary in transformed.boundaries for bridge in boundary.bridges
    }
    cell_units = {
        unit for column in columns for unit in column.source_unit_ids
    }
    cell_occurrences = {
        occurrence
        for column in columns for occurrence in column.rule_occurrence_ids
    }
    cell_mergers = {
        bridge.merger_id
        for boundary in transformed.boundaries for bridge in boundary.bridges
    }
    highlight_units = {unit for group in highlights for unit in group.unit_ids}
    highlight_sounds = {sound for group in highlights for sound in group.sound_ids}

    if cell_sounds != sounds:
        raise ValueError("transformed cells do not close over result sounds")
    if not cell_units <= units or not highlight_units <= units:
        raise ValueError("a public view names an unknown source unit")
    if not cell_occurrences <= occurrences:
        raise ValueError("transformed cells name an unknown rule occurrence")
    if not highlight_sounds <= sounds:
        raise ValueError("highlights name an unknown sound")
    if cell_mergers != mergers:
        raise ValueError("transformed cells do not close over boundary mergers")
    for kind in ("analysis_result", "source_view", "highlight_groups"):
        if result.document(kind)["schema_version"] != SCHEMA_VERSION:
            raise ValueError(f"{kind} has the wrong schema version")
    for spelling in ("source", "transformed"):
        if result.document(
            "cell_view", spelling=spelling
        )["schema_version"] != SCHEMA_VERSION:
            raise ValueError(
                f"cell_view ({spelling}) has the wrong schema version"
            )


def audit() -> AuditResult:
    reading = recitation(Riwayah.WARSH)
    reader = Phonemizer(riwayah="warsh")
    reaches: dict[str, ScalarReach] = defaultdict(ScalarReach)
    failures: list[str] = []
    verses = 0

    def audit_ref(ref: str) -> None:
        result = reader.analyse(ref)
        source = result.source()
        source_cells = result.cells(spelling="source")
        transformed = result.cells(spelling="transformed")
        _audit_facade(result, source, transformed)
        _audit_view(ref, source, source_cells, transformed, reaches, failures)

    source_ayahs: dict[int, list[int]] = defaultdict(list)
    for verse in reading.corpus.source_by_verse:
        source_ayahs[verse.surah].append(verse.ayah)
    for surah, ayahs in sorted(source_ayahs.items()):
        ayahs.sort()
        verses += len(ayahs)
        for offset in range(0, len(ayahs), 10):
            chunk = ayahs[offset:offset + 10]
            start, end = chunk[0], chunk[-1]
            ref = f"{surah}:{start}" if start == end else f"{surah}:{start}-{surah}:{end}"
            try:
                audit_ref(ref)
            except Exception:
                for ayah in chunk:
                    verse_ref = f"{surah}:{ayah}"
                    try:
                        audit_ref(verse_ref)
                    except Exception as error:
                        failures.append(
                            f"{verse_ref}: {type(error).__name__}: {error}"
                        )

    expected = Counter(
        character
        for entry in reading.corpus.entries.values()
        for character in entry.text
    )
    if not failures:
        for character, count in expected.items():
            if character == " ":
                continue
            got = reaches[character].count
            if got != count:
                failures.append(
                    f"U+{ord(character):04X} {character!r}: "
                    f"corpus count={count}, projected count={got}"
                )

    return AuditResult(
        verses=verses,
        characters=sum(reach.count for reach in reaches.values()),
        scalars=dict(reaches),
        failures=tuple(failures),
    )


def _items(values: set[str]) -> str:
    return ", ".join(sorted(values)) or "-"


def _report(result: AuditResult) -> str:
    lines = [
        f"Warsh projection audit: {result.verses} verses, "
        f"{result.characters} characters, {len(result.scalars)} scalars",
        "",
        "codepoint | glyph | Unicode name | count | route | unit | cell | tier | status",
        "--- | --- | --- | ---: | --- | --- | --- | --- | ---",
    ]
    for character, reach in sorted(result.scalars.items(), key=lambda item: ord(item[0])):
        name = unicodedata.name(character, "UNNAMED")
        glyph = "SPACE" if character == " " else character
        lines.append(
            f"U+{ord(character):04X} | {glyph} | {name} | {reach.count} | "
            f"{_items(reach.routes)} | {_items(reach.unit_kinds)} | "
            f"{_items(reach.cell_roles)} | {_items(reach.tiers)} | "
            f"{_items(reach.statuses)}"
        )
    lines.extend(("", f"Failures: {len(result.failures)}"))
    lines.extend(f"- {failure}" for failure in result.failures)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hamza", action="store_true", help="show only hamza forms")
    args = parser.parse_args()
    result = audit()
    if args.hamza:
        result = AuditResult(
            result.verses,
            result.characters,
            {
                char: reach for char, reach in result.scalars.items()
                if "HAMZA" in unicodedata.name(char, "")
            },
            result.failures,
        )
    print(_report(result))
    return bool(result.failures)


if __name__ == "__main__":
    raise SystemExit(main())
