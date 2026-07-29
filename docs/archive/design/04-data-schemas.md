# 04 - What a data file must say about itself

> **Superseded.** The lexicon sections, the budgets and the clitic pronouns
> landed as [ADR-010](../../adr/010-constants-that-restate-data.md), which
> also closes `schema_version` and rehomes the `comment_lint` chore. The
> `rules.yaml` inheritance question moved to
> [design question 08](../../design/08-what-a-second-riwayah-decides.md).

Status: **superseded**. Audit: "Data versus code", last three bullets, and
"Enforcement".

## The pattern behind all of it

`require_keys` proves a key is *whitelisted*. It never proves anything reads
it. Three findings in the July audit were the same defect wearing different
names, and all three have landed: the ledger's `riwayah` was required and
never parsed, `Assert.value` was parsed and never compared, `polysemous` was
validated and never consulted.

What is left is the general question those three were instances of: **what
must a file declare, and what proves the declaration is load-bearing?**

## Four open items

### `lexicon.yaml` sections

Seven sections. Each has its name hardcoded in `canon/lexicon.py`, its
matching mode (exact, prefix, suffix, proclitic-stripped) implemented in a
separate method, and its size ceiling in a `BUDGETS` dict at module scope.
Adding a section means editing three places in source, and nothing connects
the three.

The shape that removes all three edits:

```yaml
sections:
  wasl_particles:  {match: exact,  entries: [...]}
  form_eight_lam:  {match: prefix, entries: [...]}
```

with `MatchMode` a closed enum in source -- the modes are code, the sections
are data.

Two sub-decisions:

- **`CLITIC_PRONOUNS`** (`canon/lexicon.py:29`) is twelve Arabic strings in a
  `.py`. It is Arabic data and belongs in YAML. Open only in that the pronoun
  set may be riwayah-invariant, in which case it belongs in `data/shared/`
  rather than under `hafs/`.
- **`BUDGETS`** is a conformance concern -- "this list must not grow
  unbounded" -- being enforced during loading. It belongs in a gate, where a
  breach is a reviewable failure rather than an import-time exception.

### `data/shared/rules.yaml` inheritance

A riwayah overrides the shared file one top-level key at a time; an omitted
key is inherited silently. For Hafs that is correct -- Hafs overrides nothing
and the shared file *is* Hafs research. For Warsh it means an unwritten key
and a deliberately-identical key are indistinguishable in the file.

Options: require each riwayah to state `inherits: [families]` explicitly; or
require every family present and allow the value `shared`. Both make silence
an error. The second is more verbose and needs no new vocabulary.

Sub-question this forces: the shared file currently holds *Hafs* research
labelled as riwayah-independent fact. Establish which families genuinely are
invariant across riwayat before deciding what "inherit" means.

### `schema_version`

Checked by seven loaders. No version 2, no migration path, no second
consumer, no reader outside the package. It is a promise nothing has had to
keep.

Options: keep it as cheap insurance and accept the ceremony; delete it and
reintroduce per-file when a real second version appears; or keep the field
but state in one place what a version bump obliges. The middle option is
tempting and probably wrong -- the field costs nothing and reintroducing it
across seven schemas later costs a coordinated change.

The real question is narrower: **should the version be per-file or one package
data version?** Seven independent counters that have all stayed at 1 suggest
one.

### `comment_lint` coverage

Budgets docstrings, never groups adjacent `#` lines. 84 multi-line comment
blocks holding 213 lines are invisible to it and it reports zero problems.

Teaching it to group is small. The work is the 84 blocks it then fails on, and
that work is not mechanical: some of those blocks are the narration the policy
bans, and some are single explanations that legitimately need two lines.

Two of the seven policy classes -- whether a comment explains a non-obvious
*why*, and narration as a semantic category -- are not reliably scriptable and
stay review-owned. The other five can be tightened. Decide which five, and
whether the 84 blocks are fixed before or after the checker lands.

## What to audit before deciding

1. **Every `require_keys` call**, and for each key, the line that reads it. A
   key with no reader is either the next `polysemous` or an undocumented
   contract with a consumer outside the repo.
2. **The seven `schema_version` constants**, and whether any file has ever
   needed to differ from the others.
3. **`data/shared/rules.yaml` family by family**, marked riwayah-invariant or
   Hafs-specific, with a source. This is research, not engineering, and it
   gates the inheritance decision.
4. **The 84 comment blocks**, classified: narration to delete, explanation to
   compress, explanation that genuinely needs two lines. The third class sets
   the budget.

## Acceptance

- Adding a lexicon section is a YAML edit.
- No Arabic data in a `.py`.
- Size ceilings are a gate, not a load-time exception.
- A riwayah that omits a rule family fails to load with a message naming the
  family.
- `structure_lint` gains an `orphan-data` check: a declared key with no reader
  is an error.
