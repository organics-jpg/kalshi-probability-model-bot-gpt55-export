# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:20:11.272264+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `-1.804374513374174e-05`
- Tick Brownian delta log loss vs candle: `-4.245686804793536e-05`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.25516958043270166 | 1.0701296620778615 | 9 | -24.0 | -41.0 |
| `v28` | 18 | 1 | 0.028694793782851207 | 0.1856013820653597 | 9 | 171.0 | 76.0 |
| `candle_brownian` | 18 | 1 | 0.09385195988384326 | 0.3657916211197335 | 9 | -180.0 | -80.0 |
| `tick_brownian` | 18 | 1 | 0.09383391613870952 | 0.3657491642516856 | 9 | -180.0 | -80.0 |
| `market_side_ask` | 18 | 1 | 0.03805 | 0.2169322913149311 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
