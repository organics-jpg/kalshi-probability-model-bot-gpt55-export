# OU Mispricing Champion Refinement

Generated: 2026-05-14T18:46:22Z

Research-only. No live bot logic, state, processes, or orders were changed.

This pass starts from the best broad sweep candidate: NO-only, small take-profit grid, wider stop grid.

| Rank | Variant | Trades | Net PnL | Win rate | Avg/trade | Positive days |
|---:|---|---:|---:|---:|---:|---:|
| 1 | champion_reentry | 1407 | $393.32 | 93.46% | 27.95c | 13/14 |
| 2 | champion_reentry_ev5_loss40 | 716 | $231.19 | 95.25% | 32.29c | 14/14 |
| 3 | champion_control_1600 | 227 | $33.44 | 74.01% | 14.73c | 12/14 |
| 4 | champion_sharpe_objective | 224 | $33.43 | 74.55% | 14.92c | 12/14 |
| 5 | champion_z10 | 203 | $32.26 | 74.88% | 15.89c | 11/14 |
| 6 | champion_spread2 | 224 | $31.45 | 73.66% | 14.04c | 12/14 |
| 7 | champion_preclose_120 | 227 | $31.30 | 73.13% | 13.79c | 12/14 |
| 8 | champion_preclose_60 | 227 | $31.14 | 73.13% | 13.72c | 12/14 |
| 9 | champion_entry_90_420 | 184 | $30.91 | 77.17% | 16.80c | 10/14 |
| 10 | champion_entry_120_300 | 148 | $30.61 | 82.43% | 20.68c | 12/13 |
| 11 | champion_hold_120 | 192 | $29.94 | 73.96% | 15.59c | 13/14 |
| 12 | champion_ev4_loss44 | 169 | $28.61 | 76.92% | 16.93c | 11/14 |
| 13 | champion_ev5_loss40 | 118 | $27.54 | 83.05% | 23.34c | 14/14 |
| 14 | champion_hold_60 | 125 | $21.58 | 76.00% | 17.26c | 13/14 |

## Best Diagnostics

Best variant: `champion_reentry`.

| Exit reason | Trades | PnL |
|---|---:|---:|
| last_bid_after_tape | 9 | $-0.53 |
| max_hold | 66 | $-1.41 |
| settlement_after_tape | 42 | $4.64 |
| stop_loss | 15 | $-3.71 |
| take_profit | 1275 | $394.33 |

| Segment | Trades | PnL | First entry | Last entry |
|---:|---:|---:|---|---|
| 1 | 469 | $128.35 | 2026-05-01T22:36:28 | 2026-05-07T04:56:07 |
| 2 | 469 | $135.58 | 2026-05-07T04:56:27 | 2026-05-10T16:11:52 |
| 3 | 469 | $129.39 | 2026-05-10T16:11:58 | 2026-05-14T13:11:28 |

## Notes

Repeated-entry variants are diagnostic only. They can improve PnL by using the same market multiple times, but they need stricter fill and inventory accounting before becoming a preferred shadow candidate.
