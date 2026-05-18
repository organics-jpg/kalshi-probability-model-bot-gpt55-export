# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-18T18:27:00.281189+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `14` / `1`
- Issue count: `0`
- Best model by Brier: `candle_brownian`
- Best model by log loss: `candle_brownian`
- Tick Brownian delta Brier vs candle: `0.006789172061098581`
- Tick Brownian delta log loss vs candle: `0.013995475848211147`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 14 | 1 | 0.6356908550826088 | 2.1890335676515034 | 7 | 250.0 | -86.0 |
| `v28` | 14 | 1 | 0.5119707276053962 | 1.2570968886748772 | 7 | 588.0 | 252.0 |
| `candle_brownian` | 14 | 1 | 0.34035835703482004 | 0.8756345043233527 | 7 | 588.0 | 252.0 |
| `tick_brownian` | 14 | 1 | 0.3471475290959186 | 0.8896299801715638 | 7 | 588.0 | 252.0 |
| `market_side_ask` | 14 | 1 | 0.71405 | 1.8648507243170955 | 7 | 588.0 | 252.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
