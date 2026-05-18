# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:18:44.883116+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `16` / `1`
- Issue count: `0`
- Best model by Brier: `candle_brownian`
- Best model by log loss: `candle_brownian`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 16 | 1 | 0.40170768251422123 | 1.2975928847236884 | 8 | 425.0 | 141.0 |
| `v28` | 16 | 1 | 0.3392670863931565 | 0.8733902162562764 | 8 | 568.0 | 284.0 |
| `candle_brownian` | 16 | 1 | 0.28075971151637646 | 0.7547409980662665 | 8 | 568.0 | 284.0 |
| `tick_brownian` | 16 | 1 | 0.28075971151637646 | 0.7547409980662665 | 8 | 568.0 | 284.0 |
| `market_side_ask` | 16 | 1 | 0.51125 | 1.2554200159072524 | 8 | 568.0 | 284.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
