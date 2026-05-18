# Touch Entry + Predictor Exit Backtest

Research-only. No live bot, order logic, thresholds, state, secrets, sizing, or orders are touched.

- Raw book checkpoints loaded: 51488
- Labeled markets available: 188
- Labeled markets with raw checkpoints: 78
- Predictor carrier: `v28s_boundary_monotonic_light_v001`
- Entry: first observed raw book touch on either YES or NO side.
- Visible asks are derived from the opposing bid ladder: YES ask = 100 - best NO bid; NO ask = 100 - best YES bid.
- Exit gates are evaluated only after entry using the selected FV/boundary predictor rows.

## Key Rows
| threshold | cap | window | exit gate | entries | wins | wrong | exits | net c | avg c | max DD c | LCB c |
|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 80 | 95 | 1_to_15_min | hold | 68 | 54 | 14 | 0 | -269.0 | -3.96 | 606.0 | -12.06 |
| 80 | 95 | 1_to_15_min | fair_lt_75 | 68 | 45 | 14 | 13 | -267.0 | -3.93 | 634.0 | -11.07 |
| 80 | 95 | last_5_min | hold | 43 | 38 | 5 | 0 | 8.0 | 0.19 | 247.0 | -7.97 |
| 80 | 95 | last_5_min | fair_lt_75 | 43 | 36 | 5 | 3 | -34.8 | -0.81 | 247.0 | -8.92 |
| 90 | 95 | 1_to_15_min | hold | 60 | 55 | 5 | 0 | 15.0 | 0.25 | 177.0 | -5.64 |
| 90 | 95 | 1_to_15_min | fair_lt_75 | 60 | 52 | 5 | 3 | -18.1 | -0.30 | 177.0 | -6.18 |
| 90 | 95 | 5_to_15_min | hold | 38 | 36 | 2 | 0 | 131.0 | 3.45 | 96.0 | -2.56 |
| 90 | 95 | last_5_min | hold | 43 | 38 | 5 | 0 | -183.0 | -4.26 | 298.0 | -12.27 |

## Top Configurations
| threshold | cap | window | exit gate | entries | wins | wrong | exits | net c | avg c | LCB c |
|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 90 | 95 | 5_to_15_min | hold | 38 | 36 | 2 | 0 | 131.0 | 3.45 | -2.56 |
| 90 | 95 | 5_to_15_min | fair_lt_70 | 38 | 36 | 2 | 0 | 131.0 | 3.45 | -2.56 |
| 90 | 98 | 5_to_15_min | hold | 38 | 36 | 2 | 0 | 131.0 | 3.45 | -2.56 |
| 90 | 98 | 5_to_15_min | fair_lt_70 | 38 | 36 | 2 | 0 | 131.0 | 3.45 | -2.56 |
| 90 | 100 | 5_to_15_min | hold | 38 | 36 | 2 | 0 | 131.0 | 3.45 | -2.56 |
| 90 | 100 | 5_to_15_min | fair_lt_70 | 38 | 36 | 2 | 0 | 131.0 | 3.45 | -2.56 |
| 90 | 95 | 5_to_15_min | fair_lt_75 | 38 | 35 | 2 | 1 | 121.3 | 3.19 | -2.81 |
| 90 | 95 | 5_to_15_min | v28_fair_lt_75 | 38 | 35 | 2 | 1 | 121.3 | 3.19 | -2.81 |
| 90 | 98 | 5_to_15_min | fair_lt_75 | 38 | 35 | 2 | 1 | 121.3 | 3.19 | -2.81 |
| 90 | 98 | 5_to_15_min | v28_fair_lt_75 | 38 | 35 | 2 | 1 | 121.3 | 3.19 | -2.81 |
| 90 | 100 | 5_to_15_min | fair_lt_75 | 38 | 35 | 2 | 1 | 121.3 | 3.19 | -2.81 |
| 90 | 100 | 5_to_15_min | v28_fair_lt_75 | 38 | 35 | 2 | 1 | 121.3 | 3.19 | -2.81 |
| 90 | 95 | 5_to_15_min | fair_lt_80 | 38 | 34 | 2 | 2 | 108.3 | 2.85 | -3.16 |
| 90 | 98 | 5_to_15_min | fair_lt_80 | 38 | 34 | 2 | 2 | 108.3 | 2.85 | -3.16 |
| 90 | 100 | 5_to_15_min | fair_lt_80 | 38 | 34 | 2 | 2 | 108.3 | 2.85 | -3.16 |
| 90 | 95 | 5_to_15_min | bid_lt_entry_minus_10 | 38 | 35 | 2 | 1 | 106.0 | 2.79 | -3.28 |
| 90 | 98 | 5_to_15_min | bid_lt_entry_minus_10 | 38 | 35 | 2 | 1 | 106.0 | 2.79 | -3.28 |
| 90 | 100 | 5_to_15_min | bid_lt_entry_minus_10 | 38 | 35 | 2 | 1 | 106.0 | 2.79 | -3.28 |
| 90 | 95 | 5_to_15_min | fair_lt_75_or_bid_lt_entry_minus_10 | 38 | 34 | 2 | 2 | 96.3 | 2.53 | -3.53 |
| 90 | 98 | 5_to_15_min | fair_lt_75_or_bid_lt_entry_minus_10 | 38 | 34 | 2 | 2 | 96.3 | 2.53 | -3.53 |

## Notes
- This is the correct touch-entry framing, but still only on recorded checkpoints; unobserved exchange touches cannot be recovered.
- Exit gates are approximate because predictor rows are sampled sidecar checkpoints, not continuous tick-by-tick FV updates.
- A strong live-forward candidate should be frozen before using any of these diagnostics as primary evidence.