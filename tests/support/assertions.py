"""One assertion engine for every semantic case shape."""
from __future__ import annotations

from dataclasses import asdict

from quranic_phonemizer.analysis.ids import CharacterId
from quranic_phonemizer.analysis.source_dtos import LiteralSilence

from .case import CaseRun, RuleExpectation, resolve
from .reading import reading
from .selectors import resolve_glyph, resolve_sound


def _known_tokens(alphabet) -> frozenset[str]:
    tokens: set[str] = set()
    for entry in alphabet.consonants.values():
        forms = {value for value in asdict(entry).values() if value}
        tokens.update(forms)
        tokens.update(token * 2 for token in forms if token not in {"ŋ", "ŋˤ", "ñ", "m̃", "w̃", "j̃"})
    for entry in alphabet.vowels.values():
        forms = {value for value in asdict(entry).values() if value}
        tokens.update(forms)
        tokens.update(token + ":" for token in forms)
    tokens.update(alphabet.releases.values())
    tokens.update(token * 2 for token in alphabet.releases.values())
    return frozenset(tokens)


def parse_phonemes(value: str, alphabet) -> tuple[str, ...]:
    if not value or value != value.strip() or "  " in value:
        raise ValueError(f"phonemes need one ASCII space between tokens: {value!r}")
    tokens = tuple(value.split(" "))
    unknown = tuple(token for token in tokens if token not in _known_tokens(alphabet))
    if unknown:
        raise ValueError(f"unknown phoneme token(s) {unknown} in {value!r}")
    return tokens


def _expected_words(value, words: tuple[int, ...], alphabet):
    if isinstance(value, str):
        if len(words) != 1:
            raise ValueError("multiword cases need one phoneme string per focused word")
        return (parse_phonemes(value, alphabet),)
    if len(value) != len(words):
        raise ValueError(
            f"{len(words)} focused words need {len(words)} phoneme strings, got {len(value)}"
        )
    return tuple(parse_phonemes(word, alphabet) for word in value)


RuleKey = tuple[str, int | str]


def _columns(result):
    columns = [column for word in result._cells.words for column in word.columns]
    columns.extend(
        column for boundary in result._cells.boundaries for column in boundary.columns
    )
    return tuple(columns)


def _rules_for_glyph(result, glyph: int) -> frozenset[RuleKey]:
    character = CharacterId(glyph)
    columns = tuple(
        column for column in _columns(result)
        if character in column.source_character_ids
    )
    if len(columns) != 1:
        raise LookupError(
            f"source character {glyph} reaches {len(columns)} transformed columns"
        )
    column = columns[0]
    reached: set[RuleKey] = {
        ("occurrence", occurrence.value)
        for occurrence in column.rule_occurrence_ids
    }
    if isinstance(column.silence, LiteralSilence):
        reached.add(("literal", column.silence.value))
    return frozenset(reached)


def _rules_for_sound(result, sound: int) -> frozenset[RuleKey]:
    return frozenset(
        ("occurrence", occurrence.value)
        for occurrence in result._bundle.sounds[sound].rule_occurrence_ids
    )


def _names(result, rules: frozenset[RuleKey]) -> frozenset[str]:
    return frozenset(
        value if kind == "literal"
        else result._bundle.rule_occurrences[value].rule_id.value
        for kind, value in rules
    )


def _assert_rule_map(actual, expected: dict[str, RuleExpectation], *, absent: bool):
    for selector, wanted in expected.items():
        indices = actual(selector)
        names = _names(actual.result, indices)
        if absent:
            overlap = names & wanted.rules
            assert not overlap, f"{selector}: unexpectedly has {sorted(overlap)}"
        else:
            missing = wanted.rules - names
            assert not missing, (
                f"{selector}: missing rules {sorted(missing)}; got {sorted(names)}"
            )


class _Targets:
    def __init__(self, result, words: tuple[int, ...], *, sound: bool):
        self.result = result
        self.words = words
        self.sound = sound
        self.selected: dict[str, int] = {}

    def __call__(self, selector: str) -> frozenset[RuleKey]:
        if self.sound:
            target = resolve_sound(
                self.result._assembled,
                self.result._sound_word,
                self.words,
                selector,
            )
            rules = _rules_for_sound(self.result, target)
        else:
            target = resolve_glyph(self.result._assembled, self.words, selector)
            rules = _rules_for_glyph(self.result, target)
        self.selected[selector] = target
        return rules


def _assert_connected(char_targets: _Targets, sound_targets: _Targets, char_map, sound_map):
    names = {
        name
        for expected in (*char_map.values(), *sound_map.values())
        for name in expected.rules
    }
    for name in names:
        chars = [
            selector for selector, expected in char_map.items()
            if name in expected.rules
        ]
        sounds = [
            selector for selector, expected in sound_map.items()
            if name in expected.rules
        ]
        if not chars or not sounds:
            continue
        pairs = (
            list(zip(chars, sounds, strict=True))
            if len(chars) == len(sounds)
            else [(char, sound) for char in chars for sound in sounds]
        )
        connected_pairs: set[tuple[str, str]] = set()
        for char_selector, sound_selector in pairs:
            char_rule_indices = _rules_for_glyph(
                char_targets.result, char_targets.selected[char_selector]
            )
            sound_rule_indices = _rules_for_sound(
                sound_targets.result, sound_targets.selected[sound_selector]
            )
            connected = {
                index for index in char_rule_indices & sound_rule_indices
                if _names(char_targets.result, frozenset((index,))) == {name}
            }
            if connected:
                connected_pairs.add((char_selector, sound_selector))
            elif len(chars) == len(sounds):
                raise AssertionError(
                    f"{name}: ordered pair {char_selector} -> {sound_selector} "
                    "matched different occurrences"
                )
        assert set(chars) == {char for char, _ in connected_pairs}, (
            f"{name}: some source targets do not reach a declared sound"
        )
        assert set(sounds) == {sound for _, sound in connected_pairs}, (
            f"{name}: some sound targets are not reached by a declared source"
        )


def assert_case(run: CaseRun) -> None:
    if run is None:
        return
    address = run.site.address(run.riwayah)
    words = address.words
    expect = run.expect
    result = reading(
        run.site,
        run.riwayah,
        run.script,
        selection=expect.selection,
        extra_phonemes=expect.extra_phonemes,
        **expect.read.kwargs(words),
    )
    from quranic_phonemizer.api import alphabet

    wanted_phonemes = _expected_words(
        resolve(expect.phonemes, run.riwayah, run.script), words, alphabet()
    )
    actual_phonemes = tuple(result.sounds(word) for word in words)
    assert actual_phonemes == wanted_phonemes

    all_rules = resolve(expect.all_rules, run.riwayah, run.script)
    if all_rules is not None:
        focused = {word - 1 for word in words}
        actual = frozenset(
            occurrence.rule_id.value
            for occurrence in result._bundle.rule_occurrences
            if focused & {word.value for word in occurrence.word_ids}
        )
        assert actual == all_rules.rules

    char_map = resolve(expect.char_rules, run.riwayah, run.script)
    sound_map = resolve(expect.sound_rules, run.riwayah, run.script)
    chars = _Targets(result, words, sound=False)
    sounds = _Targets(result, words, sound=True)
    _assert_rule_map(chars, char_map, absent=False)
    _assert_rule_map(sounds, sound_map, absent=False)
    _assert_rule_map(
        chars, resolve(expect.absent_char_rules, run.riwayah, run.script), absent=True
    )
    _assert_rule_map(
        sounds, resolve(expect.absent_sound_rules, run.riwayah, run.script), absent=True
    )
    _assert_connected(chars, sounds, char_map, sound_map)

    for selector in resolve(expect.silent, run.riwayah, run.script):
        glyph = resolve_glyph(result._assembled, words, selector)
        assert glyph in {
            index for pairing in __import__(
                "quranic_phonemizer.phonemize.pairing", fromlist=["alignment"]
            ).alignment(result._assembled, text="source", grouping="glyph")
            for index in pairing.silent
        }
    for selector in resolve(expect.said, run.riwayah, run.script):
        glyph = resolve_glyph(result._assembled, words, selector)
        assert glyph not in {
            index for pairing in __import__(
                "quranic_phonemizer.phonemize.pairing", fromlist=["alignment"]
            ).alignment(result._assembled, text="source", grouping="glyph")
            for index in pairing.silent
        }
