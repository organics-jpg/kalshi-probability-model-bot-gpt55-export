# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:20:13.981804+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.0010600470219323324`
- Tick Brownian delta log loss vs candle: `0.0036589618934698975`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.010670045545089012 | 0.07507777859486459 | 10 | 52.39999999999998 | -0.4000000000000057 |
| `v28` | 18 | 1 | 0.001798186942465182 | 0.04333038206213487 | 9 | 79.19999999999997 | 35.19999999999999 |
| `candle_brownian` | 18 | 1 | 0.030357319717577644 | 0.19144325808145163 | 9 | -81.0 | -36.0 |
| `tick_brownian` | 18 | 1 | 0.031417366739509976 | 0.19510221997492153 | 9 | -81.0 | -36.0 |
| `market_side_ask` | 18 | 1 | 0.007921999999999993 | 0.09321298418952345 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
