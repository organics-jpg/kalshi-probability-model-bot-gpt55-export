# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:39.377766+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `tick_brownian`
- Best model by log loss: `tick_brownian`
- Tick Brownian delta Brier vs candle: `-0.008789537689351201`
- Tick Brownian delta log loss vs candle: `-0.01882102197777824`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.49888983391147057 | 1.2981837837306585 | 9 | -219.0 | 141.0 |
| `v28` | 18 | 1 | 0.7160777885407297 | 1.8721919268442337 | 9 | -648.0 | -288.0 |
| `candle_brownian` | 18 | 1 | 0.3993099404667359 | 0.9994271442039133 | 9 | 639.0 | 284.0 |
| `tick_brownian` | 18 | 1 | 0.3905204027773847 | 0.9806061222261351 | 9 | 639.0 | 284.0 |
| `market_side_ask` | 18 | 1 | 0.51125 | 1.2554200159072524 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
