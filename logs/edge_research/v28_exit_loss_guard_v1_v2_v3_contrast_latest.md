# v28 Exit Loss-Guard V1/V2/V3 Contrast

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:45:02.306901+00:00`
- V1 freeze UTC: `2026-05-06T21:29:32.710906+00:00`
- V2 freeze UTC: `2026-05-06T22:01:04.415577+00:00`
- V3 freeze UTC: `2026-05-07T01:01:45.501061+00:00`

## Interpretation

- v1_v3_only is the intended V3 recovery bucket: V3 keeps rows that v2 rejects, but only when the extreme-p rule passes.
- v1_only is the lower-confidence risk bucket that V3 continues to reject.
- Only v3_strict_forward is strict evidence for V3; older windows are diagnostic/comparable only.

## all_exit_rows_diagnostic

- Freeze UTC: `None`
- Rows: `173`
- Current gross: `823c ($8.23)`

| bucket | rows | net delta | helpful | harmful | helpful delta | harmful delta | top tags |
|---|---:|---:|---:|---:|---:|---:|---|
| `all_three` | 18 | 751c ($7.51) | 18 | 0 | 751c ($7.51) | 0c ($0.00) | probability_reduce:13, p_hold_79_85:13, exitable_at_70_79:13, book_gap_5_15pp:7, fair_drawdown_shallow:7 |
| `v1_v3_only` | 21 | 60c ($0.60) | 21 | 0 | 60c ($0.60) | 0c ($0.00) | value_over_hold:21, p_hold_ge_85:21, book_gap_negative:21, fair_drawdown_deep:21, exitable_at_80_plus:21 |
| `v1_only` | 17 | -2c ($-0.02) | 16 | 1 | 184c ($1.84) | -186c ($-1.86) | value_over_hold:17, p_hold_ge_85:17, book_gap_negative:17, fair_drawdown_deep:17, exitable_at_80_plus:17 |
| `v2_v3_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `v2_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `v3_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `none` | 117 | 672c ($6.72) | 91 | 26 | 3664c ($36.64) | -2992c ($-29.92) | fair_drawdown_positive:71, p_hold_lt_75:56, exit_price_below_70:41, book_gap_negative:39, value_over_hold:34 |

### V1/V3-Only Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY051800-00 | yes/yes | mushroom_v28_exit_value_over_hold | 0.991914 | -0.008086000000000038 | -19.191381 | 100.0 | 0c ($0.00) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060830-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.992185 | -0.007815000000000016 | -23.218487 | 100.0 | 0c ($0.00) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060915-15 | no/no | mushroom_v28_exit_value_over_hold | 0.994245 | -0.005754999999999955 | -17.424453 | 100.0 | 0c ($0.00) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY051300-00 | yes/yes | mushroom_v28_exit_value_over_hold | 0.980404 | -0.009595999999999938 | -17.040444 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY051915-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.968105 | -0.021894999999999998 | -14.810535 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060145-45 | no/no | mushroom_v28_exit_value_over_hold | 0.981135 | -0.008865000000000012 | -10.113544 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060315-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.975084 | -0.01491600000000004 | -11.508394 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060445-45 | yes/yes | mushroom_v28_exit_value_over_hold | 0.980285 | -0.00971500000000003 | -8.028473 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |

### V1-Only Rejected By V3 Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY051815-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.922242 | -0.007758000000000043 | -9.224209 | 93.0 | -186c ($-1.86) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060215-15 | no/no | mushroom_v28_exit_value_over_hold | 0.943338 | -0.026661999999999964 | -14.333771 | 97.0 | 6c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY070030-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.921778 | -0.04822199999999999 | -10.177771 | 97.0 | 6c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060900-00 | no/no | mushroom_v28_exit_value_over_hold | 0.948348 | -0.011651999999999996 | -15.834839 | 96.0 | 8c ($0.08) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY052145-45 | yes/yes | mushroom_v28_exit_value_over_hold | 0.901383 | -0.04861699999999991 | -7.138269 | 95.0 | 10c ($0.10) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060045-45 | no/no | mushroom_v28_exit_value_over_hold | 0.939879 | -0.010120999999999936 | -8.987878 | 95.0 | 10c ($0.10) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060245-45 | yes/yes | mushroom_v28_exit_value_over_hold | 0.941979 | -0.008020999999999945 | -18.197939 | 95.0 | 10c ($0.10) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060345-45 | no/no | mushroom_v28_exit_value_over_hold | 0.940325 | -0.00967499999999999 | -16.032531 | 95.0 | 10c ($0.10) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |

## book_gap_freeze_comparable

- Freeze UTC: `2026-05-06T08:46:39.207330+00:00`
- Rows: `120`
- Current gross: `727c ($7.27)`

| bucket | rows | net delta | helpful | harmful | helpful delta | harmful delta | top tags |
|---|---:|---:|---:|---:|---:|---:|---|
| `all_three` | 13 | 539c ($5.39) | 13 | 0 | 539c ($5.39) | 0c ($0.00) | probability_reduce:9, p_hold_79_85:9, exitable_at_70_79:9, book_gap_5_15pp:5, fair_drawdown_positive:4 |
| `v1_v3_only` | 15 | 50c ($0.50) | 15 | 0 | 50c ($0.50) | 0c ($0.00) | value_over_hold:15, p_hold_ge_85:15, book_gap_negative:15, fair_drawdown_deep:15, exitable_at_80_plus:15 |
| `v1_only` | 10 | 126c ($1.26) | 10 | 0 | 126c ($1.26) | 0c ($0.00) | value_over_hold:10, p_hold_ge_85:10, book_gap_negative:10, fair_drawdown_deep:10, exitable_at_80_plus:10 |
| `v2_v3_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `v2_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `v3_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `none` | 82 | 996c ($9.96) | 68 | 14 | 2728c ($27.28) | -1732c ($-17.32) | fair_drawdown_positive:48, p_hold_lt_75:38, exit_price_below_70:28, book_gap_negative:27, other_exit_reason:23 |

### V1/V3-Only Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY060830-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.992185 | -0.007815000000000016 | -23.218487 | 100.0 | 0c ($0.00) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060915-15 | no/no | mushroom_v28_exit_value_over_hold | 0.994245 | -0.005754999999999955 | -17.424453 | 100.0 | 0c ($0.00) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060630-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.978151 | -0.011848999999999998 | -12.815129 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060715-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.984061 | -0.005939000000000028 | -8.406103 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY061445-45 | no/no | mushroom_v28_exit_value_over_hold | 0.981991 | -0.008009000000000044 | -8.199066 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY061830-30 | no/no | mushroom_v28_exit_value_over_hold | 0.976718 | -0.013282000000000016 | -8.671753 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY061915-15 | no/no | mushroom_v28_exit_value_over_hold | 0.981987 | -0.008012999999999937 | -11.198704 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY062115-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.982461 | -0.007538999999999962 | -10.246054 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |

### V1-Only Rejected By V3 Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY070030-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.921778 | -0.04822199999999999 | -10.177771 | 97.0 | 6c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060900-00 | no/no | mushroom_v28_exit_value_over_hold | 0.948348 | -0.011651999999999996 | -15.834839 | 96.0 | 8c ($0.08) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060530-30 | no/no | mushroom_v28_exit_value_over_hold | 0.899953 | -0.05004699999999995 | -11.995311 | 95.0 | 10c ($0.10) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY061545-45 | yes/yes | mushroom_v28_exit_value_over_hold | 0.93541 | -0.014589999999999992 | -9.540987 | 95.0 | 10c ($0.10) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071015-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.923102 | -0.01689799999999997 | -8.310249 | 94.0 | 12c ($0.12) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071315-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.927498 | -0.012501999999999902 | -14.749774 | 94.0 | 12c ($0.12) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060715-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.920907 | -0.009093000000000018 | -11.09069 | 93.0 | 14c ($0.14) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY062045-45 | no/no | mushroom_v28_exit_value_over_hold | 0.891386 | -0.02861400000000003 | -9.138584 | 92.0 | 16c ($0.16) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |

## v1_strict_forward

- Freeze UTC: `2026-05-06T21:29:32.710906+00:00`
- Rows: `59`
- Current gross: `340c ($3.40)`

| bucket | rows | net delta | helpful | harmful | helpful delta | harmful delta | top tags |
|---|---:|---:|---:|---:|---:|---:|---|
| `all_three` | 5 | 152c ($1.52) | 5 | 0 | 152c ($1.52) | 0c ($0.00) | value_over_hold:3, p_hold_ge_85:3, book_gap_negative:3, fair_drawdown_shallow:3, exitable_at_80_plus:3 |
| `v1_v3_only` | 7 | 26c ($0.26) | 7 | 0 | 26c ($0.26) | 0c ($0.00) | value_over_hold:7, p_hold_ge_85:7, book_gap_negative:7, fair_drawdown_deep:7, exitable_at_80_plus:7 |
| `v1_only` | 5 | 64c ($0.64) | 5 | 0 | 64c ($0.64) | 0c ($0.00) | value_over_hold:5, p_hold_ge_85:5, book_gap_negative:5, fair_drawdown_deep:5, exitable_at_80_plus:5 |
| `v2_v3_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `v2_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `v3_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `none` | 42 | 396c ($3.96) | 34 | 8 | 1412c ($14.12) | -1016c ($-10.16) | fair_drawdown_positive:26, book_gap_negative:21, p_hold_lt_75:19, value_over_hold:18, exit_price_below_70:11 |

### V1/V3-Only Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY061830-30 | no/no | mushroom_v28_exit_value_over_hold | 0.976718 | -0.013282000000000016 | -8.671753 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY061915-15 | no/no | mushroom_v28_exit_value_over_hold | 0.981987 | -0.008012999999999937 | -11.198704 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY062115-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.982461 | -0.007538999999999962 | -10.246054 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071145-45 | yes/yes | mushroom_v28_exit_value_over_hold | 0.982146 | -0.007854000000000028 | -17.214598 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071200-00 | no/no | mushroom_v28_exit_value_over_hold | 0.961165 | -0.018834999999999935 | -19.116535 | 98.0 | 4c ($0.04) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY070930-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.969995 | -0.01000499999999993 | -13.999536 | 98.0 | 6c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY061815-15 | no/no | mushroom_v28_exit_value_over_hold | 0.950684 | -0.009315999999999991 | -11.068394 | 96.0 | 8c ($0.08) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |

### V1-Only Rejected By V3 Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY070030-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.921778 | -0.04822199999999999 | -10.177771 | 97.0 | 6c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071015-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.923102 | -0.01689799999999997 | -8.310249 | 94.0 | 12c ($0.12) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071315-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.927498 | -0.012501999999999902 | -14.749774 | 94.0 | 12c ($0.12) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY062045-45 | no/no | mushroom_v28_exit_value_over_hold | 0.891386 | -0.02861400000000003 | -9.138584 | 92.0 | 16c ($0.16) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY070545-45 | no/no | mushroom_v28_exit_value_over_hold | 0.892567 | -0.017433000000000032 | -7.256748 | 91.0 | 18c ($0.18) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |

## v2_strict_forward

- Freeze UTC: `2026-05-06T22:01:04.415577+00:00`
- Rows: `58`
- Current gross: `426c ($4.26)`

| bucket | rows | net delta | helpful | harmful | helpful delta | harmful delta | top tags |
|---|---:|---:|---:|---:|---:|---:|---|
| `all_three` | 5 | 152c ($1.52) | 5 | 0 | 152c ($1.52) | 0c ($0.00) | value_over_hold:3, p_hold_ge_85:3, book_gap_negative:3, fair_drawdown_shallow:3, exitable_at_80_plus:3 |
| `v1_v3_only` | 7 | 26c ($0.26) | 7 | 0 | 26c ($0.26) | 0c ($0.00) | value_over_hold:7, p_hold_ge_85:7, book_gap_negative:7, fair_drawdown_deep:7, exitable_at_80_plus:7 |
| `v1_only` | 5 | 64c ($0.64) | 5 | 0 | 64c ($0.64) | 0c ($0.00) | value_over_hold:5, p_hold_ge_85:5, book_gap_negative:5, fair_drawdown_deep:5, exitable_at_80_plus:5 |
| `v2_v3_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `v2_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `v3_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `none` | 41 | 244c ($2.44) | 33 | 8 | 1260c ($12.60) | -1016c ($-10.16) | fair_drawdown_positive:25, book_gap_negative:21, p_hold_lt_75:18, value_over_hold:18, exitable_at_70_79:11 |

### V1/V3-Only Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY061830-30 | no/no | mushroom_v28_exit_value_over_hold | 0.976718 | -0.013282000000000016 | -8.671753 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY061915-15 | no/no | mushroom_v28_exit_value_over_hold | 0.981987 | -0.008012999999999937 | -11.198704 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY062115-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.982461 | -0.007538999999999962 | -10.246054 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071145-45 | yes/yes | mushroom_v28_exit_value_over_hold | 0.982146 | -0.007854000000000028 | -17.214598 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071200-00 | no/no | mushroom_v28_exit_value_over_hold | 0.961165 | -0.018834999999999935 | -19.116535 | 98.0 | 4c ($0.04) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY070930-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.969995 | -0.01000499999999993 | -13.999536 | 98.0 | 6c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY061815-15 | no/no | mushroom_v28_exit_value_over_hold | 0.950684 | -0.009315999999999991 | -11.068394 | 96.0 | 8c ($0.08) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |

### V1-Only Rejected By V3 Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY070030-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.921778 | -0.04822199999999999 | -10.177771 | 97.0 | 6c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071015-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.923102 | -0.01689799999999997 | -8.310249 | 94.0 | 12c ($0.12) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071315-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.927498 | -0.012501999999999902 | -14.749774 | 94.0 | 12c ($0.12) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY062045-45 | no/no | mushroom_v28_exit_value_over_hold | 0.891386 | -0.02861400000000003 | -9.138584 | 92.0 | 16c ($0.16) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY070545-45 | no/no | mushroom_v28_exit_value_over_hold | 0.892567 | -0.017433000000000032 | -7.256748 | 91.0 | 18c ($0.18) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |

## v3_strict_forward

- Freeze UTC: `2026-05-07T01:01:45.501061+00:00`
- Rows: `46`
- Current gross: `478c ($4.78)`

| bucket | rows | net delta | helpful | harmful | helpful delta | harmful delta | top tags |
|---|---:|---:|---:|---:|---:|---:|---|
| `all_three` | 5 | 152c ($1.52) | 5 | 0 | 152c ($1.52) | 0c ($0.00) | value_over_hold:3, p_hold_ge_85:3, book_gap_negative:3, fair_drawdown_shallow:3, exitable_at_80_plus:3 |
| `v1_v3_only` | 4 | 14c ($0.14) | 4 | 0 | 14c ($0.14) | 0c ($0.00) | value_over_hold:4, p_hold_ge_85:4, book_gap_negative:4, fair_drawdown_deep:4, exitable_at_80_plus:4 |
| `v1_only` | 4 | 48c ($0.48) | 4 | 0 | 48c ($0.48) | 0c ($0.00) | value_over_hold:4, p_hold_ge_85:4, book_gap_negative:4, fair_drawdown_deep:4, exitable_at_80_plus:4 |
| `v2_v3_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `v2_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `v3_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `none` | 33 | 60c ($0.60) | 27 | 6 | 896c ($8.96) | -836c ($-8.36) | fair_drawdown_positive:19, book_gap_negative:16, value_over_hold:13, p_hold_lt_75:13, exitable_at_70_79:10 |

### V1/V3-Only Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY062115-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.982461 | -0.007538999999999962 | -10.246054 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071145-45 | yes/yes | mushroom_v28_exit_value_over_hold | 0.982146 | -0.007854000000000028 | -17.214598 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071200-00 | no/no | mushroom_v28_exit_value_over_hold | 0.961165 | -0.018834999999999935 | -19.116535 | 98.0 | 4c ($0.04) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY070930-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.969995 | -0.01000499999999993 | -13.999536 | 98.0 | 6c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |

### V1-Only Rejected By V3 Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY070030-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.921778 | -0.04822199999999999 | -10.177771 | 97.0 | 6c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071015-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.923102 | -0.01689799999999997 | -8.310249 | 94.0 | 12c ($0.12) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071315-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.927498 | -0.012501999999999902 | -14.749774 | 94.0 | 12c ($0.12) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY070545-45 | no/no | mushroom_v28_exit_value_over_hold | 0.892567 | -0.017433000000000032 | -7.256748 | 91.0 | 18c ($0.18) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
