"""
Silent-letter / single-pronounced-grapheme audit for letter-phoneme mappings.

Motivation
----------
In the Inspector Timestamps tab we want to highlight, for each phoneme, the
ONE grapheme that is actually pronounced. The letter-phoneme mapping already
groups silent letters into the same entry as their sounding neighbour, so each
flat entry maps one-or-more graphemes to a phoneme run. For highlighting to be
unambiguous, every entry must contain exactly ONE pronounced grapheme; all
other graphemes in the entry must be genuinely silent AND carry a tajweed rule
that explains the silence.

This audit verifies that invariant across an arbitrary set of references, for
both the continuous (default) and stopping contexts, and characterises every
violation pattern.

Two checks:

  A. silent-letter completeness — every silent letter (no phonemes) must carry
     at least one source tajweed rule from KNOWN_SILENT_SOURCE_RULES. A silent
     letter with no explaining rule is a missing/buggy silent rule.

  B. single-pronounced-grapheme — every flat entry must contain exactly one
     distinct pronounced letter. Entries with >= 2 pronounced letters cannot be
     reduced to a single highlight target.

Letters are attributed to flat entries by character-level lockstep: validation
Rule 2 guarantees that concatenating entry chars (minus spaces) reproduces every
letter/extension character in order, so we consume a per-character ledger in
step with the entries.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple

from quranic_phonemizer import Phonemizer
from quranic_phonemizer.tajweed_rule import TajweedRule
from quranic_phonemizer.letter_phoneme_mapping import TANWEEN_DIACRITICS


# Source rules that render a letter silent (zero phonemes) and merged into a
# neighbour. The source letter is the one that disappears; its phoneme(s), if
# any, move to / are subsumed by the target.
KNOWN_SILENT_SOURCE_RULES: Set[TajweedRule] = {
    TajweedRule.VOWEL_SILENT,
    TajweedRule.HAMZA_WASL_SILENT,
    TajweedRule.LAM_SHAMSIYAH,
    TajweedRule.IDGHAM_BILA_GHUNNAH_NOON,
    TajweedRule.IDGHAM_BILA_GHUNNAH_TANWEEN,
    TajweedRule.IDGHAM_MUTAMATHILAYN,
    TajweedRule.IDGHAM_MUTAQARIBAYN,
    TajweedRule.IDGHAM_MUTAJANISAYN_KAMIL,
    TajweedRule.SILENT_ILTIQAA_SAKINAYN,
    # idgham with ghunnah: the source NOON letter is silent (assimilated); the
    # nasalisation is carried on the target letter. The tanween variants do NOT
    # silence a letter — the letter bearing the tanween is a pronounced consonant.
    TajweedRule.IDGHAM_GHUNNAH_NOON,
}

# idgham_shafawi is dual: usually both meems sound (the source meem carries the
# geminated nasal, the target meem its vowel), but when the target meem's vowel
# is absorbed by a following long vowel the target meem is silent and explained
# by idgham_shafawi as a TARGET rule. Counted as a valid silence explanation.
SILENCE_EXPLAINING_RULES: Set[TajweedRule] = KNOWN_SILENT_SOURCE_RULES | {
    TajweedRule.IDGHAM_SHAFAWI,
}

# Short vowel phonemes — used to detect the iltiqaa demotion (a long vowel
# shortened before hamza wasl is stored on the vowel letter as a single short
# vowel, then the flat builder moves it to the preceding consonant and silences
# the vowel letter).
SHORT_VOWELS: Set[str] = {"a", "aˤ", "u", "i"}


def pronounced_in_flat(word, li: int) -> bool:
    """Whether a letter contributes an audible phoneme at its own position in
    the final flat mapping (i.e. is a highlight target).

    Mirrors the two redistributions the flat builder applies on top of the raw
    per-letter phonemes:
      - iltiqaa: a shortened long vowel before hamza wasl moves to the preceding
        consonant; the vowel letter goes silent.
      - waqf tanween: when stopping, the long vowel moves from the tanween
        consonant onto the following (otherwise silent) alef / alef-maksura.
    """
    lm = word.letter_mappings[li]
    src = {t.rule for t in lm.tajweed_rules if t.is_source}
    if lm.phonemes:
        if (TajweedRule.SILENT_ILTIQAA_SAKINAYN in src
                and len(lm.phonemes) == 1 and lm.phonemes[0] in SHORT_VOWELS):
            return False
        return True
    # raw-silent: is it the waqf-tanween redistribution target?
    if word.is_stopping and lm.char in ("ا", "ى") and li > 0:
        prev = word.letter_mappings[li - 1]
        if (prev.diacritic in TANWEEN_DIACRITICS
                and prev.phonemes and ":" in prev.phonemes[-1]):
            return True
    return False


@dataclass
class CharRec:
    """One Arabic character (base letter or one extension) in reading order."""
    ch: str
    letter_gid: Tuple[int, int]      # (word_idx, letter_idx)
    base_char: str                   # the owning letter's base char
    pronounced: bool                 # owning letter has >= 1 phoneme
    source_rules: Tuple[str, ...]
    is_stopping: bool
    location: str
    diacritic: Optional[str]
    is_base: bool                    # True for the base char, False for extensions


@dataclass
class Stats:
    refs: int = 0
    words: int = 0
    letters: int = 0
    silent_letters: int = 0
    pronounced_letters: int = 0
    entries: int = 0
    multi_grapheme_entries: int = 0
    # check A — per silent letter
    silent_without_rule: List[dict] = field(default_factory=list)
    silent_rule_dist: Counter = field(default_factory=Counter)
    silent_explained_dist: Counter = field(default_factory=Counter)
    # check B — per flat entry
    multi_sounding_entries: List[dict] = field(default_factory=list)
    zero_sounding_entries: List[dict] = field(default_factory=list)


def build_char_ledger(mapping) -> List[CharRec]:
    ledger: List[CharRec] = []
    for wi, word in enumerate(mapping.words):
        for li, lm in enumerate(word.letter_mappings):
            gid = (wi, li)
            srcset = {t.rule for t in lm.tajweed_rules if t.is_source}
            pronounced = pronounced_in_flat(word, li)
            src = tuple(sorted(r.value for r in srcset))
            ledger.append(CharRec(
                ch=lm.char, letter_gid=gid, base_char=lm.char, pronounced=pronounced,
                source_rules=src, is_stopping=word.is_stopping,
                location=word.location, diacritic=lm.diacritic, is_base=True,
            ))
            for ext in lm.extensions:
                if not ext.char:
                    continue
                ledger.append(CharRec(
                    ch=ext.char, letter_gid=gid, base_char=lm.char, pronounced=pronounced,
                    source_rules=src, is_stopping=word.is_stopping,
                    location=word.location, diacritic=lm.diacritic, is_base=False,
                ))
    return ledger


def attribute_entries(flat, ledger: List[CharRec]) -> List[Tuple[Tuple[str, List[str]], List[CharRec]]]:
    """Walk flat entries and the char ledger in lockstep; return per-entry chars."""
    out = []
    pos = 0
    for chars, phonemes in flat:
        want = chars.replace(" ", "")
        consumed: List[CharRec] = []
        acc = ""
        while pos < len(ledger) and len(acc) < len(want):
            acc += ledger[pos].ch
            consumed.append(ledger[pos])
            pos += 1
        if acc != want:
            raise RuntimeError(f"lockstep desync: entry {chars!r} want {want!r} got {acc!r}")
        out.append(((chars, phonemes), consumed))
    return out


def audit_one(pm: Phonemizer, ref: str, stop_refs: List[str], stats: Stats) -> None:
    res = pm.phonemize(ref, stop_refs=stop_refs) if stop_refs else pm.phonemize(ref)
    mapping = res.get_mapping()
    flat = res.letter_phoneme_mappings().to_list()
    ledger = build_char_ledger(mapping)

    stats.refs += 1
    stats.words += len(mapping.words)
    stats.entries += len(flat)

    # ---- Check A: silent-letter completeness (per letter) ----
    for wi, word in enumerate(mapping.words):
        for li, lm in enumerate(word.letter_mappings):
            stats.letters += 1
            src = {t.rule for t in lm.tajweed_rules if t.is_source}
            if pronounced_in_flat(word, li):
                stats.pronounced_letters += 1
                continue
            stats.silent_letters += 1
            allrules = {t.rule for t in lm.tajweed_rules}
            known = allrules & SILENCE_EXPLAINING_RULES
            stats.silent_explained_dist[
                tuple(sorted(r.value for r in known)) or ("<none>",)
            ] += 1
            stats.silent_rule_dist[
                tuple(sorted(r.value for r in allrules)) or ("<no-rules>",)
            ] += 1
            if not known:
                prev_ch = word.letter_mappings[li - 1].char if li > 0 else ""
                next_ch = word.letter_mappings[li + 1].char if li + 1 < len(word.letter_mappings) else "|"
                stats.silent_without_rule.append({
                    "location": word.location,
                    "char": lm.char,
                    "ext": [e.char for e in lm.extensions if e.char],
                    "diacritic": lm.diacritic,
                    "prev": prev_ch,
                    "next": next_ch,
                    "source_rules": sorted(r.value for r in src),
                    "is_stopping": word.is_stopping,
                    "word_text": word.text,
                })

    # ---- Check B: exactly one sounding grapheme per entry ----
    # The sounding graphemes are those audible in the final flat output
    # (pronounced_in_flat). Genuine highlight ambiguity = >= 2 distinct sounding
    # letters in one entry.
    for (chars, phonemes), consumed in attribute_entries(flat, ledger):
        if len(consumed) > 1:
            stats.multi_grapheme_entries += 1
        sounding = [c for c in consumed if c.pronounced]
        sounding_gids = {c.letter_gid for c in sounding}
        if len(sounding_gids) >= 2:
            stats.multi_sounding_entries.append({
                "ref": ref, "chars": chars, "phonemes": phonemes,
                "is_stopping": consumed[0].is_stopping if consumed else None,
                "sounding_chars": sorted({c.base_char for c in sounding}),
                "source_rules": sorted({r for c in consumed for r in c.source_rules}),
            })
        elif len(sounding_gids) == 0 and phonemes:
            stats.zero_sounding_entries.append({
                "ref": ref, "chars": chars, "phonemes": phonemes,
                "is_stopping": consumed[0].is_stopping if consumed else None,
                "source_rules": sorted({r for c in consumed for r in c.source_rules}),
            })


def all_word_refs(pm: Phonemizer) -> List[str]:
    refs = []
    for s_key, verses in pm._surah_info.items():
        for vi, wcount in enumerate(verses, start=1):
            for w in range(1, wcount + 1):
                refs.append(f"{s_key}:{vi}:{w}")
    return refs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["continuous", "random-stops"],
                    default="continuous")
    ap.add_argument("--n-random-stops", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="out/audit_silent_letters.json")
    args = ap.parse_args()

    pm = Phonemizer()
    stats = Stats()

    if args.mode == "continuous":
        # Phonemize the whole mushaf surah-by-surah, continuous (no stops).
        for s_key in sorted(pm._surah_info, key=int):
            audit_one(pm, s_key, [], stats)

    elif args.mode == "random-stops":
        refs = all_word_refs(pm)
        rng = random.Random(args.seed)
        sample = rng.sample(refs, min(args.n_random_stops, len(refs)))
        # Phonemize each sampled word's verse, stopping on that word, so the
        # word is rendered in waqf context exactly as a reciter pausing there.
        for wref in sample:
            s, v, w = wref.split(":")
            audit_one(pm, f"{s}:{v}", [wref], stats)

    report(stats, args)


def report(stats: Stats, args) -> None:
    import os
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    print(f"\n=== Silent-letter audit ({args.mode}) ===")
    print(f"refs phonemized : {stats.refs}")
    print(f"words           : {stats.words}")
    print(f"letters         : {stats.letters}")
    print(f"  pronounced    : {stats.pronounced_letters}")
    print(f"  silent        : {stats.silent_letters}")
    print(f"flat entries    : {stats.entries}")
    print(f"  multi-grapheme: {stats.multi_grapheme_entries}")
    print()
    print(f"CHECK A  silent letters with NO known silent rule : {len(stats.silent_without_rule)}")
    print(f"CHECK B  entries with >=2 sounding graphemes       : {len(stats.multi_sounding_entries)}")
    print(f"CHECK B  entries with 0 sounding graphemes (anom.) : {len(stats.zero_sounding_entries)}")
    print()

    print("--- silent letters explained by (known silent rules) ---")
    for k, c in stats.silent_explained_dist.most_common():
        print(f"  {c:8d}  {', '.join(k)}")

    if stats.silent_without_rule:
        print("\n--- CHECK A violations: silent letters lacking a known silent rule ---")
        by_pat = Counter(
            (v["char"], tuple(v["source_rules"]), v["is_stopping"])
            for v in stats.silent_without_rule
        )
        for (ch, rules, stop), c in by_pat.most_common():
            print(f"  {c:8d}  char={ch!r} stop={stop} source_rules={list(rules)}")

    if stats.multi_sounding_entries:
        print("\n--- CHECK B: entries with >=2 sounding graphemes (pattern counts) ---")
        by_pat = Counter(
            (tuple(v["sounding_chars"]), v["is_stopping"], tuple(v["source_rules"]))
            for v in stats.multi_sounding_entries
        )
        for (chs, stop, rules), c in by_pat.most_common(30):
            print(f"  {c:8d}  sounding={list(chs)} stop={stop} rules={list(rules)}")

    if stats.zero_sounding_entries:
        print("\n--- CHECK B: entries with 0 sounding graphemes (anomalies) ---")
        by_pat = Counter(
            (v["chars"], tuple(v["phonemes"]), v["is_stopping"], tuple(v["source_rules"]))
            for v in stats.zero_sounding_entries
        )
        for (chs, ph, stop, rules), c in by_pat.most_common(30):
            print(f"  {c:8d}  chars={chs!r} ph={list(ph)} stop={stop} rules={list(rules)}")

    payload = {
        "mode": args.mode,
        "summary": {
            "refs": stats.refs, "words": stats.words, "letters": stats.letters,
            "pronounced_letters": stats.pronounced_letters,
            "silent_letters": stats.silent_letters,
            "entries": stats.entries, "multi_grapheme_entries": stats.multi_grapheme_entries,
            "check_A_silent_without_rule": len(stats.silent_without_rule),
            "check_B_multi_sounding": len(stats.multi_sounding_entries),
            "check_B_zero_sounding": len(stats.zero_sounding_entries),
        },
        "silent_explained_dist": {", ".join(k): c for k, c in stats.silent_explained_dist.most_common()},
        "silent_rule_dist": {", ".join(k): c for k, c in stats.silent_rule_dist.most_common()},
        "check_A_examples": stats.silent_without_rule[:1000],
        "check_B_multi_sounding_examples": stats.multi_sounding_entries[:1000],
        "check_B_zero_sounding_examples": stats.zero_sounding_entries[:1000],
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
