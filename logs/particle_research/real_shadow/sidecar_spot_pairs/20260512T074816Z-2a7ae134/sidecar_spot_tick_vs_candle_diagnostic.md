# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:01.156071+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.003989648986924749`
- Tick Brownian delta log loss vs candle: `0.008594361337171008`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.18095922468468695 | 0.8327891835431105 | 8 | -4.0 | -39.0 |
| `v28` | 18 | 1 | 0.014795256845765723 | 0.12969391351797938 | 9 | 162.0 | 72.0 |
| `candle_brownian` | 18 | 1 | 0.13214894793713217 | 0.4518069457693677 | 9 | -171.0 | -76.0 |
| `tick_brownian` | 18 | 1 | 0.13613859692405691 | 0.4604013071065387 | 9 | -171.0 | -76.0 |
| `market_side_ask` | 18 | 1 | 0.034249999999999996 | 0.20458598501974537 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
