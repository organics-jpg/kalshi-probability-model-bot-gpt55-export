# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:58.123186+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `1.79400059269752e-05`
- Tick Brownian delta log loss vs candle: `3.5974034054531145e-05`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.4289686575821313 | 1.3295377196485165 | 9 | -477.0 | -212.0 |
| `v28` | 18 | 1 | 0.3048203510666287 | 0.8031972983438241 | 9 | -477.0 | -212.0 |
| `candle_brownian` | 18 | 1 | 0.27620618606782055 | 0.7456058254169229 | 0 | 0 | 0.0 |
| `tick_brownian` | 18 | 1 | 0.2762241260737475 | 0.7456417994509774 | 0 | 0 | 0.0 |
| `market_side_ask` | 18 | 1 | 0.27565 | 0.7444958796791166 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
