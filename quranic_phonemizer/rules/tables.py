"""The shapes a rule's letter membership takes. Loading them is riwayat's job."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ..model.canon import CanonLetter, Rule

#: What a quiescent noon's table may name. The remainder is IKHFAA, and
#: IZHAR also fires from within a word rather than selected by a letter.
NOON_OUTCOMES = frozenset({
    Rule.IZHAR,
    Rule.IDGHAM_BI_GHUNNAH,
    Rule.IDGHAM_BILA_GHUNNAH,
    Rule.IQLAB,
})

#: What a quiescent meem's table may name. The remainder is IZHAR_SHAFAWI.
MEEM_OUTCOMES = frozenset({Rule.IKHFAA_SHAFAWI, Rule.IDGHAM_SHAFAWI})

#: What the pair table may name. IDGHAM_MUTAMATHILAYN is absent: like into
#: like fires on any repeated letter, so no pair needs listing.
PAIR_OUTCOMES = frozenset({
    Rule.IDGHAM_MUTAJANISAYN_KAMIL,
    Rule.IDGHAM_MUTAJANISAYN_NAQIS,
    Rule.IDGHAM_MUTAQARIBAYN,
})


@dataclass(frozen=True, slots=True)
class Followers:
    """Which outcome each following letter selects. Disjoint by construction;
    a letter no set claims falls to the family's own default."""

    by_rule: Mapping[Rule, frozenset[CanonLetter]]
    never_follows: frozenset[CanonLetter] = frozenset()

    def of(self, letter: CanonLetter) -> Rule | None:
        for rule, letters in self.by_rule.items():
            if letter in letters:
                return rule
        return None

    def remainder(self) -> frozenset[CanonLetter]:
        """What no set claims and that can actually follow a quiescent letter."""
        claimed = frozenset().union(*self.by_rule.values()) if self.by_rule else frozenset()
        return frozenset(set(CanonLetter) - claimed - self.never_follows)


@dataclass(frozen=True, slots=True)
class Pairs:
    """Adjacent letter pairs that assimilate, first into second."""

    by_pair: Mapping[tuple[CanonLetter, CanonLetter], Rule]

    def of(self, first: CanonLetter, second: CanonLetter) -> Rule | None:
        return self.by_pair.get((first, second))
