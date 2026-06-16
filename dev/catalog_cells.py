"""
Catalogue every multi-grapheme letter-phoneme cell across 1-114.

A "cell" is one ``letter_phoneme_mappings()`` entry; a multi-grapheme cell is the
phonemizer's grouping that the bucket TS shard reproduces as letters sharing one
[start,end] span. For each such cell this enumerates, grouped and counted across
the whole mushaf in BOTH continuous and verse-end-stop context:

  - role pattern  — per grapheme: S silent letter · P pronounced (sounding) ·
                    X extension (dagger alef / mini waw-yaa)
  - rules         — the tajweed rule(s) that make the silent graphemes silent
                    (UNRULED = the otiose tanween alef, which carries none)
  - cross-word    — whether the cell spans a word boundary
  - false-tagged  — the P grapheme(s): what a naive "duplicate-span ⇒ silent"
                    rule would wrongly skip
  - example       — the word(s) the cell sits in

The point is to let a human decide, per pattern, what is a real false-tag.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict

from quranic_phonemizer import Phonemizer

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from audit_silent_letters import (  # noqa: E402
    build_char_ledger, attribute_entries, pronounced_in_flat,
    SILENCE_EXPLAINING_RULES,
)

_RULE_TAG = re.compile(r"</?rule[^>]*?>")
_KNOWN = {r.value for r in SILENCE_EXPLAINING_RULES}


def _clean(t: str) -> str:
    return _RULE_TAG.sub("", t)


def catalogue(pm: Phonemizer, refs, ctx_label, agg, examples):
    for ref, stops in refs:
        res = pm.phonemize(ref, stop_refs=stops) if stops else pm.phonemize(ref)
        m = res.get_mapping()
        flat = res.letter_phoneme_mappings().to_list()
        ledger = build_char_ledger(m)
        loc2text = {w.location: _clean(w.text) for w in m.words}
        gid2letter = {
            (wi, li): lm
            for wi, w in enumerate(m.words)
            for li, lm in enumerate(w.letter_mappings)
        }
        for (chars, phon), consumed in attribute_entries(flat, ledger):
            if len(consumed) <= 1:
                continue
            roles, rules, words = [], set(), []
            for c in consumed:
                if c.location not in words:
                    words.append(c.location)
                lm = gid2letter[c.letter_gid]
                allr = {t.rule.value for t in lm.tajweed_rules}
                if not c.is_base:
                    roles.append("X")
                elif c.pronounced:
                    roles.append("P")
                else:
                    roles.append("S")
                    known = allr & _KNOWN
                    rules |= known if known else {"UNRULED"}
            cross = " " in chars.strip()
            key = (" ".join(roles), tuple(sorted(rules)), cross, ctx_label)
            agg[key] += 1
            if len(examples[key]) < 4:
                wt = " ‖ ".join(loc2text.get(w, w) for w in words)
                examples[key].add((chars, tuple(phon), wt))


def all_surahs():
    return [(str(s), []) for s in range(1, 115)]


def all_verse_stops(pm):
    out = []
    for s_key, verses in pm._surah_info.items():
        for vi in range(1, len(verses) + 1):
            out.append((f"{s_key}:{vi}", [f"{s_key}:{vi}:{verses[vi-1]}"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out/cell_catalogue.md")
    args = ap.parse_args()
    pm = Phonemizer()
    agg = Counter()
    examples = defaultdict(set)

    catalogue(pm, all_surahs(), "cont", agg, examples)
    catalogue(pm, all_verse_stops(pm), "stop", agg, examples)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    # Merge cont/stop into one row per (roles, rules, cross).
    merged = defaultdict(lambda: {"cont": 0, "stop": 0})
    ex_by_struct = {}
    for (roles, rules, cross, ctx), cnt in agg.items():
        struct = (roles, rules, cross)
        merged[struct][ctx] += cnt
        ex_by_struct.setdefault(struct, sorted(examples[(roles, rules, cross, ctx)])[0]
                                if examples[(roles, rules, cross, ctx)] else None)

    rows = sorted(merged.items(), key=lambda kv: -(kv[1]["cont"] + kv[1]["stop"]))

    lines = ["# Multi-grapheme cell catalogue (letter-phoneme = shard duplicate-span)\n"]
    lines.append("Every grouped cell across 1-114. Roles per grapheme: **S** silent "
                 "letter · **P** pronounced (sounding) · **X** extension. "
                 "`P (false-tag)` = how many sounding graphemes a naive "
                 "\"duplicate-span ⇒ silent\" rule would wrongly skip in this cell.\n")
    lines.append("| # | roles | silencing rules | cross-word | cont | stop | "
                 "P (false-tag) | example cell → phones | word(s) |")
    lines.append("|---|---|---|---|--:|--:|--:|---|---|")
    for i, ((roles, rules, cross), c) in enumerate(rows, 1):
        nP = roles.split().count("P")
        ex = ex_by_struct[(roles, rules, cross)]
        chars, phon, wt = ex if ex else ("", (), "")
        lines.append(
            f"| {i} | `{roles}` | {', '.join(rules)} | {'yes' if cross else ''} | "
            f"{c['cont']} | {c['stop']} | {nP} | `{chars}` → {list(phon)} | {wt} |"
        )
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("\n".join(lines))
    print(f"\n[{len(rows)} distinct patterns; wrote {args.out}]")


if __name__ == "__main__":
    main()
