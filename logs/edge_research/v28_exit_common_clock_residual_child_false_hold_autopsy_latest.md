# v28 Exit Common-Clock Residual Child False-Hold Autopsy

Research-only autopsy. No live bot changes or orders.

- Generated UTC: `2026-05-07T15:07:13.429995+00:00`
- Child watch source: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_frozen_exit_common_clock_residual_child_watch_latest.json`
- Path-risk source: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_exit_common_clock_residual_child_path_risk_latest.json`

## Interpretation

- Research-only autopsy; no live bot changes or orders.
- Strict post-child rows 20 settled, 4 child suppressions, helpful/harmful 2/2, child delta -202.0c.
- False holds are concentrated in probability-reduce exits with p_hold 75-79; the harmful rows are a same-market cluster, so the child cannot be treated as a generic clipped-winner repair.

## Strict Summary

- Settled: `20`
- Child suppressions: `4`
- Helpful/harmful: `2/2`
- Child delta vs parent: `-202.0c`
- Candidate/current/delta: `190.0c` / `338.0c` / `-148.0c`
- Loss-control cost: `-304.0c`
- Cushion: `1`
- Autopsy blockers: `['settled_lt_30', 'child_suppressed_decisions_lt_30', 'delta_vs_current_not_positive', 'child_delta_vs_parent_not_positive', 'child_loss_control_cost_negative', 'full_loss_cushion_lt_3', 'strict_false_holds_present', 'same_market_false_hold_cluster', 'p_hold_75_79_false_hold_risk', 'probability_reduce_false_hold_risk']`

## Helpful vs Harmful

- Helpful rows: `2`, net child delta `102.0c`, markets `{'KXBTC15M-26MAY070830-30': 1, 'KXBTC15M-26MAY071000-00': 1}`, p-hold bands `{'lt75': 1, '75_79': 1}`, book-gap bands `{'negative_lt_1pp': 1, 'flat_to_neg_1pp': 1}`.
- Harmful rows: `2`, net child delta `-304.0c`, markets `{'KXBTC15M-26MAY071015-15': 2}`, p-hold bands `{'75_79': 2}`, book-gap bands `{'positive_0_5pp': 1, 'flat_to_neg_1pp': 1}`.
- Harmful exit reasons: `{'mushroom_v28_probability_reduce': 2}`
- Harmful same-market clusters: `{'KXBTC15M-26MAY071015-15': 2}`

## Rows

| market | side | won | reason | exit | p_hold | gap | fair dd | current | hold | child delta | path | worst adverse | tags |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY071015-15` | `no` | False | `mushroom_v28_probability_reduce` | 79.00 | 0.79 | -0.00 | -0.91 | 2.00 | -156.00 | -158.00 | False | n/a | child_residual_suppressed, settlement_loser, probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_shallow, exitable_at_70_79 |
| `KXBTC15M-26MAY071015-15` | `no` | False | `mushroom_v28_probability_reduce` | 73.00 | 0.76 | 0.03 | 4.60 | -16.00 | -162.00 | -146.00 | False | n/a | child_residual_suppressed, settlement_loser, probability_reduce, p_hold_75_79, book_gap_0_5pp, fair_drawdown_positive, exitable_at_70_79 |
| `KXBTC15M-26MAY071000-00` | `no` | True | `mushroom_v28_probability_reduce` | 79.00 | 0.78 | -0.01 | 6.86 | 16.00 | 58.00 | 42.00 | False | n/a | child_residual_suppressed, settlement_winner, probability_reduce, p_hold_75_79, book_gap_negative, fair_drawdown_positive, exitable_at_70_79 |
| `KXBTC15M-26MAY070830-30` | `no` | True | `mushroom_v28_exit_value_over_hold` | 70.00 | 0.61 | -0.09 | 15.70 | -14.00 | 46.00 | 60.00 | True | -10.00 | child_residual_suppressed, settlement_winner, value_over_hold, p_hold_lt_75, book_gap_negative, fair_drawdown_positive, exitable_at_70_79 |
