# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:20:05.937551+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.01281748497997881`
- Tick Brownian delta log loss vs candle: `0.026352629987859255`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.2826123219574324 | 1.0744717804163648 | 9 | 108.0 | -2.0 |
| `v28` | 18 | 1 | 0.08136635104775924 | 0.33581947681525887 | 9 | 333.0 | 148.0 |
| `candle_brownian` | 18 | 1 | 0.16801758271466022 | 0.5274623816671796 | 9 | -342.0 | -152.0 |
| `tick_brownian` | 18 | 1 | 0.18083506769463903 | 0.5538150116550389 | 9 | -342.0 | -152.0 |
| `market_side_ask` | 18 | 1 | 0.14065 | 0.4700356302697792 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
