# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:18:31.964731+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `16` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 16 | 1 | 0.37673697908764314 | 1.257395430368768 | 8 | 91.0 | -97.0 |
| `v28` | 16 | 1 | 0.1790280517943186 | 0.5501159209268496 | 8 | 376.0 | 188.0 |
| `candle_brownian` | 16 | 1 | 0.22516139405987196 | 0.64342743488062 | 0 | 0 | 0.0 |
| `tick_brownian` | 16 | 1 | 0.22516139405987196 | 0.64342743488062 | 0 | 0 | 0.0 |
| `market_side_ask` | 16 | 1 | 0.22565 | 0.6444023699213167 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
