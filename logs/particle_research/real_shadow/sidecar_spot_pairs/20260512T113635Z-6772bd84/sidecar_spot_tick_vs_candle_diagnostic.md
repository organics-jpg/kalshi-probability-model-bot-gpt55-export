# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:43.056525+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `1.7608960995979528e-05`
- Tick Brownian delta log loss vs candle: `3.539904130678284e-05`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.12058589281654794 | 0.40274874316114667 | 9 | -162.0 | -2.0 |
| `v28` | 18 | 1 | 0.15935039262089976 | 0.5094718154115369 | 9 | -288.0 | -128.0 |
| `candle_brownian` | 18 | 1 | 0.21550545289700795 | 0.6240421929035777 | 9 | -288.0 | -128.0 |
| `tick_brownian` | 18 | 1 | 0.21552306185800393 | 0.6240775919448844 | 9 | -288.0 | -128.0 |
| `market_side_ask` | 18 | 1 | 0.09925 | 0.3783630811014083 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
