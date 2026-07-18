from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .model import Recitation, WordRealization


@dataclass(frozen=True, slots=True)
class PhonemizeResult:
    recitation: Recitation

    @property
    def ref(self) -> str:
        return self.recitation.ref

    @property
    def stop_signs(self) -> list[str]:
        return list(self.recitation.stop_signs)

    @property
    def stop_refs(self) -> list[str]:
        return list(self.recitation.stop_refs)

    def phonemes_list(
        self,
        split: Literal["word", "verse", "both"] = "word",
    ) -> list[list[str]] | list[list[list[str]]]:
        if split == "word":
            return [list(word.phonemes) for word in self.recitation.words]
        verses = _group_verses(self.recitation.words)
        if split == "verse":
            return [
                [phoneme for word in verse for phoneme in word.phonemes]
                for verse in verses
            ]
        if split == "both":
            return [[list(word.phonemes) for word in verse] for verse in verses]
        raise ValueError("split must be 'word', 'verse', or 'both'")

    def phonemes_str(
        self,
        phoneme_sep: str = "",
        word_sep: str = " ",
        verse_sep: str = "\n",
    ) -> str:
        parts: list[str] = []
        previous = None
        for word in self.recitation.words:
            key = (word.location.surah, word.location.ayah)
            if previous is not None:
                parts.append(verse_sep if key != previous else word_sep)
            parts.append(phoneme_sep.join(word.phonemes))
            previous = key
        return "".join(parts)


def _group_verses(
    words: tuple[WordRealization, ...],
) -> list[list[WordRealization]]:
    verses: list[list[WordRealization]] = []
    for word in words:
        key = (word.location.surah, word.location.ayah)
        if (
            not verses
            or (
                verses[-1][0].location.surah,
                verses[-1][0].location.ayah,
            )
            != key
        ):
            verses.append([])
        verses[-1].append(word)
    return verses
