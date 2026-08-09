from __future__ import annotations

import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from quranic_phonemizer.api import alphabet as load_alphabet
from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import (
    Location,
    Riwayah,
    Script,
    VariantSelection,
    VerseRef,
)
from quranic_phonemizer.model.inscription import Attests, Decorates, Evidences
from quranic_phonemizer.render.anchored import anchored, graphemes_by_id
from quranic_phonemizer.render.recite import phonemes_by_word

from .boundary import UnreachableWasl, plan_for, reaches_past
from .site import Site

ROOT = Path(__file__).resolve().parents[2]


class RulesPending(NotImplementedError):
    """Which unit a rule is read against is settled by the projection."""


@lru_cache(maxsize=None)
def _recitation(riwayah: Riwayah):
    return recitation(riwayah)


@lru_cache(maxsize=None)
def _alphabet():
    return load_alphabet()


@lru_cache(maxsize=None)
def _editable(riwayah: Riwayah, script: Script) -> dict:
    base = ROOT / "corpus_sources" / "riwayat" / riwayah.value / "scripts"
    raw = json.loads(
        (base / script.value / "quran.json").read_text(encoding="utf-8")
    )
    out: dict = defaultdict(list)
    for key, record in raw.items():
        surah, ayah, word = (int(part) for part in key.split(":"))
        out[(surah, ayah)].append(
            (Location(surah, ayah, word), record["text"])
        )
    return {
        key: tuple(sorted(words, key=lambda pair: pair[0].word))
        for key, words in out.items()
    }


def _words(recitation_, riwayah: Riwayah, script: Script, verse):
    if script is Script.UTHMANI:
        return recitation_.words(verse)
    return _editable(riwayah, script)[(verse.surah, verse.ayah)]


def _after(recitation_, verse: VerseRef) -> VerseRef | None:
    """The verse a continuing reading runs into, across a surah if it must."""
    surahs = recitation_.corpus.surah_info
    if verse.ayah < len(surahs[str(verse.surah)]):
        return VerseRef(verse.surah, verse.ayah + 1)
    if str(verse.surah + 1) in surahs:
        return VerseRef(verse.surah + 1, 1)
    return None


def _through(recitation_, riwayah, script, verse):
    """This verse's words and the next one's, read as a single stretch.

    A reading that carries on past a verse end is not two readings: the rule
    that crosses the seam needs both sides in one score.
    """
    following = _after(recitation_, verse)
    if following is None:
        raise UnreachableWasl(
            f"{verse.surah}:{verse.ayah} is the last verse of the corpus, "
            f"so it has nothing to join into"
        )
    return (_words(recitation_, riwayah, script, verse)
            + _words(recitation_, riwayah, script, following))


def _written_by(inscription) -> tuple[tuple, ...]:
    """Every (grapheme, slot) pair the inscription records, whatever the fact.

    Which fact a grapheme wrote does not matter to a caller asking which
    rules name the letter it can see on the page.
    """
    return tuple(
        (spelling.grapheme, _anchor(spelling))
        for spelling in inscription.spellings
        if isinstance(spelling, (Evidences, Decorates, Attests))
    )


def _anchor(spelling):
    return spelling.anchor if isinstance(spelling, Attests) else spelling.slot


class Reading:
    """What one call produced, addressed by the word numbers of the verse."""

    def __init__(self, riwayah, script, built, performance, words):
        self.riwayah = riwayah
        self.script = script
        self.score = built.score
        self.performance = performance
        self._text = dict(enumerate((t for _, t in words), start=1))
        self._chars = graphemes_by_id(built.inscription)
        self._written_by = _written_by(built.inscription)
        self._view = anchored(performance, built.inscription, _alphabet())
        self._phonemes = phonemes_by_word(
            performance, built.score, _alphabet()
        )

    def _slots(self, word: int) -> frozenset:
        return frozenset(slot.id for slot in self.score.words[word - 1].slots)

    def text(self, word: int) -> str:
        return self._text[word]

    def phonemes(self, word: int) -> str:
        return "".join(self._phonemes[word - 1])

    def sounds(self, word: int) -> tuple[str, ...]:
        return tuple(self._phonemes[word - 1])

    def silent(self, word: int) -> frozenset[str]:
        """The characters this reading writes and does not say."""
        slots = self._slots(word)
        return frozenset(
            self._chars[grapheme].char
            for letter in self._view.silent
            if letter.slot in slots
            for grapheme in letter.graphemes
        )

    def source_of(self, rule: str):
        raise RulesPending(rule)

    def host_of(self, rule: str):
        raise RulesPending(rule)

    def rules_on_char(self, word: int, char: str) -> frozenset[str]:
        """Every rule naming a slot this character writes, in this word.

        Read off the occurrences, so a rule that classifies and produces
        nothing is visible: `هَـٰٓؤُلَآءِ` holds two madds of two names.
        """
        wanted = self._slots(word)
        slots = {
            slot
            for grapheme, slot in self._written_by
            if slot in wanted and self._chars[grapheme].char == char
        }
        return frozenset(
            occurrence.rule.value
            for occurrence in self.performance.occurrences
            if slots & set(occurrence.parts.slots)
        )

    def rules_on_sound(self, word: int, token: str):
        raise RulesPending(token)

    def pick(self, **per_riwayah):
        """An expectation that differs between riwayat."""
        return per_riwayah[self.riwayah]


def reading(
    site: Site,
    riwayah: str = "hafs",
    script: Script = Script.UTHMANI,
    selection: VariantSelection = VariantSelection(),
    **boundary,
) -> Reading:
    """Build and perform one site under one riwayah and one boundary plan."""
    name = Riwayah(riwayah)
    recitation_ = _recitation(name)
    address = site.address(riwayah)
    words = _words(recitation_, name, script, address.verse)
    if reaches_past(len(words), **boundary):
        words = _through(recitation_, name, script, address.verse)
    built = recitation_.build(
        recitation_.read(script, address.verse, words), selection=selection
    )
    plan = plan_for(len(words), **boundary)
    return Reading(
        riwayah, script, built,
        recitation_.perform(built.score, plan, selection=selection), words,
    )
