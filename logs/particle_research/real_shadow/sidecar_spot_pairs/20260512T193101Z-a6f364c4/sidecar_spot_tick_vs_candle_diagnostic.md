# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:20:44.812521+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `candidate`
- Best model by log loss: `candidate`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.15084244745243722 | 0.4571237889063422 | 9 | -212.0 | -2.0 |
| `v28` | 18 | 1 | 0.19115496515307476 | 0.5748535606072445 | 9 | -378.0 | -168.0 |
| `candle_brownian` | 18 | 1 | 0.21962268393839118 | 0.6323139839826175 | 9 | -378.0 | -168.0 |
| `tick_brownian` | 18 | 1 | 0.21962268393839118 | 0.6323139839826175 | 9 | -378.0 | -168.0 |
| `market_side_ask` | 18 | 1 | 0.17225000000000004 | 0.5361799587620221 | 9 | -378.0 | -168.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
