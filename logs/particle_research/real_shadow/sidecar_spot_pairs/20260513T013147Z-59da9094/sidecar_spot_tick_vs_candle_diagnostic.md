# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T02:02:07.327749+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `-0.016653684704310084`
- Tick Brownian delta log loss vs candle: `-0.03400767673875382`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.10261083725894392 | 0.35857175261660074 | 9 | -159.0 | -4.0 |
| `v28` | 18 | 1 | 0.12665504941700093 | 0.43987999579409526 | 9 | -279.0 | -124.0 |
| `candle_brownian` | 18 | 1 | 0.1919598222008534 | 0.5764886830474284 | 9 | -279.0 | -124.0 |
| `tick_brownian` | 18 | 1 | 0.1753061374965433 | 0.5424810063086746 | 9 | -279.0 | -124.0 |
| `market_side_ask` | 18 | 1 | 0.09010000000000003 | 0.356776995168804 | 9 | -279.0 | -124.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
