# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T02:01:24.414295+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.28703743025924033 | 0.9645665579013217 | 9 | -378.0 | -168.0 |
| `v28` | 18 | 1 | 0.17671507832543046 | 0.5453738084292437 | 9 | -378.0 | -168.0 |
| `candle_brownian` | 18 | 1 | 0.21970633273347634 | 0.632481940435611 | 9 | -378.0 | -168.0 |
| `tick_brownian` | 18 | 1 | 0.21970633273347634 | 0.632481940435611 | 9 | -378.0 | -168.0 |
| `market_side_ask` | 18 | 1 | 0.17224999999999996 | 0.5361799587620218 | 9 | 369.0 | 164.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
