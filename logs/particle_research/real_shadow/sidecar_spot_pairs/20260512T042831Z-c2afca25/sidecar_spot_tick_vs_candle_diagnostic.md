# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-18T18:29:29.300051+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `14` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `1.776756339165537e-05`
- Tick Brownian delta log loss vs candle: `0.0007585938449230396`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 14 | 1 | 6.198758269444425e-05 | 0.0034221366350709894 | 2 | -0.2 | -0.2 |
| `v28` | 14 | 1 | 1.0000000100495186e-16 | 1.0000000100247594e-08 | 0 | 0 | 0.0 |
| `candle_brownian` | 14 | 1 | 0.00013171019533060306 | 0.01154286956602 | 7 | -0.7000000000000001 | -0.30000000000000004 |
| `tick_brownian` | 14 | 1 | 0.00014947775872225843 | 0.01230146341094304 | 7 | -0.7000000000000001 | -0.30000000000000004 |
| `market_side_ask` | 14 | 1 | 5.000000000000009e-07 | 0.0005002501672917561 | 7 | -0.7000000000000001 | -0.30000000000000004 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
