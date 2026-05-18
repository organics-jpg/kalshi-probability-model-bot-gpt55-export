# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:18:39.642232+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `16` / `1`
- Issue count: `0`
- Best model by Brier: `candidate`
- Best model by log loss: `candidate`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 16 | 1 | 0.2945934548613403 | 0.7630145037914056 | 5 | 58.0 | 122.0 |
| `v28` | 16 | 1 | 0.3983903131676225 | 0.997451113913051 | 0 | 0 | 0.0 |
| `candle_brownian` | 16 | 1 | 0.29605276795884145 | 0.785497832485752 | 8 | 496.0 | 248.0 |
| `tick_brownian` | 16 | 1 | 0.29605276795884145 | 0.785497832485752 | 8 | 496.0 | 248.0 |
| `market_side_ask` | 16 | 1 | 0.397 | 0.9946176368968436 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
