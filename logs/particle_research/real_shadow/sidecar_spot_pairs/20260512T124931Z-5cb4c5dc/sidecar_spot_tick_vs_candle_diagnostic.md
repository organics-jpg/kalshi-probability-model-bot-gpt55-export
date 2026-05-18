# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:55.856213+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `candle_brownian`
- Best model by log loss: `candle_brownian`
- Tick Brownian delta Brier vs candle: `0.0017047553399084925`
- Tick Brownian delta log loss vs candle: `0.0036059497097543636`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.6228033917683811 | 1.9675419903562614 | 9 | 388.0 | -2.0 |
| `v28` | 18 | 1 | 0.5857223995546558 | 1.4495538230558822 | 9 | 702.0 | 312.0 |
| `candle_brownian` | 18 | 1 | 0.37946669891648294 | 0.9571353415570171 | 9 | 702.0 | 312.0 |
| `tick_brownian` | 18 | 1 | 0.38117145425639143 | 0.9607412912667714 | 9 | 702.0 | 312.0 |
| `market_side_ask` | 18 | 1 | 0.6162500000000001 | 1.537387740447222 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
