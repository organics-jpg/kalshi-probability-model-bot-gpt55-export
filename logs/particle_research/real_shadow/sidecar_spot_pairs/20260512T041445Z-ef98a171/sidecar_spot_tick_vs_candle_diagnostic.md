# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-18T18:29:21.066463+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `14` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `-0.00040033218201520086`
- Tick Brownian delta log loss vs candle: `-0.003635155643716949`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 14 | 1 | 0.1397711546766683 | 0.558078324750414 | 3 | -0.30000000000000004 | -0.30000000000000004 |
| `v28` | 14 | 1 | 1.0282209039907983e-10 | 1.0140174211376964e-05 | 0 | 0 | 0.0 |
| `candle_brownian` | 14 | 1 | 0.00362352659953704 | 0.062083654896096394 | 7 | -0.7000000000000001 | -0.30000000000000004 |
| `tick_brownian` | 14 | 1 | 0.003223194417521839 | 0.058448499252379445 | 7 | -0.7000000000000001 | -0.30000000000000004 |
| `market_side_ask` | 14 | 1 | 5e-07 | 0.0005002501672917561 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
