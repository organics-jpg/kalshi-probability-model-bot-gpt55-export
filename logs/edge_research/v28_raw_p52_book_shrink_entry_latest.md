# v28 Raw p52 Book-Shrink Entry

Discovery diagnostic only. Frozen validator fixes a single variant before forward validation.

- Base policy: `v28_raw_p52_edge0`
- Rule family: `Shrink raw v28 toward executable ask only when raw - ask > 15pp, then require p>=0.52 and edge>=0.`
- Watched markets: `181`

## Ranked

| rank | policy | entries | settled | W/L | coverage | net c | avg brier | avg p | win rate | shrunk | actual/sim |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | gap15_book25_p52_edge0 | 169 | 169 | 107/62 | 93.370166 | 158.000000 | 0.211776 | 0.650554 | 0.633136 | 10 | 16/153 |
| 2 | raw_probability_p52_edge0 | 169 | 169 | 104/65 | 93.370166 | 71.000000 | 0.216062 | 0.644300 | 0.615385 | 0 | 12/157 |
| 3 | gap15_book75_p52_edge0 | 169 | 169 | 107/62 | 93.370166 | -136.000000 | 0.212633 | 0.656012 | 0.633136 | 5 | 17/152 |
| 4 | gap15_book50_p52_edge0 | 169 | 169 | 105/64 | 93.370166 | -263.000000 | 0.216259 | 0.651237 | 0.621302 | 9 | 17/152 |
