# v28 Exit Policy Strict Failure Drilldown

Research-only. No live bot changes or orders.

- Generated UTC: `2026-05-11T03:45:07.775265+00:00`
- Freeze timestamps: `{'book_gap': '2026-05-06T08:46:39.207330+00:00', 'loss_guard': '2026-05-06T21:29:32.710906+00:00', 'loss_guard_v2': '2026-05-06T22:01:04.415577+00:00', 'dual': '2026-05-06T21:15:42.381999+00:00'}`
- Strict harmful suppressions: `26`
- Strict net harm: `-3944c ($-39.44)`

## Interpretation

- new_exit_mix_common_forward_v1 has 13 harmful suppressions for -1972.0c net harm; top tags are [('probability_reduce', 9), ('p_hold_75_79', 9), ('positive_fair_drawdown', 8), ('negative_book_gap', 7)].
- new_exit_mix_common_forward_v2 has 13 harmful suppressions for -1972.0c net harm; top tags are [('probability_reduce', 9), ('p_hold_75_79', 9), ('positive_fair_drawdown', 8), ('negative_book_gap', 7)].
- Across the diagnostic exit sample, the most common harmful-suppression tag is ('probability_reduce', 15).
- A harmful suppression with negative book gap and rich executable exit is an exit-policy error, not an entry edge improvement; a safer rule should usually accept the rich exit.

## all_exit_rows_diagnostic

- Rows: `173`
- Harmful suppressions: `24`
- Net harm: `-3808c ($-38.08)`
- Avoided by loss-guard v1/v2: `21/24`
- Policy counts: `{'book_gap_soft_gap15_or_p_hold75': 9, 'dual_book_gap_else_reduce': 9, 'reduce_p_hold_ge_075': 5, 'loss_guard_v1': 1}`
- Top tags: `{'probability_reduce': 15, 'negative_book_gap': 15, 'rich_exit_80_plus': 12, 'book_disagrees_with_hold_at_rich_exit': 12, 'p_hold_75_79': 12, 'positive_fair_drawdown': 11, 'p_hold_79_85': 9, 'value_over_hold': 9}`

| policy | market | side/result | reason | p_hold | gap | drawdown | exit | delta | avoided v1/v2 | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY051815-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.922242 | -0.007758000000000043 | -9.224209 | 93.0 | -186c ($-1.86) | False/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_ge_85, deep_negative_fair_drawdown, book_disagrees_with_hold_at_rich_exit |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY051815-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.922242 | -0.007758000000000043 | -9.224209 | 93.0 | -186c ($-1.86) | False/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_ge_85, deep_negative_fair_drawdown, book_disagrees_with_hold_at_rich_exit |
| `loss_guard_v1` | KXBTC15M-26MAY051815-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.922242 | -0.007758000000000043 | -9.224209 | 93.0 | -186c ($-1.86) | False/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_ge_85, deep_negative_fair_drawdown, book_disagrees_with_hold_at_rich_exit |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY052045-45 | yes/no | mushroom_v28_exit_value_over_hold | 0.8407 | -0.05930000000000002 | -1.070049 | 90.0 | -180c ($-1.80) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, book_disagrees_with_hold_at_rich_exit |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY062015-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c ($-1.80) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, positive_fair_drawdown, book_disagrees_with_hold_at_rich_exit |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY052045-45 | yes/no | mushroom_v28_exit_value_over_hold | 0.8407 | -0.05930000000000002 | -1.070049 | 90.0 | -180c ($-1.80) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, book_disagrees_with_hold_at_rich_exit |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY062015-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c ($-1.80) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, positive_fair_drawdown, book_disagrees_with_hold_at_rich_exit |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, book_disagrees_with_hold_at_rich_exit |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, book_disagrees_with_hold_at_rich_exit |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY060700-00 | no/yes | mushroom_v28_probability_reduce | 0.799603 | -0.0003970000000000917 | 4.039746 | 80.0 | -160c ($-1.60) | True/True | probability_reduce, negative_book_gap, rich_exit_80_plus, p_hold_79_85, positive_fair_drawdown, book_disagrees_with_hold_at_rich_exit |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY060700-00 | no/yes | mushroom_v28_probability_reduce | 0.799603 | -0.0003970000000000917 | 4.039746 | 80.0 | -160c ($-1.60) | True/True | probability_reduce, negative_book_gap, rich_exit_80_plus, p_hold_79_85, positive_fair_drawdown, book_disagrees_with_hold_at_rich_exit |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY060700-00 | no/yes | mushroom_v28_probability_reduce | 0.799603 | -0.0003970000000000917 | 4.039746 | 80.0 | -160c ($-1.60) | True/True | probability_reduce, negative_book_gap, rich_exit_80_plus, p_hold_79_85, positive_fair_drawdown, book_disagrees_with_hold_at_rich_exit |

## book_gap_freeze_comparable

- Rows: `120`
- Harmful suppressions: `19`
- Net harm: `-2890c ($-28.90)`
- Avoided by loss-guard v1/v2: `19/19`
- Policy counts: `{'book_gap_soft_gap15_or_p_hold75': 7, 'dual_book_gap_else_reduce': 7, 'reduce_p_hold_ge_075': 5}`
- Top tags: `{'probability_reduce': 15, 'p_hold_75_79': 12, 'positive_fair_drawdown': 11, 'negative_book_gap': 10, 'rich_exit_80_plus': 7, 'p_hold_79_85': 7, 'book_disagrees_with_hold_at_rich_exit': 7, 'value_over_hold': 4}`

| policy | market | side/result | reason | p_hold | gap | drawdown | exit | delta | avoided v1/v2 | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY062015-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c ($-1.80) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, positive_fair_drawdown, book_disagrees_with_hold_at_rich_exit |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY062015-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c ($-1.80) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, positive_fair_drawdown, book_disagrees_with_hold_at_rich_exit |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, book_disagrees_with_hold_at_rich_exit |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, book_disagrees_with_hold_at_rich_exit |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY060700-00 | no/yes | mushroom_v28_probability_reduce | 0.799603 | -0.0003970000000000917 | 4.039746 | 80.0 | -160c ($-1.60) | True/True | probability_reduce, negative_book_gap, rich_exit_80_plus, p_hold_79_85, positive_fair_drawdown, book_disagrees_with_hold_at_rich_exit |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY060700-00 | no/yes | mushroom_v28_probability_reduce | 0.799603 | -0.0003970000000000917 | 4.039746 | 80.0 | -160c ($-1.60) | True/True | probability_reduce, negative_book_gap, rich_exit_80_plus, p_hold_79_85, positive_fair_drawdown, book_disagrees_with_hold_at_rich_exit |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY060700-00 | no/yes | mushroom_v28_probability_reduce | 0.799603 | -0.0003970000000000917 | 4.039746 | 80.0 | -160c ($-1.60) | True/True | probability_reduce, negative_book_gap, rich_exit_80_plus, p_hold_79_85, positive_fair_drawdown, book_disagrees_with_hold_at_rich_exit |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | True/True | probability_reduce, negative_book_gap, p_hold_75_79 |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | True/True | probability_reduce, negative_book_gap, p_hold_75_79 |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | True/True | probability_reduce, negative_book_gap, p_hold_75_79 |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY060900-00 | yes/no | mushroom_v28_probability_reduce | 0.78999 | 0.05998999999999999 | -0.998969 | 73.0 | -146c ($-1.46) | True/True | probability_reduce, p_hold_75_79 |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.76398 | 0.03398000000000001 | 4.602013 | 73.0 | -146c ($-1.46) | True/True | probability_reduce, p_hold_75_79, positive_fair_drawdown |

## new_exit_mix_common_forward_v1

- Rows: `59`
- Harmful suppressions: `13`
- Net harm: `-1972c ($-19.72)`
- Avoided by loss-guard v1/v2: `13/13`
- Policy counts: `{'book_gap_soft_gap15_or_p_hold75': 5, 'dual_book_gap_else_reduce': 5, 'reduce_p_hold_ge_075': 3}`
- Top tags: `{'probability_reduce': 9, 'p_hold_75_79': 9, 'positive_fair_drawdown': 8, 'negative_book_gap': 7, 'value_over_hold': 4, 'rich_exit_80_plus': 4, 'p_hold_79_85': 4, 'book_disagrees_with_hold_at_rich_exit': 4}`

| policy | market | side/result | reason | p_hold | gap | drawdown | exit | delta | avoided v1/v2 | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY062015-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c ($-1.80) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, positive_fair_drawdown, book_disagrees_with_hold_at_rich_exit |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY062015-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c ($-1.80) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, positive_fair_drawdown, book_disagrees_with_hold_at_rich_exit |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, book_disagrees_with_hold_at_rich_exit |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, book_disagrees_with_hold_at_rich_exit |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | True/True | probability_reduce, negative_book_gap, p_hold_75_79 |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | True/True | probability_reduce, negative_book_gap, p_hold_75_79 |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | True/True | probability_reduce, negative_book_gap, p_hold_75_79 |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.76398 | 0.03398000000000001 | 4.602013 | 73.0 | -146c ($-1.46) | True/True | probability_reduce, p_hold_75_79, positive_fair_drawdown |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.76398 | 0.03398000000000001 | 4.602013 | 73.0 | -146c ($-1.46) | True/True | probability_reduce, p_hold_75_79, positive_fair_drawdown |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.76398 | 0.03398000000000001 | 4.602013 | 73.0 | -146c ($-1.46) | True/True | probability_reduce, p_hold_75_79, positive_fair_drawdown |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY062130-30 | no/yes | mushroom_v28_probability_reduce | 0.768407 | 0.16840699999999997 | 6.159273 | 60.0 | -120c ($-1.20) | True/True | probability_reduce, p_hold_75_79, positive_fair_drawdown |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY062130-30 | no/yes | mushroom_v28_probability_reduce | 0.768407 | 0.16840699999999997 | 6.159273 | 60.0 | -120c ($-1.20) | True/True | probability_reduce, p_hold_75_79, positive_fair_drawdown |

## new_exit_mix_common_forward_v2

- Rows: `58`
- Harmful suppressions: `13`
- Net harm: `-1972c ($-19.72)`
- Avoided by loss-guard v1/v2: `13/13`
- Policy counts: `{'book_gap_soft_gap15_or_p_hold75': 5, 'dual_book_gap_else_reduce': 5, 'reduce_p_hold_ge_075': 3}`
- Top tags: `{'probability_reduce': 9, 'p_hold_75_79': 9, 'positive_fair_drawdown': 8, 'negative_book_gap': 7, 'value_over_hold': 4, 'rich_exit_80_plus': 4, 'p_hold_79_85': 4, 'book_disagrees_with_hold_at_rich_exit': 4}`

| policy | market | side/result | reason | p_hold | gap | drawdown | exit | delta | avoided v1/v2 | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY062015-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c ($-1.80) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, positive_fair_drawdown, book_disagrees_with_hold_at_rich_exit |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY062015-15 | yes/no | mushroom_v28_exit_value_over_hold | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c ($-1.80) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, positive_fair_drawdown, book_disagrees_with_hold_at_rich_exit |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, book_disagrees_with_hold_at_rich_exit |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c ($-1.70) | True/True | value_over_hold, negative_book_gap, rich_exit_80_plus, p_hold_79_85, book_disagrees_with_hold_at_rich_exit |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | True/True | probability_reduce, negative_book_gap, p_hold_75_79 |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | True/True | probability_reduce, negative_book_gap, p_hold_75_79 |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c ($-1.58) | True/True | probability_reduce, negative_book_gap, p_hold_75_79 |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.76398 | 0.03398000000000001 | 4.602013 | 73.0 | -146c ($-1.46) | True/True | probability_reduce, p_hold_75_79, positive_fair_drawdown |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.76398 | 0.03398000000000001 | 4.602013 | 73.0 | -146c ($-1.46) | True/True | probability_reduce, p_hold_75_79, positive_fair_drawdown |
| `dual_book_gap_else_reduce` | KXBTC15M-26MAY071015-15 | no/yes | mushroom_v28_probability_reduce | 0.76398 | 0.03398000000000001 | 4.602013 | 73.0 | -146c ($-1.46) | True/True | probability_reduce, p_hold_75_79, positive_fair_drawdown |
| `reduce_p_hold_ge_075` | KXBTC15M-26MAY062130-30 | no/yes | mushroom_v28_probability_reduce | 0.768407 | 0.16840699999999997 | 6.159273 | 60.0 | -120c ($-1.20) | True/True | probability_reduce, p_hold_75_79, positive_fair_drawdown |
| `book_gap_soft_gap15_or_p_hold75` | KXBTC15M-26MAY062130-30 | no/yes | mushroom_v28_probability_reduce | 0.768407 | 0.16840699999999997 | 6.159273 | 60.0 | -120c ($-1.20) | True/True | probability_reduce, p_hold_75_79, positive_fair_drawdown |
