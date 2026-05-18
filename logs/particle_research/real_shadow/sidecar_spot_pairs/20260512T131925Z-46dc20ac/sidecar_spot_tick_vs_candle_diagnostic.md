# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:20:00.573168+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `-0.010094154512307552`
- Tick Brownian delta log loss vs candle: `-0.022728204522733053`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.20560938830857198 | 0.8450284119570775 | 9 | -54.0 | -68.0 |
| `v28` | 18 | 1 | 0.023705188060950597 | 0.1671944217735942 | 9 | 144.0 | 64.0 |
| `candle_brownian` | 18 | 1 | 0.11591553043316864 | 0.41621826533970013 | 9 | -153.0 | -68.0 |
| `tick_brownian` | 18 | 1 | 0.10582137592086109 | 0.3934900608169671 | 9 | -153.0 | -68.0 |
| `market_side_ask` | 18 | 1 | 0.027250000000000003 | 0.18034148266813566 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
