# v28 Loss-Churn Observable Full-Denominator Replay

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-07T16:52:21.775411+00:00`
- Promotion use: `diagnostic_full_denominator_replay`
- Scorecard rows: `170`
- Live baseline: `1333c ($13.33)`

## Read

- This is a full-denominator diagnostic replay, not a frozen exit candidate.
- It applies observable loss-frontier guards to all known scorecard rows so winner harm is visible.
- Best clean full-denominator guard is recross_ge_045 with 15 selected rows, 5 loss flips, 574c ($5.74) delta, and blockers ['diagnostic_full_denominator_replay', 'not_frozen_forward', 'selected_decisions_lt_30'].

## Best Clean Replay

- Rule: `recross_ge_045`
- Selected rows / loss flips: `15` / `5`
- Delta / candidate net: `574c ($5.74)` / `1393c ($13.93)`
- Loss count delta: `5`
- Helpful/harmful/new losses: `10` / `0` / `0`
- Blockers: `diagnostic_full_denominator_replay, not_frozen_forward, selected_decisions_lt_30`

## Replays

| rule | selected | flips | loss delta | delta | candidate net | helpful/harmful/new | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `recross_ge_045` | 15 | 5 | 5 | 574c ($5.74) | 1393c ($13.93) | 10/0/0 | 13 | diagnostic_full_denominator_replay, not_frozen_forward, selected_decisions_lt_30 |
| `tag_near_boundary__and__recross_ge_045` | 15 | 5 | 5 | 574c ($5.74) | 1393c ($13.93) | 10/0/0 | 13 | diagnostic_full_denominator_replay, not_frozen_forward, selected_decisions_lt_30 |
| `tag_recross_high__and__recross_ge_045` | 15 | 5 | 5 | 574c ($5.74) | 1393c ($13.93) | 10/0/0 | 13 | diagnostic_full_denominator_replay, not_frozen_forward, selected_decisions_lt_30 |
| `exit_cents_ge_50__and__recross_ge_045` | 10 | 5 | 5 | 574c ($5.74) | 1393c ($13.93) | 10/0/0 | 13 | diagnostic_full_denominator_replay, not_frozen_forward, selected_decisions_lt_30 |
| `recross_ge_030__and__recross_ge_045` | 15 | 5 | 5 | 574c ($5.74) | 1393c ($13.93) | 10/0/0 | 13 | diagnostic_full_denominator_replay, not_frozen_forward, selected_decisions_lt_30 |
| `recross_ge_045__and__absd_ge_085` | 15 | 5 | 5 | 574c ($5.74) | 1393c ($13.93) | 10/0/0 | 13 | diagnostic_full_denominator_replay, not_frozen_forward, selected_decisions_lt_30 |
| `tag_recross_high__and__raw_edge_cents_ge_15` | 5 | 3 | 3 | 376c ($3.76) | 1195c ($11.95) | 4/0/0 | 11 | diagnostic_full_denominator_replay, not_frozen_forward, selected_decisions_lt_30, does_not_beat_refreshed_live_baseline |
| `recross_ge_045__and__depth_lte_384` | 11 | 4 | 4 | 356c ($3.56) | 1175c ($11.75) | 7/0/0 | 11 | diagnostic_full_denominator_replay, not_frozen_forward, selected_decisions_lt_30, does_not_beat_refreshed_live_baseline |
| `raw_edge_cents_ge_15__and__recross_ge_030` | 4 | 2 | 2 | 224c ($2.24) | 1043c ($10.43) | 3/0/0 | 10 | diagnostic_full_denominator_replay, not_frozen_forward, selected_decisions_lt_30, loss_flips_lt_3, does_not_beat_refreshed_live_baseline |
| `p_hold_ge_060__and__recross_ge_045` | 0 | 0 | 0 | 0c ($0.00) | 819c ($8.19) | 0/0/0 | 8 | diagnostic_full_denominator_replay, not_frozen_forward, selected_decisions_lt_30, loss_flips_lt_3, delta_not_positive, does_not_beat_refreshed_live_baseline |
| `tag_crowded_depth__and__p_hold_le_060` | 0 | 0 | 0 | 0c ($0.00) | 819c ($8.19) | 0/0/0 | 8 | diagnostic_full_denominator_replay, not_frozen_forward, selected_decisions_lt_30, loss_flips_lt_3, delta_not_positive, does_not_beat_refreshed_live_baseline |
| `p_hold_ge_060__and__raw_edge_cents_ge_15` | 0 | 0 | 0 | 0c ($0.00) | 819c ($8.19) | 0/0/0 | 8 | diagnostic_full_denominator_replay, not_frozen_forward, selected_decisions_lt_30, loss_flips_lt_3, delta_not_positive, does_not_beat_refreshed_live_baseline |

## Best Selected Examples

| market | side | actual | hold | delta | failure | recross | exit | ask |
|---|---|---:|---:|---:|---|---:|---:|---:|
| `KXBTC15M-26MAY061000-00` | no | 70c ($0.70) | 70c ($0.70) | 0c ($0.00) | `none` | 0.5866639910305327 | None | 65 |
| `KXBTC15M-26MAY061015-15` | no | 54c ($0.54) | 54c ($0.54) | 0c ($0.00) | `none` | 0.5053900102338842 | None | 73 |
| `KXBTC15M-26MAY061130-30` | yes | 40c ($0.40) | 40c ($0.40) | 0c ($0.00) | `none` | 0.5363298971132572 | None | 80 |
| `KXBTC15M-26MAY071030-30` | no | 48c ($0.48) | 48c ($0.48) | 0c ($0.00) | `none` | 0.572086869997676 | None | 76 |
| `KXBTC15M-26MAY071045-45` | no | 50c ($0.50) | 50c ($0.50) | 0c ($0.00) | `none` | 0.4699176077596592 | None | 75 |
| `KXBTC15M-26MAY071145-45` | yes | 44c ($0.44) | 46c ($0.46) | 2c ($0.02) | `none` | 0.5850484031165768 | 99 | 77 |
| `KXBTC15M-26MAY061200-00` | yes | 16c ($0.16) | 36c ($0.36) | 20c ($0.20) | `none` | 0.5526871033269218 | 90 | 82 |
| `KXBTC15M-26MAY071000-00` | no | 16c ($0.16) | 58c ($0.58) | 42c ($0.42) | `exit_policy_cost` | 0.48411120022028664 | 79 | 71 |
| `KXBTC15M-26MAY060915-15` | no | 0c ($0.00) | 60c ($0.60) | 60c ($0.60) | `exit_policy_cost` | 0.5084126970275672 | 70 | 70 |
| `KXBTC15M-26MAY061015-15` | no | 0c ($0.00) | 60c ($0.60) | 60c ($0.60) | `exit_policy_cost` | 0.5588405505167043 | 70 | 70 |
