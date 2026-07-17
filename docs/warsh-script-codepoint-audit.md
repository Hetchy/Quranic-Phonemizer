# Hafs–Warsh source-script audit

Status: corpus audit for the riwāyah refactor, performed 2026-07-16 against
the current Hafs `dev/Quran.json` and PR #37 commit `c25dd0d`.

This is a source-encoding audit, not a claim that Warsh pronunciation rules
have been researched. Its job is to distinguish five things which the old
plan conflated:

1. the same Unicode and the same canonical meaning;
2. different Unicode sequences with the same canonical meaning;
3. an orthographic hint for a rule which should still be derived;
4. a source mark whose meaning depends on its sequence context;
5. a likely riwāyah pronunciation delta which cannot be settled from script
   alone.

The audit compared all word records, counted every scalar, inspected combining
clusters, and aligned 69,137 same-skeleton word pairs per surah after
normalizing only obvious alef and yāʾ families. Alignment is supporting
evidence, not a substitute for a source convention or a recitation reference.

## 1. Intake findings

| Artifact | Finding |
|---|---|
| current Hafs word corpus | 77,433 word slots; 69 distinct codepoints including embedded spaces/formatting |
| PR Warsh word corpus | 77,860 word slots; 63 distinct codepoints |
| PR cleaned verse corpus | 6,214 verses; 65 distinct codepoints, including space and NBSP |
| PR raw verse corpus | 351 distinct codepoints |
| generic PR cleaning | removes 6,228 characters: one font-dependent presentation-form marker per verse plus 14 RLMs; retains 6,648 NBSPs until splitting |

The PR metadata says the cleaned file has 66 distinct codepoints; the committed
file has 65. The transformation is probably removing verse-number glyph hacks,
but `strip_flagged_chars.py` does not encode or prove that fact. The production
pipeline must replace the generated "flagged list means delete" operation with
a checked transformation manifest: source scalar/sequence, count, reason,
expected structural replacement, and before/after hash.

The Warsh word count and address shape also differ from Hafs. Rub-el-hizb is a
standalone word in many Warsh records and attached/space-bearing in Hafs. A
corpus build must decide which source items are lexical word slots before it
assigns `sura:ayah:word`; it must never let a display mark accidentally become
a phonemizer word.

### Direct answer: how much is actually shared?

Of the 63 scalar values present in the selected Warsh word corpus, 57 also
occur in the current Hafs corpus. The six Warsh-only scalars are combining
hamza below (`U+0655`), the three alternate tanween marks (`U+0656/U+0657/
U+065E`), yeh barree (`U+06D2`), and mini mīm above (`U+06E2`). Ordinary
letters and standard harakāt are therefore mostly byte-identical, and many
remaining differences are many-to-one spelling conventions.

That summary must not be shortened to “only count deltas.” Several
high-frequency differences are sequence-semantic:

- Warsh lacks Hafs `U+0671` and spells hamzat al-waṣl with multi-scalar initial
  alef sequences;
- the same `U+06EA/U+06EC/U+06DF` scalar can have a different role by source
  and sequence;
- harakah+mini-mīm creates canonical tanween even though no tanween scalar is
  present;
- shared mini-wāw/maddah scalars include a likely plural-mīm realization
  delta;
- stop/structural attachment changes address and boundary handling.

So the correct implementation conclusion is “mostly shared ordinary
inventory, small scalar delta, important sequence/convention delta,” not a
copied Warsh rule tree and not one universal codepoint map.

## 2. Decisions by representation family

### 2.1 Byte-identical and canonically shared

The ordinary Arabic letters, standard fatha/damma/kasra, shaddah, sukun,
combining hamza above, and most dagger-alef/small-yāʾ uses have the same basic
orthographic role in both sources. They use the shared tokenizer and shared
baseline segment builder. Different corpus counts do not create a rule fork.

This does not mean a codepoint has one universal meaning. The decision applies
to the observed ordinary sequence families, with fixtures. The exceptional
families below take precedence.

### 2.2 Tanween: different bytes, same canonical marks

| Warsh source | Count | Hafs semantic counterpart | Evidence and normalization |
|---|---:|---|---|
| `ٖ` `U+0656` | 1,935 | `ٍ` `U+064D` | 1,490 aligned sites map overwhelmingly to Hafs kasratan. Normalize to `TanweenQuality.KASR`; it is not an imālah mark. |
| `ٗ` `U+0657` | 2,916 | `ً` `U+064B` | occurs mainly on final alef/taa marbuta/maqsurah where Hafs attributes fathatan differently. Normalize to `TanweenQuality.FATH`; preserve source ownership. |
| `ٞ` `U+065E` | 1,815 | `ٌ` `U+064C` | 1,575 aligned sites correspond to Hafs dammatan. Normalize to `TanweenQuality.DAMM`; the Unicode name is not the Qurʾānic function. |

These are script-adapter facts. Nūn/tanwīn rules receive one canonical tanween
value and do not know which source mark supplied it. The grapheme alignment
still points to the exact Warsh mark, so character annotation remains exact.

The alternate marks also appear to carry a **visual rule-class hint**, exactly
the kind of many-to-one encoding the model must preserve without obeying. In a
simple within-ayah next-effective-letter audit:

- all 5,123 non-boundary alternate-mark sites fell into idghām with ghunnah,
  idghām without ghunnah, or ikhfāʾ;
- none fell into iẓhār ḥalqī or iqlāb;
- the remaining 1,543 alternate sites were at the end of the audited ayah,
  where this pass deliberately did not infer a cross-ayah continuation;
- the Warsh source still uses standard tanween marks, especially around
  iẓhār/iqlāb and boundaries; the current Hafs source uses only the standard
  `U+064B/U+064C/U+064D` set.

That distribution is strong evidence for an open/closed or otherwise
rule-indicating visual convention, but the exact conventional label still
needs source documentation. Runtime normalization therefore does this:

```text
`ٍ` or `ٖ` -> TanweenQuality.KASR
`ً` or `ٗ` -> TanweenQuality.FATH
`ٌ` or `ٞ` -> TanweenQuality.DAMM
```

The exact source grapheme already preserves which form was written. Once the
convention is reviewed, the adapter may additionally attach a typed
orthographic hint and validate that the independently derived nūn/tanwīn rule
agrees. The form must never select the rule; the next canonical letter and
boundary context do that.

### 2.3 Hamzat al-waṣl: sequence equivalence, not scalar equivalence

Hafs normally uses `ٱ` `U+0671` (13,483 occurrences). The Warsh word corpus
does not contain that scalar. It uses initial alef plus vowel and one of
several small marks:

| Warsh pattern family | Corpus evidence | Canonical result |
|---|---|---|
| initial `اَ۬/اِ۬/اُ۬` | `۬` occurs 10,055 times; 9,993 are on alef immediately before lam | hamzat al-waṣl with written ibtidāʾ-vowel hint; the article lam remains its own unit |
| initial `اَ۟/اِ۟/اُ۟` | `۟` occurs 281 times, overwhelmingly on initial alef; all 124 aligned examples correspond to Hafs `ٱ` | hamzat al-waṣl in a non-article sequence family |
| initial `اَ۪/اِ۪/اُ۪` | 692 of the 2,569 `۪` occurrences are initial-alef clusters, for example `اُ۪هْدِنَا` | hamzat al-waṣl in another sequence family |

Therefore `U+06EC` is not "fixed hamzat al-qaṭʿ", and `U+06DF` cannot retain
the Hafs-global meaning "silent always" inside the Warsh adapter. The adapter
matches complete source sequences and emits `Letter.HAMZA_WASL` plus a
canonical vowel hint. The shared hamzat-al-waṣl and boundary implementation
then decides whether it sounds.

The minority nonconforming `U+06EC` sequences and every non-initial-alef use
must be committed as reviewed fixtures before the adapter accepts them. There
is no blanket `U+06EC -> HAMZA_WASL` rule.

### 2.4 `U+06EA`: one byte, multiple sequence meanings

The Hafs corpus uses `۪` once, in `مَجْر۪ىٰهَا` (11:41), where today's code
hardcodes the imālah pronunciation. The Warsh corpus uses it 2,569 times:

| Sequence context | Count | Interpretation at this stage |
|---|---:|---|
| initial alef cluster | 692 | hamzat-al-waṣl source convention |
| on a consonant before `ا/ى/ي/ے` | 1,700 | marked vowel-quality family; candidate imālah/taqlīl input |
| same cluster as dagger alef | 145 | marked vowel-quality family |
| other consonant context | 25 | unresolved; fixture and source review required |
| word-final | 7 | unresolved/special-letter context |

This yields two concrete design consequences:

- Hafs 11:41 no longer needs a location-keyed phoneme patch. Its adapter can
  recognize the marked-vowel sequence and its Hafs vowel-quality classifier can
  classify it as `IMALA`.
- Warsh occurrences must not automatically receive that Hafs value. The
  Warsh classifier must decide `IMALA`, `TAQLIL`, or another supported quality from
  reviewed recitation evidence. The source mark is evidence; it is not itself
  a universal Tajweed rule.

The canonical tokenizer may retain a typed `MarkedVowel` input between script
normalization and riwāyah classification. It must not call the mark "silent-letter /
pause indicator" as the PR metadata currently does.

### 2.5 Yāʾ family: different base scalar, same letter unit

Warsh `ے` `U+06D2` occurs 2,996 times. In aligned same-skeleton words, 2,834
instances correspond to Hafs `ى`:

- 2,276 plain `ى -> ے`;
- 274 with the same maddah;
- 217 with the same sukun;
- the remainder differ in attached stop/vowel marks.

Examples include Warsh `فِے` versus Hafs `فِى`, and Warsh `شَےْءٖ` versus
Hafs `شَىْءٍ`. Normalize the observed base to the same canonical yāʾ-family
letter while retaining the exact source base and marks. The 162 unaligned
instances need fixtures; they are not a reason to invent a separate consonant
or phoneme by default.

### 2.6 Orthographic rule hints do not drive rules

Warsh `ۢ` `U+06E2` occurs 575 times and encodes two source conventions:

| Composition | Count | Canonical normalization |
|---|---:|---|
| bare nūn + mini mīm | 270 | nūn sākinah plus `HintKind.IQLAB` |
| fatha + mini mīm | 91 | `TanweenQuality.FATH` plus the hint |
| damma + mini mīm | 123 | `TanweenQuality.DAMM` plus the hint |
| kasra + mini mīm | 91 | `TanweenQuality.KASR` plus the hint |

The harakah+mini-mīm forms are tanween even though they contain no tanween
scalar. The two source graphemes together license one canonical `Tanween`
value. All 270 nūn sites and 292 of 305 composite-tanween sites are followed
by `ب` within the audited ayah; the remaining 13 composites are at an ayah
edge which this pass treated as a boundary. The current Hafs corpus contains
zero small-mīm-above/below scalars, even though the legacy base YAML declares
them.

This selected Warsh source uses only `U+06E2` (small mīm above) and no
`U+06ED` (small mīm below). A future source which uses the below form may map
it to the same composite-tanween/nūn hint only after that source convention is
documented. Vertical placement remains visible in the source grapheme and does
not create a different phonological rule by itself.

The mini mīm is a script hint/validation signal, not a small vowel and not the
rule trigger. The nūn/tanwīn rule still derives iqlāb from the canonical
subject plus following `ب`; otherwise an unmarked corpus or a differently
marked source would change the algorithm. Validation checks that the derived
result agrees with `HintKind.IQLAB`.

The same principle applies to small nūn and other reading aids: preserve and
validate them, but do not turn glyph presence into the pronunciation engine.

#### Current source-convention contract

| Source | Written convention | Canonical value | Hint/ignored policy | Rule decision |
|---|---|---|---|---|
| current Hafs | `ً ٌ ٍ` | tanween fath/damm/kasr | no tanween-rule hint in this corpus | following canonical letter + boundary only |
| current Hafs | bare/explicit-sākin nūn before `ب` | nūn sākinah | no mini-mīm scalar occurs; legacy YAML declaration is unused | context derives iqlāb |
| selected Warsh | `ً ٌ ٍ` or alternate `ٗ ٞ ٖ` | the same three tanween qualities | preserve exact form; alternate-form rule hint remains validation-only pending convention citation | context derives rule |
| selected Warsh | harakah + `ۢ` | one composite tanween value | attach reviewed iqlāb hint; mini mīm is not a vowel or subject | context must independently derive iqlāb |
| selected Warsh | bare nūn + `ۢ` | nūn sākinah | attach reviewed iqlāb hint | context must independently derive iqlāb |
| either source | tatweel/formatting marks | no canonical sound unit | preserve exact source; phonologically ignore | none |
| either source | maddah | orthographic sign on an already represented site | preserve for attribution/validation; do not classify madd from it alone | semantic sound/context classifier |
| either source | stop/sakt sign | structural/boundary input | normalize through source convention | boundary policy, never Tajwīd glyph logic |

Each future source adapter must maintain the same table under
`docs/script-conventions/<riwayah>.md`: raw sequence, canonical value,
whether a mark is semantic/hint/structural/ignored, validation rule, examples,
and citation/review status. Runtime code contains only the mappings which have
passed that review.

### 2.7 Likely genuine riwāyah deltas

`ۥ` small wāw and `ٓ` maddah have many shared ordinary uses, but 621 aligned
Warsh sites show a plural mīm cluster with damma + small wāw (+ often maddah)
where Hafs has mīm + sukun. That is not a byte-only spelling alias. It is a
likely Warsh mīm-al-jamʿ/ṣilah realization difference and belongs in the
linguistic delta matrix. The script adapter preserves the written small wāw;
Warsh rule implementation determines the sound after research.

This is exactly why scalar counts cannot decide ownership: `U+06E5` is shared
orthography in some contexts, source-specific spelling in others, and evidence
of a possible riwāyah delta in a third.

### 2.8 Structural and stop marks

Hafs uses six principal stop signs (`ۖ ۗ ۘ ۙ ۚ ۛ`); the selected Warsh source
uses `ۖ` 9,948 times and none of the other five. Attachment also differs.
`۞` and `۩` differ in tokenization/spacing. These are source-structural facts,
not letters and not phonemes.

The script adapter creates structural graphemes and typed stop-sign facts. A
separate boundary policy decides whether a sign produces a stop. Unicode names
and the current Hafs YAML label `PREFERRED_CONTINUE` are not enough to assert
the Warsh source convention; that convention remains a required reviewed
fixture set.

## 3. Complete runtime-word inventory

`same` means the ordinary observed role is shared; a more specific row in
section 2 overrides it. `equiv` means a different representation normalizes
to an existing canonical unit. `context` means no scalar-only mapping is
allowed. `hint` and `structural` never directly create sounds. `delta` marks
a distribution that needs riwāyah research, not an implemented Warsh rule.

| Codepoint | Glyph | Hafs | Warsh | Class | Canonical treatment |
|---|---:|---:|---:|---|---|
| `U+0020` | space | 4,578 | 0 | structural | embedded Hafs source spacing; not a letter |
| `U+0621` | ء | 2,782 | 2,596 | same | hamza |
| `U+0623` | أ | 8,900 | 6,179 | same | hamza on alef |
| `U+0624` | ؤ | 706 | 185 | same | hamza on wāw |
| `U+0625` | إ | 5,088 | 4,241 | same | hamza below alef |
| `U+0626` | ئ | 921 | 678 | same | hamza on yāʾ seat |
| `U+0627` | ا | 25,184 | 42,161 | context | alef; in reviewed Warsh sequences also hamzat-al-waṣl carrier |
| `U+0628` | ب | 11,491 | 11,485 | same | bāʾ |
| `U+0629` | ة | 2,344 | 2,346 | same | tāʾ marbūṭah |
| `U+062A` | ت | 10,520 | 10,542 | same | tāʾ |
| `U+062B` | ث | 1,414 | 1,415 | same | thāʾ |
| `U+062C` | ج | 3,317 | 3,317 | same | jīm |
| `U+062D` | ح | 4,140 | 4,138 | same | ḥāʾ |
| `U+062E` | خ | 2,497 | 2,497 | same | khāʾ |
| `U+062F` | د | 5,991 | 5,992 | same | dāl |
| `U+0630` | ذ | 4,932 | 4,932 | same | dhāl |
| `U+0631` | ر | 12,403 | 12,402 | same | rāʾ; heaviness is rule output |
| `U+0632` | ز | 1,599 | 1,598 | same | zāy |
| `U+0633` | س | 6,010 | 6,009 | same | sīn |
| `U+0634` | ش | 2,124 | 2,124 | same | shīn |
| `U+0635` | ص | 2,074 | 2,074 | same | ṣād |
| `U+0636` | ض | 1,686 | 1,686 | same | ḍād |
| `U+0637` | ط | 1,273 | 1,273 | same | ṭāʾ |
| `U+0638` | ظ | 853 | 853 | same | ẓāʾ |
| `U+0639` | ع | 9,405 | 9,405 | same | ʿayn |
| `U+063A` | غ | 1,221 | 1,221 | same | ghayn |
| `U+0640` | ـ | 6,736 | 411 | structural | tatweel/attachment aid; preserve source, ignore for units |
| `U+0641` | ف | 8,747 | 8,748 | same | fāʾ |
| `U+0642` | ق | 7,034 | 7,034 | same | qāf |
| `U+0643` | ك | 10,497 | 10,497 | same | kāf |
| `U+0644` | ل | 38,102 | 38,098 | same | lām |
| `U+0645` | م | 26,735 | 26,733 | same/delta | mīm; plural-mīm realization is a riwāyah classifier delta candidate |
| `U+0646` | ن | 27,268 | 27,279 | same | nūn |
| `U+0647` | ه | 14,850 | 14,847 | same | hāʾ |
| `U+0648` | و | 24,970 | 25,486 | same | wāw; consonant/carrier decided contextually |
| `U+0649` | ى | 6,603 | 2,573 | equiv | yāʾ/alef-maqṣūrah family with `ے` |
| `U+064A` | ي | 18,222 | 19,485 | same | yāʾ; consonant/carrier decided contextually |
| `U+064B` | ً | 3,741 | 730 | same | tanween fath, supplemented by `ٗ` |
| `U+064C` | ٌ | 2,519 | 588 | same | tanween damm, supplemented by `ٞ` |
| `U+064D` | ٍ | 2,633 | 603 | same | tanween kasr, supplemented by `ٖ` |
| `U+064E` | َ | 122,948 | 125,435 | same | fatha |
| `U+064F` | ُ | 37,320 | 41,080 | same | damma |
| `U+0650` | ِ | 45,970 | 48,921 | same | kasra |
| `U+0651` | ّ | 22,678 | 21,723 | same | shaddah |
| `U+0652` | ْ | 37,148 | 37,554 | same | sukun |
| `U+0653` | ٓ | 5,376 | 6,336 | same/delta | maddah input; plural-mīm distribution requires research |
| `U+0654` | ٔ | 773 | 622 | same | combining hamza above, sequence-owned |
| `U+0655` | ٕ | 0 | 45 | context | combining hamza below; normalize reviewed sequences, not as a letter |
| `U+0656` | ٖ | 0 | 1,935 | equiv | tanween kasr |
| `U+0657` | ٗ | 0 | 2,916 | equiv | tanween fath |
| `U+065E` | ٞ | 0 | 1,815 | equiv | tanween damm |
| `U+0670` | ٰ | 9,726 | 10,033 | same | dagger alef/long-vowel carrier mark |
| `U+0671` | ٱ | 13,483 | 0 | equiv | Hafs scalar encoding of hamzat al-waṣl |
| `U+06D2` | ے | 0 | 2,996 | equiv | Warsh source yāʾ-family base |
| `U+06D6` | ۖ | 1,682 | 9,948 | structural | source stop sign; convention review required |
| `U+06D7` | ۗ | 603 | 0 | structural | Hafs stop sign |
| `U+06D8` | ۘ | 22 | 0 | structural | Hafs stop sign |
| `U+06D9` | ۙ | 68 | 0 | structural | Hafs stop sign |
| `U+06DA` | ۚ | 1,972 | 0 | structural | Hafs stop sign |
| `U+06DB` | ۛ | 12 | 0 | structural | Hafs stop sign |
| `U+06DC` | ۜ | 7 | 0 | hint | Hafs sakt/reading aid; boundary policy input |
| `U+06DE` | ۞ | 199 | 435 | structural | rub-el-hizb; never lexical sound |
| `U+06DF` | ۟ | 3,988 | 281 | context | Hafs silent-alef hint; Warsh initial-alef hamzat-al-waṣl family |
| `U+06E0` | ۠ | 66 | 0 | hint | Hafs continuation-silence/waqf input |
| `U+06E2` | ۢ | 0 | 575 | context/hint | with bare nūn: nūn-sākinah hint; with harakah: composite tanween plus hint; validate derived iqlāb |
| `U+06E3` | ۣ | 1 | 0 | hint | Hafs low-sīn reading aid |
| `U+06E5` | ۥ | 1,257 | 2,142 | context/delta | small wāw carrier; plural-mīm delta candidate |
| `U+06E6` | ۦ | 956 | 1,006 | same/context | small yāʾ carrier; rule decides realization |
| `U+06E7` | ۧ | 39 | 22 | hint/context | small high yāʾ; reviewed sequences/exception input |
| `U+06E8` | ۨ | 1 | 2 | hint/context | small high nūn; reviewed sequence input |
| `U+06E9` | ۩ | 15 | 14 | structural | sajdah mark |
| `U+06EA` | ۪ | 1 | 2,569 | context | hamzat-al-waṣl or marked vowel, selected by sequence |
| `U+06EB` | ۫ | 1 | 0 | hint | Hafs ishmām location input |
| `U+06EC` | ۬ | 1 | 10,055 | context | mainly Warsh article hamzat-al-waṣl sequence; Hafs tas-hīl site differs |
| `U+200F` | RLM | 1 | 0 | structural | formatting; preserve source audit, omit from letter units |

## 4. Adapter acceptance matrix

The Hafs adapter is implementation-ready when fixtures cover every row it
accepts. The initial Warsh adapter may accept only these proved families:

- ordinary shared letters and marks;
- the three alternate tanween marks;
- yeh barree in the reviewed yāʾ-family patterns;
- the three reviewed initial-alef hamzat-al-waṣl sequence families;
- structural marks with no phonological interpretation;
- iqlāb mini-mīm composition as canonical nūn/tanween plus a non-driving
  validation hint.

It must reject or mark unresolved:

- the 32 minority `U+06EA` contexts outside the two major vowel/initial-alef
  families until individually classified;
- minority non-article `U+06EC` contexts until fixture-reviewed;
- the full semantic meaning of Warsh stop signs;
- plural-mīm/small-wāw pronunciation;
- any imālah/taqlīl value not backed by Warsh recitation research;
- ambiguous combining-hamza-below sequences not covered by fixtures.

This permits the Hafs refactor and an honest Warsh script-normalization spike
without pretending the Warsh phonemizer is complete.
