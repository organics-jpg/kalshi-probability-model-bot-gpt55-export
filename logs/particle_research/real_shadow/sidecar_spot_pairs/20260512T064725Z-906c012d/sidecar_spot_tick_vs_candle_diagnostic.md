# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T11:18:50.482938+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `candle_brownian`
- Best model by log loss: `candle_brownian`
- Tick Brownian delta Brier vs candle: `0.0`
- Tick Brownian delta log loss vs candle: `0.0`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.43391742970058866 | 1.3173584733698729 | 9 | 308.0 | -2.0 |
| `v28` | 18 | 1 | 0.3583604768745319 | 0.9128769943122792 | 9 | 558.0 | 248.0 |
| `candle_brownian` | 18 | 1 | 0.27165043655909704 | 0.7364743020062766 | 9 | 558.0 | 248.0 |
| `tick_brownian` | 18 | 1 | 0.27165043655909704 | 0.7364743020062766 | 9 | 558.0 | 248.0 |
| `market_side_ask` | 18 | 1 | 0.39065000000000005 | 0.9809181498027864 | 0 | 0 | 0.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
