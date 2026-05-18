# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T02:01:36.168331+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `-1.4327402649894072e-05`
- Tick Brownian delta log loss vs candle: `-2.8688325563575034e-05`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.3021260501328077 | 0.9984584023102704 | 10 | 181.0 | -95.0 |
| `v28` | 18 | 1 | 0.20861896177702055 | 0.6101824342640538 | 9 | 414.0 | 184.0 |
| `candle_brownian` | 18 | 1 | 0.23320812804973196 | 0.6595504724563367 | 9 | -423.0 | -188.0 |
| `tick_brownian` | 18 | 1 | 0.23319380064708206 | 0.6595217841307731 | 9 | -423.0 | -188.0 |
| `market_side_ask` | 18 | 1 | 0.21625 | 0.6255322059298932 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
