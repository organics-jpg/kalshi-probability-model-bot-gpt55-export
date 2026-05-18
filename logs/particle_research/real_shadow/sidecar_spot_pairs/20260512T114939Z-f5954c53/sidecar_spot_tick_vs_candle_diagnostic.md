# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:45.705629+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `candidate`
- Best model by log loss: `candidate`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.11878057721135987 | 0.39687289046353386 | 7 | -110.0 | -2.0 |
| `v28` | 18 | 1 | 0.15778862242668132 | 0.5062132111476276 | 9 | -324.0 | -144.0 |
| `candle_brownian` | 18 | 1 | 0.21275269339971173 | 0.6185059130301883 | 9 | -324.0 | -144.0 |
| `tick_brownian` | 18 | 1 | 0.21275269339971173 | 0.6185059130301883 | 9 | -324.0 | -144.0 |
| `market_side_ask` | 18 | 1 | 0.12605 | 0.4385350093604369 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
