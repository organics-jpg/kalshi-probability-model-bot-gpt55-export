# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:36.678808+00:00`
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
| `candidate` | 18 | 1 | 0.21990145214373152 | 0.8591917478150172 | 9 | 87.0 | -63.0 |
| `v28` | 18 | 1 | 0.06911019176616609 | 0.3050156662812296 | 9 | 270.0 | 120.0 |
| `candle_brownian` | 18 | 1 | 0.1776685524720661 | 0.5473296558126715 | 9 | -279.0 | -124.0 |
| `tick_brownian` | 18 | 1 | 0.1776685524720661 | 0.5473296558126715 | 9 | -279.0 | -124.0 |
| `market_side_ask` | 18 | 1 | 0.09305000000000001 | 0.36386931266478223 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
