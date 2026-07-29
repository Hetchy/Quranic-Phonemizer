# ADR-010: A constant that restates a data file becomes the data, or a check against it

Status: **accepted**. Closes the Warsh-agnostic half of open design questions
01 and 04. Audit: "Data versus code", and "Enforcement".

## Context

Five findings sat in two design documents, and they read as five chores. They
are one shape. Each is a Python constant that restates something a data file
already says, or enforces a data rule from the wrong place:

| constant | what it restated | disposition |
|---|---|---|
| `cluster.SEATABLE` | which glyphs of Hafs a hamza may rest on | data: a `seat:` capability per scalar |
| role literals | inventory role names, 14 of them | a check: `role-vocabulary` |
| `lexicon.CLITIC_PRONOUNS` | Arabic's attached pronouns | data: `data/shared/morphology.yaml` |
| `lexicon.BUDGETS` | a ceiling per lexicon section | data: `budget:`, checked by a test |
| lexicon section names | the sections of `lexicon.yaml` | data: one `sections:` mapping |

The common failure is that neither copy knows about the other. A frozenset of
four glyphs cannot be wrong about Hafs, but it cannot be right about Warsh
either, and nothing would say so. A role name misspelled in Python read
`False` and changed output silently, which is exactly what `requires` was
introduced to prevent and never actually did.

## Decision

**A constant that restates data becomes the data.** A seat is a capability the
script declares, beside `onset`, `dagger_host`, `bare_rasm` and `rasm_only` —
which is a route the inventory already had. The clitic pronouns are Arabic and
go to `data/shared/`, not under `hafs/`, which would assert something false
about every other riwayah. A lexicon section states its own match mode and its
own ceiling.

**A constant that cannot become data becomes a check against it.** The role
names in code are code — they are what a derivation reads. So they are checked:
`structure_lint`'s new `role-vocabulary` collects every string the package
hands to a role lookup and requires each to be a role some derivation declares
or some inventory writes.

**What is enforced at load, and what at a gate.** A fact the package cannot
run without stays a load error: an unknown capability, an unknown match mode, a
duplicate entry. A ceiling is a conformance concern and moves to a test, where
a breach is a red build naming the section, its size and its ceiling — not a
package that will not import.

### Why the role check is a union and not per derivation

The obvious check is that each `has()` call reads a subset of its derivation's
`requires`. That check would be a lie. `requires` is not a description of what
a body reads:

- `hamzat_wasl` declares thirteen roles and its body is `del context; return
  Sets(...)`. The thirteen belong to `wasl.is_wasl`, which `canon.build` calls
  directly rather than through `resolve()`.
- `pausal_length` declares nine and reads none. `carrier` declares ten, reads one.
- Five `has()` sites in `derive/lexeme.py` sit in no registered derivation at
  all. They pass only because `ALWAYS_RUN` drags in `carrier`'s over-broad set;
  tightening `carrier` to what it reads would leave them undeclared and silent.
- `juncture.py`, `spell.py`, `build.py` and `cluster.py` read role literals from
  outside `canon/derive/` entirely.

So the claim that is true today is the union: every role named in code is a
role something declares. With the existing load-time contract check, which runs
the other way — every role a named derivation requires is one the script writes
— a one-character slip now fails on whichever side it is made.

Tightening `requires` into a real description is worth doing and is not this
decision. It is in design question 08, because `cross_word_noon` shows why it
is not mechanical: the derivation deliberately declares nothing, since
requiring IndoPak's convention would reject Uthmani for not writing something
Uthmani does not write.

### What this deliberately does not decide

Everything in 01 and 04 that turns on a second riwayah is untouched and now
lives in [08](../design/08-what-a-second-riwayah-decides.md):

- **Shape A and shape B for mark semantics** — whether `Mark` carries typed
  `fact`/`value`/`derivation`, or `Cluster` answers typed questions. `seat` is
  shape C for one base-scalar capability, which is safe because a seat is a
  property of a glyph in any script. Whether a *mark's* meaning is per-scalar is
  the question 07 says may have a different answer in Warsh.
- **`ALWAYS_RUN` and `SCRIPT_OPTIONAL`** — both are patches over the contract
  check, and `SCRIPT_OPTIONAL`'s replacement, semantic alternative groups, needs
  a third inventory to be checkable at all.
- **`data/shared/rules.yaml` inheritance** — blocked on research into which
  rule families are riwayah-invariant.

Two items leave the open list instead of moving to 08:

- **`schema_version` is per file.** `render/ipa.yaml` went to 2 in ADR-009 and
  no other loader had to move; `lexicon.yaml` goes to 2 here and the other six
  stay at 1. That is the evidence design question 04 asked for, and it argues
  against one package-wide data version. A bump obliges exactly one thing: the
  loader for that file rejects the old shape with a message naming both versions.
- **`comment_lint`'s 84 ungrouped comment blocks** are a tooling chore, not a
  design question. Recorded here so the backlog is not lost, and out of
  `docs/design/` either way.

## Rejected: leave `SEATABLE` alone until the Warsh sequence layer is settled

The safest reading of design question 01 is that shape C should wait, because a
capability that turns out to attach to a match rather than a scalar makes the
schema change wasted. Rejected for `seat` specifically: the four inventory
capabilities that already exist are per-scalar and have not been questioned, a
seat is the same kind of fact — a property of how a glyph is drawn — and if
Warsh needs a sequence-scoped capability it needs one whether or not `seat` is
already a flag. The argument holds for mark semantics, which is why those stay
open.

## Evidence

No output moves. All eight gates read exactly as they did before the change —
cross 99.997/100.000, regression 99.928/97.674, roundtrip 100.000, attest
178/239, l1 18 — and the two parity gates render every word of the Quran
through both the seat branch and the lexicon.

Three falsifiers were run by hand and each failed as it should: a role
misspelled in Python is named by `role-vocabulary` at its line; a scalar whose
script does not call it a seat stops folding a combining hamza; a section over
its ceiling fails `tests/test_lexicon.py` with both numbers.

The lexicon had no tests at all before this. It has fifteen.
