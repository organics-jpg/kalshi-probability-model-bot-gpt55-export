# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:20:16.600469+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.0015901604125073965`
- Tick Brownian delta log loss vs candle: `0.0033456191619238296`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.24584087459895324 | 0.890553521771414 | 5 | -160.0 | -128.0 |
| `v28` | 18 | 1 | 0.09155143122818356 | 0.36035982549764295 | 0 | 0 | 0.0 |
| `candle_brownian` | 18 | 1 | 0.15041971533824594 | 0.4907612762832716 | 9 | -288.0 | -128.0 |
| `tick_brownian` | 18 | 1 | 0.15200987575075334 | 0.4941068954451954 | 9 | -288.0 | -128.0 |
| `market_side_ask` | 18 | 1 | 0.09620000000000001 | 0.3711687123753586 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
