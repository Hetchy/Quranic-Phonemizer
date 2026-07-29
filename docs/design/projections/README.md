# The public projection API

ADR-005 §1 designed the mechanism by which recited text is derived and put the
public projection API out of scope. This is that API.

| | Document | Answers |
|---|---|---|
| [00](00-audit.md) | Audit | What the four legacy projections published, which consumer read what, where consumers invent facts, and what the layered model still cannot say |
| [01](01-design.md) | Design | Two projections; the key is a unit, not a character; the three model changes it needs |
| [02](02-equivalence-gate.md) | Gate | How replacement is proven not to lose anything |

Scope: Uthmani, Hafs. IndoPak is deferred and nothing here depends on it.

Assumes [03-canonical-vocabulary](../03-canonical-vocabulary.md) resolved.

The one-paragraph version: the four legacy projections were four traversals of a
join that the old model could not hold, so each recomputed the relationships
from rule names and each lost a different set of them. The layered model *is*
the join. One document -- `Reading` -- publishes it as five node arrays keyed on
the `Slot`, and `phonemes` stays separate for the consumers who want only sound.
