# v28 Policy x FV Matrix

- Scope: causal policy selections only.
- Purpose: avoid applying a globally good FV transform to a policy subset where it is worse.

## Best FV Variant Per Policy

| rank | policy | best variant | entries | resolved | wins | losses | coverage | gross c | avg brier | error | added rejects |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | book_plus_03_cheap_convex | v28_premium_book_anchor | 92 | 92 | 32 | 60 | 50.82872928176796 | 916.0 | 0.2148747214893475 | -0.0008265619565217541 | 92 |
| 2 | p50_book_plus_05_edge_nonnegative | book_ask_prior | 151 | 151 | 96 | 55 | 83.42541436464089 | 890.0 | 0.19363509933774836 | 0.03609271523178814 | 113 |
| 3 | book_plus_05_no_cheap_yes_boundary | book_when_v28_coinflip | 164 | 164 | 92 | 72 | 90.60773480662984 | 646.0 | 0.19587317732192683 | -0.04696328048780485 | 133 |
| 4 | baseline_v28_approved | fixed_shrink_50_v28_50_book | 107 | 107 | 91 | 16 | 59.11602209944752 | 494.0 | 0.12335219631608878 | 0.012768065420560748 | 0 |
| 5 | p55_edge_nonnegative | book_ask_prior | 151 | 151 | 100 | 51 | 83.42541436464089 | 305.0 | 0.19560993377483443 | 0.022847682119205404 | 126 |
| 6 | book_plus_05 | book_ask_prior | 169 | 169 | 89 | 80 | 93.37016574585635 | 132.0 | 0.19221656804733728 | 0.003668639053254541 | 139 |
| 7 | book_plus_02_avoid_coinflip | book_ask_prior | 171 | 171 | 91 | 80 | 94.47513812154696 | -27.0 | 0.2073654970760234 | 0.0019298245614035592 | 161 |
| 8 | book_plus_02_avoid_coinflip_liquid | book_ask_prior | 171 | 171 | 91 | 80 | 94.47513812154696 | -56.0 | 0.20660526315789476 | 0.0006432748538012234 | 160 |
| 9 | book_plus_03 | book_when_v28_coinflip_else_edge | 175 | 175 | 87 | 88 | 96.68508287292818 | -303.0 | 0.20263374546558002 | -0.049158422857142836 | 167 |
| 10 | book_plus_03_avoid_coinflip | book_ask_prior | 171 | 171 | 88 | 83 | 94.47513812154696 | -873.0 | 0.19226608187134503 | -0.016432748538011688 | 157 |
| 11 | p65_large_disagreement_anchor_plus_02 | book_ask_prior | 145 | 145 | 101 | 44 | 80.11049723756905 | -1198.0 | 0.19431034482758622 | -0.03517241379310343 | 118 |
| 12 | p65_v28_premium_anchor_plus_02 | book_ask_prior | 144 | 144 | 100 | 44 | 79.55801104972376 | -1376.0 | 0.1945486111111111 | -0.03819444444444442 | 116 |
| 13 | p65_book_plus_03 | book_ask_prior | 145 | 145 | 97 | 48 | 80.11049723756905 | -1486.0 | 0.19297931034482757 | -0.04137931034482756 | 112 |
| 14 | p65_book_plus_02 | book_ask_prior | 152 | 152 | 101 | 51 | 83.97790055248619 | -1542.0 | 0.1941638157894737 | -0.04664473684210524 | 125 |
