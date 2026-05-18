# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:09.572712+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `candidate`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.17292825742363188 | 0.5132670532978536 | 9 | -207.0 | -2.0 |
| `v28` | 18 | 1 | 0.2276496911813067 | 0.6484157063120701 | 9 | -369.0 | -164.0 |
| `candle_brownian` | 18 | 1 | 0.24496320853073592 | 0.6830732542537694 | 9 | -369.0 | -164.0 |
| `tick_brownian` | 18 | 1 | 0.24496320853073592 | 0.6830732542537694 | 9 | -369.0 | -164.0 |
| `market_side_ask` | 18 | 1 | 0.16405000000000003 | 0.5192291829241813 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
