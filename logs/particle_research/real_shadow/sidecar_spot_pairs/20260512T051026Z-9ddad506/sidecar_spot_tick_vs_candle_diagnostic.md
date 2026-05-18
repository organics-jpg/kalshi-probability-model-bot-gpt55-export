# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-18T18:27:35.609760+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `16` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 16 | 1 | 0.3407594598585381 | 1.1271380930793382 | 8 | 89.0 | -95.0 |
| `v28` | 16 | 1 | 0.18186693341995747 | 0.5559251483317574 | 8 | 368.0 | 184.0 |
| `candle_brownian` | 16 | 1 | 0.22324248914178724 | 0.6395788083653324 | 8 | -376.0 | -188.0 |
| `tick_brownian` | 16 | 1 | 0.22324248914178724 | 0.6395788083653324 | 8 | -376.0 | -188.0 |
| `market_side_ask` | 16 | 1 | 0.21625 | 0.6255322059298932 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
