"""Dump today's real output for the example words: sounds, glyphs, rules."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import BoundaryPlan, Junction, VerseRef
from quranic_phonemizer.model.canon import Riwayah
from quranic_phonemizer.model.inscription import Script
from quranic_phonemizer.render.alphabet import load_alphabet
from quranic_phonemizer.render.anchored import anchored, graphemes_by_id

HAFS = recitation(Riwayah.HAFS)
ALPHABET = load_alphabet(ROOT / "quranic_phonemizer" / "data" / "render" / "ipa.yaml")


def dump(surah, ayah, first, last, stops):
    verse = VerseRef(surah, ayah)
    words = HAFS.words(verse)[first - 1:last]
    reading = HAFS.read(Script.UTHMANI, verse, words)
    built = HAFS.build(reading)
    score = built.score
    plan = BoundaryPlan(tuple(
        Junction.STOP if s else Junction.JOIN for s in stops
    ))
    perf = HAFS.perform(score, plan)
    view = anchored(perf, built.inscription, ALPHABET)
    chars = graphemes_by_id(built.inscription)

    slot_letter = {}
    for word in score.words:
        for slot in word.slots:
            slot_letter[slot.id] = (
                slot.letter.value, slot.onset.value, slot.nucleus.kind.value
            )

    text = " ".join(t for _, t in words)
    print(f"\n=== {surah}:{ayah}:{first}-{last} stops={stops}  {text}")
    print(" tokens:", " ".join(s.token for s in view.sounds))
    for s in view.sounds:
        g = "".join(chars[i].char for i in s.graphemes)
        lets = ",".join(
            f"{slot_letter[x][0]}/{slot_letter[x][1]}/{slot_letter[x][2]}"
            for x in s.slots
        )
        merged = ",".join(slot_letter[x][0] for x in s.merged_from)
        print(f"   {s.token:<6} glyphs={g!r:<14} slots=[{lets}] rule={s.rule.value}"
              + (f" merged_from=[{merged}]" if merged else ""))
    for item in view.silent:
        g = "".join(chars[i].char for i in item.graphemes)
        print(f"   {'-':<6} glyphs={g!r:<14} slot={slot_letter[item.slot][0]} rule={item.rule.value}")


CASES = [
    (2, 1, 1, 1, [True]),          # muqattaat
    (1, 2, 1, 1, [True]),          # hamza wasl started on / stopped
    (1, 3, 1, 1, [True]),          # lam shamsiyyah + dagger
    (2, 2, 2, 2, [True]),          # lam qamariyyah + dagger
    (2, 6, 3, 3, [False]),         # plural waw otiose alif
    (2, 5, 3, 3, [True]),          # iwad, seat written
    (2, 22, 11, 11, [True]),       # iwad, no seat
    (2, 26, 9, 9, [True]),         # taa marbuta + tanween
    (113, 1, 3, 3, [True]),        # qalqala kubra
    (2, 27, 7, 7, [False]),        # silah
]

if __name__ == "__main__":
    for c in CASES:
        try:
            dump(*c)
        except Exception as exc:
            print(f"\n=== {c} FAILED: {type(exc).__name__}: {exc}")
