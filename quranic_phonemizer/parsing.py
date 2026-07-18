from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .dataio import load_yaml, require_keys
from .model import (
    Harakah,
    GraphemeRole,
    Letter,
    LetterForm,
    LetterUnit,
    Location,
    OrthographicHint,
    SHADDAH,
    SmallVowel,
    SourceGrapheme,
    SourceMark,
    SourceWord,
    StopSign,
    Tanween,
)


@dataclass(slots=True)
class _LetterBuilder:
    letter: Letter
    harakah: Harakah | None = None
    tanween: Tanween | None = None
    shaddah: bool = False
    small_vowels: list[SmallVowel] | None = None
    marks: set[SourceMark] | None = None
    hints: set[OrthographicHint] | None = None

    def add_small_vowel(self, value: SmallVowel) -> None:
        if self.small_vowels is None:
            self.small_vowels = []
        self.small_vowels.append(value)

    def add_mark(self, value: SourceMark) -> None:
        if self.marks is None:
            self.marks = set()
        self.marks.add(value)

    def add_hint(self, value: OrthographicHint) -> None:
        if self.hints is None:
            self.hints = set()
        self.hints.add(value)

    def freeze(self) -> LetterUnit:
        return LetterUnit(
            LetterForm(
                letter=self.letter,
                harakah=self.harakah,
                tanween=self.tanween,
                shaddah=self.shaddah,
                small_vowels=tuple(self.small_vowels or ()),
                marks=frozenset(self.marks or ()),
                hints=frozenset(self.hints or ()),
            )
        )


class ScriptParser:
    def __init__(self, path: Path):
        data = load_yaml(path)
        require_keys(
            data,
            {
                "schema_version",
                "aliases",
                "letter_hints",
                "marks",
                "structural",
                "stop_signs",
            },
            name="script data",
        )
        if data.get("schema_version") != 1:
            raise ValueError(f"Unsupported script schema: {path}")
        self._letters = {letter.value: letter for letter in Letter}
        self._aliases = data["aliases"]
        self._harakat = {item.value: item for item in Harakah}
        self._tanween = {item.value: item for item in Tanween}
        self._small_vowels = {item.value: item for item in SmallVowel}
        self._marks = {
            source: SourceMark(value) for source, value in data["marks"].items()
        }
        self._structural = frozenset(data["structural"])
        self._letter_hints = {
            source: OrthographicHint(value)
            for source, value in data.get("letter_hints", {}).items()
        }
        self._stops = {
            source: StopSign(value) for source, value in data["stop_signs"].items()
        }

    def parse_word(
        self,
        text: str,
        location: Location,
    ) -> SourceWord:
        builders: list[_LetterBuilder] = []
        graphemes: list[SourceGrapheme] = []
        stop_sign = None

        for offset, char in enumerate(text):
            if char.isspace():
                graphemes.append(
                    SourceGrapheme(char, offset, GraphemeRole.STRUCTURAL, None)
                )
                continue
            canonical = self._aliases.get(char, char)
            letter = self._letters.get(canonical)
            if letter is not None:
                builder = _LetterBuilder(letter=letter)
                hint = self._letter_hints.get(char)
                if hint is not None:
                    builder.add_hint(hint)
                builders.append(builder)
                graphemes.append(
                    SourceGrapheme(
                        char,
                        offset,
                        GraphemeRole.BASE,
                        len(builders) - 1,
                    )
                )
                continue

            stop = self._stops.get(char)
            if stop is not None:
                stop_sign = stop
                graphemes.append(SourceGrapheme(char, offset, GraphemeRole.STOP, None))
                continue

            if not builders:
                if char not in self._structural:
                    raise ValueError(
                        f"Unknown script scalar U+{ord(char):04X} at {location}"
                    )
                graphemes.append(
                    SourceGrapheme(char, offset, GraphemeRole.STRUCTURAL, None)
                )
                continue

            current = builders[-1]
            role = GraphemeRole.MARK
            harakah = self._harakat.get(canonical)
            tanween = self._tanween.get(canonical)
            small_vowel = self._small_vowels.get(canonical)
            if harakah is not None:
                current.harakah = harakah
                current.tanween = None
            elif tanween is not None:
                current.tanween = tanween
                current.harakah = None
            elif small_vowel is not None:
                current.add_small_vowel(small_vowel)
            elif canonical == SHADDAH:
                current.shaddah = True
            elif char in self._marks:
                current.add_mark(self._marks[char])
            elif char in self._structural:
                role = GraphemeRole.STRUCTURAL
            else:
                raise ValueError(
                    f"Unknown script scalar U+{ord(char):04X} at {location}"
                )
            graphemes.append(SourceGrapheme(char, offset, role, len(builders) - 1))

        return SourceWord(
            location=location,
            text=text,
            letters=tuple(builder.freeze() for builder in builders),
            graphemes=tuple(graphemes),
            stop_sign=stop_sign,
        )
