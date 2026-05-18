# v28 Dual-Lane State/Exposure Sequence Repair

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-07T16:50:58.097269+00:00`
- Promotion use: `diagnostic_same_window_only`
- Freeze UTC: `2026-05-07T13:00:17.363339+00:00`
- Candidate policy: `post_dual_union_birth_bridge_cheap_penalty025_rank_only`
- Live baseline: `1333c ($13.33)`

## Read

- This is diagnostic same-window exposure research, not a frozen candidate and not live-test approval.
- The probe tests observable exposure weights suggested by the sequence mechanism audit, without changing live bot logic.
- Best diagnostic variant is sequence_combo_strong2x_shrink50 with 192c ($1.93) candidate net and -132c ($-1.31) vs live on the same markets.
- Even the best diagnostic exposure rule still trails live on the same markets.

## Best Variant

- Variant: `sequence_combo_strong2x_shrink50`
- Entries/coverage: `13` / `86.67%`
- Adjusted candidate net: `192c ($1.93)`
- Same-window candidate-live: `-132c ($-1.31)`
- Delta vs baseline candidate: `174c ($1.75)`
- Full-loss cushion: `1`
- Weights changed / amplified losers / shrunk winners: `9` / `0` / `5`
- Blockers: `diagnostic_only_same_window, not_frozen_forward, state_sequence_not_live_ready, still_trails_live_same_window, full_loss_cushion_lt_3, shrinks_winning_rows, does_not_beat_refreshed_live_baseline`

## Variants

| variant | net | candidate-live | delta vs baseline | cushion | changed | amp losers | shrunk winners | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `sequence_combo_strong2x_shrink50` | 192c ($1.93) | -132c ($-1.31) | 174c ($1.75) | 1 | 9 | 0 | 5 | diagnostic_only_same_window, not_frozen_forward, state_sequence_not_live_ready, still_trails_live_same_window, full_loss_cushion_lt_3, shrinks_winning_rows, does_not_beat_refreshed_live_baseline |
| `sequence_combo_mid1p5_shrink50` | 170c ($1.71) | -154c ($-1.53) | 152c ($1.52) | 1 | 11 | 0 | 5 | diagnostic_only_same_window, not_frozen_forward, state_sequence_not_live_ready, still_trails_live_same_window, full_loss_cushion_lt_3, shrinks_winning_rows, does_not_beat_refreshed_live_baseline |
| `shrink_high_cost_low_edge_50` | 106c ($1.06) | -218c ($-2.17) | 88c ($0.89) | 1 | 7 | 0 | 5 | diagnostic_only_same_window, not_frozen_forward, state_sequence_not_live_ready, still_trails_live_same_window, full_loss_cushion_lt_3, shrinks_winning_rows, does_not_beat_refreshed_live_baseline |
| `scale_strong_same_side_2x` | 104c ($1.04) | -220c ($-2.20) | 86c ($0.86) | 1 | 2 | 0 | 0 | diagnostic_only_same_window, not_frozen_forward, state_sequence_not_live_ready, still_trails_live_same_window, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `scale_mid_confidence_1p5x` | 82c ($0.82) | -242c ($-2.42) | 64c ($0.64) | 0 | 4 | 0 | 0 | diagnostic_only_same_window, not_frozen_forward, state_sequence_not_live_ready, still_trails_live_same_window, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |
| `continuous_edge_cost_weight` | 49c ($0.49) | -275c ($-2.75) | 31c ($0.31) | 0 | 9 | 0 | 4 | diagnostic_only_same_window, not_frozen_forward, state_sequence_not_live_ready, still_trails_live_same_window, full_loss_cushion_lt_3, shrinks_winning_rows, does_not_beat_refreshed_live_baseline |
| `baseline` | 18c ($0.18) | -306c ($-3.06) | 0c ($0.00) | 0 | 0 | 0 | 0 | diagnostic_only_same_window, not_frozen_forward, state_sequence_not_live_ready, still_trails_live_same_window, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |

## Best Weighted Rows

| market | side | net | live | adjusted | adjusted-live | weight | reason |
|---|---|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY070945-45` | no | 28c ($0.28) | 300c ($3.00) | 56c ($0.56) | -244c ($-2.44) | 2.000 | strong_same_side_scale |
| `KXBTC15M-26MAY071145-45` | yes | 46c ($0.46) | 228c ($2.28) | 23c ($0.23) | -205c ($-2.05) | 0.500 | high_cost_low_edge_shrink |
| `KXBTC15M-26MAY071100-00` | yes | -166c ($-1.66) | 40c ($0.40) | -83c ($-0.83) | -123c ($-1.23) | 0.500 | high_cost_low_edge_shrink |
| `KXBTC15M-26MAY071015-15` | no | -162c ($-1.62) | 28c ($0.28) | -81c ($-0.81) | -109c ($-1.09) | 0.500 | high_cost_low_edge_shrink |
| `KXBTC15M-26MAY071130-30` | no | 13c ($0.13) | 88c ($0.88) | 6c ($0.07) | -82c ($-0.81) | 0.500 | high_cost_low_edge_shrink |
| `KXBTC15M-26MAY071115-15` | yes | 32c ($0.32) | 0c ($0.00) | 16c ($0.16) | 16c ($0.16) | 0.500 | high_cost_low_edge_shrink |
| `KXBTC15M-26MAY070915-15` | no | 20c ($0.20) | -14c ($-0.14) | 20c ($0.20) | 34c ($0.34) | 1.000 |  |
| `KXBTC15M-26MAY071200-00` | no | 46c ($0.46) | 0c ($0.00) | 46c ($0.46) | 46c ($0.46) | 1.000 |  |
