# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:30.923025+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.274013031982111 | 1.0697352359497974 | 9 | 78.0 | -57.0 |
| `v28` | 18 | 1 | 0.06513579579794658 | 0.2946625852394065 | 9 | 243.0 | 108.0 |
| `candle_brownian` | 18 | 1 | 0.17441639797325303 | 0.5406525447721898 | 9 | -252.0 | -112.0 |
| `tick_brownian` | 18 | 1 | 0.17441639797325303 | 0.5406525447721898 | 9 | -252.0 | -112.0 |
| `market_side_ask` | 18 | 1 | 0.07565000000000001 | 0.32160740590586817 | 9 | -252.0 | -112.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
