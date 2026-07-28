# 01 - What a script inventory hands downstream

Status: **open**. Audit: "Data versus code", first four bullets.

## The choice

`Mark` carries `char`, `offset` and `role: str`. The inventory loader parsed
more than that -- which `SlotFact` the mark supplies, what value, which
derivation it defers to -- and then kept only the string. Every consumer
recovers the meaning by comparing that string against a constant it declares
itself.

The question is not whether to fix this. It is **where the second copy goes
when it stops being a string**: into `Mark`, into `Cluster`, or into neither
because the consumer should have been asking a different question.

## Census, at `riwayah/inert-validators`

Literal role comparisons, by file:

| file | sites |
|---|---|
| `canon/derive/wasl.py` | 9 |
| `canon/derive/lexeme.py` | 5 |
| `orthography/write.py` | 2 |
| `canon/derive/length.py` | 2 |

Plus the constant sets that exist only to name roles: `canon/spell.py:22`
`HARAKAT`, `orthography/cluster.py:14` `DAGGER` and `:18` `SEATABLE`, and
`orthography/write.py:23` `_SHORT_ROLE` mapping a `Quality` back to the role
name that writes it.

`orthography/inventory.py:43` `ALWAYS_RUN` and `:48` `SCRIPT_OPTIONAL` belong
to the same family: two frozensets of role and derivation names that patch the
contract check, because the check has no way to ask a derivation whether it
runs unconditionally or whether a role is one script's convention.

## Three shapes, and what each costs

### A. Typed fields on `Mark`

`Mark` grows `fact: SlotFact | None`, `value: object | None`,
`derivation: str | None` -- exactly what the loader already parsed. `role`
survives as diagnostic text only.

Cheapest to reach: the loader stops discarding. But it does not remove
`SEATABLE` or `DAGGER`, which are facts about a *base* scalar, not a mark, and
it leaves `HARAKAT` -- "does this cluster carry any short vowel" -- as a set
membership test rather than a query.

### B. Typed queries on `Cluster`

The consumers do not want marks. They want answers: *does this cluster have a
vowel of its own*, *is this base a seat*, *does a dagger lengthen the previous
slot*. Give `Cluster` those methods and the constant sets disappear with the
string comparisons.

Costs more thought: every query added is API surface, and a query nobody can
answer from the inventory alone is a design error that only shows up later.
`canon/derive/wasl.py` at 9 sites is the test case -- if its questions do not
reduce to a small closed set, this shape is wrong.

### C. Capabilities in script YAML

`DAGGER` and `SEATABLE` are orthographic facts. A dagger host and a seat are
properties the *script* declares about a scalar, so they belong in the
inventory file as per-scalar capability flags, not in a Python frozenset that
happens to list the Hafs glyphs.

This is the only shape that survives Warsh unchanged, because Warsh's seats
and carriers are a different set. It is also the only one that requires an
inventory schema change, which means every existing script file is edited.

A, B and C are not exclusive. The likely answer is C for base-scalar
capabilities, B for the questions `canon` asks, and A as the mechanism under
B.

## What to audit before deciding

1. **Enumerate the questions.** Every one of the 18 literal sites, written as
   the question it is really asking. If two sites ask the same question in
   different words, that is one query, and the count of distinct queries is
   the size of shape B.
2. **Classify each as base or mark.** A question about the base scalar is a
   capability (C). A question about what is written on it is a typed field (A).
3. **Check `ALWAYS_RUN` against the registry.** Whether "runs even when no
   inventory names it" is a property the derivation can declare at
   registration. If it is, both frozensets become registry metadata and the
   contract check stops needing exceptions.
4. **Check `SCRIPT_OPTIONAL` against both inventories.** The four names are
   `silah_waw`, `silah_ya`, `small_waw`, `small_ya`. Establish whether these
   are genuinely "one script's convention" or whether they form a semantic
   alternative group -- a script must declare *one of* these, not
   *any subset*. The second reading is checkable; the first is not.

## What makes this decision wrong

If a Warsh capability turns out to be sequence-dependent rather than
per-scalar, shape C cannot express it and the schema change is wasted. See
[07](07-warsh-readiness.md) -- the sequence layer has to be settled first, or
at least settled enough to know whether capabilities attach to a scalar or to
a match.

## Acceptance

- No module outside `orthography/` compares a role string.
- `HARAKAT`, `DAGGER`, `SEATABLE`, `_SHORT_ROLE`, `ALWAYS_RUN` and
  `SCRIPT_OPTIONAL` are gone from source.
- A misspelled role in a script YAML is a load error, not a silent `False`.
- `tools/structure_lint.py` gains a `code-data-duplication` check that fails
  on a new string constant naming an inventory key.
