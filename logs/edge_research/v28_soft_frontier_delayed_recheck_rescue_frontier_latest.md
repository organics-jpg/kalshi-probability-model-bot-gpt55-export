# v28 Soft-Frontier Delayed-Recheck Rescue Frontier

Research-only diagnostic frontier. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:54:55.406199+00:00`

## Interpretation

- Research-only false-negative rescue frontier; no live bot changes or orders.
- Best diagnostic relax drop15_bid60 has net 1665.5c, delta vs base 164.0c, helpful/harmful 33/0, blockers ['diagnostic_prefreeze'].
- Any green relax is only a hypothesis until frozen and proven post-birth.

## Variants

| rank | variant | suppressed | H/H | base net | candidate net | delta base | losses | loss c | source counts | exit reasons | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| 1 | `drop15_bid60` | 35 | 33/0 | 1501.50 | 1665.50 | 164.00 | 7 | -308.00 | {'rejected_actionable': 3, 'approved_entry': 32} | {'mushroom_v28_exit_value_over_hold': 34, 'mushroom_v28_probability_collapse_full': 1} | diagnostic_prefreeze |
| 2 | `drop20_bid60` | 35 | 33/0 | 1501.50 | 1665.50 | 164.00 | 7 | -308.00 | {'rejected_actionable': 3, 'approved_entry': 32} | {'mushroom_v28_exit_value_over_hold': 34, 'mushroom_v28_probability_collapse_full': 1} | diagnostic_prefreeze |
| 3 | `drop11_bid60` | 34 | 32/0 | 1501.50 | 1601.50 | 100.00 | 7 | -308.00 | {'rejected_actionable': 3, 'approved_entry': 31} | {'mushroom_v28_exit_value_over_hold': 33, 'mushroom_v28_probability_collapse_full': 1} | diagnostic_prefreeze |
| 4 | `bid45_drop15_phold60` | 31 | 29/0 | 1501.50 | 1513.50 | 12.00 | 8 | -318.00 | {'rejected_actionable': 3, 'approved_entry': 28} | {'mushroom_v28_exit_value_over_hold': 30, 'mushroom_v28_probability_collapse_full': 1} | diagnostic_prefreeze |
| 5 | `base_delay60_bid60_drop10` | 33 | 31/0 | 1501.50 | 1501.50 | 0.00 | 8 | -340.00 | {'rejected_actionable': 3, 'approved_entry': 30} | {'mushroom_v28_exit_value_over_hold': 33} | diagnostic_prefreeze, does_not_improve_base_delayed_recheck |
| 6 | `bid40_drop20_phold50` | 34 | 31/1 | 1501.50 | 1535.50 | 34.00 | 7 | -338.00 | {'rejected_actionable': 4, 'approved_entry': 30} | {'mushroom_v28_probability_reduce': 1, 'mushroom_v28_exit_value_over_hold': 32, 'mushroom_v28_probability_collapse_full': 1} | diagnostic_prefreeze, suppressed_losers_present |
| 7 | `collapse_rescue_phold60_drop12` | 1 | 1/0 | 1501.50 | 1157.50 | -344.00 | 8 | -318.00 | {'approved_entry': 1} | {'mushroom_v28_probability_collapse_full': 1} | diagnostic_prefreeze, does_not_improve_base_delayed_recheck, suppressed_decisions_lt_30 |
| 8 | `bid40_drop20_phold60` | 32 | 29/1 | 1501.50 | 1483.50 | -18.00 | 8 | -348.00 | {'rejected_actionable': 4, 'approved_entry': 28} | {'mushroom_v28_probability_reduce': 1, 'mushroom_v28_exit_value_over_hold': 30, 'mushroom_v28_probability_collapse_full': 1} | diagnostic_prefreeze, suppressed_losers_present, does_not_improve_base_delayed_recheck |
| 9 | `bid40_drop20_phold55` | 32 | 29/1 | 1501.50 | 1483.50 | -18.00 | 8 | -348.00 | {'rejected_actionable': 4, 'approved_entry': 28} | {'mushroom_v28_probability_reduce': 1, 'mushroom_v28_exit_value_over_hold': 30, 'mushroom_v28_probability_collapse_full': 1} | diagnostic_prefreeze, suppressed_losers_present, does_not_improve_base_delayed_recheck |
| 10 | `low_bid_value_exit_phold50` | 36 | 33/1 | 1501.50 | 1464.00 | -37.50 | 7 | -426.00 | {'approved_entry': 32, 'rejected_actionable': 4} | {'mushroom_v28_exit_value_over_hold': 36} | diagnostic_prefreeze, suppressed_losers_present, does_not_improve_base_delayed_recheck |
