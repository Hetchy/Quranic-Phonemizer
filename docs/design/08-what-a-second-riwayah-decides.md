# 08 - What a second riwayah decides, and what waits on it

Status: **open**. Replaces 01, 04 and 07, whose Warsh-agnostic halves landed as
[ADR-010](../adr/010-constants-that-restate-data.md). Audit: "Riwayah", "Data
versus code". Evidence: `research/evidence/warsh-script-codepoint-audit.md`
and PR #37.

## One question, three documents

01 asked whether a script inventory hands downstream code a typed fact or a
string. 04 asked what a data file must say about itself. 07 asked what must
exist before a Warsh inventory can be written. They were three documents
because they were written from three sections of the audit, and each stalled at
the same place:

> **Does a script fact attach to a scalar, or to a match?**

`Inventory` maps one character to one entry. Every capability the loader knows
— `onset`, `dagger_host`, `bare_rasm`, `rasm_only`, and now `seat` — is a
property of a single scalar, and that is sufficient for both Hafs scripts. The
codepoint audit records four Warsh facts it cannot express:

- Warsh has no `U+0671`. Wasl is a multi-scalar sequence, not a glyph that
  declares its own onset the way Uthmani's `ٱ` does.
- `U+06EA`, `U+06EC` and `U+06DF` are sequence-dependent: what each supplies
  depends on its neighbours, not on the scalar.
- Tanween composes a haraka with a small meem — two scalars, one fact.
- Several marks that are per-scalar in Hafs are positional in Warsh.

Answer that, and 01's shape C is either right or wasted; 04's inheritance
question knows what a riwayah is overriding; 07's inventory can be written.
Answer anything else first and it may have to be redone.

## The sequence layer

A declarative sequence layer belongs in `orthography/`, its table in
`riwayat/warsh/`. The design content is what a match may look at:

| scope | expresses | risk |
|---|---|---|
| fixed-width neighbours | tanween composition, most of `06EA`/`06EC` | may not reach wasl |
| within-cluster | anything on one base | wasl spans bases |
| within-word | everything audited | a pattern language, and pattern languages grow |

The narrowest scope that covers the audited cases is the right answer, and
"the audited cases" is the thing to establish.

**What makes this wrong.** If it needs within-word matching, it is a pattern
language, and a pattern language in a data file is a rule engine wearing a
schema — the exact thing the Ledger was scoped to avoid. Should the audit land
there, stop: some of those facts belong in a Warsh derivation in code rather
than in the inventory.

## What waits on the answer

### Mark semantics (was 01)

`Mark` carries `char`, `offset` and `role: str`. The loader parses which
`SlotFact` a mark supplies, what value, and which derivation it defers to, then
keeps only the string.

The census, as it stands after ADR-010 — the earlier one counted
`mark.role ==` comparisons, which are now three and all inside `orthography/`:

| what | where |
|---|---|
| 16 `has()` calls with literal roles | `derive/wasl.py`, `derive/lexeme.py`, `derive/length.py` |
| `HARAKAT` | `canon/spell.py:22` |
| `VOWEL_ROLES` | `derive/wasl.py:16` and `derive/length.py:23` — same name, different value, sibling modules |
| `QUIESCENT_BLOCKERS`, `_VOWEL_ROLES`, `CROSS_WORD_ROLE`, `DAGGER` | `derive/wasl.py`, `canon/build.py`, `derive/tanween.py`, `orthography/cluster.py` |
| `_SHORT_ROLE` | `orthography/write.py:23`, a `Quality` mapped back to the role that writes it |

`role-vocabulary` now checks every one of these against what a derivation or an
inventory declares, so none of them can be misspelled. That is a floor, not the
fix: they are still a second semantic API recovered by string comparison.

**A.** Typed fields on `Mark`: `fact`, `value`, `derivation`, with `role` as
diagnostic text. Cheapest — the loader stops discarding — but leaves `HARAKAT`,
which asks whether a cluster has a vowel of its own, as a set membership test
rather than a query.

**B.** Typed queries on `Cluster`. The consumers do not want marks, they want
answers. `derive/wasl.py` is the test case: if its questions do not reduce to a
small closed set, this shape is wrong.

A and B are not exclusive; B is the likely surface and A the mechanism under it.
Neither can be sized until the sequence layer is settled, because a question
answered from a match is not a question `Cluster` can answer.

**To audit before deciding.** Every one of the 16 sites written as the question
it is really asking. Two sites asking the same question in different words are
one query, and the count of distinct queries is the size of shape B.

### `requires` as a description rather than a proxy

ADR-010 records why the role check is a union: `requires` over-declares
massively. `hamzat_wasl` names thirteen roles and reads none of them; the
thirteen belong to `wasl.is_wasl`, which `canon.build` calls directly.

Making `requires` true would let the check become per derivation, which is
strictly stronger. It is here rather than done because `cross_word_noon` shows
it is not mechanical: that derivation declares nothing on purpose, since
requiring IndoPak's convention would reject Uthmani for not writing something
Uthmani does not write. `derive/tanween.py:52-57` states the deeper problem —
`build._split_tanween_words` greps the role name, so a script fact decides a
canonical question — and its own fix, which is for the derivation to return the
slot rather than for the builder to look for the mark.

### `ALWAYS_RUN` and `SCRIPT_OPTIONAL`

Two frozensets in `orthography/inventory.py` that patch the contract check
because it has no way to ask a derivation whether it runs unconditionally, or
whether a role is one script's convention.

`ALWAYS_RUN` is the three derivations `canon.build` names itself. Whether "runs
even when no inventory names it" can be declared at registration is checkable
today and is the smaller half.

`SCRIPT_OPTIONAL` is not. Its four names are `silah_waw`, `silah_ya`,
`small_waw`, `small_ya`, and the audit's proposed replacement is semantic
alternative groups — a script must declare *one of* these, not *any subset*.
That reading is checkable and the current one is not, but with two inventories
both readings fit the data. A third is what tells them apart. Note also that
`small_waw` and `small_ya` are inert: no `requires` names either, so the
subtraction never reaches them.

### `data/shared/rules.yaml` inheritance (was 04)

A riwayah overrides the shared file one top-level key at a time; an omitted key
is inherited silently. For Hafs that is correct — Hafs overrides nothing and
the shared file *is* Hafs research. For Warsh an unwritten key and a
deliberately identical key are indistinguishable in the file.

Options: require each riwayah to state `inherits: [families]`; or require every
family present and allow the value `shared`. Both make silence an error; the
second needs no new vocabulary.

**The research this waits on**, and it is research rather than engineering:
`data/shared/rules.yaml` family by family, marked riwayah-invariant or
Hafs-specific, with a source. Until that exists, "inherit" has no meaning to
implement. `data/shared/morphology.yaml` is the first file placed on the
invariant side deliberately, and it is a small one.

## The Warsh work itself (was 07)

### What transfers unchanged

The layering — a Warsh Score is a Score. The Ledger, for facts no rule over
canonical context can reach. The khilaf mechanism, once
[06](06-seen-sad-khilaf.md) has generalised it past Hafs-shaped sections. The
composition root: a Warsh package is one row in `api.PACKAGES`. And
two-scripts-one-Score as a gate, **within** Warsh.

### Cross-riwayah parity is invalid as a gate

A riwayah is precisely a reading whose Score may differ. Comparing Hafs and
Warsh output and requiring agreement tests for the absence of the thing being
built. Anyone reaching for the existing parity harness on a Warsh corpus would
get a number, and the number would mean nothing.

Stated here because the harness is sitting there and it is the obvious next
thing to point at.

### The replacement: a per-riwayah conformance harness

Six checks, none of which compares two riwayat:

1. **Intake closure.** Every scalar in the corpus is classified by the
   inventory. Fails loudly on an unaudited codepoint.
2. **Inscription-Score closure.** Every grapheme reaches a slot or is
   structural; every slot has a written source or a Ledger citation.
3. **A reviewed rule matrix as the local oracle.** Warsh has no legacy
   implementation to regress against, so the oracle has to be authored: a
   matrix of rule against context with the expected outcome, reviewed against
   sources before any code runs. This is the largest single piece of work on
   this list and it is research, not engineering.
4. **Hint agreement.** Source marks must never *drive* a rule — they witness
   it. Same direction as today's attestation gate.
5. **Certified differential alignment.** Where a Warsh site aligns with a Hafs
   one, the difference falls into one of the five classes the codepoint audit
   names. An unclassified difference is a finding, not a failure. This is what
   people reach for parity wanting, stated so it is sound.
6. **Internal completeness.** Every rule in the Warsh `RuleSet` fires at least
   once over the corpus. A rule that never fires is unreviewed.

### Corpus intake

The Warsh text in PR #37 arrives from outside and will need normalisation.
Whatever transform is applied has to be a checked manifest — input hash,
transform, output hash — not a one-off script, or the corpus becomes
unreproducible on the day someone asks where a codepoint went.

## Ordering

1. Sequence layer scope decided. Blocks the inventory, and blocks shapes A
   and B above.
2. Intake with a manifest. Blocks everything.
3. Checks 1 and 2 — cheap, immediate, catch most intake errors.
4. Rule matrix. Long, and parallel with the above.
5. Which rule families are riwayah-invariant. Gates the inheritance decision;
   also parallel.
6. Checks 3 to 6, and `SCRIPT_OPTIONAL`, which a third inventory makes
   decidable.

## Acceptance

- A Warsh inventory can be written without editing `orthography/`.
- No gate compares Hafs output to Warsh output.
- Every Warsh corpus file has a manifest naming its source and transform.
- No module outside `orthography/` names a role at all, rather than merely
  naming one that exists.
- `HARAKAT`, `_SHORT_ROLE`, both `VOWEL_ROLES`, `ALWAYS_RUN` and
  `SCRIPT_OPTIONAL` are gone from source.
- A riwayah that omits a rule family fails to load with a message naming it.
