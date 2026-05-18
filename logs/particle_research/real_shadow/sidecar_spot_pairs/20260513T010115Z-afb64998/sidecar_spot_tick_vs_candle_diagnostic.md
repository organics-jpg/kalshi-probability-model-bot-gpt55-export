# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T02:02:03.548395+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `candidate`
- Best model by log loss: `candidate`
- Tick Brownian delta Brier vs candle: `0.0032448970463616056`
- Tick Brownian delta log loss vs candle: `0.006493458871101532`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.2434892895817293 | 0.6605642030872088 | 9 | -156.0 | -2.0 |
| `v28` | 18 | 1 | 0.29504507154975684 | 0.7834669654642672 | 9 | -459.0 | -204.0 |
| `candle_brownian` | 18 | 1 | 0.26036160900618893 | 0.7138733206779638 | 9 | -459.0 | -204.0 |
| `tick_brownian` | 18 | 1 | 0.26360650605255054 | 0.7203667795490654 | 9 | -459.0 | -204.0 |
| `market_side_ask` | 18 | 1 | 0.25505 | 0.703248534218705 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
