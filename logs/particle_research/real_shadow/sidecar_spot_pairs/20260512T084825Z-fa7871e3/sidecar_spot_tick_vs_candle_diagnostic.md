# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:12.326640+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.2880467069363905 | 0.9853544716651386 | 9 | 138.0 | -2.0 |
| `v28` | 18 | 1 | 0.15416269899604487 | 0.49862630628843185 | 9 | 423.0 | 188.0 |
| `candle_brownian` | 18 | 1 | 0.22151077823418563 | 0.6361041472057832 | 0 | 0 | 0.0 |
| `tick_brownian` | 18 | 1 | 0.22151077823418563 | 0.6361041472057832 | 0 | 0 | 0.0 |
| `market_side_ask` | 18 | 1 | 0.22565000000000002 | 0.6444023699213167 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
