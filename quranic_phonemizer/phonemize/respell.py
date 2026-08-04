"""`r.respelling(grouping)` -- 01-contract section 6.3.

A block is the union-find closure of source and recited pairings under
`from_glyphs` and under the sounds each side owns.
"""
from __future__ import annotations

from dataclasses import dataclass

from .assemble import Assembled
from .pairing import Pairing, alignment


@dataclass(frozen=True, slots=True)
class Block:
    source: tuple[int, ...]
    recited: tuple[int, ...]


def respelling(assembled: Assembled, *, grouping: str = "cell") -> tuple[Block, ...]:
    source = alignment(assembled, text="source", grouping=grouping)
    recited = alignment(assembled, text="recited", grouping=grouping)
    parent = _closure(assembled, source, recited)
    return _blocks(source, recited, parent)


def _closure(assembled: Assembled, source: tuple[Pairing, ...],
            recited: tuple[Pairing, ...]) -> list[int]:
    """Union-find over `range(len(source) + len(recited))`; a recited index
    `r` is node `len(source) + r`."""
    parent = list(range(len(source) + len(recited)))

    def find(node: int) -> int:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    offset = len(source)
    source_of_glyph = {g: i for i, p in enumerate(source) for g in p.glyphs}
    for ri, pairing in enumerate(recited):
        for glyph in pairing.glyphs:
            for source_glyph in assembled.rendered[glyph].from_glyphs:
                si = source_of_glyph.get(source_glyph)
                if si is not None:
                    union(si, offset + ri)

    owner = {s: i for i, p in enumerate(source) for s in p.sounds}
    for ri, pairing in enumerate(recited):
        for sound in pairing.sounds:
            si = owner.get(sound)
            if si is not None:
                union(si, offset + ri)
    return [find(node) for node in range(len(parent))]


def _blocks(source, recited, parent: list[int]) -> tuple[Block, ...]:
    offset = len(source)
    members: dict[int, list[int]] = {}
    for node, root in enumerate(parent):
        members.setdefault(root, []).append(node)

    keyed = []
    for nodes in members.values():
        src = tuple(sorted(n for n in nodes if n < offset))
        rec = tuple(sorted(n - offset for n in nodes if n >= offset))
        # A block with no source pairing sorts after every real one, in its
        # own recited order -- 01-contract 6.3's one case with no source.
        key = min(src) if src else offset + min(rec)
        keyed.append((key, Block(src, rec)))
    keyed.sort(key=lambda item: item[0])
    return tuple(block for _, block in keyed)


__all__ = ["Block", "respelling"]
