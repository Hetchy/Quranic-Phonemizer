from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from .dataio import load_yaml, require_keys
from .model import Letter, SourceMark, SourceWord
from .parsing import ScriptParser
from .rules.context import WordState


@dataclass(frozen=True, slots=True)
class MuqattaatLexicon:
    forms: frozenset[tuple[Letter, ...]]
    names: Mapping[Letter, str]

    @classmethod
    def load(cls, path: Path) -> MuqattaatLexicon:
        data = load_yaml(path)
        require_keys(
            data,
            {"schema_version", "forms", "names"},
            name="muqattaat data",
        )
        if data.get("schema_version") != 1:
            raise ValueError(f"Unsupported muqattaat schema: {path}")
        return cls(
            forms=frozenset(
                tuple(Letter(char) for char in form) for form in data["forms"]
            ),
            names=MappingProxyType(
                {Letter(char): spelling for char, spelling in data["names"].items()}
            ),
        )

    def expand(self, word: SourceWord, script: ScriptParser) -> tuple[SourceWord, ...]:
        skeleton = tuple(letter.form.letter for letter in word.letters)
        if skeleton not in self.forms:
            return ()
        if any(
            letter.form.harakah
            or letter.form.tanween
            or letter.form.shaddah
            or letter.form.small_vowels
            or letter.form.marks - {SourceMark.MADD}
            for letter in word.letters
        ):
            return ()
        return tuple(
            script.parse_word(self.names[letter], word.location) for letter in skeleton
        )


def expand_word_states(
    sources: list[WordState],
    lexicon: MuqattaatLexicon,
    script: ScriptParser,
) -> list[WordState]:
    expanded: list[WordState] = []
    for state in sources:
        words = lexicon.expand(state.source, script)
        if not words:
            expanded.append(state)
            continue
        last = len(words) - 1
        expanded.extend(
            WordState(
                source=word,
                owner_index=state.owner_index,
                starting=state.starting and index == 0,
                stopping=state.stopping and index == last,
                expanded=True,
                allow_forward_rules=index < last,
                incoming_source=state.source if index == 0 else None,
            )
            for index, word in enumerate(words)
        )
    return expanded
