# Yaa-zawaid

Yaa-zawaid are word-final yaas retained in recitation beyond the base
Uthmanic rasm. For Nafi, including Warsh, the general state is retention in
wasl and deletion in waqf. Al-Wafi defines the category, distinguishes it
from yaa al-idafa, and states Nafi's boundary behavior before enumerating the
sites ([Al-Wafi, yaa-zawaid](https://www.islamweb.net/ar/library/content/245/35/%D8%A8%D8%A7%D8%A8-%D9%8A%D8%A7%D8%A1%D8%A7%D8%AA-%D8%A7%D9%84%D8%B2%D9%88%D8%A7%D8%A6%D8%AF)).

For Warsh through al-Azraq the selected register contains 47 sites:

- 46 produce joined-only `/i:/` and are absent at waqf;
- one, `ءَات۪يٰنِۦَ` at canonical `27:36`, produces joined-only `/j a/` and is
  absent at waqf; and
- among the 46 long-vowel sites, 10 precede hamzat qata and receive
  `madd_munfasil`, 35 receive `madd_tabii`, and row 7 receives `madd_badal`
  because its joined yaa follows hamza.

The classical chapter specifically records the open Warsh yaa in
`فَمَآ ءَات۪يٰنِۦَ اَ۬للَّهُ` and the deletion on stopping
([Al-Wafi, the Naml site](https://www.islamweb.net/ar/library/content/245/35/%D8%A8%D8%A7%D8%A8-%D9%8A%D8%A7%D8%A1%D8%A7%D8%AA-%D8%A7%D9%84%D8%B2%D9%88%D8%A7%D8%A6%D8%AF),
[al-Kashf, focused explanation](https://ablibrary.net/book_content/7233/144)).

## Boundary shapes

### Ordinary long site

Selected source `2:185:11`, canonical `2:186`, is
`دَعَانِۦۖ فَلْيَسْتَجِيبُواْ`:

```text
state                         host tokens       effective rule
wasl                          d a ʕ a: n i:     madd_tabii on i:
ibtidaa at host and continue  d a ʕ a: n i:     madd_tabii on i:
waqf on host                  d a ʕ a: n         no final i: and no madd
```

Selected source `2:185:9-10`, canonical `2:186`, is
`اَ۬لدَّاعِۦٓ إِذَا`. It demonstrates the qata boundary:

```text
state                         relevant tokens              effective rule
wasl                          ... dd a: ʕ i: ʔ i ð a:     madd_munfasil on i:
ibtidaa at host and continue  ʔ a dd a: ʕ i: ʔ i ð a:    madd_munfasil on i:
waqf on host                  ʔ a dd a: ʕ                 no final i: and no madd
```

Starting at the following word naturally has no yaa-zawaid host. Starting at
the host but stopping there uses the waqf row, not the joined row.

### The one consonantal site

Selected source `27:37:8-9`, canonical `27:36`, is
`ءَات۪يٰنِۦَ اَ۬للَّهُ`:

The matrix shows the default `dhat_yaa=taqlil` face for the word's medial
yaa-origin alif:

```text
state                         relevant tokens
wasl                          ʔ a: t ɛ: n i j a lˤlˤ aˤ: h u
ibtidaa at host and continue  ʔ a: t ɛ: n i j a lˤlˤ aˤ: h u
waqf on host                  ʔ a: t ɛ: n
```

The extra yaa is `/j/` with fatha, not `/i:/`; it receives no madd rule. The
word's yaa-origin medial long is independently owned by the public `dhat_yaa`
selector: the default `taqlil` face is typed `TAQLIL`, renders `/ɛ:/`, and
receives `taqlil`, while the `fath` face renders `/a:/` with no inclination
rule. Thus the fath-face joined sequence is
`/ʔ a: t a: n i j a lˤlˤ aˤ: h u/` and its waqf sequence is
`/ʔ a: t a: n/`. The following article onset receives `hamza_wasl_silent` in the
joined rows. Other rules on the word, such as its initial long, are independent
of this authored final slot. See the selector contract in
[`../../../variants.md`](../../../variants.md).

## Exhaustive Warsh register

The table reconciles the Al-Wafi inventory against the selected King Fahd
script. A selected source ref follows that source's ayah numbering; the
canonical ref is the repository's cross-script identity. Every row is deleted
at waqf ([Al-Wafi, complete transmitted inventory](https://www.islamweb.net/ar/library/content/245/35/%D8%A8%D8%A7%D8%A8-%D9%8A%D8%A7%D8%A1%D8%A7%D8%AA-%D8%A7%D9%84%D8%B2%D9%88%D8%A7%D8%A6%D8%AF)).

| # | Selected source ref | Canonical ref | Exact selected text | Joined result |
| ---: | --- | --- | --- | --- |
| 1 | `2:185:9` | `2:186` | `اَ۬لدَّاعِۦٓ` | `/i:/`, `madd_munfasil` |
| 2 | `2:185:11` | `2:186` | `دَعَانِۦۖ` | `/i:/`, `madd_tabii` |
| 3 | `3:20:8` | `3:20` | `اِ۪تَّبَعَنِۦۖ` | `/i:/`, `madd_tabii` |
| 4 | `11:46:12` | `11:46` | `تَسْـَٔلَنِّۦ` | `/i:/`, `madd_tabii` |
| 5 | `11:105:2` | `11:105` | `يَاتِۦ` | `/i:/`, `madd_tabii` |
| 6 | `14:17:10` | `14:14` | `وَعِيدِۦۖ` | `/i:/`, `madd_tabii` |
| 7 | `14:42:9` | `14:40` | `دُعَآءِۦۖ` | `/i:/`, `madd_badal` |
| 8 | `17:62:8` | `17:62` | `اَخَّرْتَنِۦٓ` | `/i:/`, `madd_munfasil` |
| 9 | `17:97:5` | `17:97` | `اَ۬لْمُهْتَدِۦۖ` | `/i:/`, `madd_tabii` |
| 10 | `18:17:27` | `18:17` | `اَ۬لْمُهْتَدِۦۖ` | `/i:/`, `madd_tabii` |
| 11 | `18:24:19` | `18:24` | `يَّهْدِيَنِۦ` | `/i:/`, `madd_tabii` |
| 12 | `18:39:4` | `18:40` | `يُّوتِيَنِۦ` | `/i:/`, `madd_tabii` |
| 13 | `18:63:5` | `18:64` | `نَبْغِۦۖ` | `/i:/`, `madd_tabii` |
| 14 | `18:65:8` | `18:66` | `تُعَلِّمَنِۦ` | `/i:/`, `madd_tabii` |
| 15 | `20:91:9` | `20:93` | `تَتَّبِعَنِۦٓ` | `/i:/`, `madd_munfasil` |
| 16 | `22:23:16` | `22:25` | `وَالْبَادِۦۖ` | `/i:/`, `madd_tabii` |
| 17 | `22:42:11` | `22:44` | `نَكِيرِۦۖ` | `/i:/`, `madd_tabii` |
| 18 | `27:37:5` | `27:36` | `أَتُمِدُّونَنِۦ` | `/i:/`, `madd_tabii` |
| 19 | `27:37:8` | `27:36` | `ءَات۪يٰنِۦَ` | `/j a/`, no madd |
| 20 | `28:34:14` | `28:34` | `يُّكَذِّبُونِۦۖ` | `/i:/`, `madd_tabii` |
| 21 | `34:13:9` | `34:13` | `كَالْجَوَابِۦ` | `/i:/`, `madd_tabii` |
| 22 | `34:45:14` | `34:45` | `نَكِيرِۦۖ` | `/i:/`, `madd_tabii` |
| 23 | `35:26:7` | `35:26` | `نَكِيرِۦٓۖ` | `/i:/`, `madd_munfasil` |
| 24 | `36:22:15` | `36:23` | `يُنقِذُونِۦٓۖ` | `/i:/`, `madd_munfasil` |
| 25 | `37:56:5` | `37:56` | `لَتُرْدِينِۦ` | `/i:/`, `madd_tabii` |
| 26 | `40:14:16` | `40:15` | `اَ۬لتَّلَٰقِۦ` | `/i:/`, `madd_tabii` |
| 27 | `40:32:6` | `40:32` | `اَ۬لتَّنَادِۦ` | `/i:/`, `madd_tabii` |
| 28 | `42:30:3` | `42:32` | `اِ۬لْجَوَارِۦ` | `/i:/`, `madd_tabii` |
| 29 | `44:19:6` | `44:20` | `تَرْجُمُونِۦ` | `/i:/`, `madd_tabii` |
| 30 | `44:20:5` | `44:21` | `فَاعْتَزِلُونِۦۖ` | `/i:/`, `madd_tabii` |
| 31 | `50:14:9` | `50:14` | `وَعِيدِۦٓۖ` | `/i:/`, `madd_munfasil` |
| 32 | `50:41:4` | `50:41` | `اِ۬لْمُنَادِۦ` | `/i:/`, `madd_tabii` |
| 33 | `50:45:13` | `50:45` | `وَعِيدِۦۖ` | `/i:/`, `madd_tabii` |
| 34 | `54:6:5` | `54:6` | `اُ۬لدَّاعِۦٓ` | `/i:/`, `madd_munfasil` |
| 35 | `54:8:3` | `54:8` | `اَ۬لدَّاعِۦۖ` | `/i:/`, `madd_tabii` |
| 36 | `54:16:4` | `54:16` | `وَنُذُرِۦۖ` | `/i:/`, `madd_tabii` |
| 37 | `54:18:6` | `54:18` | `وَنُذُرِۦٓۖ` | `/i:/`, `madd_munfasil` |
| 38 | `54:21:4` | `54:21` | `وَنُذُرِۦۖ` | `/i:/`, `madd_tabii` |
| 39 | `54:30:4` | `54:30` | `وَنُذُرِۦٓۖ` | `/i:/`, `madd_munfasil` |
| 40 | `54:37:9` | `54:37` | `وَنُذُرِۦۖ` | `/i:/`, `madd_tabii` |
| 41 | `54:39:3` | `54:39` | `وَنُذُرِۦۖ` | `/i:/`, `madd_tabii` |
| 42 | `67:18:12` | `67:17` | `نَذِيرِۦۖ` | `/i:/`, `madd_tabii` |
| 43 | `67:19:8` | `67:18` | `نَكِيرِۦٓۖ` | `/i:/`, `madd_munfasil` |
| 44 | `89:4:3` | `89:4` | `يَسْرِۦ` | `/i:/`, `madd_tabii` |
| 45 | `89:9:5` | `89:9` | `بِالْوَادِۦ` | `/i:/`, `madd_tabii` |
| 46 | `89:16:3` | `89:15` | `أَكْرَمَنِۦۖ` | `/i:/`, `madd_tabii` |
| 47 | `89:18:3` | `89:16` | `أَهَٰنَنِۦ` | `/i:/`, `madd_tabii` |

The ten `madd_munfasil` rows are 1, 8, 15, 23, 24, 31, 34, 37,
39, and 43. This closed count is a useful assertion against accidentally
using the small-yaa scalar alone as a madd classifier.

Row 7 is the sole joined yaa-zawaid carrier immediately after hamza. It keeps
`madd_badal` without `madd_tabii`
([Al-Nashr lists `دُعَائِي` among after-hamza carriers](https://islamweb.net/ar/library/content/70/99/%D9%81%D8%B5%D9%84-%D9%81%D9%8A-%D9%88%D9%82%D9%88%D8%B9-%D8%AD%D8%B1%D9%81-%D8%A7%D9%84%D9%85%D8%AF-%D8%A8%D8%B9%D8%AF-%D8%A7%D9%84%D9%87%D9%85%D8%B2)).

## Sound and character attribution

For an ordinary joined site:

- the authored boundary slot produces `/i:/` in wasl or joined ibtidaa and
  produces no sound at waqf;
- the result sound receives exactly one effective madd rule:
  `madd_munfasil` before qata, `madd_badal` at row 7, otherwise `madd_tabii`;
- row 7's core occurrence and source projection retain the after-hamza origin;
- source and cell placements put the madd occurrence on the small-yaa and
  carrier/maddah units that own or present `/i:/`. For munfasil the following
  qata is trigger-only context and is not tagged merely because it caused the
  classification; and
- the following `/ʔ/` sound does not receive the madd rule.

For `ءَات۪يٰنِۦَ`, the selected small yaa and fatha witness project `/j a/` in
the joined state and nothing at waqf. Neither sound receives a madd rule. The
following article source independently receives `hamza_wasl_silent` when joined.

## Authored ownership and acceptance checks

Yaa-zawaid are authored per riwayah, canonical ref, and boundary state. They
cannot be inferred from shared morphology alone, and a small-yaa code point is
only selected-script evidence. Canonical projection resolves each authored
fact into a neutral joined-only slot; the ordinary madd classifier then sees
the resulting long and next onset. There is no `yaa_zawaid` rule ID and no
Warsh selector.

The ordinary 46 sites may reuse the neutral `joined_only_long` model also used
by other phenomena. The Naml site requires a distinct joined-only consonant
plus vowel shape; forcing it into a vowel nucleus would lose `/j/`.

Acceptance requires:

- an exact 47-row register and corpus reconciliation;
- 46 joined `/i:/` sites split into exactly 35 `madd_tabii`, 10
  `madd_munfasil`, and one `madd_badal` site;
- the single `/j a/` site with no madd;
- complete wasl, waqf, and ibtidaa assertions, including starting at the next
  word;
- sound and character attribution for ordinary and munfasil rows; and
- no inference from Unicode scalar identity, no duration setting, and no
  runtime rule or variant named after yaa-zawaid.
