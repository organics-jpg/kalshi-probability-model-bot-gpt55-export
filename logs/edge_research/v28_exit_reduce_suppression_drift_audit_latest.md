# v28 Exit Reduce Suppression Drift Audit

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:07:54.215923+00:00`
- Freeze UTC: `2026-05-06T06:33:56.987999+00:00`
- Candidate: `suppress_reduce_p_hold_ge_075`
- Suppressed exits/net delta: `25/337.000000c`
- Helpful/harmful delta: `1067.000000c/-730.000000c`
- Latest suppressed row: `KXBTC15M-26MAY071315-15` delta `52.000000c`

## Interpretation

- This audit uses only the frozen reduce-suppression research rows; it does not alter exits or live trading.
- Blanket suppression remains positive at 337.0c across 25 suppressed exits, but harmful rows cost -730.0c.
- Before the latest suppressed exit, the lane was 285.0c; the latest row added 52.0c and is tagged ['helpful_winner_recovery', 'p_hold_075_079', 'moderate_fair_drawdown', 'positive_delta'].
- Worst harmful suppression is KXBTC15M-26MAY060700-00 with delta -160.0c, p_hold 0.799603, and fair drawdown 4.039746c.
- Next exit research should isolate the harmful probability-reduce states before broadening suppression.

## Hourly Suppression Drift

| hour | rows | net delta c | helpful | harmful | tags |
|---|---:|---:|---:|---:|---|
| 2026-05-06T06:00Z | 3 | 162.000000 | 3 | 0 | {'helpful_winner_recovery': 3, 'moderate_fair_drawdown': 3, 'p_hold_075_079': 2, 'p_hold_ge_079': 1, 'positive_delta': 3} |
| 2026-05-06T10:00Z | 4 | 2.000000 | 3 | 1 | {'harmful_loss_control_cost': 1, 'helpful_winner_recovery': 3, 'moderate_fair_drawdown': 1, 'negative_delta': 1, 'p_hold_075_079': 2, 'p_hold_ge_079': 2, 'positive_delta': 3, 'small_fair_drawdown': 3} |
| 2026-05-06T12:00Z | 1 | -146.000000 | 0 | 1 | {'favorable_fair_value': 1, 'harmful_loss_control_cost': 1, 'negative_delta': 1, 'p_hold_075_079': 1} |
| 2026-05-06T13:00Z | 3 | 179.000000 | 3 | 0 | {'favorable_fair_value': 3, 'helpful_winner_recovery': 3, 'p_hold_075_079': 1, 'p_hold_ge_079': 2, 'positive_delta': 3, 'post_exit_mark_full_loss': 2} |
| 2026-05-06T14:00Z | 4 | 220.000000 | 4 | 0 | {'favorable_fair_value': 2, 'helpful_winner_recovery': 4, 'moderate_fair_drawdown': 1, 'p_hold_075_079': 1, 'p_hold_ge_079': 3, 'positive_delta': 4, 'post_exit_mark_full_loss': 2, 'small_fair_drawdown': 1} |
| 2026-05-06T18:00Z | 1 | 46.000000 | 1 | 0 | {'helpful_winner_recovery': 1, 'large_fair_drawdown': 1, 'p_hold_ge_079': 1, 'positive_delta': 1} |
| 2026-05-07T01:00Z | 1 | -120.000000 | 0 | 1 | {'harmful_loss_control_cost': 1, 'large_fair_drawdown': 1, 'negative_delta': 1, 'p_hold_075_079': 1, 'post_exit_mark_full_loss': 1} |
| 2026-05-07T13:00Z | 1 | 42.000000 | 1 | 0 | {'helpful_winner_recovery': 1, 'large_fair_drawdown': 1, 'p_hold_075_079': 1, 'positive_delta': 1} |
| 2026-05-07T14:00Z | 3 | -242.000000 | 1 | 2 | {'favorable_fair_value': 2, 'harmful_loss_control_cost': 2, 'helpful_winner_recovery': 1, 'moderate_fair_drawdown': 1, 'negative_delta': 2, 'p_hold_075_079': 3, 'positive_delta': 1, 'post_exit_mark_full_loss': 1} |
| 2026-05-07T16:00Z | 2 | 96.000000 | 2 | 0 | {'helpful_winner_recovery': 2, 'moderate_fair_drawdown': 2, 'p_hold_075_079': 1, 'p_hold_ge_079': 1, 'positive_delta': 2, 'post_exit_mark_full_loss': 2} |
| 2026-05-07T17:00Z | 2 | 98.000000 | 2 | 0 | {'favorable_fair_value': 1, 'helpful_winner_recovery': 2, 'moderate_fair_drawdown': 1, 'p_hold_075_079': 1, 'p_hold_ge_079': 1, 'positive_delta': 2} |

## Harmful Suppressions

| market | side | result | exit_ts | p_hold | drawdown | current c | hold c | delta c | worst mark | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY060700-00 | no | yes | 2026-05-06T10:51:28.209785+00:00 | 0.799603 | 4.039746 | -8.000000 | -168.000000 | -160.000000 | 10 | harmful_loss_control_cost, p_hold_ge_079, moderate_fair_drawdown, negative_delta |
| KXBTC15M-26MAY071015-15 | no | yes | 2026-05-07T14:06:00.919719+00:00 | 0.789130 | -0.913001 | 2.000000 | -156.000000 | -158.000000 | 18 | harmful_loss_control_cost, p_hold_075_079, favorable_fair_value, negative_delta |
| KXBTC15M-26MAY060900-00 | yes | no | 2026-05-06T12:48:32.874186+00:00 | 0.789990 | -0.998969 | -10.000000 | -156.000000 | -146.000000 | 34 | harmful_loss_control_cost, p_hold_075_079, favorable_fair_value, negative_delta |
| KXBTC15M-26MAY071015-15 | no | yes | 2026-05-07T14:06:32.838027+00:00 | 0.763980 | 4.602013 | -16.000000 | -162.000000 | -146.000000 | 18 | harmful_loss_control_cost, p_hold_075_079, moderate_fair_drawdown, negative_delta |
| KXBTC15M-26MAY062130-30 | no | yes | 2026-05-07T01:23:37.628590+00:00 | 0.768407 | 6.159273 | -32.000000 | -152.000000 | -120.000000 | -152 | harmful_loss_control_cost, p_hold_075_079, large_fair_drawdown, post_exit_mark_full_loss, negative_delta |

## Suppression Sequence

| idx | market | exit_ts | class | delta c | cumulative c | p_hold | drawdown | tags |
|---:|---|---|---|---:|---:|---:|---:|---|
| 1 | KXBTC15M-26MAY060245-45 | 2026-05-06T06:39:59.258259+00:00 | helpful_winner_recovery | 48.000000 | 48.000000 | 0.793334 | 2.666578 | helpful_winner_recovery, p_hold_ge_079, moderate_fair_drawdown, positive_delta |
| 2 | KXBTC15M-26MAY060300-00 | 2026-05-06T06:50:15.626414+00:00 | helpful_winner_recovery | 52.000000 | 100.000000 | 0.780402 | 2.959820 | helpful_winner_recovery, p_hold_075_079, moderate_fair_drawdown, positive_delta |
| 3 | KXBTC15M-26MAY060300-00 | 2026-05-06T06:55:59.624417+00:00 | helpful_winner_recovery | 62.000000 | 162.000000 | 0.753164 | 4.683642 | helpful_winner_recovery, p_hold_075_079, moderate_fair_drawdown, positive_delta |
| 4 | KXBTC15M-26MAY060630-30 | 2026-05-06T10:21:39.089288+00:00 | helpful_winner_recovery | 54.000000 | 216.000000 | 0.777774 | 1.222639 | helpful_winner_recovery, p_hold_075_079, small_fair_drawdown, positive_delta |
| 5 | KXBTC15M-26MAY060645-45 | 2026-05-06T10:34:59.814243+00:00 | helpful_winner_recovery | 52.000000 | 268.000000 | 0.799349 | 2.065125 | helpful_winner_recovery, p_hold_ge_079, small_fair_drawdown, positive_delta |
| 6 | KXBTC15M-26MAY060645-45 | 2026-05-06T10:37:07.824382+00:00 | helpful_winner_recovery | 56.000000 | 324.000000 | 0.779789 | 0.021114 | helpful_winner_recovery, p_hold_075_079, small_fair_drawdown, positive_delta |
| 7 | KXBTC15M-26MAY060700-00 | 2026-05-06T10:51:28.209785+00:00 | harmful_loss_control_cost | -160.000000 | 164.000000 | 0.799603 | 4.039746 | harmful_loss_control_cost, p_hold_ge_079, moderate_fair_drawdown, negative_delta |
| 8 | KXBTC15M-26MAY060900-00 | 2026-05-06T12:48:32.874186+00:00 | harmful_loss_control_cost | -146.000000 | 18.000000 | 0.789990 | -0.998969 | harmful_loss_control_cost, p_hold_075_079, favorable_fair_value, negative_delta |
| 9 | KXBTC15M-26MAY060915-15 | 2026-05-06T13:02:22.470690+00:00 | helpful_winner_recovery | 60.000000 | 78.000000 | 0.793762 | -9.376204 | helpful_winner_recovery, p_hold_ge_079, favorable_fair_value, positive_delta |
| 10 | KXBTC15M-26MAY060930-30 | 2026-05-06T13:21:54.679378+00:00 | helpful_winner_recovery | 62.000000 | 140.000000 | 0.787606 | -2.760587 | helpful_winner_recovery, p_hold_075_079, favorable_fair_value, post_exit_mark_full_loss, positive_delta |
| 11 | KXBTC15M-26MAY060930-30 | 2026-05-06T13:22:53.670531+00:00 | helpful_winner_recovery | 57.000000 | 197.000000 | 0.799180 | -6.917970 | helpful_winner_recovery, p_hold_ge_079, favorable_fair_value, post_exit_mark_full_loss, positive_delta |
| 12 | KXBTC15M-26MAY061015-15 | 2026-05-06T14:03:26.021060+00:00 | helpful_winner_recovery | 60.000000 | 257.000000 | 0.799979 | -9.997858 | helpful_winner_recovery, p_hold_ge_079, favorable_fair_value, positive_delta |
| 13 | KXBTC15M-26MAY061030-30 | 2026-05-06T14:21:53.079356+00:00 | helpful_winner_recovery | 60.000000 | 317.000000 | 0.752739 | 2.726149 | helpful_winner_recovery, p_hold_075_079, moderate_fair_drawdown, post_exit_mark_full_loss, positive_delta |
| 14 | KXBTC15M-26MAY061030-30 | 2026-05-06T14:22:40.078029+00:00 | helpful_winner_recovery | 54.000000 | 371.000000 | 0.796458 | -1.645773 | helpful_winner_recovery, p_hold_ge_079, favorable_fair_value, post_exit_mark_full_loss, positive_delta |
| 15 | KXBTC15M-26MAY061045-45 | 2026-05-06T14:36:34.192931+00:00 | helpful_winner_recovery | 46.000000 | 417.000000 | 0.796949 | 0.305083 | helpful_winner_recovery, p_hold_ge_079, small_fair_drawdown, positive_delta |
| 16 | KXBTC15M-26MAY061445-45 | 2026-05-06T18:33:57.618763+00:00 | helpful_winner_recovery | 46.000000 | 463.000000 | 0.797830 | 8.216985 | helpful_winner_recovery, p_hold_ge_079, large_fair_drawdown, positive_delta |
| 17 | KXBTC15M-26MAY062130-30 | 2026-05-07T01:23:37.628590+00:00 | harmful_loss_control_cost | -120.000000 | 343.000000 | 0.768407 | 6.159273 | harmful_loss_control_cost, p_hold_075_079, large_fair_drawdown, post_exit_mark_full_loss, negative_delta |
| 18 | KXBTC15M-26MAY071000-00 | 2026-05-07T13:57:21.055475+00:00 | helpful_winner_recovery | 42.000000 | 385.000000 | 0.781361 | 6.863933 | helpful_winner_recovery, p_hold_075_079, large_fair_drawdown, positive_delta |
| 19 | KXBTC15M-26MAY071015-15 | 2026-05-07T14:06:00.919719+00:00 | harmful_loss_control_cost | -158.000000 | 227.000000 | 0.789130 | -0.913001 | harmful_loss_control_cost, p_hold_075_079, favorable_fair_value, negative_delta |
| 20 | KXBTC15M-26MAY071015-15 | 2026-05-07T14:06:32.838027+00:00 | harmful_loss_control_cost | -146.000000 | 81.000000 | 0.763980 | 4.602013 | harmful_loss_control_cost, p_hold_075_079, moderate_fair_drawdown, negative_delta |
| 21 | KXBTC15M-26MAY071045-45 | 2026-05-07T14:31:53.190347+00:00 | helpful_winner_recovery | 62.000000 | 143.000000 | 0.760529 | -2.052947 | helpful_winner_recovery, p_hold_075_079, favorable_fair_value, post_exit_mark_full_loss, positive_delta |
| 22 | KXBTC15M-26MAY071215-15 | 2026-05-07T16:08:26.386908+00:00 | helpful_winner_recovery | 48.000000 | 191.000000 | 0.797661 | 4.233856 | helpful_winner_recovery, p_hold_ge_079, moderate_fair_drawdown, post_exit_mark_full_loss, positive_delta |
| 23 | KXBTC15M-26MAY071215-15 | 2026-05-07T16:09:39.381902+00:00 | helpful_winner_recovery | 48.000000 | 239.000000 | 0.765822 | 3.417815 | helpful_winner_recovery, p_hold_075_079, moderate_fair_drawdown, post_exit_mark_full_loss, positive_delta |
| 24 | KXBTC15M-26MAY071315-15 | 2026-05-07T17:10:38.168558+00:00 | helpful_winner_recovery | 46.000000 | 285.000000 | 0.798341 | -0.834147 | helpful_winner_recovery, p_hold_ge_079, favorable_fair_value, positive_delta |
| 25 | KXBTC15M-26MAY071315-15 | 2026-05-07T17:11:27.190018+00:00 | helpful_winner_recovery | 52.000000 | 337.000000 | 0.784166 | 2.583397 | helpful_winner_recovery, p_hold_075_079, moderate_fair_drawdown, positive_delta |
