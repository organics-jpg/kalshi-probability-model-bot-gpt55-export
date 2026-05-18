# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:15.093904+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.027585765173819526`
- Tick Brownian delta log loss vs candle: `0.055424919487458535`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.2512513949937062 | 0.9135097233409406 | 9 | 258.0 | 103.0 |
| `v28` | 18 | 1 | 0.11953283681668496 | 0.4242431348468133 | 9 | 468.0 | 208.0 |
| `candle_brownian` | 18 | 1 | 0.20465256533812257 | 0.6021835548145549 | 9 | 468.0 | 208.0 |
| `tick_brownian` | 18 | 1 | 0.2322383305119421 | 0.6576084743020134 | 9 | 468.0 | 208.0 |
| `market_side_ask` | 18 | 1 | 0.27565 | 0.7444958796791166 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
