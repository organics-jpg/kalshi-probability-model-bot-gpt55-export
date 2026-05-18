# OU Mispricing All-Market-Data Backtest

Generated: 2026-05-14T18:05:40Z

Research-only. No live bot logic, state, processes, or orders were changed.

## Inputs

- Selected unique event tapes: 26
- Duplicate event tapes skipped by exact hash: 0
- Combined market result labels: 2703
- Native spot tick files joined: 53
- Native spot ticks parsed: 477102
- Native watch-market files parsed: 86
- Native ticker files parsed: 86
- Native max prior-spot age: 30.0 seconds
- Execution-event snapshots extracted: 116166
- Native passive snapshots joined from research_data: 51136
- Exact duplicate snapshots skipped: 11718
- Raw snapshots after merge: 155584
- Fair-value snapshots: 155584
- Downsampled snapshots: 39642
- Markets in sampled snapshots: 812

## Variant Results

| Variant | Trades | Net PnL | Win rate | Avg/trade | Markets | Sim decisions |
|---|---:|---:|---:|---:|---:|---:|
| default | 595 | $22.15 | 48.07% | 3.72c | 812 | 645 |
| strict | 552 | $18.38 | 46.56% | 3.33c | 812 | 597 |
| very_strict | 517 | $23.57 | 46.62% | 4.56c | 812 | 554 |

## Shape Of The PnL

| Variant | NO trades / PnL | YES trades / PnL |
|---|---:|---:|
| default | 325 / $20.22 | 270 / $1.93 |
| strict | 294 / $15.09 | 258 / $3.29 |
| very_strict | 276 / $20.29 | 241 / $3.28 |

| Variant | Take-profit | Max-hold | Settlement-after-tape | Stop-loss | Last-bid mark |
|---|---:|---:|---:|---:|---:|
| default | 131 / $37.29 | 220 / -$7.30 | 209 / -$1.37 | 17 / -$5.36 | 18 / -$1.11 |
| strict | 120 / $35.62 | 181 / -$4.52 | 222 / -$7.45 | 14 / -$4.08 | 15 / -$1.19 |
| very_strict | 117 / $35.81 | 163 / -$4.79 | 213 / -$3.05 | 12 / -$3.09 | 12 / -$1.31 |

Very-strict daily PnL was positive on 9 of 14 observed dates. The losing dates were 2026-05-01 (-$0.76), 2026-05-03 (-$0.67), 2026-05-04 (-$0.42), 2026-05-06 (-$0.12), and 2026-05-09 (-$0.09).

## Verdict

The broader backtest is still net positive after the estimated Kalshi-style entry/exit fee model used by the lab. The best broad result is `very_strict`: 517 one-entry-per-market trades, $23.57 net PnL, and 4.56c average net PnL per trade.

This is stronger than the narrower execution-event-only run because it adds native passive market data, but it is not clean enough to treat as deployment-ready. Profit is concentrated in NO-side entries and take-profit exits; held-to-time and stop exits are negative. That means the next test should focus on whether the take-profit behavior survives in forward shadow, and whether max-hold/settlement exits should be filtered or killed earlier.

## Notes

This broad run pools locally recorded execution-event tapes plus native passive research_data ticker shards joined to prior independent BTC spot ticks.
Native passive joins use only spot ticks at or before the Kalshi quote timestamp, capped by native_max_spot_age_seconds.
Each variant still uses one-entry-per-market de-duplication.
Exact duplicate execution_events.ndjson files are skipped by SHA-256, but overlapping non-identical logs may still add richer quote history for the same market.
The result is broader retrospective evidence, not forward proof. A fresh pre-registered shadow is still required before live use.
