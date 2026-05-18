# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-18T18:28:07.331268+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `16` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `0.005126174928073879`
- Tick Brownian delta log loss vs candle: `0.010560956330558646`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 16 | 1 | 0.0584451579003414 | 0.24858324526332004 | 8 | -56.0 | -52.0 |
| `v28` | 16 | 1 | 0.06689840469167198 | 0.2992787334857507 | 8 | -104.0 | -52.0 |
| `candle_brownian` | 16 | 1 | 0.16929135796087502 | 0.5300939215889784 | 8 | -104.0 | -52.0 |
| `tick_brownian` | 16 | 1 | 0.1744175328889489 | 0.540654877919537 | 8 | -104.0 | -52.0 |
| `market_side_ask` | 16 | 1 | 0.014499999999999999 | 0.12789794179472957 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
