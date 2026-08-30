"""Dynamic sites for the naql-article start selector."""
from __future__ import annotations

from ...engine.neighbourhood import Neighbourhood
from ...model.address import KhilafId
from ...model.canon import Annotation, CanonLetter, Onset

SCOPE = "article_starts"


def dynamic_sites(definitions) -> dict:
    """Resolver over every started word opening on a naql-carrying lam."""
    definition = definitions.get(KhilafId.ARTICLE_IBTIDAA)
    if definition is None:
        return {}

    def resolve(score, boundaries):
        near = Neighbourhood(score, boundaries)
        sites = []
        for index, word in enumerate(score.words):
            if not word.slots or not boundaries.started_on(index):
                continue
            first = word.slots[0]
            if first.onset is not Onset.WASL:
                continue
            following = near.raw_after(first.id)
            carried = (
                following is not None
                and following.letter is CanonLetter.LAM
                and Annotation.NAQL in following.annotations
            )
            if carried or word.location in definition.locations:
                sites.append((KhilafId.ARTICLE_IBTIDAA.value, index))
        return tuple(sites)

    return {SCOPE: resolve}


__all__ = ["SCOPE", "dynamic_sites"]
