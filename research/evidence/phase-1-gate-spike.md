# Phase-1 gate, run as a spike

A throwaway implementation of both adapters, `canon.build`, a derivation
registry and the L1 comparator, run over the full 6,236 verses × 2 scripts.
Code is scratch-only and is not proposed for the repository. The point was to
find out whether ADR-008 §5's phase-1 gate is reachable, and what it costs.

## Result

**163 of 77,433 words disagree — 99.79%.** Every remaining row is nameable;
none needs a vocabulary member the ADRs do not already have.

| n | class |
|---:|---|
| 44 | per-site, Ledger material |
| 34 | tanwīn split across a word boundary (needs verse scope) |
| 27 | ṣilah / long-ī mark polysemy |
| 26 | muqaṭṭaʿāt — spelling expansion not implemented in the spike |
| 22 | tanwīn written in one script only (pausal spelling, **not** a split) |
| 6 | marked colouring (imāla / ishmām / tashīl) |
| 3 | final-mīm helper vowel written in Uthmani only |
| 1 | pausal long |

Derivation classes implemented, in the order they paid: hamzat al-waṣl
(article rule + skeleton lexicon), length carriers and the rasm hosts, the
Allah lexeme, tanwīn as two slots, the otiose alef and the otiose wāw, the
seat/dagger split, the ṣilah-mark polysemy fold.

## What the run confirms

- **The canonical vocabulary is sufficient.** No residue row required a
  `Nucleus`, `Onset` or `CanonLetter` member that does not exist. This is the
  strongest single result: the Slot model survives contact with a second
  orthography.
- **A1 holds.** Tanwīn as base slot + `(NOON, PLAIN, Silent)` produced no
  friction, and it is what makes IndoPak's `ࣙ` an ordinary `Evidences` row.
- **`Nucleus.Silent` collapsing bare-vs-sukūn is free**, exactly as claimed —
  37,148 Uthmani sukūns against 62,383 IndoPak ones and zero residue from it.
- **Verse scope is load-bearing, not hygiene.** 34 sites are unresolvable
  word-scoped.
- **ADR-003 §6.1 reproduces independently.** Measured: 13,483 waṣl sites, the
  article rule covers **11,994** (ADR says 11,995), residue **1,489 over 575
  skeletons** (ADR says 1,487 / 526).

## What the run contradicts or adds

**1. The waṣl lexicon has no head.** §6.1 presents "526 distinct skeletons" as
a reduction. Measured, **95% of the residue sites need 501 of the 575
skeletons** — a flat lexicon, no Pareto tail. ADR-008 §4's "~50 uncited
`Supply` entries" budget governs the Ledger and says nothing about this. The
derivation side needs its own declared budget (~575 waṣl skeletons + ADR-003
§6.4's ~169 ṣilah exemptions), stated before implementation.

**2. A sixth polysemous mark — and it is the one fixture 13 rests on.**
Uthmani U+06E7, 39 sites: `Onset.SILAH` at 27:36:8 per ADR-001 §3.5, and an
ordinary long ī at the other ~38 (`إِبْرَٰهِـۧمَ`, `ٱلنَّبِيِّـۧنَ`). Same for U+06E6
and IndoPak U+0656. ADR-001 §3.5 treats U+06E7 as if it monosemously marked
ṣilah. It needs §6.6's treatment: justified per site class, not per scalar.

**3. §4.1's attestation rule is stated positionally and should be canonical.**
Word-initial shadda is not the only attesting shadda: 5:28:2 `بَسَطْتَ` /
`بَسَطْتَّ` writes one IndoPak-only, attesting idghām mutajānisayn word-
internally. The rule that made L1 work is **a shadda on a slot whose preceding
slot is `Silent` attests `ASSIMILATION` and is not `Onset.GEMINATE`** — which
subsumes the word-initial case and is expressed in Score terms rather than
glyph positions. Recommend replacing the §4.1 formulation with it.

**4. Uthmani writes a performance fact, and no ADR row covers it.** At
`ذَٰلِكُمُ ۗ`, `بَيْنَكُمُ ۖ`, `أَنفُسَكُمُ ۖ`, `تَعْلَمُونَهُمُ`, `أَبْنَآءَهُمُ ۘ` Uthmani writes a
damma or kasra on the final mīm where IndoPak writes sukūn. That vowel is the
iltiqāʾ helper — a `BOUNDARY` outcome. Under L2 it is an `Evidences` row that
contradicts the canonical `Silent`, so the Uthmani inventory must declare it
`Inert`. ADR-003 §6's table has no row for it. Seven sites, but it is exactly
the "a present glyph asserts a performance fact" case the boundary exists to
catch, and it is currently unhandled — the same shape as the `noon_tanween.py:17`
bug class, arriving from the data side instead.

**5. The 55-word tanwīn class is two classes, not one.** §6.5 folds them into
"split across a boundary". Measured: **34 are splits** (the `ࣙ` sites) and
**22 are IndoPak simply omitting the tanwīn** at a pausal position with no
compensation anywhere (`قَدِيرٌ`/`قَدِيْرُ`, `جَمِيعًا`/`جَمِيْعَا`, `شَدِيدٍ`/`شَدِيْدِ`).
Different derivations; only the first needs verse scope.

**6. The article rule must accept a shadda'd lām** (`الَّذي`, `الَّتي`). The
"lām with sukūn" formulation misses 45 sites, where IndoPak's explicit fatha
then contradicts the derived kasra — a residue row produced by the derivation
being too narrow, which is the failure mode R9 clause 4 is meant to catch.

## What this run does *not* discharge

It is not the ADR design. There is no Ledger, no `Supply`/`Assert` split, and
**no provenance or `Inert` accounting** — ADR-008 §3.1's anti-gaming guard is
precisely what was not implemented. Two residue classes were in fact dissolved
by declaring a grapheme inert (the tatweel seat, and the final-mīm vowel above),
which is the unguarded route §3.1 names.

More seriously: **the waṣl skeleton lexicon was learned from Uthmani's own
U+0671 positions.** That drives the residue to zero by relocating the fact into
a shared table, exactly as §3.1 warns. It is legitimate only if those 575
skeletons are independently justifiable as Arabic morphology, which this run
did not check. That check — not the residue count — is the real phase-1 gate.

## Recommendation

The gate is reachable and worth keeping as a hard gate. Before implementation,
declare two numbers and hold the build to them:

- **derivation budget**: ~575 waṣl skeletons, ~169 ṣilah exemptions, and a
  named ceiling for anything else;
- **`Inert` budget per script**, since that is the one route §3.1 leaves open
  and this run used it twice without noticing.
