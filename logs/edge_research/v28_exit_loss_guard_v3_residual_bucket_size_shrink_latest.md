# v28 Exit Loss-Guard V3 Residual Bucket Size-Shrink Audit

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T16:15:49.008654+00:00`
- V1 freeze UTC: `2026-05-06T21:29:32.710906+00:00`
- V2 freeze UTC: `2026-05-06T22:01:04.415577+00:00`
- V3 freeze UTC: `2026-05-07T01:01:45.501061+00:00`

## Interpretation

- This is a research-only residual-bucket audit; it does not freeze a candidate or change live exits.
- The v1-only residual bucket is the extra exposure v3 currently rejects.
- Strict v3-forward residual currently has 3 row(s), 36.0c net delta, and 0.0c harmful delta.
- Diagnostic all-exit residual has 16 row(s), -14.0c net, and -186.0c harmful delta.
- The strict-forward residual is positive, but older diagnostic evidence is not; this is not enough to justify a new residual relaxation.
- Residual false-hold risk remains the binding physical risk, so any future residual overlay needs its own freeze and should probably be partial-size rather than a full hold.

## all_exit_rows_diagnostic

- Freeze UTC: `None`
- Rows: `167`
- Current net: `819.0c ($8.19)`
- V3 selected rows/delta: `38` / `765.0c ($7.65)`
- Residual v1-only rows/delta: `16` / `-14.0c ($-0.14)`
- Residual helpful/harmful: `15/1`
- Residual harmful delta: `-186.0c ($-1.86)`

| policy | residual weight | candidate c | delta c | selected rows | effective weight | residual weighted c | cushion cand/delta | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `v3_control` | 0.0 | 1584.0c ($15.84) | 765.0c ($7.65) | 38 | 38.00 | -0.0c ($-0.00) | 15/7 | none |
| `v3_plus_residual_quarter` | 0.25 | 1580.5c ($15.80) | 761.5c ($7.62) | 54 | 42.00 | -3.5c ($-0.04) | 15/7 | residual_false_hold_harm_present, residual_policy_not_independently_frozen |
| `v3_plus_residual_half` | 0.5 | 1577.0c ($15.77) | 758.0c ($7.58) | 54 | 46.00 | -7.0c ($-0.07) | 15/7 | residual_false_hold_harm_present, residual_policy_not_independently_frozen |
| `v3_plus_residual_full_v1_like` | 1.0 | 1570.0c ($15.70) | 751.0c ($7.51) | 54 | 54.00 | -14.0c ($-0.14) | 15/7 | residual_false_hold_harm_present, residual_policy_not_independently_frozen |

### Worst Residual Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY051815-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.922242 | -0.007758000000000043 | -9.224209 | 93.0 | -186.0c ($-1.86) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060215-15 | no/no | mushroom_v28_exit_value_over_hold | 0.943338 | -0.026661999999999964 | -14.333771 | 97.0 | 6.0c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY070030-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.921778 | -0.04822199999999999 | -10.177771 | 97.0 | 6.0c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060900-00 | no/no | mushroom_v28_exit_value_over_hold | 0.948348 | -0.011651999999999996 | -15.834839 | 96.0 | 8.0c ($0.08) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY052145-45 | yes/yes | mushroom_v28_exit_value_over_hold | 0.901383 | -0.04861699999999991 | -7.138269 | 95.0 | 10.0c ($0.10) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060045-45 | no/no | mushroom_v28_exit_value_over_hold | 0.939879 | -0.010120999999999936 | -8.987878 | 95.0 | 10.0c ($0.10) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060245-45 | yes/yes | mushroom_v28_exit_value_over_hold | 0.941979 | -0.008020999999999945 | -18.197939 | 95.0 | 10.0c ($0.10) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060345-45 | no/no | mushroom_v28_exit_value_over_hold | 0.940325 | -0.00967499999999999 | -16.032531 | 95.0 | 10.0c ($0.10) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |

## book_gap_freeze_comparable

- Freeze UTC: `2026-05-06T08:46:39.207330+00:00`
- Rows: `114`
- Current net: `723.0c ($7.23)`
- V3 selected rows/delta: `27` / `543.0c ($5.43)`
- Residual v1-only rows/delta: `9` / `114.0c ($1.14)`
- Residual helpful/harmful: `9/0`
- Residual harmful delta: `0.0c ($0.00)`

| policy | residual weight | candidate c | delta c | selected rows | effective weight | residual weighted c | cushion cand/delta | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `v3_control` | 0.0 | 1266.0c ($12.66) | 543.0c ($5.43) | 27 | 27.00 | 0.0c ($0.00) | 12/5 | suppressed_decisions_lt_30 |
| `v3_plus_residual_quarter` | 0.25 | 1294.5c ($12.95) | 571.5c ($5.71) | 36 | 29.25 | 28.5c ($0.28) | 12/5 | residual_policy_not_independently_frozen |
| `v3_plus_residual_half` | 0.5 | 1323.0c ($13.23) | 600.0c ($6.00) | 36 | 31.50 | 57.0c ($0.57) | 13/6 | residual_policy_not_independently_frozen |
| `v3_plus_residual_full_v1_like` | 1.0 | 1380.0c ($13.80) | 657.0c ($6.57) | 36 | 36.00 | 114.0c ($1.14) | 13/6 | residual_policy_not_independently_frozen |

### Worst Residual Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY070030-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.921778 | -0.04822199999999999 | -10.177771 | 97.0 | 6.0c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060900-00 | no/no | mushroom_v28_exit_value_over_hold | 0.948348 | -0.011651999999999996 | -15.834839 | 96.0 | 8.0c ($0.08) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060530-30 | no/no | mushroom_v28_exit_value_over_hold | 0.899953 | -0.05004699999999995 | -11.995311 | 95.0 | 10.0c ($0.10) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY061545-45 | yes/yes | mushroom_v28_exit_value_over_hold | 0.93541 | -0.014589999999999992 | -9.540987 | 95.0 | 10.0c ($0.10) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071015-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.923102 | -0.01689799999999997 | -8.310249 | 94.0 | 12.0c ($0.12) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY060715-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.920907 | -0.009093000000000018 | -11.09069 | 93.0 | 14.0c ($0.14) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY062045-45 | no/no | mushroom_v28_exit_value_over_hold | 0.891386 | -0.02861400000000003 | -9.138584 | 92.0 | 16.0c ($0.16) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY070545-45 | no/no | mushroom_v28_exit_value_over_hold | 0.892567 | -0.017433000000000032 | -7.256748 | 91.0 | 18.0c ($0.18) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |

## v1_strict_forward

- Freeze UTC: `2026-05-06T21:29:32.710906+00:00`
- Rows: `53`
- Current net: `336.0c ($3.36)`
- V3 selected rows/delta: `11` / `132.0c ($1.32)`
- Residual v1-only rows/delta: `4` / `52.0c ($0.52)`
- Residual helpful/harmful: `4/0`
- Residual harmful delta: `0.0c ($0.00)`

| policy | residual weight | candidate c | delta c | selected rows | effective weight | residual weighted c | cushion cand/delta | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `v3_control` | 0.0 | 468.0c ($4.68) | 132.0c ($1.32) | 11 | 11.00 | 0.0c ($0.00) | 4/1 | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3 |
| `v3_plus_residual_quarter` | 0.25 | 481.0c ($4.81) | 145.0c ($1.45) | 15 | 12.00 | 13.0c ($0.13) | 4/1 | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3, residual_policy_not_independently_frozen |
| `v3_plus_residual_half` | 0.5 | 494.0c ($4.94) | 158.0c ($1.58) | 15 | 13.00 | 26.0c ($0.26) | 4/1 | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3, residual_policy_not_independently_frozen |
| `v3_plus_residual_full_v1_like` | 1.0 | 520.0c ($5.20) | 184.0c ($1.84) | 15 | 15.00 | 52.0c ($0.52) | 5/1 | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3, residual_policy_not_independently_frozen |

### Worst Residual Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY070030-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.921778 | -0.04822199999999999 | -10.177771 | 97.0 | 6.0c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071015-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.923102 | -0.01689799999999997 | -8.310249 | 94.0 | 12.0c ($0.12) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY062045-45 | no/no | mushroom_v28_exit_value_over_hold | 0.891386 | -0.02861400000000003 | -9.138584 | 92.0 | 16.0c ($0.16) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY070545-45 | no/no | mushroom_v28_exit_value_over_hold | 0.892567 | -0.017433000000000032 | -7.256748 | 91.0 | 18.0c ($0.18) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |

## v2_strict_forward

- Freeze UTC: `2026-05-06T22:01:04.415577+00:00`
- Rows: `52`
- Current net: `422.0c ($4.22)`
- V3 selected rows/delta: `11` / `132.0c ($1.32)`
- Residual v1-only rows/delta: `4` / `52.0c ($0.52)`
- Residual helpful/harmful: `4/0`
- Residual harmful delta: `0.0c ($0.00)`

| policy | residual weight | candidate c | delta c | selected rows | effective weight | residual weighted c | cushion cand/delta | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `v3_control` | 0.0 | 554.0c ($5.54) | 132.0c ($1.32) | 11 | 11.00 | 0.0c ($0.00) | 5/1 | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3 |
| `v3_plus_residual_quarter` | 0.25 | 567.0c ($5.67) | 145.0c ($1.45) | 15 | 12.00 | 13.0c ($0.13) | 5/1 | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3, residual_policy_not_independently_frozen |
| `v3_plus_residual_half` | 0.5 | 580.0c ($5.80) | 158.0c ($1.58) | 15 | 13.00 | 26.0c ($0.26) | 5/1 | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3, residual_policy_not_independently_frozen |
| `v3_plus_residual_full_v1_like` | 1.0 | 606.0c ($6.06) | 184.0c ($1.84) | 15 | 15.00 | 52.0c ($0.52) | 6/1 | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3, residual_policy_not_independently_frozen |

### Worst Residual Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY070030-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.921778 | -0.04822199999999999 | -10.177771 | 97.0 | 6.0c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071015-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.923102 | -0.01689799999999997 | -8.310249 | 94.0 | 12.0c ($0.12) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY062045-45 | no/no | mushroom_v28_exit_value_over_hold | 0.891386 | -0.02861400000000003 | -9.138584 | 92.0 | 16.0c ($0.16) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY070545-45 | no/no | mushroom_v28_exit_value_over_hold | 0.892567 | -0.017433000000000032 | -7.256748 | 91.0 | 18.0c ($0.18) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |

## v3_strict_forward

- Freeze UTC: `2026-05-07T01:01:45.501061+00:00`
- Rows: `40`
- Current net: `474.0c ($4.74)`
- V3 selected rows/delta: `8` / `120.0c ($1.20)`
- Residual v1-only rows/delta: `3` / `36.0c ($0.36)`
- Residual helpful/harmful: `3/0`
- Residual harmful delta: `0.0c ($0.00)`

| policy | residual weight | candidate c | delta c | selected rows | effective weight | residual weighted c | cushion cand/delta | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `v3_control` | 0.0 | 594.0c ($5.94) | 120.0c ($1.20) | 8 | 8.00 | 0.0c ($0.00) | 5/1 | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3 |
| `v3_plus_residual_quarter` | 0.25 | 603.0c ($6.03) | 129.0c ($1.29) | 11 | 8.75 | 9.0c ($0.09) | 6/1 | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3, residual_policy_not_independently_frozen |
| `v3_plus_residual_half` | 0.5 | 612.0c ($6.12) | 138.0c ($1.38) | 11 | 9.50 | 18.0c ($0.18) | 6/1 | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3, residual_policy_not_independently_frozen |
| `v3_plus_residual_full_v1_like` | 1.0 | 630.0c ($6.30) | 156.0c ($1.56) | 11 | 11.00 | 36.0c ($0.36) | 6/1 | suppressed_decisions_lt_30, delta_full_loss_cushion_lt_3, residual_policy_not_independently_frozen |

### Worst Residual Examples

| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY070030-30 | yes/yes | mushroom_v28_exit_value_over_hold | 0.921778 | -0.04822199999999999 | -10.177771 | 97.0 | 6.0c ($0.06) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY071015-15 | yes/yes | mushroom_v28_exit_value_over_hold | 0.923102 | -0.01689799999999997 | -8.310249 | 94.0 | 12.0c ($0.12) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| KXBTC15M-26MAY070545-45 | no/no | mushroom_v28_exit_value_over_hold | 0.892567 | -0.017433000000000032 | -7.256748 | 91.0 | 18.0c ($0.18) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
