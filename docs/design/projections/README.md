# The public projection API

ADR-005 designed the mechanism by which recited text is derived and put the
public projection API out of scope. This is that API.

| | Document | Answers |
|---|---|---|
| [01](01-contract.md) | Contract | The two projections, the nodes and edges, the read API, and what the producer must still build |
| [02](02-gate.md) | Gate | The legacy adapters, the completeness and converse laws, and the order of work |
| [03](03-examples.md) | Examples | One generated example per linguistic case, per rule, and per alignment quadrant |
| [05](05-modelling-review.md) | Review brief | How to review this as a model rather than as a set of claims |
| [06](06-two-texts.md) | The two texts | What the mushaf writes against what recitation writes, and every transformation between them |
| [07](07-rules.md) | Rules | Every rule with its source, trigger and host, the teaching labels, and where a letter and a sound relate to a rule differently |
| [08](08-legacy-parity.md) | Legacy parity | The shipped per-character cell schema read column by column against the contract |

Scope: Uthmani, Hafs. IndoPak is deferred and nothing here depends on it.

Assumes [03-canonical-vocabulary](../03-canonical-vocabulary.md) resolved.

The one-paragraph version: four of the five legacy projections were four
traversals of a join the old model could not hold, so each recomputed
relationships from rule names and lost a different set; the fifth rebuilt
recited Arabic from rule names for the same reason. The layered model is the
join. `PhonemizeResult` publishes its ordered node arrays and its typed
spelling, attribution and modifier edges, over the written text and the
recited one alike. `phonemes` stays a method because the token stream and the
graph version at different rates.
