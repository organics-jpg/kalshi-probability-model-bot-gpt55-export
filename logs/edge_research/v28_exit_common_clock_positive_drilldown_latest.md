# v28 Exit Common-Clock Positive Drilldown

Research-only strict-window drilldown. No live bot changes or orders.

- Generated UTC: `2026-05-07T18:03:44.761546+00:00`

## Interpretation

- Research-only drilldown; it does not create or change an exit rule.
- Both positive strict common-clock windows are still promotion-blocked by sample size, suppression density, and full-loss cushion.
- new_exit_mix_common_forward_v2 best policy loss_guard_value_p85_reduce_p79_gap0 has net 668.0c, delta 242.0c, suppressed helpful/harmful 17/0, candidate losses 17, and unsuppressed winner clips 24.
- new_exit_mix_common_forward_v3 best policy loss_guard_value_p85_reduce_p79_gap0 has net 692.0c, delta 214.0c, suppressed helpful/harmful 13/0, candidate losses 13, and unsuppressed winner clips 19.

## new_exit_mix_common_forward_v2

- Freeze UTC: `2026-05-06T22:01:04.415577+00:00`
- Best policy: `loss_guard_value_p85_reduce_p79_gap0`
- Settled/suppressed: `58` / `17`
- Net/delta: `668.0c` / `242.0c`
- Helpful/harmful suppressions: `17` / `0`
- Candidate losses: `17`
- Unsuppressed winner clips: `24`
- Candidate-loss tags: `{'candidate_loss': 17, 'current_loss': 17, 'fair_drawdown_positive': 15, 'unsuppressed_winner_clip': 12, 'settlement_winner': 12, 'p_hold_lt_75': 11, 'exit_price_below_70': 9, 'value_over_hold': 6, 'book_gap_negative': 6, 'exitable_at_70_79': 6, 'probability_reduce': 6, 'settlement_loser': 5, 'p_hold_75_79': 5, 'book_gap_0_5pp': 5, 'mushroom_v28_probability_collapse_full': 4, 'book_gap_5_15pp': 4, 'exit_helped_vs_hold': 4, 'other_exit_reason': 1, 'exitable_at_80_plus': 1, 'book_gap_ge_15pp': 1, 'fair_drawdown_shallow': 1}`
- Best residual selector: `p_hold_lt_75` for `698.0c`, helpful/harmful `16`/`2`

### Suppressed Rows
- KXBTC15M-26MAY071215-15 no/no cur=-16.00 hold=32.00 cand=32.00 delta=48.00 tags=['suppressed', 'suppression_helpful', 'current_loss', 'settlement_winner', 'probability_reduce', 'p_hold_79_85', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071315-15 yes/yes cur=-6.00 hold=40.00 cand=40.00 delta=46.00 tags=['suppressed', 'suppression_helpful', 'current_loss', 'settlement_winner', 'probability_reduce', 'p_hold_79_85', 'book_gap_0_5pp', 'fair_drawdown_shallow', 'exitable_at_70_79']
- KXBTC15M-26MAY062215-15 no/no cur=10.00 hold=32.00 cand=32.00 delta=22.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_shallow', 'exitable_at_80_plus']
- KXBTC15M-26MAY070545-45 no/no cur=18.00 hold=36.00 cand=36.00 delta=18.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY070815-15 yes/yes cur=2.00 hold=20.00 cand=20.00 delta=18.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_shallow', 'exitable_at_80_plus']
- KXBTC15M-26MAY071115-15 yes/yes cur=14.00 hold=32.00 cand=32.00 delta=18.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'exitable_at_80_plus']
- KXBTC15M-26MAY062045-45 no/no cur=24.00 hold=40.00 cand=40.00 delta=16.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY071015-15 yes/yes cur=20.00 hold=32.00 cand=32.00 delta=12.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY071315-15 yes/yes cur=32.00 hold=44.00 cand=44.00 delta=12.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY061815-15 no/no cur=24.00 hold=32.00 cand=32.00 delta=8.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY070030-30 yes/yes cur=30.00 hold=36.00 cand=36.00 delta=6.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY070930-30 yes/yes cur=34.00 hold=40.00 cand=40.00 delta=6.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY071200-00 no/no cur=42.00 hold=46.00 cand=46.00 delta=4.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY061830-30 no/no cur=20.00 hold=22.00 cand=22.00 delta=2.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY061915-15 no/no cur=24.00 hold=26.00 cand=26.00 delta=2.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY062115-15 yes/yes cur=22.00 hold=24.00 cand=24.00 delta=2.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY071145-45 yes/yes cur=44.00 hold=46.00 cand=46.00 delta=2.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']

### Worst Candidate Losses
- KXBTC15M-26MAY062015-15 yes/no cur=-134.00 hold=-134.00 cand=-134.00 delta=0.00 tags=['candidate_loss', 'current_loss', 'settlement_loser', 'other_exit_reason']
- KXBTC15M-26MAY062015-15 no/no cur=-60.00 hold=116.00 cand=-60.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_5_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071230-30 yes/yes cur=-38.00 hold=32.00 cand=-38.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071000-00 no/no cur=-36.00 hold=54.00 cand=-36.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_5_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY062115-15 no/yes cur=-34.00 hold=-138.00 cand=-34.00 delta=0.00 tags=['exit_helped_vs_hold', 'candidate_loss', 'current_loss', 'settlement_loser', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY062130-30 no/yes cur=-32.00 hold=-152.00 cand=-32.00 delta=0.00 tags=['exit_helped_vs_hold', 'candidate_loss', 'current_loss', 'settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_ge_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071030-30 no/no cur=-24.00 hold=46.00 cand=-24.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_5_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY062100-00 yes/yes cur=-20.00 hold=32.00 cand=-20.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071015-15 no/yes cur=-16.00 hold=-162.00 cand=-16.00 delta=0.00 tags=['exit_helped_vs_hold', 'candidate_loss', 'current_loss', 'settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY070830-30 no/no cur=-14.00 hold=46.00 cand=-14.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_70_79']

### Largest Unsuppressed Winner Clips
- KXBTC15M-26MAY062015-15 no/no cur=-60.00 hold=116.00 cand=-60.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_5_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071000-00 no/no cur=-36.00 hold=54.00 cand=-36.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_5_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071030-30 no/no cur=-24.00 hold=46.00 cand=-24.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_5_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071230-30 yes/yes cur=-38.00 hold=32.00 cand=-38.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY062115-15 yes/yes cur=-12.00 hold=54.00 cand=-12.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY062100-00 yes/yes cur=14.00 hold=78.00 cand=14.00 delta=0.00 tags=['unsuppressed_winner_clip', 'settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071045-45 no/no cur=-10.00 hold=52.00 cand=-10.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'probability_reduce', 'p_hold_75_79', 'book_gap_5_15pp', 'fair_drawdown_shallow', 'exit_price_below_70']
- KXBTC15M-26MAY070830-30 no/no cur=-14.00 hold=46.00 cand=-14.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY062215-15 no/no cur=14.00 hold=70.00 cand=14.00 delta=0.00 tags=['unsuppressed_winner_clip', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_70_79']
- KXBTC15M-26MAY071230-30 yes/yes cur=-10.00 hold=46.00 cand=-10.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'probability_reduce', 'p_hold_lt_75', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exitable_at_70_79']

### Residual Separator Scan
- p_hold_lt_75: selected=28 helpful/harmful=16/2 net_delta=698.00c
- mushroom_probability_collapse_full: selected=5 helpful/harmful=5/0 net_delta=462.00c
- fair_drawdown_positive: selected=25 helpful/harmful=20/5 net_delta=406.00c
- p_hold_lt_75_and_exit_price_below_70: selected=8 helpful/harmful=6/2 net_delta=294.00c
- p_hold_lt_75_and_book_gap_negative: selected=13 helpful/harmful=11/2 net_delta=236.00c
- exit_price_below_70: selected=10 helpful/harmful=7/3 net_delta=236.00c
- p_hold_lt_75_and_value_over_hold: selected=12 helpful/harmful=10/2 net_delta=180.00c
- exitable_70_79: selected=11 helpful/harmful=9/2 net_delta=146.00c

## new_exit_mix_common_forward_v3

- Freeze UTC: `2026-05-07T01:01:45.501061+00:00`
- Best policy: `loss_guard_value_p85_reduce_p79_gap0`
- Settled/suppressed: `46` / `13`
- Net/delta: `692.0c` / `214.0c`
- Helpful/harmful suppressions: `13` / `0`
- Candidate losses: `13`
- Unsuppressed winner clips: `19`
- Candidate-loss tags: `{'candidate_loss': 13, 'current_loss': 13, 'fair_drawdown_positive': 12, 'unsuppressed_winner_clip': 9, 'settlement_winner': 9, 'p_hold_lt_75': 8, 'exit_price_below_70': 8, 'probability_reduce': 6, 'p_hold_75_79': 5, 'exitable_at_70_79': 5, 'book_gap_0_5pp': 5, 'value_over_hold': 4, 'book_gap_negative': 4, 'exit_helped_vs_hold': 4, 'settlement_loser': 4, 'mushroom_v28_probability_collapse_full': 3, 'book_gap_5_15pp': 3, 'book_gap_ge_15pp': 1, 'fair_drawdown_shallow': 1}`
- Best residual selector: `p_hold_lt_75` for `334.0c`, helpful/harmful `11`/`2`

### Suppressed Rows
- KXBTC15M-26MAY071215-15 no/no cur=-16.00 hold=32.00 cand=32.00 delta=48.00 tags=['suppressed', 'suppression_helpful', 'current_loss', 'settlement_winner', 'probability_reduce', 'p_hold_79_85', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071315-15 yes/yes cur=-6.00 hold=40.00 cand=40.00 delta=46.00 tags=['suppressed', 'suppression_helpful', 'current_loss', 'settlement_winner', 'probability_reduce', 'p_hold_79_85', 'book_gap_0_5pp', 'fair_drawdown_shallow', 'exitable_at_70_79']
- KXBTC15M-26MAY062215-15 no/no cur=10.00 hold=32.00 cand=32.00 delta=22.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_shallow', 'exitable_at_80_plus']
- KXBTC15M-26MAY070545-45 no/no cur=18.00 hold=36.00 cand=36.00 delta=18.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY070815-15 yes/yes cur=2.00 hold=20.00 cand=20.00 delta=18.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_shallow', 'exitable_at_80_plus']
- KXBTC15M-26MAY071115-15 yes/yes cur=14.00 hold=32.00 cand=32.00 delta=18.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'exitable_at_80_plus']
- KXBTC15M-26MAY071015-15 yes/yes cur=20.00 hold=32.00 cand=32.00 delta=12.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY071315-15 yes/yes cur=32.00 hold=44.00 cand=44.00 delta=12.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY070030-30 yes/yes cur=30.00 hold=36.00 cand=36.00 delta=6.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY070930-30 yes/yes cur=34.00 hold=40.00 cand=40.00 delta=6.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY071200-00 no/no cur=42.00 hold=46.00 cand=46.00 delta=4.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY062115-15 yes/yes cur=22.00 hold=24.00 cand=24.00 delta=2.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']
- KXBTC15M-26MAY071145-45 yes/yes cur=44.00 hold=46.00 cand=46.00 delta=2.00 tags=['suppressed', 'suppression_helpful', 'settlement_winner', 'value_over_hold', 'p_hold_ge_85', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_80_plus']

### Worst Candidate Losses
- KXBTC15M-26MAY071230-30 yes/yes cur=-38.00 hold=32.00 cand=-38.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071000-00 no/no cur=-36.00 hold=54.00 cand=-36.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_5_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY062115-15 no/yes cur=-34.00 hold=-138.00 cand=-34.00 delta=0.00 tags=['exit_helped_vs_hold', 'candidate_loss', 'current_loss', 'settlement_loser', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY062130-30 no/yes cur=-32.00 hold=-152.00 cand=-32.00 delta=0.00 tags=['exit_helped_vs_hold', 'candidate_loss', 'current_loss', 'settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_ge_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071030-30 no/no cur=-24.00 hold=46.00 cand=-24.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_5_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071015-15 no/yes cur=-16.00 hold=-162.00 cand=-16.00 delta=0.00 tags=['exit_helped_vs_hold', 'candidate_loss', 'current_loss', 'settlement_loser', 'probability_reduce', 'p_hold_75_79', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY070830-30 no/no cur=-14.00 hold=46.00 cand=-14.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071315-15 yes/yes cur=-14.00 hold=38.00 cand=-14.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'probability_reduce', 'p_hold_75_79', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY062115-15 yes/yes cur=-12.00 hold=54.00 cand=-12.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071045-45 no/no cur=-10.00 hold=52.00 cand=-10.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'probability_reduce', 'p_hold_75_79', 'book_gap_5_15pp', 'fair_drawdown_shallow', 'exit_price_below_70']

### Largest Unsuppressed Winner Clips
- KXBTC15M-26MAY071000-00 no/no cur=-36.00 hold=54.00 cand=-36.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_5_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071030-30 no/no cur=-24.00 hold=46.00 cand=-24.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_5_15pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071230-30 yes/yes cur=-38.00 hold=32.00 cand=-38.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY062115-15 yes/yes cur=-12.00 hold=54.00 cand=-12.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exit_price_below_70']
- KXBTC15M-26MAY071045-45 no/no cur=-10.00 hold=52.00 cand=-10.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'probability_reduce', 'p_hold_75_79', 'book_gap_5_15pp', 'fair_drawdown_shallow', 'exit_price_below_70']
- KXBTC15M-26MAY070830-30 no/no cur=-14.00 hold=46.00 cand=-14.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'value_over_hold', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY062215-15 no/no cur=14.00 hold=70.00 cand=14.00 delta=0.00 tags=['unsuppressed_winner_clip', 'settlement_winner', 'mushroom_v28_probability_collapse_full', 'p_hold_lt_75', 'book_gap_negative', 'fair_drawdown_deep', 'exitable_at_70_79']
- KXBTC15M-26MAY071230-30 yes/yes cur=-10.00 hold=46.00 cand=-10.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'probability_reduce', 'p_hold_lt_75', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071315-15 yes/yes cur=-14.00 hold=38.00 cand=-14.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'probability_reduce', 'p_hold_75_79', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exitable_at_70_79']
- KXBTC15M-26MAY071215-15 no/no cur=-8.00 hold=40.00 cand=-8.00 delta=0.00 tags=['unsuppressed_winner_clip', 'candidate_loss', 'current_loss', 'settlement_winner', 'probability_reduce', 'p_hold_75_79', 'book_gap_0_5pp', 'fair_drawdown_positive', 'exitable_at_70_79']

### Residual Separator Scan
- p_hold_lt_75: selected=21 helpful/harmful=11/2 net_delta=334.00c
- mushroom_probability_collapse_full: selected=4 helpful/harmful=4/0 net_delta=286.00c
- fair_drawdown_positive: selected=19 helpful/harmful=15/4 net_delta=222.00c
- exitable_70_79: selected=10 helpful/harmful=8/2 net_delta=94.00c
- p_hold_lt_75_and_exit_price_below_70: selected=6 helpful/harmful=4/2 net_delta=54.00c
- p_hold_lt_75_and_book_gap_negative: selected=9 helpful/harmful=7/2 net_delta=48.00c
- exit_price_below_70: selected=8 helpful/harmful=5/3 net_delta=-4.00c
- p_hold_lt_75_and_value_over_hold: selected=8 helpful/harmful=6/2 net_delta=-8.00c
