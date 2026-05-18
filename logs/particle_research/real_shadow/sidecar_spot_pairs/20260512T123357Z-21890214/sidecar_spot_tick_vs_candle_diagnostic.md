# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:19:53.581470+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `candle_brownian`
- Best model by log loss: `candle_brownian`
- Tick Brownian delta Brier vs candle: `0.0029708343702101736`
- Tick Brownian delta log loss vs candle: `0.007607250695439882`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.6236593918473932 | 1.9630157483336172 | 9 | -97.0 | 172.0 |
| `v28` | 18 | 1 | 0.9193919441919957 | 3.1905138859119533 | 9 | -801.0 | -356.0 |
| `candle_brownian` | 18 | 1 | 0.5372079817349936 | 1.3202996497544828 | 9 | 783.0 | 348.0 |
| `tick_brownian` | 18 | 1 | 0.5401788161052038 | 1.3279069004499227 | 9 | 783.0 | 348.0 |
| `market_side_ask` | 18 | 1 | 0.7745000000000001 | 2.1237478708581374 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
