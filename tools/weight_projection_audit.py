"""Audit weight attribution with continued/paused boundaries and both fatha modes.

Enforce complete raa/lam/long-A labels without labels on short-A carriers.
"""
from __future__ import annotations

import argparse
from collections import defaultdict

from quranic_phonemizer import Phonemizer
from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Riwayah, VerseRef


def _public_verse(package, verse: VerseRef) -> str:
    first = package.corpus.words(verse)[0][0]
    public = (
        package.corpus.public_ref(first)
        if hasattr(package.corpus, "public_ref")
        else str(first)
    )
    return ":".join(public.split(":")[:2])


def _range_ref(package, verses: list[VerseRef]) -> str:
    start = _public_verse(package, verses[0])
    end = _public_verse(package, verses[-1])
    return start if start == end else f"{start}-{end}"


def _stop_refs(package, verses: list[VerseRef]) -> tuple[str, ...]:
    return tuple(
        package.corpus.public_ref(location)
        if hasattr(package.corpus, "public_ref") else str(location)
        for verse in verses
        for location, _ in package.corpus.words(verse)
    )


def _project_chunk(package, reader, riwayah, rendering, verses):
    ref = _range_ref(package, verses)
    stops = _stop_refs(package, verses)
    projections = words = 0
    try:
        for state, stop_refs in (("joined", ()), ("all-paused", stops)):
            result = reader.analyse(ref, stop_refs=stop_refs)
            view = result.cells(spelling="transformed")
            projections += 1
            words += len(view.words)
    except Exception as error:
        if len(verses) > 1:
            middle = len(verses) // 2
            left = _project_chunk(
                package, reader, riwayah, rendering, verses[:middle]
            )
            right = _project_chunk(
                package, reader, riwayah, rendering, verses[middle:]
            )
            return left[0] + right[0], left[1] + right[1]
        raise RuntimeError(
            f"{riwayah.value} {rendering} {state} {ref}: "
            f"{type(error).__name__}: {error}"
        ) from error
    return projections, words


def audit(
    riwayah: Riwayah, chunk_size: int, surah_from: int, surah_to: int,
) -> tuple[int, int]:
    package = recitation(riwayah)
    by_surah: dict[int, list[VerseRef]] = defaultdict(list)
    verses = (
        package.corpus.source_by_verse
        if hasattr(package.corpus, "source_by_verse")
        else (
            VerseRef(int(surah), ayah)
            for surah, counts in package.corpus.surah_info.items()
            for ayah in range(1, len(counts) + 1)
        )
    )
    for verse in verses:
        if package.corpus.words(verse):
            by_surah[verse.surah].append(verse)
    readers = (
        ("plain", Phonemizer(riwayah=riwayah.value)),
        (
            "emphatic-fatha",
            Phonemizer(
                riwayah=riwayah.value,
                extra_phonemes=("emphatic_fatha",),
            ),
        ),
    )
    projections = words = 0
    for surah, verses in sorted(by_surah.items()):
        if not surah_from <= surah <= surah_to:
            continue
        verses.sort(key=lambda verse: verse.ayah)
        surah_words = 0
        for offset in range(0, len(verses), chunk_size):
            chunk = verses[offset:offset + chunk_size]
            for rendering, reader in readers:
                checked, projected = _project_chunk(
                    package, reader, riwayah, rendering, chunk
                )
                projections += checked
                words += projected
                surah_words += projected
        print(
            f"{riwayah.value:5} {surah:3} "
            f"{surah_words:7} projected word-states clean",
            flush=True,
        )
    return projections, words


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--riwayah", choices=("hafs", "warsh", "all"), default="all"
    )
    parser.add_argument("--chunk", type=int, default=10)
    parser.add_argument("--surah-from", type=int, default=1)
    parser.add_argument("--surah-to", type=int, default=114)
    args = parser.parse_args()
    names = (
        (Riwayah.HAFS, Riwayah.WARSH)
        if args.riwayah == "all"
        else ({"hafs": Riwayah.HAFS, "warsh": Riwayah.WARSH}[args.riwayah],)
    )
    projections = words = 0
    for name in names:
        checked, projected = audit(
            name, args.chunk, args.surah_from, args.surah_to
        )
        projections += checked
        words += projected
    print(
        f"{projections} projections and {words} projected word-states clean; "
        "joined/all-paused x plain/emphatic-fatha",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
