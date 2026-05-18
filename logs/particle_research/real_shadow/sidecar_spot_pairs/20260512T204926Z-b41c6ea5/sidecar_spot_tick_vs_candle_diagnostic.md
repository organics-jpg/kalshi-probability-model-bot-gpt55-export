# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T02:01:28.272915+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `candle_brownian`
- Best model by log loss: `candidate`
- Tick Brownian delta Brier vs candle: `0.016433955732559957`
- Tick Brownian delta log loss vs candle: `0.033535605946727776`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.3190804831147169 | 0.8167138788233683 | 9 | 648.0 | 288.0 |
| `v28` | 18 | 1 | 0.4279631972176107 | 1.0618627843222554 | 9 | 648.0 | 288.0 |
| `candle_brownian` | 18 | 1 | 0.3171779480710214 | 0.828246741773014 | 9 | 648.0 | 288.0 |
| `tick_brownian` | 18 | 1 | 0.33361190380358136 | 0.8617823477197418 | 9 | 648.0 | 288.0 |
| `market_side_ask` | 18 | 1 | 0.52565 | 1.291149497898325 | 9 | 648.0 | 288.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
