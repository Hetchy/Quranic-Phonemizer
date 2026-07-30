# 04 - Open questions

Status: **open**. Each needs an owner decision before the part of the contract
it touches can be built. None blocks the rest.

## 1. Can the contract say a merged-away consonant is heavy?

A recolour aimed at a part that another rule merges away has no sound to
attach to, so the rule instance owns no attribution and no modifier edge.
Where the host already carries the same colour nothing is lost. Where it does
not, a teaching fact disappears.

This is the same gap as the heavy ghunnah of an ikhfaa before an istilaa
letter: a colour the domain asserts and the model has no sound to hang it on.
Two symptoms, one cause.

Either the recolour is not minted when its part is already merged away, which
removes a concept and loses the fact; or a modifier edge may name a merged
sound, which keeps the fact and reopens what "applied" means in the gate.

## 2. What does a recited row point back to?

Under `text="recited"` a row's glyphs index `rendered`, and each rendered
glyph names its source glyph where one exists. Whether a row should also carry
the source glyphs directly is a convenience question, and the example matrix
in [03-examples](03-examples.md) is what answers it: if every case reads
cleanly through `from_glyph`, the second list is redundant.

## 3. How does a muqattaat letter cluster?

One glyph spells several units. Under `grouping="cluster"` that is one row
owning the sounds of a whole letter name, which is legal and may be the wrong
granularity for a consumer animating within the name. Splitting it would mean
a cluster that is not a font cluster, which is the thing the grouping is named
for.

## 4. Do alignment rows need a durable identity?

Rows are request-local, and the document says so. A shipped consumer persists
records against cell position and defends against drift with a content
snapshot. That is the right shape for content that genuinely changes, so the
contract probably should not add a key - but it should be explicit that it
never will, because the one consumer that needed otherwise already built the
workaround.

## 5. Which family do the pausal rules belong to?

`pausal_sukun` and `taa_marbuta_pausal` are new, and the family and phase
tables must be total. `elision` fits the first. The second changes a letter's
realization rather than removing it, and no existing family names that.

## 6. What is the authoritative source for every sakt site?

The riwayah's sakt data is short of what Hafs requires, and the missing site
is absent because its cross-script skeleton is unresolved rather than because
it does not exist. The gate's converse law for sakt cannot be total until the
source fact is chosen.

## 7. Two names

**`Unit`** is content-free, and every alternative is worse: `Letter` is what a
consumer reaches for and is wrong for the tanween noon.

**`Mappings`** is settled, and re-raised only because a plural noun for one
document reads like a bag. `Reading` and `Recitation` are both taken.
