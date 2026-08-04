"""Words, addressed by real `Location`, to one `Built` -- one index space.

Nothing here reaches into `canon/build.py`: `read`/`build` already accept a
span stretched across a sub-verse start or several verses, unchanged.
"""
from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from ..canon.build import Built
from ..engine.boundary_plan import all_join
from ..model.address import Location, Script, VariantSelection
from ..model.canon import Score
from ..model.performance import Performance

#: Exceeds the reach of any cross-word rule, in either direction:
#: `engine.neighbourhood.Neighbourhood.after` sees one slot ahead,
#: `canon/juncture.py`'s cross-word noon repair reaches a further word, and
#: `fakk_idgham` reads one word behind. Two words on each side covers all
#: three, so a chunk seam sees exactly what an unchunked build would show it.
OVERLAP_WORDS = 2


def assemble(
    recitation,
    locations: Sequence[Location],
    *,
    script: Script = Script.UTHMANI,
    selection: VariantSelection = VariantSelection(),
) -> Built:
    """One `Built` over exactly `locations`, however many verses it spans."""
    if not locations:
        raise ValueError("assemble() needs at least one word")
    words = tuple(
        (location, recitation.corpus.word(location)) for location in locations
    )
    reading = recitation.read(script, locations[0].verse, words)
    return recitation.build(reading, selection=selection)


@dataclass(frozen=True, slots=True)
class Window:
    """One piece of a chunked walk. `score`/`performance` also cover real
    context around `kept`; `offset` is where `kept` starts in `score.words`."""

    kept: tuple[Location, ...]
    offset: int
    score: Score
    performance: Performance


def windows(
    recitation,
    locations: Sequence[Location],
    *,
    chunk_words: int,
    script: Script = Script.UTHMANI,
    selection: VariantSelection = VariantSelection(),
) -> Iterator[Window]:
    """`locations`, walked in pieces of `chunk_words`, each padded with
    `OVERLAP_WORDS` of real neighbours so a rule at a seam reads correctly."""
    if chunk_words < 1:
        raise ValueError("chunk_words must be at least 1")
    total = len(locations)
    start = 0
    while start < total:
        end = min(start + chunk_words, total)
        lead = max(0, start - OVERLAP_WORDS)
        trail = min(total, end + OVERLAP_WORDS)
        built = assemble(
            recitation, locations[lead:trail], script=script, selection=selection
        )
        # Every piece's own trailing junction is EDGE regardless of position:
        # harmless, since nothing here looks past its own last word, and a
        # padding word is never kept unless it is `locations`' true end too.
        boundaries = all_join(len(built.score.words))
        performance = recitation.perform(
            built.score, boundaries, selection=selection
        )
        yield Window(
            locations[start:end], start - lead, built.score, performance
        )
        start = end


#: `Window` and `OVERLAP_WORDS` are `windows()`'s own machinery -- no caller
#: needs either name, only what `windows()` yields -- so neither is public.
__all__ = ["assemble", "windows"]
