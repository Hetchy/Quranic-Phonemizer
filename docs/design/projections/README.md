# The public projection API

ADR-005 §1 designed the mechanism by which recited text is derived and put the
public projection API out of scope. This is that API.

| | Document | Answers |
|---|---|---|
| [00](00-audit.md) | Audit | What the five legacy projections published, which consumer read what, where consumers invent facts, and what the layered model still cannot say |
| [01](01-design.md) | Design | Two projections over typed nodes and four lossless relation families |
| [02](02-equivalence-gate.md) | Gate | Exact legacy adapters plus laws for the richer graph |
| [03](03-review.md) | Review | What the three documents still get wrong, verified against source; four blockers before implementation |
| [04](04-resolutions.md) | Resolutions | The review answered item by item: four owner decisions, a fifth blocker it missed, two of its own claims corrected, and every open question closed |
| [05](05-vocabulary.md) | Vocabulary | The contract explained for a consumer who has not read `model/`, plus a name-by-name audit with the alternatives rejected |
| [06](06-examples.md) | Examples | One generated contract example per linguistic case and per rule case |
| [07](07-review-prompt.md) | Review brief | The defect classes this design has already produced, and the hit list for the next adversarial pass |

Scope: Uthmani, Hafs. IndoPak is deferred and nothing here depends on it.

Assumes [03-canonical-vocabulary](../03-canonical-vocabulary.md) resolved and
follows [ADR-013](../../adr/013-public-projection-foundations.md).

The one-paragraph version: four of the five legacy projections were four
traversals of a join that the old model could not hold, so each recomputed
relationships from rule names and lost a different set; the fifth,
`phonetic_text`, rebuilt recited Arabic from rule names for the same reason.
The layered model is the join. `Mappings` publishes its five ordered node
arrays and its typed spelling, attribution, and modifier edges, plus explicit
glyph contribution, without duplicate reverse links. `phonemes` stays separate
because the token stream and the graph version at different rates, not because
it is a convenience.
