# v28 Frozen Exit Clip Separator Watch

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:07:51.793958+00:00`
- Freeze UTC: `2026-05-07T04:04:23.876080+00:00`
- Candidate: `fair_drawdown_lte10_p_hold_ge060_exit_clip_separator`
- Rule: `For matched unchanged loss rows, flag rows with fair_drawdown_cents <= 10 and p_hold >= 0.60.`
- Post-freeze matched unchanged rows: `7`
- Selected rows: `3`
- Known helpful/harmful/unknown: `2/1/0`
- Known hold delta: `-20c`
- Blockers: `post_freeze_rows_lt_30, harmful_hold_rows_present, known_hold_delta_lt_300c`

## Interpretation

- Forward watch only; not a full exit-PnL simulator and not promotion evidence by itself.
- Post-freeze matched-unchanged rows: 7; selected rows: 3; known helpful/harmful/unknown: 2/1/0.
- Blockers: ['post_freeze_rows_lt_30', 'harmful_hold_rows_present', 'known_hold_delta_lt_300c'].

## Post-Freeze Denominator Examples

| market | failure | selected | fail reasons | actual | hold | delta | p_hold | drawdown | exit | tags |
|---|---|---:|---|---:|---:|---:|---:|---:|---|---|
| `KXBTC15M-26MAY070015-15` | `fv_or_entry_timing_error` | False | `p_hold_below_floor, fair_drawdown_above_ceiling` | -2c | -140c | -138c | 0.597 | 10.344 | `mushroom_v28_exit_value_over_hold` | `['micro_lt_10c', 'fv_or_entry_timing_error']` |
| `KXBTC15M-26MAY070830-30` | `exit_policy_cost` | False | `fair_drawdown_above_ceiling` | -14c | 46c | 60c | 0.613 | 15.700 | `mushroom_v28_exit_value_over_hold` | `['small_10_24c', 'exit_policy_cost', 'crowded_depth', 'exit_policy_clip_vs_hold']` |
| `KXBTC15M-26MAY071000-00` | `exit_policy_cost` | False | `fair_drawdown_above_ceiling` | -36c | 54c | 90c | 0.618 | 11.242 | `mushroom_v28_probability_collapse_full` | `['medium_25_49c', 'exit_policy_cost', 'recross_hazard_high', 'thin_touch_depth', 'exit_policy_clip_vs_hold', 'near_boundary']` |
| `KXBTC15M-26MAY071015-15` | `fv_or_entry_timing_error` | True | `none` | -16c | -162c | -146c | 0.764 | 4.602 | `mushroom_v28_probability_reduce` | `['small_10_24c', 'fv_or_entry_timing_error', 'recross_hazard_high', 'thin_raw_edge', 'rich_entry', 'near_boundary']` |
| `KXBTC15M-26MAY071030-30` | `exit_policy_cost` | True | `none` | -24c | 46c | 70c | 0.710 | 6.017 | `mushroom_v28_probability_collapse_full` | `['small_10_24c', 'exit_policy_cost', 'recross_hazard_high', 'exit_policy_clip_vs_hold', 'near_boundary']` |
| `KXBTC15M-26MAY071230-30` | `exit_policy_cost` | True | `none` | -10c | 46c | 56c | 0.749 | 2.062 | `mushroom_v28_probability_reduce` | `['small_10_24c', 'exit_policy_cost', 'recross_hazard_high', 'thin_touch_depth', 'exit_policy_clip_vs_hold', 'near_boundary']` |
| `KXBTC15M-26MAY071230-30` | `exit_policy_cost` | False | `fair_drawdown_above_ceiling` | -38c | 32c | 70c | 0.663 | 17.710 | `mushroom_v28_probability_collapse_full` | `['medium_25_49c', 'exit_policy_cost', 'exit_policy_clip_vs_hold', 'thin_raw_edge', 'rich_entry']` |

## Selected Examples

| market | failure | actual | hold | delta | p_hold | drawdown | exit | tags |
|---|---|---:|---:|---:|---:|---:|---|---|
| `KXBTC15M-26MAY071015-15` | `fv_or_entry_timing_error` | -16c | -162c | -146c | 0.764 | 4.602 | `mushroom_v28_probability_reduce` | `['small_10_24c', 'fv_or_entry_timing_error', 'recross_hazard_high', 'thin_raw_edge', 'rich_entry', 'near_boundary']` |
| `KXBTC15M-26MAY071030-30` | `exit_policy_cost` | -24c | 46c | 70c | 0.710 | 6.017 | `mushroom_v28_probability_collapse_full` | `['small_10_24c', 'exit_policy_cost', 'recross_hazard_high', 'exit_policy_clip_vs_hold', 'near_boundary']` |
| `KXBTC15M-26MAY071230-30` | `exit_policy_cost` | -10c | 46c | 56c | 0.749 | 2.062 | `mushroom_v28_probability_reduce` | `['small_10_24c', 'exit_policy_cost', 'recross_hazard_high', 'thin_touch_depth', 'exit_policy_clip_vs_hold', 'near_boundary']` |

## Missed Known Helpful Examples

| market | failure | actual | hold | delta | p_hold | drawdown | exit | tags |
|---|---|---:|---:|---:|---:|---:|---|---|
| `KXBTC15M-26MAY070830-30` | `exit_policy_cost` | -14c | 46c | 60c | 0.613 | 15.700 | `mushroom_v28_exit_value_over_hold` | `['small_10_24c', 'exit_policy_cost', 'crowded_depth', 'exit_policy_clip_vs_hold']` |
| `KXBTC15M-26MAY071000-00` | `exit_policy_cost` | -36c | 54c | 90c | 0.618 | 11.242 | `mushroom_v28_probability_collapse_full` | `['medium_25_49c', 'exit_policy_cost', 'recross_hazard_high', 'thin_touch_depth', 'exit_policy_clip_vs_hold', 'near_boundary']` |
| `KXBTC15M-26MAY071230-30` | `exit_policy_cost` | -38c | 32c | 70c | 0.663 | 17.710 | `mushroom_v28_probability_collapse_full` | `['medium_25_49c', 'exit_policy_cost', 'exit_policy_clip_vs_hold', 'thin_raw_edge', 'rich_entry']` |
