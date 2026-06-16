"""
Tokenization reconciliation: tajweed vs letter-phoneme vs the bucket TS shard.

Three grapheme tokenizations are in play for the Timestamps tab highlight:

  1. ``tajweed_mappings()``   — one entry per grapheme, real extensions split,
     BUT it injects a synthetic dagger-alef for lafdh jalalah (Allah's implicit
     madd) and spells muqattaat out as letter NAMES (أَلِف لَام …).
  2. ``letter_phoneme_mappings()`` — same per-grapheme atoms over the ACTUAL
     written text (no synthetic Allah dagger, muqattaat kept as written), then
     silent graphemes are GROUPED into their sounding neighbour's entry.
  3. The bucket TS shard ``letters[]`` (``reciters/<slug>/timestamps/<ch>.json.gz``)
     — one ``[char, start_ms, end_ms]`` per grapheme of the actual written text,
     real extensions split, silent letters NOT grouped but given the SAME
     timespan as their sounding neighbour (the FE "one cell" behaviour).

Part 1 quantifies where (1) and (2) diverge across 1-114 (atoms only).
Part 2 proves the shard ``letters[]`` equals the letter-phoneme ATOMS on a real
shard fixture (per word, char-for-char), so the letter-phoneme silent/sounding
classification can be stamped onto shard letters 1:1.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter

from quranic_phonemizer import Phonemizer

_CANON_VERSE = re.compile(r"^\d+:\d+$")


def _grapheme_chars(letter) -> str:
    """A letter's written graphemes: base char + each (split) extension char."""
    return letter.char + "".join(e.char for e in letter.extensions if e.char)


def part1_tajweed_vs_lp(pm: Phonemizer) -> None:
    """Compare tajweed vs letter-phoneme grapheme atoms across 1-114, by word."""
    total_words = mismatch_words = 0
    by_cause: Counter = Counter()
    for s in range(1, 115):
        res = pm.phonemize(str(s))
        mapping = res.get_mapping()
        taj = res.tajweed_mappings()
        # taj words can be more numerous than mapping words (muqattaat split into
        # multiple letter-name words), so compare at the SURAH grapheme level for
        # atoms, but attribute causes per mapping word.
        taj_seq = "".join(e.char for w in taj.words for e in w.entries)
        lp_seq = "".join(_grapheme_chars(lm) for w in mapping.words for lm in w.letter_mappings)
        for w in mapping.words:
            total_words += 1
            if w.is_special_word:
                by_cause["muqattaat (spelled out in tajweed)"] += 1
                mismatch_words += 1
            elif any(mm.is_lafdh_jalalah for mm in w.madd_mappings):
                by_cause["lafdh jalalah (synthetic dagger in tajweed)"] += 1
                mismatch_words += 1
            elif any(mm.is_hamza_fathatan for mm in w.madd_mappings):
                by_cause["hamza+fathatan (exempt madd)"] += 1
        if taj_seq != lp_seq:
            by_cause["_surah_atom_mismatch"] += 1

    print("=== Part 1: tajweed vs letter-phoneme atoms (1-114) ===")
    print(f"words total                 : {total_words}")
    print(f"words diverging (by cause)  :")
    for cause, c in by_cause.most_common():
        if cause.startswith("_"):
            continue
        print(f"  {c:6d}  {cause}")
    print(f"surahs with any atom mismatch: {by_cause['_surah_atom_mismatch']}/114")


def part2_shard_vs_lp(pm: Phonemizer, shard_path: str) -> None:
    """Prove shard letters[] == letter-phoneme atoms per word on a real fixture."""
    doc = json.load(open(shard_path, encoding="utf-8"))
    ch = doc["_meta"]["chapter"]
    seg_ok = seg_total = word_ok = word_total = 0
    mismatches = []
    for seg in doc["segments"]:
        ref = seg["ref"]
        if not _CANON_VERSE.match(ref):
            continue
        widxs = [w[0] for w in seg["words"]]
        if widxs != list(range(widxs[0], widxs[0] + len(widxs))):
            continue
        s, v = ref.split(":")
        lo, hi = widxs[0], widxs[-1]
        span = f"{s}:{v}:{lo}" if lo == hi else f"{s}:{v}:{lo}-{s}:{v}:{hi}"
        try:
            mapping = pm.phonemize(span, stop_refs=[f"{s}:{v}:{hi}"]).get_mapping()
        except Exception:
            continue
        seg_total += 1
        ok = True
        for wi, word in enumerate(mapping.words):
            ph = "".join(_grapheme_chars(lm) for lm in word.letter_mappings)
            sh = "".join(L[0] for L in seg["words"][wi][3]) if wi < len(seg["words"]) else ""
            word_total += 1
            if ph == sh:
                word_ok += 1
            else:
                ok = False
                if len(mismatches) < 10:
                    mismatches.append((span, wi, ph, sh))
        seg_ok += ok

    print(f"\n=== Part 2: shard vs letter-phoneme atoms (surah {ch}) ===")
    print(f"segments fully matching: {seg_ok}/{seg_total}")
    print(f"words matching         : {word_ok}/{word_total}")
    for mm in mismatches:
        print("  MISMATCH", mm)


def part3_shard_silence_heuristic(pm: Phonemizer, shard_path: str) -> None:
    """Can the silent grapheme be inferred from the shard's timing alone?

    Tests the "duplicate-span" signal (a silent letter is given the SAME
    [start,end] as its sounding neighbour): for each grapheme, compare
    "shares an exact span with a neighbour" against the phonemizer ground truth
    (silent vs sounding vs extension), and locate where the sounding grapheme
    sits inside each duplicate-span group.
    """
    import sys
    sys.path.insert(0, __import__("os").path.dirname(__file__))
    from audit_silent_letters import pronounced_in_flat

    doc = json.load(open(shard_path, encoding="utf-8"))
    ch = doc["_meta"]["chapter"]
    miss = false_tag = 0
    pos = Counter()
    for seg in doc["segments"]:
        ref = seg["ref"]
        if not _CANON_VERSE.match(ref):
            continue
        widxs = [w[0] for w in seg["words"]]
        if widxs != list(range(widxs[0], widxs[0] + len(widxs))):
            continue
        s, v = ref.split(":")
        lo, hi = widxs[0], widxs[-1]
        span = f"{s}:{v}:{lo}" if lo == hi else f"{s}:{v}:{lo}-{s}:{v}:{hi}"
        try:
            mapping = pm.phonemize(span, stop_refs=[f"{s}:{v}:{hi}"]).get_mapping()
        except Exception:
            continue
        gt = []
        for w in mapping.words:
            for li, lm in enumerate(w.letter_mappings):
                gt.append("sound" if pronounced_in_flat(w, li) else "silent")
                gt += ["ext" for e in lm.extensions if e.char]
        sh = [(L[1], L[2]) for w in seg["words"] for L in w[3]]
        if len(sh) != len(gt):
            continue
        n = len(sh)
        for i in range(n):
            dup = (i > 0 and sh[i - 1] == sh[i]) or (i < n - 1 and sh[i + 1] == sh[i])
            if gt[i] == "silent" and not dup:
                miss += 1
            if gt[i] == "sound" and dup:
                false_tag += 1
        i = 0
        while i < n:
            j = i
            while j + 1 < n and sh[j + 1] == sh[i]:
                j += 1
            if j > i:
                snd = [k - i for k in range(i, j + 1) if gt[k] == "sound"]
                if snd == [0]:
                    pos["sounding FIRST"] += 1
                elif snd == [j - i]:
                    pos["sounding LAST"] += 1
                elif not snd:
                    pos["no sounding"] += 1
                else:
                    pos["mid/multi"] += 1
            i = j + 1

    print(f"\n=== Part 3: can silence be inferred from shard timing alone? (surah {ch}) ===")
    print(f"silent graphemes the duplicate-span signal MISSES   : {miss}")
    print(f"sounding graphemes it would WRONGLY skip            : {false_tag}")
    print("position of the sounding grapheme in duplicate-span groups:")
    for k, c in pos.most_common():
        print(f"  {c:4d}  {k}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", help="path to a TS shard JSON (decompressed) for Parts 2+3")
    args = ap.parse_args()
    pm = Phonemizer()
    part1_tajweed_vs_lp(pm)
    if args.shard:
        part2_shard_vs_lp(pm, args.shard)
        part3_shard_silence_heuristic(pm, args.shard)


if __name__ == "__main__":
    main()
