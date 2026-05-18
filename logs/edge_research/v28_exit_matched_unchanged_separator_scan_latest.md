# v28 Exit Matched-Unchanged Separator Scan

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T12:12:23.159295+00:00`
- Matched unchanged rows: `26`
- Hold helpful/harmful/unknown: `17/7/0`
- Total actual loss: `-890.000000c`
- Total hold net: `-324.000000c`
- Total hold delta: `566.000000c`

## Interpretation

- Research-only separator scan; no live bot logic changes or orders.
- Matched-but-unchanged loss rows split into 17 hold-helpful and 7 hold-harmful rows, so broad hold suppression remains unsafe.
- Clean separator rows here are diagnostic failure-mode evidence only. A deployable exit rule would need its own frozen forward watch, row count, suppression density, path-risk review, and live-readiness gate.
- Best robust zero-harm diagnostic separator is `exit_cents_gte_70` with 6 selected rows and 340.0c hold delta.

## Top Robust Zero-Harm Rules

| rule | rows | hold delta c | helpful/harmful | actual loss c | hold net c | failure classes | exit reasons |
|---|---:|---:|---:|---:|---:|---|---|
| `exit_cents_gte_70` | 6 | 340.000000 | 6/0 | -90.000000 | 250.000000 | `{'exit_policy_cost': 6}` | `{'mushroom_v28_probability_reduce': 2, 'mushroom_v28_exit_value_over_hold': 4}` |
| `fair_drawdown_cents_lte_5` | 5 | 362.000000 | 5/0 | -102.000000 | 260.000000 | `{'exit_policy_cost': 5}` | `{'mushroom_v28_probability_reduce': 2, 'mushroom_v28_exit_value_over_hold': 2, 'mushroom_v28_probability_collapse_full': 1}` |
| `fair_drawdown_cents_lte_5 AND fair_drawdown_cents_lte_10` | 5 | 362.000000 | 5/0 | -102.000000 | 260.000000 | `{'exit_policy_cost': 5}` | `{'mushroom_v28_probability_reduce': 2, 'mushroom_v28_exit_value_over_hold': 2, 'mushroom_v28_probability_collapse_full': 1}` |

## Top Clean Zero-Harm Rules

| rule | rows | hold delta c | helpful/harmful | top tags |
|---|---:|---:|---:|---|
| `exit_cents_gte_70` | 6 | 340.000000 | 6/0 | `{'exit_policy_cost': 6, 'exit_policy_clip_vs_hold': 6, 'near_boundary': 4, 'small_10_24c': 3, 'micro_lt_10c': 2, 'rich_entry': 2}` |
| `fair_drawdown_cents_lte_5` | 5 | 362.000000 | 5/0 | `{'exit_policy_cost': 5, 'exit_policy_clip_vs_hold': 5, 'near_boundary': 5, 'medium_25_49c': 2, 'small_10_24c': 2, 'micro_lt_10c': 1}` |
| `fair_drawdown_cents_lte_5 AND fair_drawdown_cents_lte_10` | 5 | 362.000000 | 5/0 | `{'exit_policy_cost': 5, 'exit_policy_clip_vs_hold': 5, 'near_boundary': 5, 'medium_25_49c': 2, 'small_10_24c': 2, 'micro_lt_10c': 1}` |
| `p_hold_gte_0.7 AND fair_drawdown_cents_lte_5` | 4 | 262.000000 | 4/0 | `{'exit_policy_cost': 4, 'exit_policy_clip_vs_hold': 4, 'near_boundary': 4, 'small_10_24c': 2, 'micro_lt_10c': 1, 'medium_25_49c': 1}` |
| `p_hold_gte_0.7 AND exit_cents_gte_70` | 4 | 250.000000 | 4/0 | `{'exit_policy_cost': 4, 'exit_policy_clip_vs_hold': 4, 'near_boundary': 4, 'small_10_24c': 2, 'micro_lt_10c': 1, 'medium_25_49c': 1}` |
| `exit_cents_gte_70 AND fair_drawdown_cents_lte_10` | 4 | 250.000000 | 4/0 | `{'exit_policy_cost': 4, 'exit_policy_clip_vs_hold': 4, 'near_boundary': 4, 'small_10_24c': 2, 'micro_lt_10c': 1, 'medium_25_49c': 1}` |
| `exit_reason_eq_blank` | 4 | 114.000000 | 2/0 | `{'small_10_24c': 3, 'near_boundary': 3, 'fv_or_entry_timing_error': 2, 'exit_policy_cost': 2, 'recross_hazard_high': 2, 'exit_policy_clip_vs_hold': 2}` |
| `abs_d_sigma_gte_1 AND eligible_depth_gte_1000` | 3 | 198.000000 | 3/0 | `{'exit_policy_cost': 3, 'exit_policy_clip_vs_hold': 3, 'large_50_99c': 1, 'crowded_depth': 1, 'micro_lt_10c': 1, 'rich_entry': 1}` |
| `eligible_depth_gte_1000 AND p_side_gte_0.9` | 3 | 198.000000 | 3/0 | `{'exit_policy_cost': 3, 'exit_policy_clip_vs_hold': 3, 'large_50_99c': 1, 'crowded_depth': 1, 'micro_lt_10c': 1, 'rich_entry': 1}` |
| `exit_cents_gte_70 AND fair_drawdown_cents_lte_5` | 3 | 190.000000 | 3/0 | `{'exit_policy_cost': 3, 'exit_policy_clip_vs_hold': 3, 'near_boundary': 3, 'micro_lt_10c': 1, 'medium_25_49c': 1, 'recross_hazard_high': 1}` |
| `exit_cents_gte_80` | 3 | 176.000000 | 3/0 | `{'exit_policy_cost': 3, 'exit_policy_clip_vs_hold': 3, 'near_boundary': 2, 'medium_25_49c': 1, 'recross_hazard_high': 1, 'small_10_24c': 1}` |
| `exit_cents_gte_70 AND exit_cents_gte_80` | 3 | 176.000000 | 3/0 | `{'exit_policy_cost': 3, 'exit_policy_clip_vs_hold': 3, 'near_boundary': 2, 'medium_25_49c': 1, 'recross_hazard_high': 1, 'small_10_24c': 1}` |

## Highest-Risk Matched Rules

| rule | rows | hold delta c | helpful/harmful | harmful delta c | top tags |
|---|---:|---:|---:|---:|---|
| `p_hold_lte_0.79` | 21 | 382.000000 | 14/7 | -772.000000 | `{'near_boundary': 15, 'exit_policy_cost': 14, 'exit_policy_clip_vs_hold': 14, 'medium_25_49c': 8, 'recross_hazard_high': 7, 'fv_or_entry_timing_error': 7}` |
| `p_hold_lte_0.85` | 21 | 382.000000 | 14/7 | -772.000000 | `{'near_boundary': 15, 'exit_policy_cost': 14, 'exit_policy_clip_vs_hold': 14, 'medium_25_49c': 8, 'recross_hazard_high': 7, 'fv_or_entry_timing_error': 7}` |
| `exit_cents_gte_30` | 20 | 124.000000 | 13/7 | -772.000000 | `{'near_boundary': 15, 'exit_policy_cost': 13, 'exit_policy_clip_vs_hold': 13, 'medium_25_49c': 8, 'fv_or_entry_timing_error': 7, 'recross_hazard_high': 6}` |
| `exit_cents_gte_40` | 20 | 124.000000 | 13/7 | -772.000000 | `{'near_boundary': 15, 'exit_policy_cost': 13, 'exit_policy_clip_vs_hold': 13, 'medium_25_49c': 8, 'fv_or_entry_timing_error': 7, 'recross_hazard_high': 6}` |
| `exit_cents_lte_70` | 17 | 172.000000 | 10/7 | -772.000000 | `{'near_boundary': 13, 'exit_policy_cost': 10, 'exit_policy_clip_vs_hold': 10, 'medium_25_49c': 7, 'fv_or_entry_timing_error': 7, 'recross_hazard_high': 6}` |
| `exit_cents_lte_80` | 19 | 276.000000 | 12/7 | -772.000000 | `{'near_boundary': 14, 'exit_policy_cost': 12, 'exit_policy_clip_vs_hold': 12, 'medium_25_49c': 7, 'fv_or_entry_timing_error': 7, 'recross_hazard_high': 6}` |
| `exit_cents_lte_90` | 20 | 314.000000 | 13/7 | -772.000000 | `{'near_boundary': 14, 'exit_policy_cost': 13, 'exit_policy_clip_vs_hold': 13, 'medium_25_49c': 7, 'fv_or_entry_timing_error': 7, 'recross_hazard_high': 6}` |
| `fair_drawdown_cents_gte_-10` | 21 | 382.000000 | 14/7 | -772.000000 | `{'near_boundary': 15, 'exit_policy_cost': 14, 'exit_policy_clip_vs_hold': 14, 'medium_25_49c': 8, 'recross_hazard_high': 7, 'fv_or_entry_timing_error': 7}` |
| `fair_drawdown_cents_gte_-5` | 21 | 382.000000 | 14/7 | -772.000000 | `{'near_boundary': 15, 'exit_policy_cost': 14, 'exit_policy_clip_vs_hold': 14, 'medium_25_49c': 8, 'recross_hazard_high': 7, 'fv_or_entry_timing_error': 7}` |
| `fair_drawdown_cents_gte_0` | 20 | 314.000000 | 13/7 | -772.000000 | `{'near_boundary': 14, 'exit_policy_cost': 13, 'exit_policy_clip_vs_hold': 13, 'medium_25_49c': 7, 'fv_or_entry_timing_error': 7, 'recross_hazard_high': 6}` |
| `fair_drawdown_cents_gte_5` | 17 | 90.000000 | 10/7 | -772.000000 | `{'near_boundary': 11, 'exit_policy_cost': 10, 'exit_policy_clip_vs_hold': 10, 'fv_or_entry_timing_error': 7, 'medium_25_49c': 6, 'recross_hazard_high': 6}` |
| `ask_cents_gte_35` | 25 | 566.000000 | 17/7 | -772.000000 | `{'near_boundary': 19, 'exit_policy_cost': 17, 'exit_policy_clip_vs_hold': 17, 'recross_hazard_high': 9, 'medium_25_49c': 8, 'small_10_24c': 8}` |

## Blockers

- `diagnostic_loss_rows_only`
- `needs_own_frozen_forward_watch`
- `needs_path_risk_review`
- `not_live_bot_logic`
