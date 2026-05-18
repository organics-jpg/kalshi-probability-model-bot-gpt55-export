# v28 Feature-Gate Exit/State Repair Frontier

Research-only diagnostic. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:54:29.639158+00:00`
- Candidate: `post_feature_freeze_entry_raw03_recross70_abs075`

## Interpretation

- Research-only frontier; it does not change live exits or place orders.
- Baseline selected-side live PnL is 311.0c across 40 traded feature-gate markets.
- Best diagnostic variant is suppress_value_or_reduce_p_hold85 at 1331.6c, delta 1020.5999999999999c versus actual live selected-side exits.
- Rows remain non-deployable from this report alone because the simulation uses settlement outcomes and only covers live selected-side overlap.

## Exit Suppression Frontier

| variant | sim net c | delta live c | delta hold-all c | suppressed | W/L suppressed | worst market c | source counts | family counts | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| `suppress_value_or_reduce_p_hold85` | 1331.60 | 1020.60 | 526.84 | 12 | 12/0 | -99.00 | `{'approved_entry': 11, 'rejected_actionable': 1}` | `{'probability_collapse': 2, 'probability_reduce': 5, 'value_over_hold': 12}` | diagnostic_counterfactual_uses_settlement_outcomes, selected_side_live_subset_only, not_frozen_forward_shadow_policy |
| `hold_approved_entry_source_oracle` | 1210.36 | 899.36 | 405.60 | 35 | 31/4 | -511.00 | `{'approved_entry': 35}` | `{'probability_collapse': 6, 'probability_reduce': 21, 'value_over_hold': 15}` | diagnostic_counterfactual_uses_settlement_outcomes, selected_side_live_subset_only, not_frozen_forward_shadow_policy |
| `approved_suppress_any_exit_family` | 1210.36 | 899.36 | 405.60 | 29 | 25/4 | -511.00 | `{'approved_entry': 29}` | `{'probability_collapse': 6, 'probability_reduce': 21, 'value_over_hold': 15}` | diagnostic_counterfactual_uses_settlement_outcomes, selected_side_live_subset_only, not_frozen_forward_shadow_policy |
| `approved_suppress_value_or_reduce` | 1074.36 | 763.36 | 269.60 | 28 | 24/4 | -511.00 | `{'approved_entry': 28}` | `{'probability_collapse': 5, 'probability_reduce': 21, 'value_over_hold': 15}` | diagnostic_counterfactual_uses_settlement_outcomes, selected_side_live_subset_only, not_frozen_forward_shadow_policy |
| `suppress_value_or_reduce_p_hold80` | 931.60 | 620.60 | 126.84 | 14 | 13/1 | -511.00 | `{'approved_entry': 13, 'rejected_actionable': 1}` | `{'probability_collapse': 2, 'probability_reduce': 7, 'value_over_hold': 14}` | diagnostic_counterfactual_uses_settlement_outcomes, selected_side_live_subset_only, not_frozen_forward_shadow_policy |
| `hold_all_selected_oracle` | 804.76 | 493.76 | 0.00 | 40 | 34/6 | -511.00 | `{'approved_entry': 35, 'rejected_actionable': 5}` | `{'probability_collapse': 7, 'probability_reduce': 23, 'value_over_hold': 16}` | diagnostic_counterfactual_uses_settlement_outcomes, selected_side_live_subset_only, not_frozen_forward_shadow_policy |
| `suppress_any_exit_family` | 804.76 | 493.76 | -0.00 | 32 | 26/6 | -511.00 | `{'approved_entry': 29, 'rejected_actionable': 3}` | `{'probability_collapse': 7, 'probability_reduce': 23, 'value_over_hold': 16}` | diagnostic_counterfactual_uses_settlement_outcomes, selected_side_live_subset_only, not_frozen_forward_shadow_policy |
| `suppress_value_or_reduce` | 668.76 | 357.76 | -136.00 | 31 | 25/6 | -511.00 | `{'approved_entry': 28, 'rejected_actionable': 3}` | `{'probability_collapse': 6, 'probability_reduce': 23, 'value_over_hold': 16}` | diagnostic_counterfactual_uses_settlement_outcomes, selected_side_live_subset_only, not_frozen_forward_shadow_policy |
| `suppress_probability_collapse` | 590.16 | 279.16 | -214.60 | 7 | 5/2 | -344.84 | `{'approved_entry': 6, 'rejected_actionable': 1}` | `{'probability_collapse': 7, 'probability_reduce': 5, 'value_over_hold': 2}` | diagnostic_counterfactual_uses_settlement_outcomes, selected_side_live_subset_only, not_frozen_forward_shadow_policy |
| `suppress_value_or_reduce_shallow_dd5` | 567.76 | 256.76 | -237.00 | 29 | 23/6 | -511.00 | `{'approved_entry': 26, 'rejected_actionable': 3}` | `{'probability_collapse': 5, 'probability_reduce': 22, 'value_over_hold': 15}` | diagnostic_counterfactual_uses_settlement_outcomes, selected_side_live_subset_only, not_frozen_forward_shadow_policy |
| `suppress_value_over_hold` | 501.60 | 190.60 | -303.16 | 16 | 14/2 | -511.00 | `{'approved_entry': 15, 'rejected_actionable': 1}` | `{'probability_collapse': 2, 'probability_reduce': 8, 'value_over_hold': 16}` | diagnostic_counterfactual_uses_settlement_outcomes, selected_side_live_subset_only, not_frozen_forward_shadow_policy |
| `suppress_probability_reduce` | 368.16 | 57.16 | -436.60 | 23 | 17/6 | -511.00 | `{'approved_entry': 21, 'rejected_actionable': 2}` | `{'probability_collapse': 5, 'probability_reduce': 23, 'value_over_hold': 8}` | diagnostic_counterfactual_uses_settlement_outcomes, selected_side_live_subset_only, not_frozen_forward_shadow_policy |
| `baseline_live` | 311.00 | 0.00 | -493.76 | 0 | 0/0 | -100.00 | `{}` | `{}` | diagnostic_counterfactual_uses_settlement_outcomes, selected_side_live_subset_only, not_frozen_forward_shadow_policy |
| `hold_rejected_actionable_source_oracle` | -94.60 | -405.60 | -899.36 | 5 | 3/2 | -304.00 | `{'rejected_actionable': 5}` | `{'value_over_hold': 1, 'probability_reduce': 2, 'probability_collapse': 1}` | diagnostic_counterfactual_uses_settlement_outcomes, selected_side_live_subset_only, not_frozen_forward_shadow_policy |

## Largest Hold Deltas

| market | source | side | won | live c | hold c | hold delta c | p_hold max | drawdown min | families |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY071000-00 | approved_entry | no | True | -72.00 | 208.00 | 280.00 | 0.92 | -13.04 | probability_collapse, probability_reduce, value_over_hold |
| KXBTC15M-26MAY070030-30 | approved_entry | yes | True | -100.00 | 78.00 | 178.00 | 0.88 | 0.40 | probability_collapse, value_over_hold |
| KXBTC15M-26MAY062315-15 | approved_entry | no | True | -72.00 | 97.00 | 169.00 | 0.79 | 0.70 | probability_reduce |
| KXBTC15M-26MAY071315-15 | approved_entry | yes | True | -8.00 | 143.60 | 151.60 | 0.93 | -15.69 | probability_reduce, value_over_hold |
| KXBTC15M-26MAY070830-30 | approved_entry | no | True | -53.00 | 91.00 | 144.00 | 0.85 | -1.42 | probability_reduce, value_over_hold |
| KXBTC15M-26MAY062215-15 | approved_entry | no | True | 23.00 | 159.00 | 136.00 | 0.72 | 1.23 | probability_collapse |
| KXBTC15M-26MAY062045-45 | approved_entry | no | True | -2.00 | 127.00 | 129.00 | 0.79 | -3.48 | probability_reduce |
| KXBTC15M-26MAY070745-45 | approved_entry | yes | True | -19.00 | 108.00 | 127.00 | 0.79 | 1.15 | probability_reduce |
| KXBTC15M-26MAY071230-30 | approved_entry | yes | True | -22.00 | 100.00 | 122.00 | 0.75 | 1.77 | probability_collapse, probability_reduce |
| KXBTC15M-26MAY070930-30 | approved_entry | yes | True | -40.00 | 68.00 | 108.00 | 0.76 | 3.95 | probability_reduce |
| KXBTC15M-26MAY062100-00 | approved_entry | yes | True | -9.00 | 96.60 | 105.60 | 0.94 | -5.87 | probability_reduce, value_over_hold |
| KXBTC15M-26MAY061800-00 | approved_entry | no | True | 6.00 | 94.00 | 88.00 | 0.82 | -9.04 | probability_reduce, value_over_hold |
| KXBTC15M-26MAY070115-15 | approved_entry | yes | True | 20.00 | 96.20 | 76.20 | 0.88 | -1.98 | value_over_hold |
| KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 46.00 | 116.80 | 70.80 | 0.92 | -7.53 | probability_reduce, value_over_hold |
| KXBTC15M-26MAY062015-15 | approved_entry | no | True | -47.00 | 22.00 | 69.00 | 0.75 | 10.75 | probability_collapse, probability_reduce |
| KXBTC15M-26MAY071045-45 | approved_entry | no | True | 23.00 | 91.00 | 68.00 | 0.79 | -6.33 | probability_reduce |
| KXBTC15M-26MAY070915-15 | approved_entry | no | True | 56.00 | 124.00 | 68.00 | 0.79 | -5.57 | probability_reduce |
| KXBTC15M-26MAY071030-30 | approved_entry | no | True | 37.00 | 104.00 | 67.00 | 0.79 | -1.99 | probability_reduce |
| KXBTC15M-26MAY061815-15 | approved_entry | no | True | 18.00 | 84.00 | 66.00 | 0.75 | 1.99 | probability_reduce |
| KXBTC15M-26MAY062030-30 | approved_entry | no | True | 38.00 | 86.00 | 48.00 | 0.80 | -1.81 | probability_reduce |
