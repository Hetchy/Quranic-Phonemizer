# Madd badal and leen-mahmuz iteration log

This records the test-first reconciliation for delivery-map order 7. Domain
expectations come from `research/v2/madd-badal.md` and
`research/v2/madd-leen-mahmuz.md`, not from the previous runtime output.

| Failure or discrepancy | Classification | Resolution |
| --- | --- | --- |
| The raw source census had 304 leen-mahmuz candidates, while canonical adjacency exposed only 303. | Adapter defect | Added the missing source-only-alif bridge for `لِشَاْےْءٍ`; canonical and runtime reconciliation now proves 304 candidates and 302 emissions. |
| Initial U- and I-badal spellings projected a carrier consonant instead of a long qata. | Adapter defect | Project the reviewed initial-badal sequence as a long hamza nucleus and attach its written waw or yaa as the carrier. The 227-site A/U/I source register remains independently counted. |
| Binding ordinary badal also emitted `madd_tabii`; pure single-hamza ibdal risked being called badal. | Classifier defect | Warsh treats badal as the effective ordinary classification, while transformed badal receives an explicit semantic-origin annotation. Pure ibdal remains `ibdal_hamza + madd_tabii`. |
| Started wasl-plus-root-hamza forms initially collided with ordinary `madd_tabii`. | Classifier interaction | Added a start-only badal classifier and made ordinary madd stand down only for that exact realized-wasl/silent-root shape. Joined forms retain ordinary ibdal plus `madd_tabii`. |
| The folded `يُوَ۬اخِذُ` slot initially put both ibdal and badal on `/a:/`. | Attribution defect | Attribute `ibdal_hamza` to the replacement `/w/` and `madd_badal` to the independently owned `/a:/` carrier. |
| Existing iwad and ordinary-leen rows changed because their hidden following word begins an initial badal and now participates in naql. | Test ownership defect | Moved those unrelated negatives to clean exact corpus sites. The new naql-modified badal has its own visible two-word semantic row. |
| `مَأْو۪يٰهُم` and `مَأْو۪يٰكُم` fail their pre-existing taqlil expectations. | Later vertical | Reproduced unchanged at clean `84d38ab`; order 10 inclination owns these two failures. No order-7 expectation or runtime rule was changed to hide them. |

The leen register is independently partitioned as 297 ordinary, five plural
Saw'at, and two exact exclusions. Duration faces and route correlations remain
outside the runtime.
