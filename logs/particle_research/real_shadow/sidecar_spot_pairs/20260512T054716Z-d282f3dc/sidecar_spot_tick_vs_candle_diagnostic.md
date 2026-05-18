# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-18T18:28:39.944385+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `16` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `-0.0003949476316346401`
- Tick Brownian delta log loss vs candle: `-0.0007915986921739337`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 16 | 1 | 0.3167189067057949 | 1.0585075100749515 | 8 | 84.0 | -96.0 |
| `v28` | 16 | 1 | 0.18417923009763215 | 0.5606482056202015 | 8 | 360.0 | 180.0 |
| `candle_brownian` | 16 | 1 | 0.22754155139228502 | 0.6481989709014039 | 8 | -376.0 | -188.0 |
| `tick_brownian` | 16 | 1 | 0.22714660376065038 | 0.64740737220923 | 8 | -376.0 | -188.0 |
| `market_side_ask` | 16 | 1 | 0.2117 | 0.616357636595795 | 8 | 360.0 | 180.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
