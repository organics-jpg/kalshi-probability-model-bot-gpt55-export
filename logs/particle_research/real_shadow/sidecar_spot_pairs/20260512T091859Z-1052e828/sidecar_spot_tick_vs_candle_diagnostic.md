# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:17.706199+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `-0.00019161780983015242`
- Tick Brownian delta log loss vs candle: `-0.00038380011957694915`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.37520519046657264 | 1.274525259820529 | 9 | 138.0 | -97.0 |
| `v28` | 18 | 1 | 0.20326174683397014 | 0.5993756218261762 | 9 | 423.0 | 188.0 |
| `candle_brownian` | 18 | 1 | 0.23128798101513773 | 0.6557051458166896 | 9 | -432.0 | -192.0 |
| `tick_brownian` | 18 | 1 | 0.23109636320530758 | 0.6553213456971126 | 9 | -432.0 | -192.0 |
| `market_side_ask` | 18 | 1 | 0.22565000000000002 | 0.6444023699213167 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
