# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T02:01:47.838377+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.02652151359724028`
- Tick Brownian delta log loss vs candle: `0.053085112286807234`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.40064337890427826 | 1.3749294089648538 | 9 | 313.0 | -2.0 |
| `v28` | 18 | 1 | 0.248127620096683 | 0.6894024031992777 | 9 | 567.0 | 252.0 |
| `candle_brownian` | 18 | 1 | 0.2488591678856336 | 0.6908655123649673 | 9 | 567.0 | 252.0 |
| `tick_brownian` | 18 | 1 | 0.27538068148287387 | 0.7439506246517745 | 9 | 567.0 | 252.0 |
| `market_side_ask` | 18 | 1 | 0.40325000000000005 | 1.0079517604379242 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
