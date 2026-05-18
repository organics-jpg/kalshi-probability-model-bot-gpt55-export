# v28 Exit Loss-Guard V1/V2 Contrast

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:45:00.484635+00:00`
- V1 freeze UTC: `2026-05-06T21:29:32.710906+00:00`
- V2 freeze UTC: `2026-05-06T22:01:04.415577+00:00`

## Interpretation

- Rows in v1_only are the explicit cost of making v2 stricter.
- A positive v1_only net means v2 gives up winner recovery; a negative v1_only net means v2 removes harmful holds.
- Only v1_strict_forward and v2_strict_forward are strict forward evidence for their respective freezes.

## all_exit_rows_diagnostic

- Freeze UTC: `None`
- Rows: `173`
- Current gross: `823c ($8.23)`

| bucket | rows | net delta | helpful | harmful | helpful delta | harmful delta | top tags |
|---|---:|---:|---:|---:|---:|---:|---|
| `both_suppress` | 18 | 751c ($7.51) | 18 | 0 | 751c ($7.51) | 0c ($0.00) | probability_reduce:13, p_hold_79_85:13, exitable_at_70_79:13, book_gap_5_15pp:7, fair_drawdown_shallow:7 |
| `v1_only` | 38 | 58c ($0.58) | 37 | 1 | 244c ($2.44) | -186c ($-1.86) | value_over_hold:38, p_hold_ge_85:38, book_gap_negative:38, fair_drawdown_deep:38, exitable_at_80_plus:38 |
| `v2_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `neither` | 117 | 672c ($6.72) | 91 | 26 | 3664c ($36.64) | -2992c ($-29.92) | fair_drawdown_positive:71, p_hold_lt_75:56, exit_price_below_70:41, book_gap_negative:39, value_over_hold:34 |

### V1-Only Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY051815-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.922242 | -0.007758000000000043 | -9.224209 | 93.0 | -186c ($-1.86) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY051800-00 | yes/yes | mushroom_v28_exit_value_over_hold | 0.991914 | -0.008086000000000038 | -19.191381 | 100.0 | 0c ($0.00) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060830-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.992185 | -0.007815000000000016 | -23.218487 | 100.0 | 0c ($0.00) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060915-15 | no/no | mushroom_v28_exit_value_over_hold | 0.994245 | -0.005754999999999955 | -17.424453 | 100.0 | 0c ($0.00) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY051300-00 | yes/yes | mushroom_v28_exit_value_over_hold | 0.980404 | -0.009595999999999938 | -17.040444 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY051915-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.968105 | -0.021894999999999998 | -14.810535 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060145-45 | no/no | mushroom_v28_exit_value_over_hold | 0.981135 | -0.008865000000000012 | -10.113544 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060315-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.975084 | -0.01491600000000004 | -11.508394 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |

## book_gap_freeze_comparable

- Freeze UTC: `2026-05-06T08:46:39.207330+00:00`
- Rows: `120`
- Current gross: `727c ($7.27)`

| bucket | rows | net delta | helpful | harmful | helpful delta | harmful delta | top tags |
|---|---:|---:|---:|---:|---:|---:|---|
| `both_suppress` | 13 | 539c ($5.39) | 13 | 0 | 539c ($5.39) | 0c ($0.00) | probability_reduce:9, p_hold_79_85:9, exitable_at_70_79:9, book_gap_5_15pp:5, fair_drawdown_positive:4 |
| `v1_only` | 25 | 176c ($1.76) | 25 | 0 | 176c ($1.76) | 0c ($0.00) | value_over_hold:25, p_hold_ge_85:25, book_gap_negative:25, fair_drawdown_deep:25, exitable_at_80_plus:25 |
| `v2_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `neither` | 82 | 996c ($9.96) | 68 | 14 | 2728c ($27.28) | -1732c ($-17.32) | fair_drawdown_positive:48, p_hold_lt_75:38, exit_price_below_70:28, book_gap_negative:27, other_exit_reason:23 |

### V1-Only Examples

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

## v1_strict_forward

- Freeze UTC: `2026-05-06T21:29:32.710906+00:00`
- Rows: `59`
- Current gross: `340c ($3.40)`

| bucket | rows | net delta | helpful | harmful | helpful delta | harmful delta | top tags |
|---|---:|---:|---:|---:|---:|---:|---|
| `both_suppress` | 5 | 152c ($1.52) | 5 | 0 | 152c ($1.52) | 0c ($0.00) | value_over_hold:3, p_hold_ge_85:3, book_gap_negative:3, fair_drawdown_shallow:3, exitable_at_80_plus:3 |
| `v1_only` | 12 | 90c ($0.90) | 12 | 0 | 90c ($0.90) | 0c ($0.00) | value_over_hold:12, p_hold_ge_85:12, book_gap_negative:12, fair_drawdown_deep:12, exitable_at_80_plus:12 |
| `v2_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `neither` | 42 | 396c ($3.96) | 34 | 8 | 1412c ($14.12) | -1016c ($-10.16) | fair_drawdown_positive:26, book_gap_negative:21, p_hold_lt_75:19, value_over_hold:18, exit_price_below_70:11 |

### V1-Only Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY061830-30 | no/no | mushroom_v28_exit_value_over_hold | 0.976718 | -0.013282000000000016 | -8.671753 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY061915-15 | no/no | mushroom_v28_exit_value_over_hold | 0.981987 | -0.008012999999999937 | -11.198704 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY062115-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.982461 | -0.007538999999999962 | -10.246054 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071145-45 | yes/yes | mushroom_v28_exit_value_over_hold | 0.982146 | -0.007854000000000028 | -17.214598 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071200-00 | no/no | mushroom_v28_exit_value_over_hold | 0.961165 | -0.018834999999999935 | -19.116535 | 98.0 | 4c ($0.04) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY070030-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.921778 | -0.04822199999999999 | -10.177771 | 97.0 | 6c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY070930-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.969995 | -0.01000499999999993 | -13.999536 | 98.0 | 6c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY061815-15 | no/no | mushroom_v28_exit_value_over_hold | 0.950684 | -0.009315999999999991 | -11.068394 | 96.0 | 8c ($0.08) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |

## v2_strict_forward

- Freeze UTC: `2026-05-06T22:01:04.415577+00:00`
- Rows: `58`
- Current gross: `426c ($4.26)`

| bucket | rows | net delta | helpful | harmful | helpful delta | harmful delta | top tags |
|---|---:|---:|---:|---:|---:|---:|---|
| `both_suppress` | 5 | 152c ($1.52) | 5 | 0 | 152c ($1.52) | 0c ($0.00) | value_over_hold:3, p_hold_ge_85:3, book_gap_negative:3, fair_drawdown_shallow:3, exitable_at_80_plus:3 |
| `v1_only` | 12 | 90c ($0.90) | 12 | 0 | 90c ($0.90) | 0c ($0.00) | value_over_hold:12, p_hold_ge_85:12, book_gap_negative:12, fair_drawdown_deep:12, exitable_at_80_plus:12 |
| `v2_only` | 0 | 0c ($0.00) | 0 | 0 | 0c ($0.00) | 0c ($0.00) | none |
| `neither` | 41 | 244c ($2.44) | 33 | 8 | 1260c ($12.60) | -1016c ($-10.16) | fair_drawdown_positive:25, book_gap_negative:21, p_hold_lt_75:18, value_over_hold:18, exitable_at_70_79:11 |

### V1-Only Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY061830-30 | no/no | mushroom_v28_exit_value_over_hold | 0.976718 | -0.013282000000000016 | -8.671753 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY061915-15 | no/no | mushroom_v28_exit_value_over_hold | 0.981987 | -0.008012999999999937 | -11.198704 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY062115-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.982461 | -0.007538999999999962 | -10.246054 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071145-45 | yes/yes | mushroom_v28_exit_value_over_hold | 0.982146 | -0.007854000000000028 | -17.214598 | 99.0 | 2c ($0.02) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071200-00 | no/no | mushroom_v28_exit_value_over_hold | 0.961165 | -0.018834999999999935 | -19.116535 | 98.0 | 4c ($0.04) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY070030-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.921778 | -0.04822199999999999 | -10.177771 | 97.0 | 6c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY070930-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.969995 | -0.01000499999999993 | -13.999536 | 98.0 | 6c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY061815-15 | no/no | mushroom_v28_exit_value_over_hold | 0.950684 | -0.009315999999999991 | -11.068394 | 96.0 | 8c ($0.08) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
