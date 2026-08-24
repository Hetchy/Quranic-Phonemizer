# Warsh foundation test reconciliation

This ledger records every non-obvious Hafs-only row considered for the Warsh
foundation. A row was promoted when the selected Warsh site tests the same
domain law with identical phonemes or a small source-selector difference. A
row stayed deferred only when sharing it would pre-encode a Warsh-specific
rule, lexical reading, or public selector that has its own implementation
owner.

Explicit `test_hafs_*` files, the Hafs and Warsh raa partitions, and the
hamza-transformation primitive tests are self-identifying and are not repeated
row by row below. The governing boundaries are in
[`warsh-test-placement.md`](warsh-test-placement.md); the domain behavior is in
[`research/v2/`](research/v2/).

## Promoted to shared coverage

The audit promoted 28 logical rows, adding 29 Warsh pytest executions because
`plural-waw` has separate joined and stopped states.

| File | Case | Reconciliation |
| --- | --- | --- |
| `articles/test_lam_contrasts.py` | `one-lam-rasm` | Same article assimilation. The selected source `اِ۬ليْلِ` omits the lexical lam's fatha and shadda, so the shared canonical lexeme recovery supplies them. |
| `hamza/test_iltiqa.py` | `long-a` | Same long-A shortening before an elided wasl onset; the rule reaches the same fatha source selector. |
| `hamza/test_iltiqa.py` | `long-u` | Same long-U shortening before an elided wasl onset; the rule reaches the same damma source selector. |
| `hamza/test_iltiqa.py` | `plural-waw` | Same joined shortening and stopped restoration. The source spelling differs but the existing selectors remain exact. |
| `hamza/test_iltiqa.py` | `meem-repair` | Same lexical I repair in `قُمِ اِ۬ليْلَ`; it requires no Warsh U exception or mim al-jam behavior. |
| `hamza/test_iltiqa.py` | `feminine-taa-repair` | Same lexical I repair on feminine taa at the selected site. |
| `hamza/test_iltiqa.py` | `dammatan` | Same default-I collision repair on the tanwin noon. |
| `hamza/test_iltiqa.py` | `kasratan` | Same default-I collision repair on the tanwin noon. |
| `vowels/madd/test_munfasil.py` | `joined-rasm` | Same joined-particle munfasil and following muttasil; both rule carriers are present in the selected source. |
| `vowels/madd/test_munfasil.py` | `interrogative-prefix` | Same two madd identities and phonemes; only the selected source's ordinary alif selector differs. |
| `vowels/madd/test_munfasil.py` | `vocative` | Same joined vocative-particle munfasil and source reach. |
| `test_muqattaat.py` | `alif-lam-meem` | Same named-letter phonemes and rules. Initial seated hamza and visible name-vowel marks are accepted as compact opening notation. |
| `test_muqattaat.py` | `alif-lam-meem-saad` | Same named-letter phonemes and complete assimilation, madd, tafkheem, and qalqala rules. |
| `test_muqattaat.py` | `taa-seen-meem` | Same named-letter phonemes and complete idgham, madd, and tafkheem rules. |
| `test_muqattaat.py` | `taa-seen` | Same named-letter phonemes and complete izhar, madd, and tafkheem rules. |
| `test_muqattaat.py` | `saad` | Same fixed named-letter phonemes and madd, tafkheem, and qalqala rules. |
| `test_muqattaat.py` | `ayn-seen-qaaf` | Same named-letter phonemes and complete ikhfaa, madd, and tafkheem rules. |
| `test_muqattaat.py` | `qaaf` | Same fixed named-letter phonemes and madd and tafkheem rules. |
| `test_muqattaat.py` | `noon` | Same fixed named-letter phonemes and madd and izhar rules. |
| `test_silent_letters.py` | `ulaika-waw` | Same rasm-only waw; selected-source sukun is projected as the silence witness. |
| `test_silent_letters.py` | `waulaika-waw` | Same rasm-only waw with the occurrence selector adjusted by the existing compact selector grammar. |
| `test_silent_letters.py` | `miata-alif` | Same rasm-only alif; selected-source sukun is the silence witness. |
| `test_silent_letters.py` | `biaydin-second-yaa` | Same pronounced glide plus one rasm-only yaa; a riwayah pick names the selected source's first yaa. |
| `test_silent_letters.py` | `afain-yaa` | Same rasm-only yaa with a direct selected-source selector. |
| `test_silent_letters.py` | `wamalaihi-yaa` | Same rasm-only yaa with a direct selected-source selector. |
| `test_silent_letters.py` | `nabai-final-yaa` | Same final rasm-only letter; a riwayah pick names the selected source's yeh barree. |
| `test_silent_letters.py` | `tayasu-alif` | Same rasm-only alif and sounded following yaa-hamza sequence. |
| `test_silent_letters.py` | `yayasi-alif` | Same rasm-only alif and sounded following yaa-hamza sequence. |

## Retained with an existing Warsh substitute

| File | Hafs case | Warsh coverage and reason |
| --- | --- | --- |
| `assimilation/test_mutamathilayn.py` | `lam` | The selected `أَقُل لَّكُمْ` host ends in Warsh mim al-jam, so its full state matrix is not foundation-only. `lam-warsh` uses `قُل لَّا` to cover the same lam-to-lam merger without that dependency. |
| `assimilation/test_mutajanisayn_kamil.py` | `aradttum` | Selected `اَرَدتُّمُۥٓ` adds mim al-jam to the word's ending. The same internal daal-to-taa complete merger is already shared through `rawadttuhu`, `ayyadttuka`, and `rawadttunna`. |

The `interrogative-article` row was removed from
`articles/test_lam_contrasts.py`, not withheld from Warsh. Its phonemes and
article-lam attribution duplicate the `dhakarayn` row owned by
`hamza/test_istifham_article.py`.

## Deferred non-obvious rows

| File | Case | Exact dependency |
| --- | --- | --- |
| `articles/test_lam_qamariyyah.py` | `yaa-hamza` | Article naql removes the internal qata onset in selected `اِ۬لَاخِرِ`; this is not a source-selector-only difference. |
| `hamza/test_iltiqa.py` | `long-i` | In `فِے اِ۬لَارْضِ`, article naql leaves the preceding long I intact instead of exposing the Hafs shortening shape. |
| `hamza/test_iltiqa.py` | `noon-repair` | This boundary is in the closed Warsh U-over-I iltiqa register. |
| `hamza/test_iltiqa.py` | `lam-repair` | `قُلُ اُ۟نظُرُواْ` is in the closed Warsh U-over-I iltiqa register. |
| `hamza/test_iltiqa.py` | `plural-meem` | Its short U is Warsh mim al-jam before wasl and must carry `iltiqa_haraka` on the inserted boundary vowel. |
| `hamza/test_seats.py` | `sakin-hamza-waw-seat` | Warsh replaces this single sakin hamza, producing long U rather than a sounded hamza. |
| `hamza/test_seats.py` | `sakin-hamza-alif-seat` | Warsh replaces this single sakin hamza, producing long A rather than a sounded hamza. |
| `nasal/test_ikhfaa.py` | `tha` | The selected word includes article naql before the noon-thaa ikhfaa; the whole-word expectation cannot be shared independently. |
| `nasal/test_izhar.py` | `hamza-ha` | Warsh naql changes the first boundary `مِنْ أَحَدٍ` before the row reaches its second izhar witness. Other shared rows retain complete throat-letter coverage. |
| `vowels/madd/test_arid.py` | `badal-overlap` | Warsh must add its own badal classification while retaining arid; the badal vertical owns that overlap. |
| `vowels/madd/test_iwad.py` | `fathatan-maqsura` | The selected final maqsura carries inclination, changing the result quality as well as its source reach. |
| `vowels/madd/test_munfasil.py` | `pausal-alif-negative` | Warsh retains the `ana` alif in wasl; the seven-alif vertical owns the different state matrix. |
| `vowels/madd/test_tabii.py` | `two-ordinary-longs` | The final A of `مُوس۪ىٰٓ` is a Warsh inclination site. |
| `vowels/test_written_carriers.py` | `maqsura-dagger-carrier` | The same `مُوس۪ىٰٓ` inclination changes the vowel-quality expectation. |
| `vowels/test_final_glides.py` | `liyarbuwa` | The aligned selected word is the different lexical form `لِّتُرْبُواْ`; it is not a second witness of the same final-glide word shape. |
| `test_taa_marbuta.py` | `fathatan-heavy-raa` | The selected source has dammatan, so it cannot verify the Hafs row's fathatan-under-heavy-raa partition. The ordinary fathatan and other taa-marbuta states are already shared. |

## Deferred selector and named-opening rows

These remain intentionally last because their assertions require public Warsh
selectors or a fixed Warsh inclination result, not merely a packaged source.

| File | Case | Owner |
| --- | --- | --- |
| `nasal/test_ikhfaa_shafawi.py` | `meem-before-baa-boundary` | Public nasal-token selector binding. |
| `nasal/test_iqlab.py` | `written-noon-boundary` | Public nasal-token selector binding. |
| `hamza/test_istifham_article.py` | `dhakarayn` | Warsh istifham-article selector and its ibdal/tashil results. |
| `hamza/test_istifham_article.py` | `alan` | Warsh istifham-article selector and its ibdal/tashil results. |
| `hamza/test_istifham_article.py` | `allah` | Warsh istifham-article selector and its ibdal/tashil results. |
| `test_muqattaat.py` | `alif-lam-raa` | Fixed Warsh taqlil on the named raa. |
| `test_muqattaat.py` | `alif-lam-meem-raa` | Fixed Warsh taqlil on the named raa. |
| `test_muqattaat.py` | `kaaf-haa-yaa-ayn-saad` | Warsh Maryam opening-letter inclination choices. |
| `test_muqattaat.py` | `taa-haa` | Fixed Warsh kubra on the named haa. |
| `test_muqattaat.py` | `yaa-seen` | Warsh Yaseen opening-letter inclination choice. |
| `test_muqattaat.py` | `haa-meem` | Fixed Warsh taqlil on the named haa. |
| `test_muqattaat.py` | `noon-wasl` | Riwayah-owned continuation selector. |
| `test_sakt.py` | `iwaja-qayyima` | Public lexical sakt selector. |
| `test_sakt.py` | `marqadina-hadha` | Public lexical sakt selector. |
| `test_sakt.py` | `man-raq` | Public lexical sakt selector. |
| `test_sakt.py` | `bal-ran` | Public lexical sakt selector. |
| `test_sakt.py` | `maliyah-halak` | Public lexical sakt selector. |
| `vowels/test_seven_alifs.py` | `qawarira-first` | Warsh seven-alif state matrix. |
| `vowels/test_seven_alifs.py` | `al-thununa` | Warsh seven-alif state matrix. |
| `vowels/test_seven_alifs.py` | `al-rasula` | Warsh seven-alif state matrix. |
| `vowels/test_seven_alifs.py` | `al-sabila` | Warsh seven-alif state matrix. |
| `vowels/test_seven_alifs.py` | `ana` | Warsh seven-alif state matrix. |
| `vowels/test_seven_alifs.py` | `lakinna` | Warsh seven-alif state matrix. |
| `vowels/test_seven_alifs.py` | `qawarira-second` | Warsh seven-alif state matrix. |
| `vowels/test_seven_alifs.py` | `salasila` | Warsh seven-alif state matrix. |

## Acceptance invariant

No generic Hafs-only row remains unexplained. Any later row added to an
unprefixed phonemization file must either declare a Warsh site, name a clean
Warsh substitute in this ledger, or identify the owning Warsh rule or selector
vertical here. A current engine pass is not sufficient evidence: the expected
Warsh result must also agree with the selected script and the v2 domain owner.
