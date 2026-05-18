# v28 Exit Reduce Suppression Risk Ledger

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:13:34.775178+00:00`
- Freeze UTC: `2026-05-06T06:33:56.987999+00:00`
- Candidate: `suppress_reduce_p_hold_ge_075`

## Interpretation

- This ledger classifies only already-frozen reduce-suppression rows; it does not change exit policy.
- Suppressed exits net 337.0c: helpful winner recovery 1067.0c versus harmful loss-control cost -730.0c.
- p_hold_ge_079: rows 11, net delta 357.0c, tags {'favorable_fair_value': 5, 'large_adverse_mark_after_exit': 6, 'large_fair_drawdown': 1, 'loss_control_cost': 1, 'moderate_adverse_mark_after_exit': 2, 'moderate_fair_drawdown': 3, 'negative_delta': 1, 'positive_delta': 10, 'post_exit_mark_went_full_loss': 3, 'small_fair_drawdown': 2, 'very_high_p_hold': 11, 'winner_recovery': 10}.
- p_hold_075_079: rows 14, net delta -20.0c, tags {'favorable_fair_value': 4, 'large_adverse_mark_after_exit': 9, 'large_fair_drawdown': 2, 'loss_control_cost': 4, 'marginal_p_hold': 14, 'moderate_fair_drawdown': 6, 'negative_delta': 4, 'positive_delta': 10, 'post_exit_mark_went_full_loss': 5, 'small_fair_drawdown': 2, 'winner_recovery': 10}.
- drawdown_lte_2p5: rows 13, net delta 305.0c, tags {'favorable_fair_value': 9, 'large_adverse_mark_after_exit': 8, 'loss_control_cost': 2, 'marginal_p_hold': 6, 'moderate_adverse_mark_after_exit': 1, 'negative_delta': 2, 'positive_delta': 11, 'post_exit_mark_went_full_loss': 4, 'small_fair_drawdown': 4, 'very_high_p_hold': 7, 'winner_recovery': 11}.
- drawdown_2p5_5: rows 9, net delta 64.0c, tags {'large_adverse_mark_after_exit': 5, 'loss_control_cost': 2, 'marginal_p_hold': 6, 'moderate_adverse_mark_after_exit': 1, 'moderate_fair_drawdown': 9, 'negative_delta': 2, 'positive_delta': 7, 'post_exit_mark_went_full_loss': 3, 'very_high_p_hold': 3, 'winner_recovery': 7}.
- drawdown_gt_5: rows 3, net delta -32.0c, tags {'large_adverse_mark_after_exit': 2, 'large_fair_drawdown': 3, 'loss_control_cost': 1, 'marginal_p_hold': 2, 'negative_delta': 1, 'positive_delta': 2, 'post_exit_mark_went_full_loss': 1, 'very_high_p_hold': 1, 'winner_recovery': 2}.
- Promotion requires converting this into a forward-tested loss-control repair, because blanket suppression still has harmful rows.

## Group Summaries

| group | rows | net delta c | avg p_hold | avg drawdown | tags |
|---|---:|---:|---:|---:|---|
| drawdown_2p5_5 | 9 | 64.000000 | 0.776763 | 3.545891 | {'large_adverse_mark_after_exit': 5, 'loss_control_cost': 2, 'marginal_p_hold': 6, 'moderate_adverse_mark_after_exit': 1, 'moderate_fair_drawdown': 9, 'negative_delta': 2, 'positive_delta': 7, 'post_exit_mark_went_full_loss': 3, 'very_high_p_hold': 3, 'winner_recovery': 7} |
| drawdown_gt_5 | 3 | -32.000000 | 0.782533 | 7.080064 | {'large_adverse_mark_after_exit': 2, 'large_fair_drawdown': 3, 'loss_control_cost': 1, 'marginal_p_hold': 2, 'negative_delta': 1, 'positive_delta': 2, 'post_exit_mark_went_full_loss': 1, 'very_high_p_hold': 1, 'winner_recovery': 2} |
| drawdown_lte_2p5 | 13 | 305.000000 | 0.789910 | -2.452577 | {'favorable_fair_value': 9, 'large_adverse_mark_after_exit': 8, 'loss_control_cost': 2, 'marginal_p_hold': 6, 'moderate_adverse_mark_after_exit': 1, 'negative_delta': 2, 'positive_delta': 11, 'post_exit_mark_went_full_loss': 4, 'small_fair_drawdown': 4, 'very_high_p_hold': 7, 'winner_recovery': 11} |
| loss_control_cost | 5 | -730.000000 | 0.782222 | 2.577812 | {'favorable_fair_value': 2, 'large_adverse_mark_after_exit': 4, 'large_fair_drawdown': 1, 'loss_control_cost': 5, 'marginal_p_hold': 4, 'moderate_fair_drawdown': 2, 'negative_delta': 5, 'post_exit_mark_went_full_loss': 1, 'very_high_p_hold': 1} |
| p_hold_075_079 | 14 | -20.000000 | 0.773918 | 2.036735 | {'favorable_fair_value': 4, 'large_adverse_mark_after_exit': 9, 'large_fair_drawdown': 2, 'loss_control_cost': 4, 'marginal_p_hold': 14, 'moderate_fair_drawdown': 6, 'negative_delta': 4, 'positive_delta': 10, 'post_exit_mark_went_full_loss': 5, 'small_fair_drawdown': 2, 'winner_recovery': 10} |
| p_hold_ge_079 | 11 | 357.000000 | 0.797495 | -0.658598 | {'favorable_fair_value': 5, 'large_adverse_mark_after_exit': 6, 'large_fair_drawdown': 1, 'loss_control_cost': 1, 'moderate_adverse_mark_after_exit': 2, 'moderate_fair_drawdown': 3, 'negative_delta': 1, 'positive_delta': 10, 'post_exit_mark_went_full_loss': 3, 'small_fair_drawdown': 2, 'very_high_p_hold': 11, 'winner_recovery': 10} |
| winner_recovery | 20 | 1067.000000 | 0.784810 | 0.419032 | {'favorable_fair_value': 7, 'large_adverse_mark_after_exit': 11, 'large_fair_drawdown': 2, 'marginal_p_hold': 10, 'moderate_adverse_mark_after_exit': 2, 'moderate_fair_drawdown': 7, 'positive_delta': 20, 'post_exit_mark_went_full_loss': 7, 'small_fair_drawdown': 4, 'very_high_p_hold': 10, 'winner_recovery': 20} |

## Harmful Suppressed Rows

| market | side | result | entry | exit | p_hold | drawdown | current c | hold c | delta c | worst mark | tags |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY060700-00 | no | yes | 84 | 80 | 0.799603 | 4.039746 | -8.000000 | -168.000000 | -160.000000 | 10 | loss_control_cost, very_high_p_hold, moderate_fair_drawdown, large_adverse_mark_after_exit, negative_delta |
| KXBTC15M-26MAY071015-15 | no | yes | 78 | 79 | 0.789130 | -0.913001 | 2.000000 | -156.000000 | -158.000000 | 18 | loss_control_cost, marginal_p_hold, favorable_fair_value, large_adverse_mark_after_exit, negative_delta |
| KXBTC15M-26MAY060900-00 | yes | no | 78 | 73 | 0.789990 | -0.998969 | -10.000000 | -156.000000 | -146.000000 | 34 | loss_control_cost, marginal_p_hold, favorable_fair_value, large_adverse_mark_after_exit, negative_delta |
| KXBTC15M-26MAY071015-15 | no | yes | 81 | 73 | 0.763980 | 4.602013 | -16.000000 | -162.000000 | -146.000000 | 18 | loss_control_cost, marginal_p_hold, moderate_fair_drawdown, large_adverse_mark_after_exit, negative_delta |
| KXBTC15M-26MAY062130-30 | no | yes | 76 | 60 | 0.768407 | 6.159273 | -32.000000 | -152.000000 | -120.000000 | -152 | loss_control_cost, marginal_p_hold, large_fair_drawdown, post_exit_mark_went_full_loss, negative_delta |

## Helpful Suppressed Rows

| market | side | result | entry | exit | p_hold | drawdown | current c | hold c | delta c | worst mark | tags |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY060300-00 | yes | yes | 80 | 69 | 0.753164 | 4.683642 | -22.000000 | 40.000000 | 62.000000 | 28 | winner_recovery, marginal_p_hold, moderate_fair_drawdown, large_adverse_mark_after_exit, positive_delta |
| KXBTC15M-26MAY060930-30 | no | no | 76 | 69 | 0.787606 | -2.760587 | -14.000000 | 48.000000 | 62.000000 | -10 | winner_recovery, marginal_p_hold, favorable_fair_value, post_exit_mark_went_full_loss, positive_delta |
| KXBTC15M-26MAY071045-45 | no | no | 74 | 69 | 0.760529 | -2.052947 | -10.000000 | 52.000000 | 62.000000 | -14 | winner_recovery, marginal_p_hold, favorable_fair_value, post_exit_mark_went_full_loss, positive_delta |
| KXBTC15M-26MAY060915-15 | no | no | 70 | 70 | 0.793762 | -9.376204 | 0.000000 | 60.000000 | 60.000000 | 48 | winner_recovery, very_high_p_hold, favorable_fair_value, moderate_adverse_mark_after_exit, positive_delta |
| KXBTC15M-26MAY061015-15 | no | no | 70 | 70 | 0.799979 | -9.997858 | 0.000000 | 60.000000 | 60.000000 | 4 | winner_recovery, very_high_p_hold, favorable_fair_value, large_adverse_mark_after_exit, positive_delta |
| KXBTC15M-26MAY061030-30 | yes | yes | 78 | 70 | 0.752739 | 2.726149 | -16.000000 | 44.000000 | 60.000000 | -10 | winner_recovery, marginal_p_hold, moderate_fair_drawdown, post_exit_mark_went_full_loss, positive_delta |
| KXBTC15M-26MAY060930-30 | no | no | 73 | 72 | 0.799180 | -6.917970 | -3.000000 | 54.000000 | 57.000000 | -10 | winner_recovery, very_high_p_hold, favorable_fair_value, post_exit_mark_went_full_loss, positive_delta |
| KXBTC15M-26MAY060645-45 | yes | yes | 78 | 72 | 0.779789 | 0.021114 | -12.000000 | 44.000000 | 56.000000 | 30 | winner_recovery, marginal_p_hold, small_fair_drawdown, large_adverse_mark_after_exit, positive_delta |
| KXBTC15M-26MAY060630-30 | yes | yes | 79 | 73 | 0.777774 | 1.222639 | -12.000000 | 42.000000 | 54.000000 | 26 | winner_recovery, marginal_p_hold, small_fair_drawdown, large_adverse_mark_after_exit, positive_delta |
| KXBTC15M-26MAY061030-30 | yes | yes | 78 | 73 | 0.796458 | -1.645773 | -10.000000 | 44.000000 | 54.000000 | -10 | winner_recovery, very_high_p_hold, favorable_fair_value, post_exit_mark_went_full_loss, positive_delta |
| KXBTC15M-26MAY060300-00 | yes | yes | 81 | 74 | 0.780402 | 2.959820 | -14.000000 | 38.000000 | 52.000000 | 28 | winner_recovery, marginal_p_hold, moderate_fair_drawdown, large_adverse_mark_after_exit, positive_delta |
| KXBTC15M-26MAY060645-45 | yes | yes | 82 | 74 | 0.799349 | 2.065125 | -16.000000 | 36.000000 | 52.000000 | 30 | winner_recovery, very_high_p_hold, small_fair_drawdown, large_adverse_mark_after_exit, positive_delta |
| KXBTC15M-26MAY071315-15 | yes | yes | 81 | 74 | 0.784166 | 2.583397 | -14.000000 | 38.000000 | 52.000000 | 28 | winner_recovery, marginal_p_hold, moderate_fair_drawdown, large_adverse_mark_after_exit, positive_delta |
| KXBTC15M-26MAY060245-45 | yes | yes | 80 | 76 | 0.793334 | 2.666578 | -8.000000 | 40.000000 | 48.000000 | 40 | winner_recovery, very_high_p_hold, moderate_fair_drawdown, moderate_adverse_mark_after_exit, positive_delta |
| KXBTC15M-26MAY071215-15 | no | no | 84 | 76 | 0.797661 | 4.233856 | -16.000000 | 32.000000 | 48.000000 | -28 | winner_recovery, very_high_p_hold, moderate_fair_drawdown, post_exit_mark_went_full_loss, positive_delta |
| KXBTC15M-26MAY071215-15 | no | no | 80 | 76 | 0.765822 | 3.417815 | -8.000000 | 40.000000 | 48.000000 | -28 | winner_recovery, marginal_p_hold, moderate_fair_drawdown, post_exit_mark_went_full_loss, positive_delta |
| KXBTC15M-26MAY061045-45 | yes | yes | 80 | 77 | 0.796949 | 0.305083 | -6.000000 | 40.000000 | 46.000000 | 28 | winner_recovery, very_high_p_hold, small_fair_drawdown, large_adverse_mark_after_exit, positive_delta |
| KXBTC15M-26MAY061445-45 | no | no | 88 | 77 | 0.797830 | 8.216985 | -22.000000 | 24.000000 | 46.000000 | 14 | winner_recovery, very_high_p_hold, large_fair_drawdown, large_adverse_mark_after_exit, positive_delta |
| KXBTC15M-26MAY071315-15 | yes | yes | 80 | 77 | 0.798341 | -0.834147 | -6.000000 | 40.000000 | 46.000000 | 28 | winner_recovery, very_high_p_hold, favorable_fair_value, large_adverse_mark_after_exit, positive_delta |
| KXBTC15M-26MAY071000-00 | no | no | 71 | 79 | 0.781361 | 6.863933 | 16.000000 | 58.000000 | 42.000000 | 12 | winner_recovery, marginal_p_hold, large_fair_drawdown, large_adverse_mark_after_exit, positive_delta |
