# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:18:58.454224+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `candle_brownian`
- Best model by log loss: `candle_brownian`
- Tick Brownian delta Brier vs candle: `0.0007398260729750694`
- Tick Brownian delta log loss vs candle: `0.0014823622711080953`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.44897735495692653 | 1.4435522079944632 | 9 | 298.0 | -2.0 |
| `v28` | 18 | 1 | 0.3143161882268778 | 0.8224340831617813 | 9 | 540.0 | 240.0 |
| `candle_brownian` | 18 | 1 | 0.2714651659064779 | 0.736103098886678 | 9 | 540.0 | 240.0 |
| `tick_brownian` | 18 | 1 | 0.27220499197945297 | 0.7375854611577861 | 9 | 540.0 | 240.0 |
| `market_side_ask` | 18 | 1 | 0.36605 | 0.9289496358663 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
