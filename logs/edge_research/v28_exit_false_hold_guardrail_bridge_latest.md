# v28 Exit False-Hold Guardrail Bridge

Research-only bridge. No live bot changes or orders.

- Generated UTC: `2026-05-07T17:51:27.986974+00:00`
- Strict harmful suppressions: `26`
- Strict net harm: `-3944c`
- Harmful policy examples in strict windows: `24`
- Unique harmful policy examples: `24`

## Interpretation

- Strict harmful suppressions are the false-hold side of the exit problem.
- Promotion should require candidate exits to avoid these states, not only show positive clipped-winner recovery.
- Top strict guardrail tags: `{'exit_cents_gte60': 24, 'p_hold_75_85': 24, 'p_hold_75_79': 16, 'probability_reduce': 16, 'negative_book_gap': 14, 'positive_fair_drawdown': 14, 'book_disagrees_with_hold_at_rich_exit': 8, 'exit_cents_gte80': 8, 'p_hold_79_85': 8, 'rich_exit_80_plus': 8, 'value_over_hold': 8, 'positive_book_gap_ge05': 4}`

## Strict Window Guardrails

| window | rows | harmful | net harm | top tags | policies |
|---|---:|---:|---:|---|---|
| `new_exit_mix_common_forward_v1` | 59 | 13 | -1972c | `{'exit_cents_gte60': 12, 'p_hold_75_85': 12, 'p_hold_75_79': 8, 'probability_reduce': 8, 'negative_book_gap': 7, 'positive_fair_drawdown': 7, 'book_disagrees_with_hold_at_rich_exit': 4, 'exit_cents_gte80': 4, 'p_hold_79_85': 4, 'rich_exit_80_plus': 4, 'value_over_hold': 4, 'positive_book_gap_ge05': 2}` | `{'book_gap_soft_gap15_or_p_hold75': 5, 'dual_book_gap_else_reduce': 4, 'reduce_p_hold_ge_075': 3}` |
| `new_exit_mix_common_forward_v2` | 58 | 13 | -1972c | `{'exit_cents_gte60': 12, 'p_hold_75_85': 12, 'p_hold_75_79': 8, 'probability_reduce': 8, 'negative_book_gap': 7, 'positive_fair_drawdown': 7, 'book_disagrees_with_hold_at_rich_exit': 4, 'exit_cents_gte80': 4, 'p_hold_79_85': 4, 'rich_exit_80_plus': 4, 'value_over_hold': 4, 'positive_book_gap_ge05': 2}` | `{'book_gap_soft_gap15_or_p_hold75': 5, 'dual_book_gap_else_reduce': 4, 'reduce_p_hold_ge_075': 3}` |

## Policy Harm

| policy | harmful rows | net harm | avoid-tag overlap rows | top tags |
|---|---:|---:|---:|---|
| `book_gap_soft_gap15_or_p_hold75` | 10 | -1548c | 0 | `{'exit_cents_gte60': 10, 'p_hold_75_85': 10, 'negative_book_gap': 6, 'positive_fair_drawdown': 6, 'p_hold_75_79': 6, 'probability_reduce': 6, 'book_disagrees_with_hold_at_rich_exit': 4, 'exit_cents_gte80': 4, 'p_hold_79_85': 4, 'rich_exit_80_plus': 4}` |
| `dual_book_gap_else_reduce` | 8 | -1308c | 0 | `{'exit_cents_gte60': 8, 'p_hold_75_85': 8, 'negative_book_gap': 6, 'book_disagrees_with_hold_at_rich_exit': 4, 'exit_cents_gte80': 4, 'p_hold_79_85': 4, 'positive_fair_drawdown': 4, 'rich_exit_80_plus': 4, 'value_over_hold': 4, 'p_hold_75_79': 4}` |
| `reduce_p_hold_ge_075` | 6 | -848c | 0 | `{'exit_cents_gte60': 6, 'p_hold_75_79': 6, 'p_hold_75_85': 6, 'probability_reduce': 6, 'positive_fair_drawdown': 4, 'negative_book_gap': 2, 'positive_book_gap_ge05': 2}` |

## Worst False-Hold Examples

| window | policy | market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |
|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| `new_exit_mix_common_forward_v1` | `book_gap_soft_gap15_or_p_hold75` | `KXBTC15M-26MAY062015-15` | yes/no | `mushroom_v28_exit_value_over_hold` | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c | book_disagrees_with_hold_at_rich_exit, exit_cents_gte60, exit_cents_gte80, negative_book_gap, p_hold_75_85, p_hold_79_85, positive_fair_drawdown, rich_exit_80_plus, value_over_hold |
| `new_exit_mix_common_forward_v1` | `dual_book_gap_else_reduce` | `KXBTC15M-26MAY062015-15` | yes/no | `mushroom_v28_exit_value_over_hold` | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c | book_disagrees_with_hold_at_rich_exit, exit_cents_gte60, exit_cents_gte80, negative_book_gap, p_hold_75_85, p_hold_79_85, positive_fair_drawdown, rich_exit_80_plus, value_over_hold |
| `new_exit_mix_common_forward_v2` | `book_gap_soft_gap15_or_p_hold75` | `KXBTC15M-26MAY062015-15` | yes/no | `mushroom_v28_exit_value_over_hold` | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c | book_disagrees_with_hold_at_rich_exit, exit_cents_gte60, exit_cents_gte80, negative_book_gap, p_hold_75_85, p_hold_79_85, positive_fair_drawdown, rich_exit_80_plus, value_over_hold |
| `new_exit_mix_common_forward_v2` | `dual_book_gap_else_reduce` | `KXBTC15M-26MAY062015-15` | yes/no | `mushroom_v28_exit_value_over_hold` | 0.812359 | -0.08764099999999997 | 4.764109 | 90.0 | -180c | book_disagrees_with_hold_at_rich_exit, exit_cents_gte60, exit_cents_gte80, negative_book_gap, p_hold_75_85, p_hold_79_85, positive_fair_drawdown, rich_exit_80_plus, value_over_hold |
| `new_exit_mix_common_forward_v1` | `book_gap_soft_gap15_or_p_hold75` | `KXBTC15M-26MAY071100-00` | yes/no | `mushroom_v28_exit_value_over_hold` | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c | book_disagrees_with_hold_at_rich_exit, exit_cents_gte60, exit_cents_gte80, negative_book_gap, p_hold_75_85, p_hold_79_85, rich_exit_80_plus, value_over_hold |
| `new_exit_mix_common_forward_v1` | `dual_book_gap_else_reduce` | `KXBTC15M-26MAY071100-00` | yes/no | `mushroom_v28_exit_value_over_hold` | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c | book_disagrees_with_hold_at_rich_exit, exit_cents_gte60, exit_cents_gte80, negative_book_gap, p_hold_75_85, p_hold_79_85, rich_exit_80_plus, value_over_hold |
| `new_exit_mix_common_forward_v2` | `book_gap_soft_gap15_or_p_hold75` | `KXBTC15M-26MAY071100-00` | yes/no | `mushroom_v28_exit_value_over_hold` | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c | book_disagrees_with_hold_at_rich_exit, exit_cents_gte60, exit_cents_gte80, negative_book_gap, p_hold_75_85, p_hold_79_85, rich_exit_80_plus, value_over_hold |
| `new_exit_mix_common_forward_v2` | `dual_book_gap_else_reduce` | `KXBTC15M-26MAY071100-00` | yes/no | `mushroom_v28_exit_value_over_hold` | 0.83675 | -0.013249999999999984 | -0.675039 | 85.0 | -170c | book_disagrees_with_hold_at_rich_exit, exit_cents_gte60, exit_cents_gte80, negative_book_gap, p_hold_75_85, p_hold_79_85, rich_exit_80_plus, value_over_hold |
| `new_exit_mix_common_forward_v1` | `reduce_p_hold_ge_075` | `KXBTC15M-26MAY071015-15` | no/yes | `mushroom_v28_probability_reduce` | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c | exit_cents_gte60, negative_book_gap, p_hold_75_79, p_hold_75_85, probability_reduce |
| `new_exit_mix_common_forward_v1` | `book_gap_soft_gap15_or_p_hold75` | `KXBTC15M-26MAY071015-15` | no/yes | `mushroom_v28_probability_reduce` | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c | exit_cents_gte60, negative_book_gap, p_hold_75_79, p_hold_75_85, probability_reduce |
| `new_exit_mix_common_forward_v1` | `dual_book_gap_else_reduce` | `KXBTC15M-26MAY071015-15` | no/yes | `mushroom_v28_probability_reduce` | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c | exit_cents_gte60, negative_book_gap, p_hold_75_79, p_hold_75_85, probability_reduce |
| `new_exit_mix_common_forward_v2` | `reduce_p_hold_ge_075` | `KXBTC15M-26MAY071015-15` | no/yes | `mushroom_v28_probability_reduce` | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c | exit_cents_gte60, negative_book_gap, p_hold_75_79, p_hold_75_85, probability_reduce |
| `new_exit_mix_common_forward_v2` | `book_gap_soft_gap15_or_p_hold75` | `KXBTC15M-26MAY071015-15` | no/yes | `mushroom_v28_probability_reduce` | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c | exit_cents_gte60, negative_book_gap, p_hold_75_79, p_hold_75_85, probability_reduce |
| `new_exit_mix_common_forward_v2` | `dual_book_gap_else_reduce` | `KXBTC15M-26MAY071015-15` | no/yes | `mushroom_v28_probability_reduce` | 0.78913 | -0.0008700000000000374 | -0.913001 | 79.0 | -158c | exit_cents_gte60, negative_book_gap, p_hold_75_79, p_hold_75_85, probability_reduce |
| `new_exit_mix_common_forward_v1` | `reduce_p_hold_ge_075` | `KXBTC15M-26MAY071015-15` | no/yes | `mushroom_v28_probability_reduce` | 0.76398 | 0.03398000000000001 | 4.602013 | 73.0 | -146c | exit_cents_gte60, p_hold_75_79, p_hold_75_85, positive_fair_drawdown, probability_reduce |
