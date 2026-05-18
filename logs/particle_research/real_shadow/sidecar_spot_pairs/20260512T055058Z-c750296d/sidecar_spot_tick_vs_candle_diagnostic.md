# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:18:34.518767+00:00`
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
| `candidate` | 16 | 1 | 0.3285726220737524 | 1.2357352945381512 | 8 | -208.0 | -104.0 |
| `v28` | 16 | 1 | 0.0905487213754347 | 0.3579802896747534 | 8 | -208.0 | -104.0 |
| `candle_brownian` | 16 | 1 | 0.18413098242989223 | 0.5605497320948903 | 8 | -208.0 | -104.0 |
| `tick_brownian` | 16 | 1 | 0.18413098242989223 | 0.5605497320948903 | 8 | -208.0 | -104.0 |
| `market_side_ask` | 16 | 1 | 0.06505 | 0.29439358261785126 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
