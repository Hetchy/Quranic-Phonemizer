# Iltiqa al-sakinayn

This document distinguishes two related facts which must not share one public
rule occurrence merely because both avoid adjacent sakin sounds:

- a connected-form haraka already present in the canonical reading; and
- a short vowel the boundary runtime must insert onto a canonically
  vowel-absent unit.

The public `iltiqa_haraka` rule names only the second transformation. It does
not own hamzat al-wasl, ordinary naql, long-vowel shortening, or every lexical
connected vowel traditionally explained through iltiqa al-sakinayn.

## Public transformation trigger

Emit `iltiqa_haraka` only when all of the following hold:

1. the next word begins with genuine hamzat al-wasl;
2. joined reading elides that onset;
3. its first exposed consonant is sakin;
4. the preceding canonical unit has no vowel; and
5. the runtime realizes a new short A, I, or U on that unit.

The implemented hosts are the consonantal noon supplied by tanwin and the
quiescent ending of a spelled letter name. A visible source haraka may attest
the result, but does not by itself trigger or define the public rule.

Lexical and morphological connected forms are different. Hafs `قُلِ
ٱنظُرُوا۟`, Warsh `قُلُ اُ۟دْعُواْ`, `مِنَ اَ۬لنَّاسِ`, `أَنِ/أَنُ`, feminine
taa, and mim al-jam before wasl already carry their connected vowel in the
canonical reading. They emit no `iltiqa_haraka` occurrence.

## Choosing A, I, or U

A spelled letter name takes A. The cross-ayah join `الٓمٓ اَ۬للَّهُ`, canonical
3:1-3:2, therefore inserts A after the final meem.

A tanwin noon takes I by default. Warsh takes U in the authenticated subfamily
where the following wasl word begins with an original U, rather than a
temporary surface damm. Al-Wafi states this condition and gives representative
families including tanwin before `انظر`
([Al-Wafi](https://www.islamweb.net/ar/library/content/245/38/)). Al-Nashr
enumerates the same connected-reading choices
([Al-Nashr](https://www.islamweb.net/ar/library/content/70/230/)).

The selected source contains 44 within-ayah tanwin repair sites: 40 with I and
4 with Warsh U. Cross-ayah continuation is request-dependent and therefore not
part of that closed within-ayah count.

## Connected-vowel audit

The broader selected-corpus audit contains 1,665 within-ayah connected-vowel
sites:

| Result quality | Count |
| --- | ---: |
| A | 770 |
| I | 381 |
| U | 514 |

This is not a count of `iltiqa_haraka` occurrences. It reconciles canonical
morphology and selected-source linking marks, so it also includes lexical and
morphological connected forms which emit no public transformation.

Within that audit, 38 boundaries use Warsh U where the corresponding Hafs
connected form uses I:

| Host family | Count | Canonical boundary refs |
| --- | ---: | --- |
| `أن` | 11 | 4:66:5-6; 5:49:1-2; 5:117:8-9; 16:36:7-8; 23:32:5-6; 27:45:7-8; 31:12:5-6; 31:14:12-13; 36:61:1-2; 68:22:1-2; 71:3:1-2 |
| Plural mim | 6 | 4:154:6-7; 7:161:3-4; 16:32:7-8; 25:60:3-4; 36:45:3-4; 40:60:2-3 |
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
- plural mim: 4:153:6-7; 7:161:3-4; 16:32:7-8; 25:60:3-4;
  36:44:3-4; 40:60:2-3.
- `قل`: 7:195:20-21; 10:101:1-2; 17:56:1-2; 17:109:1-2;
  34:22:1-2.
- `من`: 2:172:13-14; 5:4:51-52; 6:146:30-31; 16:115:13-14.
- tanwin noon: 6:66:21-22; 6:100:32-33; 7:48:7-8; 14:28:5-6.
- `أو`: 4:65:8-9; 17:109:4-5; 73:2:2-3.
- `قد`: 6:11:1-2; 13:33:1-2; 21:41:1-2.
- `لكن`: 7:143:15-16.
- feminine taa: 12:31:14-15.

Only the four tanwin rows in this 38-row quality register emit
`iltiqa_haraka`. The other 34 are authored connected forms; plural mim remains
owned by mim al-jam.

## Manual outcomes

| Domain | Connected sequence | Public rules |
| --- | --- | --- |
| Spelled name A | `الٓمٓ اَ۬للَّهُ`, 3:1-3:2: `... m a lˤlˤ ...` | `iltiqa_haraka` on inserted A; `hamza_wasl_silent` on the following onset |
| Tanwin I | `خَيْرٌۖ اِ۪هْبِطُواْ`, canonical 2:61:30-31: `... rˤ u n i h b ...` | `iltiqa_haraka` on inserted I; `hamza_wasl_silent` separately |
| Warsh tanwin U | `بَعْضٍۖ اُ۟نظُرْ`, canonical 6:65:21-22: `... dˤ i n u ŋˤ ðˤ ...` | `iltiqa_haraka` on inserted U; `hamza_wasl_silent` separately |
| Lexical I/U | Hafs `قُلِ ٱدْعُوا۟`; Warsh `قُلُ اُ۟دْعُواْ` | No `iltiqa_haraka`; only `hamza_wasl_silent` on the following onset |
| Mim al-jam U | `فَزَادَهُمُ اُ۬للَّهُ` | No `iltiqa_haraka`; mim al-jam owns the connected form |

A complete stop after the first word suppresses a runtime insertion. If the
range continues, the second word begins a new ibtidaa and realizes its wasl
onset with `hamza_wasl_fatha`, `hamza_wasl_kasra`, or
`hamza_wasl_damma`. No preceding-word `iltiqa_haraka` survives that stop.

## Rule identity and reach

The public rule is `iltiqa_haraka`, not `iltiqa_kasra`, because its inserted
sound may be A, I, or U. The quality lives on the resulting vowel rather than
in the rule name.

One occurrence reaches only the newly realized short-vowel sound. It does not
classify the host consonant or tanwin-noon sound. The core occurrence names
the repaired slot as its subject and the following wasl slot as private trigger
context. The transformed cell view places the sound and occurrence on a
source-less inserted boundary-haraka column.

The next word's wasl unit receives its independent `hamza_wasl_silent`
occurrence. A source linking mark may attest the canonical or performed
quality, but a mark alone never creates rule ownership.

## Exclusions and precedence

- A long carrier meeting the exposed sakin uses `iltiqa_shortening`.
- A lexical or morphological connected vowel already present in the Score
  emits no `iltiqa_haraka`, regardless of its historical explanation.
- Mim al-jam before wasl is an authored connected form, not a runtime repair.
- A qata onset handled by naql is not hamzat al-wasl; naql owns that change.
- A source stop sign does not choose the boundary state. Only the requested
  plan decides whether the words join.

## Acceptance checks

- Assert the closed 44-row tanwin source register and its 40-I/4-U partition.
- Assert the spelled-name A case across 3:1-3:2.
- Assert source, sound, and transformed-cell reach only for inserted vowels.
- Assert Hafs `قُلِ` and Warsh `قُلُ` have no `iltiqa_haraka` occurrence.
- Retain the 1,665 connected-vowel audit and 38 U-over-I register as quality
  reconciliation, without treating either as a public-rule count.
- Keep `hamza_wasl_silent`, `iltiqa_shortening`, naql, and mim al-jam under
  their separate owners.
