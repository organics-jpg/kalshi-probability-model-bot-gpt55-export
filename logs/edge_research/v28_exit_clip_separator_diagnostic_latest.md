# v28 Exit Clip Separator Diagnostic

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:07:51.611244+00:00`
- Matched unchanged rows: `37`
- Known hold helpful/harmful/unknown: `27/8/0`
- Known hold delta: `1140c`

## Interpretation

- Diagnostic only; this does not create or promote an exit rule.
- Matched-unchanged losses have 27 hold-helpful rows, 8 hold-harmful rows, and 0 unknown-hold rows.
- Best diagnostic separator is fair_drawdown_lte_5.0 AND raw_edge_ge_6.0 with 10 helpful, 0 harmful, 0 unknown, and 732.0c known hold delta.

## Top Diagnostic Separators

| rule | selected | known | helpful | harmful | unknown | delta | precision | failure classes | exit reasons |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| `fair_drawdown_lte_5.0 AND raw_edge_ge_6.0` | 10 | 10 | 10 | 0 | 0 | 732c | 1.000 | `{'exit_policy_cost': 10}` | `{'mushroom_v28_probability_reduce': 7, 'mushroom_v28_probability_collapse_full': 3}` |
| `fair_drawdown_lte_5.0 AND raw_edge_ge_8.0` | 8 | 8 | 8 | 0 | 0 | 624c | 1.000 | `{'exit_policy_cost': 8}` | `{'mushroom_v28_probability_reduce': 5, 'mushroom_v28_probability_collapse_full': 3}` |
| `p_hold_ge_0.60 AND recross_lte_0.20` | 9 | 9 | 9 | 0 | 0 | 590c | 1.000 | `{'exit_policy_cost': 9}` | `{'mushroom_v28_probability_reduce': 4, 'mushroom_v28_probability_collapse_full': 3, 'mushroom_v28_exit_value_over_hold': 2}` |
| `fair_drawdown_lte_10.0 AND recross_lte_0.20` | 7 | 7 | 7 | 0 | 0 | 498c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 4, 'mushroom_v28_probability_collapse_full': 3}` |
| `fair_drawdown_lte_5.0 AND recross_lte_0.35` | 7 | 7 | 7 | 0 | 0 | 496c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 5, 'mushroom_v28_probability_collapse_full': 2}` |
| `fair_drawdown_lte_2.5` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `fair_drawdown_lte_2.5 AND p_hold_ge_0.55` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `fair_drawdown_lte_2.5 AND p_hold_ge_0.60` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `fair_drawdown_lte_2.5 AND p_hold_ge_0.65` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `fair_drawdown_lte_2.5 AND p_hold_ge_0.67` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `fair_drawdown_lte_2.5 AND fair_drawdown_lte_5.0` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `fair_drawdown_lte_2.5 AND fair_drawdown_lte_7.5` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `fair_drawdown_lte_2.5 AND recross_lte_0.65` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `fair_drawdown_lte_2.5 AND recross_lte_0.80` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `fair_drawdown_lte_2.5 AND raw_edge_ge_2.0` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `fair_drawdown_lte_2.5 AND raw_edge_ge_4.0` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `fair_drawdown_lte_2.5 AND raw_edge_ge_6.0` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `fair_drawdown_lte_2.5 AND tag_near_boundary` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `fair_drawdown_lte_10.0 AND fair_drawdown_lte_2.5` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `fair_drawdown_lte_12.5 AND fair_drawdown_lte_2.5` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `fair_drawdown_lte_15.0 AND fair_drawdown_lte_2.5` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `exit_cents_ge_60 AND fair_drawdown_lte_2.5` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `exit_cents_ge_62 AND fair_drawdown_lte_2.5` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `abs_d_ge_0.65 AND fair_drawdown_lte_2.5` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |
| `abs_d_ge_0.75 AND fair_drawdown_lte_2.5` | 7 | 7 | 7 | 0 | 0 | 466c | 1.000 | `{'exit_policy_cost': 7}` | `{'mushroom_v28_probability_reduce': 6, 'mushroom_v28_probability_collapse_full': 1}` |

## Harmful Hold Examples

| market | failure | actual | hold | delta | p_hold | drawdown | exit | abs_d | recross | tags |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY071015-15` | `fv_or_entry_timing_error` | -16c | -162c | -146c | 0.764 | 4.602 | `mushroom_v28_probability_reduce` | 0.949 | 0.381 | `['small_10_24c', 'fv_or_entry_timing_error', 'recross_hazard_high', 'thin_raw_edge', 'rich_entry', 'near_boundary']` |
| `KXBTC15M-26MAY070015-15` | `fv_or_entry_timing_error` | -2c | -140c | -138c | 0.597 | 10.344 | `mushroom_v28_exit_value_over_hold` | 1.544 | 0.074 | `['micro_lt_10c', 'fv_or_entry_timing_error']` |
| `KXBTC15M-26MAY061300-00` | `fv_or_entry_timing_error` | -30c | -160c | -130c | 0.666 | 13.357 | `mushroom_v28_probability_collapse_full` | 0.913 | 0.302 | `['medium_25_49c', 'fv_or_entry_timing_error', 'recross_hazard_high', 'crowded_depth', 'thin_raw_edge', 'rich_entry', 'near_boundary']` |
| `KXBTC15M-26MAY062130-30` | `fv_or_entry_timing_error` | -32c | -152c | -120c | 0.768 | 6.159 | `mushroom_v28_probability_reduce` | 0.999 | 0.304 | `['medium_25_49c', 'fv_or_entry_timing_error', 'recross_hazard_high', 'thin_touch_depth', 'near_boundary']` |
| `KXBTC15M-26MAY060745-45` | `fv_or_entry_timing_error` | -24c | -138c | -114c | 0.610 | 7.965 | `mushroom_v28_probability_collapse_full` | 0.890 | 0.303 | `['small_10_24c', 'fv_or_entry_timing_error', 'recross_hazard_high', 'near_boundary']` |
| `KXBTC15M-26MAY062115-15` | `fv_or_entry_timing_error` | -34c | -138c | -104c | 0.456 | 14.422 | `mushroom_v28_exit_value_over_hold` | 0.898 | 0.247 | `['medium_25_49c', 'fv_or_entry_timing_error', 'near_boundary']` |
| `KXBTC15M-26MAY060745-45` | `fv_or_entry_timing_error` | -70c | -156c | -86c | 0.564 | 21.643 | `mushroom_v28_probability_collapse_full` | 0.863 | 0.173 | `['large_50_99c', 'fv_or_entry_timing_error', 'near_boundary']` |
| `KXBTC15M-26MAY060900-00` | `fv_or_entry_timing_error` | -76c | -156c | -80c | 0.397 | 41.268 | `mushroom_v28_probability_collapse_full` | 0.848 | 0.267 | `['large_50_99c', 'fv_or_entry_timing_error', 'recross_hazard_high', 'near_boundary']` |

## Helpful Hold Examples

| market | failure | actual | hold | delta | p_hold | drawdown | exit | abs_d | recross | tags |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---|
| `KXBTC15M-26MAY062015-15` | `exit_policy_cost` | -60c | 116c | 176c | 0.269 | 15.107 | `mushroom_v28_probability_collapse_full` | 0.916 | 0.094 | `['large_50_99c', 'exit_policy_cost', 'exit_policy_clip_vs_hold', 'near_boundary']` |
| `KXBTC15M-26MAY061800-00` | `exit_policy_cost` | -86c | 66c | 152c | 0.553 | 11.739 | `mushroom_v28_probability_collapse_full` | 1.042 | 0.255 | `['large_50_99c', 'exit_policy_cost', 'recross_hazard_high', 'exit_policy_clip_vs_hold']` |
| `KXBTC15M-26MAY060800-00` | `exit_policy_cost` | -32c | 68c | 100c | 0.615 | 4.530 | `mushroom_v28_probability_collapse_full` | 0.932 | 0.130 | `['medium_25_49c', 'exit_policy_cost', 'exit_policy_clip_vs_hold', 'near_boundary']` |
| `KXBTC15M-26MAY060945-45` | `exit_policy_cost` | -16c | 82c | 98c | 0.557 | 3.344 | `mushroom_v28_probability_collapse_full` | 0.906 | 0.588 | `['small_10_24c', 'exit_policy_cost', 'recross_hazard_high', 'crowded_depth', 'exit_policy_clip_vs_hold', 'near_boundary']` |
| `KXBTC15M-26MAY060330-30` | `exit_policy_cost` | -52c | 42c | 94c | 0.501 | 28.914 | `mushroom_v28_exit_value_over_hold` | 1.072 | 0.148 | `['large_50_99c', 'exit_policy_cost', 'crowded_depth', 'exit_policy_clip_vs_hold']` |
| `KXBTC15M-26MAY071000-00` | `exit_policy_cost` | -36c | 54c | 90c | 0.618 | 11.242 | `mushroom_v28_probability_collapse_full` | 0.929 | 0.483 | `['medium_25_49c', 'exit_policy_cost', 'recross_hazard_high', 'thin_touch_depth', 'exit_policy_clip_vs_hold', 'near_boundary']` |
| `KXBTC15M-26MAY060615-15` | `exit_policy_cost` | -30c | 50c | 80c | 0.643 | 10.652 | `mushroom_v28_probability_collapse_full` | 0.889 | 0.328 | `['medium_25_49c', 'exit_policy_cost', 'recross_hazard_high', 'exit_policy_clip_vs_hold', 'near_boundary']` |
| `KXBTC15M-26MAY060700-00` | `exit_policy_cost` | -30c | 46c | 76c | 0.674 | 9.552 | `mushroom_v28_probability_collapse_full` | 0.887 | 0.151 | `['medium_25_49c', 'exit_policy_cost', 'exit_policy_clip_vs_hold', 'near_boundary']` |
| `KXBTC15M-26MAY060945-45` | `exit_policy_cost` | -16c | 60c | 76c | 0.689 | 1.084 | `mushroom_v28_probability_collapse_full` | 0.847 | 0.333 | `['small_10_24c', 'exit_policy_cost', 'recross_hazard_high', 'crowded_depth', 'exit_policy_clip_vs_hold', 'near_boundary']` |
| `KXBTC15M-26MAY061100-00` | `exit_policy_cost` | -40c | 34c | 74c | 0.704 | 12.587 | `mushroom_v28_probability_collapse_full` | 0.975 | 0.442 | `['medium_25_49c', 'exit_policy_cost', 'recross_hazard_high', 'exit_policy_clip_vs_hold', 'thin_raw_edge', 'rich_entry', 'near_boundary']` |
| `KXBTC15M-26MAY060700-00` | `exit_policy_cost` | -22c | 50c | 72c | 0.749 | 0.142 | `mushroom_v28_probability_reduce` | 0.872 | 0.192 | `['small_10_24c', 'exit_policy_cost', 'exit_policy_clip_vs_hold', 'near_boundary']` |
| `KXBTC15M-26MAY060900-00` | `exit_policy_cost` | -16c | 54c | 70c | 0.721 | 0.890 | `mushroom_v28_probability_reduce` | 0.859 | 0.146 | `['small_10_24c', 'exit_policy_cost', 'exit_policy_clip_vs_hold', 'near_boundary']` |
