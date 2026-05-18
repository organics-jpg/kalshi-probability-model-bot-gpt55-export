# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:20:08.556447+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `-0.0506973743264566`
- Tick Brownian delta log loss vs candle: `-0.10151585155636877`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.22771482440179844 | 0.6287731558229706 | 10 | -248.0 | -83.0 |
| `v28` | 18 | 1 | 0.2673693403913712 | 0.7278994929264475 | 9 | -369.0 | -164.0 |
| `candle_brownian` | 18 | 1 | 0.2669432819986314 | 0.7270464047580889 | 9 | -369.0 | -164.0 |
| `tick_brownian` | 18 | 1 | 0.21624590767217478 | 0.6255305532017201 | 9 | -369.0 | -164.0 |
| `market_side_ask` | 18 | 1 | 0.16405000000000003 | 0.5192291829241813 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
