# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-18T18:29:38.058457+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `14` / `1`
- Issue count: `0`
- Best model by Brier: `candle_brownian`
- Best model by log loss: `candle_brownian`
- Tick Brownian delta Brier vs candle: `0.004900010234600349`
- Tick Brownian delta log loss vs candle: `0.00992051224431012`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 14 | 1 | 0.541067714033961 | 1.7470346811642457 | 7 | 214.0 | -74.0 |
| `v28` | 14 | 1 | 0.40005864060057134 | 1.0010371026553926 | 7 | 504.0 | 216.0 |
| `candle_brownian` | 14 | 1 | 0.3056747022187715 | 0.8049250436386733 | 7 | 504.0 | 216.0 |
| `tick_brownian` | 14 | 1 | 0.31057471245337187 | 0.8148455558829835 | 7 | 504.0 | 216.0 |
| `market_side_ask` | 14 | 1 | 0.52565 | 1.2911494978983247 | 7 | 504.0 | 216.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
