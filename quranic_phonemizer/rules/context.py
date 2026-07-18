from __future__ import annotations

from dataclasses import dataclass, field

from ..model import Harakah, LetterForm, Segment, SourceWord, Tanween, Vowel


@dataclass(slots=True)
class LetterState:
    form: LetterForm
    word_index: int
    letter_index: int
    harakah: Harakah | None = None
    tanween: Tanween | None = None
    shaddah: bool = False
    force_long_vowel: bool = False
    resolved: bool = False
    segments: list[Segment] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.harakah = self.form.harakah
        self.tanween = self.form.tanween
        self.shaddah = self.form.shaddah


@dataclass(slots=True)
class WordState:
    source: SourceWord
    owner_index: int
    starting: bool
    stopping: bool
    expanded: bool = False
    allow_forward_rules: bool = True
    incoming_source: SourceWord | None = None
    letters: list[LetterState] = field(default_factory=list)

    @property
    def skeleton(self) -> tuple:
        return tuple(letter.form.letter for letter in self.letters)


class RuleContext:
    def __init__(self, words: list[WordState]):
        self.words = words
        self._incoming_proxies: dict[int, list[LetterState]] = {}
        for word_index, word in enumerate(words):
            word.letters = [
                LetterState(
                    source.form,
                    word_index,
                    letter_index,
                )
                for letter_index, source in enumerate(word.source.letters)
            ]
            if word.incoming_source is not None:
                # A preceding word sees the compact source, not its expanded spelling.
                self._incoming_proxies[word_index] = [
                    LetterState(source.form, word_index, letter_index)
                    for letter_index, source in enumerate(word.incoming_source.letters)
                ]

    def word(self, letter: LetterState) -> WordState:
        return self.words[letter.word_index]

    def previous_letter(
        self, letter: LetterState, count: int = 1
    ) -> LetterState | None:
        index = letter.letter_index - count
        if index >= 0:
            return self.words[letter.word_index].letters[index]
        if letter.word_index == 0:
            return None
        previous = self.words[letter.word_index - 1].letters
        index = len(previous) + index
        return previous[index] if 0 <= index < len(previous) else None

    def next_letter(self, letter: LetterState, count: int = 1) -> LetterState | None:
        word = self.words[letter.word_index]
        index = letter.letter_index + count
        if index < len(word.letters):
            return word.letters[index]
        if not word.allow_forward_rules or letter.word_index + 1 >= len(self.words):
            return None
        following_word_index = letter.word_index + 1
        following = self._incoming_proxies.get(
            following_word_index,
            self.words[following_word_index].letters,
        )
        index -= len(word.letters)
        return following[index] if index < len(following) else None

    def previous_segment_slot(
        self,
        letter: LetterState,
    ) -> tuple[LetterState, int] | None:
        word = self.words[letter.word_index]
        for index in range(letter.letter_index - 1, -1, -1):
            candidate = word.letters[index]
            if candidate.segments:
                return candidate, len(candidate.segments) - 1
        if letter.word_index == 0:
            return None
        for candidate in reversed(self.words[letter.word_index - 1].letters):
            if candidate.segments:
                return candidate, len(candidate.segments) - 1
        return None

    def previous_segment(self, letter: LetterState) -> Segment | None:
        slot = self.previous_segment_slot(letter)
        return slot[0].segments[slot[1]] if slot else None

    def shorten_previous_vowel(self, letter: LetterState) -> bool:
        slot = self.previous_segment_slot(letter)
        if slot is None:
            return False
        owner, index = slot
        segment = owner.segments[index]
        if not isinstance(segment, Vowel) or not segment.long:
            return False
        owner.segments[index] = Vowel(
            quality=segment.quality,
            long=False,
            emphatic=segment.emphatic,
        )
        return True
