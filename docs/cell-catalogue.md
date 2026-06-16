# Multi-grapheme cell catalogue (letter-phoneme = shard duplicate-span)

Every grouped cell across 1-114. Roles per grapheme: **S** silent letter · **P** pronounced (sounding) · **X** extension. `P (false-tag)` = how many sounding graphemes a naive "duplicate-span ⇒ silent" rule would wrongly skip in this cell.

| # | roles | silencing rules | cross-word | cont | stop | P (false-tag) | example cell → phones | word(s) |
|---|---|---|---|--:|--:|--:|---|---|
| 1 | `S P` | hamza_wasl_silent |  | 6673 | 6513 | 1 | `ٱل` → ['l'] | ٱلْحَمْدُ |
| 2 | `P X` |  |  | 5535 | 5559 | 1 | `آ` → ['aˤ:'] | ٱلضَّآلِّينَ |
| 3 | `S S P` | hamza_wasl_silent, lam_shamsiyah |  | 4120 | 4072 | 1 | `ٱلد` → ['dd'] | ٱلدِّينِ |
| 4 | `P S` | vowel_silent |  | 3000 | 2996 | 1 | `أو` → ['ʔ', 'u'] | أُو۟لَـٰٓئِكَ |
| 5 | `P S` | UNRULED |  | 3145 | 2249 | 1 | `دى ` → ['d', 'a'] | هُدًى |
| 6 | `S S P` | hamza_wasl_silent, silent_iltiqaa_sakinayn | yes | 1447 | 1437 | 1 | `ا ٱل` → ['l'] | تَحْتِهَا ‖ ٱلْأَنْهَـٰرُ ۖ |
| 7 | `S P` | idgham_ghunnah_noon | yes | 1022 | 1022 | 1 | `ن م` → ['m̃', 'i'] | مِّن ‖ مِّثْلِهِۦ |
| 8 | `X X` |  |  | 953 | 951 | 0 | `ٰٓ` → ['a:'] | أُو۟لَـٰٓئِكَ |
| 9 | `S S S P` | hamza_wasl_silent, lam_shamsiyah, silent_iltiqaa_sakinayn | yes | 737 | 735 | 1 | `ا ٱلص` → ['sˤsˤ', 'i'] | ٱهْدِنَا ‖ ٱلصِّرَٰطَ |
| 10 | `P P` |  | yes | 706 | 705 | 2 | `م م` → ['m̃', 'a'] | قُلُوبِهِم ‖ مَّرَضٌ |
| 11 | `P X S` | vowel_silent |  | 527 | 527 | 1 | `وٓا ` → ['u:'] | تَكُونُوٓا۟ |
| 12 | `P X X` |  |  | 392 | 394 | 1 | `ىٰٓ ` → ['a:'] | مُوسَىٰٓ |
| 13 | `S P` | idgham_bila_ghunnah_noon | yes | 338 | 338 | 1 | `ن ر` → ['rˤrˤ', 'aˤ'] | مِن ‖ رَّبِّهِمْ ۖ |
| 14 | `S S S S P` | hamza_wasl_silent, lam_shamsiyah, silent_iltiqaa_sakinayn, vowel_silent | yes | 293 | 293 | 1 | `وا ٱلز` → ['zz', 'a'] | وَءَاتُوا۟ ‖ ٱلزَّكَوٰةَ |
| 15 | `S S S P` | hamza_wasl_silent, silent_iltiqaa_sakinayn, vowel_silent | yes | 202 | 202 | 1 | `وا ٱل` → ['l'] | تَلْبِسُوا۟ ‖ ٱلْحَقَّ |
| 16 | `S P` | lam_shamsiyah |  | 133 | 183 | 1 | `لر` → ['rr', 'i'] | وَلِلرِّجَالِ |
| 17 | `P S` | idgham_shafawi | yes | 125 | 125 | 1 | `م م` → ['m̃'] | جَآءَكُم ‖ مُّوسَىٰ |
| 18 | `S P` | idgham_mutamathilayn | yes | 122 | 122 | 1 | `ب ب` → ['bb', 'i'] | ٱضْرِب ‖ بِّعَصَاكَ |
| 19 | `S P` | idgham_mutajanisayn_kamil |  | 38 | 38 | 1 | `دت` → ['tt', 'a'] | وَعَدتَّنَا |
| 20 | `P S S` | idgham_mutamathilayn, vowel_silent |  | 22 | 22 | 1 | `توا ` → ['t', 'a'] | أَتَوا۟ |
| 21 | `S P` | idgham_mutajanisayn_kamil | yes | 20 | 20 | 1 | `ت ط` → ['tˤtˤ'] | هَمَّت ‖ طَّآئِفَتَانِ |
| 22 | `S P` | idgham_mutaqaribayn | yes | 12 | 12 | 1 | `ل ر` → ['rˤrˤ', 'aˤ'] | بَل ‖ رَّفَعَهُ |
| 23 | `S P` | idgham_mutamathilayn |  | 4 | 4 | 1 | `كك` → ['kk', 'u'] | يُدْرِككُّمُ |
| 24 | `P X X S` | vowel_silent |  | 2 | 2 | 1 | `وٰٓا ` → ['a:'] | ٱلرِّبَوٰٓا۟ |
| 25 | `X X S` | vowel_silent |  | 2 | 2 | 0 | `ۥٓا ` → ['u:'] | تَلْوُۥٓا۟ |
| 26 | `P P S` | vowel_silent | yes | 2 | 2 | 2 | `م ما` → ['m̃', 'i'] | مِّنكُم ‖ مِّا۟ئَةٌ |
| 27 | `X S` | vowel_silent |  | 1 | 1 | 0 | `ۥا ` → ['u:'] | لِتَسْتَوُۥا۟ |
| 28 | `S P` | idgham_mutaqaribayn |  | 1 | 1 | 1 | `قك` → ['kk', 'u'] | نَخْلُقكُّم |
