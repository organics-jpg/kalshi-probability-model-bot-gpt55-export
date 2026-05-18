# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:33.921704+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `tick_brownian`
- Best model by log loss: `tick_brownian`
- Tick Brownian delta Brier vs candle: `-1.6205902663379845e-05`
- Tick Brownian delta log loss vs candle: `-3.242812745818391e-05`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.4415545791880854 | 1.3985441809730834 | 9 | 162.0 | -113.0 |
| `v28` | 18 | 1 | 0.3011801903836962 | 0.7958420555301948 | 9 | 495.0 | 220.0 |
| `candle_brownian` | 18 | 1 | 0.2613514719714865 | 0.715853961263935 | 9 | 495.0 | 220.0 |
| `tick_brownian` | 18 | 1 | 0.2613352660688231 | 0.7158215331364768 | 9 | 495.0 | 220.0 |
| `market_side_ask` | 18 | 1 | 0.30805000000000005 | 0.809744124143801 | 9 | -504.0 | -224.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
