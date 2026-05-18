# v28 Frozen Exit Common-Clock Residual Child Watch

Research-only. No live bot changes or orders.

- Generated UTC: `2026-05-07T15:07:11.968523+00:00`
- State: `{'candidate': 'parent_loss_guard_plus_residual_exit70_79', 'child_condition': 'parent_not_suppressed_and_exit_price_cents_70_to_79', 'freeze_ts_utc': '2026-05-07T08:06:06.929631+00:00', 'parent_policy': 'loss_guard_value_p85_reduce_p79_gap0', 'physics': 'A still-high exit price with low parent confidence may be transient winner clipping; strict forward rows must prove it does not reopen loss-control damage.'}`

## Interpretation

- Research-only child watch; no live bot changes or orders.
- Child freeze UTC is 2026-05-07T08:06:06.929631+00:00; only post_child_birth is strict evidence.
- Diagnostic context is allowed to shape hypotheses, not promotion.
- diagnostic_v2_common_clock_context: settled 45, child suppressed 7, helpful/harmful 5/2, child delta -52.0c, candidate net 374.0c, blockers ['child_suppressed_decisions_lt_30', 'child_delta_vs_parent_not_positive', 'child_loss_control_cost_negative'].
- diagnostic_v3_common_clock_context: settled 33, child suppressed 6, helpful/harmful 4/2, child delta -104.0c, candidate net 346.0c, blockers ['child_suppressed_decisions_lt_30', 'delta_vs_current_not_positive', 'child_delta_vs_parent_not_positive', 'child_loss_control_cost_negative'].
- post_child_birth: settled 20, child suppressed 4, helpful/harmful 2/2, child delta -202.0c, candidate net 190.0c, blockers ['settled_lt_30', 'child_suppressed_decisions_lt_30', 'delta_vs_current_not_positive', 'child_delta_vs_parent_not_positive', 'child_loss_control_cost_negative', 'full_loss_cushion_lt_3'].

## Lanes

| lane | strict | settled | parent suppressed | child suppressed | child helpful/harmful | current | parent | candidate | child delta | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `diagnostic_v2_common_clock_context` | `False` | 45 | 11 | 7 | 5/2 | 314.00c | 426.00c | 374.00c | -52.00c | 3 | child_suppressed_decisions_lt_30, child_delta_vs_parent_not_positive, child_loss_control_cost_negative |
| `diagnostic_v3_common_clock_context` | `False` | 33 | 7 | 6 | 4/2 | 366.00c | 450.00c | 346.00c | -104.00c | 3 | child_suppressed_decisions_lt_30, delta_vs_current_not_positive, child_delta_vs_parent_not_positive, child_loss_control_cost_negative |
| `post_child_birth` | `True` | 20 | 4 | 4 | 2/2 | 338.00c | 392.00c | 190.00c | -202.00c | 1 | settled_lt_30, child_suppressed_decisions_lt_30, delta_vs_current_not_positive, child_delta_vs_parent_not_positive, child_loss_control_cost_negative, full_loss_cushion_lt_3 |

## diagnostic_v2_common_clock_context

### Child Rows
- KXBTC15M-26MAY070830-30 no/no parent=-14.00 hold=46.00 cand=46.00 child_delta=60.00 tags=['child_residual_suppressed', 'settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY062215-15 no/no parent=14.00 hold=70.00 cand=70.00 child_delta=56.00 tags=['child_residual_suppressed', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_70_79']
- KXBTC15M-26MAY062100-00 yes/yes parent=-20.00 hold=32.00 cand=32.00 child_delta=52.00 tags=['child_residual_suppressed', 'settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY070000-00 no/no parent=2.00 hold=44.00 cand=44.00 child_delta=42.00 tags=['child_residual_suppressed', 'settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071000-00 no/no parent=16.00 hold=58.00 cand=58.00 child_delta=42.00 tags=['child_residual_suppressed', 'settlement_winner', 'probability_reduce', 'p_hold_75_79', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071015-15 no/yes parent=-16.00 hold=-162.00 cand=-162.00 child_delta=-146.00 tags=['child_residual_suppressed', 'settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071015-15 no/yes parent=2.00 hold=-156.00 cand=-156.00 child_delta=-158.00 tags=['child_residual_suppressed', 'settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_negative', 'fair_drawdown_shallow', 'exitable_at_70_79']

### Worst Candidate Rows
- KXBTC15M-26MAY071015-15 no/yes parent=-16.00 hold=-162.00 cand=-162.00 child_delta=-146.00 tags=['child_residual_suppressed', 'settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071015-15 no/yes parent=2.00 hold=-156.00 cand=-156.00 child_delta=-158.00 tags=['child_residual_suppressed', 'settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_negative', 'fair_drawdown_shallow', 'exitable_at_70_79']
- KXBTC15M-26MAY062015-15 yes/no parent=-134.00 hold=-134.00 cand=-134.00 child_delta=0.00 tags=['settlement_loser', 'other_exit_reason']
- KXBTC15M-26MAY062015-15 no/no parent=-60.00 hold=116.00 cand=-60.00 child_delta=0.00 tags=['settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_5_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071000-00 no/no parent=-36.00 hold=54.00 cand=-36.00 child_delta=0.00 tags=['settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_5_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY062115-15 no/yes parent=-34.00 hold=-138.00 cand=-34.00 child_delta=0.00 tags=['settlement_loser', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY062130-30 no/yes parent=-32.00 hold=-152.00 cand=-32.00 child_delta=0.00 tags=['settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_ge_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071030-30 no/no parent=-24.00 hold=46.00 cand=-24.00 child_delta=0.00 tags=['settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_5_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY062115-15 yes/yes parent=-12.00 hold=54.00 cand=-12.00 child_delta=0.00 tags=['settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071045-45 no/no parent=-10.00 hold=52.00 cand=-10.00 child_delta=0.00 tags=['settlement_winner', 'probability_reduce', 'p_hold_75_79', 'book_gap_5_15pp', 'fair_drawdown_shallow', 'exit_price_below_70']

## diagnostic_v3_common_clock_context

### Child Rows
- KXBTC15M-26MAY070830-30 no/no parent=-14.00 hold=46.00 cand=46.00 child_delta=60.00 tags=['child_residual_suppressed', 'settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY062215-15 no/no parent=14.00 hold=70.00 cand=70.00 child_delta=56.00 tags=['child_residual_suppressed', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_70_79']
- KXBTC15M-26MAY070000-00 no/no parent=2.00 hold=44.00 cand=44.00 child_delta=42.00 tags=['child_residual_suppressed', 'settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071000-00 no/no parent=16.00 hold=58.00 cand=58.00 child_delta=42.00 tags=['child_residual_suppressed', 'settlement_winner', 'probability_reduce', 'p_hold_75_79', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071015-15 no/yes parent=-16.00 hold=-162.00 cand=-162.00 child_delta=-146.00 tags=['child_residual_suppressed', 'settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071015-15 no/yes parent=2.00 hold=-156.00 cand=-156.00 child_delta=-158.00 tags=['child_residual_suppressed', 'settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_negative', 'fair_drawdown_shallow', 'exitable_at_70_79']

### Worst Candidate Rows
- KXBTC15M-26MAY071015-15 no/yes parent=-16.00 hold=-162.00 cand=-162.00 child_delta=-146.00 tags=['child_residual_suppressed', 'settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071015-15 no/yes parent=2.00 hold=-156.00 cand=-156.00 child_delta=-158.00 tags=['child_residual_suppressed', 'settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_negative', 'fair_drawdown_shallow', 'exitable_at_70_79']
- KXBTC15M-26MAY071000-00 no/no parent=-36.00 hold=54.00 cand=-36.00 child_delta=0.00 tags=['settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_5_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY062115-15 no/yes parent=-34.00 hold=-138.00 cand=-34.00 child_delta=0.00 tags=['settlement_loser', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY062130-30 no/yes parent=-32.00 hold=-152.00 cand=-32.00 child_delta=0.00 tags=['settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_ge_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071030-30 no/no parent=-24.00 hold=46.00 cand=-24.00 child_delta=0.00 tags=['settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_5_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY062115-15 yes/yes parent=-12.00 hold=54.00 cand=-12.00 child_delta=0.00 tags=['settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071045-45 no/no parent=-10.00 hold=52.00 cand=-10.00 child_delta=0.00 tags=['settlement_winner', 'probability_reduce', 'p_hold_75_79', 'book_gap_5_15pp', 'fair_drawdown_shallow', 'exit_price_below_70']
- KXBTC15M-26MAY070015-15 no/yes parent=-2.00 hold=-140.00 cand=-2.00 child_delta=0.00 tags=['settlement_loser', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY070115-15 yes/yes parent=0.00 hold=36.00 cand=0.00 child_delta=0.00 tags=['settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_80_plus']

## post_child_birth

### Child Rows
- KXBTC15M-26MAY070830-30 no/no parent=-14.00 hold=46.00 cand=46.00 child_delta=60.00 tags=['child_residual_suppressed', 'settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071000-00 no/no parent=16.00 hold=58.00 cand=58.00 child_delta=42.00 tags=['child_residual_suppressed', 'settlement_winner', 'probability_reduce', 'p_hold_75_79', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071015-15 no/yes parent=-16.00 hold=-162.00 cand=-162.00 child_delta=-146.00 tags=['child_residual_suppressed', 'settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071015-15 no/yes parent=2.00 hold=-156.00 cand=-156.00 child_delta=-158.00 tags=['child_residual_suppressed', 'settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_negative', 'fair_drawdown_shallow', 'exitable_at_70_79']

### Worst Candidate Rows
- KXBTC15M-26MAY071015-15 no/yes parent=-16.00 hold=-162.00 cand=-162.00 child_delta=-146.00 tags=['child_residual_suppressed', 'settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071015-15 no/yes parent=2.00 hold=-156.00 cand=-156.00 child_delta=-158.00 tags=['child_residual_suppressed', 'settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_negative', 'fair_drawdown_shallow', 'exitable_at_70_79']
- KXBTC15M-26MAY071000-00 no/no parent=-36.00 hold=54.00 cand=-36.00 child_delta=0.00 tags=['settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_5_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071030-30 no/no parent=-24.00 hold=46.00 cand=-24.00 child_delta=0.00 tags=['settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_5_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071045-45 no/no parent=-10.00 hold=52.00 cand=-10.00 child_delta=0.00 tags=['settlement_winner', 'probability_reduce', 'p_hold_75_79', 'book_gap_5_15pp', 'fair_drawdown_shallow', 'exit_price_below_70']
- KXBTC15M-26MAY071100-00 yes/no parent=4.00 hold=-166.00 cand=4.00 child_delta=0.00 tags=['settlement_loser', 'value_over_hold', 'p_hold_79_85', 'book_gap_negative', 'fair_drawdown_shallow', 'exitable_at_80_plus']
- KXBTC15M-26MAY070830-30 no/no parent=18.00 hold=36.00 cand=18.00 child_delta=0.00 tags=['settlement_winner', 'value_over_hold', 'p_hold_79_85', 'book_gap_negative', 'fair_drawdown_shallow', 'exitable_at_80_plus']
- KXBTC15M-26MAY070815-15 yes/yes parent=20.00 hold=20.00 cand=20.00 child_delta=0.00 tags=['parent_suppressed', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_shallow', 'exitable_at_80_plus']
- KXBTC15M-26MAY071015-15 yes/yes parent=32.00 hold=32.00 cand=32.00 child_delta=0.00 tags=['parent_suppressed', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY070745-45 yes/yes parent=34.00 hold=64.00 cand=34.00 child_delta=0.00 tags=['settlement_winner', 'value_over_hold', 'p_hold_79_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
