# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:20:03.270850+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `candidate`
- Best model by log loss: `candidate`
- Tick Brownian delta Brier vs candle: `0.004127998256727328`
- Tick Brownian delta log loss vs candle: `0.008398348058261451`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.08764637140724474 | 0.3279763540138227 | 9 | 265.0 | 152.0 |
| `v28` | 18 | 1 | 0.09469666163101789 | 0.36777666477130233 | 9 | 342.0 | 152.0 |
| `candle_brownian` | 18 | 1 | 0.18709279071702847 | 0.5665889668298603 | 9 | -351.0 | -156.0 |
| `tick_brownian` | 18 | 1 | 0.1912207889737558 | 0.5749873148881217 | 9 | -351.0 | -156.0 |
| `market_side_ask` | 18 | 1 | 0.14825000000000002 | 0.48616606137889 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
