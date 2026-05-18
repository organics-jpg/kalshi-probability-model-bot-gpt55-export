# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:20:47.929055+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `-0.008046860286951993`
- Tick Brownian delta log loss vs candle: `-0.017883908651732172`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.037892686269433214 | 0.19552331320392496 | 10 | -59.400000000000006 | -38.8 |
| `v28` | 18 | 1 | 0.034163057011665596 | 0.20436167851166295 | 9 | -87.3 | -38.8 |
| `candle_brownian` | 18 | 1 | 0.12090283620753321 | 0.42726733597338057 | 9 | -87.3 | -38.8 |
| `tick_brownian` | 18 | 1 | 0.11285597592058122 | 0.4093834273216484 | 9 | -87.3 | -38.8 |
| `market_side_ask` | 18 | 1 | 0.008844999999999995 | 0.0987214551849049 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
