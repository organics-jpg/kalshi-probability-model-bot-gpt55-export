# v28 Frozen Exit Common-Clock Residual Child Book-Gap Guard Watch

Research-only. No live bot changes or orders.

- Generated UTC: `2026-05-07T15:14:41.054074+00:00`
- State: `{'candidate': 'residual_exit70_79_book_gap_le_neg_0_5pp', 'child_condition': 'parent_not_suppressed_and_exit_price_70_79_and_hold_book_gap_le_neg_0_5pp', 'diagnostic_source': 'C:\\Users\\organ\\Desktop\\KALSHI PROBABILITY MODEL BOT\\logs\\edge_research\\v28_exit_common_clock_residual_child_guardrail_variants_latest.json', 'freeze_ts_utc': '2026-05-07T15:09:26.289911+00:00', 'parent_child': 'parent_loss_guard_plus_residual_exit70_79', 'parent_policy': 'loss_guard_value_p85_reduce_p79_gap0', 'physics': 'A 70-79c exit may be a transient winner clip only when the order book still leans toward holding. Flat or positive hold-book gap in p_hold 75-79 probability-reduce exits is a false-hold risk.'}`

## Interpretation

- Research-only frozen child-repair watch; no live bot changes or orders.
- Book-gap guard freeze UTC is 2026-05-07T15:09:26.289911+00:00; only post_book_gap_guard_birth is strict evidence for this child.
- Diagnostic common-clock lanes explain the mechanism but cannot promote the guard.
- post_book_gap_guard_birth: settled 0, child suppressed 0, helpful/harmful 0/0, child delta 0c, candidate net 0c, blockers ['settled_lt_30', 'child_suppressed_decisions_lt_30', 'net_not_positive', 'delta_vs_current_not_positive', 'child_delta_vs_parent_not_positive', 'full_loss_cushion_lt_3'].
- No post-birth rows yet; this is an empty strict watch.

## Lanes

| lane | strict | settled | child suppressed | helpful/harmful | child delta | candidate net | delta vs current | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `diagnostic_v2_common_clock_context` | False | 20 | 2 | 2/0 | 94.00 | 128.00 | 132.00 | 1 | settled_lt_30, child_suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| `diagnostic_v3_common_clock_context` | False | 13 | 1 | 1/0 | 42.00 | 170.00 | 78.00 | 1 | settled_lt_30, child_suppressed_decisions_lt_30, full_loss_cushion_lt_3 |
| `post_book_gap_guard_birth` | True | 0 | 0 | 0/0 | 0 | 0 | 0 | 0 | settled_lt_30, child_suppressed_decisions_lt_30, net_not_positive, delta_vs_current_not_positive, child_delta_vs_parent_not_positive, full_loss_cushion_lt_3 |

## diagnostic_v2_common_clock_context

### Child Rows
- KXBTC15M-26MAY071000-00 no/no parent=16.00 hold=58.00 cand=58.00 child_delta=42.00 p_hold=0.78 gap=-0.01 tags=['child_residual_suppressed', 'settlement_winner', 'probability_reduce', 'p_hold_75_79', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_70_79', 'probability_reduce_exit', 'p_hold_75_79_guard_zone', 'book_gap_le_neg_0_5pp']
- KXBTC15M-26MAY062100-00 yes/yes parent=-20.00 hold=32.00 cand=32.00 child_delta=52.00 p_hold=0.66 gap=-0.08 tags=['child_residual_suppressed', 'settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_70_79', 'value_over_hold_exit', 'book_gap_le_neg_0_5pp']

### Worst Candidate Rows
- KXBTC15M-26MAY062015-15 yes/no parent=-134.00 hold=-134.00 cand=-134.00 child_delta=0.00 p_hold=n/a gap=n/a tags=['settlement_loser', 'other_exit_reason']
- KXBTC15M-26MAY062115-15 no/yes parent=-34.00 hold=-138.00 cand=-34.00 child_delta=0.00 p_hold=0.46 gap=-0.06 tags=['settlement_loser', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70', 'value_over_hold_exit', 'book_gap_le_neg_0_5pp']
- KXBTC15M-26MAY062130-30 no/yes parent=-32.00 hold=-152.00 cand=-32.00 child_delta=0.00 p_hold=0.77 gap=0.17 tags=['settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_ge_15pp', 'fair_drawdown_positive', 'exit_price_below_70', 'probability_reduce_exit', 'p_hold_75_79_guard_zone']
- KXBTC15M-26MAY071015-15 no/yes parent=-16.00 hold=-162.00 cand=-16.00 child_delta=0.00 p_hold=0.76 gap=0.03 tags=['settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exitable_at_70_79', 'probability_reduce_exit', 'p_hold_75_79_guard_zone']
- KXBTC15M-26MAY062115-15 yes/yes parent=-12.00 hold=54.00 cand=-12.00 child_delta=0.00 p_hold=0.40 gap=-0.27 tags=['settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70', 'value_over_hold_exit', 'book_gap_le_neg_0_5pp']
- KXBTC15M-26MAY062100-00 yes/yes parent=-4.00 hold=34.00 cand=-4.00 child_delta=0.00 p_hold=0.65 gap=-0.16 tags=['settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_80_plus', 'value_over_hold_exit', 'book_gap_le_neg_0_5pp']
- KXBTC15M-26MAY070015-15 no/yes parent=-2.00 hold=-140.00 cand=-2.00 child_delta=0.00 p_hold=0.60 gap=-0.09 tags=['settlement_loser', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70', 'value_over_hold_exit', 'book_gap_le_neg_0_5pp']
- KXBTC15M-26MAY062015-15 yes/no parent=8.00 hold=-172.00 cand=8.00 child_delta=0.00 p_hold=0.81 gap=-0.09 tags=['settlement_loser', 'value_over_hold', 'p_hold_79_85', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_80_plus', 'value_over_hold_exit', 'book_gap_le_neg_0_5pp']
- KXBTC15M-26MAY062245-45 yes/yes parent=8.00 hold=28.00 cand=8.00 child_delta=0.00 p_hold=0.64 gap=-0.26 tags=['settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_80_plus', 'value_over_hold_exit', 'book_gap_le_neg_0_5pp']
- KXBTC15M-26MAY062100-00 yes/yes parent=14.00 hold=78.00 cand=14.00 child_delta=0.00 p_hold=0.49 gap=-0.19 tags=['settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70', 'value_over_hold_exit', 'book_gap_le_neg_0_5pp']

## diagnostic_v3_common_clock_context

### Child Rows
- KXBTC15M-26MAY071000-00 no/no parent=16.00 hold=58.00 cand=58.00 child_delta=42.00 p_hold=0.78 gap=-0.01 tags=['child_residual_suppressed', 'settlement_winner', 'probability_reduce', 'p_hold_75_79', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_70_79', 'probability_reduce_exit', 'p_hold_75_79_guard_zone', 'book_gap_le_neg_0_5pp']

### Worst Candidate Rows
- KXBTC15M-26MAY062115-15 no/yes parent=-34.00 hold=-138.00 cand=-34.00 child_delta=0.00 p_hold=0.46 gap=-0.06 tags=['settlement_loser', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70', 'value_over_hold_exit', 'book_gap_le_neg_0_5pp']
- KXBTC15M-26MAY062130-30 no/yes parent=-32.00 hold=-152.00 cand=-32.00 child_delta=0.00 p_hold=0.77 gap=0.17 tags=['settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_ge_15pp', 'fair_drawdown_positive', 'exit_price_below_70', 'probability_reduce_exit', 'p_hold_75_79_guard_zone']
- KXBTC15M-26MAY071015-15 no/yes parent=-16.00 hold=-162.00 cand=-16.00 child_delta=0.00 p_hold=0.76 gap=0.03 tags=['settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exitable_at_70_79', 'probability_reduce_exit', 'p_hold_75_79_guard_zone']
- KXBTC15M-26MAY062115-15 yes/yes parent=-12.00 hold=54.00 cand=-12.00 child_delta=0.00 p_hold=0.40 gap=-0.27 tags=['settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70', 'value_over_hold_exit', 'book_gap_le_neg_0_5pp']
- KXBTC15M-26MAY070015-15 no/yes parent=-2.00 hold=-140.00 cand=-2.00 child_delta=0.00 p_hold=0.60 gap=-0.09 tags=['settlement_loser', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70', 'value_over_hold_exit', 'book_gap_le_neg_0_5pp']
- KXBTC15M-26MAY062245-45 yes/yes parent=8.00 hold=28.00 cand=8.00 child_delta=0.00 p_hold=0.64 gap=-0.26 tags=['settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_80_plus', 'value_over_hold_exit', 'book_gap_le_neg_0_5pp']
- KXBTC15M-26MAY062300-00 yes/yes parent=16.00 hold=26.00 cand=16.00 child_delta=0.00 p_hold=0.75 gap=-0.20 tags=['settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_80_plus', 'value_over_hold_exit', 'book_gap_le_neg_0_5pp']
- KXBTC15M-26MAY062115-15 yes/yes parent=24.00 hold=24.00 cand=24.00 child_delta=0.00 p_hold=0.98 gap=-0.01 tags=['parent_suppressed', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus', 'value_over_hold_exit', 'book_gap_le_neg_0_5pp']
- KXBTC15M-26MAY062215-15 no/no parent=32.00 hold=32.00 cand=32.00 child_delta=0.00 p_hold=0.86 gap=-0.03 tags=['parent_suppressed', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_shallow', 'exitable_at_80_plus', 'value_over_hold_exit', 'book_gap_le_neg_0_5pp']
- KXBTC15M-26MAY071015-15 yes/yes parent=32.00 hold=32.00 cand=32.00 child_delta=0.00 p_hold=0.92 gap=-0.02 tags=['parent_suppressed', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus', 'value_over_hold_exit', 'book_gap_le_neg_0_5pp']

## post_book_gap_guard_birth

### Child Rows

### Worst Candidate Rows
