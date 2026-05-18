# v28 Live Loss Escape Analysis

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:42:25.725189+00:00`
- Losing control rows: `75`
- Escape class counts: `{'no_exit_repair_observation': 19, 'repair_flips_loss': 17, 'loss_escapes_current_exit_repairs': 37, 'repair_would_worsen': 2}`
- Best repair policy counts: `{'exit_reduce': 17}`

## Interpretation

- This report is diagnostic only; it does not clear live-readiness or change exit logic.
- Among 75 losing control rows, frozen exit repairs flip 17 losses and reduce 0 more in matched row replay.
- 37 losses have a matching exit-repair row but still escape the current repair family; 19 have no matching row in the tracked exit artifacts.
- Best repair policy counts for save/reduce rows: {'exit_reduce': 17}.

## Failure Class x Escape

| failure class | escape counts |
|---|---|
| `exit_policy_cost` | `{'no_exit_repair_observation': 9, 'repair_flips_loss': 17, 'loss_escapes_current_exit_repairs': 27}` |
| `fv_or_entry_timing_error` | `{'no_exit_repair_observation': 10, 'loss_escapes_current_exit_repairs': 10, 'repair_would_worsen': 2}` |

## Largest Escaped Losses

| market | side/result | loss | failure | exit/hold | best policy | best effect | tags |
|---|---|---:|---|---:|---|---|---|
| `KXBTC15M-26MAY062015-15` | yes/no | -134c ($-1.34) | `fv_or_entry_timing_error` | n/a/-134c ($-1.34) | `exit_reduce` | `unchanged` 0c ($0.00) | `full_loss_ge_100c, fv_or_entry_timing_error, near_boundary` |
| `KXBTC15M-26MAY061800-00` | no/no | -86c ($-0.86) | `exit_policy_cost` | 24c ($0.24)/66c ($0.66) | `exit_reduce` | `unchanged` 0c ($0.00) | `large_50_99c, exit_policy_cost, recross_hazard_high, exit_policy_clip_vs_hold` |
| `KXBTC15M-26MAY060900-00` | yes/no | -76c ($-0.76) | `fv_or_entry_timing_error` | 40c ($0.40)/-156c ($-1.56) | `exit_reduce` | `unchanged` 0c ($0.00) | `large_50_99c, fv_or_entry_timing_error, recross_hazard_high, near_boundary` |
| `KXBTC15M-26MAY060745-45` | yes/no | -70c ($-0.70) | `fv_or_entry_timing_error` | 43c ($0.43)/-156c ($-1.56) | `exit_reduce` | `unchanged` 0c ($0.00) | `large_50_99c, fv_or_entry_timing_error, near_boundary` |
| `KXBTC15M-26MAY062015-15` | no/no | -60c ($-0.60) | `exit_policy_cost` | 12c ($0.12)/116c ($1.16) | `exit_reduce` | `unchanged` 0c ($0.00) | `large_50_99c, exit_policy_cost, exit_policy_clip_vs_hold, near_boundary` |
| `KXBTC15M-26MAY060330-30` | yes/yes | -52c ($-0.52) | `exit_policy_cost` | 53c ($0.53)/42c ($0.42) | `exit_reduce` | `unchanged` 0c ($0.00) | `large_50_99c, exit_policy_cost, crowded_depth, exit_policy_clip_vs_hold` |
| `KXBTC15M-26MAY061100-00` | no/no | -40c ($-0.40) | `exit_policy_cost` | 63c ($0.63)/34c ($0.34) | `exit_reduce` | `unchanged` 0c ($0.00) | `medium_25_49c, exit_policy_cost, recross_hazard_high, exit_policy_clip_vs_hold, thin_raw_edge, rich_entry, near_boundary` |
| `KXBTC15M-26MAY071230-30` | yes/yes | -38c ($-0.38) | `exit_policy_cost` | 65c ($0.65)/32c ($0.32) | `exit_reduce` | `unchanged` 0c ($0.00) | `medium_25_49c, exit_policy_cost, exit_policy_clip_vs_hold, thin_raw_edge, rich_entry` |
| `KXBTC15M-26MAY071000-00` | no/no | -36c ($-0.36) | `exit_policy_cost` | 55c ($0.55)/54c ($0.54) | `exit_reduce` | `unchanged` 0c ($0.00) | `medium_25_49c, exit_policy_cost, recross_hazard_high, thin_touch_depth, exit_policy_clip_vs_hold, near_boundary` |
| `KXBTC15M-26MAY062115-15` | no/yes | -34c ($-0.34) | `fv_or_entry_timing_error` | 52c ($0.52)/-138c ($-1.38) | `exit_reduce` | `unchanged` 0c ($0.00) | `medium_25_49c, fv_or_entry_timing_error, near_boundary` |
| `KXBTC15M-26MAY060800-00` | yes/yes | -32c ($-0.32) | `exit_policy_cost` | 50c ($0.50)/68c ($0.68) | `exit_reduce` | `unchanged` 0c ($0.00) | `medium_25_49c, exit_policy_cost, exit_policy_clip_vs_hold, near_boundary` |
| `KXBTC15M-26MAY062130-30` | no/yes | -32c ($-0.32) | `fv_or_entry_timing_error` | 60c ($0.60)/-152c ($-1.52) | `loss_guard_v1` | `unchanged` 0c ($0.00) | `medium_25_49c, fv_or_entry_timing_error, recross_hazard_high, thin_touch_depth, near_boundary` |

## Recent Loss Rows

| market | ts | side/result | loss | escape | best policy | best effect | tags |
|---|---|---|---:|---|---|---|---|
| `KXBTC15M-26MAY070015-15` | `2026-05-07T04:10:20.371309+00:00` | no/yes | -2c ($-0.02) | `loss_escapes_current_exit_repairs` | `exit_reduce` | `unchanged` 0c ($0.00) | `micro_lt_10c, fv_or_entry_timing_error` |
| `KXBTC15M-26MAY070830-30` | `2026-05-07T12:25:30.079423+00:00` | no/no | -14c ($-0.14) | `loss_escapes_current_exit_repairs` | `exit_reduce` | `unchanged` 0c ($0.00) | `small_10_24c, exit_policy_cost, crowded_depth, exit_policy_clip_vs_hold` |
| `KXBTC15M-26MAY071000-00` | `2026-05-07T13:45:58.883423+00:00` | no/no | -36c ($-0.36) | `loss_escapes_current_exit_repairs` | `exit_reduce` | `unchanged` 0c ($0.00) | `medium_25_49c, exit_policy_cost, recross_hazard_high, thin_touch_depth, exit_policy_clip_vs_hold, near_boundary` |
| `KXBTC15M-26MAY071015-15` | `2026-05-07T14:06:01.660553+00:00` | no/yes | -16c ($-0.16) | `loss_escapes_current_exit_repairs` | `loss_guard_v1` | `unchanged` 0c ($0.00) | `small_10_24c, fv_or_entry_timing_error, recross_hazard_high, thin_raw_edge, rich_entry, near_boundary` |
| `KXBTC15M-26MAY071030-30` | `2026-05-07T14:16:08.501513+00:00` | no/no | -24c ($-0.24) | `loss_escapes_current_exit_repairs` | `exit_reduce` | `unchanged` 0c ($0.00) | `small_10_24c, exit_policy_cost, recross_hazard_high, exit_policy_clip_vs_hold, near_boundary` |
| `KXBTC15M-26MAY071045-45` | `2026-05-07T14:31:17.596817+00:00` | no/no | -10c ($-0.10) | `repair_flips_loss` | `exit_reduce` | `loss_to_non_loss` 62c ($0.62) | `small_10_24c, exit_policy_cost, recross_hazard_high, exit_policy_clip_vs_hold, near_boundary` |
| `KXBTC15M-26MAY071215-15` | `2026-05-07T16:07:12.974265+00:00` | no/no | -16c ($-0.16) | `repair_flips_loss` | `exit_reduce` | `loss_to_non_loss` 48c ($0.48) | `small_10_24c, exit_policy_cost, recross_hazard_high, thin_touch_depth, exit_policy_clip_vs_hold, rich_entry` |
| `KXBTC15M-26MAY071215-15` | `2026-05-07T16:08:58.526685+00:00` | no/no | -8c ($-0.08) | `repair_flips_loss` | `exit_reduce` | `loss_to_non_loss` 48c ($0.48) | `micro_lt_10c, exit_policy_cost, crowded_depth, exit_policy_clip_vs_hold, thin_raw_edge, rich_entry, near_boundary` |
| `KXBTC15M-26MAY071230-30` | `2026-05-07T16:23:06.054499+00:00` | yes/yes | -10c ($-0.10) | `loss_escapes_current_exit_repairs` | `exit_reduce` | `unchanged` 0c ($0.00) | `small_10_24c, exit_policy_cost, recross_hazard_high, thin_touch_depth, exit_policy_clip_vs_hold, near_boundary` |
| `KXBTC15M-26MAY071230-30` | `2026-05-07T16:23:59.930534+00:00` | yes/yes | -38c ($-0.38) | `loss_escapes_current_exit_repairs` | `exit_reduce` | `unchanged` 0c ($0.00) | `medium_25_49c, exit_policy_cost, exit_policy_clip_vs_hold, thin_raw_edge, rich_entry` |
| `KXBTC15M-26MAY071315-15` | `2026-05-07T17:06:27.270122+00:00` | yes/yes | -6c ($-0.06) | `repair_flips_loss` | `exit_reduce` | `loss_to_non_loss` 46c ($0.46) | `micro_lt_10c, exit_policy_cost, recross_hazard_high, exit_policy_clip_vs_hold, thin_raw_edge, rich_entry, near_boundary` |
| `KXBTC15M-26MAY071315-15` | `2026-05-07T17:10:51.231869+00:00` | yes/yes | -14c ($-0.14) | `repair_flips_loss` | `exit_reduce` | `loss_to_non_loss` 52c ($0.52) | `small_10_24c, exit_policy_cost, thin_touch_depth, exit_policy_clip_vs_hold, thin_raw_edge, rich_entry, near_boundary` |
