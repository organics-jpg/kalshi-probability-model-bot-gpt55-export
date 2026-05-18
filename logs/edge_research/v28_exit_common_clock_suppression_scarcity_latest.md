# v28 Exit Common-Clock Suppression Scarcity

Research-only audit. No live bot changes or orders.

- Generated UTC: `2026-05-07T18:03:46.256830+00:00`
- Window: `new_exit_mix_common_forward_v2`
- Freeze UTC: `2026-05-06T22:01:04.415577+00:00`
- Rows: `58`

## Interpretation

- This is an audit over the existing strict common-clock v2 rows; it does not create or change a live exit rule.
- Best audit policy v1_like_on_v2_clock has 58 settled, 17 suppressions, candidate net 668.0c, delta 242.0c, loss cost 0c, blockers ['suppressed_decisions_lt_30'].
- V2 control suppresses 5 rows for 152.0c delta; the scarcity problem remains suppression count and cushion, not observed harmful suppressions.

## Policies

| rank | policy | settled | suppressed | helpful/harmful | current c | candidate c | delta c | recovery c | loss cost c | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | v1_like_on_v2_clock | 58 | 17 | 17/0 | 426.000000 | 668.000000 | 242.000000 | 242.000000 | 0 | 6 | suppressed_decisions_lt_30 |
| 2 | value_p85_shallow10 | 58 | 9 | 9/0 | 426.000000 | 626.000000 | 200.000000 | 200.000000 | 0 | 6 | suppressed_decisions_lt_30 |
| 3 | v2_control | 58 | 5 | 5/0 | 426.000000 | 578.000000 | 152.000000 | 152.000000 | 0 | 5 | suppressed_decisions_lt_30 |
| 4 | value_v2_plus_reduce_shallow2p5 | 58 | 5 | 5/0 | 426.000000 | 578.000000 | 152.000000 | 152.000000 | 0 | 5 | suppressed_decisions_lt_30 |
| 5 | value_p90_shallow10 | 58 | 4 | 4/0 | 426.000000 | 534.000000 | 108.000000 | 108.000000 | 0 | 5 | suppressed_decisions_lt_30 |
| 6 | value_p80_shallow5 | 58 | 9 | 7/2 | 426.000000 | 272.000000 | -154.000000 | 196.000000 | -350.000000 | 2 | suppressed_decisions_lt_30, delta_not_positive, loss_control_cost_negative, full_loss_cushion_lt_3 |

## Worst Suppressed Rows By Policy

| policy | market | side/result | reason | won | p_hold | gap | drawdown | current | hold | delta | tags |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| v1_like_on_v2_clock | KXBTC15M-26MAY061830-30 | no/no | mushroom_v28_exit_value_over_hold | True | 0.976718 | -0.013282 | -8.671753 | 20.000000 | 22.000000 | 2.000000 | value_over_hold, p_hold_ge95, gap_neg_0_5pp, drawdown_neg5_to_neg10 |
| v1_like_on_v2_clock | KXBTC15M-26MAY061915-15 | no/no | mushroom_v28_exit_value_over_hold | True | 0.981987 | -0.008013 | -11.198704 | 24.000000 | 26.000000 | 2.000000 | value_over_hold, p_hold_ge95, gap_neg_0_5pp, drawdown_deep_lt_neg10 |
| v1_like_on_v2_clock | KXBTC15M-26MAY062115-15 | yes/yes | mushroom_v28_exit_value_over_hold | True | 0.982461 | -0.007539 | -10.246054 | 22.000000 | 24.000000 | 2.000000 | value_over_hold, p_hold_ge95, gap_neg_0_5pp, drawdown_deep_lt_neg10 |
| v1_like_on_v2_clock | KXBTC15M-26MAY071145-45 | yes/yes | mushroom_v28_exit_value_over_hold | True | 0.982146 | -0.007854 | -17.214598 | 44.000000 | 46.000000 | 2.000000 | value_over_hold, p_hold_ge95, gap_neg_0_5pp, drawdown_deep_lt_neg10 |
| v1_like_on_v2_clock | KXBTC15M-26MAY071200-00 | no/no | mushroom_v28_exit_value_over_hold | True | 0.961165 | -0.018835 | -19.116535 | 42.000000 | 46.000000 | 4.000000 | value_over_hold, p_hold_ge95, gap_neg_0_5pp, drawdown_deep_lt_neg10 |
| v1_like_on_v2_clock | KXBTC15M-26MAY070030-30 | yes/yes | mushroom_v28_exit_value_over_hold | True | 0.921778 | -0.048222 | -10.177771 | 30.000000 | 36.000000 | 6.000000 | value_over_hold, p_hold_90_95, gap_neg_0_5pp, drawdown_deep_lt_neg10 |
| v1_like_on_v2_clock | KXBTC15M-26MAY070930-30 | yes/yes | mushroom_v28_exit_value_over_hold | True | 0.969995 | -0.010005 | -13.999536 | 34.000000 | 40.000000 | 6.000000 | value_over_hold, p_hold_ge95, gap_neg_0_5pp, drawdown_deep_lt_neg10 |
| v1_like_on_v2_clock | KXBTC15M-26MAY061815-15 | no/no | mushroom_v28_exit_value_over_hold | True | 0.950684 | -0.009316 | -11.068394 | 24.000000 | 32.000000 | 8.000000 | value_over_hold, p_hold_ge95, gap_neg_0_5pp, drawdown_deep_lt_neg10 |
| v1_like_on_v2_clock | KXBTC15M-26MAY071015-15 | yes/yes | mushroom_v28_exit_value_over_hold | True | 0.923102 | -0.016898 | -8.310249 | 20.000000 | 32.000000 | 12.000000 | value_over_hold, p_hold_90_95, gap_neg_0_5pp, drawdown_neg5_to_neg10 |
| v1_like_on_v2_clock | KXBTC15M-26MAY071315-15 | yes/yes | mushroom_v28_exit_value_over_hold | True | 0.927498 | -0.012502 | -14.749774 | 32.000000 | 44.000000 | 12.000000 | value_over_hold, p_hold_90_95, gap_neg_0_5pp, drawdown_deep_lt_neg10 |
| value_p85_shallow10 | KXBTC15M-26MAY061830-30 | no/no | mushroom_v28_exit_value_over_hold | True | 0.976718 | -0.013282 | -8.671753 | 20.000000 | 22.000000 | 2.000000 | value_over_hold, p_hold_ge95, gap_neg_0_5pp, drawdown_neg5_to_neg10 |
| value_p85_shallow10 | KXBTC15M-26MAY071015-15 | yes/yes | mushroom_v28_exit_value_over_hold | True | 0.923102 | -0.016898 | -8.310249 | 20.000000 | 32.000000 | 12.000000 | value_over_hold, p_hold_90_95, gap_neg_0_5pp, drawdown_neg5_to_neg10 |
| value_p85_shallow10 | KXBTC15M-26MAY062045-45 | no/no | mushroom_v28_exit_value_over_hold | True | 0.891386 | -0.028614 | -9.138584 | 24.000000 | 40.000000 | 16.000000 | value_over_hold, p_hold_85_90, gap_neg_0_5pp, drawdown_neg5_to_neg10 |
| value_p85_shallow10 | KXBTC15M-26MAY070545-45 | no/no | mushroom_v28_exit_value_over_hold | True | 0.892567 | -0.017433 | -7.256748 | 18.000000 | 36.000000 | 18.000000 | value_over_hold, p_hold_85_90, gap_neg_0_5pp, drawdown_neg5_to_neg10 |
| value_p85_shallow10 | KXBTC15M-26MAY070815-15 | yes/yes | mushroom_v28_exit_value_over_hold | True | 0.890464 | -0.019536 | -1.046434 | 2.000000 | 20.000000 | 18.000000 | value_over_hold, p_hold_85_90, gap_neg_0_5pp, drawdown_shallow_ge_neg2p5 |
| value_p85_shallow10 | KXBTC15M-26MAY071115-15 | yes/yes | mushroom_v28_exit_value_over_hold | True | 0.888844 | -0.021156 | -4.884431 | 14.000000 | 32.000000 | 18.000000 | value_over_hold, p_hold_85_90, gap_neg_0_5pp, drawdown_neg2p5_to_neg5 |
| value_p85_shallow10 | KXBTC15M-26MAY062215-15 | no/no | mushroom_v28_exit_value_over_hold | True | 0.860673 | -0.029327 | -2.067333 | 10.000000 | 32.000000 | 22.000000 | value_over_hold, p_hold_85_90, gap_neg_0_5pp, drawdown_shallow_ge_neg2p5 |
| value_p85_shallow10 | KXBTC15M-26MAY071315-15 | yes/yes | mushroom_v28_probability_reduce | True | 0.798341 | 0.028341 | -0.834147 | -6.000000 | 40.000000 | 46.000000 | probability_reduce, p_hold_79_85, gap_nonnegative, drawdown_shallow_ge_neg2p5 |
| value_p85_shallow10 | KXBTC15M-26MAY071215-15 | no/no | mushroom_v28_probability_reduce | True | 0.797661 | 0.037661 | 4.233856 | -16.000000 | 32.000000 | 48.000000 | probability_reduce, p_hold_79_85, gap_nonnegative, drawdown_shallow_ge_neg2p5 |
| v2_control | KXBTC15M-26MAY070815-15 | yes/yes | mushroom_v28_exit_value_over_hold | True | 0.890464 | -0.019536 | -1.046434 | 2.000000 | 20.000000 | 18.000000 | value_over_hold, p_hold_85_90, gap_neg_0_5pp, drawdown_shallow_ge_neg2p5 |
| v2_control | KXBTC15M-26MAY071115-15 | yes/yes | mushroom_v28_exit_value_over_hold | True | 0.888844 | -0.021156 | -4.884431 | 14.000000 | 32.000000 | 18.000000 | value_over_hold, p_hold_85_90, gap_neg_0_5pp, drawdown_neg2p5_to_neg5 |
| v2_control | KXBTC15M-26MAY062215-15 | no/no | mushroom_v28_exit_value_over_hold | True | 0.860673 | -0.029327 | -2.067333 | 10.000000 | 32.000000 | 22.000000 | value_over_hold, p_hold_85_90, gap_neg_0_5pp, drawdown_shallow_ge_neg2p5 |
| v2_control | KXBTC15M-26MAY071315-15 | yes/yes | mushroom_v28_probability_reduce | True | 0.798341 | 0.028341 | -0.834147 | -6.000000 | 40.000000 | 46.000000 | probability_reduce, p_hold_79_85, gap_nonnegative, drawdown_shallow_ge_neg2p5 |
| v2_control | KXBTC15M-26MAY071215-15 | no/no | mushroom_v28_probability_reduce | True | 0.797661 | 0.037661 | 4.233856 | -16.000000 | 32.000000 | 48.000000 | probability_reduce, p_hold_79_85, gap_nonnegative, drawdown_shallow_ge_neg2p5 |
| value_v2_plus_reduce_shallow2p5 | KXBTC15M-26MAY070815-15 | yes/yes | mushroom_v28_exit_value_over_hold | True | 0.890464 | -0.019536 | -1.046434 | 2.000000 | 20.000000 | 18.000000 | value_over_hold, p_hold_85_90, gap_neg_0_5pp, drawdown_shallow_ge_neg2p5 |
| value_v2_plus_reduce_shallow2p5 | KXBTC15M-26MAY071115-15 | yes/yes | mushroom_v28_exit_value_over_hold | True | 0.888844 | -0.021156 | -4.884431 | 14.000000 | 32.000000 | 18.000000 | value_over_hold, p_hold_85_90, gap_neg_0_5pp, drawdown_neg2p5_to_neg5 |
| value_v2_plus_reduce_shallow2p5 | KXBTC15M-26MAY062215-15 | no/no | mushroom_v28_exit_value_over_hold | True | 0.860673 | -0.029327 | -2.067333 | 10.000000 | 32.000000 | 22.000000 | value_over_hold, p_hold_85_90, gap_neg_0_5pp, drawdown_shallow_ge_neg2p5 |
| value_v2_plus_reduce_shallow2p5 | KXBTC15M-26MAY071315-15 | yes/yes | mushroom_v28_probability_reduce | True | 0.798341 | 0.028341 | -0.834147 | -6.000000 | 40.000000 | 46.000000 | probability_reduce, p_hold_79_85, gap_nonnegative, drawdown_shallow_ge_neg2p5 |
| value_v2_plus_reduce_shallow2p5 | KXBTC15M-26MAY071215-15 | no/no | mushroom_v28_probability_reduce | True | 0.797661 | 0.037661 | 4.233856 | -16.000000 | 32.000000 | 48.000000 | probability_reduce, p_hold_79_85, gap_nonnegative, drawdown_shallow_ge_neg2p5 |
| value_p90_shallow10 | KXBTC15M-26MAY061830-30 | no/no | mushroom_v28_exit_value_over_hold | True | 0.976718 | -0.013282 | -8.671753 | 20.000000 | 22.000000 | 2.000000 | value_over_hold, p_hold_ge95, gap_neg_0_5pp, drawdown_neg5_to_neg10 |
| value_p90_shallow10 | KXBTC15M-26MAY071015-15 | yes/yes | mushroom_v28_exit_value_over_hold | True | 0.923102 | -0.016898 | -8.310249 | 20.000000 | 32.000000 | 12.000000 | value_over_hold, p_hold_90_95, gap_neg_0_5pp, drawdown_neg5_to_neg10 |
| value_p90_shallow10 | KXBTC15M-26MAY071315-15 | yes/yes | mushroom_v28_probability_reduce | True | 0.798341 | 0.028341 | -0.834147 | -6.000000 | 40.000000 | 46.000000 | probability_reduce, p_hold_79_85, gap_nonnegative, drawdown_shallow_ge_neg2p5 |
| value_p90_shallow10 | KXBTC15M-26MAY071215-15 | no/no | mushroom_v28_probability_reduce | True | 0.797661 | 0.037661 | 4.233856 | -16.000000 | 32.000000 | 48.000000 | probability_reduce, p_hold_79_85, gap_nonnegative, drawdown_shallow_ge_neg2p5 |
| value_p80_shallow5 | KXBTC15M-26MAY062015-15 | yes/no | mushroom_v28_exit_value_over_hold | False | 0.812359 | -0.087641 | 4.764109 | 8.000000 | -172.000000 | -180.000000 | value_over_hold, p_hold_79_85, gap_neg_gt5pp, drawdown_shallow_ge_neg2p5 |
| value_p80_shallow5 | KXBTC15M-26MAY071100-00 | yes/no | mushroom_v28_exit_value_over_hold | False | 0.836750 | -0.013250 | -0.675039 | 4.000000 | -166.000000 | -170.000000 | value_over_hold, p_hold_79_85, gap_neg_0_5pp, drawdown_shallow_ge_neg2p5 |
| value_p80_shallow5 | KXBTC15M-26MAY070815-15 | yes/yes | mushroom_v28_exit_value_over_hold | True | 0.890464 | -0.019536 | -1.046434 | 2.000000 | 20.000000 | 18.000000 | value_over_hold, p_hold_85_90, gap_neg_0_5pp, drawdown_shallow_ge_neg2p5 |
| value_p80_shallow5 | KXBTC15M-26MAY070830-30 | no/no | mushroom_v28_exit_value_over_hold | True | 0.825354 | -0.084646 | -0.535395 | 18.000000 | 36.000000 | 18.000000 | value_over_hold, p_hold_79_85, gap_neg_gt5pp, drawdown_shallow_ge_neg2p5 |
| value_p80_shallow5 | KXBTC15M-26MAY071115-15 | yes/yes | mushroom_v28_exit_value_over_hold | True | 0.888844 | -0.021156 | -4.884431 | 14.000000 | 32.000000 | 18.000000 | value_over_hold, p_hold_85_90, gap_neg_0_5pp, drawdown_neg2p5_to_neg5 |
| value_p80_shallow5 | KXBTC15M-26MAY062215-15 | no/no | mushroom_v28_exit_value_over_hold | True | 0.860673 | -0.029327 | -2.067333 | 10.000000 | 32.000000 | 22.000000 | value_over_hold, p_hold_85_90, gap_neg_0_5pp, drawdown_shallow_ge_neg2p5 |
| value_p80_shallow5 | KXBTC15M-26MAY062315-15 | no/no | mushroom_v28_exit_value_over_hold | True | 0.811182 | -0.058818 | 2.881757 | 6.000000 | 32.000000 | 26.000000 | value_over_hold, p_hold_79_85, gap_neg_gt5pp, drawdown_shallow_ge_neg2p5 |
| value_p80_shallow5 | KXBTC15M-26MAY071315-15 | yes/yes | mushroom_v28_probability_reduce | True | 0.798341 | 0.028341 | -0.834147 | -6.000000 | 40.000000 | 46.000000 | probability_reduce, p_hold_79_85, gap_nonnegative, drawdown_shallow_ge_neg2p5 |
| value_p80_shallow5 | KXBTC15M-26MAY071215-15 | no/no | mushroom_v28_probability_reduce | True | 0.797661 | 0.037661 | 4.233856 | -16.000000 | 32.000000 | 48.000000 | probability_reduce, p_hold_79_85, gap_nonnegative, drawdown_shallow_ge_neg2p5 |
