# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:20.337934+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.00783759337973925 | 0.06289943221939459 | 9 | 63.09999999999995 | 17.599999999999984 |
| `v28` | 18 | 1 | 0.0018737652607123097 | 0.04425183877965417 | 9 | 81.89999999999995 | 36.39999999999998 |
| `candle_brownian` | 18 | 1 | 0.09102804218054054 | 0.3591186967023174 | 9 | -87.3 | -38.8 |
| `tick_brownian` | 18 | 1 | 0.09102804218054054 | 0.3591186967023174 | 9 | -87.3 | -38.8 |
| `market_side_ask` | 18 | 1 | 0.008844999999999995 | 0.0987214551849049 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
