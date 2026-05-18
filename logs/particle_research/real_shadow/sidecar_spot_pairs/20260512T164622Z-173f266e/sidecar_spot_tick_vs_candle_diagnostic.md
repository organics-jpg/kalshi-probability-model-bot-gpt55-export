# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:20:21.839219+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.0023450047551344527`
- Tick Brownian delta log loss vs candle: `0.007492780796444082`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.1813304298590817 | 0.7891000362938493 | 9 | -16.0 | -48.0 |
| `v28` | 18 | 1 | 0.0034969405232618397 | 0.060955544875430916 | 9 | 99.0 | 44.0 |
| `candle_brownian` | 18 | 1 | 0.03654939242172928 | 0.21217759024874105 | 9 | -108.0 | -48.0 |
| `tick_brownian` | 18 | 1 | 0.038894397176863736 | 0.21967037104518514 | 9 | -108.0 | -48.0 |
| `market_side_ask` | 18 | 1 | 0.01325 | 0.1221835938829182 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
