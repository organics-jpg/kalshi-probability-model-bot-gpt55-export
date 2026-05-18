# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-18T18:27:18.574120+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `14` / `1`
- Issue count: `0`
- Best model by Brier: `market_side_ask`
- Best model by log loss: `market_side_ask`
- Tick Brownian delta Brier vs candle: `1.7615713102825392e-05`
- Tick Brownian delta log loss vs candle: `3.625492331249536e-05`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 14 | 1 | 0.30938138214707706 | 1.1336672856686916 | 7 | -161.0 | -69.0 |
| `v28` | 14 | 1 | 0.0766954494949736 | 0.324262288409499 | 7 | -161.0 | -69.0 |
| `candle_brownian` | 14 | 1 | 0.17303906015307283 | 0.5378194322219079 | 7 | -161.0 | -69.0 |
| `tick_brownian` | 14 | 1 | 0.17305667586617565 | 0.5378556871452204 | 7 | -161.0 | -69.0 |
| `market_side_ask` | 14 | 1 | 0.05065000000000001 | 0.25491306171645356 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
