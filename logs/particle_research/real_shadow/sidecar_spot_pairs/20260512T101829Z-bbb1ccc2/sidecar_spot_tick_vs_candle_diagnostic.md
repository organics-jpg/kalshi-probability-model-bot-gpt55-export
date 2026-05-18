# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:28.254621+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.0012077432008262834`
- Tick Brownian delta log loss vs candle: `0.0024344035432714017`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.2852912632495559 | 0.9846571162465292 | 9 | 114.0 | -81.0 |
| `v28` | 18 | 1 | 0.13285186495560292 | 0.45332508890981527 | 9 | 351.0 | 156.0 |
| `candle_brownian` | 18 | 1 | 0.20726459259178648 | 0.6074525595675125 | 9 | -360.0 | -160.0 |
| `tick_brownian` | 18 | 1 | 0.20847233579261276 | 0.6098869631107839 | 9 | -360.0 | -160.0 |
| `market_side_ask` | 18 | 1 | 0.15605000000000002 | 0.5025609727903855 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
