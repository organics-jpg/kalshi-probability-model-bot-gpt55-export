# v28 Probability Profit Bridge

Maps settlement probability buckets to realized exit P&L and hold-to-settlement P&L.

- Surface: `actual_v28_approved_entries`
- Rows/settled: `173/173`
- Overall actual/hold/exit value: `823.000000c/2304.000000c/-1481.000000c`

## Current Read

- Overall settled win rate is 0.8439306358381503 with avg p 0.8838875953757226, actual gross 823.0c, and exit value -1481.0c.
- Worst raw/book gap bucket by actual gross is raw_above_book_15_30pp with 22 settled rows and -118.0c.
- Reentry bucket first_same_side has 116 settled rows, gross 532.0c, hold 1356.0c.
- Reentry bucket same_side_reentry has 57 settled rows, gross 291.0c, hold 948.0c.

## By Probability

| bucket | settled | W/L | avg p | win rate | cal err | actual c | hold c | exit value c | avg actual c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `p_85_875` | 91 | 76/15 | 0.858773 | 0.835165 | -0.023608 | 323.000000 | 1518.000000 | -1195.000000 | 3.549451 |
| `p_875_90` | 36 | 29/7 | 0.885288 | 0.805556 | -0.079733 | -52.000000 | 68.000000 | -120.000000 | -1.444444 |
| `p_90_95` | 35 | 32/3 | 0.922357 | 0.914286 | -0.008071 | 462.000000 | 690.000000 | -228.000000 | 13.200000 |
| `p_ge_95` | 11 | 9/2 | 0.964669 | 0.818182 | -0.146487 | 90.000000 | 28.000000 | 62.000000 | 8.181818 |

## By Edge

| bucket | settled | W/L | avg p | win rate | cal err | actual c | hold c | exit value c | avg actual c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `edge_2_4c` | 84 | 72/12 | 0.886077 | 0.857143 | -0.028934 | 314.000000 | 510.000000 | -196.000000 | 3.738095 |
| `edge_4_8c` | 44 | 38/6 | 0.881168 | 0.863636 | -0.017532 | 500.000000 | 656.000000 | -156.000000 | 11.363636 |
| `edge_8_16c` | 28 | 24/4 | 0.874390 | 0.857143 | -0.017247 | 187.000000 | 680.000000 | -493.000000 | 6.678571 |
| `edge_ge_16c` | 17 | 12/5 | 0.895751 | 0.705882 | -0.189868 | -178.000000 | 458.000000 | -636.000000 | -10.470588 |

## By Raw Book Gap

| bucket | settled | W/L | avg p | win rate | cal err | actual c | hold c | exit value c | avg actual c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `raw_above_book_15_30pp` | 22 | 17/5 | 0.877921 | 0.772727 | -0.105194 | -118.000000 | 426.000000 | -544.000000 | -5.363636 |
| `raw_above_book_5_15pp` | 146 | 127/19 | 0.883694 | 0.869863 | -0.013831 | 1035.000000 | 1852.000000 | -817.000000 | 7.089041 |
| `raw_above_book_gt_30pp` | 5 | 2/3 | 0.915795 | 0.400000 | -0.515795 | -94.000000 | 26.000000 | -120.000000 | -18.800000 |

## By Reentry

| bucket | settled | W/L | avg p | win rate | cal err | actual c | hold c | exit value c | avg actual c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `first_same_side` | 116 | 97/19 | 0.887765 | 0.836207 | -0.051558 | 532.000000 | 1356.000000 | -824.000000 | 4.586207 |
| `same_side_reentry` | 57 | 49/8 | 0.875996 | 0.859649 | -0.016347 | 291.000000 | 948.000000 | -657.000000 | 5.105263 |
