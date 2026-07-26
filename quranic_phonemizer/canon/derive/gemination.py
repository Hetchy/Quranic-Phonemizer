"""The shadda: canonical gemination, or a witness to an assimilation.

ADR-003 §4.1 first stated this positionally — *word-initial* shadda attests.
Measured, position is the wrong axis: 5:28:2 `بَسَطْتَ` / `بَسَطْتَّ` writes an
IndoPak-only shadda word-**internally**, attesting idghām mutajānisayn.

The canonical statement covers both and needs no glyph positions:

> A shadda on a slot whose preceding **sound** is silent attests
> `ASSIMILATION`. Anywhere else it is `Onset.GEMINATE`.

It is a Performance predicate, evaluated under the all-join plan — which is
what §4.1 property 2 ("a mushaf writes the connected reading") and invariant A1
("under the all-join boundary plan") already said. The three readings differ by
2,440 sites per script, all of them the article before a geminated lām, whose
helping vowel is elided in waṣl but present in the Score.

Word-initial gemination is deliberately **not** a Score fact: it is waṣl-only,
it drops at ibtidāʾ, and making it canonical would put the measured 2,415-word
disagreement between the two scripts into the L1 residue.
"""
from __future__ import annotations

from ...model.canon import NucleusKind, Onset, RuleFamily
from ...model.inscription import SlotFact
from . import Attests, Context, Outcome, Sets, register


@register("gemination")
def gemination(context: Context) -> Outcome:
    if _preceded_by_silence(context):
        return Attests(RuleFamily.ASSIMILATION)
    return Sets(SlotFact.ONSET, Onset.GEMINATE)


def _preceded_by_silence(context: Context) -> bool:
    if context.word_initial:
        return True
    previous = context.previous_nucleus
    return previous is not None and previous.kind is NucleusKind.SILENT
