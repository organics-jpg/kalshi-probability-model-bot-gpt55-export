# v28 Exit Value/Reduce-Depth Suppressed-Loser Audit

Research-only. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T11:57:57.819099+00:00`
- Composite generated UTC: `2026-05-07T11:56:05.065279+00:00`
- Composite freeze UTC: `2026-05-06T23:34:20.352483+00:00`
- Total suppressed-loser hits: `8`
- Post-birth suppressed-loser hits: `4`
- Unique suppressed-loser markets: `2`

## Interpretation

- Research-only audit; no live bot changes or orders.
- Suppressed losers are the active blocker for the looser value/reduce-depth composite variants.
- Post-birth suppressed loser row(s) exist; do not promote p75 reduce-depth variants until a child avoids them.
- Most repeated suppressed-loser market is KXBTC15M-26MAY062130-30 across 6 variant/lane hits.

## Tag Counts

| tag | hits |
|---|---:|
| `positive_fair_drawdown` | 8 |
| `already_negative_exit` | 6 |
| `p_hold_075_079` | 6 |
| `p_hold_below_079` | 6 |
| `positive_book_gap` | 6 |
| `probability_reduce` | 6 |
| `very_shallow_entry_depth` | 6 |
| `not_yet_negative_exit` | 2 |
| `value_over_hold` | 2 |

## Suppressed Loser Rows

| lane | rule | market | side | reason | current | hold | delta | p_hold | gap | drawdown | depth | worst mark | tags |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `diagnostic_from_exit_freezes` | `value_only_p75_reduce_depth384` | `KXBTC15M-26MAY062015-15` | `yes` | `mushroom_v28_exit_value_over_hold` | 8.000000 | -172.000000 | -180.000000 | 0.812359 | -0.087641 | 4.764109 | 1557.140000 | -172 | value_over_hold, positive_fair_drawdown, not_yet_negative_exit |
| `diagnostic_from_exit_freezes` | `value_only_p75_reduce_depth384` | `KXBTC15M-26MAY062130-30` | `no` | `mushroom_v28_probability_reduce` | -32.000000 | -152.000000 | -120.000000 | 0.768407 | 0.168407 | 6.159273 | 24.000000 | -152 | probability_reduce, p_hold_below_079, p_hold_075_079, positive_book_gap, positive_fair_drawdown, very_shallow_entry_depth, already_negative_exit |
| `diagnostic_from_exit_freezes` | `value_v2_reduce_depth295` | `KXBTC15M-26MAY062130-30` | `no` | `mushroom_v28_probability_reduce` | -32.000000 | -152.000000 | -120.000000 | 0.768407 | 0.168407 | 6.159273 | 24.000000 | -152 | probability_reduce, p_hold_below_079, p_hold_075_079, positive_book_gap, positive_fair_drawdown, very_shallow_entry_depth, already_negative_exit |
| `diagnostic_from_exit_freezes` | `value_v2_reduce_depth384` | `KXBTC15M-26MAY062130-30` | `no` | `mushroom_v28_probability_reduce` | -32.000000 | -152.000000 | -120.000000 | 0.768407 | 0.168407 | 6.159273 | 24.000000 | -152 | probability_reduce, p_hold_below_079, p_hold_075_079, positive_book_gap, positive_fair_drawdown, very_shallow_entry_depth, already_negative_exit |
| `post_composite_birth` | `value_only_p75_reduce_depth384` | `KXBTC15M-26MAY062015-15` | `yes` | `mushroom_v28_exit_value_over_hold` | 8.000000 | -172.000000 | -180.000000 | 0.812359 | -0.087641 | 4.764109 | 1557.140000 | -172 | value_over_hold, positive_fair_drawdown, not_yet_negative_exit |
| `post_composite_birth` | `value_only_p75_reduce_depth384` | `KXBTC15M-26MAY062130-30` | `no` | `mushroom_v28_probability_reduce` | -32.000000 | -152.000000 | -120.000000 | 0.768407 | 0.168407 | 6.159273 | 24.000000 | -152 | probability_reduce, p_hold_below_079, p_hold_075_079, positive_book_gap, positive_fair_drawdown, very_shallow_entry_depth, already_negative_exit |
| `post_composite_birth` | `value_v2_reduce_depth295` | `KXBTC15M-26MAY062130-30` | `no` | `mushroom_v28_probability_reduce` | -32.000000 | -152.000000 | -120.000000 | 0.768407 | 0.168407 | 6.159273 | 24.000000 | -152 | probability_reduce, p_hold_below_079, p_hold_075_079, positive_book_gap, positive_fair_drawdown, very_shallow_entry_depth, already_negative_exit |
| `post_composite_birth` | `value_v2_reduce_depth384` | `KXBTC15M-26MAY062130-30` | `no` | `mushroom_v28_probability_reduce` | -32.000000 | -152.000000 | -120.000000 | 0.768407 | 0.168407 | 6.159273 | 24.000000 | -152 | probability_reduce, p_hold_below_079, p_hold_075_079, positive_book_gap, positive_fair_drawdown, very_shallow_entry_depth, already_negative_exit |
