# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:20:38.087360+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `candidate`
- Best model by log loss: `candidate`
- Tick Brownian delta Brier vs candle: `-0.005168303268714702`
- Tick Brownian delta log loss vs candle: `-0.010576617415336331`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.31874005877752754 | 0.8033284474923642 | 9 | 612.0 | 272.0 |
| `v28` | 18 | 1 | 0.441955968363417 | 1.0930210183931854 | 9 | 612.0 | 272.0 |
| `candle_brownian` | 18 | 1 | 0.33356525019102756 | 0.861686739274803 | 9 | 612.0 | 272.0 |
| `tick_brownian` | 18 | 1 | 0.32839694692231286 | 0.8511101218594667 | 9 | 612.0 | 272.0 |
| `market_side_ask` | 18 | 1 | 0.46924999999999994 | 1.155308632345655 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
