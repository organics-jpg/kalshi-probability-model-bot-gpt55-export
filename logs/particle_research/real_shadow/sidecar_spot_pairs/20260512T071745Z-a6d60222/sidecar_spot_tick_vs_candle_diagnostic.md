# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:18:55.888166+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `1.0874086175949316e-05`
- Tick Brownian delta log loss vs candle: `2.3413559880336443e-05`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.2332167067845908 | 0.977575647871563 | 9 | 66.0 | -49.0 |
| `v28` | 18 | 1 | 0.017228409814522186 | 0.14070798251004413 | 9 | 207.0 | 92.0 |
| `candle_brownian` | 18 | 1 | 0.1344265799393549 | 0.45671993771225267 | 9 | -216.0 | -96.0 |
| `tick_brownian` | 18 | 1 | 0.13443745402553084 | 0.456743351272133 | 9 | -216.0 | -96.0 |
| `market_side_ask` | 18 | 1 | 0.05525 | 0.26790080491808393 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
