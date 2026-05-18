# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:51.307279+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `-0.0007915146923302974`
- Tick Brownian delta log loss vs candle: `-0.0015832428944141386`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.3525066125969821 | 1.1300811678796134 | 9 | 273.0 | -2.0 |
| `v28` | 18 | 1 | 0.22246261498363648 | 0.6380141784043604 | 9 | 495.0 | 220.0 |
| `candle_brownian` | 18 | 1 | 0.24462770241750553 | 0.682402168522897 | 9 | 495.0 | 220.0 |
| `tick_brownian` | 18 | 1 | 0.24383618772517524 | 0.6808189256284829 | 9 | 495.0 | 220.0 |
| `market_side_ask` | 18 | 1 | 0.30805000000000005 | 0.809744124143801 | 9 | -504.0 | -224.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
