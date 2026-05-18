# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T02:01:32.128990+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.23984415806649353 | 0.6530761685895732 | 9 | -147.0 | -2.0 |
| `v28` | 18 | 1 | 0.29354179677735354 | 0.7804385459062934 | 9 | -432.0 | -192.0 |
| `candle_brownian` | 18 | 1 | 0.2657924173920779 | 0.7247422831259365 | 9 | -432.0 | -192.0 |
| `tick_brownian` | 18 | 1 | 0.2657924173920779 | 0.7247422831259365 | 9 | -432.0 | -192.0 |
| `market_side_ask` | 18 | 1 | 0.22565000000000002 | 0.6444023699213167 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
