# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:18:42.267706+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `16` / `1`
- Issue count: `0`
- Best model by Brier: `candidate`
- Best model by log loss: `candidate`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 16 | 1 | 0.1567338410874737 | 0.4732763228119249 | 8 | -170.0 | -2.0 |
| `v28` | 16 | 1 | 0.21165926604130506 | 0.6163054337613256 | 8 | -336.0 | -168.0 |
| `candle_brownian` | 16 | 1 | 0.23466497483637183 | 0.6624672796520727 | 8 | -336.0 | -168.0 |
| `tick_brownian` | 16 | 1 | 0.23466497483637183 | 0.6624672796520727 | 8 | -336.0 | -168.0 |
| `market_side_ask` | 16 | 1 | 0.17225000000000001 | 0.5361799587620221 | 8 | -336.0 | -168.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
