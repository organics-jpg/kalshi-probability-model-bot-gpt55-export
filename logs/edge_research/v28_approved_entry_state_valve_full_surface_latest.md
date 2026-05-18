# v28 Approved-Entry State Valve Full-Surface Replay

Research-only adapter replay; no live bot changes or orders.

- Live baseline net: `925.000000c`
- Replayed rows: `4`
- Promotion-ready rows: `0`

## Interpretation

- Best full-surface valve replay is danger_zone_entry_valve / entry_surface with net -349.0c, delta vs base 65.0c, and blockers ['coverage_too_low', 'net_not_positive', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3', 'delta_full_loss_cushion_lt_3', 'does_not_beat_refreshed_live_baseline', 'adapter_replay_not_independently_frozen_candidate', 'live_readiness_not_evaluated'].
- Live baseline used for naive comparison is 925.0c.
- This is an adapter replay, not a new independently frozen candidate; promote nothing from this report.

## Full-Surface Rows

| valve | surface | policy | settled | W/L | coverage | net c | delta vs base | delta vs live | recon share | cushion/delta cushion | skipped | blockers |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `danger_zone_entry_valve` | `entry_surface` | `skip_reentry_gap15_or_gap30` | 86 | 50/36 | 71.311475 | -349.000000 | 65.000000 | -1274.000000 | 0.942529 | 0/0 | 5 | coverage_too_low, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3, delta_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, adapter_replay_not_independently_frozen_candidate, live_readiness_not_evaluated |
| `danger_zone_entry_valve` | `fv_bridge_surface` | `skip_reentry_gap15_or_gap30` | 86 | 50/36 | 71.311475 | -349.000000 | 65.000000 | -1274.000000 | 0.942529 | 0/0 | 5 | coverage_too_low, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3, delta_full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline, adapter_replay_not_independently_frozen_candidate, live_readiness_not_evaluated |
| `approved_entry_state_valve` | `fv_bridge_surface` | `same_side_reentry_gap_lte_15pp` | 65 | 38/27 | 75.200000 | -178.000000 | 0.000000 | -1103.000000 | 0.925532 | 0/0 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3, delta_full_loss_cushion_lt_3, delta_vs_base_not_positive, does_not_beat_refreshed_live_baseline, adapter_replay_not_independently_frozen_candidate, live_readiness_not_evaluated |
| `approved_entry_state_valve` | `entry_surface` | `same_side_reentry_gap_lte_15pp` | 94 | 54/40 | 75.806452 | -329.000000 | 0.000000 | -1254.000000 | 0.925532 | 0/0 | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3, delta_full_loss_cushion_lt_3, delta_vs_base_not_positive, does_not_beat_refreshed_live_baseline, adapter_replay_not_independently_frozen_candidate, live_readiness_not_evaluated |

## Skipped Rows

### danger_zone_entry_valve / entry_surface
- `KXBTC15M-26MAY061745-45` `rejected_actionable` `no` won `False`, net `-30.000000c`, gap `0.370383`, same-side idx `0`
- `KXBTC15M-26MAY061830-30` `rejected_actionable` `yes` won `False`, net `-49.000000c`, gap `0.323162`, same-side idx `0`
- `KXBTC15M-26MAY062100-00` `rejected_actionable` `no` won `False`, net `-47.000000c`, gap `0.395588`, same-side idx `0`
- `KXBTC15M-26MAY062230-30` `rejected_actionable` `yes` won `False`, net `-80.000000c`, gap `0.338015`, same-side idx `0`
- `KXBTC15M-26MAY070615-15` `rejected_actionable` `no` won `True`, net `141.000000c`, gap `0.330872`, same-side idx `0`

### danger_zone_entry_valve / fv_bridge_surface
- `KXBTC15M-26MAY061745-45` `rejected_actionable` `no` won `False`, net `-30.000000c`, gap `0.370383`, same-side idx `0`
- `KXBTC15M-26MAY061830-30` `rejected_actionable` `yes` won `False`, net `-49.000000c`, gap `0.323162`, same-side idx `0`
- `KXBTC15M-26MAY062100-00` `rejected_actionable` `no` won `False`, net `-47.000000c`, gap `0.395588`, same-side idx `0`
- `KXBTC15M-26MAY062230-30` `rejected_actionable` `yes` won `False`, net `-80.000000c`, gap `0.338015`, same-side idx `0`
- `KXBTC15M-26MAY070615-15` `rejected_actionable` `no` won `True`, net `141.000000c`, gap `0.330872`, same-side idx `0`

