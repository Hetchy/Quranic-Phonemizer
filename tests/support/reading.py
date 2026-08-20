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
from quranic_phonemizer.model.canon import Rule
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.phonemize import edges as ed
from quranic_phonemizer.phonemize import nodes as nd
from quranic_phonemizer.phonemize.assemble import assemble
from quranic_phonemizer.phonemize.document import phonemes as assembled_phonemes
from quranic_phonemizer.phonemize.pairing import alignment
from quranic_phonemizer.phonemize.legacy_views import (
    anchored,
    graphemes_by_id,
    phonemes_by_word,
)
from quranic_phonemizer.phonemize.session import Session as PhonemizeSession

from .boundary import UnreachableWasl, plan_for, reaches_past
from .site import Site

ROOT = Path(__file__).resolve().parents[2]


@lru_cache(maxsize=None)
def _recitation(riwayah: Riwayah):
    return recitation(riwayah)


@lru_cache(maxsize=None)
def _alphabet():
    return load_alphabet()


def loaded(riwayah: str = "hafs"):
    """The one copy of a riwayah every case in this suite reads from."""
    return _recitation(Riwayah(riwayah))


@lru_cache(maxsize=None)
def _pen(riwayah: Riwayah, script: Script):
    return pen_for(_recitation(riwayah).inventory(script))


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


def _word_of_sound(assembled) -> dict[int, int]:
    """A sound's word is its primary origin's, mirroring `document._sound_words`."""
    return {
        a.sound: assembled.units[a.unit].word
        for a in assembled.attributions
        if isinstance(a, ed.Hosts)
    }


class Reading:
    """What one call produced, addressed by the word numbers of the verse."""

    def __init__(
        self, riwayah, script, built, performance, words, assembled,
        *, uses_extra_phonemes: bool,
    ):
        self.riwayah = riwayah
        self.script = script
        self.score = built.score
        self.performance = performance
        self._text = dict(enumerate((t for _, t in words), start=1))
        self._chars = graphemes_by_id(built.inscription)
        self._view = anchored(performance, built.inscription, _alphabet())
        self._phonemes = phonemes_by_word(
            performance, built.score, _alphabet()
        )
        self._assembled = assembled
        self._uses_extra_phonemes = uses_extra_phonemes
        self._assembled_phonemes = (
            assembled_phonemes(assembled, by="word") if uses_extra_phonemes else None
        )
        self._sound_word = _word_of_sound(assembled)

    def _slots(self, word: int) -> frozenset:
        return frozenset(slot.id for slot in self.score.words[word - 1].slots)

    def text(self, word: int) -> str:
        return self._text[word]

    def phonemes(self, word: int) -> str:
        if self._uses_extra_phonemes:
            return "".join(self._assembled_phonemes[word - 1])
        return "".join(self._phonemes[word - 1])

    def sounds(self, word: int) -> tuple[str, ...]:
        if self._uses_extra_phonemes:
            return self._assembled_phonemes[word - 1]
        return tuple(self._phonemes[word - 1])

    def silent(self, word: int) -> frozenset[str]:
        """The characters whose slot this reading silences."""
        slots = self._slots(word)
        return frozenset(
            self._chars[grapheme].char
            for letter in self._view.silent
            if letter.slot in slots
            for grapheme in letter.graphemes
        )

    def unsaid(self, word: int) -> frozenset[str]:
        """The characters this reading writes and does not say."""
        pairings = alignment(self._assembled, text="source", grouping="glyph")
        return frozenset(
            self._assembled.glyphs[glyph].char
            for pairing in pairings
            for glyph in pairing.silent
            if self._assembled.glyphs[glyph].word == word - 1
        )

    def _char_of_unit(self, unit: int) -> str:
        """The character supplying `unit`'s letter, or failing that any
        glyph that spells it -- a tanween's noon has no `LETTER` fact."""
        by_fact, any_glyph = None, None
        for spelling in self._assembled.spellings:
            if getattr(spelling, "unit", None) != unit:
                continue
            any_glyph = any_glyph if any_glyph is not None else spelling.glyph
            if isinstance(spelling, ed.Supplies) and spelling.fact is ed.Fact.LETTER:
                by_fact = spelling.glyph
                break
        glyph = by_fact if by_fact is not None else any_glyph
        if glyph is None:
            raise LookupError(f"unit {unit} has no glyph in this reading")
        return self._assembled.glyphs[glyph].char

    def _instances_of(self, rule: str) -> tuple[nd.RuleInstance, ...]:
        wanted = Rule(rule)
        instances = tuple(
            ri for ri in self._assembled.rules if ri.rule is wanted
        )
        if not instances:
            raise LookupError(f"{rule!r} does not fire in this reading")
        return instances

    def source_of(self, rule: str) -> str:
        """The character supplying `rule`'s source unit."""
        return self._char_of_unit(self._instances_of(rule)[0].source)

    def host_of(self, rule: str) -> str | None:
        """The character supplying `rule`'s host unit, or `None` where the
        rule acted on its own unit alone."""
        host = self._instances_of(rule)[0].host
        return None if host is None else self._char_of_unit(host)

    def rules_on_char(self, word: int, char: str) -> frozenset[str]:
        """Every rule read against `char` (in `word`).

        A rule anchored on the glyph rather than on a unit counts too: a
        letter the reading never says has no unit to reach it by.
        """
        idx = word - 1
        glyphs = {
            i for i, g in enumerate(self._assembled.glyphs)
            if g.word == idx and g.char == char
        }
        units = {
            spelling.unit for spelling in self._assembled.spellings
            if getattr(spelling, "unit", None) is not None
            and getattr(spelling, "glyph", None) in glyphs
        }
        reached = {
            i for i, ri in enumerate(self._assembled.rules)
            if ri.source in units or ri.host in units
        }
        reached |= {
            rule for glyph, rule in self._assembled.orthographic_silence.items()
            if glyph in glyphs
        }
        return frozenset(self._assembled.rules[i].rule.value for i in reached)

    def rules_on_sound(self, word: int, token: str) -> frozenset[str]:
        """Every rule reaching a sound `token` produced, in `word`."""
        idx = word - 1
        sounds = {
            i for i, s in enumerate(self._assembled.sounds)
            if s.token == token and self._sound_word.get(i) == idx
        }
        by: set[int] = set()
        for a in self._assembled.attributions:
            if (
                isinstance(a, (ed.Hosts, ed.MergedInto))
                and a.sound in sounds and a.by is not None
            ):
                by.add(a.by)
        for m in self._assembled.modifiers:
            if m.sound in sounds:
                by.add(m.by)
        return frozenset(self._assembled.rules[i].rule.value for i in by)

    def pick(self, **per_riwayah):
        """An expectation that differs between riwayat."""
        return per_riwayah[self.riwayah]


def _assembled_for(name, script, built, plan, performance, words, extra):
    session = PhonemizeSession(
        locations=tuple(location for location, _ in words),
        score=built.score, inscription=built.inscription,
        boundaries=plan, performance=performance,
    )
    return assemble(
        session, _pen(name, script), _alphabet(), extra_phonemes=extra
    )


def reading(
    site: Site,
    riwayah: str = "hafs",
    script: Script = Script.UTHMANI,
    selection: VariantSelection = VariantSelection(),
    extra_phonemes: tuple[str, ...] | frozenset[str] | None = None,
    **boundary,
) -> Reading:
    """Build and perform one site under one riwayah and one boundary plan.

    `extra_phonemes` left unnamed keeps `phonemes`/`sounds` reading the
    legacy default; naming it, even as `()`, gates all four toggles.
    """
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
    performance = recitation_.perform(built.score, plan, selection=selection)
    assembled = _assembled_for(
        name, script, built, plan, performance, words,
        frozenset() if extra_phonemes is None else frozenset(extra_phonemes),
    )
    return Reading(
        riwayah, script, built, performance, words, assembled,
        uses_extra_phonemes=extra_phonemes is not None,
    )
