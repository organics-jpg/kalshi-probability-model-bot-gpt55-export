# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:48.572901+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `candle_brownian`
- Best model by log loss: `candidate`
- Tick Brownian delta Brier vs candle: `0.005360406944068363`
- Tick Brownian delta log loss vs candle: `0.01081353279046715`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.3069634895978665 | 0.7776733975687484 | 9 | 585.0 | 260.0 |
| `v28` | 18 | 1 | 0.41713627101831513 | 1.038065437122763 | 9 | 585.0 | 260.0 |
| `candle_brownian` | 18 | 1 | 0.2957397591835338 | 0.7848669373744839 | 9 | 585.0 | 260.0 |
| `tick_brownian` | 18 | 1 | 0.30110016612760215 | 0.795680470164951 | 9 | 585.0 | 260.0 |
| `market_side_ask` | 18 | 1 | 0.42904999999999993 | 1.0643158929353038 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
