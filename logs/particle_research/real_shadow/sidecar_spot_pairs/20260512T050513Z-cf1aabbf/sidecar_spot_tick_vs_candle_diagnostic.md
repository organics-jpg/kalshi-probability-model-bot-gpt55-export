# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-12T05:06:03.781539+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `False`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `0` / `0`
- Issue count: `0`
- Best model by Brier: `candidate`
- Best model by log loss: `candidate`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 0 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| `v28` | 0 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| `candle_brownian` | 0 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| `tick_brownian` | 0 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| `market_side_ask` | 0 | 0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
