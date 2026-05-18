# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-18T18:29:03.862249+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `14` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 14 | 1 | 0.2799233572379475 | 1.2547400486487084 | 4 | -9.6 | -7.199999999999999 |
| `v28` | 14 | 1 | 0.0003170884298785291 | 0.01796742884347672 | 0 | 0 | 0.0 |
| `candle_brownian` | 14 | 1 | 0.04937704140662839 | 0.25129801201320673 | 7 | -16.8 | -7.199999999999999 |
| `tick_brownian` | 14 | 1 | 0.04937704140662839 | 0.25129801201320673 | 7 | -16.8 | -7.199999999999999 |
| `market_side_ask` | 14 | 1 | 0.00043250000000000005 | 0.02071942570200755 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
