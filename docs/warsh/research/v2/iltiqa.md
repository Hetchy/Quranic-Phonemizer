# Iltiqa al-sakinayn

This document owns the connected-reading repair when eliding a genuine
hamzat al-wasl would expose two adjacent sakin sounds. It defines the general
`iltiqa_haraka` transformation and its Warsh U subregister. It does not own
the WASL onset, ordinary naql, or the separate shortening of a long vowel.

## Structural trigger

After boundary planning and wasl elision, apply a collision repair only when:

1. the last performed unit of the first word would otherwise be sakin;
2. the next word begins a canonical WASL onset;
3. that onset is elided by joined speech; and
4. the exposed first consonant of the next word is sakin.

The repaired host may be a lexical consonant, the consonantal noon supplied by
tanwin, feminine taa, or another canonically silent boundary unit. The
plural-pronoun mim's authored short U before wasl belongs to mim al-jam and is
not an `iltiqa_haraka` occurrence.
A visible source haraka may attest the result, but does not trigger it.

The selected-corpus register has 1,659 within-ayah `iltiqa_haraka` sites:

| Result quality | Count |
| --- | ---: |
| A | 770 |
| I | 381 |
| U | 508 |

These counts are a generated corpus invariant, not a hand-maintained location
table. The generator compares canonical morphology with the requested
boundary and then reconciles the result to the selected Warsh source. Ayah-end
continuation is outside this count because the source corpus does not encode
one compulsory cross-ayah plan.

## Choosing A, I, or U

Lexically established boundary vowels keep their quality. For example, the
sakin noon of `مِنْ` takes A in `وَمِنَ اَ۬لنَّاسِ`, source 2:7:1-2,
canonical 2:8:1-2. Other closed morphological classes keep their authenticated
U or I behavior.

For the otherwise-default I repair, Warsh and the other cited readers use U
when the following WASL word begins with U because its third written letter
has an original, not temporary, damm. Al-Wafi states the condition and the
representative families `قل ادعوا`, `أو انقص`, `قالت اخرج`, `أن اعبدوا`,
tanwin before `انظر`, and `ولقد استهزئ`
([Al-Wafi](https://www.islamweb.net/ar/library/content/245/38/)). Al-Nashr
enumerates the same consonant classes and readings
([Al-Nashr](https://www.islamweb.net/ar/library/content/70/230/)).

The original-vowel condition matters. `أَنِ اِ۪تَّقُواْ`, source
4:130:16-17, canonical 4:131:16-17, stays I. The qaf damm in `اتقوا` is not
the original stem damm licensed by the U rule. A classifier that simply looks
two written clusters ahead produces the wrong result here.

## Warsh U register

There are 32 closed U-over-I boundaries in the selected Warsh reading. The
domain grouping and canonical registers are:

| Host family | Count | Canonical boundary refs |
| --- | ---: | --- |
| `أن` | 11 | 4:66:5-6; 5:49:1-2; 5:117:8-9; 16:36:7-8; 23:32:5-6; 27:45:7-8; 31:12:5-6; 31:14:12-13; 36:61:1-2; 68:22:1-2; 71:3:1-2 |
| `قل` | 5 | 7:195:20-21; 10:101:1-2; 17:56:1-2; 17:110:1-2; 34:22:1-2 |
| `من` | 4 | 2:173:13-14; 5:3:51-52; 6:145:30-31; 16:115:13-14 |
| Tanwin noon | 4 | 6:65:21-22; 6:99:32-33; 7:49:7-8; 14:26:5-6 |
| `أو` | 3 | 4:66:8-9; 17:110:4-5; 73:3:2-3 |
| `قد` | 3 | 6:10:1-2; 13:32:1-2; 21:41:1-2 |
| `لكن` | 1 | 7:143:15-16 |
| Feminine taa | 1 | 12:31:14-15 |

The corresponding selected-source boundaries, in the same row order, are:

- `أن`: 4:65:5-6; 5:51:1-2; 5:119:8-9; 16:36:7-8;
  23:32:5-6; 27:47:7-8; 31:11:5-6; 31:13:12-13; 36:60:1-2;
  68:22:1-2; 71:3:1-2.
- `قل`: 7:195:20-21; 10:101:1-2; 17:56:1-2; 17:109:1-2;
  34:22:1-2.
- `من`: 2:172:13-14; 5:4:51-52; 6:146:30-31; 16:115:13-14.
- tanwin noon: 6:66:21-22; 6:100:32-33; 7:48:7-8; 14:28:5-6.
- `أو`: 4:65:8-9; 17:109:4-5; 73:2:2-3.
- `قد`: 6:11:1-2; 13:33:1-2; 21:41:1-2.
- `لكن`: 7:143:15-16.
- feminine taa: 12:31:14-15.

The register is closed because U depends on an authenticated qiraa choice,
not merely on the universal collision. Its data rows should carry both
addresses and the target word's derived U start. The general 1,659-site
register remains predicate-owned.

## Manual outcomes

The sequences below show the affected span only.

| Quality | Selected source and refs | Wasl sequence | Rules |
| --- | --- | --- | --- |
| A | `وَمِنَ اَ۬لنَّاسِ`, source 2:7:1-2, canonical 2:8:1-2 | `... m i n a ñ a: ...` | `iltiqa_haraka` classifies only A. Its transformed vowel column is inserted at the boundary; `hamza_wasl_silent` and the ordinary article/noon rules remain separate. |
| I | `وَإِذِ اِ۪سْتَسْق۪ىٰ`, source 2:59:1-2, canonical 2:60:1-2 | `w a ʔ i ð i s t ...` | `iltiqa_haraka` classifies only I. Its transformed vowel column is inserted at the boundary; `hamza_wasl_silent` remains separate. The omitted final nucleus follows its independent inclination selection. |
| U | `قُلُ اُ۟دْعُواْ`, source and canonical 7:195:20-21 | `q u l u d Q ʕ u:` | `iltiqa_haraka` classifies only U. Its transformed vowel column is inserted at the boundary. Ordinary qalqala owns `/Q/`, and `hamza_wasl_silent` remains separate. |
| U on tanwin | `بَعْضٍۖ اُ۟نظُرْ`, source 6:66:21-22, canonical 6:65:21-22 | `... dˤ i n u ŋˤ ðˤ u rˤ` | `iltiqa_haraka` classifies only U. Its transformed vowel column is inserted at the boundary. The following emphatic `ikhfaa`, ordinary raa tafkheem, and `hamza_wasl_silent` remain separate. |

For any row, a complete stop after the first word suppresses
`iltiqa_haraka`; the first word receives its ordinary waqf result. If the
requested range continues after that stop, the second word is a new ibtidaa
and realizes its WASL onset and helping vowel with `hamza_wasl_damma`, so the U
example begins `ʔ u d Q ʕ u:`. Ordinary qalqala still owns `/Q/`. Only a
following word outside the requested
utterance is unperformed. Neither case emits a repair on the preceding word.

## Rule identity and reach

The public rule is `iltiqa_haraka`, not `iltiqa_kasra`. Its result vowel holds
A, I, or U; the rule name does not encode one quality.

One occurrence classifies only the realized short A, I, or U sound. It does
not classify the repaired consonant or noon sound. The core occurrence names
the repaired slot, including the nunation slot for tanwin, as its subject and
the following wasl slot as trigger context. In the transformed cell view the
performed vowel is an inserted boundary column carrying `iltiqa_haraka`; the
base consonant or tanwin column does not carry that rule. A written linking-
haraka witness remains source evidence and never selects the result.

The next word's WASL unit is trigger context, not an affected participant of
`iltiqa_haraka`; it receives its separate `hamza_wasl_silent` occurrence. The two
rules must not be collapsed, because a caller can start on the next word
without a host repair.

## Exclusions and precedence

- If the preceding unit is a long carrier, collision repair is
  `iltiqa_shortening`; do not add a short vowel or `iltiqa_haraka`.
- If an ordinary lexical vowel already sounds at the boundary, there is no
  collision and no iltiqa rule.
- A qata onset softened by ordinary naql is not WASL. Naql transfers the qata
  vowel and owns that transformation; it emits no iltiqa rule.
- A source stop sign does not suppress the repair. Only the explicit boundary
  plan does.
- Under the single-script decision, the reviewed linking-haraka family may
  supply the repair quality per site; the predicate, the 1,659 partition, and
  the 32 U rows remain its conformance reconciliation. The repair itself stays
  boundary-dependent: an explicit stop suppresses it regardless of the mark.

Tests should derive the complete register, assert the 1,659 total and quality
partition, assert all 38 U-over-I rows, and fail on any source attestation that
disagrees with the independently derived result.
