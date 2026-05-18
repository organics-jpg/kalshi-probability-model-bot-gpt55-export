# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:20:24.668717+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `candidate`
- Tick Brownian delta Brier vs candle: `-0.004994231477109784`
- Tick Brownian delta log loss vs candle: `-0.011407454243568371`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.04905632379615168 | 0.22452529724056955 | 5 | -27.0 | -4.0 |
| `v28` | 18 | 1 | 0.047472336145920856 | 0.24574898048497248 | 0 | 0 | 0.0 |
| `candle_brownian` | 18 | 1 | 0.10726829487241046 | 0.39678051152599253 | 9 | -207.0 | -92.0 |
| `tick_brownian` | 18 | 1 | 0.10227406339530068 | 0.38537305728242416 | 9 | -207.0 | -92.0 |
| `market_side_ask` | 18 | 1 | 0.04849999999999999 | 0.2485435488277387 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
