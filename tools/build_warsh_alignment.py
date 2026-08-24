"""Build the reviewed King Fahd Warsh source/public word alignment.

Run: python tools/build_warsh_alignment.py
"""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "corpus_sources" / "hafs" / "scripts" / "uthmani" / "quran.json"
SOURCE = ROOT / "corpus_sources" / "warsh" / "scripts" / "king-fahd" / "quran.json"
OUTPUT = (
    ROOT
    / "quranic_phonemizer"
    / "data"
    / "riwayat"
    / "warsh"
    / "corpus"
    / "alignment.jsonl.gz"
)
ARTIFACT = "king-fahd-warsh-v2"


# The only word-cardinality differences in the two monotonic surah streams.
# Verse-boundary changes need no offset table: every generated row stores both
# exact references, and the validation below preserves every source edge.
EDITS = (
    (("1:1:1", "1:1:2", "1:1:3", "1:1:4"), ()),
    (("15:7:1", "15:7:2"), ("15:7:1",)),
    (("27:20:4", "27:20:5"), ("27:20:4",)),
    (("36:22:1", "36:22:2"), ("36:21:1",)),
    (("40:26:13", "40:26:14"), ("40:26:13",)),
    (("57:24:10",), ()),
    (("72:16:1",), ("72:16:1", "72:16:2")),
)


def _key(value: str) -> tuple[int, int, int]:
    return tuple(int(part) for part in value.split(":"))  # type: ignore[return-value]


def _load(path: Path) -> dict[str, dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def _by_surah(data: dict[str, dict]) -> dict[int, list[str]]:
    out = {surah: [] for surah in range(1, 115)}
    for ref in sorted(data, key=_key):
        out[_key(ref)[0]].append(ref)
    return out


def _edge(ref: str, positions: dict[tuple[int, int], tuple[int, int]]) -> str:
    surah, ayah, word = _key(ref)
    first, last = positions[(surah, ayah)]
    if word == first == last:
        return "both"
    if word == first:
        return "start"
    if word == last:
        return "end"
    return "inside"


def _rows(canonical: dict[str, dict], source: dict[str, dict]) -> list[dict]:
    canon = _by_surah(canonical)
    selected = _by_surah(source)
    edits = {canonical[0]: (canonical, source) for canonical, source in EDITS}
    source_positions: dict[tuple[int, int], tuple[int, int]] = {}
    for ref in source:
        surah, ayah, word = _key(ref)
        low, high = source_positions.get((surah, ayah), (word, word))
        source_positions[(surah, ayah)] = min(low, word), max(high, word)
    ordinal = {ref: index for index, ref in enumerate(sorted(source, key=_key), 1)}

    rows: list[dict] = []
    used_source: list[str] = []
    used_canonical: list[str] = []
    for surah in range(1, 115):
        i = j = 0
        while i < len(canon[surah]):
            canonical_ref = canon[surah][i]
            edit = edits.get(canonical_ref)
            if edit is None:
                if j >= len(selected[surah]):
                    raise ValueError(f"surah {surah}: source ended at {canonical_ref}")
                canonical_refs = (canonical_ref,)
                source_refs = (selected[surah][j],)
            else:
                canonical_refs, source_refs = edit
                actual = tuple(selected[surah][j : j + len(source_refs)])
                if actual != source_refs:
                    raise ValueError(
                        f"{canonical_ref}: expected source {source_refs}, found {actual}"
                    )
            rows.append(
                {
                    "canonical": list(canonical_refs),
                    "source": [
                        {
                            "ref": ref,
                            "text": source[ref]["text"],
                            "ordinal": ordinal[ref],
                            "verse_edge": _edge(ref, source_positions),
                        }
                        for ref in source_refs
                    ],
                }
            )
            used_canonical.extend(canonical_refs)
            used_source.extend(source_refs)
            i += len(canonical_refs)
            j += len(source_refs)
        if j != len(selected[surah]):
            raise ValueError(
                f"surah {surah}: {len(selected[surah]) - j} source words remain"
            )

    if used_canonical != sorted(canonical, key=_key):
        raise ValueError("canonical coverage or monotonicity failed")
    if used_source != sorted(source, key=_key):
        raise ValueError("source coverage or monotonicity failed")
    return rows


def main() -> None:
    canonical = _load(CANONICAL)
    source = _load(SOURCE)
    rows = _rows(canonical, source)
    lines = [json.dumps({"schema_version": 1, "artifact": ARTIFACT})]
    lines.extend(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows)
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            zipped.write(payload)
    digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    print(
        f"wrote {OUTPUT}: {len(rows):,} aligned rows, "
        f"{OUTPUT.stat().st_size / 1024:.1f} KiB, sha256={digest}"
    )


if __name__ == "__main__":
    main()
