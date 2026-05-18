# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-18T18:27:59.247541+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `16` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `1.729196879057815e-05`
- Tick Brownian delta log loss vs candle: `3.5323106289619766e-05`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 16 | 1 | 0.06744484333254179 | 0.2716225713372949 | 8 | -72.0 | -4.0 |
| `v28` | 16 | 1 | 0.08716057032986364 | 0.3498833318082423 | 8 | -136.0 | -68.0 |
| `candle_brownian` | 16 | 1 | 0.1828938547112051 | 0.5580236501334797 | 8 | -136.0 | -68.0 |
| `tick_brownian` | 16 | 1 | 0.18291114667999567 | 0.5580589732397693 | 8 | -136.0 | -68.0 |
| `market_side_ask` | 16 | 1 | 0.025700000000000008 | 0.17442425384463422 | 8 | -136.0 | -68.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
