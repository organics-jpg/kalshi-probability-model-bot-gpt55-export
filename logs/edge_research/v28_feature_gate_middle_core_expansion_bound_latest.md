# v28 Feature-Gate Middle-Core Expansion Bound

Research-only. No live bot logic changes, no orders, no process control.

- Generated UTC: `2026-05-07T12:45:20.948354+00:00`
- Feature-gate parent freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Middle-core watch freeze UTC: `2026-05-07T12:00:53.752707+00:00`
- Live baseline: `1049.000c`

## Interpretation

- Research-only expansion-bound audit; no live bot changes or orders.
- Live baseline for delta math is 1049c.
- diagnostic_feature_window_entry: core has 36 entries vs 48 required for 75%; it needs 12 more entries.
- diagnostic_feature_window_entry: best approved-only expansion adds 2 rows with -142.0c addable PnL; combined coverage 60.317460317460316% and net -10.0c.
- diagnostic_feature_window_entry: even the best reconstructed fill that stays under the 35% source gate reaches 73.01587301587301% coverage and 1003.0c; blockers ['coverage_too_low', 'does_not_beat_refreshed_live_baseline'].
- diagnostic_feature_window_entry: conclusion is source/coverage supply, not core quality; current core W/L is 18/3 with 132.0c.
- diagnostic_feature_window_bridge: core has 36 entries vs 48 required for 75%; it needs 12 more entries.
- diagnostic_feature_window_bridge: best approved-only expansion adds 2 rows with -142.0c addable PnL; combined coverage 60.317460317460316% and net 42.0c.
- diagnostic_feature_window_bridge: even the best reconstructed fill that stays under the 35% source gate reaches 73.01587301587301% coverage and 1055.0c; blockers ['coverage_too_low'].
- diagnostic_feature_window_bridge: conclusion is source/coverage supply, not core quality; current core W/L is 21/2 with 184.0c.
- post_middle_core_freeze_entry: core has 1 entries vs 2 required for 75%; it needs 1 more entries.
- post_middle_core_freeze_entry: best approved-only expansion adds 0 rows with 0c addable PnL; combined coverage 50.0% and net 21.0c.
- post_middle_core_freeze_entry: even the best reconstructed fill that stays under the 35% source gate reaches 50.0% coverage and 21.0c; blockers ['settled_lt_30', 'coverage_too_low', 'full_loss_cushion_lt_3', 'does_not_beat_refreshed_live_baseline'].
- post_middle_core_freeze_entry: conclusion is source/coverage supply, not core quality; current core W/L is 1/0 with 21.0c.
- post_middle_core_freeze_bridge: core has 1 entries vs 2 required for 75%; it needs 1 more entries.
- post_middle_core_freeze_bridge: best approved-only expansion adds 0 rows with 0c addable PnL; combined coverage 50.0% and net 21.0c.
- post_middle_core_freeze_bridge: even the best reconstructed fill that stays under the 35% source gate reaches 50.0% coverage and 21.0c; blockers ['settled_lt_30', 'coverage_too_low', 'full_loss_cushion_lt_3', 'does_not_beat_refreshed_live_baseline'].
- post_middle_core_freeze_bridge: conclusion is source/coverage supply, not core quality; current core W/L is 1/0 with 21.0c.

## diagnostic_feature_window_entry

- Denominator: `63`
- Core entries: `36`
- Required entries for 75%: `48`
- Entries needed to 75%: `12`
- Omitted approved settled market/sides: `2`

### Scenarios

| scenario | entries | settled | W/L | coverage | net c | delta live c | source share | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `abs_floor_core_raw03_recross50_abs075_ask35` | 36 | 21 | 18/3 | 57.143% | 132.000 | -917.000 | 0.167 | 1 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `best_reconstructed_fill_under_35pct_source_gate` | 46 | 31 | 28/3 | 73.016% | 1003.000 | -46.000 | 0.348 | 10 | coverage_too_low, does_not_beat_refreshed_live_baseline |
| `core_plus_any_omitted_approved` | 38 | 23 | 18/5 | 60.317% | -10.000 | -1059.000 | 0.158 | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_approved_raw03_recross70_ask35` | 38 | 23 | 18/5 | 60.317% | -10.000 | -1059.000 | 0.158 | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_approved_raw00_recross70_ask35` | 38 | 23 | 18/5 | 60.317% | -10.000 | -1059.000 | 0.158 | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_approved_raw03_recross90_ask35` | 38 | 23 | 18/5 | 60.317% | -10.000 | -1059.000 | 0.158 | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_approved_abs50_raw03_recross70_ask35` | 38 | 23 | 18/5 | 60.317% | -10.000 | -1059.000 | 0.158 | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |

### Approved Addable Rows

| rule | add rows | add W/L | add net c | combined coverage | combined net c |
|---|---:|---:|---:|---:|---:|
| `any_omitted_approved` | 2 | 0/2 | -142.000 | 60.317% | -10.000 |
| `approved_raw03_recross70_ask35` | 2 | 0/2 | -142.000 | 60.317% | -10.000 |
| `approved_raw00_recross70_ask35` | 2 | 0/2 | -142.000 | 60.317% | -10.000 |
| `approved_raw03_recross90_ask35` | 2 | 0/2 | -142.000 | 60.317% | -10.000 |
| `approved_abs50_raw03_recross70_ask35` | 2 | 0/2 | -142.000 | 60.317% | -10.000 |

### Best Approved Addable Row Detail

| market | side | net | raw edge | recross | abs d | ask | p_side |
|---|---|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY062015-15` | yes | -71.000 | 0.216 | 0.032 | 0.974 | 0.670 | 0.886 |
| `KXBTC15M-26MAY062115-15` | no | -71.000 | 0.171 | 0.247 | 0.898 | 0.690 | 0.861 |

## diagnostic_feature_window_bridge

- Denominator: `63`
- Core entries: `36`
- Required entries for 75%: `48`
- Entries needed to 75%: `12`
- Omitted approved settled market/sides: `2`

### Scenarios

| scenario | entries | settled | W/L | coverage | net c | delta live c | source share | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `abs_floor_core_raw03_recross50_abs075_ask35` | 36 | 23 | 21/2 | 57.143% | 184.000 | -865.000 | 0.167 | 1 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `best_reconstructed_fill_under_35pct_source_gate` | 46 | 33 | 31/2 | 73.016% | 1055.000 | 6.000 | 0.348 | 10 | coverage_too_low |
| `core_plus_any_omitted_approved` | 38 | 25 | 21/4 | 60.317% | 42.000 | -1007.000 | 0.158 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_approved_raw03_recross70_ask35` | 38 | 25 | 21/4 | 60.317% | 42.000 | -1007.000 | 0.158 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_approved_raw00_recross70_ask35` | 38 | 25 | 21/4 | 60.317% | 42.000 | -1007.000 | 0.158 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_approved_raw03_recross90_ask35` | 38 | 25 | 21/4 | 60.317% | 42.000 | -1007.000 | 0.158 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_approved_abs50_raw03_recross70_ask35` | 38 | 25 | 21/4 | 60.317% | 42.000 | -1007.000 | 0.158 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |

### Approved Addable Rows

| rule | add rows | add W/L | add net c | combined coverage | combined net c |
|---|---:|---:|---:|---:|---:|
| `any_omitted_approved` | 2 | 0/2 | -142.000 | 60.317% | 42.000 |
| `approved_raw03_recross70_ask35` | 2 | 0/2 | -142.000 | 60.317% | 42.000 |
| `approved_raw00_recross70_ask35` | 2 | 0/2 | -142.000 | 60.317% | 42.000 |
| `approved_raw03_recross90_ask35` | 2 | 0/2 | -142.000 | 60.317% | 42.000 |
| `approved_abs50_raw03_recross70_ask35` | 2 | 0/2 | -142.000 | 60.317% | 42.000 |

### Best Approved Addable Row Detail

| market | side | net | raw edge | recross | abs d | ask | p_side |
|---|---|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY062015-15` | yes | -71.000 | 0.216 | 0.032 | 0.974 | 0.670 | 0.886 |
| `KXBTC15M-26MAY062115-15` | no | -71.000 | 0.171 | 0.247 | 0.898 | 0.690 | 0.861 |

## post_middle_core_freeze_entry

- Denominator: `2`
- Core entries: `1`
- Required entries for 75%: `2`
- Entries needed to 75%: `1`
- Omitted approved settled market/sides: `0`

### Scenarios

| scenario | entries | settled | W/L | coverage | net c | delta live c | source share | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `abs_floor_core_raw03_recross50_abs075_ask35` | 1 | 1 | 1/0 | 50.000% | 21.000 | -1028.000 | 0.000 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `best_reconstructed_fill_under_35pct_source_gate` | 1 | 1 | 1/0 | 50.000% | 21.000 | -1028.000 | 0.000 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_any_omitted_approved` | 1 | 1 | 1/0 | 50.000% | 21.000 | -1028.000 | 0.000 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_approved_raw03_recross70_ask35` | 1 | 1 | 1/0 | 50.000% | 21.000 | -1028.000 | 0.000 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_approved_raw00_recross70_ask35` | 1 | 1 | 1/0 | 50.000% | 21.000 | -1028.000 | 0.000 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_approved_raw03_recross90_ask35` | 1 | 1 | 1/0 | 50.000% | 21.000 | -1028.000 | 0.000 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_approved_abs50_raw03_recross70_ask35` | 1 | 1 | 1/0 | 50.000% | 21.000 | -1028.000 | 0.000 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |

### Approved Addable Rows

| rule | add rows | add W/L | add net c | combined coverage | combined net c |
|---|---:|---:|---:|---:|---:|
| `any_omitted_approved` | 0 | 0/0 | 0 | 50.000% | 21.000 |
| `approved_raw03_recross70_ask35` | 0 | 0/0 | 0 | 50.000% | 21.000 |
| `approved_raw00_recross70_ask35` | 0 | 0/0 | 0 | 50.000% | 21.000 |
| `approved_raw03_recross90_ask35` | 0 | 0/0 | 0 | 50.000% | 21.000 |
| `approved_abs50_raw03_recross70_ask35` | 0 | 0/0 | 0 | 50.000% | 21.000 |

## post_middle_core_freeze_bridge

- Denominator: `2`
- Core entries: `1`
- Required entries for 75%: `2`
- Entries needed to 75%: `1`
- Omitted approved settled market/sides: `0`

### Scenarios

| scenario | entries | settled | W/L | coverage | net c | delta live c | source share | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `abs_floor_core_raw03_recross50_abs075_ask35` | 1 | 1 | 1/0 | 50.000% | 21.000 | -1028.000 | 0.000 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `best_reconstructed_fill_under_35pct_source_gate` | 1 | 1 | 1/0 | 50.000% | 21.000 | -1028.000 | 0.000 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_any_omitted_approved` | 1 | 1 | 1/0 | 50.000% | 21.000 | -1028.000 | 0.000 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_approved_raw03_recross70_ask35` | 1 | 1 | 1/0 | 50.000% | 21.000 | -1028.000 | 0.000 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_approved_raw00_recross70_ask35` | 1 | 1 | 1/0 | 50.000% | 21.000 | -1028.000 | 0.000 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_approved_raw03_recross90_ask35` | 1 | 1 | 1/0 | 50.000% | 21.000 | -1028.000 | 0.000 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `core_plus_approved_abs50_raw03_recross70_ask35` | 1 | 1 | 1/0 | 50.000% | 21.000 | -1028.000 | 0.000 | 0 | settled_lt_30, coverage_too_low, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |

### Approved Addable Rows

| rule | add rows | add W/L | add net c | combined coverage | combined net c |
|---|---:|---:|---:|---:|---:|
| `any_omitted_approved` | 0 | 0/0 | 0 | 50.000% | 21.000 |
| `approved_raw03_recross70_ask35` | 0 | 0/0 | 0 | 50.000% | 21.000 |
| `approved_raw00_recross70_ask35` | 0 | 0/0 | 0 | 50.000% | 21.000 |
| `approved_raw03_recross90_ask35` | 0 | 0/0 | 0 | 50.000% | 21.000 |
| `approved_abs50_raw03_recross70_ask35` | 0 | 0/0 | 0 | 50.000% | 21.000 |
