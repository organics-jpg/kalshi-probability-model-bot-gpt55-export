# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-18T18:27:09.389353+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `14` / `1`
- Issue count: `0`
- Best model by Brier: `candle_brownian`
- Best model by log loss: `candle_brownian`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 14 | 1 | 0.459274733096201 | 1.468212827275364 | 7 | 205.0 | -71.0 |
| `v28` | 14 | 1 | 0.3251271322422336 | 0.8444334427512447 | 7 | 483.0 | 207.0 |
| `candle_brownian` | 14 | 1 | 0.27745290570554476 | 0.7481061026747213 | 7 | 483.0 | 207.0 |
| `tick_brownian` | 14 | 1 | 0.27745290570554476 | 0.7481061026747213 | 7 | 483.0 | 207.0 |
| `market_side_ask` | 14 | 1 | 0.4830499999999999 | 1.1875778929144403 | 7 | 483.0 | 207.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
