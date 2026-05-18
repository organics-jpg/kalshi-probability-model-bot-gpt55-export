# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-18T18:28:23.501616+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `16` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 16 | 1 | 0.2705152558406312 | 1.093365652347418 | 8 | -76.0 | -38.0 |
| `v28` | 16 | 1 | 0.026609457482767083 | 0.17807943393390155 | 8 | -76.0 | -38.0 |
| `candle_brownian` | 16 | 1 | 0.1357084694243748 | 0.45947731319137547 | 8 | -76.0 | -38.0 |
| `tick_brownian` | 16 | 1 | 0.1357084694243748 | 0.45947731319137547 | 8 | -76.0 | -38.0 |
| `market_side_ask` | 16 | 1 | 0.008930500000000001 | 0.09926815411068429 | 8 | 75.20000000000005 | 37.60000000000002 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
