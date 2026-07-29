# 06 - The seen/sad khilaf

Status: **open**, and the only item on this list that is wrong today.
Audit: "Critical, found alone".

## What exists

`KhilafId.SEEN_SAD` is declared at `model/address.py:126`. Searching the whole
tree for that member or its value `seen_sad` returns exactly one hit: the
declaration. No section in `khilaf.yaml`, no loader branch, no rule, no test.

The sites are decided instead by the script inventories, unconditionally:

```yaml
# uthmani.yaml
"ۜ": {fact: LETTER, cls: annotation, role: seen_over, value: SEEN}
"ۣ": {fact: LETTER, cls: annotation, role: seen_over, value: SEEN}
# indopak.yaml
"ۜ": {fact: LETTER, cls: annotation, role: seen_over, value: SEEN}
```

Two scalars in Uthmani -- a small seen written above (U+06DC) and below
(U+06E3) the sad -- and one in IndoPak. All three declare `LETTER = SEEN`,
so wherever a script writes the mark, the slot reads seen and no selection can
change it.

That is a choice the model is making silently on behalf of the reciter, at
sites where the tradition records two readings.

## Why it is not a data entry

Three complications, in increasing order of how much they constrain the fix.

### The mark is polysemous, and that was load-bearing

The same `ۜ` scalar is the sakt sign at the four sakt sites. `polysemous` used
to record this and was deleted in the July hygiene pass, correctly -- it
recorded the ambiguity and then resolved it in favour of the primary
declaration anyway, so it never deferred. What replaced it is the Ledger: the
three authorable sakt sites are `SAKT` supplies, on the grounds that no rule
over canonical context can separate the two senses.

Any change to how the seen/sad sites are decided has to leave those supplies
intact and must not make the sakt sites selectable.

### The fourth sakt site is unwritable today

18:1:11 has no Ledger row. Its skeleton differs between the scripts -- IndoPak
builds the tanween noon and Uthmani does not, which is one of the 18 L1
residue rows -- so a mandatory `skeleton` cannot match both. Addressing it by
slot ordinal instead would weaken the check that catches ordinal drift.

This is a constraint on the *shape* of the fix: whatever authors these sites
must tolerate a site whose skeleton is not yet script-independent, or must
wait for that L1 row to close.

### The four sites may not share a default

The tradition does not give one answer for all four. Naming a single default
for the khilaf and applying it everywhere would be a different wrong answer
from the current one.

## The shape

A typed `seen_sad` section in `khilaf.yaml`, per site, each with its own
default:

```yaml
seen_sad:
  options: {seen: SEEN, sad: SAD}
  sites:
    <vocalised skeleton>: {default: seen}
```

with three consequences:

1. The canonical khilaf pass must apply a selected `LETTER`. Today the vowel
   khilaf pass applies a `NUCLEUS`; letter selection is a new path.
2. Two evidences supplying a conflicting `LETTER` for one slot must be a
   build error. Today the first wins, which is how the inventory silently
   overrides.
3. The inventory declarations become a deferral -- the mark names the khilaf
   rather than carrying a value -- which is the mechanism
   [08](08-what-a-second-riwayah-decides.md) is deciding the shape of, under
   mark semantics. These two documents are coupled.

## What to audit before deciding

This is research first and engineering second.

1. **The four sites, by location and skeleton.** Both scripts, both Uthmani
   scalars.
2. **The default at each site, with a source.** Shatibiyyah and at least one
   contemporary mushaf convention. Sites that disagree with each other are the
   point of the exercise.
3. **Whether IndoPak writes all four.** Uthmani has two scalars and IndoPak
   one; establish whether that is a notation difference or a coverage
   difference. If IndoPak omits a site, the khilaf is authored canonically and
   both scripts inherit it -- which is the better outcome.
4. **Whether any site is also a sakt site.** Expected no, but the shared
   scalar makes it worth confirming before the two mechanisms are wired to the
   same mark.
5. **What the current output is at each of the four**, so the change is a
   measured diff rather than a hope.

## Acceptance

- `KhilafId.SEEN_SAD` has a section, a loader, a default per site, and a test
  that both wajh are reachable.
- Two evidences supplying a conflicting `LETTER` for one slot raise, naming
  both sources.
- The three sakt supplies are untouched and the sakt sites are not selectable.
- `out/phonemized_v{N+1}/` regenerated, with the four sites named in
  `changes.txt`.
