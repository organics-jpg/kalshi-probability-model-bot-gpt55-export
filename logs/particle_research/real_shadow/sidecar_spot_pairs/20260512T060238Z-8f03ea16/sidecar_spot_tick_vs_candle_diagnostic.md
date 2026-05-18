# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:18:37.060535+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `16` / `1`
- Issue count: `0`
- Best model by Brier: `candidate`
- Best model by log loss: `candidate`
- Tick Brownian delta Brier vs candle: `0.005850296710144226`
- Tick Brownian delta log loss vs candle: `0.011706526310746423`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 16 | 1 | 0.15725910308738208 | 0.47531052505992766 | 7 | -139.0 | -4.0 |
| `v28` | 16 | 1 | 0.21211417180661798 | 0.6172210141664565 | 8 | -360.0 | -180.0 |
| `candle_brownian` | 16 | 1 | 0.23607899745641484 | 0.665297823251316 | 8 | -360.0 | -180.0 |
| `tick_brownian` | 16 | 1 | 0.24192929416655906 | 0.6770043495620625 | 8 | -360.0 | -180.0 |
| `market_side_ask` | 16 | 1 | 0.19369999999999998 | 0.5799779594545809 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
