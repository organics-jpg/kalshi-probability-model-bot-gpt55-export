# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:18:47.563763+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.0365602746740874`
- Tick Brownian delta log loss vs candle: `0.07853491217842484`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.1746480982975757 | 0.8136109966040143 | 9 | 60.0 | -45.0 |
| `v28` | 18 | 1 | 0.008879341826168 | 0.09897015492057236 | 9 | 189.0 | 84.0 |
| `candle_brownian` | 18 | 1 | 0.11862097173056022 | 0.42222571670440295 | 9 | -198.0 | -88.0 |
| `tick_brownian` | 18 | 1 | 0.15518124640464762 | 0.5007606288828278 | 9 | -198.0 | -88.0 |
| `market_side_ask` | 18 | 1 | 0.04624999999999999 | 0.2420918464097847 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
