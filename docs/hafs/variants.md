# Hafs variants

Each ID takes one scalar value. A grouped ID applies to every reference in
its row. There are no per-location overrides and no aliases for removed IDs.

`available_variants()` returns the legal values and default for each ID.

| Variant ID | Covered words and references | Options; default | Phoneme difference | Score effect | Tajweed and projection effect | Junction | Research source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `raa_firq_wasl` | firq, 26:63:11 | heavy, light; heavy | heavy r or light r | none | `tafkheem` or `tarqeeq` on raa | wasl | `research/tafkheem-tarqeeq.md` |
| `raa_alqitr_waqf` | alqitr, 34:12:10 | light, heavy; light | light r or heavy r | none | `tarqeeq` or `tafkheem` on raa | waqf | `research/tafkheem-tarqeeq.md` |
| `raa_misr_waqf` | misr, 12:21:5, 12:99:10, 43:51:10; bimisr, 10:87:8 | heavy, light; heavy | heavy r or light r | none | `tafkheem` or `tarqeeq` on raa | waqf | `research/tafkheem-tarqeeq.md` |
| `raa_nuthur_waqf` | wanuthur, 54:16:4, 54:18:6, 54:21:4, 54:30:4, 54:37:9, 54:39:3; bilnuthur, 54:23:3, 54:33:4, 54:36:5 | heavy, light; heavy | heavy r or light r | none | `tafkheem` or `tarqeeq` on raa | waqf | `research/tafkheem-tarqeeq.md` |
| `raa_yasr_waqf` | yasr, 89:4:3 | light, heavy; light | light r or heavy r | none | `tarqeeq` or `tafkheem` on raa | waqf | `research/tafkheem-tarqeeq.md` |
| `raa_asr_waqf` | asr, 20:77:6, 26:52:5; faasr, 11:81:9, 15:65:1, 44:23:1 | light, heavy; light | light r or heavy r | none | `tarqeeq` or `tafkheem` on raa | waqf | `research/tafkheem-tarqeeq.md` |
| `yaa_aatani_waqf` | aatani, 27:36:8 | hadhf, ithbat; hadhf | final long i absent or present | none | changes `waqf_ending` ownership of the final yaa | waqf | `research/waqf-ibtidaa.md` |
| `daaf_haraka` | daaf forms, 30:54:5, 30:54:10, 30:54:17 | fatha, damma; fatha | emphatic a or u after daaf | first nucleus is A or U | fatha receives emphatic colour; damma does not | all | `research/special-rules.md` |
| `seen_sad_yabsut` | yabsut, 2:245:14 | seen, saad; seen | s or emphatic s | selected slot is SEEN or SAD | saad adds `tafkheem` and emphatic fatha when present | all | `research/special-rules.md` |
| `seen_sad_bastah` | bastah, 7:69:22 | seen, saad; seen | s or emphatic s | selected slot is SEEN or SAD | saad adds `tafkheem` and emphatic fatha when present | all | `research/special-rules.md` |
| `seen_sad_al_musaytirun` | al-musaytirun, 52:37:7 | saad, seen; saad | emphatic s or s | selected slot is SAD or SEEN | saad adds `tafkheem` and emphatic fatha when present | all | `research/special-rules.md` |
| `seen_sad_bimusaytir` | bimusaytir, 88:22:3 | saad, seen; saad | emphatic s or s | selected slot is SAD or SEEN | saad adds `tafkheem` and emphatic fatha when present | all | `research/special-rules.md` |
| `noon_yaseen_wasl` | Ya-Seen to 36:2:1; Noon to 68:2:1 | izhar, idgham; izhar | final n stays, or merges into nasal w | none | `izhar`, or `idgham_bi_ghunnah` with noon as source and waw as host | wasl | `research/noon-meem.md` |
| `madd_lazim_tasheel` | al-dhakrayn, 6:143:10 and 6:144:8; al-aan, 10:51:7 and 10:91:1; al-lah, 10:59:14 and 27:59:9 | madd_lazim, tasheel; madd_lazim | long a, or short a plus a second eased hamza and short a | long nucleus, or short nucleus plus TASHIL hamza | `madd_lazim`, or `tashil`; the `tashil` extra phoneme controls whether the second hamza renders eased | all | `research/madd.md` |
| `iqlab_nasal` | all iqlab sites | assimilated, bilabial; assimilated | generic nasal or lip-closed nasal | none | `iqlab` identity and participants stay the same | all | `research/noon-meem.md` |
| `ikhfaa_shafawi_nasal` | all ikhfaa shafawi sites | assimilated, bilabial; assimilated | generic nasal or lip-closed nasal | none | `ikhfaa_shafawi` identity and participants stay the same | all | `research/noon-meem.md` |

The `madd_lazim_tasheel` selection is not changed by waqf or wasl. The small
seen marks at sakt sites remain sakt evidence and are not selectable variants.
Imala is not a variant. Its rendering is controlled only by the `imala` extra
phoneme.
