# v28 Frozen Book-Edge FV Calibration

Future-only FV calibration for frozen book-edge entry lanes. No live orders.

- Any FV-ready lane: `True`
- Minimum settled rows: `30`

## Current Read

- p50_book_plus_05_edge_nonnegative: best FV variant is book_ask on 104 settled rows; blockers none.
- book_plus_05: best FV variant is book_ask on 113 settled rows; blockers none.
- book_plus_05_no_cheap_yes_boundary: best FV variant is book_ask on 111 settled rows; blockers none.

## p50_book_plus_05_edge_nonnegative

- FV ready: `True`
- Future denominator markets: `118`
- Blockers: `none`

| variant | rows | avg p | win rate | brier | brier d | logloss | logloss d |
|---|---:|---:|---:|---:|---:|---:|---:|
| book_ask | 104 | 0.581058 | 0.615385 | 0.193559 | -0.015452 | 0.568057 | -0.030286 |
| blend_25raw | 104 | 0.608704 | 0.615385 | 0.193778 | -0.015233 | 0.569264 | -0.029078 |
| disagreement_shrink | 104 | 0.633747 | 0.615385 | 0.194086 | -0.014924 | 0.568996 | -0.029347 |
| blend_50raw | 104 | 0.636351 | 0.615385 | 0.196426 | -0.012585 | 0.574466 | -0.023877 |
| raw_v28 | 104 | 0.691645 | 0.615385 | 0.209010 | 0.000000 | 0.598343 | 0.000000 |

### Source Rollups

| source | entries | settled | W-L | gross c | best variant | brier d | logloss d |
|---|---:|---:|---:|---:|---|---:|---:|
| approved_entry | 22 | 22 | 19-3 | 176.000000 | raw_v28 | 0.000000 | 0.000000 |
| rejected_actionable | 82 | 82 | 45-37 | 484.000000 | book_ask | -0.021774 | -0.046974 |

### Physics Rollups

| bucket | entries | settled | W-L | gross c | best variant | brier d | logloss d |
|---|---:|---:|---:|---:|---|---:|---:|
| high_conf_p65_plus | 52 | 52 | 41-11 | 566.000000 | blend_50raw | -0.001218 | 0.001508 |
| mid_conf_45_65 | 52 | 52 | 23-29 | 94.000000 | book_ask | -0.033578 | -0.074289 |
| yes_side | 59 | 59 | 34-25 | 328.000000 | book_ask | -0.022464 | -0.047512 |
| no_side | 45 | 45 | 30-15 | 332.000000 | disagreement_shrink | -0.011011 | -0.019387 |
| high_recross_075_plus | 32 | 32 | 20-12 | 870.000000 | raw_v28 | 0.000000 | 0.000000 |
| near_strike_sigma_lt025 | 36 | 36 | 17-19 | 426.000000 | book_ask | -0.028533 | -0.066368 |

## book_plus_05

- FV ready: `True`
- Future denominator markets: `117`
- Blockers: `none`

| variant | rows | avg p | win rate | brier | brier d | logloss | logloss d |
|---|---:|---:|---:|---:|---:|---:|---:|
| book_ask | 113 | 0.519558 | 0.495575 | 0.191091 | -0.026441 | 0.564104 | -0.057649 |
| blend_25raw | 113 | 0.546185 | 0.495575 | 0.194414 | -0.023119 | 0.573023 | -0.048730 |
| disagreement_shrink | 113 | 0.572232 | 0.495575 | 0.196750 | -0.020782 | 0.578454 | -0.043300 |
| blend_50raw | 113 | 0.572812 | 0.495575 | 0.199929 | -0.017604 | 0.585398 | -0.036355 |
| raw_v28 | 113 | 0.626066 | 0.495575 | 0.217533 | 0.000000 | 0.621754 | 0.000000 |

### Source Rollups

| source | entries | settled | W-L | gross c | best variant | brier d | logloss d |
|---|---:|---:|---:|---:|---|---:|---:|
| approved_entry | 17 | 17 | 14-3 | 62.000000 | blend_50raw | -0.001741 | -0.002507 |
| rejected_actionable | 96 | 96 | 42-54 | -576.000000 | book_ask | -0.031217 | -0.068834 |

### Physics Rollups

| bucket | entries | settled | W-L | gross c | best variant | brier d | logloss d |
|---|---:|---:|---:|---:|---|---:|---:|
| high_conf_p65_plus | 42 | 42 | 32-10 | 306.000000 | raw_v28 | 0.000000 | 0.000000 |
| mid_conf_45_65 | 57 | 57 | 21-36 | -640.000000 | book_ask | -0.049142 | -0.106397 |
| yes_side | 60 | 60 | 28-32 | -514.000000 | book_ask | -0.034086 | -0.075215 |
| no_side | 53 | 53 | 28-25 | 0.000000 | disagreement_shrink | -0.018140 | -0.036287 |
| high_recross_075_plus | 42 | 42 | 22-20 | 566.000000 | disagreement_shrink | -0.009870 | -0.019873 |
| near_strike_sigma_lt025 | 49 | 49 | 19-30 | -48.000000 | book_ask | -0.040656 | -0.090709 |

## book_plus_05_no_cheap_yes_boundary

- FV ready: `True`
- Future denominator markets: `116`
- Blockers: `none`

| variant | rows | avg p | win rate | brier | brier d | logloss | logloss d |
|---|---:|---:|---:|---:|---:|---:|---:|
| book_ask | 111 | 0.531532 | 0.522523 | 0.193305 | -0.023698 | 0.568905 | -0.051113 |
| blend_25raw | 111 | 0.557963 | 0.522523 | 0.195958 | -0.021045 | 0.576172 | -0.043846 |
| disagreement_shrink | 111 | 0.584396 | 0.522523 | 0.197468 | -0.019534 | 0.579611 | -0.040407 |
| blend_50raw | 111 | 0.584394 | 0.522523 | 0.200792 | -0.016211 | 0.586907 | -0.033110 |
| raw_v28 | 111 | 0.637257 | 0.522523 | 0.217002 | 0.000000 | 0.620018 | 0.000000 |

### Source Rollups

| source | entries | settled | W-L | gross c | best variant | brier d | logloss d |
|---|---:|---:|---:|---:|---|---:|---:|
| approved_entry | 17 | 17 | 14-3 | 62.000000 | blend_50raw | -0.001741 | -0.002507 |
| rejected_actionable | 94 | 94 | 44-50 | -234.000000 | book_ask | -0.028079 | -0.061353 |

### Physics Rollups

| bucket | entries | settled | W-L | gross c | best variant | brier d | logloss d |
|---|---:|---:|---:|---:|---|---:|---:|
| high_conf_p65_plus | 44 | 44 | 34-10 | 426.000000 | raw_v28 | 0.000000 | 0.000000 |
| mid_conf_45_65 | 57 | 57 | 21-36 | -640.000000 | book_ask | -0.049142 | -0.106397 |
| yes_side | 56 | 56 | 28-28 | -292.000000 | book_ask | -0.031448 | -0.068950 |
| no_side | 55 | 55 | 30-25 | 120.000000 | disagreement_shrink | -0.017242 | -0.034305 |
| high_recross_075_plus | 42 | 42 | 22-20 | 566.000000 | disagreement_shrink | -0.009870 | -0.019873 |
| near_strike_sigma_lt025 | 47 | 47 | 19-28 | 72.000000 | book_ask | -0.039360 | -0.087750 |
