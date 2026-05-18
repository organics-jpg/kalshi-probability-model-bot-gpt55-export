# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-18T18:29:12.817876+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `14` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `-0.0017015342352887895`
- Tick Brownian delta log loss vs candle: `-0.006003051402055953`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 14 | 1 | 0.27283082849511403 | 1.2359602804126102 | 7 | -1.2999999999999998 | -2.0999999999999996 |
| `v28` | 14 | 1 | 2.372528068558621e-05 | 0.004882761666458694 | 7 | 3.5 | 1.5 |
| `candle_brownian` | 14 | 1 | 0.030079185049752426 | 0.19047492655953513 | 7 | -4.8999999999999995 | -2.0999999999999996 |
| `tick_brownian` | 14 | 1 | 0.028377650814463636 | 0.18447187515747918 | 7 | -4.8999999999999995 | -2.0999999999999996 |
| `market_side_ask` | 14 | 1 | 3.7e-05 | 0.006018578380254376 | 7 | -4.8999999999999995 | -2.0999999999999996 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
