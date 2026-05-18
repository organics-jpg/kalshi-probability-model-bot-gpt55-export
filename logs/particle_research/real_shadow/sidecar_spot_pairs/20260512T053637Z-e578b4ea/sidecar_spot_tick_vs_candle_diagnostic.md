# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-18T18:28:15.531589+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `16` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 16 | 1 | 0.2606585609944588 | 1.0189479288585943 | 8 | -128.0 | -64.0 |
| `v28` | 16 | 1 | 0.03654296740146035 | 0.21215681402765915 | 8 | -128.0 | -64.0 |
| `candle_brownian` | 16 | 1 | 0.1461990407559778 | 0.4818492427407289 | 8 | -128.0 | -64.0 |
| `tick_brownian` | 16 | 1 | 0.1461990407559778 | 0.4818492427407289 | 8 | -128.0 | -64.0 |
| `market_side_ask` | 16 | 1 | 0.024050000000000002 | 0.16843615832127637 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
