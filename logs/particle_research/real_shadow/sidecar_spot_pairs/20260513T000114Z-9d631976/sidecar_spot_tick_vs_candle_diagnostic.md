# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T02:01:55.684159+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `candle_brownian`
- Best model by log loss: `candle_brownian`
- Tick Brownian delta Brier vs candle: `0.006189135781250965`
- Tick Brownian delta log loss vs candle: `0.012447960407792613`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.4684724408887435 | 1.4145786971861305 | 10 | 400.0 | -2.0 |
| `v28` | 18 | 1 | 0.4110995641624435 | 1.024907833902294 | 9 | 603.0 | 268.0 |
| `candle_brownian` | 18 | 1 | 0.2856784668913825 | 0.7646195033484733 | 9 | 603.0 | 268.0 |
| `tick_brownian` | 18 | 1 | 0.29186760267263345 | 0.7770674637562659 | 9 | 603.0 | 268.0 |
| `market_side_ask` | 18 | 1 | 0.45565000000000005 | 1.1240484538549882 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
