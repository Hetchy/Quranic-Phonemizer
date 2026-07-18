from __future__ import annotations

from collections.abc import Iterable

from .corpus import load_corpus
from .expansion import MuqattaatLexicon, expand_word_states
from .hafs import apply_exceptions, load_exceptions
from .model import BoundaryMode, Recitation, Riwayah, WordRealization
from .parsing import ScriptParser
from .rendering import load_render_config, render_segments
from .resources import resources_for
from .rule_data import load_rule_config
from .rules import RuleContext, WordState, apply_rules


_VALID_STOP_SIGNS = frozenset(
    {
        "verse",
        "preferred_continue",
        "preferred_stop",
        "optional_stop",
        "compulsory_stop",
        "prohibited_stop",
    }
)


class PhonemeEngine:
    def __init__(self, riwayah: Riwayah = Riwayah.HAFS):
        riwayah = Riwayah(riwayah)
        resources = resources_for(riwayah)
        self._resources = resources
        self._corpus = load_corpus(resources.corpus, resources.addresses)
        self._script = ScriptParser(resources.script)
        self._rules = load_rule_config(resources.tajweed)
        self._render = load_render_config(resources.render)
        self._muqattaat = MuqattaatLexicon.load(resources.muqattaat)
        self._exceptions = load_exceptions(resources.exceptions)

    def phonemize(
        self,
        reference: str,
        *,
        stop_signs: Iterable[str] = (),
        stop_refs: Iterable[str] = (),
    ) -> Recitation:
        stop_signs = _items(stop_signs)
        stop_refs = _items(stop_refs)
        invalid = set(stop_signs) - _VALID_STOP_SIGNS
        if invalid:
            raise ValueError(
                f"Invalid stop sign types: {sorted(invalid)}. "
                f"Valid stop signs are: {sorted(_VALID_STOP_SIGNS)}"
            )

        locations = self._corpus.locations(reference)
        sources = [
            self._script.parse_word(self._corpus.word(location), location)
            for location in locations
        ]
        source_states = self._source_states(
            sources,
            stop_signs=frozenset(stop_signs),
            stop_refs=frozenset(stop_refs),
        )
        boundaries = tuple(
            BoundaryMode.EDGE
            if index == len(source_states) - 1
            else BoundaryMode.STOP
            if state.stopping
            else BoundaryMode.JOIN
            for index, state in enumerate(source_states)
        )
        states = expand_word_states(source_states, self._muqattaat, self._script)
        context = RuleContext(states)
        apply_rules(context, self._rules)
        apply_exceptions(context, self._exceptions)

        owner_segments = [[] for _ in sources]
        for word in context.words:
            for letter in word.letters:
                owner_segments[word.owner_index].extend(letter.segments)

        return Recitation(
            riwayah=self._resources.riwayah,
            ref=reference,
            stop_signs=stop_signs,
            stop_refs=stop_refs,
            words=tuple(
                WordRealization(
                    source=source,
                    segments=tuple(segments),
                    phonemes=render_segments(segments, self._render),
                    boundary_after=boundary,
                )
                for source, segments, boundary in zip(
                    sources,
                    owner_segments,
                    boundaries,
                )
            ),
        )

    @staticmethod
    def _source_states(
        sources,
        *,
        stop_signs: frozenset[str],
        stop_refs: frozenset[str],
    ) -> list[WordState]:
        last = len(sources) - 1
        states = [
            WordState(
                source=source,
                owner_index=index,
                starting=index == 0,
                stopping=index == last,
            )
            for index, source in enumerate(sources)
        ]

        for index, state in enumerate(states[:-1]):
            verse_end = (
                sources[index + 1].location.ayah != state.source.location.ayah
                or sources[index + 1].location.surah != state.source.location.surah
            )
            stop_for_sign = (
                state.source.stop_sign is not None
                and state.source.stop_sign.value in stop_signs
            )
            stop_for_verse = "verse" in stop_signs and verse_end
            stop_for_ref = str(state.source.location) in stop_refs
            if stop_for_sign or stop_for_verse or stop_for_ref:
                state.stopping = True
                states[index + 1].starting = True
        return states


def _items(values: Iterable[str]) -> tuple[str, ...]:
    if isinstance(values, str):
        return (values,)
    return tuple(values)
