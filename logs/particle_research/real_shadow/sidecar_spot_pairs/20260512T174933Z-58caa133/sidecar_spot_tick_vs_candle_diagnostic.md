# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:20:31.592084+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `candidate`
- Best model by log loss: `candidate`
- Tick Brownian delta Brier vs candle: `0.002475405812787712`
- Tick Brownian delta log loss vs candle: `0.004995537199728006`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.2542768018751913 | 0.6781187607938247 | 8 | 113.0 | 232.0 |
| `v28` | 18 | 1 | 0.35269853993154815 | 0.9011171393014297 | 9 | -531.0 | -236.0 |
| `candle_brownian` | 18 | 1 | 0.2983063181770448 | 0.7900419789327929 | 9 | 522.0 | 232.0 |
| `tick_brownian` | 18 | 1 | 0.3007817239898325 | 0.7950375161325209 | 9 | 522.0 | 232.0 |
| `market_side_ask` | 18 | 1 | 0.3422500000000001 | 0.8795493434942533 | 9 | -531.0 | -236.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
