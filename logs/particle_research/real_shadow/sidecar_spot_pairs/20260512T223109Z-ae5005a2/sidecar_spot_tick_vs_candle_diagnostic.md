# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T02:01:43.953207+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.001592933654577966`
- Tick Brownian delta log loss vs candle: `0.00319597487461043`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.36262379750843327 | 1.2997069805382886 | 9 | 132.0 | -93.0 |
| `v28` | 18 | 1 | 0.16923917951695291 | 0.5299861831518937 | 9 | 405.0 | 180.0 |
| `candle_brownian` | 18 | 1 | 0.22187998862672542 | 0.6368450872014577 | 9 | -414.0 | -184.0 |
| `tick_brownian` | 18 | 1 | 0.2234729222813034 | 0.6400410620760681 | 9 | -414.0 | -184.0 |
| `market_side_ask` | 18 | 1 | 0.20705 | 0.6070115700897187 | 9 | 405.0 | 180.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
