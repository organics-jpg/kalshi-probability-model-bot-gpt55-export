# v28 Top-Component Loss Cluster Drilldown

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:52:54.650127+00:00`
- Source report UTC: `2026-05-11T02:52:54.104756+00:00`
- Variant: `rescue_drop15_plus_absd_parent_fill_to75`
- Variant PnL/WL/Coverage: `1680.500c`, `64/12`, `75.248%`
- Loss net: `-533.000c` across `12` rows

## Interpretation

- Research-only loss drilldown; no live bot changes or orders.
- Best inspected variant is rescue_drop15_plus_absd_parent_fill_to75 with net 1680.5c and W/L 64/12.
- Exit-policy false negatives remain: 3 losing rows would have been helped by holding instead of taking current exit marks.
- Parent-fill losses are the entry/FV repair target: 5 rows for -225.0c.
- Rejected/reconstructed losses are still material: 7 losing rows for -303.0c.
- On losing rows with both marks, holding would worsen losses by -52.0c, so these are mostly true FV/entry losers rather than clipped winners.

## Losses By Mode

| mode | rows | net | source counts | tags |
|---|---:|---:|---|---|
| `parent_fill_entry_or_fv_loss` | 5 | -225.000 | `{'rejected_actionable': 5}` | `{'source_quality_risk': 5, 'entry_timing_or_fv_error': 5}` |
| `missed_exit_rescue_false_negative` | 3 | -198.000 | `{'approved_entry': 3}` | `{'exit_policy_error': 3}` |
| `true_loser_entry_or_fv_loss` | 4 | -110.000 | `{'rejected_actionable': 2, 'approved_entry': 2}` | `{'source_quality_risk': 2, 'fv_or_entry_error': 4}` |

## Worst Loss Rows

| market | side | source | mode | component | weighted | hold | current | exit | p_hold | drawdown | recheck |
|---|---|---|---|---|---:|---:|---:|---|---:|---:|---:|
| KXBTC15M-26MAY061800-00 | no | approved_entry | `missed_exit_rescue_false_negative` | delayed_recheck_rescue:drop15_bid60 | -86.000 | 66.000 | -86.000 | mushroom_v28_probability_collapse_full | 0.553 | 11.739 | 45.000 |
| KXBTC15M-26MAY060745-45 | yes | rejected_actionable | `true_loser_entry_or_fv_loss` | delayed_recheck_rescue:drop15_bid60 | -70.000 | -156.000 | -70.000 | mushroom_v28_probability_collapse_full | 0.564 | 21.643 | 3.000 |
| KXBTC15M-26MAY062015-15 | no | approved_entry | `missed_exit_rescue_false_negative` | delayed_recheck_rescue:drop15_bid60 | -60.000 | 116.000 | -60.000 | mushroom_v28_probability_collapse_full | 0.269 | 15.107 | 10.000 |
| KXBTC15M-26MAY062345-45 | no | rejected_actionable | `parent_fill_entry_or_fv_loss` | parent_midprice_hold_fill | -60.000 | n/a | n/a | None | n/a | n/a | n/a |
| KXBTC15M-26MAY070630-30 | yes | rejected_actionable | `parent_fill_entry_or_fv_loss` | parent_midprice_hold_fill | -59.000 | n/a | n/a | None | n/a | n/a | n/a |
| KXBTC15M-26MAY060330-30 | yes | approved_entry | `missed_exit_rescue_false_negative` | delayed_recheck_rescue:drop15_bid60 | -52.000 | 42.000 | -52.000 | mushroom_v28_exit_value_over_hold | 0.501 | 28.914 | 43.000 |
| KXBTC15M-26MAY070615-15 | yes | rejected_actionable | `parent_fill_entry_or_fv_loss` | parent_midprice_hold_fill | -47.000 | n/a | n/a | None | n/a | n/a | n/a |
| KXBTC15M-26MAY061700-00 | no | rejected_actionable | `parent_fill_entry_or_fv_loss` | parent_midprice_hold_fill | -42.000 | n/a | n/a | None | n/a | n/a | n/a |
| KXBTC15M-26MAY061300-00 | yes | approved_entry | `true_loser_entry_or_fv_loss` | delayed_recheck_rescue:drop15_bid60 | -30.000 | -160.000 | -30.000 | mushroom_v28_probability_collapse_full | 0.666 | 13.357 | n/a |
| KXBTC15M-26MAY061715-15 | yes | rejected_actionable | `parent_fill_entry_or_fv_loss` | parent_midprice_hold_fill | -17.000 | n/a | n/a | None | n/a | n/a | n/a |
| KXBTC15M-26MAY062130-30 | no | rejected_actionable | `true_loser_entry_or_fv_loss` | delayed_recheck_rescue:drop15_bid60 | -8.000 | -152.000 | -32.000 | mushroom_v28_probability_reduce | 0.768 | 6.159 | 43.000 |
| KXBTC15M-26MAY070015-15 | no | approved_entry | `true_loser_entry_or_fv_loss` | delayed_recheck_rescue:drop15_bid60 | -2.000 | -140.000 | -2.000 | mushroom_v28_exit_value_over_hold | 0.597 | 10.344 | 52.000 |
