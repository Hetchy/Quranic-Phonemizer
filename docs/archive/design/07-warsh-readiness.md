# 07 - What must exist before a Warsh inventory can be written

> **Superseded.** Carried forward whole into
> [design question 08](../../design/08-what-a-second-riwayah-decides.md),
> which asks its blocking question once for the three documents that
> stalled on it. Nothing here landed in code.

Status: **superseded**. Audit: "Riwayah". Evidence:
`warsh-script-codepoint-audit.md` and PR #37.

## The claim to test

The Hafs work produced a pattern: two scripts, one Score, and a gate that
proves they meet. The bet is that most of that transfers to a second riwayah.

Most of it does. Two parts do not, and one of them is a gate that would give a
false answer if anyone ran it.

## What transfers unchanged

- The layering. A Warsh Score is a Score.
- The Ledger, for facts no rule over canonical context can reach.
- The khilaf mechanism, once [06](../../design/06-seen-sad-khilaf.md) has generalised it
  past Hafs-shaped sections.
- The composition root: a Warsh package is one row in `api.PACKAGES`.
- Two-scripts-one-Score as a gate, **within** Warsh.

## What does not: the inventory is one scalar at a time

`Inventory` maps `dict[str, LetterEntry | MarkEntry]`. One character, one
entry. The codepoint audit records at least four Warsh facts that shape cannot
express:

- Warsh has no `U+0671`. Wasl is a multi-scalar sequence, not a glyph that
  declares its own onset the way Uthmani's `ٱ` does.
- `U+06EA`, `U+06EC` and `U+06DF` are sequence-dependent: what each supplies
  depends on its neighbours, not on the scalar.
- Tanween composes a haraka with a small meem -- two scalars, one fact.
- Several marks that are per-scalar in Hafs are positional in Warsh.

A declarative sequence layer belongs in `orthography/`, its table in
`riwayat/warsh/`. The design content is what a match is allowed to look at:

| scope | expresses | risk |
|---|---|---|
| fixed-width neighbours | tanween composition, most of `06EA`/`06EC` | may not reach wasl |
| within-cluster | anything on one base | wasl spans bases |
| within-word | everything audited | a pattern language, and pattern languages grow |

The narrowest scope that covers the audited cases is the right answer, and
"the audited cases" is the thing to establish. It is also the constraint on
[01](01-mark-semantics.md): if capabilities attach to a match rather than a
scalar, shape C in that document is wrong.

## What does not: cross-riwayah parity is invalid as a gate

A riwayah is precisely a reading whose Score may differ. Comparing Hafs and
Warsh output and requiring agreement tests for the absence of the thing being
built. Anyone reaching for the existing parity harness on a Warsh corpus would
get a number, and the number would mean nothing.

Stated here because the harness is sitting there and it is the obvious next
thing to point at.

## The replacement: a per-riwayah conformance harness

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
4. **Hint agreement.** Source marks must never *drive* a rule -- they witness
   it. Same direction as today's attestation gate.
5. **Certified differential alignment.** Where a Warsh site aligns with a Hafs
   one, the difference falls into one of the five classes the codepoint audit
   names. An unclassified difference is a finding, not a failure. This is what
   people reach for parity wanting, stated so it is sound.
6. **Internal completeness.** Every rule in the Warsh `RuleSet` fires at least
   once over the corpus. A rule that never fires is unreviewed.

## Corpus intake

The Warsh text in PR #37 arrives from outside and will need normalisation.
Whatever transform is applied has to be a checked manifest -- input hash,
transform, output hash -- not a one-off script, or the corpus becomes
unreproducible on the day someone asks where a codepoint went.

## Ordering

1. Sequence layer scope decided (blocks the inventory).
2. Intake with a manifest (blocks everything).
3. Checks 1 and 2 (cheap, immediate, catch most intake errors).
4. Rule matrix (long, parallel with the above).
5. Checks 3 to 6.

## What makes this wrong

If the sequence layer turns out to need within-word matching, it is a pattern
language, and a pattern language in a data file is a rule engine wearing a
schema -- the exact thing the Ledger was scoped to avoid. Should the audit in
step 1 land there, stop and reconsider: some of those facts may belong in a
Warsh derivation in code rather than in the inventory.

## Acceptance

- A Warsh inventory can be written without editing `orthography/`.
- No gate compares Hafs output to Warsh output.
- Every Warsh corpus file has a manifest naming its source and transform.
