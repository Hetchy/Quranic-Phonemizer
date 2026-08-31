"""Compare two digest streams and describe where the readings moved."""
from __future__ import annotations

import json
from pathlib import Path

#: Differing paths reported per reading. A structural change usually repeats,
#: so the first few name it without burying the report.
PATHS_PER_READING = 12


def load(path: Path) -> dict[tuple[str, str], dict]:
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows[(row["ref"], row["plan"])] = row
    return rows


def _paths(before, after, at: str = "") -> list[str]:
    """Where two decoded documents differ, as reader-facing paths."""
    if type(before) is not type(after):
        return [f"{at}: {type(before).__name__} -> {type(after).__name__}"]
    if isinstance(before, dict):
        found = []
        for key in sorted(set(before) | set(after)):
            if key not in before:
                found.append(f"{at}.{key}: added")
            elif key not in after:
                found.append(f"{at}.{key}: removed")
            else:
                found += _paths(before[key], after[key], f"{at}.{key}")
        return found
    if isinstance(before, list):
        if len(before) != len(after):
            return [f"{at}: {len(before)} entries -> {len(after)}"]
        return [
            path
            for index, (one, two) in enumerate(zip(before, after, strict=True))
            for path in _paths(one, two, f"{at}[{index}]")
        ]
    return [] if before == after else [f"{at}: {before!r} -> {after!r}"]


def _words(before: dict, after: dict) -> list[str]:
    """Per-word phoneme changes, addressed by the word reference."""
    old_refs, new_refs = before.get("refs", []), after.get("refs", [])
    if old_refs != new_refs:
        return [f"words {len(old_refs)} -> {len(new_refs)}"]
    return [
        f"{ref}: {' '.join(one) or '-'} -> {' '.join(two) or '-'}"
        for ref, one, two in zip(old_refs, before["words"], after["words"], strict=True)
        if one != two
    ]


def _structure(before: dict, after: dict) -> list[str]:
    one, two = before.get("structure"), after.get("structure")
    if one is None or two is None:
        return []
    found = _paths(json.loads(one), json.loads(two))
    extra = len(found) - PATHS_PER_READING
    return found[:PATHS_PER_READING] + (
        [f"and {extra} further differing paths"] if extra > 0 else []
    )


def classify(baseline: dict, candidate: dict) -> dict:
    """Group every reading by how the two installs disagree about it."""
    report = {
        "compared": 0, "errors": [], "only_baseline": [], "only_candidate": [],
        "phonemes": [], "structure": [], "structure_compared": 0,
    }
    for key in sorted(set(baseline) | set(candidate)):
        ref = f"{key[0]} {key[1]}"
        one, two = baseline.get(key), candidate.get(key)
        if one is None:
            report["only_candidate"].append(ref)
            continue
        if two is None:
            report["only_baseline"].append(ref)
            continue
        report["compared"] += 1
        for row, side in ((one, "baseline"), (two, "candidate")):
            if "error" in row:
                report["errors"].append(f"{ref} {side}: {row['error']}")
        if "error" in one or "error" in two:
            continue
        if one["phonemes_digest"] != two["phonemes_digest"]:
            report["phonemes"].append(ref)
        if one["structure_digest"] is not None and two["structure_digest"] is not None:
            report["structure_compared"] += 1
            if one["structure_digest"] != two["structure_digest"]:
                report["structure"].append(ref)
    return report


def detail(baseline: dict, candidate: dict, keys: list[tuple[str, str]]) -> list[dict]:
    """The readable diff for the readings that changed."""
    rows = []
    for key in keys:
        one, two = baseline.get(key), candidate.get(key)
        if one is None or two is None:
            continue
        rows.append({
            "ref": key[0],
            "plan": key[1],
            "phonemes": _words(one, two),
            "structure": _structure(one, two),
        })
    return rows
