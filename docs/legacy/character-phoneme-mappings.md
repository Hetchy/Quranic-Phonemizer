# Character-Phoneme Mappings

Character-phoneme mappings provide one **cell per written character** — base letter,
each haraka / tanween, the long-vowel carrier — plus the rule-inserted *implicit* units
(hamza-waṣl connecting vowel, iltiqāʾ kasra, the Allah dagger-alef, the madd-ʿiwaḍ alef).
Each cell carries the phoneme(s) it sounds and their indices, so a forced aligner's
per-phoneme timestamps can drive **per-diacritic** highlighting.

This is the finer, character-level companion to [letter-phoneme-mappings](letter-phoneme-mappings.md)
(which aligns one entry per *letter*). It is additive — it changes nothing about the
letter-phoneme, silent, or tajweed outputs.

```python
from quranic_phonemizer import Phonemizer

pm = Phonemizer()
result = pm.phonemize("1:1")
cpm = result.character_phoneme_mappings()
for word in cpm.words:
    print(word.location, word.text)
    for c in word.cells:
        print(f"  {c.chars!r:5} {c.role:8} {c.status:9} {c.phonemes} idx={c.phoneme_indices}")
```

## Design principle — canonical domain only

A cell carries **only canonical domain facts**: its role, status, the phonemes it sounds,
their indices, and a tajweed-rule `tag`. It carries **no script/visual details** — no glyph
codes, no open/closed/iqlāb tanween form, no above/below placement. A consumer (e.g. the
Inspector) derives all of that from the `tag` + the diacritic char. This keeps the
phonemizer the single source of recitation domain knowledge and lets each renderer own its
own script conventions (e.g. the Digital Khatt mini-meem for iqlāb).

So the consumer never has to inspect the phonemes themselves, two facts that would
otherwise require phonology are folded into the cell: a **geminated** base composes the
canonical shaddah `ّ` into its `chars` (the consumer renders the text verbatim), and an
**idgham-shafawi** haraka whose vowel the merged base absorbs stays `present` — carrying the
base's `phoneme_indices` + a `share_group` — so the consumer co-lights it on the merger
rather than greying it out.

## Output structure

```
CharPhonemeResult
├── ref: str
├── mapping: PhonemizationMapping        # the underlying full mapping (for validation)
└── words: List[CharWord]
        ├── location, text, is_starting, is_stopping
        └── cells: List[Cell]
```

### Cell

| Field | Meaning |
|-------|---------|
| `chars` | the canonical source character(s) — includes a composed shaddah `ّ` on a geminated base; `""` if the cell is fully implicit |
| `role` | `base` · `haraka` · `tanween` · `madd` |
| `status` | `present` · `inserted` · `dropped` · `replaced` · `shortened` |
| `phonemes` | the phoneme strings this cell sounds (`[]` if silent) |
| `phoneme_indices` | **word-local** indices into the word's phoneme sequence — the timing anchor |
| `tag` | canonical case/rule key the consumer switches on (see below); else `null` |
| `share_group` | cells with the same id share timing / highlight together; else `null` |
| `source_letter_index` | the letter this cell sits on/after; `-1` if fully implicit |
| `source_letter_indices` | every contributing letter index |

**Roles** — `base` = consonant / consonantal vowel-letter / hamza / hamza-waṣl;
`haraka` = fatḥa/ḍamma/kasra/sukūn; `tanween` = fatḥatān/ḍammatān/kasratān;
`madd` = long-vowel carrier (`ا و ي ى`, mini `ۥ ۦ ۧ`, dagger-alef `ٰ`).

**Statuses** — `present` (explicit, sounded); `inserted` (implicit, no source char);
`dropped` (char present but silent in this context — render greyed); `replaced` (sound
changed from the written form, e.g. madd-ʿiwaḍ); `shortened` (long vowel reduced, carrier
silenced — iltiqāʾ).

**Tags** — the tajweed rule for rule-driven cases (`iqlab_tanween`, `ikhfaa_tanween`,
`idgham_ghunnah_tanween`, `idgham_bila_ghunnah_tanween`, `ikhfaa_noon`, …) and a small set
of structural keys: `hamza_wasl_vowel`, `iltiqaa_kasra`, `iltiqaa`, `madd_iwad`,
`allah_dagger_alef`, `qalqala`.

## The `phoneme_indices` invariant

`phoneme_indices` are taken from the **raw per-letter walk** (the same order as
`word.phonemes` and a forced aligner's per-word phones), never a redistributed view.
Iltiqāʾ demotion and waqf-tanween redistribution change which *cell displays* a phoneme,
never the phoneme's index. An index referenced by more than one cell is always an
intentional **shared-timing group** (e.g. a long vowel's haraka + carrier), flagged with
`share_group`. `validate()` enforces: every index covered ≥1×, shared indices share one
group, every diacritic char has a cell, and each cell's phoneme equals the resolved
phoneme at its index.

## Families (worked examples)

### Simple haraka — `بِسْمِ` (1:1:1)
```
'ب'  base    present  ['b'] idx=[0]
'ِ'  haraka  present  ['i'] idx=[1]
```

### Geminate — shaddah composed into `chars` (`رَبِّ`)
```
'ر'   base    present  ['rˤ'] idx=[0]
'بّ'  base    present  ['bb'] idx=[2]   ← canonical shaddah ◌ّ folded into chars
```

### Long vowel — haraka + carrier share the vowel (`ٱلرَّحِيمِ`, continue)
```
'ح'  base    present  ['ħ']  idx=[4]
'ِ'  haraka  present  ['i:'] idx=[5] share_group=G   ← both reference idx 5
'ي'  madd    present  ['i:'] idx=[5] share_group=G
```
Same for an extension carrier (`ٱلرَّحْمَـٰنِ` → `م`=`m`, fatḥa & dagger-alef `ٰ` share `a:`).

### Tanween (closed, continue)
```
# izhar  عَذَابٌ ع…     'ٌ' tanween present ['u','n']
# ikhfaa/iqlab أَلِيمٌ ب… 'ٌ' tanween present ['u','ŋ']  tag=iqlab_tanween
# idgham  هُدًى لِّـ…    'ً' tanween present ['a']        tag=idgham_bila_ghunnah_tanween share_group=G
#                        + next word 'لّ' base ['ll'] share_group=G   (cross-word co-highlight)
```

### Tanween + iltiqāʾ kasra (continue) — `خَيْرٌ ٱ…`
```
'ٌ'  tanween  present  ['u','n'] idx=[4,5]
''   haraka   inserted ['i']     idx=[6]  tag=iltiqaa_kasra     ← graphemeless bridge kasra
```

### Stopping — tanween dropped / madd-ʿiwaḍ
```
# عَظِيمٌ⏹   'ٌ' tanween dropped []            (dammatan/kasratan vanish at waqf)
# هُدًى⏹     'ً' tanween dropped [] tag=madd_iwad
#            'ى' madd    replaced ['a:'] tag=madd_iwad   (the long ā moves onto the alef-maksura)
```

### Hamza-waṣl pronounced (start) — `ٱلْحَمْدُ`
```
'ٱ'  base    present  ['ʔ'] idx=[0]
''   haraka  inserted ['a'] idx=[1] tag=hamza_wasl_vowel   ← connecting vowel, no grapheme
```

### Allah — implicit dagger-alef — `ٱللَّهِ`
```
'ل'  base    present  ['lˤlˤ'] idx=[2]
''   madd    inserted ['aˤ:']  idx=[3] tag=allah_dagger_alef
```

### Iltiqāʾ shortening (continue) — `فِى ٱل…`
```
'ف'  base    present   ['f'] idx=[0]
'ِ'  haraka  shortened ['i'] idx=[1] tag=iltiqaa   ← short vowel attaches to the base
'ى'  madd    shortened []                          ← carrier silenced
```

### Muqaṭṭaʿāt — `الٓمٓ` (2:1:1)
```
'ا'  base  present  ['ʔ','a','l','i','f']   ← one char, five phonemes
'لٓ' base  present  ['l','a:']
'مٓ' base  present  ['m̃','i:','m']
```

## Serialization

```python
cpm = result.character_phoneme_mappings()
cpm.to_dict()                      # nested dict (named fields)
cpm.to_list()                      # [[cell-as-list, ...] per word]
cpm.to_json(indent=2)
cpm.validate()                     # [] = valid
cpm.save("out.json")
result.save("out.json", fmt="char_phoneme")
```

Run with `result.character_phoneme_mappings(validate_result=True)` to raise on any violation.
