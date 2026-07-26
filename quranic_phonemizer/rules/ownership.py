"""Which family owns a slot, stated once instead of guarded per rule.

Two rules had grown anonymous `return None` guards meaning "another family
owns this trigger", and each new MERGE family would have added more — an
O(families²) pattern and the mechanism by which a rule set turns into a pile
of exceptions.

The obvious fix does not work, and the reason is worth recording. A static
partition of *trigger letters* would reject the ruleset that is already
correct: `lam` is claimed by `ArticleLam` and `Idgham`, `meem` by three rules,
`noon` by two. In every case the families are separated by the **shape of the
slot**, not by its letter — is the onset geminate, is this lām the definite
article. Letters overlap legitimately; only outcomes are exclusive.

So ownership is expressed as the preconditions themselves, named once and
shared, and the exclusivity of outcomes stays where it belongs: E1, which
catches two rules claiming one `(slot, aspect)` and has now caught three real
overlaps.
"""
from __future__ import annotations

from ..model.canon import NucleusKind, Onset, Slot


def is_quiescent(slot: Slot | None) -> bool:
    """The precondition of the sākin families — nūn sākinah and mīm sākinah.

    A geminate slot belongs to `GhunnahMushaddadah`, which nasalizes it where
    it stands. Both families need this and only one had it: `MeemSakinah` was
    written with the guard because E1 fired immediately, and `NoonSakinah` has
    never had it. That asymmetry is latent rather than harmless — a geminate
    nūn with a silent nucleus would have both rules realizing the same onset
    in the same phase, and nothing but the absence of such a slot in this
    corpus has been keeping it quiet.
    """
    return (
        slot is not None
        and slot.nucleus.kind is NucleusKind.SILENT
        and slot.onset is not Onset.GEMINATE
    )
