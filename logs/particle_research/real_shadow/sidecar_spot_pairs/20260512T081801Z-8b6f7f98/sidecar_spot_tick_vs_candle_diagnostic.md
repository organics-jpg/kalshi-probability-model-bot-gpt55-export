# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:06.688066+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `candidate`
- Best model by log loss: `candidate`
- Tick Brownian delta Brier vs candle: `0.015528535156072276`
- Tick Brownian delta log loss vs candle: `0.031087534971236286`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.1383208300577599 | 0.4305005008143584 | 9 | 432.0 | 192.0 |
| `v28` | 18 | 1 | 0.1656124381144986 | 0.5224851344552003 | 9 | 432.0 | 192.0 |
| `candle_brownian` | 18 | 1 | 0.2275287810194803 | 0.6481733760274747 | 9 | 432.0 | 192.0 |
| `tick_brownian` | 18 | 1 | 0.24305731617555257 | 0.679260910998711 | 9 | -441.0 | -196.0 |
| `market_side_ask` | 18 | 1 | 0.23525 | 0.6636355103352147 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
