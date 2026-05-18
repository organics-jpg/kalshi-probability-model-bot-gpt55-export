# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:20:19.223434+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.012423748765569703`
- Tick Brownian delta log loss vs candle: `0.026761449476637833`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.26739106100107113 | 1.0004488335934212 | 9 | 90.0 | -65.0 |
| `v28` | 18 | 1 | 0.06551413829707788 | 0.2956568503659923 | 9 | 279.0 | 124.0 |
| `candle_brownian` | 18 | 1 | 0.1280625376780579 | 0.44294622830246194 | 9 | -288.0 | -128.0 |
| `tick_brownian` | 18 | 1 | 0.1404862864436276 | 0.4697076777790998 | 9 | -288.0 | -128.0 |
| `market_side_ask` | 18 | 1 | 0.09925 | 0.3783630811014084 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
