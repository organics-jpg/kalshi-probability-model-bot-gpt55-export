# OU Mispricing Refinement Sweep

Generated: 2026-05-14T18:25:58Z

Research-only. No live bot logic, state, processes, or orders were changed.

## Data

- Markets: 812
- Downsampled snapshots: 39642
- Execution-event snapshots: 116166
- Native passive snapshots: 51136

## Results

| Rank | Variant | Trades | Net PnL | Win rate | Avg/trade | Positive days | Sim decisions |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | no_only_small_tp_grid | 224 | $31.46 | 74.11% | 14.04c | 11/14 | 1243 |
| 2 | no_only_fast_hold | 224 | $29.40 | 67.86% | 13.12c | 11/14 | 1320 |
| 3 | no_only_lossprob_40 | 309 | $28.02 | 52.75% | 9.07c | 13/14 | 354 |
| 4 | no_only_early_window | 186 | $27.79 | 67.74% | 14.94c | 12/14 | 255 |
| 5 | no_only_fast_hold_tight_gate | 199 | $27.76 | 68.84% | 13.95c | 11/14 | 1616 |
| 6 | no_only | 310 | $27.57 | 52.58% | 8.89c | 13/14 | 349 |
| 7 | no_only_sharpe_objective | 301 | $26.80 | 55.48% | 8.90c | 13/14 | 448 |
| 8 | no_only_mid_window | 244 | $23.27 | 60.25% | 9.54c | 10/14 | 315 |
| 9 | no_only_preclose_90 | 310 | $23.22 | 52.58% | 7.49c | 13/14 | 349 |
| 10 | control_very_strict_1200 | 517 | $22.40 | 46.23% | 4.33c | 9/14 | 554 |
| 11 | both_sides_preclose_90 | 517 | $21.58 | 47.78% | 4.17c | 12/14 | 554 |
| 12 | both_sides_sharpe_objective | 500 | $21.54 | 48.80% | 4.31c | 10/14 | 686 |
| 13 | yes_only | 279 | $5.92 | 43.01% | 2.12c | 7/14 | 279 |

## Best Variant Diagnostics

Best by net PnL: `no_only_small_tp_grid`.

| Side | Trades | PnL |
|---|---:|---:|
| no | 224 | $31.46 |

| Exit reason | Trades | PnL |
|---|---:|---:|
| last_bid_after_tape | 4 | $-0.40 |
| max_hold | 53 | $-1.34 |
| settlement_after_tape | 20 | $3.36 |
| stop_loss | 8 | $-2.12 |
| take_profit | 139 | $31.96 |

| Segment | Trades | PnL | First entry | Last entry |
|---:|---:|---:|---|---|
| 1 | 75 | $10.74 | 2026-05-01T22:36:28 | 2026-05-07T01:40:17 |
| 2 | 75 | $15.91 | 2026-05-07T02:35:18 | 2026-05-11T06:56:00 |
| 3 | 74 | $4.81 | 2026-05-11T07:23:26 | 2026-05-14T13:05:10 |

## Interpretation

This sweep is still retrospective. Treat it as a filter for the next shadow candidate, not as deployment proof.
A refinement only matters if it improves broad PnL without collapsing sample size and without relying on a single late segment.
