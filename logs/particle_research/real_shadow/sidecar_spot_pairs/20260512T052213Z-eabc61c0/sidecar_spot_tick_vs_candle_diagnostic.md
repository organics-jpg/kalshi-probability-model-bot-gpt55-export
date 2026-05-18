# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-18T18:27:51.943271+00:00`
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
| `candidate` | 16 | 1 | 0.10222410263026757 | 0.3634944640500199 | 8 | -103.0 | -68.0 |
| `v28` | 16 | 1 | 0.09147264690851363 | 0.36017313060807915 | 8 | -136.0 | -68.0 |
| `candle_brownian` | 16 | 1 | 0.1857231939532916 | 0.5637977638993602 | 8 | -136.0 | -68.0 |
| `tick_brownian` | 16 | 1 | 0.1857231939532916 | 0.5637977638993602 | 8 | -136.0 | -68.0 |
| `market_side_ask` | 16 | 1 | 0.02725000000000001 | 0.18034148266813566 | 8 | -136.0 | -68.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
