# v28 Exit Policy Common-Clock Watch

Research-only. No live bot changes or orders.

- Generated UTC: `2026-05-11T03:47:29.009944+00:00`
- Strict common-forward windows: `{'new_exit_mix_common_forward_v1': '2026-05-06T21:29:32.710906+00:00', 'new_exit_mix_common_forward_v2': '2026-05-06T22:01:04.415577+00:00', 'new_exit_mix_common_forward_v3': '2026-05-07T01:01:45.501061+00:00'}`
- Freeze timestamps: `{'reduce': '2026-05-06T06:33:56.987999+00:00', 'book_gap': '2026-05-06T08:46:39.207330+00:00', 'loss_guard': '2026-05-06T21:29:32.710906+00:00', 'loss_guard_v2': '2026-05-06T22:01:04.415577+00:00', 'loss_guard_v3': '2026-05-07T01:01:45.501061+00:00', 'dual': '2026-05-06T21:15:42.381999+00:00'}`

## Interpretation

- Only the new_exit_mix_common_forward_* windows are strict forward evidence for newly frozen exit-mix branches.
- The v1/v2/v3 common windows each start from that branch's own shared/freeze clock; later branches are not credited inside older strict windows.
- All older windows are diagnostic/comparable only.
- new_exit_mix_common_forward_v1 has 59 rows; best policy loss_guard_value_p85_reduce_p79_gap0 has net 582.0c and blockers ['suppressed_decisions_lt_30'].
- new_exit_mix_common_forward_v1 best loss-count reducer is reduce_p_hold_ge_075 with loss-count reduction 4 and delta -126.0c.
- new_exit_mix_common_forward_v2 has 58 rows; best policy loss_guard_value_p85_reduce_p79_gap0 has net 668.0c and blockers ['suppressed_decisions_lt_30'].
- new_exit_mix_common_forward_v2 best loss-count reducer is reduce_p_hold_ge_075 with loss-count reduction 4 and delta -126.0c.
- new_exit_mix_common_forward_v3 has 46 rows; best policy loss_guard_value_p85_reduce_p79_gap0 has net 692.0c and blockers ['suppressed_decisions_lt_30'].
- new_exit_mix_common_forward_v3 best loss-count reducer is reduce_p_hold_ge_075 with loss-count reduction 4 and delta -126.0c.
- Comparable book-gap-freeze window best policy is loss_guard_value_p85_reduce_p79_gap0 with net 1442.0c and loss cost 0c.

## all_exit_rows_diagnostic

- Freeze UTC: `None`
- Rows: `173`

| rank | policy | settled | current W/L | candidate W/L | loss count delta | current | candidate | delta | suppressed | winner recovery | loss cost | cushion | pass | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `loss_guard_v3_value_gap0_or_p85_shallow_or_p95_extreme_reduce_p79_gap0` | 173 | 98/75 | 109/64 | 11 | 823c ($8.23) | 1634c ($16.34) | 811c ($8.11) | 39 | 811c ($8.11) | 0c ($0.00) | 16 | True | none |
| 2 | `loss_guard_value_p85_reduce_p79_gap0` | 173 | 98/75 | 108/65 | 10 | 823c ($8.23) | 1632c ($16.32) | 809c ($8.09) | 56 | 995c ($9.95) | -186c ($-1.86) | 16 | False | loss_control_cost_negative |
| 3 | `loss_guard_v2_value_gap0_or_p85_shallowdd_reduce_p79_gap0` | 173 | 98/75 | 109/64 | 11 | 823c ($8.23) | 1574c ($15.74) | 751c ($7.51) | 18 | 751c ($7.51) | 0c ($0.00) | 15 | False | suppressed_decisions_lt_30 |
| 4 | `reduce_p_hold_ge_075` | 173 | 98/75 | 118/55 | 20 | 823c ($8.23) | 1424c ($14.24) | 601c ($6.01) | 30 | 1331c ($13.31) | -730c ($-7.30) | 14 | False | loss_control_cost_negative |
| 5 | `book_gap_soft_gap15_or_p_hold75` | 173 | 98/75 | 115/58 | 17 | 823c ($8.23) | 1396c ($13.96) | 573c ($5.73) | 89 | 2019c ($20.19) | -1446c ($-14.46) | 13 | False | loss_control_cost_negative |
| 6 | `dual_book_gap_else_reduce` | 173 | 98/75 | 115/58 | 17 | 823c ($8.23) | 1396c ($13.96) | 573c ($5.73) | 89 | 2019c ($20.19) | -1446c ($-14.46) | 13 | False | loss_control_cost_negative |
| 7 | `current_v28_exit` | 173 | 98/75 | 98/75 | 0 | 823c ($8.23) | 823c ($8.23) | 0c ($0.00) | 0 | 0c ($0.00) | 0c ($0.00) | 8 | False | suppressed_decisions_lt_30, delta_vs_current_not_positive |

### Suppressed Loss Tags

| policy | helpful/harmful suppressed | loss cost | top harmful tags |
|---|---:|---:|---|
| `loss_guard_v3_value_gap0_or_p85_shallow_or_p95_extreme_reduce_p79_gap0` | 39/0 | 0c ($0.00) | none |
| `loss_guard_value_p85_reduce_p79_gap0` | 55/1 | -186c ($-1.86) | value_over_hold:1, p_hold_ge_85:1, book_gap_negative:1, fair_drawdown_deep:1, exitable_at_80_plus:1 |
| `loss_guard_v2_value_gap0_or_p85_shallowdd_reduce_p79_gap0` | 18/0 | 0c ($0.00) | none |
| `reduce_p_hold_ge_075` | 25/5 | -730c ($-7.30) | probability_reduce:5, p_hold_75_79:4, fair_drawdown_positive:3, exitable_at_70_79:3, book_gap_negative:2, fair_drawdown_shallow:2 |
| `book_gap_soft_gap15_or_p_hold75` | 80/9 | -1446c ($-14.46) | book_gap_negative:6, exitable_at_80_plus:5, probability_reduce:5, value_over_hold:4, p_hold_79_85:4, fair_drawdown_shallow:4 |
| `dual_book_gap_else_reduce` | 80/9 | -1446c ($-14.46) | book_gap_negative:6, exitable_at_80_plus:5, probability_reduce:5, value_over_hold:4, p_hold_79_85:4, fair_drawdown_shallow:4 |
| `current_v28_exit` | 0/0 | 0c ($0.00) | none |

### Worst Suppressed-Loss Examples

| policy | market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| `loss_guard_value_p85_reduce_p79_gap0` | KXBTC15M-26MAY051815-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.922242 | -0.007758000000000043 | -9.224209 | 93.0 | -186c ($-1.86) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY051815-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.922242 | -0.007758000000000043 | -9.224209 | 93.0 | -186c ($-1.86) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY051815-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.922242 | -0.007758000000000043 | -9.224209 | 93.0 | -186c ($-1.86) | value_over_hold, p_hold_ge_85, book_gap_negative, fair_drawdown_deep, exitable_at_80_plus |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY052045-45 | yes/no | mushroom_v28_exit_value_over_hold | 0.8407 | -0.05930000000000002 | -1.070049 | 90.0 | -180c ($-1.80) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_shallow, exitable_at_80_plus |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY062015-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c ($-1.80) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_positive, exitable_at_80_plus |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY052045-45 | yes/no | mushroom_v28_exit_value_over_hold | 0.8407 | -0.05930000000000002 | -1.070049 | 90.0 | -180c ($-1.80) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_shallow, exitable_at_80_plus |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY062015-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c ($-1.80) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_positive, exitable_at_80_plus |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_shallow, exitable_at_80_plus |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_shallow, exitable_at_80_plus |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY060700-00 | no/yes | mushroom_v28_probability_reduce | 0.799603 | -0.0003970000000000917 | 4.039746 | 80.0 | -160c ($-1.60) | probability_reduce, p_hold_79_85, book_gap_negative, fair_drawdown_positive, exitable_at_80_plus |

## book_gap_freeze_comparable

- Freeze UTC: `2026-05-06T08:46:39.207330+00:00`
- Rows: `120`

| rank | policy | settled | current W/L | candidate W/L | loss count delta | current | candidate | delta | suppressed | winner recovery | loss cost | cushion | pass | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `loss_guard_value_p85_reduce_p79_gap0` | 120 | 71/49 | 78/42 | 7 | 727c ($7.27) | 1442c ($14.42) | 715c ($7.15) | 38 | 715c ($7.15) | 0c ($0.00) | 14 | True | none |
| 2 | `loss_guard_v3_value_gap0_or_p85_shallow_or_p95_extreme_reduce_p79_gap0` | 120 | 71/49 | 78/42 | 7 | 727c ($7.27) | 1316c ($13.16) | 589c ($5.89) | 28 | 589c ($5.89) | 0c ($0.00) | 13 | False | suppressed_decisions_lt_30 |
| 3 | `loss_guard_v2_value_gap0_or_p85_shallowdd_reduce_p79_gap0` | 120 | 71/49 | 78/42 | 7 | 727c ($7.27) | 1266c ($12.66) | 539c ($5.39) | 13 | 539c ($5.39) | 0c ($0.00) | 12 | False | suppressed_decisions_lt_30 |
| 4 | `book_gap_soft_gap15_or_p_hold75` | 120 | 71/49 | 82/38 | 11 | 727c ($7.27) | 962c ($9.62) | 235c ($2.35) | 59 | 1315c ($13.15) | -1080c ($-10.80) | 9 | False | loss_control_cost_negative |
| 5 | `dual_book_gap_else_reduce` | 120 | 71/49 | 82/38 | 11 | 727c ($7.27) | 962c ($9.62) | 235c ($2.35) | 59 | 1315c ($13.15) | -1080c ($-10.80) | 9 | False | loss_control_cost_negative |
| 6 | `reduce_p_hold_ge_075` | 120 | 71/49 | 84/36 | 13 | 727c ($7.27) | 902c ($9.02) | 175c ($1.75) | 22 | 905c ($9.05) | -730c ($-7.30) | 9 | False | suppressed_decisions_lt_30, loss_control_cost_negative |
| 7 | `current_v28_exit` | 120 | 71/49 | 71/49 | 0 | 727c ($7.27) | 727c ($7.27) | 0c ($0.00) | 0 | 0c ($0.00) | 0c ($0.00) | 7 | False | suppressed_decisions_lt_30, delta_vs_current_not_positive |

### Suppressed Loss Tags

| policy | helpful/harmful suppressed | loss cost | top harmful tags |
|---|---:|---:|---|
| `loss_guard_value_p85_reduce_p79_gap0` | 38/0 | 0c ($0.00) | none |
| `loss_guard_v3_value_gap0_or_p85_shallow_or_p95_extreme_reduce_p79_gap0` | 28/0 | 0c ($0.00) | none |
| `loss_guard_v2_value_gap0_or_p85_shallowdd_reduce_p79_gap0` | 13/0 | 0c ($0.00) | none |
| `book_gap_soft_gap15_or_p_hold75` | 52/7 | -1080c ($-10.80) | probability_reduce:5, book_gap_negative:4, fair_drawdown_positive:4, p_hold_75_79:4, p_hold_79_85:3, exitable_at_80_plus:3 |
| `dual_book_gap_else_reduce` | 52/7 | -1080c ($-10.80) | probability_reduce:5, book_gap_negative:4, fair_drawdown_positive:4, p_hold_75_79:4, p_hold_79_85:3, exitable_at_80_plus:3 |
| `reduce_p_hold_ge_075` | 17/5 | -730c ($-7.30) | probability_reduce:5, p_hold_75_79:4, fair_drawdown_positive:3, exitable_at_70_79:3, book_gap_negative:2, fair_drawdown_shallow:2 |
| `current_v28_exit` | 0/0 | 0c ($0.00) | none |

### Worst Suppressed-Loss Examples

| policy | market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY062015-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c ($-1.80) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_positive, exitable_at_80_plus |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY062015-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c ($-1.80) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_positive, exitable_at_80_plus |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_shallow, exitable_at_80_plus |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_shallow, exitable_at_80_plus |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY060700-00 | no/yes | mushroom_v28_probability_reduce | 0.799603 | -0.0003970000000000917 | 4.039746 | 80.0 | -160c ($-1.60) | probability_reduce, p_hold_79_85, book_gap_negative, fair_drawdown_positive, exitable_at_80_plus |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY060700-00 | no/yes | mushroom_v28_probability_reduce | 0.799603 | -0.0003970000000000917 | 4.039746 | 80.0 | -160c ($-1.60) | probability_reduce, p_hold_79_85, book_gap_negative, fair_drawdown_positive, exitable_at_80_plus |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY060700-00 | no/yes | mushroom_v28_probability_reduce | 0.799603 | -0.0003970000000000917 | 4.039746 | 80.0 | -160c ($-1.60) | probability_reduce, p_hold_79_85, book_gap_negative, fair_drawdown_positive, exitable_at_80_plus |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_shallow, exitable_at_70_79 |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_shallow, exitable_at_70_79 |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_shallow, exitable_at_70_79 |

## new_exit_mix_common_forward_v1

- Freeze UTC: `2026-05-06T21:29:32.710906+00:00`
- Rows: `59`

| rank | policy | settled | current W/L | candidate W/L | loss count delta | current | candidate | delta | suppressed | winner recovery | loss cost | cushion | pass | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `loss_guard_value_p85_reduce_p79_gap0` | 59 | 39/20 | 41/18 | 2 | 340c ($3.40) | 582c ($5.82) | 242c ($2.42) | 17 | 242c ($2.42) | 0c ($0.00) | 5 | False | suppressed_decisions_lt_30 |
| 2 | `loss_guard_v2_value_gap0_or_p85_shallowdd_reduce_p79_gap0` | 59 | 39/20 | 41/18 | 2 | 340c ($3.40) | 492c ($4.92) | 152c ($1.52) | 5 | 152c ($1.52) | 0c ($0.00) | 4 | False | suppressed_decisions_lt_30 |
| 3 | `current_v28_exit` | 59 | 39/20 | 39/20 | 0 | 340c ($3.40) | 340c ($3.40) | 0c ($0.00) | 0 | 0c ($0.00) | 0c ($0.00) | 3 | False | suppressed_decisions_lt_30, delta_vs_current_not_positive |
| 4 | `reduce_p_hold_ge_075` | 59 | 39/20 | 43/16 | 4 | 340c ($3.40) | 214c ($2.14) | -126c ($-1.26) | 9 | 298c ($2.98) | -424c ($-4.24) | 2 | False | suppressed_decisions_lt_30, delta_vs_current_not_positive, loss_control_cost_negative, full_loss_cushion_lt_3 |
| 5 | `book_gap_soft_gap15_or_p_hold75` | 59 | 39/20 | 41/18 | 2 | 340c ($3.40) | 128c ($1.28) | -212c ($-2.12) | 30 | 562c ($5.62) | -774c ($-7.74) | 1 | False | delta_vs_current_not_positive, loss_control_cost_negative, full_loss_cushion_lt_3 |
| 6 | `dual_book_gap_else_reduce` | 59 | 39/20 | 41/18 | 2 | 340c ($3.40) | 128c ($1.28) | -212c ($-2.12) | 30 | 562c ($5.62) | -774c ($-7.74) | 1 | False | delta_vs_current_not_positive, loss_control_cost_negative, full_loss_cushion_lt_3 |

### Suppressed Loss Tags

| policy | helpful/harmful suppressed | loss cost | top harmful tags |
|---|---:|---:|---|
| `loss_guard_value_p85_reduce_p79_gap0` | 17/0 | 0c ($0.00) | none |
| `loss_guard_v2_value_gap0_or_p85_shallowdd_reduce_p79_gap0` | 5/0 | 0c ($0.00) | none |
| `current_v28_exit` | 0/0 | 0c ($0.00) | none |
| `reduce_p_hold_ge_075` | 6/3 | -424c ($-4.24) | probability_reduce:3, p_hold_75_79:3, fair_drawdown_positive:2, exitable_at_70_79:2, book_gap_ge_15pp:1, exit_price_below_70:1 |
| `book_gap_soft_gap15_or_p_hold75` | 25/5 | -774c ($-7.74) | book_gap_negative:3, fair_drawdown_positive:3, probability_reduce:3, p_hold_75_79:3, value_over_hold:2, p_hold_79_85:2 |
| `dual_book_gap_else_reduce` | 25/5 | -774c ($-7.74) | book_gap_negative:3, fair_drawdown_positive:3, probability_reduce:3, p_hold_75_79:3, value_over_hold:2, p_hold_79_85:2 |

### Worst Suppressed-Loss Examples

| policy | market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY062015-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c ($-1.80) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_positive, exitable_at_80_plus |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY062015-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c ($-1.80) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_positive, exitable_at_80_plus |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_shallow, exitable_at_80_plus |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_shallow, exitable_at_80_plus |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_shallow, exitable_at_70_79 |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_shallow, exitable_at_70_79 |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_shallow, exitable_at_70_79 |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.76398 | 0.03398000000000001 | 4.602013 | 73.0 | -146c ($-1.46) | probability_reduce, p_hold_75_79, book_gap_0_5pp, fair_drawdown_positive, exitable_at_70_79 |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.76398 | 0.03398000000000001 | 4.602013 | 73.0 | -146c ($-1.46) | probability_reduce, p_hold_75_79, book_gap_0_5pp, fair_drawdown_positive, exitable_at_70_79 |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.76398 | 0.03398000000000001 | 4.602013 | 73.0 | -146c ($-1.46) | probability_reduce, p_hold_75_79, book_gap_0_5pp, fair_drawdown_positive, exitable_at_70_79 |

## new_exit_mix_common_forward_v2

- Freeze UTC: `2026-05-06T22:01:04.415577+00:00`
- Rows: `58`

| rank | policy | settled | current W/L | candidate W/L | loss count delta | current | candidate | delta | suppressed | winner recovery | loss cost | cushion | pass | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `loss_guard_value_p85_reduce_p79_gap0` | 58 | 39/19 | 41/17 | 2 | 426c ($4.26) | 668c ($6.68) | 242c ($2.42) | 17 | 242c ($2.42) | 0c ($0.00) | 6 | False | suppressed_decisions_lt_30 |
| 2 | `loss_guard_v2_value_gap0_or_p85_shallowdd_reduce_p79_gap0` | 58 | 39/19 | 41/17 | 2 | 426c ($4.26) | 578c ($5.78) | 152c ($1.52) | 5 | 152c ($1.52) | 0c ($0.00) | 5 | False | suppressed_decisions_lt_30 |
| 3 | `current_v28_exit` | 58 | 39/19 | 39/19 | 0 | 426c ($4.26) | 426c ($4.26) | 0c ($0.00) | 0 | 0c ($0.00) | 0c ($0.00) | 4 | False | suppressed_decisions_lt_30, delta_vs_current_not_positive |
| 4 | `reduce_p_hold_ge_075` | 58 | 39/19 | 43/15 | 4 | 426c ($4.26) | 300c ($3.00) | -126c ($-1.26) | 9 | 298c ($2.98) | -424c ($-4.24) | 3 | False | suppressed_decisions_lt_30, delta_vs_current_not_positive, loss_control_cost_negative |
| 5 | `book_gap_soft_gap15_or_p_hold75` | 58 | 39/19 | 41/17 | 2 | 426c ($4.26) | 214c ($2.14) | -212c ($-2.12) | 30 | 562c ($5.62) | -774c ($-7.74) | 2 | False | delta_vs_current_not_positive, loss_control_cost_negative, full_loss_cushion_lt_3 |
| 6 | `dual_book_gap_else_reduce` | 58 | 39/19 | 41/17 | 2 | 426c ($4.26) | 214c ($2.14) | -212c ($-2.12) | 30 | 562c ($5.62) | -774c ($-7.74) | 2 | False | delta_vs_current_not_positive, loss_control_cost_negative, full_loss_cushion_lt_3 |

### Suppressed Loss Tags

| policy | helpful/harmful suppressed | loss cost | top harmful tags |
|---|---:|---:|---|
| `loss_guard_value_p85_reduce_p79_gap0` | 17/0 | 0c ($0.00) | none |
| `loss_guard_v2_value_gap0_or_p85_shallowdd_reduce_p79_gap0` | 5/0 | 0c ($0.00) | none |
| `current_v28_exit` | 0/0 | 0c ($0.00) | none |
| `reduce_p_hold_ge_075` | 6/3 | -424c ($-4.24) | probability_reduce:3, p_hold_75_79:3, fair_drawdown_positive:2, exitable_at_70_79:2, book_gap_ge_15pp:1, exit_price_below_70:1 |
| `book_gap_soft_gap15_or_p_hold75` | 25/5 | -774c ($-7.74) | book_gap_negative:3, fair_drawdown_positive:3, probability_reduce:3, p_hold_75_79:3, value_over_hold:2, p_hold_79_85:2 |
| `dual_book_gap_else_reduce` | 25/5 | -774c ($-7.74) | book_gap_negative:3, fair_drawdown_positive:3, probability_reduce:3, p_hold_75_79:3, value_over_hold:2, p_hold_79_85:2 |

### Worst Suppressed-Loss Examples

| policy | market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY062015-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c ($-1.80) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_positive, exitable_at_80_plus |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY062015-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c ($-1.80) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_positive, exitable_at_80_plus |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_shallow, exitable_at_80_plus |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_shallow, exitable_at_80_plus |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_shallow, exitable_at_70_79 |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_shallow, exitable_at_70_79 |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_shallow, exitable_at_70_79 |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.76398 | 0.03398000000000001 | 4.602013 | 73.0 | -146c ($-1.46) | probability_reduce, p_hold_75_79, book_gap_0_5pp, fair_drawdown_positive, exitable_at_70_79 |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.76398 | 0.03398000000000001 | 4.602013 | 73.0 | -146c ($-1.46) | probability_reduce, p_hold_75_79, book_gap_0_5pp, fair_drawdown_positive, exitable_at_70_79 |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.76398 | 0.03398000000000001 | 4.602013 | 73.0 | -146c ($-1.46) | probability_reduce, p_hold_75_79, book_gap_0_5pp, fair_drawdown_positive, exitable_at_70_79 |

## new_exit_mix_common_forward_v3

- Freeze UTC: `2026-05-07T01:01:45.501061+00:00`
- Rows: `46`

| rank | policy | settled | current W/L | candidate W/L | loss count delta | current | candidate | delta | suppressed | winner recovery | loss cost | cushion | pass | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `loss_guard_value_p85_reduce_p79_gap0` | 46 | 31/15 | 33/13 | 2 | 478c ($4.78) | 692c ($6.92) | 214c ($2.14) | 13 | 214c ($2.14) | 0c ($0.00) | 6 | False | suppressed_decisions_lt_30 |
| 2 | `loss_guard_v3_value_gap0_or_p85_shallow_or_p95_extreme_reduce_p79_gap0` | 46 | 31/15 | 33/13 | 2 | 478c ($4.78) | 644c ($6.44) | 166c ($1.66) | 9 | 166c ($1.66) | 0c ($0.00) | 6 | False | suppressed_decisions_lt_30 |
| 3 | `loss_guard_v2_value_gap0_or_p85_shallowdd_reduce_p79_gap0` | 46 | 31/15 | 33/13 | 2 | 478c ($4.78) | 630c ($6.30) | 152c ($1.52) | 5 | 152c ($1.52) | 0c ($0.00) | 6 | False | suppressed_decisions_lt_30 |
| 4 | `current_v28_exit` | 46 | 31/15 | 31/15 | 0 | 478c ($4.78) | 478c ($4.78) | 0c ($0.00) | 0 | 0c ($0.00) | 0c ($0.00) | 4 | False | suppressed_decisions_lt_30, delta_vs_current_not_positive |
| 5 | `book_gap_soft_gap15_or_p_hold75` | 46 | 31/15 | 34/12 | 3 | 478c ($4.78) | 418c ($4.18) | -60c ($-0.60) | 25 | 534c ($5.34) | -594c ($-5.94) | 4 | False | suppressed_decisions_lt_30, delta_vs_current_not_positive, loss_control_cost_negative |
| 6 | `dual_book_gap_else_reduce` | 46 | 31/15 | 34/12 | 3 | 478c ($4.78) | 418c ($4.18) | -60c ($-0.60) | 25 | 534c ($5.34) | -594c ($-5.94) | 4 | False | suppressed_decisions_lt_30, delta_vs_current_not_positive, loss_control_cost_negative |
| 7 | `reduce_p_hold_ge_075` | 46 | 31/15 | 35/11 | 4 | 478c ($4.78) | 352c ($3.52) | -126c ($-1.26) | 9 | 298c ($2.98) | -424c ($-4.24) | 3 | False | suppressed_decisions_lt_30, delta_vs_current_not_positive, loss_control_cost_negative |

### Suppressed Loss Tags

| policy | helpful/harmful suppressed | loss cost | top harmful tags |
|---|---:|---:|---|
| `loss_guard_value_p85_reduce_p79_gap0` | 13/0 | 0c ($0.00) | none |
| `loss_guard_v3_value_gap0_or_p85_shallow_or_p95_extreme_reduce_p79_gap0` | 9/0 | 0c ($0.00) | none |
| `loss_guard_v2_value_gap0_or_p85_shallowdd_reduce_p79_gap0` | 5/0 | 0c ($0.00) | none |
| `current_v28_exit` | 0/0 | 0c ($0.00) | none |
| `book_gap_soft_gap15_or_p_hold75` | 21/4 | -594c ($-5.94) | probability_reduce:3, p_hold_75_79:3, fair_drawdown_positive:2, book_gap_negative:2, fair_drawdown_shallow:2, exitable_at_70_79:2 |
| `dual_book_gap_else_reduce` | 21/4 | -594c ($-5.94) | probability_reduce:3, p_hold_75_79:3, fair_drawdown_positive:2, book_gap_negative:2, fair_drawdown_shallow:2, exitable_at_70_79:2 |
| `reduce_p_hold_ge_075` | 6/3 | -424c ($-4.24) | probability_reduce:3, p_hold_75_79:3, fair_drawdown_positive:2, exitable_at_70_79:2, book_gap_ge_15pp:1, exit_price_below_70:1 |

### Worst Suppressed-Loss Examples

| policy | market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_shallow, exitable_at_80_plus |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | value_over_hold, p_hold_79_85, book_gap_negative, fair_drawdown_shallow, exitable_at_80_plus |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_shallow, exitable_at_70_79 |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_shallow, exitable_at_70_79 |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_shallow, exitable_at_70_79 |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.76398 | 0.03398000000000001 | 4.602013 | 73.0 | -146c ($-1.46) | probability_reduce, p_hold_75_79, book_gap_0_5pp, fair_drawdown_positive, exitable_at_70_79 |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.76398 | 0.03398000000000001 | 4.602013 | 73.0 | -146c ($-1.46) | probability_reduce, p_hold_75_79, book_gap_0_5pp, fair_drawdown_positive, exitable_at_70_79 |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.76398 | 0.03398000000000001 | 4.602013 | 73.0 | -146c ($-1.46) | probability_reduce, p_hold_75_79, book_gap_0_5pp, fair_drawdown_positive, exitable_at_70_79 |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY062130-30 | no/yes | mushroom_v28_probability_reduce | 0.768407 | 0.16840699999999997 | 6.159273 | 60.0 | -120c ($-1.20) | probability_reduce, p_hold_75_79, book_gap_ge_15pp, fair_drawdown_positive, exit_price_below_70 |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY062130-30 | no/yes | mushroom_v28_probability_reduce | 0.768407 | 0.16840699999999997 | 6.159273 | 60.0 | -120c ($-1.20) | probability_reduce, p_hold_75_79, book_gap_ge_15pp, fair_drawdown_positive, exit_price_below_70 |
