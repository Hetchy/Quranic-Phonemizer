"""Full-Hafs corpus inventory and invariants for source animation tokens."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quranic_phonemizer import Phonemizer  # noqa: E402

SPECIAL = {
    "hamza_above": "\u0654",
    "hamza_below": "\u0655",
    "dagger_alif": "\u0670",
    "small_waw": "\u06e5",
    "small_yaa": "\u06e6",
    "small_high_yaa": "\u06e7",
    "small_high_noon": "\u06e8",
    "mini_seen": "\u06dc",
    "mini_seen_alt": "\u06e3",
}
_worker: Phonemizer | None = None


def _init() -> None:
    global _worker
    _worker = Phonemizer()


def _verse(ref: str) -> dict:
    assert _worker is not None
    analysed = _worker.analyse(ref)
    source = analysed.source()
    analysis = analysed.analysis
    occurrence_rules = {
        occurrence.id.value: occurrence.rule_id.value
        for occurrence in analysis.rule_occurrences
    }
    solar_sound_ids = {
        sound.id.value
        for sound in analysis.sounds
        if any(
            occurrence_rules[occurrence_id.value] == "lam_shamsiyyah"
            for occurrence_id in sound.rule_occurrence_ids
        )
    }
    policies = Counter(token.policy.value for token in source.animation_tokens)
    ownership = Counter(
        f"{token.policy.value}:{'sounding' if token.sound_ids else 'soundless'}"
        for token in source.animation_tokens
    )
    specials = Counter()
    examples = {}
    policy_examples = {}
    adjacency_conflicts = []
    silent_solar_lams = 0
    for token in source.animation_tokens:
        policy_examples.setdefault(
            token.policy.value,
            {
                "ref": ref,
                "text": token.text,
                "token": token.id.value,
                "target": (
                    None if token.target_token_id is None else token.target_token_id.value
                ),
            },
        )
        for name, scalar in SPECIAL.items():
            if scalar in token.text:
                specials[name] += 1
                examples.setdefault(name, {"ref": ref, "text": token.text, "token": token.id.value})
        if any(mark in token.text for mark in (SPECIAL["mini_seen"], SPECIAL["mini_seen_alt"])):
            if len(token.source_unit_ids) != 1:
                raise RuntimeError(f"{ref}: mini seen is not independent token {token.id.value}")
            saad = [
                candidate
                for candidate in source.animation_tokens
                if candidate.word_id == token.word_id and "ص" in candidate.text
            ]
            if len(saad) != 1 or bool(saad[0].sound_ids) == bool(token.sound_ids):
                raise RuntimeError(
                    f"{ref}: mini seen and sad do not select exactly one sound owner"
                )
            sounded, silent = (token, saad[0]) if token.sound_ids else (saad[0], token)
            if silent.target_token_id != sounded.id:
                raise RuntimeError(
                    f"{ref}: silent mini-seen choice does not target its sounded pair"
                )
        if not token.paint_character_ids:
            raise RuntimeError(f"{ref}: token {token.id.value} has no paint characters")
        presented = {
            sound_id.value
            for unit_id in token.source_unit_ids
            for sound_id in source.units[unit_id.value].presented_sound_ids
        }
        if presented & solar_sound_ids:
            if token.sound_ids:
                raise RuntimeError(
                    f"{ref}: solar lam token {token.id.value} incorrectly owns highlight sound"
                )
            silent_solar_lams += 1
        if token.target_token_id is not None:
            target = source.animation_tokens[token.target_token_id.value]
            if target.policy.value != "timed":
                raise RuntimeError(
                    f"{ref}: token {token.id.value} targets non-timed token {target.id.value}"
                )
    for previous, token in zip(source.animation_tokens, source.animation_tokens[1:], strict=False):
        if (
            previous.word_id == token.word_id
            and previous.policy.value == "cohighlight_next"
            and token.policy.value == "cohighlight_previous"
            and previous.target_token_id != token.target_token_id
        ):
            adjacency_conflicts.append(
                {
                    "ref": ref,
                    "previous": previous.text,
                    "token": token.text,
                    "previous_target": previous.target_token_id.value,
                    "token_target": token.target_token_id.value,
                }
            )
    return {
        "tokens": len(source.animation_tokens),
        "policies": policies,
        "ownership": ownership,
        "specials": specials,
        "examples": examples,
        "policy_examples": policy_examples,
        "adjacency_conflicts": adjacency_conflicts,
        "silent_solar_lams": silent_solar_lams,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--output", type=Path, default=Path(".local/hafs-animation-token-audit.json"))
    args = parser.parse_args()
    package = Phonemizer()
    refs = [
        f"{surah}:{ayah}"
        for surah in range(1, 115)
        for ayah in range(1, len(package._recitation.corpus.surah_info[str(surah)]) + 1)
    ]
    policies, ownership = Counter(), Counter()
    specials, examples, policy_examples = Counter(), {}, {}
    total = 0
    silent_solar_lams = 0
    adjacency_conflicts = []
    if args.workers == 1:
        _init()
        rows = map(_verse, refs)
    else:
        pool = ProcessPoolExecutor(max_workers=args.workers, initializer=_init)
        rows = pool.map(_verse, refs, chunksize=8)
    try:
        for row in rows:
            total += row["tokens"]
            silent_solar_lams += row["silent_solar_lams"]
            policies.update(row["policies"])
            ownership.update(row["ownership"])
            specials.update(row["specials"])
            for name, example in row["examples"].items():
                examples.setdefault(name, example)
            for name, example in row["policy_examples"].items():
                policy_examples.setdefault(name, example)
            adjacency_conflicts.extend(row["adjacency_conflicts"])
    finally:
        if args.workers != 1:
            pool.shutdown()
    report = {
        "riwayah": "hafs",
        "script": "uthmani",
        "verses": len(refs),
        "animation_tokens": total,
        "silent_solar_lams": silent_solar_lams,
        "policies": dict(sorted(policies.items())),
        "policy_sound_ownership": dict(sorted(ownership.items())),
        "special_token_occurrences": dict(sorted(specials.items())),
        "first_examples": dict(sorted(examples.items())),
        "first_policy_examples": dict(sorted(policy_examples.items())),
        "adjacent_delegate_conflicts": {
            "count": len(adjacency_conflicts),
            "examples": adjacency_conflicts[:20],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
